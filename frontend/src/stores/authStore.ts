import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '@/services/api'

interface User {
  id: string
  email: string
  full_name: string
  company_name?: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  register: (data: RegisterData) => Promise<void>
  clearError: () => void
}

interface RegisterData {
  email: string
  password: string
  full_name: string
  company_name?: string
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await api.post('/auth/login', {
            username: email, // OAuth2 expects username field
            password,
          })
          
          const { access_token } = response.data
          
          // Set token in API client
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
          
          // Get user info
          const userResponse = await api.get('/auth/me')
          
          set({
            token: access_token,
            user: userResponse.data,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || 'Login failed',
            isLoading: false,
          })
          throw error
        }
      },

      logout: () => {
        // Clear token from API client
        delete api.defaults.headers.common['Authorization']
        
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        })
      },

      register: async (data: RegisterData) => {
        set({ isLoading: true, error: null })
        try {
          await api.post('/auth/register', data)
          // Auto-login after registration
          await useAuthStore.getState().login(data.email, data.password)
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || 'Registration failed',
            isLoading: false,
          })
          throw error
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
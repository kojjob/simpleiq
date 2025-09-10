import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api, { setAuthStoreAccessor } from '@/services/api'

interface User {
  id: string
  email: string
  full_name: string
  company_name?: string
}

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  tokenExpiry: number | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  register: (data: RegisterData) => Promise<void>
  initializeAuth: () => Promise<void>
  refreshAccessToken: () => Promise<void>
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
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      tokenExpiry: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          // OAuth2 expects form-encoded data
          const formData = new URLSearchParams()
          formData.append('username', email)
          formData.append('password', password)
          
          const response = await api.post('/auth/login', formData, {
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
            },
          })
          
          const { access_token, refresh_token, expires_in } = response.data
          
          // Calculate token expiry time
          const tokenExpiry = Date.now() + (expires_in * 1000) // Convert to milliseconds
          
          // Set token in API client
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
          
          // Get user info
          const userResponse = await api.get('/auth/me')
          
          set({
            token: access_token,
            refreshToken: refresh_token,
            tokenExpiry,
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
          refreshToken: null,
          tokenExpiry: null,
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

      refreshAccessToken: async () => {
        const state = get()
        if (!state.refreshToken) {
          throw new Error('No refresh token available')
        }

        try {
          const response = await api.post('/auth/refresh', {
            refresh_token: state.refreshToken,
          })
          
          const { access_token, refresh_token, expires_in } = response.data
          const tokenExpiry = Date.now() + (expires_in * 1000)
          
          // Update API client with new token
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
          
          set({
            token: access_token,
            refreshToken: refresh_token,
            tokenExpiry,
          })
        } catch (error) {
          // Refresh failed, logout user
          get().logout()
          throw error
        }
      },

      initializeAuth: async () => {
        const state = get()
        if (state.token) {
          try {
            // Check if token is about to expire (within 5 minutes)
            const isExpiringSoon = state.tokenExpiry && (state.tokenExpiry - Date.now()) < 5 * 60 * 1000
            
            if (isExpiringSoon && state.refreshToken) {
              // Try to refresh the token
              await get().refreshAccessToken()
            } else {
              // Set token in API client
              api.defaults.headers.common['Authorization'] = `Bearer ${state.token}`
            }
            
            // Verify token is still valid by getting user info
            const userResponse = await api.get('/auth/me')
            
            set({
              user: userResponse.data,
              isAuthenticated: true,
            })
          } catch (error) {
            // Token is invalid, try to refresh if possible
            if (state.refreshToken) {
              try {
                await get().refreshAccessToken()
                const userResponse = await api.get('/auth/me')
                set({
                  user: userResponse.data,
                  isAuthenticated: true,
                })
              } catch (refreshError) {
                // Refresh failed, clear everything
                get().logout()
              }
            } else {
              // No refresh token, clear everything
              get().logout()
            }
          }
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
        tokenExpiry: state.tokenExpiry,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)

// Set up API client accessor
setAuthStoreAccessor(() => useAuthStore.getState())

// Periodic token check (every 5 minutes)
setInterval(() => {
  const state = useAuthStore.getState()
  if (state.isAuthenticated && state.tokenExpiry) {
    const timeUntilExpiry = state.tokenExpiry - Date.now()
    // If token expires within 10 minutes, try to refresh
    if (timeUntilExpiry < 10 * 60 * 1000 && state.refreshToken) {
      state.refreshAccessToken().catch(() => {
        // Refresh failed, user will be logged out by the axios interceptor
      })
    }
  }
}, 5 * 60 * 1000) // Check every 5 minutes
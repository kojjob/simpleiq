import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useAuthStore } from '../authStore'
import api from '@/services/api'

// Mock the API module
vi.mock('@/services/api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    defaults: {
      headers: {
        common: {}
      }
    }
  }
}))

describe('AuthStore', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks()
    // Reset the store
    const { result } = renderHook(() => useAuthStore())
    act(() => {
      result.current.logout()
    })
  })

  describe('login', () => {
    it('should successfully login with valid credentials', async () => {
      const mockToken = 'test-access-token'
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        full_name: 'Test User',
        company_name: 'Test Company'
      }

      // Mock successful login response
      vi.mocked(api.post).mockResolvedValueOnce({
        data: { access_token: mockToken }
      })

      // Mock successful user info response
      vi.mocked(api.get).mockResolvedValueOnce({
        data: mockUser
      })

      const { result } = renderHook(() => useAuthStore())

      await act(async () => {
        await result.current.login('test@example.com', 'password123')
      })

      // Check that the store was updated correctly
      expect(result.current.isAuthenticated).toBe(true)
      expect(result.current.token).toBe(mockToken)
      expect(result.current.user).toEqual(mockUser)
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBe(null)

      // Check that the API was called correctly
      expect(api.post).toHaveBeenCalledWith(
        '/auth/login',
        expect.any(URLSearchParams),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      )

      // Check that the token was set in the API headers
      expect(api.defaults.headers.common['Authorization']).toBe(`Bearer ${mockToken}`)
    })

    it('should handle login failure', async () => {
      const errorMessage = 'Invalid credentials'
      
      // Mock failed login response
      vi.mocked(api.post).mockRejectedValueOnce({
        response: {
          data: {
            detail: errorMessage
          }
        }
      })

      const { result } = renderHook(() => useAuthStore())

      await expect(
        act(async () => {
          await result.current.login('test@example.com', 'wrongpassword')
        })
      ).rejects.toThrow()

      // Check that the store reflects the error
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.token).toBe(null)
      expect(result.current.user).toBe(null)
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBe(errorMessage)
    })

    it('should send form-encoded data for OAuth2 compatibility', async () => {
      vi.mocked(api.post).mockResolvedValueOnce({
        data: { access_token: 'token' }
      })
      vi.mocked(api.get).mockResolvedValueOnce({
        data: { id: '1', email: 'test@example.com', full_name: 'Test' }
      })

      const { result } = renderHook(() => useAuthStore())

      await act(async () => {
        await result.current.login('test@example.com', 'password123')
      })

      // Get the actual call arguments
      const postCall = vi.mocked(api.post).mock.calls[0]
      const formData = postCall[1] as URLSearchParams

      // Check that form data was sent correctly
      expect(formData).toBeInstanceOf(URLSearchParams)
      expect(formData.get('username')).toBe('test@example.com')
      expect(formData.get('password')).toBe('password123')
    })
  })

  describe('register', () => {
    it('should successfully register and auto-login', async () => {
      const registerData = {
        email: 'new@example.com',
        password: 'password123',
        full_name: 'New User',
        company_name: 'New Company'
      }

      const mockUser = {
        id: '456',
        email: registerData.email,
        full_name: registerData.full_name,
        company_name: registerData.company_name
      }

      // Mock successful registration
      vi.mocked(api.post)
        .mockResolvedValueOnce({ data: {} }) // Registration response
        .mockResolvedValueOnce({ data: { access_token: 'new-token' } }) // Login response

      // Mock successful user info response
      vi.mocked(api.get).mockResolvedValueOnce({ data: mockUser })

      const { result } = renderHook(() => useAuthStore())

      await act(async () => {
        await result.current.register(registerData)
      })

      // Check that registration was called
      expect(api.post).toHaveBeenCalledWith('/auth/register', registerData)

      // Check that auto-login occurred
      expect(result.current.isAuthenticated).toBe(true)
      expect(result.current.user).toEqual(mockUser)
    })

    it('should handle registration failure', async () => {
      const errorMessage = 'Email already exists'
      
      vi.mocked(api.post).mockRejectedValueOnce({
        response: {
          data: {
            detail: errorMessage
          }
        }
      })

      const { result } = renderHook(() => useAuthStore())

      await expect(
        act(async () => {
          await result.current.register({
            email: 'existing@example.com',
            password: 'password123',
            full_name: 'Test User'
          })
        })
      ).rejects.toThrow()

      expect(result.current.error).toBe(errorMessage)
      expect(result.current.isAuthenticated).toBe(false)
    })
  })

  describe('logout', () => {
    it('should clear all auth data on logout', async () => {
      // Setup initial authenticated state
      vi.mocked(api.post).mockResolvedValueOnce({
        data: { access_token: 'test-token' }
      })
      vi.mocked(api.get).mockResolvedValueOnce({
        data: { id: '1', email: 'test@example.com', full_name: 'Test' }
      })

      const { result } = renderHook(() => useAuthStore())

      // First login
      await act(async () => {
        await result.current.login('test@example.com', 'password')
      })

      expect(result.current.isAuthenticated).toBe(true)

      // Then logout
      act(() => {
        result.current.logout()
      })

      // Check that all auth data was cleared
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.token).toBe(null)
      expect(result.current.user).toBe(null)
      expect(result.current.error).toBe(null)

      // Check that the Authorization header was removed
      expect(api.defaults.headers.common['Authorization']).toBeUndefined()
    })
  })

  describe('clearError', () => {
    it('should clear the error state', async () => {
      // Create an error state
      vi.mocked(api.post).mockRejectedValueOnce({
        response: { data: { detail: 'Test error' } }
      })

      const { result } = renderHook(() => useAuthStore())

      await expect(
        act(async () => {
          await result.current.login('test@example.com', 'wrong')
        })
      ).rejects.toThrow()

      expect(result.current.error).toBe('Test error')

      // Clear the error
      act(() => {
        result.current.clearError()
      })

      expect(result.current.error).toBe(null)
    })
  })
})
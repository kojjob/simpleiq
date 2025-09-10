import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Keep track of refresh attempts to prevent infinite loops
let isRefreshing = false
let failedQueue: Array<{
  resolve: (value?: any) => void
  reject: (reason?: any) => void
}> = []

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve(token)
    }
  })
  
  failedQueue = []
}

// Function to get auth store (will be set up after store is created)
let getAuthStore: (() => any) | null = null

export const setAuthStoreAccessor = (accessor: () => any) => {
  getAuthStore = accessor
}

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    // Token is set by authStore when logging in
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // If refresh is already in progress, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          originalRequest.headers['Authorization'] = `Bearer ${token}`
          return api(originalRequest)
        }).catch(err => {
          return Promise.reject(err)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        if (getAuthStore) {
          const authStore = getAuthStore()
          if (authStore.refreshToken) {
            await authStore.refreshAccessToken()
            const newToken = authStore.token
            processQueue(null, newToken)
            originalRequest.headers['Authorization'] = `Bearer ${newToken}`
            return api(originalRequest)
          }
        }
        
        // No refresh token available, logout
        if (getAuthStore) {
          getAuthStore().logout()
        }
        processQueue(error, null)
        return Promise.reject(error)
      } catch (refreshError) {
        // Refresh failed, logout
        if (getAuthStore) {
          getAuthStore().logout()
        }
        processQueue(refreshError, null)
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default api
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Login from '../Login'
import { useAuthStore } from '@/stores/authStore'
import '@testing-library/jest-dom'

// Mock the auth store
vi.mock('@/stores/authStore')

// Mock react-router-dom's useNavigate
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate
  }
})

// Mock antd message
vi.mock('antd', async () => {
  const actual = await vi.importActual('antd')
  return {
    ...actual,
    message: {
      success: vi.fn(),
      error: vi.fn()
    }
  }
})

describe('Login Component', () => {
  const mockLogin = vi.fn()
  const mockRegister = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Setup default mock implementation
    vi.mocked(useAuthStore).mockReturnValue({
      login: mockLogin,
      register: mockRegister,
      isLoading: false,
      user: null,
      token: null,
      isAuthenticated: false,
      error: null,
      logout: vi.fn(),
      clearError: vi.fn()
    })
  })

  const renderLogin = () => {
    return render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )
  }

  describe('Login Form', () => {
    it('should render login form by default', () => {
      renderLogin()

      expect(screen.getByText('Welcome Back')).toBeInTheDocument()
      expect(screen.getByText('Sign in to SimpleIQ - Analytics Made Simple')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('Email')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('Password')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /Sign In/i })).toBeInTheDocument()
    })

    it('should handle successful login', async () => {
      mockLogin.mockResolvedValueOnce(undefined)
      renderLogin()

      const emailInput = screen.getByPlaceholderText('Email')
      const passwordInput = screen.getByPlaceholderText('Password')
      const submitButton = screen.getByRole('button', { name: /Sign In/i })

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
      fireEvent.change(passwordInput, { target: { value: 'password123' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123')
        expect(mockNavigate).toHaveBeenCalledWith('/dashboard')
      })
    })

    it('should handle login failure', async () => {
      const errorMessage = 'Invalid credentials'
      mockLogin.mockRejectedValueOnce({
        response: { data: { detail: errorMessage } }
      })
      
      renderLogin()

      const emailInput = screen.getByPlaceholderText('Email')
      const passwordInput = screen.getByPlaceholderText('Password')
      const submitButton = screen.getByRole('button', { name: /Sign In/i })

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
      fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalled()
        expect(mockNavigate).not.toHaveBeenCalled()
      })
    })

    it('should show loading state during login', () => {
      vi.mocked(useAuthStore).mockReturnValue({
        login: mockLogin,
        register: mockRegister,
        isLoading: true,
        user: null,
        token: null,
        isAuthenticated: false,
        error: null,
        logout: vi.fn(),
        clearError: vi.fn()
      })

      renderLogin()

      const submitButton = screen.getByRole('button', { name: /Sign In/i })
      expect(submitButton).toHaveClass('ant-btn-loading')
    })
  })

  describe('Registration Form', () => {
    it('should switch to registration form when Sign Up is clicked', () => {
      renderLogin()

      const signUpLink = screen.getByText('Sign Up')
      fireEvent.click(signUpLink)

      expect(screen.getByText('Create Account')).toBeInTheDocument()
      expect(screen.getByText('Start your data analytics journey')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('Full Name')).toBeInTheDocument()
      expect(screen.getByPlaceholderText('Company Name (Optional)')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /Create Account/i })).toBeInTheDocument()
    })

    it('should handle successful registration', async () => {
      mockRegister.mockResolvedValueOnce(undefined)
      renderLogin()

      // Switch to registration form
      const signUpLink = screen.getByText('Sign Up')
      fireEvent.click(signUpLink)

      const fullNameInput = screen.getByPlaceholderText('Full Name')
      const emailInput = screen.getByPlaceholderText('Email')
      const passwordInput = screen.getByPlaceholderText('Password')
      const submitButton = screen.getByRole('button', { name: /Create Account/i })

      fireEvent.change(fullNameInput, { target: { value: 'Test User' } })
      fireEvent.change(emailInput, { target: { value: 'new@example.com' } })
      fireEvent.change(passwordInput, { target: { value: 'password123' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalledWith({
          full_name: 'Test User',
          email: 'new@example.com',
          password: 'password123',
          company_name: undefined
        })
        expect(mockNavigate).toHaveBeenCalledWith('/dashboard')
      })
    })

    it('should include company name if provided', async () => {
      mockRegister.mockResolvedValueOnce(undefined)
      renderLogin()

      // Switch to registration form
      const signUpLink = screen.getByText('Sign Up')
      fireEvent.click(signUpLink)

      const fullNameInput = screen.getByPlaceholderText('Full Name')
      const companyInput = screen.getByPlaceholderText('Company Name (Optional)')
      const emailInput = screen.getByPlaceholderText('Email')
      const passwordInput = screen.getByPlaceholderText('Password')
      const submitButton = screen.getByRole('button', { name: /Create Account/i })

      fireEvent.change(fullNameInput, { target: { value: 'Test User' } })
      fireEvent.change(companyInput, { target: { value: 'Test Company' } })
      fireEvent.change(emailInput, { target: { value: 'new@example.com' } })
      fireEvent.change(passwordInput, { target: { value: 'password123' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalledWith({
          full_name: 'Test User',
          company_name: 'Test Company',
          email: 'new@example.com',
          password: 'password123'
        })
      })
    })

    it('should reset form when switching between login and register', () => {
      renderLogin()

      // Fill in login form
      const emailInput = screen.getByPlaceholderText('Email')
      const passwordInput = screen.getByPlaceholderText('Password')
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
      fireEvent.change(passwordInput, { target: { value: 'password123' } })

      // Switch to registration
      const signUpLink = screen.getByText('Sign Up')
      fireEvent.click(signUpLink)

      // Switch back to login
      const signInLink = screen.getByText('Sign In')
      fireEvent.click(signInLink)

      // Check that form is reset
      const newEmailInput = screen.getByPlaceholderText('Email')
      const newPasswordInput = screen.getByPlaceholderText('Password')
      expect(newEmailInput).toHaveValue('')
      expect(newPasswordInput).toHaveValue('')
    })
  })

  describe('Form Validation', () => {
    it('should validate email format', async () => {
      renderLogin()

      const emailInput = screen.getByPlaceholderText('Email')
      const submitButton = screen.getByRole('button', { name: /Sign In/i })

      fireEvent.change(emailInput, { target: { value: 'invalid-email' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Please enter a valid email')).toBeInTheDocument()
      })
    })

    it('should require all mandatory fields for registration', async () => {
      renderLogin()

      // Switch to registration form
      const signUpLink = screen.getByText('Sign Up')
      fireEvent.click(signUpLink)

      const submitButton = screen.getByRole('button', { name: /Create Account/i })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Please enter your full name')).toBeInTheDocument()
        expect(screen.getByText('Please enter your email')).toBeInTheDocument()
        expect(screen.getByText('Please enter your password')).toBeInTheDocument()
      })
    })

    it('should enforce minimum password length', async () => {
      renderLogin()

      // Switch to registration form
      const signUpLink = screen.getByText('Sign Up')
      fireEvent.click(signUpLink)

      const passwordInput = screen.getByPlaceholderText('Password')
      const submitButton = screen.getByRole('button', { name: /Create Account/i })

      fireEvent.change(passwordInput, { target: { value: 'short' } })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Password must be at least 8 characters')).toBeInTheDocument()
      })
    })
  })
})
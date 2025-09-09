import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Form, Input, Button, Card, message, Typography, Space, Divider } from 'antd'
import { UserOutlined, LockOutlined, MailOutlined, TeamOutlined } from '@ant-design/icons'
import { useAuthStore } from '@/stores/authStore'

const { Title, Text, Link } = Typography

interface LoginForm {
  email: string
  password: string
}

interface RegisterForm extends LoginForm {
  full_name: string
  company_name?: string
}

export default function Login() {
  const [isRegister, setIsRegister] = useState(false)
  const navigate = useNavigate()
  const { login, register, isLoading } = useAuthStore()
  const [form] = Form.useForm()

  const handleSubmit = async (values: LoginForm | RegisterForm) => {
    try {
      if (isRegister) {
        await register(values as RegisterForm)
        message.success('Registration successful! Welcome to SimpleIQ!')
      } else {
        await login(values.email, values.password)
        message.success('Login successful!')
      }
      navigate('/dashboard')
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Authentication failed')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <Card className="w-full max-w-md shadow-xl">
        <div className="text-center mb-8">
          <Title level={2} className="mb-2">
            {isRegister ? 'Create Account' : 'Welcome Back'}
          </Title>
          <Text type="secondary">
            {isRegister 
              ? 'Start your data analytics journey' 
              : 'Sign in to SimpleIQ - Analytics Made Simple'}
          </Text>
        </div>

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          size="large"
        >
          {isRegister && (
            <>
              <Form.Item
                name="full_name"
                rules={[{ required: true, message: 'Please enter your full name' }]}
              >
                <Input 
                  prefix={<UserOutlined />} 
                  placeholder="Full Name" 
                />
              </Form.Item>

              <Form.Item
                name="company_name"
              >
                <Input 
                  prefix={<TeamOutlined />} 
                  placeholder="Company Name (Optional)" 
                />
              </Form.Item>
            </>
          )}

          <Form.Item
            name="email"
            rules={[
              { required: true, message: 'Please enter your email' },
              { type: 'email', message: 'Please enter a valid email' }
            ]}
          >
            <Input 
              prefix={<MailOutlined />} 
              placeholder="Email" 
              type="email"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: 'Please enter your password' },
              { min: 8, message: 'Password must be at least 8 characters' }
            ]}
          >
            <Input.Password 
              prefix={<LockOutlined />} 
              placeholder="Password" 
            />
          </Form.Item>

          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              block 
              loading={isLoading}
            >
              {isRegister ? 'Create Account' : 'Sign In'}
            </Button>
          </Form.Item>
        </Form>

        <Divider>or</Divider>

        <div className="text-center">
          <Text>
            {isRegister ? 'Already have an account? ' : "Don't have an account? "}
            <Link onClick={() => {
              setIsRegister(!isRegister)
              form.resetFields()
            }}>
              {isRegister ? 'Sign In' : 'Sign Up'}
            </Link>
          </Text>
        </div>

        <div className="mt-6 pt-6 border-t border-gray-200">
          <Space direction="vertical" className="w-full text-center">
            <Text type="secondary" className="text-xs">
              By signing up, you agree to our Terms of Service and Privacy Policy
            </Text>
            <Text type="secondary" className="text-xs">
              🚀 Databricks-level analytics at 1% of the cost
            </Text>
          </Space>
        </div>
      </Card>
    </div>
  )
}
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Suspense, lazy, useEffect } from 'react'
import { Spin } from 'antd'
import { useAuthStore } from './stores/authStore'

// Lazy load components to isolate import errors
const Login = lazy(() => import('./pages/Login'))
const MainLayout = lazy(() => import('./components/Layout/MainLayout'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Query = lazy(() => import('./pages/Query'))
const DataSources = lazy(() => import('./pages/DataSources'))
const Settings = lazy(() => import('./pages/Settings'))

function App() {
  const { initializeAuth } = useAuthStore()

  useEffect(() => {
    initializeAuth()
  }, [initializeAuth])

  return (
    <Router>
      <Suspense fallback={<Spin size="large" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }} />}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="query" element={<Query />} />
            <Route path="data-sources" element={<DataSources />} />
            <Route path="settings" element={<Settings />} />
          </Route>
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Suspense>
    </Router>
  )
}

export default App
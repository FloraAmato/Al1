import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './lib/auth-store'

// Layouts
import MainLayout from './components/layout/MainLayout'
import AuthLayout from './components/layout/AuthLayout'

// Pages
import HomePage from './pages/HomePage'
import LoginPage from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import DisputeListPage from './pages/disputes/DisputeListPage'
import DisputeCreatePage from './pages/disputes/DisputeCreatePage'
import DisputeDetailPage from './pages/disputes/DisputeDetailPage'
import DisputeBidsPage from './pages/disputes/DisputeBidsPage'
import DisputeSolutionPage from './pages/disputes/DisputeSolutionPage'

// Static pages
import HelpPage from './pages/static/HelpPage'
import ResearchPage from './pages/static/ResearchPage'
import ProjectPage from './pages/static/ProjectPage'
import ContactPage from './pages/static/ContactPage'
import LegalTermsPage from './pages/static/LegalTermsPage'
import NewsPage from './pages/static/NewsPage'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes with main layout */}
        <Route path="/" element={<MainLayout />}>
          <Route index element={<HomePage />} />
          <Route path="help" element={<HelpPage />} />
          <Route path="research" element={<ResearchPage />} />
          <Route path="project" element={<ProjectPage />} />
          <Route path="contact" element={<ContactPage />} />
          <Route path="legal-terms" element={<LegalTermsPage />} />
          <Route path="news" element={<NewsPage />} />
        </Route>

        {/* Auth routes */}
        <Route path="/login" element={<AuthLayout><LoginPage /></AuthLayout>} />
        <Route path="/register" element={<AuthLayout><RegisterPage /></AuthLayout>} />

        {/* Private routes with main layout */}
        <Route path="/" element={<MainLayout />}>
          <Route
            path="dashboard"
            element={
              <PrivateRoute>
                <DashboardPage />
              </PrivateRoute>
            }
          />
          <Route
            path="disputes"
            element={
              <PrivateRoute>
                <DisputeListPage />
              </PrivateRoute>
            }
          />
          <Route
            path="disputes/create"
            element={
              <PrivateRoute>
                <DisputeCreatePage />
              </PrivateRoute>
            }
          />
          <Route
            path="disputes/:id"
            element={
              <PrivateRoute>
                <DisputeDetailPage />
              </PrivateRoute>
            }
          />
          <Route
            path="disputes/:id/bids"
            element={
              <PrivateRoute>
                <DisputeBidsPage />
              </PrivateRoute>
            }
          />
          <Route
            path="disputes/:id/solution"
            element={
              <PrivateRoute>
                <DisputeSolutionPage />
              </PrivateRoute>
            }
          />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App

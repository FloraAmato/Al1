import { Outlet, Link } from 'react-router-dom'
import { useAuthStore } from '@/lib/auth-store'

export default function MainLayout() {
  const { isAuthenticated, user, logout } = useAuthStore()

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-primary-600 text-white shadow-lg">
        <nav className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="text-2xl font-bold">
              CREA2
            </Link>

            <div className="flex items-center gap-6">
              <Link to="/project" className="hover:text-primary-200">
                Project
              </Link>
              <Link to="/research" className="hover:text-primary-200">
                Research
              </Link>
              <Link to="/help" className="hover:text-primary-200">
                Help
              </Link>
              <Link to="/news" className="hover:text-primary-200">
                News
              </Link>
              <Link to="/contact" className="hover:text-primary-200">
                Contact
              </Link>

              {isAuthenticated ? (
                <>
                  <Link to="/dashboard" className="hover:text-primary-200">
                    Dashboard
                  </Link>
                  <Link to="/disputes" className="hover:text-primary-200">
                    Disputes
                  </Link>
                  <div className="flex items-center gap-4">
                    <span className="text-sm">{user?.email}</span>
                    <button
                      onClick={logout}
                      className="px-4 py-2 bg-white text-primary-600 rounded hover:bg-primary-50"
                    >
                      Logout
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="px-4 py-2 hover:bg-primary-700 rounded"
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    className="px-4 py-2 bg-white text-primary-600 rounded hover:bg-primary-50"
                  >
                    Register
                  </Link>
                </>
              )}
            </div>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="flex-1 container mx-auto px-4 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-sm">© 2024 CREA2 - Fair Division Platform</p>
            </div>
            <div className="flex gap-4">
              <Link to="/legal-terms" className="text-sm hover:text-primary-300">
                Legal Terms
              </Link>
              <Link to="/privacy" className="text-sm hover:text-primary-300">
                Privacy Policy
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

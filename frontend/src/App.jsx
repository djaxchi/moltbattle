import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext'
import Landing from './pages/Landing'
import CombatLobby from './pages/CombatLobby'
import AcceptInvite from './pages/AcceptInvite'
import Dashboard from './pages/Dashboard'
import { Auth, RegisterHandle } from './pages/Auth'
import { Zap, LogOut } from 'lucide-react'

// Protected route wrapper - redirects to auth if not logged in
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading, needsUsername, firebaseUser, setRedirectUrl } = useAuth()
  const location = useLocation()
  
  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading...</div>
      </div>
    )
  }
  
  if (!firebaseUser) {
    // Save the current URL to redirect back after auth
    setRedirectUrl(location.pathname)
    return <Navigate to="/auth" replace />
  }
  
  if (needsUsername) {
    // Save the current URL to redirect back after registration
    setRedirectUrl(location.pathname)
    return <Navigate to="/register" replace />
  }
  
  return children
}

// Auth route wrapper (redirect to home if already authenticated)
function AuthRoute({ children }) {
  const { isAuthenticated, loading, needsUsername, firebaseUser } = useAuth()
  
  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading...</div>
      </div>
    )
  }
  
  if (firebaseUser && needsUsername) {
    return <Navigate to="/register" replace />
  }
  
  if (isAuthenticated) {
    return <Navigate to="/" replace />
  }
  
  return children
}

function App() {
  const { user, signOut, isAuthenticated, firebaseUser } = useAuth()

  return (
    <div>
      {/* Navigation bar */}
      <nav className="navbar">
        <a href="/" className="navbar-brand">
          <Zap size={24} fill="#ef4444" />
          MoltBattle
        </a>
        
        {firebaseUser ? (
          <div className="navbar-actions">
            {isAuthenticated ? (
              <div className="navbar-user">
                <div>
                  <div className="font-bold">{user?.username}</div>
                  <div className="text-xs text-muted">
                    {user?.rank} • {user?.wins}W / {user?.losses}L
                  </div>
                </div>
              </div>
            ) : (
              <div className="navbar-user">
                <div>
                  <div className="font-bold">{firebaseUser.email}</div>
                  <div className="text-xs text-muted">Setting up profile...</div>
                </div>
              </div>
            )}
            <button onClick={signOut} className="btn btn-secondary btn-sm">
              <LogOut size={16} />
              Sign Out
            </button>
          </div>
        ) : (
          <a href="/auth" className="btn btn-sm">
            Sign In
          </a>
        )}
      </nav>

      <Routes>
        {/* Public routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/dashboard/:code" element={<Dashboard />} />
        
        {/* Auth routes */}
        <Route path="/auth" element={
          <AuthRoute>
            <Auth />
          </AuthRoute>
        } />
        <Route path="/register" element={<RegisterHandle />} />

        {/* Protected routes - require auth to create/join combats */}
        <Route path="/lobby/:code" element={
          <ProtectedRoute>
            <CombatLobby />
          </ProtectedRoute>
        } />
        <Route path="/accept/:code" element={
          <ProtectedRoute>
            <AcceptInvite />
          </ProtectedRoute>
        } />
      </Routes>
    </div>
  )
}

export default App

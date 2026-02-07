import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext'
import Landing from './pages/Landing'
import CombatLobby from './pages/CombatLobby'
import AcceptInvite from './pages/AcceptInvite'
import Dashboard from './pages/Dashboard'
import ApiDocs from './pages/ApiDocs'
import MCPDocs from './pages/MCPDocs'
import { Auth } from './pages/Auth'
import { LogOut, BookOpen, Cpu } from 'lucide-react'
import logo from '../images/icon.png'

// Protected route wrapper - redirects to auth if not logged in
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading, setRedirectUrl } = useAuth()
  const location = useLocation()
  
  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading...</div>
      </div>
    )
  }
  
  if (!isAuthenticated) {
    // Save the current URL to redirect back after auth
    setRedirectUrl(location.pathname)
    return <Navigate to="/auth" replace />
  }
  
  return children
}

// Auth route wrapper (redirect to home if already authenticated)
function AuthRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading...</div>
      </div>
    )
  }
  
  if (isAuthenticated) {
    return <Navigate to="/" replace />
  }
  
  return children
}

function App() {
  const { user, signOut, isAuthenticated } = useAuth()

  return (
    <div>
      {/* Navigation bar */}
      <nav className="navbar">
        <a href="/" className="navbar-brand">
          <img src={logo} alt="MoltClash" style={{ height: '28px', width: 'auto', filter: 'drop-shadow(0 0 8px #ff0055)' }} />
          MoltClash
        </a>
        
        <a href="/docs" className="btn btn-sm btn-secondary" style={{ marginLeft: 'auto', marginRight: '0.5rem' }}>
          <BookOpen size={16} />
          API Docs
        </a>
        
        <a href="/mcp-docs" className="btn btn-sm btn-secondary" style={{ marginRight: '1rem' }}>
          <Cpu size={16} />
          MCP Guide
        </a>
        
        {isAuthenticated ? (
          <div className="navbar-actions">
            <div className="navbar-user">
              <div>
                <div className="font-bold">{user?.username}</div>
                <div className="text-xs text-muted">
                  {user?.rank} • {user?.wins}W / {user?.losses}L
                </div>
              </div>
            </div>
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
        <Route path="/docs" element={<ApiDocs />} />
        <Route path="/mcp-docs" element={<MCPDocs />} />
        <Route path="/dashboard/:code" element={<Dashboard />} />
        
        {/* Auth routes */}
        <Route path="/auth" element={
          <AuthRoute>
            <Auth />
          </AuthRoute>
        } />

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

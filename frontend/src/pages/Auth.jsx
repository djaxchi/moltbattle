import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'
import { checkUsernameAvailable } from '../api'
import { LogIn, UserPlus, Lock, User, Check, X } from 'lucide-react'
import logo from '../../images/icon.png'

function Auth() {
  const [isLogin, setIsLogin] = useState(true)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [email, setEmail] = useState('')
  const [techDescription, setTechDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [usernameAvailable, setUsernameAvailable] = useState(null)
  const navigate = useNavigate()
  const { signIn, signUp, redirectUrl, setRedirectUrl } = useAuth()

  const checkUsername = async (value) => {
    if (value.length < 3) {
      setUsernameAvailable(null)
      return
    }
    try {
      const result = await checkUsernameAvailable(value)
      setUsernameAvailable(result.available)
    } catch (err) {
      console.error('Error checking username:', err)
    }
  }

  const handleUsernameChange = (e) => {
    const value = e.target.value.replace(/[^a-zA-Z0-9_]/g, '')
    setUsername(value)
    if (!isLogin) {
      checkUsername(value)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    
    if (!isLogin && password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (!isLogin && password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    if (!isLogin && !usernameAvailable) {
      setError('Username is not available')
      return
    }

    setLoading(true)

    try {
      if (isLogin) {
        await signIn(username, password)
      } else {
        await signUp(username, password, email || null, techDescription || null)
      }
      // Navigate to saved redirect URL or dashboard
      const destination = redirectUrl || '/'
      setRedirectUrl(null)
      navigate(destination)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Authentication failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container fade-in">
      <div className="header">
        <h1 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem' }}>
          <img src={logo} alt="MoltClash" style={{ height: '52px', width: 'auto', filter: 'drop-shadow(0 0 12px #ff0055)' }} />
          MoltClash
        </h1>
        <p>Real-time 1v1 Agent Combat Platform</p>
      </div>

      <div className="card auth-card">
        <h2 className="auth-title">
          {isLogin ? (
            <>
              <LogIn size={24} />
              SIGN IN
            </>
          ) : (
            <>
              <UserPlus size={24} />
              CREATE ACCOUNT
            </>
          )}
        </h2>

        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label>Username</label>
            <input
              type="text"
              value={username}
              onChange={handleUsernameChange}
              placeholder="agent_alpha"
              minLength={3}
              maxLength={30}
              required
              autoFocus
            />
            {!isLogin && username.length >= 3 && (
              <p className={`handle-status ${usernameAvailable ? 'available' : 'taken'}`}>
                {usernameAvailable ? (
                  <>
                    <Check size={14} />
                    Username available
                  </>
                ) : (
                  <>
                    <X size={14} />
                    Username taken
                  </>
                )}
              </p>
            )}
          </div>

          <div className="input-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              minLength={isLogin ? 1 : 8}
              required
            />
            {!isLogin && (
              <small style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>
                Must be at least 8 characters
              </small>
            )}
          </div>

          {!isLogin && (
            <>
              <div className="input-group">
                <label>Confirm Password</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  minLength={8}
                  required
                />
              </div>

              <div className="input-group">
                <label>Email (Optional)</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="agent@example.com"
                />
                <small style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>
                  For password recovery (future feature)
                </small>
              </div>

              <div className="input-group">
                <label>Tech Setup (Optional)</label>
                <textarea
                  value={techDescription}
                  onChange={(e) => setTechDescription(e.target.value)}
                  placeholder="Describe your agentic setup: Claude 3.5 Sonnet + custom reasoning framework..."
                  maxLength={2000}
                  rows={3}
                  style={{ 
                    width: '100%', 
                    padding: '0.75rem', 
                    borderRadius: '8px',
                    border: '1px solid var(--color-border)',
                    backgroundColor: 'var(--color-bg-elevated)',
                    color: 'var(--color-text)',
                    fontFamily: 'inherit',
                    fontSize: '0.95rem',
                    resize: 'vertical'
                  }}
                />
              </div>
            </>
          )}

          {error && <div className="error">{error}</div>}

          <button 
            type="submit" 
            className="btn btn-full" 
            disabled={loading || (!isLogin && !usernameAvailable)}
          >
            {loading ? (
              'Loading...'
            ) : isLogin ? (
              <>
                <LogIn size={18} />
                Sign In
              </>
            ) : (
              <>
                <UserPlus size={18} />
                Create Account
              </>
            )}
          </button>
        </form>

        <p className="auth-switch">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button 
            onClick={() => {
              setIsLogin(!isLogin)
              setError('')
              setUsernameAvailable(null)
            }} 
            className="link-btn"
          >
            {isLogin ? 'Sign Up' : 'Sign In'}
          </button>
        </p>
      </div>
    </div>
  )
}

export { Auth }

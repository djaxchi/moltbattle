import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'
import { checkUsernameAvailable, registerUser } from '../api'
import { Zap, LogIn, UserPlus, Mail, Lock, User, Check, X, Swords } from 'lucide-react'

function Auth() {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const { signIn, signUp, signInWithGoogle } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isLogin) {
        await signIn(email, password)
        // AuthContext will check if user exists in DB, redirect to /register if needed
      } else {
        await signUp(email, password)
        // New user will be redirected to /register to choose username
      }
    } catch (err) {
      setError(err.message || 'Authentication failed')
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleSignIn = async () => {
    setError('')
    setLoading(true)
    try {
      await signInWithGoogle()
      // AuthContext will check if user exists in DB, redirect to /register if needed
    } catch (err) {
      setError(err.message || 'Google sign-in failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container fade-in">
      <div className="header">
        <h1 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem' }}>
          <Zap size={48} fill="#ef4444" color="#ef4444" />
          MoltBattle
        </h1>
        <p>Real-time 1v1 Combat Platform</p>
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
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="agent@example.com"
              required
            />
          </div>

          <div className="input-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              minLength={6}
              required
            />
          </div>

          {error && <div className="error">{error}</div>}

          <button 
            type="submit" 
            className="btn btn-full" 
            disabled={loading}
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

        <div className="divider">OR</div>

        <button 
          onClick={handleGoogleSignIn}
          className="btn btn-secondary btn-full"
          disabled={loading}
        >
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.615z" fill="#4285F4"/>
            <path d="M9.003 18c2.43 0 4.467-.806 5.956-2.18L12.05 13.56c-.806.54-1.836.86-3.047.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332C2.438 15.983 5.482 18 9.003 18z" fill="#34A853"/>
            <path d="M3.964 10.712c-.18-.54-.282-1.117-.282-1.71 0-.593.102-1.17.282-1.71V4.96H.957C.347 6.175 0 7.55 0 9.002c0 1.452.348 2.827.957 4.042l3.007-2.332z" fill="#FBBC05"/>
            <path d="M9.003 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.464.891 11.426 0 9.003 0 5.482 0 2.438 2.017.957 4.958L3.964 7.29c.708-2.127 2.692-3.71 5.039-3.71z" fill="#EA4335"/>
          </svg>
          Continue with Google
        </button>

        <p className="auth-switch">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button onClick={() => setIsLogin(!isLogin)} className="link-btn">
            {isLogin ? 'Sign Up' : 'Sign In'}
          </button>
        </p>
      </div>
    </div>
  )
}

function RegisterHandle() {
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [available, setAvailable] = useState(null)
  const navigate = useNavigate()
  const { firebaseUser, signOut, refreshUser, setNeedsUsername, redirectUrl, setRedirectUrl } = useAuth()

  const checkUsername = async (value) => {
    if (value.length < 3) {
      setAvailable(null)
      return
    }
    try {
      const result = await checkUsernameAvailable(value)
      setAvailable(result.available)
    } catch (err) {
      console.error('Error checking username:', err)
    }
  }

  const handleChange = (e) => {
    const value = e.target.value.replace(/[^a-zA-Z0-9_]/g, '')
    setUsername(value)
    checkUsername(value)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!available) return
    
    setError('')
    setLoading(true)

    try {
      // Create user in our database with chosen username
      await registerUser(username)
      // Refresh to get the new user data
      await refreshUser()
      // Clear the needs username flag
      setNeedsUsername(false)
      // Navigate to saved redirect URL or dashboard
      const destination = redirectUrl || '/'
      setRedirectUrl(null)
      navigate(destination)
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  const handleSignOut = async () => {
    await signOut()
    navigate('/auth')
  }

  return (
    <div className="container fade-in">
      <div className="header">
        <h1 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem' }}>
          <Zap size={48} fill="#ef4444" color="#ef4444" />
          MoltBattle
        </h1>
        <p>Almost there! Choose your username.</p>
      </div>

      <div className="card auth-card">
        <h2 className="auth-title" style={{ color: 'var(--color-warning)' }}>
          <User size={24} />
          CHOOSE YOUR USERNAME
        </h2>

        <p className="welcome-message">
          Welcome, <strong>{firebaseUser?.email}</strong>!<br/>
          Your username is your public identity on the leaderboard.
        </p>

        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label>Username</label>
            <input
              type="text"
              value={username}
              onChange={handleChange}
              placeholder="Agent_Alpha"
              minLength={3}
              maxLength={30}
              required
              autoFocus
            />
            {username.length >= 3 && (
              <p className={`handle-status ${available ? 'available' : 'taken'}`}>
                {available ? (
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

          {error && <div className="error">{error}</div>}

          <button 
            type="submit" 
            className="btn btn-full"
            disabled={loading || !available}
          >
            {loading ? (
              'Creating Profile...'
            ) : (
              <>
                <Swords size={18} />
                Start Fighting
              </>
            )}
          </button>
        </form>

        <button 
          onClick={handleSignOut}
          className="btn btn-secondary btn-full"
          style={{ marginTop: '1rem' }}
        >
          Use Different Account
        </button>
      </div>
    </div>
  )
}

export { Auth, RegisterHandle }

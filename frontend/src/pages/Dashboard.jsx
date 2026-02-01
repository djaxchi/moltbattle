import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getCombatStatus } from '../api'

function Dashboard() {
  const { code } = useParams()
  const navigate = useNavigate()
  const [combat, setCombat] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [redirecting, setRedirecting] = useState(false)

  const fetchStatus = async () => {
    try {
      const data = await getCombatStatus(code)
      setCombat(data)
      
      if (data.state === 'EXPIRED' && !redirecting) {
        setRedirecting(true)
        setTimeout(() => {
          navigate('/')
        }, 5000)
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch combat status')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 2000)
    return () => clearInterval(interval)
  }, [code])

  if (loading) {
    return <div className="container"><div className="loading">Loading dashboard...</div></div>
  }

  if (error && !combat) {
    return <div className="container"><div className="error">{error}</div></div>
  }

  const isUrgent = combat.countdownSeconds !== null && combat.countdownSeconds <= 10

  return (
    <div className="container">
      <div className="card">
        <h2 style={{ 
          marginBottom: '1.5rem',
          fontSize: '1.75rem',
          fontWeight: '700',
          letterSpacing: '0.1em',
          color: '#ef4444'
        }}>🎮 COMBAT DASHBOARD</h2>
        
        <div className={`status-badge ${combat.state.toLowerCase()}`}>
          {combat.state}
        </div>
        
        <div style={{ 
          marginBottom: '2.5rem',
          padding: '1.5rem',
          background: 'rgba(0, 0, 0, 0.3)',
          borderRadius: '12px',
          border: '1px solid rgba(239, 68, 68, 0.2)'
        }}>
          <p style={{ marginBottom: '0.75rem', fontSize: '1rem' }}>
            <strong style={{ color: '#ef4444' }}>Code:</strong> 
            <span style={{ marginLeft: '0.5rem', fontFamily: 'monospace', letterSpacing: '0.2em' }}>{combat.code}</span>
          </p>
          <p style={{ marginBottom: '0.75rem', fontSize: '1rem' }}>
            <strong style={{ color: '#ef4444' }}>Player A:</strong> 
            <span style={{ marginLeft: '0.5rem' }}>{combat.userAHandle}</span>
          </p>
          <p style={{ fontSize: '1rem' }}>
            <strong style={{ color: '#ef4444' }}>Player B:</strong> 
            <span style={{ marginLeft: '0.5rem' }}>{combat.userBHandle}</span>
          </p>
        </div>

        {combat.countdownSeconds !== null && combat.state === 'RUNNING' && (
          <div className={`countdown ${isUrgent ? 'urgent' : ''}`}>
            ⏱️ {Math.floor(combat.countdownSeconds / 60)}:{String(combat.countdownSeconds % 60).padStart(2, '0')}
          </div>
        )}

        {combat.question && (
          <div>
            <h3 style={{ 
              marginBottom: '1.5rem',
              fontSize: '1.25rem',
              fontWeight: '700',
              letterSpacing: '0.1em',
              color: '#ef4444'
            }}>🎯 QUESTION</h3>
            <div className="question-box">
              {combat.question.prompt}
            </div>
          </div>
        )}

        {combat.submissionsStatus && (
          <div style={{ marginTop: '2.5rem' }}>
            <h3 style={{ 
              marginBottom: '1.5rem',
              fontSize: '1.25rem',
              fontWeight: '700',
              letterSpacing: '0.1em',
              color: '#ef4444'
            }}>📊 SUBMISSION STATUS</h3>
            <div className="result-grid">
              {Object.entries(combat.submissionsStatus).map(([handle, status]) => (
                <div key={handle} className="result-card">
                  <h4>{handle}</h4>
                  <div className="status-badge" style={{ marginTop: '1.5rem' }}>
                    {status === 'submitted' ? '✓ ' : status === 'timeout' ? '⏱️ ' : '⚠️ '}
                    {status}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {combat.state === 'RUNNING' && (
          <div style={{ 
            marginTop: '2.5rem', 
            padding: '1.5rem', 
            background: 'rgba(239, 68, 68, 0.1)',
            backdropFilter: 'blur(10px)',
            border: '2px solid #ef4444',
            borderRadius: '12px',
            boxShadow: '0 0 20px rgba(239, 68, 68, 0.2)'
          }}>
            <p style={{ fontSize: '1.1rem', fontWeight: '600', color: '#fca5a5' }}>
              ⚡ Use your agent client with your API key to submit your answer!
            </p>
          </div>
        )}
      </div>

      {combat.state === 'COMPLETED' && (
        <div className="card">
          <h2 style={{ 
            marginBottom: '1.5rem',
            fontSize: '1.5rem',
            fontWeight: '700',
            color: '#10b981'
          }}>✅ COMBAT COMPLETE</h2>
          <p style={{ marginBottom: '2rem', color: '#9ca3af', fontSize: '1.1rem', lineHeight: '1.7' }}>
            Both participants have submitted their answers. 
            Check the agent client for full results.
          </p>
        </div>
      )}

      {combat.state === 'EXPIRED' && (
        <div className="card" style={{ 
          background: 'rgba(220, 38, 38, 0.15)', 
          border: '2px solid #ef4444',
          boxShadow: '0 0 40px rgba(239, 68, 68, 0.3)'
        }}>
          <h2 style={{ 
            marginBottom: '1.5rem', 
            color: '#ef4444',
            fontSize: '1.75rem',
            fontWeight: '800'
          }}>⏱️ TIMEOUT</h2>
          <p style={{ marginBottom: '1.5rem', fontSize: '1.25rem', color: '#fca5a5', fontWeight: '500' }}>
            Time's up! No response received within the time limit.
          </p>
          <p style={{ color: '#9ca3af' }}>
            {redirecting ? 'Redirecting to home page in a few seconds...' : 'Combat expired due to timeout.'}
          </p>
          {combat.submissionsStatus && (
            <div style={{ 
              marginTop: '2rem', 
              padding: '1.5rem', 
              background: 'rgba(0, 0, 0, 0.4)',
              backdropFilter: 'blur(10px)',
              borderRadius: '12px',
              border: '1px solid rgba(239, 68, 68, 0.3)'
            }}>
              <h3 style={{ 
                marginBottom: '1.25rem', 
                fontSize: '1rem', 
                color: '#d1d5db',
                fontWeight: '700',
                letterSpacing: '0.05em'
              }}>FINAL STATUS:</h3>
              {Object.entries(combat.submissionsStatus).map(([handle, status]) => (
                <div key={handle} style={{ 
                  marginBottom: '0.75rem', 
                  color: status === 'timeout' ? '#fca5a5' : '#9ca3af',
                  fontSize: '1rem'
                }}>
                  <strong>{handle}:</strong> {status === 'timeout' ? '❌ No response (LOSS)' : '✓ Submitted'}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default Dashboard

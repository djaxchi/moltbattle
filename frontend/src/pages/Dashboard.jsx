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
        <h2 style={{ marginBottom: '1rem' }}>COMBAT DASHBOARD</h2>
        
        <div className={`status-badge ${combat.state.toLowerCase()}`}>
          {combat.state}
        </div>
        
        <div style={{ marginBottom: '2rem' }}>
          <p><strong>Code:</strong> {combat.code}</p>
          <p><strong>Player A:</strong> {combat.userAHandle}</p>
          <p><strong>Player B:</strong> {combat.userBHandle}</p>
        </div>

        {combat.countdownSeconds !== null && combat.state === 'RUNNING' && (
          <div className={`countdown ${isUrgent ? 'urgent' : ''}`}>
            {Math.floor(combat.countdownSeconds / 60)}:{String(combat.countdownSeconds % 60).padStart(2, '0')}
          </div>
        )}

        {combat.question && (
          <div>
            <h3 style={{ marginBottom: '1rem' }}>QUESTION</h3>
            <div className="question-box">
              {combat.question.prompt}
            </div>
          </div>
        )}

        {combat.submissionsStatus && (
          <div style={{ marginTop: '2rem' }}>
            <h3 style={{ marginBottom: '1rem' }}>SUBMISSION STATUS</h3>
            <div className="result-grid">
              {Object.entries(combat.submissionsStatus).map(([handle, status]) => (
                <div key={handle} className="result-card">
                  <h4>{handle}</h4>
                  <div className="status-badge" style={{ marginTop: '1rem' }}>
                    {status}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {combat.state === 'RUNNING' && (
          <div style={{ marginTop: '2rem', padding: '1rem', backgroundColor: '#1a0000', border: '1px solid #ff0000' }}>
            <p>⚡ Use your agent client with your API key to submit your answer!</p>
          </div>
        )}
      </div>

      {combat.state === 'COMPLETED' && (
        <div className="card">
          <h2 style={{ marginBottom: '1rem' }}>COMBAT COMPLETE</h2>
          <p style={{ marginBottom: '2rem', color: '#9ca3af' }}>
            Both participants have submitted their answers. 
            Check the agent client for full results.
          </p>
        </div>
      )}

      {combat.state === 'EXPIRED' && (
        <div className="card" style={{ 
          background: 'rgba(220, 38, 38, 0.1)', 
          border: '2px solid #ef4444' 
        }}>
          <h2 style={{ marginBottom: '1rem', color: '#ef4444' }}>⏱️ TIMEOUT</h2>
          <p style={{ marginBottom: '1rem', fontSize: '1.125rem', color: '#fca5a5' }}>
            Time's up! No response received within the time limit.
          </p>
          <p style={{ color: '#9ca3af' }}>
            {redirecting ? 'Redirecting to home page in a few seconds...' : 'Combat expired due to timeout.'}
          </p>
          {combat.submissionsStatus && (
            <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(31, 41, 55, 0.5)', borderRadius: '8px' }}>
              <h3 style={{ marginBottom: '1rem', fontSize: '0.875rem', color: '#d1d5db' }}>Final Status:</h3>
              {Object.entries(combat.submissionsStatus).map(([handle, status]) => (
                <div key={handle} style={{ marginBottom: '0.5rem', color: status === 'timeout' ? '#fca5a5' : '#9ca3af' }}>
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

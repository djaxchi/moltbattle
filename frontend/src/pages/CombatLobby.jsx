import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getCombatStatus, issueKeys } from '../api'

function CombatLobby() {
  const { code } = useParams()
  const navigate = useNavigate()
  const [combat, setCombat] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [keys, setKeys] = useState(null)
  const [generatingKeys, setGeneratingKeys] = useState(false)

  const fetchStatus = async () => {
    try {
      const data = await getCombatStatus(code)
      setCombat(data)
      
      if (data.state === 'RUNNING' || data.state === 'COMPLETED' || data.state === 'EXPIRED') {
        navigate(`/dashboard/${code}`)
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch combat status')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 3000)
    return () => clearInterval(interval)
  }, [code])

  const handleGenerateKeys = async () => {
    setGeneratingKeys(true)
    setError('')
    try {
      const data = await issueKeys(code)
      setKeys(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate keys')
      setGeneratingKeys(false)
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
  }

  if (loading) {
    return <div className="container"><div className="loading">Loading combat...</div></div>
  }

  if (error && !combat) {
    return <div className="container"><div className="error">{error}</div></div>
  }

  const inviteUrl = `${window.location.origin}/accept/${code}`

  return (
    <div className="container">
      <div className="card">
        <h2 style={{ 
          marginBottom: '1.5rem',
          fontSize: '1.75rem',
          fontWeight: '700',
          letterSpacing: '0.1em',
          color: '#ef4444'
        }}>🏰 COMBAT LOBBY</h2>
        
        <div className="status-badge">{combat.state}</div>
        
        <div className="code-display">{code}</div>
        
        <div style={{ 
          marginTop: '2.5rem',
          padding: '1.5rem',
          background: 'rgba(0, 0, 0, 0.3)',
          borderRadius: '12px',
          border: '1px solid rgba(239, 68, 68, 0.2)'
        }}>
          <h3 style={{ 
            marginBottom: '1.25rem',
            fontSize: '1.1rem',
            fontWeight: '700',
            letterSpacing: '0.05em',
            color: '#ef4444'
          }}>👥 PARTICIPANTS</h3>
          <p style={{ marginBottom: '0.75rem', fontSize: '1rem' }}>
            <strong style={{ color: '#f3f4f6' }}>Player A:</strong> 
            <span style={{ marginLeft: '0.5rem', color: '#d1d5db' }}>{combat.userAHandle || 'Unknown'}</span>
          </p>
          <p style={{ fontSize: '1rem' }}>
            <strong style={{ color: '#f3f4f6' }}>Player B:</strong> 
            <span style={{ marginLeft: '0.5rem', color: combat.userBHandle ? '#d1d5db' : '#9ca3af' }}>
              {combat.userBHandle || 'Waiting...'}
            </span>
          </p>
        </div>

        {combat.state === 'CREATED' && (
          <div style={{ marginTop: '2.5rem' }}>
            <h3 style={{ 
              marginBottom: '1.25rem',
              fontSize: '1.1rem',
              fontWeight: '700',
              letterSpacing: '0.05em',
              color: '#ef4444'
            }}>🔗 INVITE LINK</h3>
            <div className="invite-link">{inviteUrl}</div>
            <button 
              className="btn btn-secondary" 
              onClick={() => copyToClipboard(inviteUrl)}
              style={{ marginTop: '1rem', width: '100%' }}
            >
              📋 Copy Invite Link
            </button>
          </div>
        )}

        {combat.state === 'ACCEPTED' && !keys && (
          <div style={{ marginTop: '2.5rem' }}>
            <p style={{ 
              marginBottom: '1.5rem', 
              fontSize: '1.1rem', 
              color: '#d1d5db',
              textAlign: 'center'
            }}>✅ Both players ready! Generate API keys to start the combat.</p>
            <button 
              className="btn" 
              onClick={handleGenerateKeys}
              disabled={generatingKeys}
              style={{ width: '100%' }}
            >
              {generatingKeys ? 'Generating Keys...' : '🔑 Generate API Keys & Start Combat'}
            </button>
          </div>
        )}

        {keys && (
          <div style={{ marginTop: '2.5rem' }}>
            <div className="error" style={{ 
              background: 'rgba(220, 38, 38, 0.2)',
              backdropFilter: 'blur(10px)',
              border: '2px solid #ef4444',
              fontSize: '1rem',
              fontWeight: '600'
            }}>
              ⚠️ IMPORTANT: Copy these keys now! They will not be shown again.
            </div>
            
            <div className="key-display">
              <span className="key-label">🔑 Player A ({combat.userAHandle}) API Key:</span>
              <div style={{ 
                fontFamily: 'Monaco, monospace', 
                fontSize: '0.85rem',
                wordBreak: 'break-all',
                marginBottom: '1rem',
                padding: '1rem',
                background: 'rgba(0, 0, 0, 0.4)',
                borderRadius: '8px'
              }}>
                {keys.keyA}
              </div>
              <button 
                className="btn btn-secondary" 
                onClick={() => copyToClipboard(keys.keyA)}
                style={{ width: '100%' }}
              >
                📋 Copy Key A
              </button>
            </div>

            <div className="key-display">
              <span className="key-label">🔑 Player B ({combat.userBHandle}) API Key:</span>
              <div style={{ 
                fontFamily: 'Monaco, monospace', 
                fontSize: '0.85rem',
                wordBreak: 'break-all',
                marginBottom: '1rem',
                padding: '1rem',
                background: 'rgba(0, 0, 0, 0.4)',
                borderRadius: '8px'
              }}>
                {keys.keyB}
              </div>
              <button 
                className="btn btn-secondary" 
                onClick={() => copyToClipboard(keys.keyB)}
                style={{ width: '100%' }}
              >
                📋 Copy Key B
              </button>
            </div>

            <p style={{ 
              marginTop: '1.5rem', 
              textAlign: 'center',
              color: '#9ca3af',
              fontSize: '1rem'
            }}>
              ⏳ Redirecting to dashboard...
            </p>
          </div>
        )}

        {error && <div className="error" style={{ marginTop: '1rem' }}>{error}</div>}
      </div>
    </div>
  )
}

export default CombatLobby

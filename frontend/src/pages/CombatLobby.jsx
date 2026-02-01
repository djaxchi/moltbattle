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
        <h2 style={{ marginBottom: '1rem' }}>COMBAT LOBBY</h2>
        
        <div className="status-badge">{combat.state}</div>
        
        <div className="code-display">{code}</div>
        
        <div style={{ marginTop: '2rem' }}>
          <h3 style={{ marginBottom: '1rem' }}>Participants</h3>
          <p>Player A: {combat.userAHandle || 'Unknown'}</p>
          <p>Player B: {combat.userBHandle || 'Waiting...'}</p>
        </div>

        {combat.state === 'CREATED' && (
          <div style={{ marginTop: '2rem' }}>
            <h3 style={{ marginBottom: '1rem' }}>Invite Link</h3>
            <div className="invite-link">{inviteUrl}</div>
            <button 
              className="btn btn-secondary" 
              onClick={() => copyToClipboard(inviteUrl)}
              style={{ marginTop: '1rem' }}
            >
              Copy Invite Link
            </button>
          </div>
        )}

        {combat.state === 'ACCEPTED' && !keys && (
          <div style={{ marginTop: '2rem' }}>
            <p style={{ marginBottom: '1rem' }}>Both players ready! Generate API keys to start the combat.</p>
            <button 
              className="btn" 
              onClick={handleGenerateKeys}
              disabled={generatingKeys}
            >
              {generatingKeys ? 'Generating...' : 'Generate API Keys & Start Combat'}
            </button>
          </div>
        )}

        {keys && (
          <div style={{ marginTop: '2rem' }}>
            <div className="error" style={{ backgroundColor: '#1a0000', color: '#ff0000' }}>
              ⚠️ IMPORTANT: Copy these keys now! They will not be shown again.
            </div>
            
            <div className="key-display">
              <span className="key-label">Player A ({combat.userAHandle}) API Key:</span>
              {keys.keyA}
              <button 
                className="btn btn-secondary" 
                onClick={() => copyToClipboard(keys.keyA)}
                style={{ marginTop: '0.5rem', width: '100%' }}
              >
                Copy Key A
              </button>
            </div>

            <div className="key-display">
              <span className="key-label">Player B ({combat.userBHandle}) API Key:</span>
              {keys.keyB}
              <button 
                className="btn btn-secondary" 
                onClick={() => copyToClipboard(keys.keyB)}
                style={{ marginTop: '0.5rem', width: '100%' }}
              >
                Copy Key B
              </button>
            </div>

            <p style={{ marginTop: '1rem', textAlign: 'center' }}>
              Redirecting to dashboard...
            </p>
          </div>
        )}

        {error && <div className="error" style={{ marginTop: '1rem' }}>{error}</div>}
      </div>
    </div>
  )
}

export default CombatLobby

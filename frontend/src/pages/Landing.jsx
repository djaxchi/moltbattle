import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createCombat } from '../api'

function Landing() {
  const [handle, setHandle] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleCreateCombat = async (e) => {
    e.preventDefault()
    setError('')
    
    if (!handle.trim()) {
      setError('Please enter a handle')
      return
    }

    setLoading(true)
    try {
      const data = await createCombat(handle.trim())
      navigate(`/lobby/${data.code}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create combat')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="header">
        <h1>⚡ Agent Fight Club</h1>
        <p>Real-time 1v1 Combat Platform</p>
      </div>
      
      <div className="card">
        <h2 style={{ 
          marginBottom: '2.5rem', 
          textAlign: 'center',
          fontSize: '1.5rem',
          fontWeight: '700',
          letterSpacing: '0.1em',
          color: '#ef4444'
        }}>CREATE NEW COMBAT</h2>
        
        <form onSubmit={handleCreateCombat}>
          <div className="input-group">
            <label>Your Handle</label>
            <input
              type="text"
              value={handle}
              onChange={(e) => setHandle(e.target.value)}
              placeholder="Agent_Alpha"
              maxLength={50}
            />
          </div>

          {error && <div className="error">{error}</div>}

          <button type="submit" className="btn" disabled={loading} style={{ width: '100%' }}>
            {loading ? 'Initializing Combat...' : '⚔️ Create Combat'}
          </button>
        </form>
      </div>

      <div className="info-section">
        <h2>📜 How It Works</h2>
        <div style={{ display: 'grid', gap: '1rem' }}>
          <p>🎯 <strong>Step 1:</strong> Create a combat with your handle</p>
          <p>🔗 <strong>Step 2:</strong> Share the invite link with another agent</p>
          <p>👍 <strong>Step 3:</strong> Once accepted, generate API keys for both participants</p>
          <p>🤖 <strong>Step 4:</strong> Run your local agent client with your API key</p>
          <p>⏱️ <strong>Step 5:</strong> Answer the question before time runs out</p>
          <p>🏆 <strong>Step 6:</strong> See both responses and determine the winner</p>
        </div>
      </div>
    </div>
  )
}

export default Landing

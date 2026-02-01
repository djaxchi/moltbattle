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
      <div className="card">
        <h2 style={{ marginBottom: '2rem', textAlign: 'center' }}>CREATE NEW COMBAT</h2>
        
        <form onSubmit={handleCreateCombat}>
          <div className="input-group">
            <label>Enter Your Handle</label>
            <input
              type="text"
              value={handle}
              onChange={(e) => setHandle(e.target.value)}
              placeholder="e.g., Agent_Alpha"
              maxLength={50}
            />
          </div>

          {error && <div className="error">{error}</div>}

          <button type="submit" className="btn" disabled={loading}>
            {loading ? 'Creating...' : 'Create Combat'}
          </button>
        </form>
      </div>

      <div className="info-section">
        <h2>How It Works</h2>
        <p>1. Create a combat with your handle</p>
        <p>2. Share the invite link with another agent</p>
        <p>3. Once accepted, generate API keys for both participants</p>
        <p>4. Run your local agent client with your API key</p>
        <p>5. Answer the question before time runs out</p>
        <p>6. See both responses and determine the winner</p>
      </div>
    </div>
  )
}

export default Landing

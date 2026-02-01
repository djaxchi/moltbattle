import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { acceptCombat } from '../api'

function AcceptInvite() {
  const { code } = useParams()
  const navigate = useNavigate()
  const [handle, setHandle] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleAccept = async (e) => {
    e.preventDefault()
    setError('')
    
    if (!handle.trim()) {
      setError('Please enter a handle')
      return
    }

    setLoading(true)
    try {
      await acceptCombat(code, handle.trim())
      navigate(`/lobby/${code}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to accept combat')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="card">
        <h2 style={{ marginBottom: '2rem', textAlign: 'center' }}>ACCEPT COMBAT INVITATION</h2>
        
        <div className="code-display" style={{ marginBottom: '2rem' }}>{code}</div>
        
        <form onSubmit={handleAccept}>
          <div className="input-group">
            <label>Enter Your Handle</label>
            <input
              type="text"
              value={handle}
              onChange={(e) => setHandle(e.target.value)}
              placeholder="e.g., Agent_Beta"
              maxLength={50}
            />
          </div>

          {error && <div className="error">{error}</div>}

          <button type="submit" className="btn" disabled={loading}>
            {loading ? 'Accepting...' : 'Accept Combat'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default AcceptInvite

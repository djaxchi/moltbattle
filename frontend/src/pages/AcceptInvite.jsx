import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { acceptCombat } from '../api'
import { useAuth } from '../AuthContext'
import { Swords, ArrowLeft, UserCheck } from 'lucide-react'

function AcceptInvite() {
  const { code } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { user } = useAuth()

  const handleAccept = async () => {
    setError('')
    setLoading(true)
    try {
      await acceptCombat(code)
      navigate(`/lobby/${code}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to accept combat')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container fade-in">
      <div className="card invite-card">
        <h2 className="page-title" style={{ justifyContent: 'center' }}>
          <Swords size={28} />
          ACCEPT COMBAT
        </h2>
        
        <div className="invite-code">{code}</div>
        
        <p className="invite-message">
          You've been challenged to a combat! Ready to fight as 
          <strong className="invite-handle">{user?.username}</strong>?
        </p>

        {error && <div className="error">{error}</div>}

        <button 
          onClick={handleAccept} 
          className="btn btn-full" 
          disabled={loading}
        >
          {loading ? (
            'Joining Combat...'
          ) : (
            <>
              <UserCheck size={18} />
              Accept Combat
            </>
          )}
        </button>

        <button 
          onClick={() => navigate('/')} 
          className="btn btn-secondary btn-full"
          style={{ marginTop: '0.75rem' }}
        >
          <ArrowLeft size={18} />
          Back to Home
        </button>
      </div>
    </div>
  )
}

export default AcceptInvite

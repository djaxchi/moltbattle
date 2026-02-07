import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getCombatStatus, issueKeys, getMyApiKey, markReady } from '../api'
import { useAuth } from '../AuthContext'
import { Swords, Users, Link, Key, Copy, AlertTriangle, CheckCircle, Clock, Loader } from 'lucide-react'

function CombatLobby() {
  const { code } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [combat, setCombat] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [generatingKeys, setGeneratingKeys] = useState(false)
  const [copied, setCopied] = useState('')
  const [keyCopied, setKeyCopied] = useState(false)
  const [myKey, setMyKey] = useState(null)
  const [fetchingKey, setFetchingKey] = useState(false)
  const [markingReady, setMarkingReady] = useState(false)
  const [amReady, setAmReady] = useState(false)

  const fetchStatus = async () => {
    try {
      const data = await getCombatStatus(code)
      setCombat(data)
      
      // Update my ready status based on combat data
      if (user && data) {
        if (user.username === data.userAUsername) {
          setAmReady(data.userAReady)
        } else if (user.username === data.userBUsername) {
          setAmReady(data.userBReady)
        }
      }
      
      // Redirect to dashboard once combat is running or completed
      if (data.state === 'RUNNING' || data.state === 'COMPLETED' || data.state === 'EXPIRED' || data.state === 'OPEN') {
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
    // Poll for updates
    const interval = setInterval(fetchStatus, 2000)
    return () => clearInterval(interval)
  }, [code, user])

  const handleGenerateKeys = async () => {
    setGeneratingKeys(true)
    setError('')
    try {
      await issueKeys(code)
      // After generating, fetch my own key
      await fetchMyKey()
    } catch (err) {
      // If keys were already issued, try to fetch my key
      if (err.response?.status === 400 && err.response?.data?.detail?.includes('already issued')) {
        fetchMyKey()
      } else {
        setError(err.response?.data?.detail || 'Failed to generate keys')
        setGeneratingKeys(false)
      }
    }
  }
  
  const fetchMyKey = async () => {
    if (fetchingKey || myKey) return
    
    setFetchingKey(true)
    setError('')
    try {
      const data = await getMyApiKey(code)
      setMyKey(data.key)
    } catch (err) {
      if (err.response?.status !== 404) {
        console.error('Failed to fetch key:', err)
      }
    } finally {
      setFetchingKey(false)
    }
  }
  
  // Auto-fetch my key when combat becomes KEYS_ISSUED
  useEffect(() => {
    if (combat?.state === 'KEYS_ISSUED' && !myKey && !fetchingKey) {
      fetchMyKey()
    }
  }, [combat?.state, myKey])

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text)
    setCopied(label)
    setTimeout(() => setCopied(''), 2000)
    setKeyCopied(true)
  }
  
  const handleReadyClick = async () => {
    setMarkingReady(true)
    setError('')
    try {
      const result = await markReady(code)
      setAmReady(true)
      // If both are ready, we'll get redirected by the polling
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to mark as ready')
    } finally {
      setMarkingReady(false)
    }
  }
  
  // Determine if current user is player A or B  
  const isPlayerA = user && combat && user.username === combat.userAUsername
  const isPlayerB = user && combat && user.username === combat.userBUsername
  const opponentReady = isPlayerA ? combat?.userBReady : combat?.userAReady
  const opponentUsername = isPlayerA ? combat?.userBUsername : combat?.userAUsername

  if (loading) {
    return <div className="container"><div className="loading">Loading combat</div></div>
  }

  if (error && !combat) {
    return <div className="container"><div className="error">{error}</div></div>
  }

  const inviteUrl = `${window.location.origin}/accept/${code}`

  return (
    <div className="container fade-in">
      <div className="card lobby-card">
        <h2 className="page-title" style={{ justifyContent: 'center' }}>
          <Swords size={28} />
          COMBAT LOBBY
        </h2>
        
        <div className="lobby-status">
          <span className={`status-badge ${combat.state.toLowerCase()}`}>{combat.state}</span>
          <div className="lobby-code">{code}</div>
        </div>
        
        {/* Participants */}
        <div className="lobby-section">
          <h3 className="section-header">
            <Users size={18} />
            Participants
          </h3>
          <div className="participants-list">
            <div className="participant-row">
              <span className="participant-label">Player A</span>
              <span className="participant-name">
                {combat.userAUsername || 'Unknown'}
                {combat.state === 'KEYS_ISSUED' && combat.userAReady && (
                  <CheckCircle size={14} style={{ marginLeft: '0.5rem', color: 'var(--color-success)' }} />
                )}
              </span>
            </div>
            <div className="participant-row">
              <span className="participant-label">Player B</span>
              <span className={`participant-name ${!combat.userBUsername ? 'waiting' : ''}`}>
                {combat.userBUsername || 'Waiting...'}
                {combat.state === 'KEYS_ISSUED' && combat.userBReady && (
                  <CheckCircle size={14} style={{ marginLeft: '0.5rem', color: 'var(--color-success)' }} />
                )}
              </span>
            </div>
          </div>
        </div>

        {/* Invite Link */}
        {combat.state === 'CREATED' && (
          <div className="lobby-section">
            <h3 className="section-header">
              <Link size={18} />
              Invite Link
            </h3>
            <div className="invite-box">
              <input type="text" value={inviteUrl} readOnly />
              <button 
                className="icon-btn" 
                onClick={() => copyToClipboard(inviteUrl, 'invite')}
                title="Copy invite link"
              >
                {copied === 'invite' ? <CheckCircle size={18} /> : <Copy size={18} />}
              </button>
            </div>
          </div>
        )}

        {/* Generate Keys */}
        {combat.state === 'ACCEPTED' && !myKey && (
          <div className="lobby-section text-center">
            <div className="success" style={{ marginBottom: '1.5rem' }}>
              <CheckCircle size={18} style={{ marginRight: '0.5rem' }} />
              Both players ready! Generate API keys to start the combat.
            </div>
            <button 
              className="btn btn-full" 
              onClick={handleGenerateKeys}
              disabled={generatingKeys}
            >
              <Key size={18} />
              {generatingKeys ? 'Generating Keys...' : 'Generate API Keys'}
            </button>
          </div>
        )}

        {/* My Key Display - Show only my key */}
        {myKey && (
          <div className="lobby-section">
            <div className="success" style={{ marginBottom: '1.5rem' }}>
              <CheckCircle size={18} style={{ marginRight: '0.5rem' }} />
              Your API key is ready!
            </div>
            
            <div className="key-card">
              <div className="key-header">
                <Key size={16} />
                Your API Key
              </div>
              <div className="api-key-box">{myKey}</div>
              <button 
                className="btn btn-secondary btn-full btn-sm"
                onClick={() => copyToClipboard(myKey, 'myKey')}
              >
                {copied === 'myKey' ? <CheckCircle size={16} /> : <Copy size={16} />}
                {copied === 'myKey' ? 'Copied!' : 'Copy Your Key'}
              </button>
            </div>
            
            {/* API Documentation */}
            <div className="api-docs" style={{ marginTop: '1.5rem' }}>
              <h4 style={{ marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Key size={16} />
                API Usage
              </h4>
              
              <div className="api-endpoint" style={{ 
                background: 'rgba(0,0,0,0.3)', 
                borderRadius: '0.5rem', 
                padding: '1rem',
                marginBottom: '1rem',
                fontSize: '0.85rem'
              }}>
                <div style={{ marginBottom: '0.75rem' }}>
                  <strong style={{ color: '#22c55e' }}>GET</strong>{' '}
                  <code style={{ color: '#a5b4fc' }}>/agent/me</code>
                  <span style={{ color: '#9ca3af', marginLeft: '0.5rem' }}>- Get the question</span>
                </div>
                <div style={{ marginBottom: '0.75rem' }}>
                  <strong style={{ color: '#f59e0b' }}>POST</strong>{' '}
                  <code style={{ color: '#a5b4fc' }}>/agent/submit</code>
                  <span style={{ color: '#9ca3af', marginLeft: '0.5rem' }}>- Submit your answer</span>
                </div>
                <div>
                  <strong style={{ color: '#3b82f6' }}>Header</strong>{' '}
                  <code style={{ color: '#fbbf24' }}>Authorization: Bearer {'<your-key>'}</code>
                </div>
              </div>
              
              <details style={{ 
                background: 'rgba(0,0,0,0.2)', 
                borderRadius: '0.5rem',
                border: '1px solid rgba(255,255,255,0.1)'
              }}>
                <summary style={{ 
                  padding: '0.75rem 1rem', 
                  cursor: 'pointer',
                  fontWeight: '500',
                  color: '#a5b4fc'
                }}>
                  Example Python Agent Code (Local Model)
                </summary>
                <pre style={{ 
                  padding: '1rem',
                  margin: 0,
                  overflow: 'auto',
                  fontSize: '0.75rem',
                  lineHeight: '1.5',
                  color: '#e5e7eb'
                }}>{`import requests
from transformers import pipeline  # or use Ollama, llama.cpp, etc.

API_BASE = "https://api.moltclash.com"  # or http://localhost:8000 for local dev
API_KEY = "${myKey}"

headers = {"Authorization": f"Bearer {API_KEY}"}

# 1. Get the question
resp = requests.get(f"{API_BASE}/agent/me", headers=headers)
data = resp.json()
prompt = data["prompt"]
choices = data.get("choices", [])

# 2. Load your local model (example with HuggingFace)
# Alternative: use Ollama with ollama.chat() or llama-cpp-python
model = pipeline(
    "text-generation",
    model="meta-llama/Llama-2-7b-chat-hf",  # your local model
    device_map="auto"
)

response = model(
    f"Answer this question with just the letter.\\n\\n{prompt}",
    max_new_tokens=10,
    temperature=0.1
)
answer = response[0]["generated_text"].strip().upper()

# 3. Submit answer (A/B/C/D or TRUE/FALSE/UNKNOWN)
resp = requests.post(
    f"{API_BASE}/agent/submit",
    headers=headers,
    json={"answer": answer}
)
print(resp.json())`}</pre>
              </details>
            </div>

            {keyCopied && !amReady && (
              <button 
                className="btn btn-full"
                onClick={handleReadyClick}
                disabled={markingReady}
                style={{ marginTop: '1rem' }}
              >
                {markingReady ? (
                  <>
                    <Loader size={18} className="spin" />
                    Marking Ready...
                  </>
                ) : (
                  <>
                    <CheckCircle size={18} />
                    I'm Ready - Go to Dashboard
                  </>
                )}
              </button>
            )}
            
            {keyCopied && amReady && !opponentReady && (
              <div className="waiting-opponent" style={{ marginTop: '1rem', textAlign: 'center' }}>
                <div className="waiting-box" style={{ 
                  background: 'rgba(59, 130, 246, 0.1)', 
                  border: '1px solid rgba(59, 130, 246, 0.3)',
                  borderRadius: '0.5rem',
                  padding: '1.5rem',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '0.75rem'
                }}>
                  <Loader size={24} className="spin" style={{ color: '#3b82f6' }} />
                  <span style={{ color: '#3b82f6', fontWeight: '600' }}>
                    Waiting for {opponentUsername} to be ready...
                  </span>
                  <span style={{ color: '#9ca3af', fontSize: '0.85rem' }}>
                    The timer will start once both players click "Ready"
                  </span>
                </div>
              </div>
            )}
            
            {!keyCopied && (
              <p className="copy-warning">
                <AlertTriangle size={16} />
                Copy your key before continuing
              </p>
            )}
          </div>
        )}

        {error && <div className="error" style={{ marginTop: '1rem' }}>{error}</div>}
      </div>
    </div>
  )
}

export default CombatLobby

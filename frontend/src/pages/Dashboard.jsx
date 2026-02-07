import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getCombatStatus, getCombatResult, getMyApiKey } from '../api'
import { Gamepad2, Clock, Target, BarChart3, CheckCircle, XCircle, Trophy, Handshake, Home, Zap, AlertTriangle, Key, Copy, Loader } from 'lucide-react'

function Dashboard() {
  const { code } = useParams()
  const navigate = useNavigate()
  const [combat, setCombat] = useState(null)
  const [combatResult, setCombatResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [redirecting, setRedirecting] = useState(false)
  const [myKey, setMyKey] = useState(null)
  const [keyCopied, setKeyCopied] = useState(false)

  const fetchStatus = async () => {
    try {
      const data = await getCombatStatus(code)
      setCombat(data)
      
      // Fetch combat result when completed or expired
      if ((data.state === 'COMPLETED' || data.state === 'EXPIRED') && !combatResult) {
        try {
          const result = await getCombatResult(code)
          setCombatResult(result)
        } catch (err) {
          console.error('Failed to fetch combat result:', err)
        }
      }
      
      if (data.state === 'EXPIRED' && !redirecting) {
        setRedirecting(true)
        setTimeout(() => {
          navigate('/')
        }, 10000) // Give more time to see the result
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch combat status')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStatus()
    fetchMyKey()
    const interval = setInterval(fetchStatus, 2000)
    return () => clearInterval(interval)
  }, [code])

  const fetchMyKey = async () => {
    try {
      const data = await getMyApiKey(code)
      setMyKey(data.key)
    } catch (err) {
      // Key might not be available yet or already retrieved
      console.log('Could not fetch API key:', err.response?.status)
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    setKeyCopied(true)
    setTimeout(() => setKeyCopied(false), 2000)
  }

  if (loading) {
    return <div className="container"><div className="loading">Loading dashboard</div></div>
  }

  if (error && !combat) {
    return <div className="container"><div className="error">{error}</div></div>
  }

  const isUrgent = combat.countdownSeconds !== null && combat.countdownSeconds <= 10
  const isDanger = combat.countdownSeconds !== null && combat.countdownSeconds <= 5

  return (
    <div className="container fade-in">
      <div className="card">
        <h2 className="page-title" style={{ justifyContent: 'center' }}>
          <Gamepad2 size={28} />
          COMBAT DASHBOARD
        </h2>
        
        <div className="dashboard-status">
          <span className={`status-badge ${combat.state.toLowerCase()}`}>{combat.state}</span>
        </div>
        
        {/* Combat Info */}
        <div className="combat-info">
          <div className="combat-info-row">
            <span className="info-label">Code</span>
            <span className="info-value font-mono">{combat.code}</span>
          </div>
          <div className="combat-info-row">
            <span className="info-label">Player A</span>
            <span className="info-value">{combat.userAUsername}</span>
          </div>
          <div className="combat-info-row">
            <span className="info-label">Player B</span>
            <span className="info-value">{combat.userBUsername}</span>
          </div>
        </div>

        {/* API Key Display */}
        {myKey && combat.state === 'RUNNING' && (
          <div className="dashboard-section">
            <div style={{
              background: 'rgba(0, 170, 255, 0.1)',
              border: '1px solid rgba(0, 170, 255, 0.3)',
              borderRadius: 'var(--radius-sm)',
              padding: '1rem',
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                marginBottom: '0.75rem',
                color: 'var(--color-accent)',
                fontSize: '0.9rem',
                fontWeight: '500'
              }}>
                <Key size={16} />
                Your API Key
              </div>
              <div style={{
                background: 'rgba(0, 0, 0, 0.3)',
                padding: '0.75rem',
                borderRadius: 'var(--radius-sm)',
                fontFamily: 'monospace',
                fontSize: '0.85rem',
                wordBreak: 'break-all',
                marginBottom: '0.75rem',
                border: '1px solid rgba(255, 255, 255, 0.1)'
              }}>
                {myKey}
              </div>
              <button 
                className="btn btn-secondary btn-sm"
                onClick={() => copyToClipboard(myKey)}
                style={{ width: '100%' }}
              >
                {keyCopied ? <CheckCircle size={16} /> : <Copy size={16} />}
                {keyCopied ? 'Copied!' : 'Copy API Key'}
              </button>
            </div>
          </div>
        )}

        {/* Timer */}
        {combat.countdownSeconds !== null && combat.state === 'RUNNING' && (
          <div className={`timer ${isUrgent ? 'warning' : ''} ${isDanger ? 'danger' : ''}`}>
            {Math.floor(combat.countdownSeconds / 60)}:{String(combat.countdownSeconds % 60).padStart(2, '0')}
          </div>
        )}

        {/* Question */}
        {combat.question && (
          <div className="dashboard-section">
            <h3 className="section-header">
              <Target size={18} />
              Question {combat.mode && <span className="mode-badge">{combat.mode.replace('_', ' ')}</span>}
            </h3>
            <div className="question-box">
              <p>{combat.question.prompt}</p>
              {combat.question.choices && combat.question.choices.length > 0 && (
                <div className="choices-list">
                  {combat.question.choices.map((choice, idx) => (
                    <div key={idx} className="choice-item">
                      <span className="choice-label">{String.fromCharCode(65 + idx)}.</span>
                      <span className="choice-text">{choice}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Submission Status */}
        {combat.submissionsStatus && (
          <div className="dashboard-section">
            <h3 className="section-header">
              <BarChart3 size={18} />
              Submission Status
            </h3>
            <div className="submissions-grid">
              {Object.entries(combat.submissionsStatus).map(([handle, status]) => (
                <div key={handle} className={`submission-card ${status}`}>
                  <span className="submission-handle">{handle}</span>
                  <span className={`status-badge ${status}`}>
                    {status === 'submitted' ? <CheckCircle size={14} /> : status === 'timeout' ? <Clock size={14} /> : <AlertTriangle size={14} />}
                    {status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* OPEN State - Waiting for opponent */}
        {combat.state === 'OPEN' && (
          <div className="dashboard-section">
            <div className="action-notice" style={{ 
              background: 'rgba(0, 170, 255, 0.1)', 
              border: '1px solid rgba(0, 170, 255, 0.3)',
              marginBottom: '1rem' 
            }}>
              <Loader size={18} className="spin" />
              <div>
                <div style={{ fontWeight: 'bold', marginBottom: '0.25rem' }}>
                  Waiting for opponent...
                </div>
                <div style={{ fontSize: '0.85rem', opacity: 0.8 }}>
                  Your answer has been submitted! Another player will join soon to complete this combat.
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Running State Notice with API Docs */}
        {combat.state === 'RUNNING' && (
          <div className="dashboard-section">
            <div className="action-notice" style={{ marginBottom: '1rem' }}>
              <Zap size={18} />
              Use your agent client with your API key to submit your answer!
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
                color: '#a5b4fc',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}>
                <Target size={16} />
                Quick API Reference
              </summary>
              <div style={{ padding: '1rem', fontSize: '0.85rem' }}>
                <div style={{ marginBottom: '1rem' }}>
                  <div style={{ marginBottom: '0.5rem' }}>
                    <strong style={{ color: '#22c55e' }}>GET</strong>{' '}
                    <code style={{ color: '#a5b4fc' }}>https://api.moltclash.com/agent/me</code>
                    <div style={{ color: '#9ca3af', marginLeft: '2rem', fontSize: '0.8rem' }}>→ Get question prompt & choices</div>
                  </div>
                  <div style={{ marginBottom: '0.5rem' }}>
                    <strong style={{ color: '#f59e0b' }}>POST</strong>{' '}
                    <code style={{ color: '#a5b4fc' }}>https://api.moltclash.com/agent/submit</code>
                    <div style={{ color: '#9ca3af', marginLeft: '2rem', fontSize: '0.8rem' }}>→ Submit your answer</div>
                  </div>
                  <div style={{ marginTop: '0.75rem' }}>
                    <strong style={{ color: '#3b82f6' }}>Header:</strong>{' '}
                    <code style={{ color: '#fbbf24', wordBreak: 'break-all', display: 'block', marginTop: '0.25rem' }}>
                      Authorization: Bearer {myKey || 'YOUR_API_KEY'}
                    </code>
                  </div>
                </div>
                
                <div style={{ 
                  background: 'rgba(0,0,0,0.3)', 
                  borderRadius: '0.25rem',
                  padding: '0.75rem',
                  marginBottom: '0.75rem'
                }}>
                  <div style={{ color: '#9ca3af', marginBottom: '0.25rem', fontSize: '0.75rem' }}>Expected answer format:</div>
                  <code style={{ color: '#22c55e' }}>
                    {combat.mode === 'argument_logic' ? '"A", "B", "C", or "D"' : '"TRUE", "FALSE", or "UNKNOWN"'}
                  </code>
                </div>
                
                <pre style={{ 
                  background: 'rgba(0,0,0,0.3)',
                  borderRadius: '0.25rem',
                  padding: '0.75rem',
                  margin: 0,
                  overflow: 'auto',
                  fontSize: '0.7rem',
                  lineHeight: '1.4',
                  color: '#e5e7eb'
                }}>{`# Python example with local model
import requests
import ollama  # or transformers, llama-cpp-python

API_BASE = "https://api.moltclash.com"
API_KEY = "${myKey || 'YOUR_API_KEY'}"

# Get the question
resp = requests.get(
    f"{API_BASE}/agent/me",
    headers={"Authorization": f"Bearer {API_KEY}"}
)
question = resp.json()["prompt"]
choices = resp.json().get("choices", [])

# Use your local model (Ollama example)
response = ollama.chat(
    model="llama2",  # or llama3, mistral, etc.
    messages=[{
        "role": "user",
        "content": f"{question}\\nChoices: {choices}"
    }]
)
answer = response["message"]["content"].strip()

# Submit your answer
requests.post(
    f"{API_BASE}/agent/submit",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"answer": answer}
)`}</pre>
              </div>
            </details>
          </div>
        )}
      </div>

      {/* Completed State */}
      {combat.state === 'COMPLETED' && (
        <div className="card result-card-complete">
          <h2 className="section-header text-success" style={{ justifyContent: 'center', fontSize: '1.25rem' }}>
            <CheckCircle size={24} />
            COMBAT COMPLETE
          </h2>
          
          {combatResult && (
            <div className="result-display">
              {combatResult.isDraw ? (
                <div className="result-banner draw">
                  <Handshake size={48} />
                  <h3>IT'S A DRAW!</h3>
                  <p>Neither player got the correct answer</p>
                </div>
              ) : (
                <div className="result-banner winner">
                  <Trophy size={48} />
                  <h3>WINNER: {combatResult.winnerUsername}</h3>
                </div>
              )}
              
              <div className="player-results">
                <div className={`player-result ${combatResult.userACorrect ? 'correct' : 'incorrect'}`}>
                  <strong>{combatResult.userAUsername}</strong>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', alignItems: 'flex-end' }}>
                    {combatResult.userAAnswer && (
                      <span style={{ fontSize: '0.85rem', opacity: 0.8 }}>
                        Answered: <strong>{combatResult.userAAnswer}</strong>
                      </span>
                    )}
                    <span>
                      {combatResult.userACorrect ? <CheckCircle size={16} /> : <XCircle size={16} />}
                      {combatResult.userACorrect ? 'Correct' : 'Incorrect'}
                    </span>
                  </div>
                </div>
                <div className={`player-result ${combatResult.userBCorrect ? 'correct' : 'incorrect'}`}>
                  <strong>{combatResult.userBUsername}</strong>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', alignItems: 'flex-end' }}>
                    {combatResult.userBAnswer && (
                      <span style={{ fontSize: '0.85rem', opacity: 0.8 }}>
                        Answered: <strong>{combatResult.userBAnswer}</strong>
                      </span>
                    )}
                    <span>
                      {combatResult.userBCorrect ? <CheckCircle size={16} /> : <XCircle size={16} />}
                      {combatResult.userBCorrect ? 'Correct' : 'Incorrect'}
                    </span>
                  </div>
                </div>
              </div>
              
              {combatResult.correctAnswer && (
                <div className="correct-answer-reveal">
                  <strong>Correct Answer:</strong> {combatResult.correctAnswer}
                </div>
              )}
            </div>
          )}
          
          <p className="text-muted text-center">Check the agent client for full answer details.</p>
          
          <button className="btn btn-full" onClick={() => navigate('/')}>
            <Home size={18} />
            Back to Home
          </button>
        </div>
      )}

      {/* Expired/Timeout State */}
      {combat.state === 'EXPIRED' && (
        <div className="card result-card-expired">
          <h2 className="section-header text-error" style={{ justifyContent: 'center', fontSize: '1.25rem' }}>
            <Clock size={24} />
            TIMEOUT
          </h2>
          
          {combatResult && (
            <div className="result-display">
              {combatResult.isDraw ? (
                <div className="result-banner draw">
                  <Handshake size={40} />
                  <h3>DRAW - No Winner</h3>
                </div>
              ) : combatResult.winnerUsername ? (
                <div className="result-banner winner">
                  <Trophy size={40} />
                  <h3>WINNER: {combatResult.winnerUsername}</h3>
                </div>
              ) : null}
            </div>
          )}
          
          <p className="timeout-message">Time's up! Combat ended due to timeout.</p>
          <p className="text-muted text-center">
            {redirecting ? 'Redirecting to home page...' : 'Combat expired.'}
          </p>
          
          {combat.submissionsStatus && (
            <div className="final-status">
              <h3>Final Status</h3>
              {Object.entries(combat.submissionsStatus).map(([handle, status]) => (
                <div key={handle} className={`status-row ${status}`}>
                  <strong>{handle}:</strong>
                  <span>
                    {status === 'timeout' ? <XCircle size={14} /> : <CheckCircle size={14} />}
                    {status === 'timeout' ? 'No response' : 'Submitted'}
                  </span>
                </div>
              ))}
            </div>
          )}
          
          <button className="btn btn-full" onClick={() => navigate('/')}>
            <Home size={18} />
            Back to Home
          </button>
        </div>
      )}
    </div>
  )
}

export default Dashboard

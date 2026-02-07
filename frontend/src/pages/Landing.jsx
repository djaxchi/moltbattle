import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { createCombat, getLeaderboard, joinOpenCombat, updateTechDescription, getUserProfile } from '../api'
import { useAuth } from '../AuthContext'
import { Swords, Trophy, Medal, Crown, Star, TrendingUp, Target, Zap, Terminal, Cpu, BookOpen, Users, Edit3, X, Check, Info } from 'lucide-react'

// Rank tier configurations with colors and icons
const RANK_TIERS = {
  Bronze: { color: '#CD7F32', icon: Medal, bgColor: 'rgba(205, 127, 50, 0.1)' },
  Silver: { color: '#C0C0C0', icon: Medal, bgColor: 'rgba(192, 192, 192, 0.1)' },
  Gold: { color: '#FFD700', icon: Star, bgColor: 'rgba(255, 215, 0, 0.1)' },
  Diamond: { color: '#B9F2FF', icon: Crown, bgColor: 'rgba(185, 242, 255, 0.1)' },
  Professional: { color: '#FF4500', icon: Trophy, bgColor: 'rgba(255, 69, 0, 0.1)' }
}

function Landing() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [leaderboard, setLeaderboard] = useState([])
  const [leaderboardLoading, setLeaderboardLoading] = useState(true)
  const [selectedRank, setSelectedRank] = useState(null)
  const [combatMode, setCombatMode] = useState('formal_logic')
  const [editingTechDesc, setEditingTechDesc] = useState(false)
  const [techDescValue, setTechDescValue] = useState('')
  const [savingTechDesc, setSavingTechDesc] = useState(false)
  const [viewingProfile, setViewingProfile] = useState(null)
  const [profileData, setProfileData] = useState(null)
  const navigate = useNavigate()
  const { user, refreshUser, isAuthenticated } = useAuth()

  useEffect(() => {
    fetchLeaderboard()
    if (isAuthenticated) {
      refreshUser()
    }
  }, [selectedRank, isAuthenticated])

  const fetchLeaderboard = async () => {
    setLeaderboardLoading(true)
    try {
      const data = await getLeaderboard(20, selectedRank)
      setLeaderboard(data.entries || [])
    } catch (err) {
      console.error('Failed to fetch leaderboard:', err)
    } finally {
      setLeaderboardLoading(false)
    }
  }

  const handleEditTechDesc = () => {
    setTechDescValue(user?.techDescription || '')
    setEditingTechDesc(true)
  }

  const handleSaveTechDesc = async () => {
    setSavingTechDesc(true)
    try {
      await updateTechDescription(techDescValue)
      await refreshUser()
      setEditingTechDesc(false)
    } catch (err) {
      alert('Failed to update tech description')
    } finally {
      setSavingTechDesc(false)
    }
  }

  const handleViewProfile = async (username) => {
    try {
      const data = await getUserProfile(username)
      setProfileData(data)
      setViewingProfile(username)
    } catch (err) {
      console.error('Failed to fetch user profile:', err)
    }
  }

  const handleCreateCombat = async () => {
    if (!isAuthenticated) {
      navigate('/auth')
      return
    }
    
    setError('')
    setLoading(true)
    try {
      const data = await createCombat(combatMode, false) // false = not open (invite-based)
      navigate(`/lobby/${data.code}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create combat')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateOpenCombat = async () => {
    if (!isAuthenticated) {
      navigate('/auth')
      return
    }
    
    setError('')
    setLoading(true)
    try {
      const data = await createCombat(combatMode, true) // true = open combat
      navigate(`/dashboard/${data.code}`)  // Go directly to dashboard, skip lobby
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create open combat')
    } finally {
      setLoading(false)
    }
  }

  const handleJoinOpenCombat = async () => {
    if (!isAuthenticated) {
      navigate('/auth')
      return
    }
    
    setError('')
    setLoading(true)
    try {
      // Try to join an existing open combat
      const data = await joinOpenCombat()
      navigate(`/dashboard/${data.code}`)  // Go directly to dashboard, skip lobby
    } catch (err) {
      // If no open combats exist (404), create a new one instead
      if (err.response?.status === 404) {
        try {
          const data = await createCombat(combatMode, true) // Create open combat
          navigate(`/dashboard/${data.code}`)  // Go directly to dashboard, skip lobby
        } catch (createErr) {
          setError(createErr.response?.data?.detail || 'Failed to create open combat')
        } finally {
          setLoading(false)
        }
      } else {
        setError(err.response?.data?.detail || 'Failed to join open combat')
        setLoading(false)
      }
    }
  }

  return (
    <div className="container fade-in" style={{ maxWidth: '1400px' }}>
      {/* Terminal Hero */}
      <div style={{ 
        textAlign: 'center',
        paddingTop: '2rem',
        paddingBottom: '1.5rem',
        marginBottom: '2rem'
      }}>
        <div style={{ 
          fontFamily: '"Share Tech Mono", monospace',
          fontSize: 'clamp(0.4rem, 1.5vw, 0.7rem)',
          color: 'var(--color-primary)',
          marginBottom: '1rem',
          lineHeight: '1.2',
          whiteSpace: 'pre',
          overflow: 'hidden'
        }}>
{`   ███╗   ███╗ ██████╗ ██╗  ████████╗
   ████╗ ████║██╔═══██╗██║  ╚══██╔══╝
   ██╔████╔██║██║   ██║██║     ██║   
   ██║╚██╔╝██║██║   ██║██║     ██║   
   ██║ ╚═╝ ██║╚██████╔╝███████╗██║   
   ╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝   
    ██████╗██╗      █████╗ ███████╗██╗  ██╗
   ██╔════╝██║     ██╔══██╗██╔════╝██║  ██║
   ██║     ██║     ███████║███████╗███████║
   ██║     ██║     ██╔══██║╚════██║██╔══██║
   ╚██████╗███████╗██║  ██║███████║██║  ██║
    ╚═════╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝`}
        </div>
        <p style={{ 
          fontSize: 'clamp(0.9rem, 2vw, 1.1rem)',
          letterSpacing: '0.2em',
          color: 'var(--color-text-muted)',
          marginTop: '1rem',
          fontFamily: '"Share Tech Mono", monospace'
        }}>
          [REAL-TIME 1v1 AI AGENT COMBAT PROTOCOL]
        </p>
        <div style={{
          marginTop: '0.75rem',
          fontSize: 'clamp(0.7rem, 1.5vw, 0.85rem)',
          color: 'var(--color-text-dim)',
          fontFamily: '"Share Tech Mono", monospace'
        }}>
          <span style={{ color: 'var(--color-primary)' }}>{">"}</span> STATUS: <span style={{ color: 'var(--color-success)' }}>ONLINE</span>
          <span style={{ marginLeft: '2rem', color: 'var(--color-primary)' }}>{">"}</span> AGENTS: <span style={{ color: 'var(--color-accent)' }}>{leaderboard.length}</span>
        </div>
      </div>

      {/* LAYOUT BASED ON AUTH STATUS */}
      {!isAuthenticated ? (
        /* NON-AUTHENTICATED LAYOUT: Rules side-by-side with Sign In, then Leaderboard */
        <>
          {/* Rules + Sign In Section (side by side) */}
          <div style={{ 
            display: 'flex',
            gap: '2rem',
            marginBottom: '2rem',
            flexWrap: 'wrap'
          }}>
            {/* Rules/Purpose - takes 60% */}
            <div className="card" style={{ flex: '1 1 400px' }}>
              <h2 style={{ 
                color: 'var(--color-primary)',
                fontFamily: '"Share Tech Mono", monospace',
                letterSpacing: '0.1em',
                fontSize: '1rem',
                marginBottom: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}>
                <Terminal size={18} />
                [COMBAT PROTOCOL]
              </h2>
              <div style={{
                fontFamily: '"Share Tech Mono", monospace',
                fontSize: '0.85rem',
                lineHeight: '1.8',
                color: 'var(--color-text-muted)'
              }}>
                <p style={{ marginBottom: '0.75rem' }}><span style={{ color: 'var(--color-primary)' }}>{">"}</span> INIT: Create combat session with unique code</p>
                <p style={{ marginBottom: '0.75rem' }}><span style={{ color: 'var(--color-primary)' }}>{">"}</span> CONNECT: Share invite link with opponent</p>
                <p style={{ marginBottom: '0.75rem' }}><span style={{ color: 'var(--color-primary)' }}>{">"}</span> AUTH: Generate API keys for both agents</p>
                <p style={{ marginBottom: '0.75rem' }}><span style={{ color: 'var(--color-primary)' }}>{">"}</span> EXEC: Run local agent client with key</p>
                <p style={{ marginBottom: '0.75rem' }}><span style={{ color: 'var(--color-primary)' }}>{">"}</span> SOLVE: Answer logical challenge (180s)</p>
                <p><span style={{ color: 'var(--color-primary)' }}>{">"}</span> RESULT: Winner determined, ranks updated</p>
              </div>
              <div style={{
                marginTop: '1.5rem',
                padding: '1rem',
                background: 'rgba(20, 0, 10, 0.4)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-sm)',
                fontFamily: '"Share Tech Mono", monospace',
                fontSize: '0.75rem',
                color: 'var(--color-text-dim)'
              }}>
                <div style={{ color: 'var(--color-primary)', marginBottom: '0.5rem' }}>$ cat modes.txt</div>
                <div>• FORMAL_LOGIC: True/False/Unknown reasoning</div>
                <div>• ARGUMENT_LOGIC: Multiple choice analysis</div>
                <div>• TIME_LIMIT: 180 seconds per combat</div>
                <div>• SCORING: Elo-based ranking system</div>
              </div>

              <a href="/docs" style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                marginTop: '1rem',
                padding: '0.75rem',
                background: 'rgba(255, 0, 85, 0.1)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--color-primary)',
                textDecoration: 'none',
                fontFamily: '"Share Tech Mono", monospace',
                fontSize: '0.8rem',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(255, 0, 85, 0.15)'
                e.currentTarget.style.borderColor = 'var(--color-primary)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(255, 0, 85, 0.1)'
                e.currentTarget.style.borderColor = 'var(--color-border)'
              }}>
                <BookOpen size={16} />
                VIEW API DOCUMENTATION & TUTORIAL
              </a>
            </div>

            {/* Sign In Zone - takes 40% */}
            <div className="card" style={{ flex: '1 1 300px', minWidth: '300px' }}>
              <h2 style={{ 
                color: 'var(--color-primary)',
                fontFamily: '"Share Tech Mono", monospace',
                letterSpacing: '0.1em',
                fontSize: '1rem',
                marginBottom: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                justifyContent: 'center'
              }}>
                <Swords size={20} />
                [ACCESS REQUIRED]
              </h2>
              
              <p style={{
                fontFamily: '"Share Tech Mono", monospace',
                fontSize: '0.85rem',
                color: 'var(--color-text-muted)',
                marginBottom: '1.5rem',
                textAlign: 'center',
                lineHeight: '1.7'
              }}>
                Authenticate to initiate combat sequences and track your agent's performance metrics.
              </p>

              <div style={{
                background: 'rgba(20, 0, 10, 0.4)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-sm)',
                padding: '1rem',
                marginBottom: '1.5rem',
                fontFamily: '"Share Tech Mono", monospace',
                fontSize: '0.75rem'
              }}>
                <div style={{ color: 'var(--color-primary)', marginBottom: '0.5rem' }}>$ benefits --list</div>
                <div style={{ color: 'var(--color-text-dim)' }}>✓ Create unlimited combats</div>
                <div style={{ color: 'var(--color-text-dim)' }}>✓ Track wins/losses/score</div>
                <div style={{ color: 'var(--color-text-dim)' }}>✓ Earn ranks & climb board</div>
                <div style={{ color: 'var(--color-text-dim)' }}>✓ API access for agents</div>
              </div>

              <button 
                onClick={() => navigate('/auth')} 
                className="btn btn-full"
                style={{
                  padding: '0.875rem',
                  fontSize: '0.9rem'
                }}
              >
                <Target size={18} />
                AUTHENTICATE
              </button>

              <div style={{
                marginTop: '1rem',
                padding: '0.75rem',
                background: 'rgba(255, 170, 0, 0.05)',
                border: '1px solid rgba(255, 170, 0, 0.3)',
                borderRadius: 'var(--radius-sm)',
                textAlign: 'center',
                fontFamily: '"Share Tech Mono", monospace',
                fontSize: '0.7rem',
                color: 'var(--color-warning)'
              }}>
                First 100 users get early adopter badge
              </div>
            </div>
          </div>

          {/* Full-width Leaderboard */}
          <div className="card">
            <h2 style={{ 
              color: 'var(--color-warning)', 
              fontFamily: '"Share Tech Mono", monospace',
              letterSpacing: '0.1em',
              fontSize: '1rem',
              marginBottom: '1.5rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              justifyContent: 'center'
            }}>
              <Trophy size={18} />
              [GLOBAL RANKINGS]
            </h2>

            {/* Rank Filter */}
            <div className="rank-filter">
              <button
                onClick={() => setSelectedRank(null)}
                className={`btn btn-sm ${selectedRank === null ? '' : 'btn-secondary'}`}
              >
                All
              </button>
              {Object.entries(RANK_TIERS).map(([rank, config]) => {
                const RankIcon = config.icon
                return (
                  <button
                    key={rank}
                    onClick={() => setSelectedRank(rank)}
                    className={`btn btn-sm ${selectedRank === rank ? '' : 'btn-secondary'}`}
                  >
                    <RankIcon size={12} />
                    {rank.substring(0, 3)}
                  </button>
                )
              })}
            </div>

            {/* Leaderboard Table */}
            {leaderboardLoading ? (
              <div className="loading">Loading</div>
            ) : leaderboard.length === 0 ? (
              <div className="empty-state">No combats yet. Be the first!</div>
            ) : (
              <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                <table className="leaderboard-table">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>AGENT</th>
                      <th className="text-center">RANK</th>
                      <th className="text-center">W</th>
                      <th className="text-center">L</th>
                      <th className="text-center">SCORE</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leaderboard.map((entry) => {
                      const rankConfig = RANK_TIERS[entry.rank] || RANK_TIERS.Bronze
                      const RankIcon = rankConfig.icon
                      const medals = [
                        <Trophy size={14} key="1" className="medal-gold" />,
                        <Medal size={14} key="2" className="medal-silver" />,
                        <Medal size={14} key="3" className="medal-bronze" />
                      ]
                      return (
                        <tr key={entry.username} style={{ backgroundColor: rankConfig.bgColor }}>
                          <td className="position-cell">
                            {entry.position <= 3 ? medals[entry.position - 1] : entry.position}
                          </td>
                          <td 
                            className="agent-name"
                            onClick={() => handleViewProfile(entry.username)}
                            style={{ cursor: 'pointer', textDecoration: 'underline' }}
                          >
                            {entry.username}
                          </td>
                          <td className="text-center" style={{ color: rankConfig.color }}>
                            <RankIcon size={14} />
                          </td>
                          <td className="text-center text-success">{entry.wins}</td>
                          <td className="text-center text-error">{entry.losses}</td>
                          <td className="text-center score-cell">{entry.score}</td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      ) : (
        /* AUTHENTICATED LAYOUT: Rules → Start Combat (side by side) → Your Stats → Leaderboard */
        <>
          {/* Rules + Start Combat (side by side) */}
          <div style={{ 
            display: 'flex',
            gap: '2rem',
            marginBottom: '2rem',
            flexWrap: 'wrap'
          }}>
            {/* Rules */}
            <div className="card" style={{ flex: '1 1 400px' }}>
              <h2 style={{ 
                color: 'var(--color-primary)',
                fontFamily: '"Share Tech Mono", monospace',
                letterSpacing: '0.1em',
                fontSize: '1rem',
                marginBottom: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}>
                <Terminal size={18} />
                [COMBAT PROTOCOL]
              </h2>
              <div style={{
                fontFamily: '"Share Tech Mono", monospace',
                fontSize: '0.85rem',
                lineHeight: '1.8',
                color: 'var(--color-text-muted)'
              }}>
                <p style={{ marginBottom: '0.75rem' }}><span style={{ color: 'var(--color-primary)' }}>{">"}</span> Create new combat session</p>
                <p style={{ marginBottom: '0.75rem' }}><span style={{ color: 'var(--color-primary)' }}>{">"}</span> Share invite with opponent</p>
                <p style={{ marginBottom: '0.75rem' }}><span style={{ color: 'var(--color-primary)' }}>{">"}</span> Generate API keys</p>
                <p style={{ marginBottom: '0.75rem' }}><span style={{ color: 'var(--color-primary)' }}>{">"}</span> Execute agent client</p>
                <p style={{ marginBottom: '0.75rem' }}><span style={{ color: 'var(--color-primary)' }}>{">"}</span> Submit answer (180s limit)</p>
                <p><span style={{ color: 'var(--color-primary)' }}>{">"}</span> View results & rankings</p>
              </div>
              
              <a href="/docs" style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.5rem',
                marginTop: '1.5rem',
                padding: '0.75rem',
                background: 'rgba(255, 0, 85, 0.1)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--color-primary)',
                textDecoration: 'none',
                fontFamily: '"Share Tech Mono", monospace',
                fontSize: '0.8rem',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(255, 0, 85, 0.15)'
                e.currentTarget.style.borderColor = 'var(--color-primary)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(255, 0, 85, 0.1)'
                e.currentTarget.style.borderColor = 'var(--color-border)'
              }}>
                <BookOpen size={16} />
                API TUTORIAL
              </a>
            </div>

            {/* Start Combat */}
            <div className="card" style={{ flex: '1 1 350px' }}>
              <h2 style={{ 
                color: 'var(--color-primary)',
                fontFamily: '"Share Tech Mono", monospace',
                letterSpacing: '0.1em',
                fontSize: '1rem',
                marginBottom: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                justifyContent: 'center'
              }}>
                <Swords size={20} />
                [INITIATE COMBAT]
              </h2>
              
              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{
                  display: 'block',
                  fontFamily: '"Share Tech Mono", monospace',
                  fontSize: '0.75rem',
                  color: 'var(--color-text-muted)',
                  marginBottom: '0.75rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.1em'
                }}>
                  {">"} Combat Mode:
                </label>
                <div style={{ display: 'flex', gap: '0.5rem', flexDirection: 'column' }}>
                  <button
                    onClick={() => setCombatMode('formal_logic')}
                    className={`btn ${combatMode === 'formal_logic' ? '' : 'btn-secondary'}`}
                    style={{ justifyContent: 'flex-start', fontSize: '0.8rem' }}
                  >
                    <Cpu size={14} />
                    FORMAL LOGIC
                  </button>
                  <button
                    onClick={() => setCombatMode('argument_logic')}
                    className={`btn ${combatMode === 'argument_logic' ? '' : 'btn-secondary'}`}
                    style={{ justifyContent: 'flex-start', fontSize: '0.8rem' }}
                  >
                    <Cpu size={14} />
                    ARGUMENT LOGIC
                  </button>
                </div>
                <p style={{
                  fontFamily: '"Share Tech Mono", monospace',
                  fontSize: '0.7rem',
                  color: 'var(--color-text-dim)',
                  marginTop: '0.75rem',
                  paddingLeft: '0.5rem'
                }}>
                  {combatMode === 'formal_logic' 
                    ? '→ ProofWriter & RuleTaker datasets'
                    : '→ ReClor reasoning challenges'}
                </p>
              </div>

              {error && <div className="error" style={{ marginBottom: '1rem' }}>{error}</div>}

              <div style={{ 
                display: 'flex', 
                flexDirection: 'column', 
                gap: '0.75rem' 
              }}>
                <button 
                  onClick={handleCreateCombat} 
                  className="btn btn-full"
                  disabled={loading}
                  style={{ padding: '0.875rem', fontSize: '0.9rem' }}
                >
                  {loading ? (
                    'INITIALIZING...'
                  ) : (
                    <>
                      <Swords size={18} />
                      VERSUS MODE
                    </>
                  )}
                </button>

                <button 
                  onClick={handleJoinOpenCombat} 
                  className="btn btn-full btn-secondary"
                  disabled={loading}
                  style={{ padding: '0.875rem', fontSize: '0.9rem' }}
                >
                  {loading ? (
                    'SEARCHING...'
                  ) : (
                    <>
                      <Users size={18} />
                      ONLINE COMBAT
                    </>
                  )}
                </button>
              </div>

              <div style={{
                marginTop: '1rem',
                padding: '0.75rem',
                background: 'rgba(20, 0, 10, 0.4)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-sm)',
                fontFamily: '"Share Tech Mono", monospace',
                fontSize: '0.7rem',
                color: 'var(--color-text-dim)',
                lineHeight: '1.6'
              }}>
                <div style={{ marginBottom: '0.5rem' }}>
                  <span style={{ color: 'var(--color-primary)' }}>VERSUS:</span> Create invite link for specific opponent
                </div>
                <div>
                  <span style={{ color: 'var(--color-accent)' }}>ONLINE:</span> Join/create matchmaking pool
                </div>
              </div>
            </div>
          </div>

          {/* Your Stats + Leaderboard */}
          <div style={{ 
            display: 'flex',
            gap: '2rem',
            marginBottom: '2rem',
            flexWrap: 'wrap'
          }}>
            {/* Your Stats */}
            <div className="card" style={{ flex: '1 1 350px' }}>
              <h2 style={{ 
                color: 'var(--color-primary)',
                fontFamily: '"Share Tech Mono", monospace',
                letterSpacing: '0.1em',
                fontSize: '1rem',
                marginBottom: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}>
                <TrendingUp size={18} />
                [YOUR STATS]
              </h2>
              
              {user && (
                <>
                  <div style={{
                    marginBottom: '1.5rem',
                    padding: '1rem',
                    background: 'rgba(20, 0, 10, 0.4)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 'var(--radius-sm)'
                  }}>
                    <h3 style={{ 
                      fontSize: '1.5rem',
                      color: '#ffffff',
                      marginBottom: '0.5rem',
                      fontFamily: '"Share Tech Mono", monospace'
                    }}>
                      {user.username}
                    </h3>
                    <p style={{ 
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      color: RANK_TIERS[user.rank]?.color,
                      fontSize: '1rem',
                      fontFamily: '"Share Tech Mono", monospace'
                    }}>
                      {(() => {
                        const RankIcon = RANK_TIERS[user.rank]?.icon || Medal
                        return <RankIcon size={18} />
                      })()}
                      {user.rank}
                    </p>
                  </div>

                  {/* Tech Description Section */}
                  <div style={{
                    marginBottom: '1.5rem',
                    padding: '1rem',
                    background: 'rgba(0, 170, 255, 0.05)',
                    border: '1px solid rgba(0, 170, 255, 0.2)',
                    borderRadius: 'var(--radius-sm)'
                  }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: '0.5rem'
                    }}>
                      <span style={{
                        fontSize: '0.75rem',
                        color: 'var(--color-accent)',
                        fontFamily: '"Share Tech Mono", monospace',
                        letterSpacing: '0.05em'
                      }}>
                        <Cpu size={14} style={{ display: 'inline', marginRight: '0.25rem' }} />
                        TECH SETUP
                      </span>
                      <button
                        onClick={handleEditTechDesc}
                        className="btn btn-sm"
                        style={{
                          padding: '0.25rem 0.5rem',
                          fontSize: '0.7rem'
                        }}
                      >
                        <Edit3 size={12} />
                      </button>
                    </div>
                    <p style={{
                      fontSize: '0.8rem',
                      color: user.techDescription ? 'var(--color-text)' : 'var(--color-text-dim)',
                      fontStyle: user.techDescription ? 'normal' : 'italic',
                      lineHeight: '1.4',
                      whiteSpace: 'pre-wrap'
                    }}>
                      {user.techDescription || 'Click edit to describe your agentic setup (model, framework, approach...)'}
                    </p>
                  </div>

                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(2, 1fr)',
                    gap: '0.75rem'
                  }}>
                    <div className="stat-card">
                      <div className="value text-success" style={{ fontSize: '2rem', fontWeight: '700', fontFamily: '"Share Tech Mono", monospace' }}>{user.wins}</div>
                      <div className="label" style={{ fontSize: '0.75rem', color: 'var(--color-text-dim)', fontFamily: '"Share Tech Mono", monospace' }}>WINS</div>
                    </div>
                    <div className="stat-card">
                      <div className="value text-error" style={{ fontSize: '2rem', fontWeight: '700', fontFamily: '"Share Tech Mono", monospace' }}>{user.losses}</div>
                      <div className="label" style={{ fontSize: '0.75rem', color: 'var(--color-text-dim)', fontFamily: '"Share Tech Mono", monospace' }}>LOSSES</div>
                    </div>
                    <div className="stat-card">
                      <div className="value text-muted" style={{ fontSize: '2rem', fontWeight: '700', fontFamily: '"Share Tech Mono", monospace' }}>{user.draws}</div>
                      <div className="label" style={{ fontSize: '0.75rem', color: 'var(--color-text-dim)', fontFamily: '"Share Tech Mono", monospace' }}>DRAWS</div>
                    </div>
                    <div className="stat-card">
                      <div className="value" style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--color-primary)', fontFamily: '"Share Tech Mono", monospace' }}>{user.score}</div>
                      <div className="label" style={{ fontSize: '0.75rem', color: 'var(--color-text-dim)', fontFamily: '"Share Tech Mono", monospace' }}>SCORE</div>
                    </div>
                  </div>
                </>
              )}
            </div>

            {/* Leaderboard */}
            <div className="card" style={{ flex: '1 1 600px' }}>
              <h2 style={{ 
                color: 'var(--color-warning)', 
                fontFamily: '"Share Tech Mono", monospace',
                letterSpacing: '0.1em',
                fontSize: '1rem',
                marginBottom: '1.5rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                justifyContent: 'center'
              }}>
                <Trophy size={18} />
                [GLOBAL RANKINGS]
              </h2>

              {/* Rank Filter */}
              <div className="rank-filter">
                <button
                  onClick={() => setSelectedRank(null)}
                  className={`btn btn-sm ${selectedRank === null ? '' : 'btn-secondary'}`}
                >
                  All
                </button>
                {Object.entries(RANK_TIERS).map(([rank, config]) => {
                  const RankIcon = config.icon
                  return (
                    <button
                      key={rank}
                      onClick={() => setSelectedRank(rank)}
                      className={`btn btn-sm ${selectedRank === rank ? '' : 'btn-secondary'}`}
                    >
                      <RankIcon size={12} />
                      {rank.substring(0, 3)}
                    </button>
                  )
                })}
              </div>

              {/* Leaderboard Table */}
              {leaderboardLoading ? (
                <div className="loading">Loading</div>
              ) : leaderboard.length === 0 ? (
                <div className="empty-state">No combats yet!</div>
              ) : (
                <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                  <table className="leaderboard-table">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>AGENT</th>
                        <th className="text-center">RANK</th>
                        <th className="text-center">W</th>
                        <th className="text-center">L</th>
                        <th className="text-center">SCORE</th>
                      </tr>
                    </thead>
                    <tbody>
                      {leaderboard.map((entry) => {
                        const rankConfig = RANK_TIERS[entry.rank] || RANK_TIERS.Bronze
                        const RankIcon = rankConfig.icon
                        const medals = [
                          <Trophy size={14} key="1" className="medal-gold" />,
                          <Medal size={14} key="2" className="medal-silver" />,
                          <Medal size={14} key="3" className="medal-bronze" />
                        ]
                        return (
                          <tr key={entry.username} style={{ backgroundColor: rankConfig.bgColor }}>
                            <td className="position-cell">
                              {entry.position <= 3 ? medals[entry.position - 1] : entry.position}
                            </td>
                            <td 
                              className="agent-name" 
                              onClick={() => handleViewProfile(entry.username)}
                              style={{ cursor: 'pointer', textDecoration: 'underline' }}
                            >
                              {entry.username}
                            </td>
                            <td className="text-center" style={{ color: rankConfig.color }}>
                              <RankIcon size={14} />
                            </td>
                            <td className="text-center text-success">{entry.wins}</td>
                            <td className="text-center text-error">{entry.losses}</td>
                            <td className="text-center score-cell">{entry.score}</td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {/* Tech Description Edit Modal */}
      {editingTechDesc && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '1rem'
        }}
        onClick={() => setEditingTechDesc(false)}
        >
          <div 
            className="card" 
            style={{ maxWidth: '600px', width: '100%' }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '1rem'
            }}>
              <h3 style={{
                color: 'var(--color-accent)',
                fontFamily: '"Share Tech Mono", monospace',
                fontSize: '1rem',
                letterSpacing: '0.05em'
              }}>
                <Cpu size={18} style={{ display: 'inline', marginRight: '0.5rem' }} />
                EDIT TECH SETUP
              </h3>
              <button
                onClick={() => setEditingTechDesc(false)}
                className="btn btn-sm btn-secondary"
              >
                <X size={16} />
              </button>
            </div>
            
            <textarea
              value={techDescValue}
              onChange={(e) => setTechDescValue(e.target.value)}
              placeholder="Describe your agentic setup (e.g., Llama 3.2 with Ollama, custom RAG pipeline, LangChain + GPT-4...)"
              style={{
                width: '100%',
                minHeight: '150px',
                padding: '0.75rem',
                background: 'rgba(0, 0, 0, 0.3)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--color-text)',
                fontFamily: 'inherit',
                fontSize: '0.9rem',
                resize: 'vertical',
                marginBottom: '1rem'
              }}
              maxLength={2000}
            />
            
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-dim)', marginBottom: '1rem' }}>
              {techDescValue.length} / 2000 characters
            </div>
            
            <button
              onClick={handleSaveTechDesc}
              disabled={savingTechDesc}
              className="btn btn-full"
            >
              {savingTechDesc ? 'Saving...' : (
                <>
                  <Check size={16} />
                  Save
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* User Profile Modal */}
      {viewingProfile && profileData && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '1rem'
        }}
        onClick={() => setViewingProfile(null)}
        >
          <div 
            className="card" 
            style={{ maxWidth: '500px', width: '100%' }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '1.5rem'
            }}>
              <h3 style={{
                fontSize: '1.5rem',
                color: '#ffffff',
                fontFamily: '"Share Tech Mono", monospace'
              }}>
                {profileData.username}
              </h3>
              <button
                onClick={() => setViewingProfile(null)}
                className="btn btn-sm btn-secondary"
              >
                <X size={16} />
              </button>
            </div>

            <p style={{ 
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              color: RANK_TIERS[profileData.rank]?.color,
              fontSize: '1rem',
              fontFamily: '"Share Tech Mono", monospace',
              marginBottom: '1.5rem'
            }}>
              {(() => {
                const RankIcon = RANK_TIERS[profileData.rank]?.icon || Medal
                return <RankIcon size={18} />
              })()}
              {profileData.rank}
            </p>

            {profileData.techDescription && (
              <div style={{
                marginBottom: '1.5rem',
                padding: '1rem',
                background: 'rgba(0, 170, 255, 0.05)',
                border: '1px solid rgba(0, 170, 255, 0.2)',
                borderRadius: 'var(--radius-sm)'
              }}>
                <div style={{
                  fontSize: '0.75rem',
                  color: 'var(--color-accent)',
                  fontFamily: '"Share Tech Mono", monospace',
                  letterSpacing: '0.05em',
                  marginBottom: '0.5rem'
                }}>
                  <Cpu size={14} style={{ display: 'inline', marginRight: '0.25rem' }} />
                  TECH SETUP
                </div>
                <p style={{
                  fontSize: '0.85rem',
                  color: 'var(--color-text)',
                  lineHeight: '1.5',
                  whiteSpace: 'pre-wrap'
                }}>
                  {profileData.techDescription}
                </p>
              </div>
            )}

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '0.75rem'
            }}>
              <div className="stat-card">
                <div className="value text-success" style={{ fontSize: '2rem', fontWeight: '700' }}>{profileData.wins}</div>
                <div className="label" style={{ fontSize: '0.75rem' }}>WINS</div>
              </div>
              <div className="stat-card">
                <div className="value text-error" style={{ fontSize: '2rem', fontWeight: '700' }}>{profileData.losses}</div>
                <div className="label" style={{ fontSize: '0.75rem' }}>LOSSES</div>
              </div>
              <div className="stat-card">
                <div className="value text-muted" style={{ fontSize: '2rem', fontWeight: '700' }}>{profileData.draws}</div>
                <div className="label" style={{ fontSize: '0.75rem' }}>DRAWS</div>
              </div>
              <div className="stat-card">
                <div className="value" style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--color-primary)' }}>{profileData.score}</div>
                <div className="label" style={{ fontSize: '0.75rem' }}>SCORE</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Landing

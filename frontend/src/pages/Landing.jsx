import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { createCombat, getLeaderboard } from '../api'
import { useAuth } from '../AuthContext'
import { Swords, Trophy, Medal, Crown, Star, TrendingUp, Target, Zap, User } from 'lucide-react'

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
  const navigate = useNavigate()
  const { user, refreshUser, isAuthenticated } = useAuth()

  useEffect(() => {
    fetchLeaderboard()
    // Refresh user stats on landing if authenticated
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

  const handleCreateCombat = async () => {
    // If not authenticated, redirect to auth page
    if (!isAuthenticated) {
      navigate('/auth')
      return
    }
    
    setError('')
    setLoading(true)
    try {
      const data = await createCombat(combatMode)
      navigate(`/lobby/${data.code}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create combat')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container fade-in">
      {/* Hero Section for non-authenticated users */}
      {!isAuthenticated && (
        <div className="header">
          <h1 style={{ 
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.75rem'
          }}>
            <Zap size={36} fill="#ef4444" color="#ef4444" />
            MoltClash
          </h1>
          <p>Real-time 1v1 AI Agent Combat Platform</p>
        </div>
      )}

      {/* 2x2 Grid Layout */}
      <div className="dashboard-grid" style={{ marginBottom: '2rem' }}>
        {/* Top Left: How It Works */}
        <div className="card">
          <h2 className="section-header" style={{ color: 'var(--color-primary)' }}>
            <Target size={18} />
            How It Works
          </h2>
          <div className="rules-list">
            <p><span className="step-number">1.</span> Create a combat with your handle</p>
            <p><span className="step-number">2.</span> Share the invite link with another agent</p>
            <p><span className="step-number">3.</span> Generate API keys for both participants</p>
            <p><span className="step-number">4.</span> Run your local agent client with your API key</p>
            <p><span className="step-number">5.</span> Answer the question before time runs out</p>
            <p><span className="step-number">6.</span> See both responses and determine the winner</p>
          </div>
        </div>

        {/* Top Right: Leaderboard */}
        <div className="card leaderboard-card">
          <h2 className="section-header" style={{ color: 'var(--color-warning)', justifyContent: 'center' }}>
            <Trophy size={18} />
            Leaderboard
          </h2>

          {/* Rank Tier Filter */}
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
                  style={selectedRank === rank ? { background: config.color, borderColor: config.color } : {}}
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
            <table className="leaderboard-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Agent</th>
                  <th className="text-center">Rank</th>
                  <th className="text-center">W</th>
                  <th className="text-center">L</th>
                  <th className="text-center">Score</th>
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
                      <td className="agent-name">{entry.username}</td>
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
          )}
        </div>

        {/* Bottom Left: User Stats or Guest Message */}
        <div className="card">
          {isAuthenticated && user ? (
            <>
              <h2 className="section-header" style={{ color: 'var(--color-primary)' }}>
                <TrendingUp size={18} />
                Your Stats
              </h2>
              <div className="user-profile">
                <h3 className="user-handle">{user.username}</h3>
                <p className="user-rank" style={{ color: RANK_TIERS[user.rank]?.color }}>
                  {(() => {
                    const RankIcon = RANK_TIERS[user.rank]?.icon || Medal
                    return <RankIcon size={18} />
                  })()}
                  {user.rank}
                </p>
              </div>
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="value text-success">{user.wins}</div>
                  <div className="label">WINS</div>
                </div>
                <div className="stat-card">
                  <div className="value text-error">{user.losses}</div>
                  <div className="label">LOSSES</div>
                </div>
                <div className="stat-card">
                  <div className="value text-muted">{user.draws}</div>
                  <div className="label">DRAWS</div>
                </div>
                <div className="stat-card">
                  <div className="value text-warning">{user.score}</div>
                  <div className="label">SCORE</div>
                </div>
              </div>
            </>
          ) : (
            <>
              <h2 className="section-header" style={{ color: 'var(--color-primary)' }}>
                <User size={18} />
                Guest Mode
              </h2>
              <p className="guest-message">
                Sign in to track your stats, compete on the leaderboard, and earn ranks!
              </p>
              <div className="rank-requirements">
                {Object.entries(RANK_TIERS).map(([rank, config]) => {
                  const RankIcon = config.icon
                  const requirements = {
                    Bronze: '0+',
                    Silver: '10+',
                    Gold: '25+',
                    Diamond: '50+',
                    Professional: '100+'
                  }
                  return (
                    <div key={rank} className="rank-item" style={{ color: config.color }}>
                      <RankIcon size={12} />
                      {rank}: {requirements[rank]}
                    </div>
                  )
                })}
              </div>
            </>
          )}
        </div>

        {/* Bottom Right: Start Battle */}
        <div className="card battle-card">
          <h2 className="section-header" style={{ color: 'var(--color-primary)', justifyContent: 'center' }}>
            <Swords size={20} />
            START A BATTLE
          </h2>
          
          <p className="description">
            {isAuthenticated 
              ? 'Create a combat and share the invite link with another agent to battle!'
              : 'Sign in to create a combat and challenge other AI agents!'}
          </p>

          {isAuthenticated && (
            <div className="mode-selector">
              <label className="mode-label">Question Mode:</label>
              <div className="mode-buttons">
                <button
                  onClick={() => setCombatMode('formal_logic')}
                  className={`btn btn-sm ${combatMode === 'formal_logic' ? '' : 'btn-secondary'}`}
                >
                  Formal Logic
                </button>
                <button
                  onClick={() => setCombatMode('argument_logic')}
                  className={`btn btn-sm ${combatMode === 'argument_logic' ? '' : 'btn-secondary'}`}
                >
                  Argument Logic
                </button>
              </div>
              <p className="mode-description text-muted">
                {combatMode === 'formal_logic' 
                  ? 'True/False/Unknown questions from ProofWriter & RuleTaker'
                  : 'Multiple choice reasoning from ReClor'}
              </p>
            </div>
          )}

          {error && <div className="error">{error}</div>}

          <button 
            onClick={handleCreateCombat} 
            className="btn btn-full"
            disabled={loading}
          >
            {loading ? (
              'Initializing Combat...'
            ) : isAuthenticated ? (
              <>
                <Swords size={18} />
                Create Combat
              </>
            ) : (
              <>
                <Target size={18} />
                Sign In to Fight
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

export default Landing

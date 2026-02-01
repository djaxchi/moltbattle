import { Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import CombatLobby from './pages/CombatLobby'
import AcceptInvite from './pages/AcceptInvite'
import Dashboard from './pages/Dashboard'

function App() {
  return (
    <div>
      <div className="header">
        <h1>⚔️ Agent Fight Club ⚔️</h1>
        <p>Where AI agents battle for supremacy</p>
      </div>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/lobby/:code" element={<CombatLobby />} />
        <Route path="/accept/:code" element={<AcceptInvite />} />
        <Route path="/dashboard/:code" element={<Dashboard />} />
      </Routes>
    </div>
  )
}

export default App

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Workout from './pages/Workout'
import Programs from './pages/Programs'
import Calendar from './pages/Calendar'
import Performance from './pages/Performance'
import Profile from './pages/Profile'
import Leaderboard from './pages/Leaderboard'
import Coach from './pages/Coach'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/workout/:exercise" element={<Workout />} />
          <Route path="/programs" element={<Programs />} />
          <Route path="/calendar" element={<Calendar />} />
          <Route path="/performance" element={<Performance />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
          <Route path="/coach" element={<Coach />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App

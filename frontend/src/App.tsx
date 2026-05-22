import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Workout from './pages/Workout'
import Planning from './pages/Planning'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/workout/:exercise" element={<Workout />} />
          <Route path="/planning" element={<Planning />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App

import { Link, useLocation } from 'react-router-dom'
import { Home, Dumbbell, CalendarDays, BarChart3, Trophy, MessageCircle, User } from 'lucide-react'

const navItems = [
  { path: '/', icon: Home, label: 'Accueil' },
  { path: '/programs', icon: Dumbbell, label: 'Programmes' },
  { path: '/calendar', icon: CalendarDays, label: 'Calendrier' },
  { path: '/performance', icon: BarChart3, label: 'Performance' },
  { path: '/leaderboard', icon: Trophy, label: 'Classement' },
  { path: '/coach', icon: MessageCircle, label: 'Coach' },
  { path: '/profile', icon: User, label: 'Profil' },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation()

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-4 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-2">
            <span className="text-2xl">🏋️</span>
            <span className="text-xl font-bold text-primary-400">FitCoach AI</span>
          </Link>
          <nav className="hidden md:flex space-x-1">
            {navItems.map(({ path, icon: Icon, label }) => (
              <Link
                key={path}
                to={path}
                className={`flex items-center space-x-1 px-3 py-2 rounded-lg text-sm transition-colors ${
                  location.pathname === path
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
                }`}
              >
                <Icon size={16} />
                <span>{label}</span>
              </Link>
            ))}
          </nav>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-6">
        {children}
      </main>

      {/* Mobile bottom nav */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-gray-800 border-t border-gray-700 px-2 py-1">
        <div className="flex justify-around">
          {navItems.slice(0, 5).map(({ path, icon: Icon, label }) => (
            <Link
              key={path}
              to={path}
              className={`flex flex-col items-center py-1 px-2 text-xs ${
                location.pathname === path ? 'text-primary-400' : 'text-gray-500'
              }`}
            >
              <Icon size={20} />
              <span className="mt-0.5">{label}</span>
            </Link>
          ))}
        </div>
      </nav>
    </div>
  )
}

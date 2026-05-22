import { Link } from 'react-router-dom'
import { Flame, Target, Calendar, TrendingUp } from 'lucide-react'

const exercises = [
  { id: 'pushups_standard', name: 'Pompes', emoji: '🫸', color: 'from-red-500 to-orange-500' },
  { id: 'squats_standard', name: 'Squats', emoji: '🦵', color: 'from-blue-500 to-purple-500' },
  { id: 'dips_standard', name: 'Dips', emoji: '💪', color: 'from-green-500 to-teal-500' },
  { id: 'pullups', name: 'Tractions', emoji: '🏋️', color: 'from-yellow-500 to-red-500' },
  { id: 'plank', name: 'Planche', emoji: '🧘', color: 'from-indigo-500 to-blue-500' },
  { id: 'lunges', name: 'Fentes', emoji: '🦿', color: 'from-pink-500 to-rose-500' },
]

export default function Dashboard() {
  return (
    <div className="pb-20 md:pb-0">
      {/* Hero */}
      <div className="text-center mb-8">
        <h1 className="text-3xl md:text-4xl font-bold mb-3">
          Votre <span className="text-primary-400">Coach IA</span> Personnel
        </h1>
        <p className="text-gray-400 max-w-xl mx-auto">
          Activez votre webcam, l'IA analyse votre posture en temps réel et vous guide vers la forme parfaite.
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <Flame className="text-orange-400 mb-1" size={20} />
          <p className="text-2xl font-bold">7</p>
          <p className="text-xs text-gray-400">Jours de streak</p>
        </div>
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <Target className="text-green-400 mb-1" size={20} />
          <p className="text-2xl font-bold">85%</p>
          <p className="text-xs text-gray-400">Score moyen</p>
        </div>
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <Calendar className="text-blue-400 mb-1" size={20} />
          <p className="text-2xl font-bold">12</p>
          <p className="text-xs text-gray-400">Séances ce mois</p>
        </div>
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <TrendingUp className="text-purple-400 mb-1" size={20} />
          <p className="text-2xl font-bold">Lv.3</p>
          <p className="text-xs text-gray-400">Régulier</p>
        </div>
      </div>

      {/* Exercise Grid */}
      <h2 className="text-xl font-bold mb-4">Commencer un exercice</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
        {exercises.map((ex) => (
          <Link
            key={ex.id}
            to={`/workout/${ex.id}`}
            className="group relative overflow-hidden rounded-2xl p-5 bg-gray-800 border border-gray-700 hover:border-gray-500 transition-all hover:scale-105"
          >
            <div className={`absolute inset-0 bg-gradient-to-br ${ex.color} opacity-10 group-hover:opacity-20 transition-opacity`} />
            <div className="relative">
              <span className="text-4xl block mb-2">{ex.emoji}</span>
              <h3 className="text-lg font-bold">{ex.name}</h3>
              <p className="text-primary-400 text-sm mt-1 group-hover:translate-x-1 transition-transform">
                Commencer →
              </p>
            </div>
          </Link>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-2 gap-4">
        <Link
          to="/programs"
          className="flex items-center space-x-3 bg-gray-800 rounded-xl p-4 border border-gray-700 hover:border-primary-500 transition-colors"
        >
          <span className="text-3xl">📅</span>
          <div>
            <h3 className="font-bold">Mon programme</h3>
            <p className="text-sm text-gray-400">Voir ou créer un programme personnalisé</p>
          </div>
        </Link>
        <Link
          to="/coach"
          className="flex items-center space-x-3 bg-gray-800 rounded-xl p-4 border border-gray-700 hover:border-primary-500 transition-colors"
        >
          <span className="text-3xl">🤖</span>
          <div>
            <h3 className="font-bold">Parler au Coach</h3>
            <p className="text-sm text-gray-400">Conseils, questions, motivation</p>
          </div>
        </Link>
      </div>
    </div>
  )
}

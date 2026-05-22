import { Link } from 'react-router-dom'

const exercises = [
  {
    id: 'pushups',
    name: 'Pompes',
    emoji: '🫸',
    description: 'Travaillez vos pectoraux, triceps et épaules',
    color: 'from-red-500 to-orange-500',
  },
  {
    id: 'squats',
    name: 'Squats',
    emoji: '🦵',
    description: 'Renforcez vos quadriceps, fessiers et ischio-jambiers',
    color: 'from-blue-500 to-purple-500',
  },
  {
    id: 'curls',
    name: 'Curls',
    emoji: '💪',
    description: 'Développez vos biceps avec une forme parfaite',
    color: 'from-green-500 to-teal-500',
  },
]

export default function Home() {
  return (
    <div>
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">
          Votre <span className="text-primary-400">Personal Trainer</span> IA
        </h1>
        <p className="text-gray-400 text-lg max-w-2xl mx-auto">
          Activez votre webcam et laissez l'IA analyser votre posture en temps réel.
          Recevez des conseils personnalisés pour améliorer votre forme.
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {exercises.map((exercise) => (
          <Link
            key={exercise.id}
            to={`/workout/${exercise.id}`}
            className="group relative overflow-hidden rounded-2xl p-6 bg-gray-800 border border-gray-700 hover:border-gray-500 transition-all duration-300 hover:scale-105"
          >
            <div className={`absolute inset-0 bg-gradient-to-br ${exercise.color} opacity-10 group-hover:opacity-20 transition-opacity`} />
            <div className="relative">
              <span className="text-5xl mb-4 block">{exercise.emoji}</span>
              <h2 className="text-2xl font-bold mb-2">{exercise.name}</h2>
              <p className="text-gray-400">{exercise.description}</p>
              <div className="mt-4 text-primary-400 font-medium group-hover:translate-x-2 transition-transform">
                Commencer →
              </div>
            </div>
          </Link>
        ))}
      </div>

      <div className="mt-12 text-center">
        <Link
          to="/planning"
          className="inline-flex items-center px-6 py-3 bg-primary-600 hover:bg-primary-700 rounded-lg font-medium transition-colors"
        >
          📅 Créer mon planning d'exercices
        </Link>
      </div>
    </div>
  )
}

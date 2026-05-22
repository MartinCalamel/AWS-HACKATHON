import { useState } from 'react'
import { generatePlanning } from '../services/api'

interface DayPlan {
  day: string
  exercises: {
    name: string
    sets: number
    reps: number
    rest: string
  }[]
}

export default function Planning() {
  const [level, setLevel] = useState<string>('beginner')
  const [goal, setGoal] = useState<string>('general')
  const [daysPerWeek, setDaysPerWeek] = useState<number>(3)
  const [planning, setPlanning] = useState<DayPlan[] | null>(null)
  const [loading, setLoading] = useState(false)

  const handleGenerate = async () => {
    setLoading(true)
    try {
      const result = await generatePlanning({ level, goal, daysPerWeek })
      setPlanning(result)
    } catch (err) {
      console.error('Erreur génération planning:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">📅 Mon Planning d'Exercices</h1>

      {/* Configuration */}
      <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700 mb-8">
        <h2 className="text-xl font-semibold mb-4">Configurer mon programme</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Niveau
            </label>
            <select
              value={level}
              onChange={(e) => setLevel(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
            >
              <option value="beginner">Débutant</option>
              <option value="intermediate">Intermédiaire</option>
              <option value="advanced">Avancé</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Objectif
            </label>
            <select
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
            >
              <option value="general">Forme générale</option>
              <option value="strength">Force</option>
              <option value="endurance">Endurance</option>
              <option value="muscle">Prise de masse</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Jours par semaine
            </label>
            <select
              value={daysPerWeek}
              onChange={(e) => setDaysPerWeek(Number(e.target.value))}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
            >
              <option value={2}>2 jours</option>
              <option value={3}>3 jours</option>
              <option value={4}>4 jours</option>
              <option value={5}>5 jours</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="mt-6 px-6 py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-600 rounded-lg font-medium transition-colors"
        >
          {loading ? '⏳ Génération en cours...' : '🤖 Générer mon planning avec l\'IA'}
        </button>
      </div>

      {/* Planning Display */}
      {planning && (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {planning.map((day, index) => (
            <div
              key={index}
              className="bg-gray-800 rounded-2xl p-6 border border-gray-700"
            >
              <h3 className="text-lg font-bold text-primary-400 mb-4">
                {day.day}
              </h3>
              <ul className="space-y-3">
                {day.exercises.map((ex, i) => (
                  <li key={i} className="flex justify-between items-center">
                    <span className="text-gray-300">{ex.name}</span>
                    <span className="text-sm text-gray-500">
                      {ex.sets}×{ex.reps} | {ex.rest}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

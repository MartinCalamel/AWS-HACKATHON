import { useState } from 'react'
import { generateProgram } from '../services/api'
import type { Program } from '../types'

export default function Programs() {
  const [level, setLevel] = useState('beginner')
  const [goal, setGoal] = useState('general')
  const [daysPerWeek, setDaysPerWeek] = useState(3)
  const [program, setProgram] = useState<Program | null>(null)
  const [loading, setLoading] = useState(false)

  const handleGenerate = async () => {
    setLoading(true)
    try {
      const result = await generateProgram({ userId: 'user1', level, goal, daysPerWeek })
      setProgram(result.program)
    } catch (err) {
      console.error('Erreur génération:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="pb-20 md:pb-0">
      <h1 className="text-2xl font-bold mb-6">📋 Programmes d'entraînement</h1>

      {/* Generator */}
      <div className="bg-gray-800 rounded-xl p-5 border border-gray-700 mb-6">
        <h2 className="text-lg font-semibold mb-4">Générer un programme IA</h2>
        <div className="grid md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Niveau</label>
            <select value={level} onChange={e => setLevel(e.target.value)} className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white">
              <option value="beginner">Débutant</option>
              <option value="intermediate">Intermédiaire</option>
              <option value="advanced">Avancé</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Objectif</label>
            <select value={goal} onChange={e => setGoal(e.target.value)} className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white">
              <option value="general">Forme générale</option>
              <option value="strength">Force</option>
              <option value="endurance">Endurance</option>
              <option value="hypertrophy">Hypertrophie</option>
              <option value="weight_loss">Perte de poids</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Jours/semaine</label>
            <select value={daysPerWeek} onChange={e => setDaysPerWeek(Number(e.target.value))} className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white">
              {[2, 3, 4, 5, 6].map(d => <option key={d} value={d}>{d} jours</option>)}
            </select>
          </div>
        </div>
        <button onClick={handleGenerate} disabled={loading} className="mt-4 px-5 py-2.5 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-600 rounded-lg font-medium transition-colors">
          {loading ? '⏳ Génération...' : '🤖 Générer mon programme'}
        </button>
      </div>

      {/* Display program */}
      {program && (
        <div>
          <h2 className="text-lg font-bold mb-3">{program.name}</h2>
          <p className="text-gray-400 text-sm mb-4">{program.description}</p>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
            {program.weeks?.[0]?.days?.map((day, i) => (
              <div key={i} className="bg-gray-800 rounded-xl p-4 border border-gray-700">
                <h3 className="font-bold text-primary-400 mb-3">{day.day}</h3>
                <ul className="space-y-2">
                  {day.exercises.map((ex, j) => (
                    <li key={j} className="flex justify-between text-sm">
                      <span className="text-gray-300">{ex.name}</span>
                      <span className="text-gray-500">{ex.sets}×{ex.reps}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

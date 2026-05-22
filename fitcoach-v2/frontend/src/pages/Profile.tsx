import { useState, useEffect } from 'react'
import { getAchievements } from '../services/api'
import type { Achievements } from '../types'

export default function Profile() {
  const [achievements, setAchievements] = useState<Achievements | null>(null)

  useEffect(() => {
    loadAchievements()
  }, [])

  const loadAchievements = async () => {
    try {
      const data = await getAchievements('user1')
      setAchievements(data)
    } catch {
      setAchievements({
        totalXp: 2150,
        level: { level: 3, name: 'Régulier', xp_required: 1500 },
        nextLevel: { level: 4, name: 'Athlète', xp_required: 3500 },
        xpToNextLevel: 1350,
        badges: [
          { id: 'first_session', name: '🔥 Premier pas', condition: 'Première séance', xp: 50, unlocked: true, unlockedAt: '2026-05-01' },
          { id: 'perfect_form', name: '💯 Perfectionniste', condition: 'Score > 90%', xp: 100, unlocked: true, unlockedAt: '2026-05-10' },
          { id: 'streak_7', name: '📅 Régulier', condition: '7 jours streak', xp: 150, unlocked: true, unlockedAt: '2026-05-15' },
          { id: 'centurion', name: '🏆 Centurion', condition: '100 pompes', xp: 200, unlocked: false },
          { id: 'streak_30', name: '⚡ Infatigable', condition: '30 jours streak', xp: 500, unlocked: false },
        ],
        streak: 7,
      })
    }
  }

  if (!achievements) return <div className="text-center py-10 text-gray-400">Chargement...</div>

  const xpProgress = achievements.nextLevel
    ? ((achievements.totalXp - achievements.level.xp_required) / (achievements.nextLevel.xp_required - achievements.level.xp_required)) * 100
    : 100

  return (
    <div className="pb-20 md:pb-0">
      <h1 className="text-2xl font-bold mb-6">👤 Profil</h1>

      {/* Level & XP */}
      <div className="bg-gray-800 rounded-xl p-5 border border-gray-700 mb-6">
        <div className="flex items-center justify-between mb-3">
          <div>
            <p className="text-sm text-gray-400">Niveau {achievements.level.level}</p>
            <p className="text-xl font-bold text-primary-400">{achievements.level.name}</p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold">{achievements.totalXp} XP</p>
            {achievements.nextLevel && (
              <p className="text-xs text-gray-400">{achievements.xpToNextLevel} XP → {achievements.nextLevel.name}</p>
            )}
          </div>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-3">
          <div className="bg-primary-500 h-3 rounded-full transition-all" style={{ width: `${xpProgress}%` }} />
        </div>
        <div className="flex justify-between mt-2">
          <span className="text-xs text-gray-400">🔥 Streak: {achievements.streak} jours</span>
        </div>
      </div>

      {/* Badges */}
      <h2 className="text-lg font-bold mb-3">🏅 Badges</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {achievements.badges.map((badge) => (
          <div
            key={badge.id}
            className={`flex items-center space-x-3 p-4 rounded-xl border ${
              badge.unlocked ? 'bg-gray-800 border-primary-600' : 'bg-gray-800/50 border-gray-700 opacity-60'
            }`}
          >
            <span className="text-2xl">{badge.name.split(' ')[0]}</span>
            <div>
              <p className="font-medium">{badge.name.split(' ').slice(1).join(' ')}</p>
              <p className="text-xs text-gray-400">{badge.condition}</p>
              {badge.unlocked && <p className="text-xs text-green-400">+{badge.xp} XP</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

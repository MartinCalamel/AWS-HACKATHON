import { useState, useEffect } from 'react'
import { getLeaderboard } from '../services/api'
import type { LeaderboardEntry } from '../types'
import { Trophy, Medal } from 'lucide-react'

export default function Leaderboard() {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([])

  useEffect(() => {
    loadLeaderboard()
  }, [])

  const loadLeaderboard = async () => {
    try {
      const data = await getLeaderboard('user1')
      setEntries(data)
    } catch {
      setEntries([
        { rank: 1, userId: 'u1', username: 'FitMaster42', xp: 850, isCurrentUser: false },
        { rank: 2, userId: 'u2', username: 'IronWill', xp: 720, isCurrentUser: false },
        { rank: 3, userId: 'user1', username: 'Vous', xp: 680, isCurrentUser: true },
        { rank: 4, userId: 'u3', username: 'BodyPro', xp: 540, isCurrentUser: false },
        { rank: 5, userId: 'u4', username: 'FlexKing', xp: 490, isCurrentUser: false },
      ])
    }
  }

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Trophy className="text-yellow-400" size={20} />
    if (rank === 2) return <Medal className="text-gray-300" size={20} />
    if (rank === 3) return <Medal className="text-amber-600" size={20} />
    return <span className="text-gray-500 font-bold w-5 text-center">{rank}</span>
  }

  return (
    <div className="pb-20 md:pb-0">
      <h1 className="text-2xl font-bold mb-6">🏆 Classement hebdomadaire</h1>

      <div className="space-y-2">
        {entries.map((entry) => (
          <div
            key={entry.userId}
            className={`flex items-center justify-between p-4 rounded-xl border ${
              entry.isCurrentUser
                ? 'bg-primary-900/30 border-primary-600'
                : 'bg-gray-800 border-gray-700'
            }`}
          >
            <div className="flex items-center space-x-3">
              {getRankIcon(entry.rank)}
              <div>
                <p className={`font-medium ${entry.isCurrentUser ? 'text-primary-400' : ''}`}>
                  {entry.username}
                  {entry.isCurrentUser && ' (vous)'}
                </p>
              </div>
            </div>
            <p className="font-bold">{entry.xp} XP</p>
          </div>
        ))}
      </div>

      <p className="text-center text-gray-500 text-sm mt-6">
        Le classement est réinitialisé chaque lundi.
      </p>
    </div>
  )
}

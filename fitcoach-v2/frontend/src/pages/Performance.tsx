import { useState, useEffect } from 'react'
import { getStats, getHistory } from '../services/api'
import type { PerformanceStats, SessionRecord } from '../types'
import { TrendingUp, Award, Clock, Target } from 'lucide-react'

export default function Performance() {
  const [stats, setStats] = useState<PerformanceStats | null>(null)
  const [history, setHistory] = useState<SessionRecord[]>([])

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [s, h] = await Promise.all([getStats('user1'), getHistory('user1')])
      setStats(s)
      setHistory(h)
    } catch {
      // Mock data
      setStats({ totalSessions: 24, totalReps: 2840, totalSets: 312, avgPostureScore: 82, totalDurationMinutes: 720 })
      setHistory([
        { sessionId: '1', date: '2026-05-21', totalReps: 120, totalSets: 12, avgScore: 85, durationMinutes: 35 },
        { sessionId: '2', date: '2026-05-19', totalReps: 98, totalSets: 10, avgScore: 78, durationMinutes: 28 },
        { sessionId: '3', date: '2026-05-17', totalReps: 135, totalSets: 14, avgScore: 88, durationMinutes: 40 },
      ])
    }
  }

  return (
    <div className="pb-20 md:pb-0">
      <h1 className="text-2xl font-bold mb-6">📊 Performance</h1>

      {/* Stats Grid */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
          <StatCard icon={<Target className="text-green-400" size={20} />} value={`${stats.avgPostureScore}%`} label="Score moyen" />
          <StatCard icon={<TrendingUp className="text-blue-400" size={20} />} value={stats.totalReps.toString()} label="Reps totales" />
          <StatCard icon={<Award className="text-yellow-400" size={20} />} value={stats.totalSessions.toString()} label="Séances" />
          <StatCard icon={<Clock className="text-purple-400" size={20} />} value={`${Math.round(stats.totalDurationMinutes / 60)}h`} label="Temps total" />
        </div>
      )}

      {/* History */}
      <h2 className="text-lg font-bold mb-3">Historique récent</h2>
      <div className="space-y-2">
        {history.map((session) => (
          <div key={session.sessionId} className="flex items-center justify-between bg-gray-800 rounded-xl p-4 border border-gray-700">
            <div>
              <p className="font-medium">{session.date}</p>
              <p className="text-xs text-gray-400">{session.durationMinutes} min • {session.totalSets} séries</p>
            </div>
            <div className="text-right">
              <p className={`font-bold ${session.avgScore >= 80 ? 'text-green-400' : 'text-yellow-400'}`}>
                {session.avgScore}%
              </p>
              <p className="text-xs text-gray-400">{session.totalReps} reps</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function StatCard({ icon, value, label }: { icon: React.ReactNode; value: string; label: string }) {
  return (
    <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
      {icon}
      <p className="text-2xl font-bold mt-1">{value}</p>
      <p className="text-xs text-gray-400">{label}</p>
    </div>
  )
}

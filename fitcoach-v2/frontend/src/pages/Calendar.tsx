import { useState, useEffect } from 'react'
import { getWeekCalendar } from '../services/api'
import type { CalendarDay } from '../types'
import { CheckCircle, Circle, Moon } from 'lucide-react'

export default function Calendar() {
  const [week, setWeek] = useState<CalendarDay[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadWeek()
  }, [])

  const loadWeek = async () => {
    try {
      const data = await getWeekCalendar('user1')
      setWeek(data)
    } catch {
      // Fallback mock data
      const days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
      setWeek(days.map((d, i) => ({
        date: `2026-05-${18 + i}`,
        dayName: d,
        session: i % 2 === 0 ? { day: `${d} - Full Body`, exercises: [] } : null,
        isRest: i % 2 !== 0,
        completed: i < 3,
      })))
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="text-center py-10 text-gray-400">Chargement...</div>

  return (
    <div className="pb-20 md:pb-0">
      <h1 className="text-2xl font-bold mb-6">📅 Calendrier</h1>

      <div className="grid gap-3">
        {week.map((day) => (
          <div
            key={day.date}
            className={`flex items-center justify-between p-4 rounded-xl border ${
              day.completed
                ? 'bg-green-900/20 border-green-700'
                : day.isRest
                ? 'bg-gray-800/50 border-gray-700'
                : 'bg-gray-800 border-gray-700'
            }`}
          >
            <div className="flex items-center space-x-3">
              {day.completed ? (
                <CheckCircle className="text-green-400" size={20} />
              ) : day.isRest ? (
                <Moon className="text-gray-500" size={20} />
              ) : (
                <Circle className="text-gray-500" size={20} />
              )}
              <div>
                <p className="font-medium">{day.dayName}</p>
                <p className="text-xs text-gray-400">{day.date}</p>
              </div>
            </div>
            <div className="text-right">
              {day.isRest ? (
                <span className="text-sm text-gray-500">Repos</span>
              ) : day.session ? (
                <span className="text-sm text-primary-400">{day.session.day}</span>
              ) : (
                <span className="text-sm text-gray-500">Non planifié</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

import { useState, useEffect, useCallback } from 'react'
import { Timer, Play, Pause, RotateCcw } from 'lucide-react'

interface RestTimerProps {
  initialSeconds: number
  onComplete?: () => void
  autoStart?: boolean
}

export default function RestTimer({ initialSeconds, onComplete, autoStart = true }: RestTimerProps) {
  const [seconds, setSeconds] = useState(initialSeconds)
  const [isRunning, setIsRunning] = useState(autoStart)
  const [isComplete, setIsComplete] = useState(false)

  useEffect(() => {
    if (!isRunning || seconds <= 0) return

    const interval = setInterval(() => {
      setSeconds(prev => {
        if (prev <= 1) {
          setIsRunning(false)
          setIsComplete(true)
          onComplete?.()
          // Play notification sound
          try {
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQ==')
            audio.play().catch(() => {})
          } catch {}
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(interval)
  }, [isRunning, seconds, onComplete])

  const reset = useCallback(() => {
    setSeconds(initialSeconds)
    setIsRunning(false)
    setIsComplete(false)
  }, [initialSeconds])

  const progress = ((initialSeconds - seconds) / initialSeconds) * 100

  return (
    <div className={`rounded-xl p-4 border ${isComplete ? 'bg-green-900/30 border-green-600' : 'bg-gray-800 border-gray-700'}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <Timer size={18} className="text-primary-400" />
          <span className="text-sm font-medium">Repos</span>
        </div>
        <span className={`text-2xl font-bold tabular-nums ${isComplete ? 'text-green-400' : 'text-white'}`}>
          {Math.floor(seconds / 60)}:{(seconds % 60).toString().padStart(2, '0')}
        </span>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-700 rounded-full h-2 mb-3">
        <div
          className={`h-2 rounded-full transition-all duration-1000 ${isComplete ? 'bg-green-500' : 'bg-primary-500'}`}
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Controls */}
      <div className="flex justify-center space-x-3">
        <button
          onClick={() => setIsRunning(!isRunning)}
          className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 transition-colors"
          aria-label={isRunning ? 'Pause' : 'Play'}
        >
          {isRunning ? <Pause size={18} /> : <Play size={18} />}
        </button>
        <button
          onClick={reset}
          className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 transition-colors"
          aria-label="Reset"
        >
          <RotateCcw size={18} />
        </button>
      </div>

      {isComplete && (
        <p className="text-center text-green-400 text-sm mt-2 font-medium">
          ✅ Repos terminé — Série suivante !
        </p>
      )}
    </div>
  )
}

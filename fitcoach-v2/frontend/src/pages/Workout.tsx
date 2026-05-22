import { useParams } from 'react-router-dom'
import { useRef, useState, useCallback } from 'react'
import Webcam from 'react-webcam'
import { analyzePose } from '../services/api'
import RestTimer from '../components/RestTimer'
import type { PoseAnalysisResult } from '../types'

const exerciseNames: Record<string, string> = {
  pushups_standard: 'Pompes standard',
  pushups_diamond: 'Pompes diamant',
  squats_standard: 'Squats',
  squats_jump: 'Squats sautés',
  dips_standard: 'Dips',
  pullups: 'Tractions',
  plank: 'Planche',
  lunges: 'Fentes',
}

export default function Workout() {
  const { exercise = 'pushups_standard' } = useParams<{ exercise: string }>()
  const webcamRef = useRef<Webcam>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState<PoseAnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [phase, setPhase] = useState('')
  const [repCount, setRepCount] = useState(0)
  const [currentSet, setCurrentSet] = useState(1)
  const [showRestTimer, setShowRestTimer] = useState(false)
  const intervalRef = useRef<number | null>(null)

  const captureAndAnalyze = useCallback(async () => {
    if (!webcamRef.current) return
    const imageSrc = webcamRef.current.getScreenshot()
    if (!imageSrc) return

    try {
      const analysis = await analyzePose(imageSrc, exercise, phase, repCount)
      setResult(analysis)
      setPhase(analysis.phase)
      setRepCount(analysis.repCount)
      setError(null)
    } catch (err) {
      setError('Erreur d\'analyse. Vérifiez votre connexion.')
      console.error(err)
    }
  }, [exercise, phase, repCount])

  const startAnalysis = () => {
    setIsAnalyzing(true)
    setShowRestTimer(false)
    captureAndAnalyze()
    intervalRef.current = window.setInterval(captureAndAnalyze, 200) // 5fps
  }

  const stopAnalysis = () => {
    setIsAnalyzing(false)
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }

  const nextSet = () => {
    stopAnalysis()
    setCurrentSet(prev => prev + 1)
    setRepCount(0)
    setPhase('')
    setShowRestTimer(true)
  }

  const scoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400'
    if (score >= 50) return 'text-yellow-400'
    return 'text-red-400'
  }

  return (
    <div className="pb-20 md:pb-0">
      <h1 className="text-2xl font-bold mb-4">
        {exerciseNames[exercise] || 'Exercice'} — Série {currentSet}
      </h1>

      <div className="grid lg:grid-cols-3 gap-4">
        {/* Webcam */}
        <div className="lg:col-span-2">
          <div className="relative rounded-2xl overflow-hidden bg-gray-800 border border-gray-700">
            <Webcam
              ref={webcamRef}
              audio={false}
              screenshotFormat="image/jpeg"
              screenshotQuality={0.7}
              className="w-full"
              videoConstraints={{ width: 640, height: 480, facingMode: 'user' }}
            />
            {isAnalyzing && (
              <div className="absolute top-3 right-3 flex items-center space-x-2 bg-red-600/90 px-3 py-1 rounded-full">
                <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                <span className="text-xs font-medium">LIVE</span>
              </div>
            )}
            {result && isAnalyzing && (
              <div className="absolute bottom-3 left-3 bg-black/70 rounded-lg px-3 py-2">
                <span className={`text-lg font-bold ${scoreColor(result.score)}`}>
                  {result.score}%
                </span>
                <span className="text-gray-300 text-sm ml-2">
                  Reps: {result.repCount}
                </span>
              </div>
            )}
          </div>

          <div className="mt-3 flex justify-center space-x-3">
            {!isAnalyzing ? (
              <button onClick={startAnalysis} className="px-5 py-2.5 bg-green-600 hover:bg-green-700 rounded-lg font-medium transition-colors">
                ▶️ Démarrer
              </button>
            ) : (
              <>
                <button onClick={stopAnalysis} className="px-5 py-2.5 bg-red-600 hover:bg-red-700 rounded-lg font-medium transition-colors">
                  ⏹️ Stop
                </button>
                <button onClick={nextSet} className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors">
                  ⏭️ Série suivante
                </button>
              </>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-3">
          {/* Score */}
          <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
            <h3 className="text-sm font-semibold text-gray-400 mb-2">Score posture</h3>
            <div className="text-4xl font-bold text-center">
              {result ? (
                <span className={scoreColor(result.score)}>{result.score}%</span>
              ) : (
                <span className="text-gray-600">--</span>
              )}
            </div>
            {result && (
              <p className="text-center text-gray-400 text-xs mt-1">
                Reps: {result.repCount} | Phase: {result.phase}
              </p>
            )}
          </div>

          {/* Feedback */}
          <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
            <h3 className="text-sm font-semibold text-gray-400 mb-2">💡 Conseils</h3>
            {error && <p className="text-red-400 text-xs">{error}</p>}
            {result?.feedback && result.feedback.length > 0 ? (
              <ul className="space-y-1.5">
                {result.feedback.map((tip, i) => (
                  <li key={i} className="flex items-start space-x-2">
                    <span className="text-primary-400 mt-0.5">•</span>
                    <span className="text-gray-300 text-sm">{tip}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-500 text-sm">Démarrez pour recevoir des conseils.</p>
            )}
          </div>

          {/* Rest Timer */}
          {showRestTimer && (
            <RestTimer
              initialSeconds={60}
              onComplete={() => setShowRestTimer(false)}
            />
          )}
        </div>
      </div>
    </div>
  )
}

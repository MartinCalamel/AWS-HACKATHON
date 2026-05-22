import { useParams } from 'react-router-dom'
import { useRef, useState, useCallback } from 'react'
import Webcam from 'react-webcam'
import { analyzePose } from '../services/api'

const exerciseNames: Record<string, string> = {
  pushups: 'Pompes',
  squats: 'Squats',
  curls: 'Curls',
}

interface PoseAnalysisResult {
  repCount: number
  feedback: string[]
  score: number
  phase: string
}

export default function Workout() {
  const { exercise } = useParams<{ exercise: string }>()
  const webcamRef = useRef<Webcam>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState<PoseAnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const intervalRef = useRef<number | null>(null)

  const captureAndAnalyze = useCallback(async () => {
    if (!webcamRef.current) return

    const imageSrc = webcamRef.current.getScreenshot()
    if (!imageSrc || !exercise) return

    try {
      const analysis = await analyzePose(imageSrc, exercise)
      setResult(analysis)
      setError(null)
    } catch (err) {
      setError('Erreur lors de l\'analyse. Vérifiez votre connexion.')
      console.error(err)
    }
  }, [exercise])

  const startAnalysis = () => {
    setIsAnalyzing(true)
    captureAndAnalyze()
    intervalRef.current = window.setInterval(captureAndAnalyze, 2000)
  }

  const stopAnalysis = () => {
    setIsAnalyzing(false)
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">
        {exerciseNames[exercise || ''] || 'Exercice'}
      </h1>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Webcam */}
        <div className="lg:col-span-2">
          <div className="relative rounded-2xl overflow-hidden bg-gray-800 border border-gray-700">
            <Webcam
              ref={webcamRef}
              audio={false}
              screenshotFormat="image/jpeg"
              screenshotQuality={0.8}
              className="w-full"
              videoConstraints={{
                width: 1280,
                height: 720,
                facingMode: 'user',
              }}
            />
            {isAnalyzing && (
              <div className="absolute top-4 right-4 flex items-center space-x-2 bg-red-600 px-3 py-1 rounded-full">
                <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                <span className="text-sm font-medium">Analyse en cours</span>
              </div>
            )}
          </div>

          <div className="mt-4 flex justify-center space-x-4">
            {!isAnalyzing ? (
              <button
                onClick={startAnalysis}
                className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-medium transition-colors"
              >
                ▶️ Démarrer l'analyse
              </button>
            ) : (
              <button
                onClick={stopAnalysis}
                className="px-6 py-3 bg-red-600 hover:bg-red-700 rounded-lg font-medium transition-colors"
              >
                ⏹️ Arrêter
              </button>
            )}
          </div>
        </div>

        {/* Feedback Panel */}
        <div className="space-y-4">
          {/* Score */}
          <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
            <h3 className="text-lg font-semibold mb-3">Score de posture</h3>
            <div className="text-5xl font-bold text-center">
              {result ? (
                <span className={result.score >= 80 ? 'text-green-400' : result.score >= 50 ? 'text-yellow-400' : 'text-red-400'}>
                  {result.score}%
                </span>
              ) : (
                <span className="text-gray-600">--</span>
              )}
            </div>
            {result && (
              <p className="text-center text-gray-400 mt-2">
                Répétitions : {result.repCount} | Phase : {result.phase}
              </p>
            )}
          </div>

          {/* Feedback */}
          <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700">
            <h3 className="text-lg font-semibold mb-3">💡 Conseils</h3>
            {error && (
              <p className="text-red-400 text-sm">{error}</p>
            )}
            {result?.feedback && result.feedback.length > 0 ? (
              <ul className="space-y-2">
                {result.feedback.map((tip, i) => (
                  <li key={i} className="flex items-start space-x-2">
                    <span className="text-primary-400 mt-1">•</span>
                    <span className="text-gray-300 text-sm">{tip}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-500 text-sm">
                Démarrez l'analyse pour recevoir des conseils en temps réel.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

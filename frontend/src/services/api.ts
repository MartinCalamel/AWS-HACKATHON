import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface PoseAnalysisResult {
  repCount: number
  feedback: string[]
  score: number
  phase: string
}

export interface PlanningRequest {
  level: string
  goal: string
  daysPerWeek: number
}

export interface DayPlan {
  day: string
  exercises: {
    name: string
    sets: number
    reps: number
    rest: string
  }[]
}

/**
 * Envoie une frame de la webcam pour analyse de posture
 */
export async function analyzePose(
  imageBase64: string,
  exercise: string
): Promise<PoseAnalysisResult> {
  const response = await api.post('/analyze-pose', {
    image: imageBase64,
    exercise,
  })
  return response.data
}

/**
 * Génère un planning d'exercices personnalisé via Bedrock
 */
export async function generatePlanning(
  params: PlanningRequest
): Promise<DayPlan[]> {
  const response = await api.post('/generate-planning', params)
  return response.data.planning
}

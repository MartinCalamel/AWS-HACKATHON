import axios from 'axios'
import type {
  PoseAnalysisResult, Program, CalendarDay,
  PerformanceStats, SessionRecord, Achievements,
  LeaderboardEntry, RestRecommendation, FatigueStatus,
} from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// ===== Master Agent =====
export async function askAgent(message: string, userId: string, context?: Record<string, unknown>) {
  const res = await api.post('/agent/ask', { message, userId, context })
  return res.data
}

// ===== Pose Analysis =====
export async function analyzePose(
  image: string, exercise: string, prevPhase: string, repCount: number
): Promise<PoseAnalysisResult> {
  const res = await api.post('/pose/analyze', { image, exercise, prevPhase, repCount })
  return res.data
}

// ===== Programs =====
export async function generateProgram(params: {
  userId: string; level: string; goal: string; daysPerWeek: number
}): Promise<{ programId: string; program: Program }> {
  const res = await api.post('/program', { ...params, intent: 'generate' })
  return res.data.response
}

export async function getPrograms(userId: string): Promise<Program[]> {
  const res = await api.get('/program', { params: { userId, intent: 'list' } })
  return res.data.response.programs
}

// ===== Calendar =====
export async function getWeekCalendar(userId: string): Promise<CalendarDay[]> {
  const res = await api.get('/calendar', { params: { userId, intent: 'week' } })
  return res.data.response.week
}

export async function scheduleSession(userId: string, date: string, session: unknown) {
  const res = await api.put('/calendar', { userId, intent: 'schedule', date, session })
  return res.data.response
}

// ===== Performance =====
export async function getStats(userId: string): Promise<PerformanceStats> {
  const res = await api.get('/performance', { params: { userId, intent: 'stats' } })
  return res.data.response
}

export async function getHistory(userId: string, limit = 10): Promise<SessionRecord[]> {
  const res = await api.get('/performance', { params: { userId, intent: 'history', limit } })
  return res.data.response.history
}

export async function recordSession(userId: string, data: unknown) {
  const res = await api.post('/performance', { userId, intent: 'record', ...data })
  return res.data.response
}

// ===== Achievements =====
export async function getAchievements(userId: string): Promise<Achievements> {
  const res = await api.get('/achievements', { params: { userId } })
  return res.data.response
}

// ===== Leaderboard =====
export async function getLeaderboard(userId: string): Promise<LeaderboardEntry[]> {
  const res = await api.get('/leaderboard', { params: { userId } })
  return res.data.response.leaderboard
}

// ===== Rest =====
export async function getRestTime(params: {
  userId: string; exercise: string; goal: string; currentSet: number; fatigueLevel: number
}): Promise<RestRecommendation> {
  const res = await api.get('/rest', { params: { ...params, intent: 'timer' } })
  return res.data.response
}

export async function getFatigue(userId: string): Promise<FatigueStatus> {
  const res = await api.get('/rest', { params: { userId, intent: 'fatigue' } })
  return res.data.response
}

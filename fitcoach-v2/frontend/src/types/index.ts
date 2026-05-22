// ===== Pose Analysis =====
export interface PoseAnalysisResult {
  repCount: number
  feedback: string[]
  score: number
  phase: string
  angles?: Record<string, number>
  detected: boolean
}

// ===== Programs =====
export interface Exercise {
  name: string
  sets: number
  reps: number
  rest_seconds: number
  tempo?: string
}

export interface DayPlan {
  day: string
  exercises: Exercise[]
}

export interface WeekPlan {
  week: number
  days: DayPlan[]
}

export interface Program {
  programId: string
  name: string
  description: string
  duration_weeks: number
  days_per_week: number
  weeks: WeekPlan[]
  createdAt?: string
  active?: boolean
}

// ===== Calendar =====
export interface CalendarDay {
  date: string
  dayName: string
  session: DayPlan | null
  isRest: boolean
  completed: boolean
}

// ===== Performance =====
export interface SessionRecord {
  sessionId: string
  date: string
  totalReps: number
  totalSets: number
  avgScore: number
  durationMinutes: number
}

export interface PerformanceStats {
  totalSessions: number
  totalReps: number
  totalSets: number
  avgPostureScore: number
  totalDurationMinutes: number
}

export interface PersonalRecord {
  maxVolume: number
  maxScore: number
  date: string
}

// ===== Gamification =====
export interface Badge {
  id: string
  name: string
  condition: string
  xp: number
  unlocked: boolean
  unlockedAt?: string
}

export interface Level {
  level: number
  name: string
  xp_required: number
}

export interface Achievements {
  totalXp: number
  level: Level
  nextLevel: Level | null
  xpToNextLevel: number
  badges: Badge[]
  streak: number
}

// ===== Leaderboard =====
export interface LeaderboardEntry {
  rank: number
  userId: string
  username: string
  xp: number
  isCurrentUser: boolean
}

// ===== Rest =====
export interface RestRecommendation {
  restSeconds: number
  exercise: string
  goal: string
  fatigueLevel: number
  message: string
}

export interface FatigueStatus {
  fatigueLevel: number
  weeklyVolume: number
  maxWeeklyVolume: number
  sessionsThisWeek: number
  shouldRest: boolean
  recommendation: string
}

// ===== User =====
export interface UserProfile {
  userId: string
  email: string
  level: string
  goal: string
  daysPerWeek: number
}

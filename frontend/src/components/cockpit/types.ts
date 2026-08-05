export type SkillStatus = 'mastered' | 'improving' | 'missing' | 'transferable'

export type SkillOrbit = 1 | 2 | 3

export type SkillSize = 'core' | 'normal' | 'minor'

export type SkillCategory =
  | 'professional'
  | 'tools'
  | 'project'
  | 'general'
  | 'industry'
  | 'jobhunt'

export interface UserProfile {
  id: string
  name: string
  avatar: string
  currentIdentity: string
  growthStage: string
  currentLevel: string
  targetRoleId: string
  updatedAt: string
  summary: string
}

export interface SkillEvidence {
  id: string
  skillId: string
  sourceType: 'resume' | 'project' | 'certificate' | 'portfolio' | 'interview' | 'assessment' | 'manual'
  sourceId: string
  sourceTitle: string
  content: string
  credibility: number
  createdAt: string
}

export interface Skill {
  id: string
  name: string
  category: SkillCategory
  currentLevel: number
  requiredLevel: number
  status: SkillStatus
  proficiency: number
  importance: number
  evidenceCount: number
  transferableFrom?: string
  relatedProjects: string[]
  lastUsedAt?: string
  learningSuggestion: string
  evidences?: SkillEvidence[]
  orbit?: SkillOrbit
  size?: SkillSize
  angle?: number
}

export interface TargetRole {
  id: string
  name: string
  level: string
  city: string
  matchScore: number
  matchChange: number
  requiredSkills: string[]
  estimatedReadyDays: number
  coreSkillsCount: number
  matchedCoreCount: number
  categoryName: string
  icon: string
}

export interface MatchBreakdown {
  name: string
  score: number
  maxScore: number
  color: string
  note: string
}

export interface LearningTask {
  id: string
  name: string
  targetSkill: string
  status: 'pending' | 'in-progress' | 'completed' | 'blocked'
  estimatedHours: number
  type: 'course' | 'project' | 'practice' | 'reading' | 'interview'
  description: string
}

export interface LearningStage {
  id: string
  name: string
  description: string
  status: 'locked' | 'available' | 'in-progress' | 'completed'
  progress: number
  tasks: LearningTask[]
  unlockCondition: string
  estimatedDays: number
  expectedMatchIncrease: number
  icon: string
}

export interface InterviewDimension {
  name: string
  score: number
  prevScore?: number
}

export interface MockInterview {
  id: string
  roleName: string
  date: string
  totalScore: number
  dimensionScores: InterviewDimension[]
  strengths: string[]
  weaknesses: string[]
  suggestions: string[]
  questionCount: number
  keyQuestions?: { q: string; a: string }[]
}

export type GrowthEventType =
  | 'resume_upload'
  | 'skill_added'
  | 'course_completed'
  | 'project_completed'
  | 'certificate'
  | 'interview'
  | 'role_changed'
  | 'match_increased'
  | 'stage_completed'
  | 'portfolio'

export interface GrowthEvent {
  id: string
  type: GrowthEventType
  title: string
  description: string
  date: string
  relatedSkills: string[]
  matchScoreChange: number
  source: string
  isMilestone?: boolean
}

export interface RecommendedRole {
  id: string
  name: string
  company?: string
  currentMatch: number
  matchChange: number
  recommendReason: string
  transferableSkills: string[]
  skillGaps: string[]
  estimatedDays: number
  tag: 'current' | 'adjacent' | 'easier' | 'longterm'
}

export interface ResumeData {
  fileName: string
  version: string
  updatedAt: string
  parseStatus: 'completed' | 'parsing' | 'failed'
  skillsExtracted: number
  projectsExtracted: number
  experiencesCount: number
  certificatesCount: number
  quantifiedAchievements: number
  recentUpdates: { date: string; action: string; detail: string }[]
}

export interface SkillFilter {
  status?: SkillStatus | 'all' | 'gap'
  category?: SkillCategory | 'all'
  showCoreOnly: boolean
}

export interface GalaxyOrbit {
  id: SkillCategory
  label: string
  radius: number
  color: string
  glowColor: string
}

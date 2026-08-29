import axios from 'axios'

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '',
  timeout: 15000
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const api = {
  register: (payload: unknown) => http.post('/api/auth/register', payload).then((res) => res.data),
  captcha: () => http.get('/api/auth/captcha').then((res) => res.data),
  login: (payload: unknown) => http.post('/api/auth/login', payload).then((res) => res.data),
  logout: () => http.post('/api/auth/logout').then((res) => res.data),
  me: () => http.get('/api/auth/me').then((res) => res.data),
  changePassword: (payload: unknown) => http.post('/api/auth/change-password', payload).then((res) => res.data),
  updateAccount: (payload: unknown) => http.put('/api/account', payload).then((res) => res.data),
  myProfile: () => http.get('/api/profile/me').then((res) => res.data),
  updateMyProfile: (payload: unknown) => http.put('/api/profile/me', payload).then((res) => res.data),
  hrCandidates: () => http.get('/api/hr/candidates').then((res) => res.data),
  overview: () => http.get('/api/overview/summary').then((res) => res.data),
  datasets: () => http.get('/api/datasets').then((res) => res.data),
  dataSourceStatus: () => http.get('/api/data-sources/status').then((res) => res.data),
  syncDataSources: () => http.post('/api/data-sources/sync', {}, { timeout: 180000 }).then((res) => res.data),
  marketSnapshot: () => http.get('/api/market/snapshot').then((res) => res.data),
  marketCatalog: (params?: { keyword?: string; item_type?: string; limit?: number }) =>
    http.get('/api/market/catalog', { params }).then((res) => res.data),
  parseJd: (text: string) => http.post('/api/jd/parse', { text }, { timeout: 120000 }).then((res) => res.data),
  jdHistory: () => http.get('/api/jd/history').then((res) => res.data),
  jdImports: () => http.get('/api/jd/imports').then((res) => res.data),
  importJds: (file: File, payload: { source_name: string; publisher: string; source_url: string; license_name: string; auto_parse: boolean; parse_limit: number }) => {
    const form = new FormData()
    form.append('file', file, file.name)
    Object.entries(payload).forEach(([key, value]) => form.append(key, String(value)))
    return http.post('/api/jd/import', form, { timeout: 180000 }).then((res) => res.data)
  },
  parseJdImport: (sourceId: number, limit = 50) =>
    http.post(`/api/jd/imports/${sourceId}/parse`, {}, { params: { limit }, timeout: 180000 }).then((res) => res.data),
  jobs: () => http.get('/api/jobs').then((res) => res.data),
  updateJob: (id: number, payload: unknown) => http.put(`/api/jobs/${id}`, payload).then((res) => res.data),
  emergingJobs: () => http.get('/api/emerging-jobs').then((res) => res.data),
  jobEvolution: (id: number) => http.get(`/api/job-evolution/${id}`).then((res) => res.data),
  skillGraph: () => http.get('/api/skill-graph').then((res) => res.data),
  graphFull: (params?: { keyword?: string; community?: number; limit?: number }) =>
    http.get('/api/graph/full', { params }).then((res) => res.data),
  graphStats: () => http.get('/api/graph/stats').then((res) => res.data),
  graphCommunities: () => http.get('/api/graph/communities').then((res) => res.data),
  graphPath: (from_job: number, to_job: number) =>
    http.get('/api/graph/path', { params: { from_job, to_job } }).then((res) => res.data),
  graphSearch: (keyword: string) => http.get('/api/graph/search', { params: { keyword } }).then((res) => res.data),
  evolutionTimeline: () => http.get('/api/evolution/timeline').then((res) => res.data),
  evolutionHotspot: () => http.get('/api/evolution/hotspot').then((res) => res.data),
  evolutionCompare: () => http.get('/api/evolution/compare').then((res) => res.data),
  evolutionVersionCompare: () => http.get('/api/evolution/version-compare').then((res) => res.data),
  graphEvidence: (node_type: 'job' | 'skill', node_id: number) =>
    http.get('/api/graph/evidence', { params: { node_type, node_id } }).then((res) => res.data),
  evaluationReport: () => http.get('/api/evaluation/report').then((res) => res.data),
  parseResume: (text: string) => http.post('/api/resume/parse', { text }, { timeout: 120000 }).then((res) => res.data),
  parseResumeFile: (file: File) => {
    const form = new FormData()
    form.append('file', file, file.name)
    return http.post('/api/resume/parse-file', form, { timeout: 120000 }).then((res) => res.data)
  },
  matchAnalysis: (payload: unknown) => http.post('/api/match-analysis', payload, { timeout: 120000 }).then((res) => res.data),
  matchAnalysisHistory: () => http.get('/api/match-analysis/history').then((res) => res.data),
  matchAnalysisDetail: (id: number) => http.get(`/api/match-analysis/${id}`).then((res) => res.data),
  learningPath: (id: number) => http.get(`/api/learning-path/${id}`, { timeout: 120000 }).then((res) => res.data),
  reviewTasks: () => http.get('/api/review-tasks').then((res) => res.data),
  approveTask: (id: number) => http.post(`/api/review-tasks/${id}/approve`).then((res) => res.data),
  rejectTask: (id: number) => http.post(`/api/review-tasks/${id}/reject`).then((res) => res.data),
  evaluation: () => http.get('/api/evaluation/metrics').then((res) => res.data),
  governanceHealth: () => http.get('/api/governance/health').then((res) => res.data),
  hallucinationStats: () => http.get('/api/governance/hallucination').then((res) => res.data),
  resumes: () => http.get('/api/resumes').then((res) => res.data),
  saveParsedResume: (payload: { resume: Record<string, unknown>; source_filename?: string; raw_text?: string }) =>
    http.post('/api/resumes/save-parsed', payload).then((res) => res.data),
  aiStatus: () => http.get('/api/ai/status').then((res) => res.data),
  aiAnalyze: (task_type: string, payload: Record<string, unknown>) => http.post('/api/ai/analyze', { task_type, payload }).then((res) => res.data),
  digitalInterview: (payload: { job_name: string; resume_summary?: string; candidate_answer?: string; stage?: string; interview_session_id?: number; interview_style?: string; action?: 'start' | 'answer' | 'skip'; digital_human_session_id?: string }) =>
    http.post('/api/digital-interviewer/interview', payload, { timeout: 120000 }).then((res) => res.data),
  interviewSessions: () => http.get('/api/digital-interviewer/sessions').then((res) => res.data),
  interviewSession: (id: number) => http.get(`/api/digital-interviewer/sessions/${id}`).then((res) => res.data),
  completeInterviewSession: (id: number) => http.post(`/api/digital-interviewer/sessions/${id}/complete`).then((res) => res.data),
  virtualHumanStatus: () => http.get('/api/digital-interviewer/virtual-human/status').then((res) => res.data),
  startVirtualHuman: () => http.post('/api/digital-interviewer/virtual-human/start', {}, { timeout: 45000 }).then((res) => res.data),
  speakVirtualHuman: (session_id: string, text: string) =>
    http.post('/api/digital-interviewer/virtual-human/speak', { session_id, text }, { timeout: 45000 }).then((res) => res.data),
  pingVirtualHuman: (session_id: string) =>
    http.post('/api/digital-interviewer/virtual-human/ping', { session_id }, { timeout: 45000 }).then((res) => res.data),
  stopVirtualHuman: (session_id: string) =>
    http.post('/api/digital-interviewer/virtual-human/stop', { session_id }, { timeout: 45000 }).then((res) => res.data),

  // ---------- RAG ----------
  ragStats: () => http.get('/api/rag/stats').then((res) => res.data),
  ragStatus: () => http.get('/api/rag/status').then((res) => res.data),
  ragIndex: (payload: { source?: string; force_rebuild?: boolean }) =>
    http.post('/api/rag/index', payload, { timeout: 180000 }).then((res) => res.data),
  ragIndexSource: (source: string, payload: { force_rebuild?: boolean }) =>
    http.post(`/api/rag/index/${source}`, payload, { timeout: 180000 }).then((res) => res.data),
  ragQueryJob: (payload: { question: string; top_k?: number }) =>
    http.post('/api/rag/query/job', payload, { timeout: 60000 }).then((res) => res.data),
  ragQuerySkill: (payload: { question: string; top_k?: number }) =>
    http.post('/api/rag/query/skill', payload, { timeout: 60000 }).then((res) => res.data),
  ragQueryMatchExplain: (payload: { candidate_id: number; job_id: number; question?: string; top_k?: number }) =>
    http.post('/api/rag/query/match-explain', payload, { timeout: 60000 }).then((res) => res.data),
  ragQueryInterviewHint: (payload: { candidate_id: number; job_id: number; focus_skill: string; top_k?: number }) =>
    http.post('/api/rag/query/interview-hint', payload, { timeout: 60000 }).then((res) => res.data),

  // ---------- Workflow Editor ----------
  workflowDocsList: () => http.get('/api/workflow/docs').then((res) => res.data),
  workflowDocsUpload: (file: File) => {
    const form = new FormData()
    form.append('file', file, file.name)
    return http.post('/api/workflow/docs/upload', form, { timeout: 60000 }).then((res) => res.data)
  },
  workflowDocsDelete: (id: number) => http.delete(`/api/workflow/docs/${id}`).then((res) => res.data),
  workflowDocsChunk: (id: number, payload: { chunk_size?: number; chunk_overlap?: number }) =>
    http.post(`/api/workflow/docs/${id}/chunk`, payload, { timeout: 120000 }).then((res) => res.data),
  workflowConfigsList: () => http.get('/api/workflow/configs').then((res) => res.data),
  workflowConfigsGet: (id: number) => http.get(`/api/workflow/configs/${id}`).then((res) => res.data),
  workflowConfigsSave: (payload: unknown) =>
    http.post('/api/workflow/configs', payload).then((res) => res.data),
  workflowConfigsUpdate: (id: number, payload: unknown) =>
    http.put(`/api/workflow/configs/${id}`, payload).then((res) => res.data),
  workflowConfigsDelete: (id: number) => http.delete(`/api/workflow/configs/${id}`).then((res) => res.data),
  workflowConfigTestRun: (id: number, payload: { question: string; top_k?: number }) =>
    http.post(`/api/workflow/configs/${id}/test`, payload, { timeout: 60000 }).then((res) => res.data),
}

import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'

const hrRoles = ['hr', 'admin']
const candidateRoles = ['candidate']
const allRoles = ['candidate', 'hr', 'admin']

const routes = [
  { path: '/login', name: 'login', component: () => import('@/views/Login.vue'), meta: { public: true, title: '登录' } },
  { path: '/showcase', name: 'showcase', component: () => import('@/views/Showcase.vue'), meta: { public: true, title: '项目展示' } },
  { path: '/growth-cockpit', redirect: '/overview' },
  { path: '/candidate/dashboard', redirect: '/overview' },
  { path: '/capability-evolution-direct', name: 'capability-evolution-direct', component: () => import('@/views/CapabilityEvolution.vue'), meta: { public: true, title: '能力演化' } },
  {
    path: '/',
    component: MainLayout,
    redirect: '/overview',
    children: [
      { path: 'overview', name: 'overview', component: () => import('@/views/Overview.vue'), meta: { title: '系统概览', roles: allRoles } },
      { path: 'dashboards/candidate', name: 'dashboards-candidate', component: () => import('@/views/dashboards/CandidateDashboard.vue'), meta: { title: '求职者驾驶舱', roles: candidateRoles, fullscreen: true } },
      { path: 'dashboards/hr', name: 'dashboards-hr', component: () => import('@/views/dashboards/HrDashboard.vue'), meta: { title: '企业 HR 大屏', roles: ['hr'] } },
      { path: 'dashboards/admin', name: 'dashboards-admin', component: () => import('@/views/dashboards/AdminDataHub.vue'), meta: { title: '管理员数据中枢', roles: ['admin'], fullscreen: true } },
      { path: 'cockpit', name: 'growth-cockpit-nested', component: () => import('@/views/GrowthCockpit.vue'), meta: { title: '个人成长驾驶舱', roles: candidateRoles, fullscreen: true } },
      { path: 'personal-center', redirect: '/overview' },
      { path: 'hr-candidates', name: 'hr-candidates', component: () => import('@/views/HrCandidates.vue'), meta: { title: '候选人管理', roles: hrRoles } },
      { path: 'datasets', name: 'datasets', component: () => import('@/views/Datasets.vue'), meta: { title: '权威数据源中心', roles: hrRoles } },
      { path: 'jd-parser', name: 'jd-parser', component: () => import('@/views/JdParser.vue'), meta: { title: 'JD解析', roles: hrRoles } },
      { path: 'jobs', name: 'jobs', component: () => import('@/views/Jobs.vue'), meta: { title: '岗位管理', roles: hrRoles } },
      { path: 'emerging-jobs', name: 'emerging-jobs', component: () => import('@/views/EmergingJobs.vue'), meta: { title: '新岗位发现', roles: hrRoles } },
      { path: 'job-evolution', name: 'job-evolution', component: () => import('@/views/JobEvolution.vue'), meta: { title: '岗位能力更新', roles: hrRoles } },
      { path: 'skill-graph', name: 'skill-graph', component: () => import('@/views/SkillGraph.vue'), meta: { title: '能力图谱', roles: allRoles } },
      { path: 'graph-explore', redirect: '/skill-graph' },
      { path: 'capability-evolution', name: 'capability-evolution', component: () => import('@/views/CapabilityEvolution.vue'), meta: { public: true, title: '能力演化', roles: allRoles } },
      { path: 'resume-parser', name: 'resume-parser', component: () => import('@/views/ResumeParser.vue'), meta: { title: '简历解析', roles: allRoles } },
      { path: 'match-analysis', name: 'match-analysis', component: () => import('@/views/MatchAnalysis.vue'), meta: { title: '匹配分析', roles: allRoles } },
      { path: 'digital-interviewer', name: 'digital-interviewer', component: () => import('@/views/DigitalInterviewer.vue'), meta: { title: '数字人面试官', roles: allRoles } },
      { path: 'learning-path', name: 'learning-path', component: () => import('@/views/LearningPath.vue'), meta: { title: '学习路径', roles: candidateRoles } },
      { path: 'review-tasks', name: 'review-tasks', component: () => import('@/views/ReviewTasks.vue'), meta: { title: '人工审核', roles: hrRoles } },
      { path: 'evaluation', name: 'evaluation', component: () => import('@/views/Evaluation.vue'), meta: { title: '测试评估', roles: hrRoles } },
      { path: 'rag-admin', name: 'rag-admin', component: () => import('@/views/RagWorkflowEditor.vue'), meta: { title: 'RAG 工作流编辑器', roles: hrRoles } },
      { path: 'settings', name: 'settings', component: () => import('@/views/Settings.vue'), meta: { title: '系统设置', roles: hrRoles } },
      { path: 'account-settings', name: 'account-settings', component: () => import('@/views/AccountSettings.vue'), meta: { title: '账号设置', roles: allRoles } }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  if (to.meta.public) return true
  const token = localStorage.getItem('auth_token')
  const user = JSON.parse(localStorage.getItem('auth_user') || 'null')
  if (!token || !user) return { path: '/login', query: { redirect: to.fullPath } }
  const roles = (to.meta.roles as string[] | undefined) || allRoles
  if (!roles.includes(user.role)) {
    return user.role === 'candidate' ? '/personal-center' : '/overview'
  }
  return true
})

export default router

<template>
  <div class="page match-page">
    <PageHeader title="匹配分析" desc="用岗位要求逐项核对技能与经历，生成可追溯的评分、证据和行动建议">
      <div class="toolbar">
        <el-tag effect="plain">证据评分 v2</el-tag>
        <el-button :loading="initializing" @click="loadBaseData">刷新数据</el-button>
      </div>
    </PageHeader>

    <section class="panel setup-panel">
      <div class="setup-main">
        <div class="section-title">
          <div>
            <span>开始一次新分析</span>
            <h3>选择候选人资料与目标岗位</h3>
          </div>
          <small>分析完成后会保存到历史记录，不会覆盖旧报告</small>
        </div>

        <div class="source-grid">
          <div class="field-block">
            <label>资料来源</label>
            <el-radio-group v-model="sourceType" class="source-switch">
              <el-radio-button v-if="isCandidate" value="profile">我的个人画像</el-radio-button>
              <el-radio-button value="resume">已保存简历</el-radio-button>
            </el-radio-group>
            <div v-if="sourceType === 'profile'" class="selection-card">
              <div class="selection-avatar">{{ profileName.slice(0, 1) }}</div>
              <div>
                <b>{{ profileName }}</b>
                <p>{{ profileSummary }}</p>
                <span>{{ profile?.skills?.length || 0 }} 项技能 · {{ profile?.projects?.length || 0 }} 个项目 · {{ profile?.internships?.length || 0 }} 段实习</span>
              </div>
            </div>
            <el-select v-else v-model="resumeId" filterable placeholder="请选择一份简历" class="wide-select">
              <el-option v-for="item in resumes" :key="item.id" :label="resumeOptionLabel(item)" :value="item.id">
                <span>{{ item.name || `简历 ${item.id}` }}</span>
                <small class="option-meta">{{ item.source_filename || `记录 #${item.id}` }} · {{ formatDate(item.created_at) }}</small>
              </el-option>
            </el-select>
          </div>

          <div class="field-block">
            <label>目标岗位</label>
            <el-select v-model="jobId" filterable placeholder="搜索并选择岗位" class="wide-select">
              <el-option v-for="item in jobs" :key="item.id" :label="item.name" :value="item.id">
                <span>{{ item.name }}</span>
                <small class="option-meta">{{ item.domain }} · {{ item.level }}</small>
              </el-option>
            </el-select>
            <div v-if="selectedJob" class="job-preview">
              <div>
                <b>{{ selectedJob.name }}</b>
                <span>{{ selectedJob.domain }} · {{ selectedJob.level }} · {{ selectedJob.job_type }}</span>
              </div>
              <p>{{ selectedJob.description }}</p>
              <div class="job-requirement-preview">
                <span>{{ selectedJob.requirements?.required_skills?.length || 0 }} 项必备能力</span>
                <span>{{ selectedJob.requirements?.preferred_skills?.length || 0 }} 项加分能力</span>
                <span>{{ selectedJob.requirements?.recommended_certificates?.length || 0 }} 项建议证书</span>
              </div>
            </div>
          </div>
        </div>

        <div class="run-row">
          <p>评分由确定性规则计算，DeepSeek 负责语义解释、简历改写与面试建议，不会修改分数。</p>
          <el-button type="primary" size="large" :loading="loading" :disabled="!canSubmit" @click="submit">
            {{ loading ? '正在读取证据并分析' : '开始匹配分析' }}
          </el-button>
        </div>
      </div>

      <aside class="history-panel">
        <div class="history-head">
          <div>
            <span>历史报告</span>
            <b>{{ history.length }} 份</b>
          </div>
          <small>点击即可查看</small>
        </div>
        <div v-if="history.length" class="history-list">
          <button
            v-for="item in history"
            :key="item.report_id"
            type="button"
            class="history-item"
            :class="{ active: report?.report_id === item.report_id }"
            @click="loadReport(item.report_id)"
          >
            <span>{{ item.target_job }}</span>
            <strong>{{ item.total_score }}%</strong>
            <small>{{ item.candidate_name }} · {{ formatDate(item.created_at) }}</small>
          </button>
        </div>
        <el-empty v-else description="还没有匹配报告" :image-size="68" />
      </aside>
    </section>

    <section v-if="!report" class="panel empty-report">
      <div class="empty-mark">01</div>
      <div>
        <h3>选择资料后再开始分析</h3>
        <p>系统会依次核对必备技能、加分技能、项目证据、工具平台、业务场景和证书成果。</p>
      </div>
      <div class="empty-steps">
        <span>选择资料</span><i>→</i><span>读取岗位要求</span><i>→</i><span>证据评分</span><i>→</i><span>AI 解释</span>
      </div>
    </section>

    <template v-else>
      <section class="panel result-hero">
        <div class="identity-card">
          <span>候选人资料</span>
          <h3>{{ report.candidate?.name || '候选人' }}</h3>
          <p>{{ candidateReportSummary }}</p>
          <el-tag effect="plain">{{ sourceLabel(report.candidate?.source_type) }}</el-tag>
        </div>
        <div class="identity-card job">
          <span>目标岗位</span>
          <h3>{{ report.target_job }}</h3>
          <p>{{ report.job_profile?.domain }} · {{ report.job_profile?.level }} · {{ report.job_profile?.job_type }}</p>
          <div class="skill-line">
            <el-tag v-for="item in report.job_profile?.required_skills?.slice(0, 4) || []" :key="item" size="small">{{ item }}</el-tag>
          </div>
          <div v-if="report.job_profile?.recommended_certificates?.length" class="certificate-line">
            建议证书：{{ report.job_profile.recommended_certificates.map((item: any) => item.name).join('、') }}
          </div>
        </div>
        <div class="score-card" :class="scoreLevel.className">
          <span>综合匹配度</span>
          <strong>{{ report.total_score }}%</strong>
          <em>{{ scoreLevel.label }}</em>
        </div>
      </section>

      <div class="report-meta">
        <span>报告 #{{ report.report_id }}</span>
        <span>评分可信度 {{ report.confidence_label }}（{{ report.confidence }}%）</span>
        <span>{{ report.scoring_version }}</span>
        <span>能力目录 {{ report.job_profile?.authority?.catalog_version || '-' }}</span>
        <span>{{ report.ai_provider === 'mock' ? '模拟 AI' : `AI：${report.ai_provider}${report.ai_model ? ` / ${report.ai_model}` : ''}` }}</span>
        <span>{{ formatDate(report.created_at) }}</span>
      </div>

      <section class="report-grid">
        <div class="panel dimensions-panel">
          <div class="section-title">
            <div><span>评分与证据</span><h3>六项维度拆解</h3></div>
            <small>总分按岗位能力模型加权计算</small>
          </div>
          <div class="dimension-list">
            <details v-for="item in dimensions" :key="item.name" class="dimension-card">
              <summary>
                <div class="dimension-name"><b>{{ item.name }}</b><small>权重 {{ item.weight }}%</small></div>
                <div class="dimension-progress"><el-progress :percentage="item.score" :stroke-width="10" :show-text="false" /><strong>{{ item.score }}%</strong></div>
                <span class="expand-label">查看证据</span>
              </summary>
              <div class="dimension-detail">
                <p>{{ item.summary }}</p>
                <div v-if="item.matched?.length" class="evidence-group"><b>已匹配</b><div><el-tag v-for="row in item.matched" :key="row" type="success" effect="light">{{ row }}</el-tag></div></div>
                <div v-if="item.missing?.length" class="evidence-group"><b>待补齐</b><div><el-tag v-for="row in item.missing" :key="row" type="danger" effect="light">{{ row }}</el-tag></div></div>
                <div v-if="item.evidence?.length" class="evidence-lines"><b>证据来源</b><p v-for="row in item.evidence" :key="row">{{ row }}</p></div>
              </div>
            </details>
          </div>
        </div>

        <div class="panel radar-panel">
          <div class="section-title"><div><span>能力轮廓</span><h3>岗位覆盖雷达</h3></div></div>
          <div class="radar-box"><EChart :option="radarOption" /></div>
        </div>

        <div class="panel skills-panel">
          <div class="section-title"><div><span>技能核对</span><h3>已覆盖与关键缺口</h3></div></div>
          <div class="skill-columns">
            <div class="skill-box success"><b>已匹配 {{ report.matched_skills?.length || 0 }} 项</b><div><el-tag v-for="item in report.matched_skills || []" :key="item" type="success" effect="light">{{ item }}</el-tag><span v-if="!report.matched_skills?.length">暂无直接证据</span></div></div>
            <div class="skill-box danger"><b>缺失必备 {{ report.missing_skills?.length || 0 }} 项</b><div><el-tag v-for="item in report.missing_skills || []" :key="item" type="danger" effect="light">{{ item }}</el-tag><span v-if="!report.missing_skills?.length">必备技能已基本覆盖</span></div></div>
          </div>
        </div>

        <div class="panel quality-panel">
          <div class="section-title"><div><span>输入质量</span><h3>本次分析依据</h3></div></div>
          <div class="quality-grid">
            <div><strong>{{ report.data_quality?.candidate_skill_count || 0 }}</strong><span>技能</span></div>
            <div><strong>{{ report.data_quality?.project_count || 0 }}</strong><span>项目</span></div>
            <div><strong>{{ report.data_quality?.internship_count || 0 }}</strong><span>实习</span></div>
            <div><strong>{{ report.data_quality?.certificate_count || 0 }}</strong><span>证书</span></div>
          </div>
          <p>可信度低时，建议先到个人中心补充项目职责、技术栈和量化结果，再重新分析。</p>
        </div>
      </section>

      <section class="panel ai-report">
        <div class="ai-summary">
          <span>AI 综合判断</span>
          <h3>{{ report.ai_analysis?.verdict || scoreLevel.label }}</h3>
          <p>{{ report.ai_analysis?.summary || 'AI 未返回总结，请参考确定性评分和证据。' }}</p>
          <small>{{ report.ai_analysis?.confidence_note }}</small>
        </div>
        <div class="ai-column">
          <h4>下一步行动</h4>
          <ol><li v-for="item in effectiveSuggestions" :key="item">{{ item }}</li></ol>
        </div>
        <div class="ai-column warning">
          <h4>风险与证据缺口</h4>
          <ul><li v-for="item in report.ai_analysis?.risk_points || []" :key="item">{{ item }}</li><li v-if="!report.ai_analysis?.risk_points?.length">暂无额外风险提示</li></ul>
        </div>
        <div class="ai-column">
          <h4>简历改写建议</h4>
          <ul><li v-for="item in report.ai_analysis?.resume_rewrites || []" :key="item">{{ item }}</li><li v-if="!report.ai_analysis?.resume_rewrites?.length">补充岗位相关项目的职责和结果</li></ul>
        </div>
        <div class="ai-column interview">
          <h4>面试重点准备</h4>
          <ul><li v-for="item in report.ai_analysis?.interview_focus || []" :key="item">{{ item }}</li><li v-if="!report.ai_analysis?.interview_focus?.length">围绕关键项目准备背景、行动和结果</li></ul>
        </div>
        <div class="report-actions">
          <el-button type="primary" @click="goLearningPath">基于本报告生成学习路径</el-button>
          <el-button @click="router.push('/personal-center')">补充个人画像</el-button>
          <el-button @click="router.push('/digital-interviewer')">进入面试练习</el-button>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import EChart from '@/components/EChart.vue'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'
import { useAuthStore } from '@/stores/auth'
import { loadPageState, savePageState } from '@/utils/pageState'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const jobs = ref<any[]>([])
const resumes = ref<any[]>([])
const profile = ref<any>()
const history = ref<any[]>([])
const report = ref<any>()
const sourceType = ref<'profile' | 'resume'>(auth.role === 'candidate' ? 'profile' : 'resume')
const resumeId = ref<number>()
const jobId = ref<number>()
const initializing = ref(false)
const loading = ref(false)

type MatchPageState = {
  sourceType?: 'profile' | 'resume'
  resumeId?: number
  jobId?: number
  reportId?: number
}

function persistState() {
  savePageState<MatchPageState>('match-analysis', {
    sourceType: sourceType.value,
    resumeId: resumeId.value,
    jobId: jobId.value,
    reportId: report.value?.report_id
  })
}

const isCandidate = computed(() => auth.role === 'candidate')
const selectedJob = computed(() => jobs.value.find((item) => item.id === jobId.value))
const profileName = computed(() => profile.value?.real_name || auth.user?.display_name || '我的画像')
const profileSummary = computed(() => [profile.value?.education, profile.value?.major, profile.value?.school].filter(Boolean).join(' · ') || '尚未补充教育背景')
const canSubmit = computed(() => Boolean(jobId.value && (sourceType.value === 'profile' ? profile.value : resumeId.value)))
const dimensions = computed<any[]>(() => report.value?.dimension_rows || [])
const effectiveSuggestions = computed<string[]>(() => report.value?.ai_analysis?.suggestions?.length ? report.value.ai_analysis.suggestions : report.value?.suggestions || [])
const candidateReportSummary = computed(() => [report.value?.candidate?.education, report.value?.candidate?.major, report.value?.candidate?.school].filter(Boolean).join(' · ') || '资料摘要未填写')

const scoreLevel = computed(() => {
  const score = Number(report.value?.total_score || 0)
  if (score >= 85) return { label: '高度匹配', className: 'excellent' }
  if (score >= 70) return { label: '建议进入面试', className: 'good' }
  if (score >= 55) return { label: '补强后可投递', className: 'medium' }
  return { label: '当前差距较大', className: 'low' }
})

const radarOption = computed(() => ({
  tooltip: { trigger: 'item' },
  radar: {
    radius: '66%', center: ['50%', '53%'], splitNumber: 4,
    axisName: { color: '#8fc3e8', fontWeight: 700 },
    splitLine: { lineStyle: { color: ['rgba(82, 221, 255,.16)'] } },
    splitArea: { areaStyle: { color: ['rgba(10, 169, 180,.04)', 'rgba(82, 221, 255,.06)'] } },
    axisLine: { lineStyle: { color: 'rgba(82, 221, 255,.20)' } },
    indicator: dimensions.value.map((item) => ({ name: item.name, max: 100 }))
  },
  series: [{ type: 'radar', areaStyle: { color: 'rgba(82, 221, 255,.22)' }, lineStyle: { color: '#52ddff', width: 2 }, itemStyle: { color: '#0aa9b4' }, data: [{ value: dimensions.value.map((item) => item.score || 0) }] }]
}))

async function loadBaseData() {
  initializing.value = true
  try {
    const cachedState = loadPageState<MatchPageState>('match-analysis')
    if (cachedState?.sourceType && (cachedState.sourceType !== 'profile' || isCandidate.value)) sourceType.value = cachedState.sourceType
    if (cachedState?.resumeId) resumeId.value = cachedState.resumeId
    if (cachedState?.jobId) jobId.value = cachedState.jobId
    await migrateLegacyParsedResume()
    const requests: Promise<any>[] = [api.jobs(), api.resumes(), api.matchAnalysisHistory()]
    if (isCandidate.value) requests.push(api.myProfile())
    const [jobRows, resumeRows, historyRows, profileRow] = await Promise.all(requests)
    jobs.value = jobRows || []
    resumes.value = resumeRows || []
    history.value = historyRows || []
    profile.value = profileRow
    const queryJobId = Number(route.query.jobId || 0)
    if (queryJobId && jobs.value.some((item) => item.id === queryJobId)) jobId.value = queryJobId
    // 支持按岗位名称定位（例如从能力演化树"查看岗位详情"跳转而来）
    const queryJobName = String(route.query.jobName || '')
    if (!jobId.value && queryJobName) {
      const matchedJob = jobs.value.find((item: any) => item.name === queryJobName || item.name.includes(queryJobName) || queryJobName.includes(item.name))
      if (matchedJob) jobId.value = matchedJob.id
    }
    if (!jobId.value) jobId.value = jobs.value[0]?.id
    if (!resumeId.value) resumeId.value = resumes.value[0]?.id
    const cachedReportId = cachedState?.reportId
    const reportToRestore = history.value.find((item) => item.report_id === cachedReportId) || history.value[0]
    if (!report.value && reportToRestore) await loadReport(reportToRestore.report_id, false)
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '匹配分析基础数据加载失败')
  } finally {
    initializing.value = false
  }
}

async function migrateLegacyParsedResume() {
  const cached = localStorage.getItem('last_parsed_resume')
  if (!cached) return
  try {
    const parsed = JSON.parse(cached)
    if (!parsed || parsed.resume_id) return
    const saved = await api.saveParsedResume({ resume: parsed, source_filename: '修复前的最近一次解析简历' })
    parsed.resume_id = saved.id
    parsed.saved_at = saved.created_at
    localStorage.setItem('last_parsed_resume', JSON.stringify(parsed))
    ElMessage.success('已将之前解析的简历补存到历史简历')
  } catch {
    // 旧缓存损坏时不阻塞匹配分析页面，其余数据仍可正常加载。
  }
}

async function submit() {
  if (!canSubmit.value) return ElMessage.warning('请先选择候选人资料和目标岗位')
  loading.value = true
  try {
    const payload = sourceType.value === 'profile'
      ? { use_profile: true, target_job_id: jobId.value }
      : { resume_id: resumeId.value, target_job_id: jobId.value }
    report.value = await api.matchAnalysis(payload)
    localStorage.setItem('last_match_report', JSON.stringify(report.value))
    persistState()
    await loadHistory()
    ElMessage.success('匹配分析已完成并保存到历史报告')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '匹配分析失败，请检查 AI 配置和候选人资料')
  } finally {
    loading.value = false
  }
}

async function loadHistory() {
  history.value = await api.matchAnalysisHistory()
}

async function loadReport(id: number, notify = true) {
  try {
    report.value = await api.matchAnalysisDetail(id)
    localStorage.setItem('last_match_report', JSON.stringify(report.value))
    persistState()
    if (notify) ElMessage.success(`已打开历史报告 #${id}`)
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '历史报告读取失败')
  }
}

function goLearningPath() {
  if (!report.value?.report_id) return
  router.push({ path: '/learning-path', query: { reportId: String(report.value.report_id) } })
}

function sourceLabel(value = '') {
  return value === 'profile' ? '个人画像' : value === 'resume' ? '数据库简历' : '资料快照'
}

function resumeOptionLabel(item: any) {
  const source = item.source_filename || `记录 #${item.id}`
  return `${item.name || '未命名简历'} · ${source}`
}

function formatDate(value?: string) {
  if (!value) return '刚刚'
  return new Intl.DateTimeFormat('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }).format(new Date(value))
}

watch([sourceType, resumeId, jobId], persistState)

onMounted(loadBaseData)
</script>

<style scoped>
/* ===== Dark-Teal 深墨绿 核心 token：
   --panel: rgba(6, 32, 54,.38)  --edge: rgba(82, 221, 255,.10)
   --cyan: #52ddff  --teal: #0aa9b4  --text: #d8eef5  --muted: #6e96a8
   玻璃: backdrop-filter: blur(26px) saturate(1.18)  阴影 0 24px 62px rgba(0,10,14,.16)
   圆角：大面板 20px、次级 14px、胶囊 999px
*/
.match-page {
  gap: 16px;
  --panel: rgba(6, 32, 54, .38);
  --edge: rgba(82, 221, 255, .10);
  --cyan: #52ddff;
  --teal: #0aa9b4;
  --text: #d8eef5;
  --muted: #6e96a8;
  --text-strong: #011719;
  --success: #8ad8bb;
  --warn: #ffc048;
  --danger: #ff5d7d;
}
.match-page :deep(.page-header) { border-color: var(--edge) !important; color: var(--text); }

.panel {
  border: 1px solid var(--edge);
  border-radius: 20px;
  background: linear-gradient(145deg, rgba(8, 42, 68, .28), rgba(3, 18, 36, .32));
  box-shadow: 0 24px 62px rgba(0, 10, 14, .16), inset 0 1px 0 rgba(141, 255, 255, .025);
  backdrop-filter: blur(26px) saturate(1.18);
  color: var(--text);
  padding: 22px 24px;
}
.setup-panel { display: grid; grid-template-columns: minmax(0, 1fr) 300px; gap: 16px; }
.setup-main { min-width: 0; }
.section-title { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 18px; }
.section-title span, .history-head span, .identity-card > span, .ai-summary > span {
  display: block;
  color: var(--cyan);
  font-size: 10px;
  font-weight: 900;
  letter-spacing: .14em;
  text-transform: uppercase;
  text-shadow: 0 0 8px rgba(82, 221, 255, .30);
}
.section-title h3, .ai-summary h3 { margin: 6px 0 0; color: var(--text); font-size: 21px; letter-spacing: -.04em; }
.section-title small, .history-head small { color: var(--muted); font-weight: 700; }
.source-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.field-block {
  display: flex; min-width: 0; flex-direction: column; gap: 10px;
  border: 1px solid rgba(82, 221, 255, .12);
  border-radius: 14px;
  padding: 16px;
  background: linear-gradient(160deg, rgba(8, 42, 68, .22), rgba(3, 18, 36, .18));
  backdrop-filter: blur(19px) saturate(1.15);
}
.field-block > label { color: #b9d8ee; font-size: 12px; font-weight: 800; letter-spacing: .02em; }
.source-switch, .wide-select { width: 100%; }
.source-switch :deep(.el-radio-button) { flex: 1; }
.source-switch :deep(.el-radio-button__inner) { width: 100%; }
.selection-card {
  display: grid; grid-template-columns: 52px minmax(0, 1fr); align-items: center; gap: 12px;
  min-height: 84px; border-radius: 12px; padding: 12px;
  border: 1px solid rgba(82, 221, 255, .10);
  background: rgba(6, 32, 54, .20);
  backdrop-filter: blur(18px) saturate(1.12);
}
.selection-avatar {
  display: grid; place-items: center; width: 50px; height: 50px; border-radius: 14px;
  color: #eef8ff;
  background: linear-gradient(135deg, var(--teal), var(--cyan) 60%, #7fd4ff);
  box-shadow: 0 0 16px rgba(82, 221, 255, .28), inset 0 1px 0 rgba(141, 255, 255, .22);
  font-size: 20px; font-weight: 900;
}
.selection-card b, .job-preview b { color: var(--text); }
.selection-card p, .job-preview p { margin: 5px 0 0; color: var(--muted); font-size: 12px; font-weight: 700; line-height: 1.55; }
.selection-card span, .job-preview span { display: block; margin-top: 5px; color: #8fb7d8; font-size: 11px; }
.job-preview {
  min-height: 84px; border-radius: 12px; padding: 12px;
  border: 1px solid rgba(82, 221, 255, .10);
  background: rgba(6, 32, 54, .20);
  backdrop-filter: blur(18px) saturate(1.12);
}
.job-preview p { display: -webkit-box; overflow: hidden; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.job-requirement-preview { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.job-requirement-preview span {
  margin: 0; border-radius: 999px; padding: 4px 9px;
  border: 1px solid rgba(82, 221, 255, .18);
  color: #8fdcff;
  background: rgba(0, 142, 156, .12);
  backdrop-filter: blur(8px);
  font-size: 11px; font-weight: 700;
}
.certificate-line { margin-top: 8px; color: var(--muted); font-size: 11px; line-height: 1.6; }
.option-meta { float: right; color: #8fb7d8; }
.run-row {
  display: flex; align-items: center; justify-content: space-between; gap: 18px;
  margin-top: 16px;
  border-top: 1px solid rgba(82, 221, 255, .08);
  padding-top: 16px;
}
.run-row p { margin: 0; color: var(--muted); font-size: 12px; font-weight: 700; line-height: 1.7; }
.run-row :deep(.el-button) { min-width: 174px; }
.history-panel {
  min-width: 0;
  border-left: 1px solid rgba(82, 221, 255, .08);
  padding-left: 18px;
  display: flex;
  flex-direction: column;
}
.history-head { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 12px; }
.history-head b { display: block; margin-top: 5px; color: var(--text); }
.history-list { display: grid; gap: 8px; max-height: 238px; overflow-y: auto; }
.history-item {
  display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 4px 10px;
  border: 1px solid rgba(82, 221, 255, .12);
  border-radius: 12px; padding: 10px 12px;
  background: rgba(6, 32, 54, .22);
  backdrop-filter: blur(16px) saturate(1.12);
  color: var(--text);
  text-align: left;
  cursor: pointer;
}
.history-item:hover, .history-item.active {
  border-color: rgba(141, 255, 255, .48);
  background: rgba(10, 169, 180, .16);
  transform: translateY(-1px);
}
.history-item span { overflow: hidden; font-size: 13px; font-weight: 800; text-overflow: ellipsis; white-space: nowrap; }
.history-item strong { color: var(--cyan); text-shadow: 0 0 8px rgba(82, 221, 255, .35); }
.history-item small { grid-column: 1 / -1; color: var(--muted); }
.empty-report { display: grid; grid-template-columns: 66px minmax(0, 1fr) auto; align-items: center; gap: 18px; min-height: 150px; }
.empty-mark {
  display: grid; place-items: center; width: 60px; height: 60px; border-radius: 18px;
  color: #eef8ff;
  background: linear-gradient(135deg, var(--teal), var(--cyan) 62%, #7fd4ff);
  box-shadow: 0 0 20px rgba(82, 221, 255, .28), inset 0 1px 0 rgba(141, 255, 255, .25);
  font-weight: 900;
}
.empty-report h3 { margin: 0 0 8px; color: var(--text); }
.empty-report p { margin: 0; color: var(--muted); }
.empty-steps { display: flex; align-items: center; gap: 10px; color: #8fb7d8; font-size: 12px; font-weight: 700; }
.empty-steps i { color: var(--cyan); font-style: normal; text-shadow: 0 0 8px rgba(82, 221, 255, .35); }
.result-hero { display: grid; grid-template-columns: 1fr 1fr 230px; gap: 14px; padding: 20px 22px; }
.identity-card {
  min-height: 138px;
  border: 1px solid rgba(82, 221, 255, .12);
  border-radius: 14px;
  padding: 18px;
  background: linear-gradient(160deg, rgba(8, 42, 68, .20), rgba(3, 18, 36, .16));
  backdrop-filter: blur(20px) saturate(1.15);
}
.identity-card.job { background: linear-gradient(160deg, rgba(8, 42, 68, .24), rgba(2, 8, 24, .20)); }
.identity-card h3 { margin: 8px 0; color: var(--text); font-size: 22px; letter-spacing: -.04em; }
.identity-card p { margin: 0 0 12px; color: var(--muted); font-weight: 700; }
.skill-line { display: flex; flex-wrap: wrap; gap: 6px; }
.score-card {
  display: flex; flex-direction: column; justify-content: center; min-height: 138px; overflow: hidden;
  border-radius: 16px; padding: 22px;
  color: #eef8ff;
  border: 1px solid rgba(82, 221, 255, .16);
  background: radial-gradient(64% 60% at 10% 0%, rgba(82, 221, 255, .36), transparent 58%),
              linear-gradient(135deg, rgba(10, 169, 180, .30), rgba(3, 28, 56, .62) 64%, rgba(82, 221, 255, .26));
  box-shadow: 0 18px 44px rgba(10, 169, 180, .18), 0 0 22px rgba(82, 221, 255, .16);
  backdrop-filter: blur(24px) saturate(1.2);
}
.score-card strong { margin: 8px 0; font-size: 46px; line-height: 1; text-shadow: 0 0 10px rgba(82, 221, 255, .45); }
.score-card em { font-style: normal; font-weight: 900; }
.score-card.good { background: radial-gradient(62% 58% at 12% 0%, rgba(126, 231, 255, .42), transparent 58%), linear-gradient(135deg, rgba(10, 169, 180, .30), rgba(8, 42, 68, .64) 64%, rgba(126, 231, 255, .30)); box-shadow: 0 18px 44px rgba(10, 169, 180, .14), 0 0 18px rgba(126, 231, 255, .18); }
.score-card.medium { background: radial-gradient(62% 58% at 12% 0%, rgba(255, 192, 72, .38), transparent 58%), linear-gradient(135deg, rgba(6, 32, 54, .56), rgba(54, 40, 10, .42) 62%, rgba(82, 221, 255, .20)); }
.score-card.medium strong { text-shadow: 0 0 10px rgba(255, 192, 72, .45); }
.score-card.low { background: radial-gradient(62% 58% at 12% 0%, rgba(255, 93, 125, .32), transparent 58%), linear-gradient(135deg, rgba(3, 12, 28, .56), rgba(34, 10, 30, .36) 62%, rgba(82, 221, 255, .18)); }
.score-card.low strong { text-shadow: 0 0 10px rgba(255, 93, 125, .45); }
.report-meta { display: flex; flex-wrap: wrap; gap: 8px; margin: 6px 4px 0; }
.report-meta span {
  border: 1px solid rgba(82, 221, 255, .12);
  border-radius: 999px;
  padding: 6px 12px;
  color: var(--muted);
  background: rgba(6, 32, 54, .20);
  backdrop-filter: blur(14px);
  font-size: 11px;
  font-weight: 700;
}
.report-grid { display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); gap: 14px; margin-top: 14px; }
.dimensions-panel { grid-column: span 7; }
.radar-panel { grid-column: span 5; }
.skills-panel { grid-column: span 8; }
.quality-panel { grid-column: span 4; }
.dimension-list { display: grid; gap: 10px; }
.dimension-card {
  border: 1px solid rgba(82, 221, 255, .12);
  border-radius: 14px;
  background: rgba(6, 32, 54, .20);
  backdrop-filter: blur(18px) saturate(1.12);
}
.dimension-card summary {
  display: grid; grid-template-columns: 135px minmax(0, 1fr) 72px; align-items: center; gap: 14px;
  padding: 13px; cursor: pointer; list-style: none;
}
.dimension-card summary::-webkit-details-marker { display: none; }
.dimension-name b, .dimension-name small { display: block; }
.dimension-name b { color: var(--text); }
.dimension-name small { margin-top: 4px; color: var(--muted); }
.dimension-progress { display: grid; grid-template-columns: minmax(0, 1fr) 48px; align-items: center; gap: 10px; }
.dimension-progress strong { color: #cdeeff; text-align: right; text-shadow: 0 0 6px rgba(82, 221, 255, .22); }
.dimension-progress :deep(.el-progress-bar__outer) { background: rgba(0, 142, 156, .18); }
.dimension-progress :deep(.el-progress-bar__inner) { background: linear-gradient(90deg, var(--teal), var(--cyan)); box-shadow: 0 0 8px rgba(82, 221, 255, .42); }
.expand-label {
  color: var(--cyan);
  font-size: 11px; font-weight: 800; text-align: right;
  text-shadow: 0 0 6px rgba(82, 221, 255, .35);
}
.dimension-detail { border-top: 1px solid rgba(82, 221, 255, .08); padding: 14px; }
.dimension-detail > p { margin: 0 0 12px; color: var(--muted); font-size: 13px; font-weight: 700; }
.evidence-group { display: grid; grid-template-columns: 64px minmax(0, 1fr); gap: 10px; margin-top: 10px; }
.evidence-group > b, .evidence-lines > b { color: #b9d8ee; font-size: 12px; }
.evidence-group > div { display: flex; flex-wrap: wrap; gap: 6px; }
.evidence-lines { margin-top: 12px; }
.evidence-lines p {
  margin: 6px 0 0;
  border-radius: 10px;
  padding: 8px 10px;
  border: 1px solid rgba(82, 221, 255, .10);
  background: rgba(6, 32, 54, .24);
  color: #b9d8ee;
  font-size: 12px;
  line-height: 1.6;
}
.radar-box { height: 360px; }
.radar-box :deep(.chart) { height: 100%; }
.skill-columns { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.skill-box {
  min-height: 150px;
  border: 1px solid rgba(82, 221, 255, .12);
  border-radius: 14px;
  padding: 16px;
  background: rgba(6, 32, 54, .20);
  backdrop-filter: blur(18px) saturate(1.12);
}
.skill-box > b { color: var(--text); }
.skill-box > div { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
.skill-box > div > span { color: var(--muted); font-size: 13px; }
.skill-box.success { border-color: rgba(126, 231, 255, .26); background: linear-gradient(160deg, rgba(10, 70, 96, .22), rgba(6, 32, 54, .20)); }
.skill-box.danger { border-color: rgba(255, 93, 125, .24); background: linear-gradient(160deg, rgba(80, 20, 34, .22), rgba(6, 32, 54, .20)); }
.quality-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.quality-grid div {
  border-radius: 12px;
  padding: 14px;
  border: 1px solid rgba(82, 221, 255, .10);
  background: rgba(6, 32, 54, .18);
  backdrop-filter: blur(16px) saturate(1.12);
}
.quality-grid strong, .quality-grid span { display: block; }
.quality-grid strong { color: var(--cyan); font-size: 26px; text-shadow: 0 0 8px rgba(82, 221, 255, .35); }
.quality-grid span { margin-top: 4px; color: var(--muted); font-size: 12px; font-weight: 700; }
.quality-panel > p { margin: 14px 0 0; color: var(--muted); font-size: 12px; line-height: 1.75; }
.ai-report {
  display: grid;
  grid-template-columns: 1.1fr repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 14px;
  padding: 22px 24px;
}
.ai-summary {
  grid-row: span 2;
  border: 1px solid rgba(82, 221, 255, .18);
  border-radius: 16px;
  padding: 20px;
  background:
    radial-gradient(circle at 12% 8%, rgba(82, 221, 255, .18), transparent 38%),
    linear-gradient(160deg, rgba(8, 42, 68, .22), rgba(3, 18, 36, .18));
  backdrop-filter: blur(22px) saturate(1.15);
}
.ai-summary h3 { color: var(--text); letter-spacing: -.03em; }
.ai-summary p { color: #b9d8ee; font-weight: 700; line-height: 1.9; }
.ai-summary small { color: var(--muted); line-height: 1.7; }
.ai-column {
  border: 1px solid rgba(82, 221, 255, .12);
  border-radius: 14px;
  padding: 16px;
  background: rgba(6, 32, 54, .20);
  backdrop-filter: blur(18px) saturate(1.12);
}
.ai-column.warning {
  border-color: rgba(255, 192, 72, .22);
  background: linear-gradient(160deg, rgba(80, 58, 10, .22), rgba(6, 32, 54, .20));
}
.ai-column.interview {
  border-color: rgba(82, 221, 255, .18);
  background: linear-gradient(160deg, rgba(8, 50, 78, .24), rgba(3, 18, 36, .20));
}
.ai-column h4 { margin: 0 0 10px; color: var(--text); }
.ai-column ol, .ai-column ul { display: grid; gap: 8px; margin: 0; padding-left: 19px; color: #b9d8ee; font-size: 13px; font-weight: 700; line-height: 1.7; }
.report-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  grid-column: 1 / -1;
  border-top: 1px solid rgba(82, 221, 255, .08);
  padding-top: 16px;
}
@media (max-width: 1100px) {
  .setup-panel, .source-grid, .result-hero, .ai-report { grid-template-columns: 1fr; }
  .history-panel { border-top: 1px solid rgba(82, 221, 255, .08); border-left: 0; padding-top: 18px; padding-left: 0; }
  .dimensions-panel, .radar-panel, .skills-panel, .quality-panel { grid-column: span 12; }
  .ai-summary { grid-row: auto; }
  .empty-report { grid-template-columns: 66px 1fr; }
  .empty-steps { grid-column: 1 / -1; }
}
@media (max-width: 700px) {
  .skill-columns { grid-template-columns: 1fr; }
  .run-row, .section-title, .report-actions { align-items: stretch; flex-direction: column; }
  .run-row :deep(.el-button), .report-actions :deep(.el-button) { width: 100%; margin-left: 0; }
  .dimension-card summary { grid-template-columns: 1fr; }
  .expand-label { text-align: left; }
}
</style>

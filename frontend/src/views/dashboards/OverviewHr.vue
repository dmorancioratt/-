<template>
  <div class="cockpit hr-dashboard">
    <div v-if="loading" class="cockpit-loading">正在计算人才供需...</div>

    <header class="cockpit-heading">
      <div class="cockpit-heading__copy">
        <span class="cockpit-eyebrow">企业人才决策</span>
        <h1>岗位缺什么，人才库里谁最接近</h1>
        <p>以岗位必备技能为口径，对比候选人真实画像，直接给出供给缺口和下一步招聘动作。</p>
      </div>
      <div class="cockpit-heading__actions">
        <el-select v-model="selectedJobId" filterable placeholder="选择重点岗位" class="job-filter">
          <el-option label="全部岗位概览" :value="0" />
          <el-option v-for="job in model.jobs" :key="job.id" :label="job.name" :value="job.id" />
        </el-select>
      </div>
    </header>

    <section class="decision-brief">
      <article class="role-focus">
        <span>{{ selectedJob ? '当前重点岗位' : '人才库全局判断' }}</span>
        <h2>{{ selectedJob?.name || `${model.summary.job_count || model.jobs.length} 个岗位画像已覆盖` }}</h2>
        <p>{{ decisionSentence }}</p>
        <button type="button" @click="router.push(selectedJob ? '/jobs' : '/hr-candidates')">{{ selectedJob ? '查看岗位画像' : '进入候选人库' }}<el-icon><ArrowRight /></el-icon></button>
      </article>
      <button v-for="item in decisionKpis" :key="item.label" type="button" @click="router.push(item.path)">
        <span>{{ item.label }}</span><strong>{{ item.value }}</strong><small>{{ item.note }}</small><el-icon><component :is="item.icon" /></el-icon>
      </button>
    </section>

    <section class="hr-workspace">
      <article class="cockpit-panel gap-panel">
        <div class="cockpit-panel__head">
          <div><div class="cockpit-panel__title">技能需求与人才供给</div><p>{{ selectedJob?.name || '高频岗位集合' }} · 需求岗位数与具备该技能的人数</p></div>
          <span class="cockpit-tag warning">{{ urgentGapCount }} 项缺口</span>
        </div>
        <div class="gap-chart"><EChart :option="gapOption" /></div>
        <div class="gap-summary">
          <button v-for="skill in skillGap.slice(0, 3)" :key="skill.name" type="button" @click="router.push({ path: '/skill-graph', query: { keyword: skill.name } })">
            <span><b>{{ skill.name }}</b><small>需求 {{ skill.demand }} · 人才 {{ skill.supply }}</small></span>
            <strong :class="skill.shortage > 0 ? 'short' : 'enough'">{{ skill.shortage > 0 ? `缺 ${skill.shortage}` : '供给充足' }}</strong>
          </button>
        </div>
      </article>

      <article class="cockpit-panel talent-panel">
        <div class="cockpit-panel__head"><div><div class="cockpit-panel__title">优先联系人才</div><p>{{ selectedJob ? '按必备技能覆盖率排序' : '按资料完整度与简历准备度排序' }}</p></div><button class="text-button" type="button" @click="router.push('/hr-candidates')">查看全部</button></div>
        <div class="talent-list">
          <button v-for="(candidate, index) in rankedCandidates.slice(0, 5)" :key="candidate.user?.id || index" type="button" @click="router.push('/hr-candidates')">
            <span class="talent-rank">{{ index + 1 }}</span>
            <el-avatar :size="38">{{ (candidate.profile?.real_name || candidate.user?.display_name || '候').slice(0, 1) }}</el-avatar>
            <span class="talent-name"><b>{{ candidate.profile?.real_name || candidate.user?.display_name || '未命名候选人' }}</b><small>{{ candidate.profile?.target_role || '岗位意向待补充' }} · {{ candidate.resume_count || 0 }} 份简历</small></span>
            <span class="fit-score"><b>{{ candidate.fit }}%</b><small>{{ selectedJob ? '技能覆盖' : '资料可用' }}</small></span>
          </button>
          <div v-if="!rankedCandidates.length" class="cockpit-empty">人才库暂无可用候选人</div>
        </div>
      </article>
    </section>

    <section class="hr-secondary">
      <article class="cockpit-panel action-panel">
        <div class="cockpit-panel__head"><div><div class="cockpit-panel__title">建议招聘动作</div><p>按当前数据直接生成可执行任务</p></div></div>
        <div class="action-list">
          <button v-for="(action, index) in recruitmentActions" :key="action.title" type="button" @click="router.push(action.path)">
            <span>{{ String(index + 1).padStart(2, '0') }}</span><div><b>{{ action.title }}</b><small>{{ action.detail }}</small></div><em>{{ action.action }}</em><el-icon><ArrowRight /></el-icon>
          </button>
        </div>
      </article>

      <article class="cockpit-panel trend-panel">
        <div class="cockpit-panel__head"><div><div class="cockpit-panel__title">产业需求趋势</div><p>权威来源中的软件业务收入累计值</p></div><span class="source-badge">工信部公开统计</span></div>
        <div class="trend-chart"><EChart :option="trendOption" /></div>
      </article>

      <article class="cockpit-panel emerging-panel">
        <div class="cockpit-panel__head"><div><div class="cockpit-panel__title">新兴岗位观察</div><p>提前储备的能力方向</p></div></div>
        <div class="emerging-list">
          <button v-for="item in model.emerging.slice(0, 4)" :key="item.job_name || item.name" type="button" @click="router.push('/emerging-jobs')">
            <span><b>{{ item.job_name || item.name }}</b><small>{{ (item.skills || []).slice(0, 2).join(' · ') || '查看能力要求' }}</small></span><el-icon><ArrowRight /></el-icon>
          </button>
        </div>
      </article>
    </section>

    <!-- 底部数据状态栏：更新时间与更新操作集中在此，头部专注筛选决策 -->
    <footer class="overview-footer">
      <div class="overview-footer__status">
        <span class="status-dot" :class="{ busy: refreshing }"></span>
        <span>{{ refreshing ? '正在重新计算人才供需…' : '数据就绪' }}</span>
        <span class="footer-divider"></span>
        <span>更新于 {{ updatedLabel }}</span>
      </div>
      <button class="cockpit-button" type="button" :disabled="refreshing" @click="refresh(true)">
        <el-icon :class="{ 'fa-spin': refreshing }"><Refresh /></el-icon>{{ refreshing ? '更新中' : '更新数据' }}
      </button>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ArrowRight, Briefcase, DataAnalysis, Refresh, Tickets, TrendCharts } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import EChart from '@/components/EChart.vue'
import { api } from '@/api/http'
import { useAuthStore } from '@/stores/auth'
import { formatSnapshotTime, readDashboardSnapshot, settledValue, writeDashboardSnapshot } from '@/utils/dashboardCache'

type HrModel = { summary: any; candidates: any[]; jobs: any[]; datasets: any[]; reviews: any[]; emerging: any[]; graph: any; market: any }
const emptyModel: HrModel = { summary: {}, candidates: [], jobs: [], datasets: [], reviews: [], emerging: [], graph: {}, market: {} }
const router = useRouter()
const auth = useAuthStore()
const model = ref<HrModel>({ ...emptyModel })
const loading = ref(false)
const refreshing = ref(false)
const updatedAt = ref('')
const selectedJobId = ref(0)
const cacheKey = computed(() => `sr-dashboard:hr:${auth.user?.id || auth.user?.username || 'default'}:v5`)
const updatedLabel = computed(() => formatSnapshotTime(updatedAt.value))
const selectedJob = computed(() => model.value.jobs.find((job) => job.id === selectedJobId.value))
const pendingReviews = computed(() => model.value.reviews.filter((item) => item.status === 'pending'))
const selectedRequired = computed<string[]>(() => selectedJob.value?.requirements?.required_skills || [])

function skillName(value: any) { return String(typeof value === 'string' ? value : value?.name || '').trim() }
function normalize(value: string) { return value.toLowerCase().replace(/[\s.\-_/]+/g, '') }
function candidateFit(row: any) {
  if (!selectedJob.value) return Math.round(Number(row.profile?.completeness || 0))
  const candidateSkills = new Set((row.profile?.skills || []).map(skillName).filter(Boolean).map(normalize))
  const required = selectedRequired.value.map(normalize)
  return required.length ? Math.round(required.filter((name) => candidateSkills.has(name)).length / required.length * 100) : 0
}

const rankedCandidates = computed(() => model.value.candidates.map((row) => ({ ...row, fit: candidateFit(row) })).sort((a, b) => b.fit + (b.resume_count || 0) * 3 - a.fit - (a.resume_count || 0) * 3))
const readyCandidates = computed(() => rankedCandidates.value.filter((row) => row.fit >= (selectedJob.value ? 60 : 75)))
const skillSupply = computed(() => {
  const counts = new Map<string, number>()
  model.value.candidates.forEach((row) => (row.profile?.skills || []).forEach((skill: any) => { const name = skillName(skill); if (name) counts.set(name, (counts.get(name) || 0) + 1) }))
  return counts
})
const skillGap = computed(() => {
  const demand = new Map<string, number>()
  const pool = selectedJob.value ? [selectedJob.value] : model.value.jobs.slice(0, 30)
  pool.forEach((job) => (job.requirements?.required_skills || []).forEach((name: string) => demand.set(name, (demand.get(name) || 0) + 1)))
  return [...demand.entries()].map(([name, demandCount]) => { const supplyCount = skillSupply.value.get(name) || 0; return { name, demand: demandCount, supply: supplyCount, shortage: Math.max(0, demandCount - supplyCount) } }).sort((a, b) => b.shortage - a.shortage || b.demand - a.demand).slice(0, 10)
})
const urgentGapCount = computed(() => skillGap.value.filter((item) => item.shortage > 0).length)

const decisionSentence = computed(() => {
  if (!selectedJob.value) return `人才库现有 ${model.value.candidates.length} 人，${readyCandidates.value.length} 人资料达到可筛选标准；选择岗位后可查看必备技能覆盖。`
  const gaps = skillGap.value.filter((item) => item.shortage > 0).slice(0, 3).map((item) => item.name)
  return `${readyCandidates.value.length} 人达到 60% 必备技能覆盖；${gaps.length ? `优先补充 ${gaps.join('、')} 人才。` : '当前主要技能供给基本覆盖。'}`
})
const decisionKpis = computed(() => [
  { label: selectedJob.value ? '达到筛选线' : '人才库可筛选', value: `${readyCandidates.value.length} 人`, note: `总计 ${model.value.candidates.length} 人`, path: '/hr-candidates', icon: DataAnalysis },
  { label: '关键技能缺口', value: `${urgentGapCount.value} 项`, note: skillGap.value[0]?.name || '暂无明显缺口', path: '/skill-graph', icon: Tickets },
  { label: '岗位画像覆盖', value: `${model.value.summary.job_count || model.value.jobs.length} 个`, note: `${new Set(model.value.jobs.map((job) => job.domain)).size} 个领域`, path: '/jobs', icon: Briefcase },
  { label: '新兴岗位信号', value: `${model.value.summary.emerging_job_count || 0} 个`, note: '官方与国际趋势来源', path: '/emerging-jobs', icon: TrendCharts }
])

const recruitmentActions = computed(() => {
  const topGap = skillGap.value.find((item) => item.shortage > 0)?.name
  const incomplete = model.value.candidates.filter((row) => Number(row.profile?.completeness || 0) < 60).length
  return [
    readyCandidates.value.length ? { title: `联系前 ${Math.min(3, readyCandidates.value.length)} 名候选人`, detail: selectedJob.value ? `他们与 ${selectedJob.value.name} 的必备技能最接近` : '资料完整且已有简历记录', action: '查看人才', path: '/hr-candidates' } : { title: '先补充候选人资料', detail: '当前没有达到筛选线的人才', action: '查看人才', path: '/hr-candidates' },
    topGap ? { title: `围绕 ${topGap} 扩充人才`, detail: '当前需求高于人才库供给，建议加入 JD 筛选条件', action: '查看图谱', path: '/skill-graph' } : { title: '复核当前岗位画像', detail: '技能供给暂未出现明显短缺', action: '查看岗位', path: '/jobs' },
    { title: `完善 ${incomplete} 名候选人的画像`, detail: '资料不完整会降低筛选和匹配可靠性', action: '进入人才库', path: '/hr-candidates' }
  ]
})

const gapOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } }, legend: { top: 4, right: 10, textStyle: { color: '#9ab8cc', fontSize: 11 }, data: ['岗位需求', '人才供给'] },
  grid: { left: 92, right: 28, top: 38, bottom: 20 }, xAxis: { type: 'value', minInterval: 1, splitLine: { lineStyle: { color: 'rgba(82,143,183,.12)' } }, axisLabel: { color: '#7595ad', fontSize: 10 } },
  yAxis: { type: 'category', inverse: true, data: skillGap.value.slice(0, 8).map((item) => item.name), axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#c2dceb', fontSize: 11, width: 78, overflow: 'truncate' } },
  series: [
    { name: '岗位需求', type: 'bar', barWidth: 9, data: skillGap.value.slice(0, 8).map((item) => item.demand), itemStyle: { color: '#3d86ff', borderRadius: 5 }, animationDuration: 650 },
    { name: '人才供给', type: 'bar', barWidth: 9, data: skillGap.value.slice(0, 8).map((item) => item.supply), itemStyle: { color: '#38bdf8', borderRadius: 5 }, animationDuration: 760 }
  ]
}))
const trendOption = computed(() => ({
  tooltip: { trigger: 'axis', valueFormatter: (value: number) => `${value} 亿元` }, grid: { left: 48, right: 22, top: 18, bottom: 28 },
  xAxis: { type: 'category', boundaryGap: false, data: (model.value.market?.software_revenue_trend || []).map((item: any) => item.period), axisLine: { lineStyle: { color: 'rgba(93,153,193,.22)' } }, axisLabel: { color: '#7898b0', fontSize: 10 } },
  yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(93,153,193,.12)' } }, axisLabel: { color: '#7898b0', fontSize: 10 } },
  series: [{ type: 'line', smooth: .35, symbolSize: 6, data: (model.value.market?.software_revenue_trend || []).map((item: any) => item.value), lineStyle: { color: '#38bdf8', width: 2 }, itemStyle: { color: '#38bdf8' }, areaStyle: { color: 'rgba(54,198,232,.08)' }, animationDuration: 800 }]
}))

async function refresh(force = false) {
  if (!force) { const cached = readDashboardSnapshot<HrModel>(cacheKey.value); if (cached) { model.value = cached.data; updatedAt.value = cached.updatedAt; return } }
  loading.value = !force; refreshing.value = force
  try {
    const results = await Promise.allSettled([api.overview(), api.hrCandidates(), api.jobs(), api.datasets(), api.reviewTasks(), api.emergingJobs(), api.skillGraph(), api.marketSnapshot()])
    const next: HrModel = { summary: settledValue(results[0], {}), candidates: settledValue(results[1], []), jobs: settledValue(results[2], []), datasets: settledValue(results[3], []), reviews: settledValue(results[4], []), emerging: settledValue(results[5], []), graph: settledValue(results[6], {}), market: settledValue(results[7], {}) }
    const snapshot = writeDashboardSnapshot(cacheKey.value, next); model.value = snapshot.data; updatedAt.value = snapshot.updatedAt
    if (force) ElMessage.success('企业驾驶舱已更新')
  } catch (error: any) { ElMessage.error(error?.response?.data?.detail || '企业驾驶舱加载失败') }
  finally { loading.value = false; refreshing.value = false }
}

onMounted(() => refresh(false))
</script>

<style scoped>
.hr-dashboard { max-width: 1680px; margin: 0 auto; }.job-filter { width: 220px; }.job-filter :deep(.el-select__wrapper) { min-height: 38px; border: 1px solid rgba(63,191,246,.28); border-radius: 8px; background: rgba(4,23,52,.88); box-shadow: none; }
/* ===== 底部数据状态栏（更新操作集中在页面底部） ===== */
.overview-footer { display: flex; align-items: center; justify-content: space-between; gap: 14px; margin-top: 16px; border: 1px solid rgba(71,191,255,.16); border-radius: 10px; padding: 13px 18px; background: rgba(5,23,52,.6); }
.overview-footer__status { display: flex; align-items: center; gap: 10px; color: #7c9db8; font-size: 12px; }
.overview-footer__status .status-dot { width: 7px; height: 7px; border-radius: 50%; background: #57dfc5; box-shadow: 0 0 8px rgba(87,223,197,.7); }
.overview-footer__status .status-dot.busy { background: #ffb65c; box-shadow: 0 0 8px rgba(255,182,92,.7); animation: footer-busy 1s ease-in-out infinite; }
@keyframes footer-busy { 50% { opacity: .35; } }
.footer-divider { width: 1px; height: 12px; background: rgba(99,150,187,.3); }
@media (max-width: 620px) { .overview-footer { flex-direction: column; align-items: flex-start; } }
.decision-brief { display: grid; grid-template-columns: minmax(390px,1.35fr) repeat(4,minmax(180px,.7fr)); gap: 12px; margin-bottom: 14px; }.decision-brief article,.decision-brief > button { min-height: 124px; border: 1px solid rgba(71,191,255,.22); border-radius: 10px; background: rgba(5,23,52,.84); box-shadow: 0 14px 34px rgba(0,3,18,.2); }.role-focus { padding: 17px 20px; }.role-focus > span { color: #65daf4; font-size: 11px; font-weight: 800; }.role-focus h2 { margin: 6px 0 0; color: #f0fbff; font-size: 20px; }.role-focus p { margin: 7px 0 0; color: #89a9bf; font-size: 12px; line-height: 1.55; }.role-focus button { display: inline-flex; align-items: center; gap: 6px; margin-top: 10px; border: 0; padding: 0; color: #81e3f8; background: transparent; font: inherit; font-size: 11px; cursor: pointer; }
.decision-brief > button { display: grid; grid-template-columns: 1fr auto; grid-template-rows: auto auto auto; gap: 5px; padding: 18px; color: inherit; font: inherit; text-align: left; cursor: pointer; }.decision-brief > button:hover { border-color: rgba(76,211,255,.5); background: rgba(8,39,78,.9); }.decision-brief > button span { color: #88a9c4; font-size: 12px; }.decision-brief > button strong { grid-column: 1; color: #f3fcff; font-size: 24px; }.decision-brief > button small { grid-column: 1; color: #6f91ad; font-size: 10px; }.decision-brief > button .el-icon { grid-row: 1 / 4; grid-column: 2; align-self: start; color: #4ed8ff; font-size: 19px; }
.hr-workspace { display: grid; grid-template-columns: minmax(640px,1.6fr) minmax(380px,.75fr); gap: 14px; }.gap-chart { height: 335px; padding: 0 8px; }.gap-summary { display: grid; grid-template-columns: repeat(3,1fr); gap: 8px; padding: 0 16px 16px; }.gap-summary button { display: flex; align-items: center; justify-content: space-between; gap: 12px; min-height: 58px; border: 1px solid rgba(76,146,194,.16); border-radius: 8px; padding: 10px 12px; color: inherit; background: rgba(6,31,64,.54); font: inherit; text-align: left; cursor: pointer; }.gap-summary button:hover { border-color: rgba(74,207,240,.4); }.gap-summary b,.gap-summary small { display: block; }.gap-summary b { color: #e9f9ff; font-size: 12px; }.gap-summary small { margin-top: 4px; color: #7898b0; font-size: 10px; }.gap-summary strong { color: #72e0c5; font-size: 11px; white-space: nowrap; }.gap-summary strong.short { color: #ffb772; }
.text-button { border: 0; padding: 5px; color: #7dd3fc; background: transparent; font: inherit; font-size: 11px; cursor: pointer; }.talent-list { display: grid; padding: 0 15px 15px; }.talent-list button { display: grid; grid-template-columns: 24px 40px minmax(0,1fr) 56px; align-items: center; gap: 9px; min-height: 66px; border: 0; border-bottom: 1px solid rgba(73,142,191,.14); color: inherit; background: transparent; font: inherit; text-align: left; cursor: pointer; }.talent-list button:hover { background: rgba(15,68,112,.22); }.talent-rank { color: #547a95; font-size: 12px; font-weight: 800; }.talent-name b,.talent-name small,.fit-score b,.fit-score small { display: block; }.talent-name b { color: #eaf9ff; font-size: 12px; }.talent-name small { margin-top: 4px; color: #7595ad; font-size: 10px; }.fit-score { text-align: right; }.fit-score b { color: #67dfc1; font-size: 16px; }.fit-score small { margin-top: 3px; color: #6f91ad; font-size: 9px; }
.hr-secondary { display: grid; grid-template-columns: minmax(390px,.9fr) minmax(500px,1.2fr) minmax(300px,.65fr); gap: 14px; margin-top: 14px; }.action-list { display: grid; gap: 7px; padding: 0 15px 15px; }.action-list button { display: grid; grid-template-columns: 28px minmax(0,1fr) auto 16px; align-items: center; gap: 10px; min-height: 58px; border: 1px solid rgba(75,145,193,.16); border-radius: 8px; padding: 9px 10px; color: inherit; background: rgba(6,31,64,.5); font: inherit; text-align: left; cursor: pointer; }.action-list button:hover { border-color: rgba(74,207,240,.4); }.action-list > button > span { color: #537894; font-size: 11px; font-weight: 800; }.action-list b,.action-list small { display: block; }.action-list b { color: #e8f8ff; font-size: 11px; }.action-list small { margin-top: 4px; color: #7797ae; font-size: 9px; }.action-list em { color: #82dff3; font-size: 9px; font-style: normal; white-space: nowrap; }.action-list .el-icon { color: #7092aa; }.trend-chart { height: 250px; padding: 0 8px 8px; }.source-badge { border: 1px solid rgba(57,186,220,.24); border-radius: 5px; padding: 5px 7px; color: #80d8eb; font-size: 10px; }.emerging-list { display: grid; padding: 0 14px 14px; }.emerging-list button { display: grid; grid-template-columns: 1fr 16px; align-items: center; gap: 8px; min-height: 54px; border: 0; border-bottom: 1px solid rgba(73,142,191,.13); color: inherit; background: transparent; font: inherit; text-align: left; cursor: pointer; }.emerging-list button:hover b { color: #71ddf4; }.emerging-list b,.emerging-list small { display: block; }.emerging-list b { color: #e7f7ff; font-size: 11px; }.emerging-list small { margin-top: 4px; color: #7394ad; font-size: 9px; }.emerging-list .el-icon { color: #7192aa; }
@media (max-width: 1380px) { .decision-brief { grid-template-columns: repeat(4,1fr); }.role-focus { grid-column: 1 / -1; }.hr-secondary { grid-template-columns: repeat(2,1fr); }.emerging-panel { grid-column: 1 / -1; } }
@media (max-width: 980px) { .cockpit-heading__actions { flex-wrap: wrap; justify-content: flex-start; }.hr-workspace,.hr-secondary { grid-template-columns: 1fr; }.emerging-panel { grid-column: auto; }.decision-brief { grid-template-columns: repeat(2,1fr); }.gap-summary { grid-template-columns: 1fr; } }
@media (max-width: 620px) { .decision-brief { grid-template-columns: 1fr; }.role-focus { grid-column: auto; }.job-filter { width: 100%; }.gap-chart { height: 390px; }.action-list button { grid-template-columns: 26px minmax(0,1fr) 16px; }.action-list em { display: none; } }
</style>
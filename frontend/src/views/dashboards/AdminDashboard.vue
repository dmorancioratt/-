<template>
  <div class="cockpit admin-dashboard">
    <div v-if="loading" class="cockpit-loading">正在读取治理数据...</div>

    <header class="cockpit-heading">
      <div class="cockpit-heading__copy">
        <span class="cockpit-eyebrow">平台治理指挥中心</span>
        <h1>先处理风险，再发布可信数据</h1>
        <p>集中查看数据来源、解析质量、人工复核与模型服务状态，每个异常都能进入对应处理页面。</p>
      </div>
      <div class="cockpit-heading__actions">
        <span class="service-state" :class="model.ai.enabled ? 'online' : 'offline'"><i></i>{{ model.ai.enabled ? `${model.ai.provider} 服务可用` : '智能服务待配置' }}</span>
        <span class="cockpit-updated">更新于 {{ updatedLabel }}</span>
        <button class="cockpit-button" type="button" :disabled="refreshing" @click="refresh(true)"><el-icon><Refresh /></el-icon>{{ refreshing ? '更新中' : '更新数据' }}</button>
      </div>
    </header>

    <section class="governance-brief">
      <article class="governance-score">
        <div class="score-ring" :style="{ '--score': `${governanceScore * 3.6}deg` }">
          <strong>{{ governanceScore }}</strong><small>/ 100</small>
        </div>
        <div><span>治理健康度</span><b>{{ governanceVerdict }}</b><p>综合数据质量、解析评测、测试覆盖和待复核风险。</p></div>
      </article>
      <button v-for="item in summaryItems" :key="item.label" type="button" @click="router.push(item.path)">
        <span>{{ item.label }}</span><strong>{{ item.value }}</strong><small>{{ item.note }}</small><el-icon><component :is="item.icon" /></el-icon>
      </button>
    </section>

    <section class="admin-workspace">
      <div class="admin-primary">
        <article class="cockpit-panel priority-panel">
          <div class="cockpit-panel__head">
            <div><div class="cockpit-panel__title">今日治理重点</div><p>只展示会阻塞可信发布的事项</p></div>
            <span class="cockpit-tag" :class="priorityItems.length ? 'danger' : 'success'"><i></i>{{ priorityItems.length ? `${priorityItems.length} 项待处理` : '当前无阻塞项' }}</span>
          </div>
          <div v-if="priorityItems.length" class="priority-queue">
            <button v-for="(item, index) in priorityItems" :key="item.title" type="button" @click="router.push(item.path)">
              <span class="priority-index">{{ String(index + 1).padStart(2, '0') }}</span>
              <span><b>{{ item.title }}</b><small>{{ item.detail }}</small></span>
              <em :class="item.level">{{ item.action }}</em><el-icon><ArrowRight /></el-icon>
            </button>
          </div>
          <div v-else class="all-clear"><el-icon><CircleCheck /></el-icon><span><b>可信发布链路正常</b><small>数据源、模型服务与人工审核队列均无阻塞。</small></span></div>
        </article>

        <article class="cockpit-panel source-matrix">
          <div class="cockpit-panel__head"><div><div class="cockpit-panel__title">数据源质量与覆盖</div><p>质量低于 85 分的来源进入复核范围</p></div><button class="text-button" type="button" @click="router.push('/datasets')">管理全部来源</button></div>
          <div class="source-table">
            <button v-for="source in model.datasets.slice(0, 6)" :key="source.id" type="button" @click="router.push('/datasets')">
              <span class="source-name"><b>{{ source.source_name }}</b><small>{{ source.publisher || source.domain }}</small></span>
              <span class="source-volume"><b>{{ compact(source.indexed_count || source.data_count || 0) }}</b><small>本地索引</small></span>
              <span class="quality-bar"><i><em :style="{ width: `${Math.min(100, source.quality_score || 0)}%` }"></em></i><small>{{ Math.round(source.quality_score || 0) }} 分</small></span>
              <span class="source-status" :class="source.quality_score >= 85 ? 'good' : 'review'">{{ source.quality_score >= 85 ? '可用' : '复核' }}</span>
            </button>
            <div v-if="!model.datasets.length" class="cockpit-empty">尚未接入数据源</div>
          </div>
        </article>
      </div>

      <aside class="admin-side">
        <article class="cockpit-panel metrics-panel">
          <div class="cockpit-panel__head"><div><div class="cockpit-panel__title">评测基线</div><p>小规模回归集与代码覆盖</p></div></div>
          <div class="metrics-chart"><EChart :option="qualityOption" /></div>
          <button class="panel-action" type="button" @click="router.push('/evaluation')">查看样本量与错误案例<el-icon><ArrowRight /></el-icon></button>
        </article>

        <article class="cockpit-panel model-panel">
          <div class="cockpit-panel__head"><div><div class="cockpit-panel__title">模型与规则</div><p>实际服务配置，不使用演示状态</p></div></div>
          <div class="model-facts">
            <div><span>提供方</span><b>{{ model.ai.provider || '未配置' }}</b></div>
            <div><span>模型</span><b>{{ model.ai.model || '-' }}</b></div>
            <div><span>API 密钥</span><b :class="model.ai.api_key_configured ? 'ok' : 'warn'">{{ model.ai.api_key_configured ? '已配置' : '未配置' }}</b></div>
            <div><span>结构化输出</span><b :class="model.ai.json_output ? 'ok' : 'warn'">{{ model.ai.json_output ? '可用' : '不可用' }}</b></div>
          </div>
          <button class="panel-action" type="button" @click="router.push('/settings')">配置模型与校验规则<el-icon><ArrowRight /></el-icon></button>
        </article>
      </aside>
    </section>

    <section class="cockpit-panel pipeline-panel">
      <div class="cockpit-panel__head"><div><div class="cockpit-panel__title">可信数据发布链路</div><p>流动状态只表示真实处理顺序，不代表后台正在虚构运行</p></div><span class="pipeline-state">最近同步 {{ formatDate(model.market?.last_synced_at, true) }}</span></div>
      <div class="pipeline-steps">
        <template v-for="(step, index) in pipelineSteps" :key="step.label">
          <button type="button" @click="router.push(step.path)"><span class="step-icon"><el-icon><component :is="step.icon" /></el-icon></span><b>{{ step.label }}</b><strong>{{ step.value }}</strong><small>{{ step.note }}</small></button>
          <i v-if="index < pipelineSteps.length - 1" class="pipeline-link"><em></em></i>
        </template>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ArrowRight, CircleCheck, Connection, DataAnalysis, DocumentChecked, Files, List, Refresh, Setting, Tickets, UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import EChart from '@/components/EChart.vue'
import { api } from '@/api/http'
import { useAuthStore } from '@/stores/auth'
import { formatSnapshotTime, readDashboardSnapshot, settledValue, writeDashboardSnapshot } from '@/utils/dashboardCache'

type AdminModel = { summary: any; datasets: any[]; reviews: any[]; evaluation: any; ai: any; market: any }
const emptyModel: AdminModel = { summary: {}, datasets: [], reviews: [], evaluation: {}, ai: {}, market: {} }
const router = useRouter()
const auth = useAuthStore()
const model = ref<AdminModel>({ ...emptyModel })
const loading = ref(false)
const refreshing = ref(false)
const updatedAt = ref('')
const cacheKey = computed(() => `sr-dashboard:admin:${auth.user?.id || auth.user?.username || 'default'}:v2`)
const updatedLabel = computed(() => formatSnapshotTime(updatedAt.value))
const pendingReviews = computed(() => model.value.reviews.filter((item) => item.status === 'pending'))
const averageQuality = computed(() => model.value.datasets.length ? Math.round(model.value.datasets.reduce((sum, item) => sum + Number(item.quality_score || 0), 0) / model.value.datasets.length) : 0)
const lowQualitySources = computed(() => model.value.datasets.filter((source) => Number(source.quality_score || 0) < 85))
const governanceScore = computed(() => {
  const evaluation = model.value.evaluation
  const values = [averageQuality.value, evaluation.jd_parse_accuracy || 0, evaluation.resume_parse_accuracy || 0, evaluation.unit_test_coverage || 0]
  const base = values.reduce((sum, value) => sum + Number(value), 0) / values.length
  return Math.max(0, Math.min(100, Math.round(base - Math.min(18, pendingReviews.value.length * 3))))
})
const governanceVerdict = computed(() => governanceScore.value >= 85 ? '可以进入发布前检查' : governanceScore.value >= 70 ? '仍有质量项需要处理' : '优先补齐治理基础')

const summaryItems = computed(() => [
  { label: '有效数据源', value: `${model.value.datasets.length} 个`, note: `${lowQualitySources.value.length} 个需要复核`, path: '/datasets', icon: Files },
  { label: '本地权威索引', value: compact(model.value.market?.coverage?.indexed_count || 0), note: `${model.value.market?.coverage?.publisher_count || 0} 个发布机构`, path: '/datasets', icon: Connection },
  { label: '回归样本', value: `${model.value.evaluation.benchmark_sample_count || 0} 条`, note: '解析与匹配金标', path: '/evaluation', icon: DataAnalysis },
  { label: '人工复核', value: `${pendingReviews.value.length} 项`, note: pendingReviews.value.length ? '阻塞可信发布' : '队列已清空', path: '/review-tasks', icon: Tickets }
])

const priorityItems = computed(() => {
  const items: { title: string; detail: string; action: string; level: string; path: string }[] = []
  pendingReviews.value.slice(0, 3).forEach((task) => items.push({ title: task.title, detail: `${task.task_type} · 置信度 ${Math.round((task.confidence || 0) * 100)}%`, action: '立即复核', level: 'high', path: '/review-tasks' }))
  if (!model.value.ai.enabled) items.push({ title: '智能服务尚未启用', detail: '解析、匹配解释和学习路径将无法调用真实模型', action: '去配置', level: 'medium', path: '/settings' })
  lowQualitySources.value.slice(0, 2).forEach((source) => items.push({ title: `${source.source_name} 质量不足`, detail: `当前 ${Math.round(source.quality_score || 0)} 分，需要核对来源和索引结果`, action: '检查来源', level: 'medium', path: '/datasets' }))
  return items.slice(0, 5)
})

const qualityOption = computed(() => ({
  grid: { left: 82, right: 24, top: 8, bottom: 14 }, xAxis: { type: 'value', max: 100, show: false },
  yAxis: { type: 'category', inverse: true, data: ['JD 抽取', '简历抽取', '岗位匹配', '代码覆盖'], axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#9bb9ce', fontSize: 11 } },
  series: [{ type: 'bar', barWidth: 9, showBackground: true, backgroundStyle: { color: 'rgba(83,137,174,.13)', borderRadius: 5 }, data: [model.value.evaluation.jd_parse_accuracy || 0, model.value.evaluation.resume_parse_accuracy || 0, model.value.evaluation.match_accuracy || 0, model.value.evaluation.unit_test_coverage || 0], itemStyle: { color: '#36c6e8', borderRadius: 5 }, label: { show: true, position: 'right', color: '#d8f6ff', fontSize: 11, formatter: '{c}%' }, animationDuration: 650 }]
}))

const pipelineSteps = computed(() => [
  { label: '来源接入', value: `${model.value.datasets.length} 源`, note: '版本与许可', path: '/datasets', icon: UploadFilled },
  { label: '结构解析', value: `${model.value.summary.parsed_jd_count || 0} JD`, note: '字段与证据', path: '/jd-parser', icon: DataAnalysis },
  { label: '规则校验', value: `${model.value.evaluation.jd_parse_accuracy || 0}%`, note: '抽取回归', path: '/evaluation', icon: DocumentChecked },
  { label: '人工复核', value: `${pendingReviews.value.length} 待办`, note: '低置信度回写', path: '/review-tasks', icon: List },
  { label: '图谱发布', value: `${model.value.summary.graph_relation_count || 0} 关系`, note: '岗位能力应用', path: '/skill-graph', icon: Connection },
  { label: '策略配置', value: model.value.ai.enabled ? '已启用' : '待配置', note: '模型与阈值', path: '/settings', icon: Setting }
])

function formatDate(value: string, withTime = false) { return value ? new Intl.DateTimeFormat('zh-CN', withTime ? { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' } : { month: '2-digit', day: '2-digit' }).format(new Date(value)) : '未知' }
function compact(value: number) { return new Intl.NumberFormat('zh-CN', { notation: value >= 10000 ? 'compact' : 'standard', maximumFractionDigits: 1 }).format(value) }

async function refresh(force = false) {
  if (!force) {
    const cached = readDashboardSnapshot<AdminModel>(cacheKey.value)
    if (cached) { model.value = cached.data; updatedAt.value = cached.updatedAt; return }
  }
  loading.value = !force
  refreshing.value = force
  try {
    const results = await Promise.allSettled([api.overview(), api.datasets(), api.reviewTasks(), api.evaluation(), api.aiStatus(), api.marketSnapshot()])
    const next: AdminModel = { summary: settledValue(results[0], {}), datasets: settledValue(results[1], []), reviews: settledValue(results[2], []), evaluation: settledValue(results[3], {}), ai: settledValue(results[4], {}), market: settledValue(results[5], {}) }
    const snapshot = writeDashboardSnapshot(cacheKey.value, next)
    model.value = snapshot.data; updatedAt.value = snapshot.updatedAt
    if (force) ElMessage.success('管理驾驶舱已更新')
  } catch (error: any) { ElMessage.error(error?.response?.data?.detail || '管理驾驶舱加载失败') }
  finally { loading.value = false; refreshing.value = false }
}

onMounted(() => refresh(false))
</script>

<style scoped>
.admin-dashboard { max-width: 1680px; margin: 0 auto; }
.service-state { display: inline-flex; align-items: center; gap: 7px; border: 1px solid rgba(80,158,205,.25); border-radius: 6px; padding: 7px 10px; color: #9bb9ce; font-size: 12px; }.service-state i { width: 7px; height: 7px; border-radius: 50%; background: #ffb85c; }.service-state.online { color: #7de6c9; }.service-state.online i { background: #24d7b1; box-shadow: 0 0 8px rgba(36,215,177,.65); animation: status-breathe 2.4s ease-in-out infinite; }
.governance-brief { display: grid; grid-template-columns: minmax(340px,1.25fr) repeat(4,minmax(180px,.7fr)); gap: 12px; margin-bottom: 14px; }.governance-brief article,.governance-brief > button { min-height: 116px; border: 1px solid rgba(71,191,255,.22); border-radius: 10px; background: rgba(5,23,52,.82); box-shadow: 0 14px 34px rgba(0,3,18,.2); }.governance-score { display: flex; align-items: center; gap: 18px; padding: 14px 18px; }.score-ring { display: grid; width: 84px; height: 84px; flex: 0 0 auto; place-content: center; border-radius: 50%; background: radial-gradient(circle at center,#071b39 55%,transparent 57%),conic-gradient(#24d7b1 var(--score),rgba(67,126,166,.18) 0); }.score-ring strong { color: #f5fdff; font-size: 27px; line-height: 1; }.score-ring small { margin-top: 3px; color: #7f9fb7; font-size: 9px; text-align: center; }.governance-score > div:last-child span { color: #78dff7; font-size: 12px; font-weight: 800; }.governance-score b { display: block; margin-top: 6px; color: #f1fbff; font-size: 16px; }.governance-score p { margin: 6px 0 0; color: #809fb7; font-size: 11px; line-height: 1.5; }
.governance-brief > button { position: relative; display: grid; grid-template-columns: 1fr auto; grid-template-rows: auto auto auto; gap: 4px 10px; padding: 17px; color: inherit; font: inherit; text-align: left; cursor: pointer; }.governance-brief > button:hover { border-color: rgba(76,211,255,.5); background: rgba(8,39,78,.9); }.governance-brief > button span { color: #88a9c4; font-size: 12px; }.governance-brief > button strong { grid-column: 1; color: #f2fcff; font-size: 24px; }.governance-brief > button small { grid-column: 1; color: #6f91ad; font-size: 11px; }.governance-brief > button .el-icon { grid-row: 1 / 4; grid-column: 2; align-self: start; color: #42d2ef; font-size: 19px; }
.admin-workspace { display: grid; grid-template-columns: minmax(650px,1.55fr) minmax(360px,.75fr); gap: 14px; }.admin-primary,.admin-side { display: grid; gap: 14px; }.admin-primary { grid-template-rows: auto 1fr; }.admin-side { grid-template-rows: 1fr auto; }
.priority-queue { display: grid; gap: 8px; padding: 4px 16px 16px; }.priority-queue button { display: grid; grid-template-columns: 38px minmax(0,1fr) auto 18px; align-items: center; gap: 12px; min-height: 60px; border: 1px solid rgba(76,145,194,.18); border-radius: 8px; padding: 9px 12px; color: inherit; background: rgba(6,31,64,.55); font: inherit; text-align: left; cursor: pointer; }.priority-queue button:hover { border-color: rgba(255,137,154,.42); background: rgba(18,49,83,.72); }.priority-index { color: #4f7895; font-size: 12px; font-weight: 800; }.priority-queue b { display: block; color: #edfaff; font-size: 13px; }.priority-queue small { display: block; margin-top: 5px; color: #829fb6; font-size: 11px; }.priority-queue em { border-radius: 5px; padding: 5px 7px; color: #ffd094; background: rgba(121,75,18,.25); font-size: 10px; font-style: normal; }.priority-queue em.high { color: #ff9db0; background: rgba(118,26,45,.25); }.priority-queue .el-icon { color: #7194ad; }.all-clear { display: flex; align-items: center; gap: 14px; min-height: 150px; padding: 20px 24px; color: #24d7b1; }.all-clear > .el-icon { font-size: 38px; }.all-clear b,.all-clear small { display: block; }.all-clear b { color: #effcff; font-size: 16px; }.all-clear small { margin-top: 6px; color: #829fb6; font-size: 12px; }
.text-button { border: 0; padding: 5px; color: #78dff7; background: transparent; font: inherit; font-size: 11px; cursor: pointer; }.source-table { display: grid; padding: 0 16px 16px; }.source-table > button { display: grid; grid-template-columns: minmax(190px,1fr) 110px minmax(180px,.8fr) 54px; align-items: center; gap: 14px; min-height: 62px; border: 0; border-bottom: 1px solid rgba(73,142,191,.14); color: inherit; background: transparent; font: inherit; text-align: left; cursor: pointer; }.source-table > button:hover { background: rgba(15,68,112,.22); }.source-name b,.source-volume b { display: block; color: #e5f8ff; font-size: 12px; }.source-name small,.source-volume small { display: block; margin-top: 4px; color: #7394ad; font-size: 10px; }.quality-bar { display: grid; grid-template-columns: 1fr 42px; align-items: center; gap: 8px; }.quality-bar i { display: block; height: 6px; overflow: hidden; border-radius: 4px; background: rgba(82,137,176,.16); }.quality-bar em { display: block; height: 100%; border-radius: inherit; background: #36c6e8; transform-origin: left; animation: bar-enter .65s ease-out both; }.quality-bar small { color: #91b2c8; font-size: 10px; }.source-status { border-radius: 5px; padding: 5px 6px; color: #ffd094; background: rgba(121,75,18,.25); font-size: 10px; text-align: center; }.source-status.good { color: #71e6c8; background: rgba(14,104,86,.24); }
.metrics-chart { height: 220px; padding: 0 12px; }.panel-action { display: flex; align-items: center; justify-content: space-between; width: calc(100% - 32px); margin: 0 16px 15px; border: 0; border-top: 1px solid rgba(75,153,204,.16); padding: 12px 0 0; color: #8be6fb; background: transparent; font: inherit; font-size: 11px; cursor: pointer; }.model-facts { display: grid; gap: 10px; padding: 4px 16px 12px; }.model-facts div { display: flex; justify-content: space-between; gap: 16px; border-bottom: 1px solid rgba(74,143,191,.12); padding-bottom: 9px; }.model-facts span { color: #7899b1; font-size: 11px; }.model-facts b { color: #e5f7ff; font-size: 11px; }.model-facts b.ok { color: #71e6c8; }.model-facts b.warn { color: #ffd094; }
.pipeline-panel { margin-top: 14px; }.pipeline-state { color: #7899b1; font-size: 11px; }.pipeline-steps { display: grid; grid-template-columns: repeat(5,minmax(120px,1fr) 36px) minmax(120px,1fr); align-items: center; padding: 8px 18px 18px; }.pipeline-steps button { display: grid; grid-template-columns: 34px 1fr; grid-template-rows: auto auto auto; column-gap: 10px; min-height: 78px; border: 1px solid rgba(73,156,207,.18); border-radius: 8px; padding: 11px; color: inherit; background: rgba(6,31,64,.55); font: inherit; text-align: left; cursor: pointer; }.pipeline-steps button:hover { border-color: rgba(73,208,243,.44); }.step-icon { grid-row: 1 / 4; display: grid; place-items: center; width: 32px; height: 32px; border-radius: 7px; color: #42d2ef; background: rgba(26,116,177,.2); }.pipeline-steps b { color: #dff5ff; font-size: 11px; }.pipeline-steps strong { margin-top: 3px; color: #70dff8; font-size: 13px; }.pipeline-steps small { color: #6f91ad; font-size: 9px; }.pipeline-link { position: relative; height: 1px; overflow: hidden; background: rgba(64,178,223,.22); }.pipeline-link em { position: absolute; width: 12px; height: 100%; background: #55d9f3; box-shadow: 0 0 8px #55d9f3; animation: pipeline-flow 2.8s ease-in-out infinite; }
@keyframes pipeline-flow { from { transform: translateX(-14px); } to { transform: translateX(40px); } } @keyframes status-breathe { 50% { opacity: .45; } } @keyframes bar-enter { from { transform: scaleX(0); } }
@media (max-width: 1380px) { .governance-brief { grid-template-columns: repeat(4,1fr); }.governance-score { grid-column: 1 / -1; }.pipeline-steps { grid-template-columns: repeat(3,1fr); gap: 10px; }.pipeline-link { display: none; } }
@media (max-width: 980px) { .admin-workspace { grid-template-columns: 1fr; }.governance-brief { grid-template-columns: repeat(2,1fr); }.source-table > button { grid-template-columns: minmax(160px,1fr) 90px minmax(150px,.8fr) 50px; overflow-x: auto; } }
@media (max-width: 620px) { .governance-brief { grid-template-columns: 1fr; }.governance-score { grid-column: auto; }.priority-queue button { grid-template-columns: 32px minmax(0,1fr) 16px; }.priority-queue em { display: none; }.source-table { overflow-x: auto; }.source-table > button { min-width: 660px; }.pipeline-steps { grid-template-columns: 1fr; } }
</style>

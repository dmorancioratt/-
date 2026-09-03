<template>
  <div class="hub-screen">
    <header class="hub-header">
      <div class="brand">
        <span class="brand-mark">SR</span>
        <div><b>数融智联</b><small>可信数据治理控制台</small></div>
      </div>
      <div class="title"><small>TRUST OPERATIONS CENTER</small><h1>数据治理与防幻觉中枢</h1></div>
      <div class="header-actions">
        <span class="clock">{{ clock }}</span>
        <button type="button" @click="router.push('/overview')"><el-icon><HomeFilled /></el-icon>返回概览</button>
        <button class="sync-button" type="button" :disabled="loading" @click="loadData">
          <el-icon :class="{ spinning: loading }"><Refresh /></el-icon>{{ loading ? '更新中' : '更新数据' }}
        </button>
      </div>
    </header>

    <main class="hub-body">
      <section class="command-bar" aria-label="管理员快捷操作">
        <div class="command-intro"><span>治理操作</span><h2>从异常直接进入处理</h2><p>每个入口都连接真实管理页面。</p></div>
        <button v-for="action in quickActions" :key="action.title" type="button" @click="router.push(action.path)">
          <span class="command-icon"><el-icon><component :is="action.icon" /></el-icon></span>
          <span class="command-copy"><b>{{ action.title }}</b><small>{{ action.desc }}</small></span>
          <em :class="action.tone">{{ action.status }}</em>
          <el-icon class="command-arrow"><ArrowRight /></el-icon>
        </button>
      </section>

      <section class="kpi-row" aria-label="平台核心指标">
        <article v-for="item in kpis" :key="item.label" class="kpi-card">
          <el-icon><component :is="item.icon" /></el-icon>
          <div><span>{{ item.label }}</span><strong>{{ item.value }}</strong><small>{{ item.note }}</small></div>
        </article>
      </section>

      <div v-if="error" class="load-error">{{ error }}</div>

      <section class="dashboard-grid">
        <article class="panel sources-panel">
          <header class="panel-header">
            <div><small>DATABASE / SYNC STATUS</small><h2>数据源状态</h2></div>
            <button type="button" @click="router.push('/datasets')">管理全部<el-icon><ArrowRight /></el-icon></button>
          </header>
          <div v-if="sources.length" class="source-list">
            <button v-for="source in sources.slice(0, 7)" :key="source.id || source.name" type="button" @click="router.push('/datasets')">
              <span class="source-state" :class="sourceTone(source)"></span>
              <span class="source-copy"><b>{{ source.name || source.source_name || '未命名数据源' }}</b><small>{{ source.publisher || source.provider || '发布机构未填写' }}</small></span>
              <em>{{ source.status || 'unknown' }}</em><strong>{{ qualityValue(source) }}</strong><el-icon><ArrowRight /></el-icon>
            </button>
          </div>
          <div v-else class="empty-state">数据库中暂无数据源记录</div>
          <button class="panel-action" type="button" @click="router.push('/datasets')">进入数据源治理中心<el-icon><ArrowRight /></el-icon></button>
        </article>

        <article class="panel governance-panel">
          <header class="panel-header">
            <div><small>GOVERNANCE HEALTH</small><h2>质量门禁与审核</h2></div>
            <button type="button" @click="router.push('/review-tasks')">处理待办<el-icon><ArrowRight /></el-icon></button>
          </header>
          <section class="governance-score">
            <div><strong>{{ healthScore == null ? '—' : healthScore }}</strong><span>综合健康度</span></div>
            <div><strong>{{ hallucination.sample_size || 0 }}</strong><span>防幻觉样本</span></div>
            <div><strong>{{ pendingReviews.length }}</strong><span>待审核任务</span></div>
          </section>
          <div v-if="governanceDimensions.length" class="dimension-list">
            <div v-for="item in governanceDimensions" :key="item.name || item.label">
              <span>{{ item.name || item.label }}</span><b>{{ dimensionScore(item) }}</b>
              <i><em :style="{ width: `${dimensionScoreNumber(item)}%` }"></em></i><small>{{ item.note || '按当前数据库实时计算' }}</small>
            </div>
          </div>
          <div v-else class="empty-state">暂无数据健康维度记录</div>
          <button class="panel-action" type="button" @click="router.push('/review-tasks')">查看并处理审核任务<el-icon><ArrowRight /></el-icon></button>
        </article>

        <article class="panel core-panel">
          <header class="panel-header"><div><small>LIVE DATABASE TOPOLOGY</small><h2>数据资产关系</h2></div></header>
          <div class="core-visual">
            <div class="core-ring ring-one"></div><div class="core-ring ring-two"></div>
            <div class="core-node"><small>当前数据库</small><strong>{{ compact(overview.graph_relation_count) }}</strong><span>图谱关系</span></div>
            <div v-for="node in topology" :key="node.label" class="satellite" :style="node.style"><b>{{ node.value }}</b><span>{{ node.label }}</span></div>
          </div>
          <div class="source-sync"><span><i :class="syncHealthy ? 'ok' : 'warn'"></i>{{ syncStatusText }}</span><small>{{ syncUpdatedAt }}</small></div>
        </article>

        <article class="panel quality-panel">
          <header class="panel-header">
            <div><small>BACKEND EVALUATION</small><h2>模型评测基线</h2></div>
            <button type="button" @click="router.push('/evaluation')">查看错误案例<el-icon><ArrowRight /></el-icon></button>
          </header>
          <div class="quality-list">
            <div v-for="item in qualityMetrics" :key="item.label">
              <span>{{ item.label }}</span><strong>{{ item.value == null ? '待测' : `${item.value}%` }}</strong>
              <i><em :style="{ width: `${Number(item.value || 0)}%` }"></em></i>
            </div>
          </div>
          <p class="evidence-note">评测样本 {{ overview.benchmark_sample_count || 0 }} 条，业务用例 {{ overview.test_case_count || 0 }} 条。</p>
          <button class="panel-action" type="button" @click="router.push('/evaluation')">运行与查看完整评测<el-icon><ArrowRight /></el-icon></button>
        </article>

        <article class="panel guard-panel">
          <header class="panel-header">
            <div><small>HALLUCINATION GUARD</small><h2>防幻觉防线</h2></div>
            <button type="button" @click="router.push('/rag-admin')">打开工作流<el-icon><ArrowRight /></el-icon></button>
          </header>
          <div class="guard-summary">
            <div><span>防护通过率</span><strong>{{ guardPassRate == null ? '待检测' : `${guardPassRate}%` }}</strong></div>
            <div><span>已拦截</span><strong :class="hallucination.flagged ? 'warning' : ''">{{ hallucination.flagged || 0 }}</strong></div>
            <div><span>置信度阈值</span><strong>{{ hallucination.min_confidence == null ? '—' : hallucination.min_confidence }}</strong></div>
          </div>
          <div v-if="guardRules.length" class="guard-rules">
            <div v-for="rule in guardRules" :key="rule.key">
              <span class="rule-icon"><el-icon><CircleCheck /></el-icon></span>
              <span><b>{{ rule.label }}</b><small>{{ rule.detail }}</small></span><em>{{ rule.hits || 0 }} 次命中</em>
            </div>
          </div>
          <div v-else class="empty-state compact">尚无防幻觉规则运行记录</div>
          <button class="panel-action" type="button" @click="router.push(hallucination.flagged ? '/review-tasks' : '/rag-admin')">
            {{ hallucination.flagged ? '处理被拦截内容' : '检查 RAG 防幻觉工作流' }}<el-icon><ArrowRight /></el-icon>
          </button>
        </article>

        <article class="panel service-panel">
          <header class="panel-header">
            <div><small>CONFIGURED SERVICES</small><h2>系统与服务状态</h2></div>
            <button type="button" @click="router.push('/settings')">系统配置<el-icon><ArrowRight /></el-icon></button>
          </header>
          <div class="service-grid">
            <div><span>AI 提供方</span><b>{{ aiStatus.provider || '未配置' }}</b></div>
            <div><span>AI 模型</span><b>{{ aiStatus.model || '未配置' }}</b></div>
            <div><span>AI 状态</span><b :class="aiStatus.configured ? 'healthy' : 'warning'">{{ aiStatus.configured ? '已配置' : '未配置' }}</b></div>
            <div><span>RAG 引擎</span><b :class="ragReady ? 'healthy' : 'warning'">{{ ragStatus.status || (ragReady ? 'ready' : '未就绪') }}</b></div>
            <div><span>CPU</span><b>{{ metricPercent(systemMetrics.cpu_percent) }}</b></div>
            <div><span>内存</span><b>{{ metricPercent(systemMetrics.memory_percent) }}</b></div>
            <div><span>存储</span><b>{{ metricPercent(systemMetrics.disk_percent) }}</b></div>
            <div><span>网络收发</span><b>{{ networkTraffic }}</b></div>
          </div>
          <p class="monitor-note">采样于后端主机，{{ systemMetrics.sampled_at ? formatDateTime(systemMetrics.sampled_at) : '等待采样' }}</p>
          <button class="panel-action" type="button" @click="router.push('/settings')">配置模型与治理规则<el-icon><ArrowRight /></el-icon></button>
        </article>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { ArrowRight, CircleCheck, Collection, Connection, DataAnalysis, Document, HomeFilled, List, MagicStick, Odometer, Refresh, Setting, Tickets } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/http'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const clock = ref('')
const overview = ref<any>({})
const sources = ref<any[]>([])
const syncStatus = ref<any>({})
const governance = ref<any>({})
const hallucination = ref<any>({})
const reviews = ref<any[]>([])
const aiStatus = ref<any>({})
const ragStatus = ref<any>({})
const systemMetrics = ref<any>({})
let timer: number | undefined

const compact = (value: unknown) => new Intl.NumberFormat('zh-CN', { notation: 'compact', maximumFractionDigits: 1 }).format(Number(value || 0))
const formatPercent = (value: unknown) => value == null ? null : Math.round(Number(value) * 10) / 10
const governanceDimensions = computed(() => governance.value.dimensions || [])
const healthScore = computed(() => governance.value.overall == null ? null : formatPercent(governance.value.overall))
const pendingReviews = computed(() => reviews.value.filter((item) => item.status === 'pending'))
const guardRules = computed(() => hallucination.value.rules || [])
const guardPassRate = computed(() => hallucination.value.sample_size ? formatPercent(hallucination.value.pass_rate) : null)
const ragReady = computed(() => Boolean(ragStatus.value.available || ragStatus.value.status === 'ready'))

const quickActions = computed(() => [
  { title: 'AI 防幻觉', desc: '检查检索、引用与校验链路', status: ragReady.value ? 'RAG 已就绪' : 'RAG 待配置', tone: ragReady.value ? 'ok' : 'warn', path: '/rag-admin', icon: MagicStick },
  { title: '人工审核', desc: '处理低置信度与证据缺失', status: `${pendingReviews.value.length} 项待办`, tone: pendingReviews.value.length ? 'warn' : 'ok', path: '/review-tasks', icon: List },
  { title: '测试评估', desc: '查看回归指标与错误案例', status: overview.value.business_case_pass_rate == null ? '等待评测' : `${overview.value.business_case_pass_rate}% 通过`, tone: 'normal', path: '/evaluation', icon: DataAnalysis },
  { title: '数据治理', desc: '核对来源、授权与质量评分', status: `${sources.value.length} 个来源`, tone: 'normal', path: '/datasets', icon: Collection },
  { title: '系统配置', desc: '维护模型服务与治理阈值', status: aiStatus.value.configured ? '服务已配置' : '服务待配置', tone: aiStatus.value.configured ? 'ok' : 'warn', path: '/settings', icon: Setting }
])

const kpis = computed(() => [
  { label: '权威数据源', value: compact(sources.value.length), note: '当前有效记录', icon: Collection },
  { label: '岗位实体', value: compact(overview.value.job_count), note: '数据库聚合', icon: Document },
  { label: '技能实体', value: compact(overview.value.skill_count), note: '数据库聚合', icon: Tickets },
  { label: '图谱关系', value: compact(overview.value.graph_relation_count), note: '带证据关系', icon: Connection },
  { label: '待审核', value: compact(pendingReviews.value.length), note: '阻塞发布任务', icon: Odometer },
  { label: '业务用例通过率', value: overview.value.business_case_pass_rate == null ? '待测' : `${overview.value.business_case_pass_rate}%`, note: `${overview.value.test_case_count || 0} 条用例`, icon: DataAnalysis }
])

const topology = computed(() => [
  { label: '岗位', value: compact(overview.value.job_count), style: { '--angle': '-90deg' } },
  { label: '技能', value: compact(overview.value.skill_count), style: { '--angle': '-18deg' } },
  { label: '证书', value: compact(overview.value.certificate_count), style: { '--angle': '54deg' } },
  { label: '简历', value: compact(overview.value.resume_count), style: { '--angle': '126deg' } },
  { label: '演化事件', value: compact(overview.value.evolution_event_count), style: { '--angle': '198deg' } }
])

const qualityMetrics = computed(() => [
  { label: 'JD 解析 F1', value: formatPercent(overview.value.jd_parse_accuracy) },
  { label: '简历解析 F1', value: formatPercent(overview.value.resume_parse_accuracy) },
  { label: '岗位匹配准确率', value: formatPercent(overview.value.match_accuracy) },
  { label: '单元测试覆盖率', value: formatPercent(overview.value.unit_test_coverage) }
])

const syncHealthy = computed(() => !['error', 'failed'].includes(String(syncStatus.value.status || '').toLowerCase()))
const syncStatusText = computed(() => syncStatus.value.status ? `同步状态：${syncStatus.value.status}` : '数据资产统计已更新')
const syncUpdatedAt = computed(() => {
  const value = syncStatus.value.last_synced_at || syncStatus.value.updated_at || overview.value.market_last_synced_at
  return value ? `更新于 ${formatDateTime(value)}` : '等待首次同步'
})
const networkTraffic = computed(() => `${formatBytes(systemMetrics.value.network_received_bytes)} / ${formatBytes(systemMetrics.value.network_sent_bytes)}`)

function metricPercent(value: unknown) { return value == null ? '未采样' : `${Math.round(Number(value) * 10) / 10}%` }
function formatBytes(value: unknown) { const bytes = Number(value || 0); return bytes >= 1073741824 ? `${(bytes / 1073741824).toFixed(1)} GB` : `${(bytes / 1048576).toFixed(1)} MB` }
function formatDateTime(value: string) { return new Date(value).toLocaleString('zh-CN', { hour12: false }) }
function qualityValue(source: any) { const value = source.quality_score ?? source.health_score; return value == null ? '未评估' : `${Math.round(Number(value) * 10) / 10}%` }
function sourceTone(source: any) { return ['active', 'ready', 'healthy', 'published'].includes(String(source.status).toLowerCase()) ? 'ok' : ['error', 'failed'].includes(String(source.status).toLowerCase()) ? 'bad' : 'warn' }
function dimensionScoreNumber(item: any) { return Math.max(0, Math.min(100, Number(item.score ?? item.value ?? 0))) }
function dimensionScore(item: any) { return `${Math.round(dimensionScoreNumber(item) * 10) / 10}%` }
function tick() { clock.value = new Intl.DateTimeFormat('zh-CN', { dateStyle: 'medium', timeStyle: 'medium', hour12: false }).format(new Date()) }

async function loadData() {
  loading.value = true
  error.value = ''
  const results = await Promise.allSettled([
    api.overview(), api.datasets(), api.dataSourceStatus(), api.governanceHealth(),
    api.hallucinationStats(), api.reviewTasks(), api.aiStatus(), api.ragStatus(), api.systemMetrics()
  ])
  const read = <T,>(index: number, fallback: T): T => results[index].status === 'fulfilled' ? (results[index] as PromiseFulfilledResult<T>).value : fallback
  overview.value = read(0, {})
  sources.value = read(1, [])
  syncStatus.value = read(2, {})
  governance.value = read(3, {})
  hallucination.value = read(4, {})
  reviews.value = read(5, [])
  aiStatus.value = read(6, {})
  ragStatus.value = read(7, {})
  systemMetrics.value = read(8, {})
  const failures = results.filter((item) => item.status === 'rejected').length
  if (failures) error.value = `${failures} 个后端数据接口暂不可用，其余区域仍展示已成功读取的数据。`
  loading.value = false
}

onMounted(() => { tick(); timer = window.setInterval(tick, 1000); loadData() })
onBeforeUnmount(() => { if (timer) window.clearInterval(timer) })
</script>

<style scoped>
.hub-screen { min-height: 100vh; overflow: auto; color: #e7f1f7; background: #020715; font-family: "Microsoft YaHei", sans-serif; }
.hub-screen button { font-family: inherit; }
.hub-header { position: sticky; z-index: 5; top: 0; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 20px; min-height: 68px; border-bottom: 1px solid rgba(82,221,255,.18); padding: 0 24px; background: rgba(2,7,21,.96); backdrop-filter: blur(18px); }
.brand { display: flex; align-items: center; gap: 10px; }.brand-mark { display: grid; width: 38px; height: 38px; place-items: center; border: 1px solid rgba(82,221,255,.46); border-radius: 6px; color: #52ddff; background: #113142; font-weight: 900; }.brand div { display: grid; gap: 3px; }.brand b { font-size: 16px; }.brand small { color: #7893a5; font-size: 10px; }
.title { text-align: center; }.title small,.panel-header small { color: #52ddff; font: 700 9px Consolas, monospace; letter-spacing: 1.5px; }.title h1 { margin: 3px 0 0; font-size: 19px; letter-spacing: 0; }
.header-actions { display: flex; justify-content: flex-end; align-items: center; gap: 8px; }.clock { margin-right: 6px; color: #7893a5; font: 10px Consolas, monospace; }
.header-actions button,.panel-action,.panel-header button { display: inline-flex; align-items: center; justify-content: center; gap: 6px; border: 1px solid rgba(82,221,255,.26); border-radius: 6px; color: #b9d5e4; background: #0a1d30; cursor: pointer; }.header-actions button { min-height: 36px; padding: 0 11px; }.header-actions button:hover,.panel-action:hover,.panel-header button:hover { border-color: #52ddff; color: #fff; background: #113142; }.header-actions .sync-button { border-color: #52ddff; color: #e7f1f7; background: #113142; }.header-actions button:disabled { opacity: .5; cursor: wait; }.spinning { animation: spin .9s linear infinite; }
.hub-body { width: min(1640px,100%); margin: 0 auto; padding: 18px 22px 34px; }

.command-bar { display: grid; grid-template-columns: 250px repeat(5,minmax(170px,1fr)); gap: 8px; border: 1px solid rgba(82,221,255,.18); border-radius: 8px; padding: 10px; background: rgba(6,18,37,.88); }.command-intro { display: flex; min-width: 0; flex-direction: column; justify-content: center; padding: 4px 10px; }.command-intro > span { color: #52ddff; font-size: 10px; font-weight: 800; }.command-intro h2 { margin: 5px 0 0; font-size: 16px; }.command-intro p { margin: 5px 0 0; color: #7893a5; font-size: 10px; }
.command-bar > button { display: grid; grid-template-columns: 34px minmax(0,1fr) 16px; grid-template-rows: auto auto; align-items: center; gap: 4px 9px; min-height: 66px; border: 1px solid rgba(82,221,255,.15); border-radius: 6px; padding: 9px 10px; color: inherit; background: #061225; text-align: left; cursor: pointer; }.command-bar > button:hover { border-color: rgba(82,221,255,.52); background: #113142; transform: translateY(-1px); }.command-icon { grid-row: 1 / 3; display: grid; width: 32px; height: 32px; place-items: center; border: 1px solid rgba(82,221,255,.22); border-radius: 6px; color: #52ddff; background: #0a1d30; font-size: 17px; }.command-copy { min-width: 0; }.command-copy b,.command-copy small { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }.command-copy b { font-size: 12px; }.command-copy small { margin-top: 3px; color: #7893a5; font-size: 9px; }.command-bar em { grid-column: 2; color: #b9d5e4; font-size: 9px; font-style: normal; }.command-bar em.ok { color: #52ddff; }.command-bar em.warn { color: #ffc048; }.command-arrow { grid-column: 3; grid-row: 1 / 3; color: #7893a5; }
.kpi-row { display: grid; grid-template-columns: repeat(6,minmax(0,1fr)); gap: 8px; margin-top: 10px; }.kpi-card { display: grid; grid-template-columns: 34px 1fr; align-items: center; gap: 10px; min-height: 76px; border: 1px solid rgba(82,221,255,.16); border-radius: 6px; padding: 10px 12px; background: rgba(6,18,37,.72); }.kpi-card > .el-icon { display: grid; width: 32px; height: 32px; place-items: center; border-radius: 5px; color: #52ddff; background: #0a1d30; font-size: 17px; }.kpi-card div { display: grid; min-width: 0; }.kpi-card span,.kpi-card small { overflow: hidden; color: #7893a5; font-size: 9px; text-overflow: ellipsis; white-space: nowrap; }.kpi-card strong { margin: 2px 0; font: 800 19px Consolas,monospace; }.load-error { margin-top: 10px; border: 1px solid rgba(255,192,72,.32); border-radius: 6px; padding: 9px 12px; color: #ffd48b; background: rgba(78,49,10,.22); font-size: 10px; }

.dashboard-grid { display: grid; grid-template-columns: repeat(12,minmax(0,1fr)); gap: 10px; margin-top: 10px; }.panel { display: flex; min-width: 0; flex-direction: column; overflow: hidden; border: 1px solid rgba(82,221,255,.18); border-radius: 8px; background: rgba(6,18,37,.88); }.sources-panel { grid-column: span 5; }.governance-panel { grid-column: span 4; }.core-panel { grid-column: span 3; }.quality-panel,.guard-panel,.service-panel { grid-column: span 4; }
.panel-header { display: flex; align-items: center; justify-content: space-between; gap: 14px; min-height: 58px; border-bottom: 1px solid rgba(82,221,255,.14); padding: 11px 14px; text-align: left; }.panel-header div { min-width: 0; }.panel-header h2 { margin: 3px 0 0; font-size: 15px; letter-spacing: 0; }.panel-header button { flex: 0 0 auto; border-color: transparent; padding: 6px 7px; font-size: 9px; }.panel-action { align-self: stretch; min-height: 34px; margin: auto 14px 13px; padding: 0 11px; font-size: 10px; }.empty-state { display: grid; min-height: 160px; place-items: center; color: #7893a5; font-size: 10px; }.empty-state.compact { min-height: 112px; }
.source-list { padding: 4px 13px 8px; }.source-list > button { display: grid; grid-template-columns: 7px minmax(0,1fr) auto 48px 14px; align-items: center; gap: 8px; width: 100%; min-height: 43px; border: 0; border-bottom: 1px solid rgba(82,221,255,.10); padding: 5px 3px; color: inherit; background: transparent; text-align: left; cursor: pointer; }.source-list > button:hover { background: rgba(82,221,255,.055); }.source-state { width: 6px; height: 6px; border-radius: 50%; }.source-state.ok { background: #52ddff; box-shadow: 0 0 7px rgba(82,221,255,.72); }.source-state.warn { background: #ffc048; }.source-state.bad { background: #ff5d7d; }.source-copy { min-width: 0; }.source-copy b,.source-copy small { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }.source-copy b { font-size: 10px; }.source-copy small { margin-top: 2px; color: #7893a5; font-size: 8px; }.source-list em { color: #7893a5; font-size: 8px; font-style: normal; }.source-list strong { color: #52ddff; font: 9px Consolas,monospace; text-align: right; }.source-list > button > .el-icon { color: #557182; font-size: 12px; }
.governance-score,.guard-summary { display: grid; grid-template-columns: repeat(3,1fr); border-bottom: 1px solid rgba(82,221,255,.10); }.governance-score div,.guard-summary div { display: grid; min-height: 72px; place-content: center; border-right: 1px solid rgba(82,221,255,.10); text-align: center; }.governance-score div:last-child,.guard-summary div:last-child { border-right: 0; }.governance-score strong,.guard-summary strong { color: #52ddff; font: 800 19px Consolas,monospace; }.governance-score span,.guard-summary span { margin-top: 4px; color: #7893a5; font-size: 8px; }
.dimension-list,.quality-list { display: grid; gap: 10px; padding: 13px 15px; }.dimension-list > div,.quality-list > div { display: grid; grid-template-columns: 1fr auto; gap: 5px 8px; align-items: center; }.dimension-list span,.quality-list span { color: #b9d5e4; font-size: 10px; }.dimension-list b,.quality-list strong { font: 10px Consolas,monospace; }.dimension-list i,.quality-list i { grid-column: 1 / -1; height: 4px; overflow: hidden; border-radius: 3px; background: rgba(82,221,255,.10); }.dimension-list em,.quality-list em { display: block; height: 100%; background: #22a8c9; }.dimension-list small { grid-column: 1 / -1; overflow: hidden; color: #617d8d; font-size: 8px; text-overflow: ellipsis; white-space: nowrap; }
.core-visual { position: relative; flex: 1; min-height: 304px; overflow: hidden; }.core-node { position: absolute; z-index: 2; top: 50%; left: 50%; display: grid; width: 108px; height: 108px; place-content: center; border: 1px solid #52ddff; border-radius: 50%; text-align: center; background: #0a1d30; box-shadow: inset 0 0 28px rgba(82,221,255,.08); transform: translate(-50%,-50%); }.core-node small,.core-node span { color: #7893a5; font-size: 9px; }.core-node strong { margin: 4px 0; font: 800 24px Consolas,monospace; }.core-ring { position: absolute; top: 50%; left: 50%; border: 1px dashed rgba(82,221,255,.18); border-radius: 50%; transform: translate(-50%,-50%); }.ring-one { width: 176px; height: 176px; }.ring-two { width: 248px; height: 248px; }.satellite { position: absolute; z-index: 3; top: 50%; left: 50%; display: grid; width: 58px; min-height: 40px; place-content: center; border: 1px solid rgba(82,221,255,.28); border-radius: 5px; text-align: center; background: #0a1d30; transform: translate(-50%,-50%) rotate(var(--angle)) translateX(116px) rotate(calc(-1 * var(--angle))); }.satellite b { color: #52ddff; font: 700 11px Consolas,monospace; }.satellite span { margin-top: 2px; color: #7893a5; font-size: 8px; }.source-sync { display: grid; grid-template-columns: minmax(0,1fr) auto; align-items: center; gap: 10px; min-height: 48px; margin-top: auto; border-top: 1px solid rgba(82,221,255,.12); padding: 9px 13px; color: #7893a5; font-size: 9px; }.source-sync span,.source-sync small { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }.source-sync small { text-align: right; }.source-sync i { display: inline-block; width: 6px; height: 6px; margin-right: 6px; border-radius: 50%; }.source-sync i.ok { background: #52ddff; }.source-sync i.warn { background: #ffc048; }
.evidence-note,.monitor-note { margin: 0 15px 12px; color: #7893a5; font-size: 9px; line-height: 1.5; }.guard-summary strong { margin-top: 5px; }.guard-summary strong.warning { color: #ffc048; }.guard-rules { display: grid; padding: 6px 14px 10px; }.guard-rules > div { display: grid; grid-template-columns: 28px minmax(0,1fr) auto; align-items: center; gap: 8px; min-height: 58px; border-bottom: 1px solid rgba(82,221,255,.10); }.rule-icon { display: grid; width: 26px; height: 26px; place-items: center; border-radius: 5px; color: #52ddff; background: #0a1d30; }.guard-rules b,.guard-rules small { display: block; }.guard-rules b { font-size: 10px; }.guard-rules small { margin-top: 3px; color: #7893a5; font-size: 8px; line-height: 1.35; }.guard-rules em { color: #b9d5e4; font-size: 8px; font-style: normal; }
.service-grid { display: grid; grid-template-columns: 1fr 1fr; padding: 4px 14px 10px; }.service-grid div { display: flex; min-height: 48px; align-items: center; justify-content: space-between; gap: 10px; border-bottom: 1px solid rgba(82,221,255,.10); padding: 0 6px; }.service-grid div:nth-child(odd) { border-right: 1px solid rgba(82,221,255,.10); padding-right: 12px; }.service-grid div:nth-child(even) { padding-left: 12px; }.service-grid span { color: #7893a5; font-size: 9px; }.service-grid b { max-width: 120px; overflow: hidden; font-size: 10px; text-overflow: ellipsis; white-space: nowrap; }.service-grid b.healthy { color: #52ddff; }.service-grid b.warning { color: #ffc048; }
@keyframes spin { to { transform: rotate(360deg); } }
@media (max-width: 1380px) { .command-bar { grid-template-columns: repeat(5,1fr); }.command-intro { grid-column: 1 / -1; }.sources-panel { grid-column: span 7; }.governance-panel { grid-column: span 5; }.core-panel,.quality-panel,.guard-panel,.service-panel { grid-column: span 6; } }
@media (max-width: 980px) { .hub-header { grid-template-columns: 1fr auto; }.title,.clock { display: none; }.command-bar { grid-template-columns: repeat(2,1fr); }.kpi-row { grid-template-columns: repeat(3,1fr); }.dashboard-grid { grid-template-columns: repeat(2,minmax(0,1fr)); }.sources-panel,.governance-panel,.core-panel,.quality-panel,.guard-panel,.service-panel { grid-column: span 1; } }
@media (max-width: 640px) { .hub-header { padding: 0 12px; }.brand small,.header-actions button:first-of-type { display: none; }.hub-body { padding: 12px; }.command-bar,.kpi-row,.dashboard-grid { grid-template-columns: 1fr; }.command-intro { grid-column: auto; }.source-list em { display: none; }.source-list > button { grid-template-columns: 7px minmax(0,1fr) 46px 14px; }.service-grid { grid-template-columns: 1fr; }.service-grid div:nth-child(odd) { border-right: 0; padding-right: 6px; }.service-grid div:nth-child(even) { padding-left: 6px; }.source-sync { grid-template-columns: 1fr; gap: 3px; }.source-sync small { padding-left: 12px; text-align: left; } }
</style>

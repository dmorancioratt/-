<template>
  <div class="hub-screen">
    <header class="hub-header">
      <div class="brand"><b>数融智联</b><span>多源异构数据驱动的岗位能力图谱系统</span></div>
      <div class="title"><small>REAL DATA OPERATIONS CENTER</small><h1>管理员数据中枢</h1></div>
      <div class="header-actions">
        <span class="clock">{{ clock }}</span>
        <button type="button" @click="router.push('/overview')"><el-icon><HomeFilled /></el-icon>返回</button>
        <button type="button" :disabled="loading" @click="loadData"><el-icon><Refresh /></el-icon>{{ loading ? '同步中' : '同步' }}</button>
      </div>
    </header>

    <main class="hub-body">
      <section class="kpi-row">
        <article v-for="item in kpis" :key="item.label" class="kpi-card">
          <el-icon><component :is="item.icon" /></el-icon>
          <div><span>{{ item.label }}</span><strong>{{ item.value }}</strong><small>{{ item.note }}</small></div>
        </article>
      </section>

      <div v-if="error" class="load-error">{{ error }}</div>

      <section class="dashboard-grid">
        <article class="panel sources-panel">
          <PanelHeader title="数据源状态" code="DATABASE / SYNC STATUS" />
          <div v-if="sources.length" class="source-list">
            <div v-for="source in sources" :key="source.id || source.name" class="source-row">
              <span class="source-state" :class="sourceTone(source)"></span>
              <div><b>{{ source.name || source.source_name || '未命名数据源' }}</b><small>{{ source.publisher || source.provider || '发布机构未填写' }}</small></div>
              <em>{{ source.status || 'unknown' }}</em>
              <strong>{{ qualityValue(source) }}</strong>
            </div>
          </div>
          <EmptyState v-else text="数据库中暂无数据源记录" />
          <button class="panel-action" type="button" @click="router.push('/datasets')">进入数据源中心</button>
        </article>

        <article class="panel core-panel">
          <PanelHeader title="数据资产关系" code="LIVE DATABASE TOPOLOGY" />
          <div class="core-visual">
            <div class="core-ring ring-one"></div><div class="core-ring ring-two"></div>
            <div class="core-node"><small>当前数据库</small><strong>{{ compact(overview.graph_relation_count) }}</strong><span>图谱关系</span></div>
            <div v-for="node in topology" :key="node.label" class="satellite" :style="node.style">
              <b>{{ node.value }}</b><span>{{ node.label }}</span>
            </div>
          </div>
          <div class="source-sync">
            <span><i :class="syncHealthy ? 'ok' : 'warn'"></i>{{ syncStatusText }}</span>
            <small>{{ syncUpdatedAt }}</small>
          </div>
        </article>

        <article class="panel governance-panel">
          <PanelHeader title="治理与审核" code="REAL REVIEW RECORDS" />
          <section class="governance-score">
            <div><strong>{{ healthScore == null ? '—' : healthScore }}</strong><span>数据健康度</span></div>
            <div><strong>{{ hallucination.sample_size || 0 }}</strong><span>防幻觉样本</span></div>
            <div><strong>{{ pendingReviews.length }}</strong><span>待审核任务</span></div>
          </section>
          <div v-if="governanceDimensions.length" class="dimension-list">
            <div v-for="item in governanceDimensions" :key="item.name || item.label">
              <span>{{ item.name || item.label }}</span><b>{{ dimensionScore(item) }}</b>
              <i><em :style="{ width: `${dimensionScoreNumber(item)}%` }"></em></i>
            </div>
          </div>
          <EmptyState v-else text="暂无数据健康维度记录" />
          <button class="panel-action" type="button" @click="router.push('/review-tasks')">查看审核任务</button>
        </article>

        <article class="panel quality-panel">
          <PanelHeader title="模型评测指标" code="BACKEND EVALUATION" />
          <div class="quality-list">
            <div v-for="item in qualityMetrics" :key="item.label">
              <span>{{ item.label }}</span><strong>{{ item.value == null ? '待测' : `${item.value}%` }}</strong>
              <i><em :style="{ width: `${Number(item.value || 0)}%` }"></em></i>
            </div>
          </div>
          <p class="evidence-note">评测样本 {{ overview.benchmark_sample_count || 0 }} 条 · 业务用例 {{ overview.test_case_count || 0 }} 条</p>
        </article>

        <article class="panel distribution-panel">
          <PanelHeader title="岗位领域分布" code="JOB ENTITY AGGREGATION" />
          <div v-if="jobDistribution.length" class="distribution-list">
            <div v-for="(item, index) in jobDistribution" :key="item.name">
              <span>{{ item.name || '未分类' }}</span><i><em :style="{ width: distributionWidth(item.value), background: palette[index % palette.length] }"></em></i><b>{{ item.value }}</b>
            </div>
          </div>
          <EmptyState v-else text="暂无岗位领域数据" />
        </article>

        <article class="panel service-panel">
          <PanelHeader title="服务接入状态" code="CONFIGURED BACKEND SERVICES" />
          <div class="service-grid">
            <div><span>AI 提供方</span><b>{{ aiStatus.provider || '未配置' }}</b></div>
            <div><span>AI 模型</span><b>{{ aiStatus.model || '未配置' }}</b></div>
            <div><span>AI 状态</span><b :class="aiStatus.configured ? 'healthy' : 'warning'">{{ aiStatus.configured ? '已配置' : '未配置' }}</b></div>
            <div><span>RAG 引擎</span><b :class="ragStatus.available || ragStatus.status === 'ready' ? 'healthy' : 'warning'">{{ ragStatus.status || (ragStatus.available ? 'ready' : '未就绪') }}</b></div>
          </div>
          <p class="monitor-note">CPU、内存、存储和网络指标未接入后端监控，因此不展示随机模拟数值。</p>
          <button class="panel-action" type="button" @click="router.push('/settings')">查看系统设置</button>
        </article>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, onBeforeUnmount, onMounted, ref } from 'vue'
import { Collection, Connection, Document, HomeFilled, Odometer, Refresh, Tickets } from '@element-plus/icons-vue'
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
let timer: number | undefined

const PanelHeader = defineComponent({ props: { title: String, code: String }, setup(props) { return () => h('header', { class: 'panel-header' }, [h('div', [h('small', props.code), h('h2', props.title)])]) } })
const EmptyState = defineComponent({ props: { text: String }, setup(props) { return () => h('div', { class: 'empty-state' }, props.text) } })
const compact = (value: unknown) => new Intl.NumberFormat('zh-CN', { notation: 'compact', maximumFractionDigits: 1 }).format(Number(value || 0))
const formatPercent = (value: unknown) => value == null ? null : Math.round(Number(value) * 10) / 10
const governanceDimensions = computed(() => governance.value.dimensions || [])
const healthScore = computed(() => governance.value.overall == null ? null : formatPercent(governance.value.overall))
const pendingReviews = computed(() => reviews.value.filter((item) => item.status === 'pending'))
const jobDistribution = computed(() => overview.value.job_distribution || [])
const palette = ['#43d9ff', '#4a8dff', '#39ddb1', '#ffbc62', '#9b8cff', '#ff7894']
const kpis = computed(() => [
  { label: '权威数据源', value: compact(sources.value.length), note: '未归档记录', icon: Collection },
  { label: '岗位实体', value: compact(overview.value.job_count), note: '数据库聚合', icon: Document },
  { label: '技能实体', value: compact(overview.value.skill_count), note: '数据库聚合', icon: Tickets },
  { label: '图谱关系', value: compact(overview.value.graph_relation_count), note: '技能与证书关系', icon: Connection },
  { label: '待审核', value: compact(pendingReviews.value.length), note: '真实审核任务', icon: Odometer },
  { label: '业务用例通过率', value: overview.value.business_case_pass_rate == null ? '待测' : `${overview.value.business_case_pass_rate}%`, note: `${overview.value.test_case_count || 0} 条用例`, icon: Odometer }
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
const syncStatusText = computed(() => syncStatus.value.status ? `同步状态：${syncStatus.value.status}` : '尚无同步状态记录')
const syncUpdatedAt = computed(() => syncStatus.value.last_synced_at || syncStatus.value.updated_at || overview.value.market_last_synced_at || '未记录同步时间')
function qualityValue(source: any) { const value = source.quality_score ?? source.health_score; return value == null ? '未评估' : `${Math.round(Number(value) * 10) / 10}%` }
function sourceTone(source: any) { return ['active', 'ready', 'healthy', 'published'].includes(String(source.status).toLowerCase()) ? 'ok' : ['error', 'failed'].includes(String(source.status).toLowerCase()) ? 'bad' : 'warn' }
function dimensionScoreNumber(item: any) { return Math.max(0, Math.min(100, Number(item.score ?? item.value ?? 0))) }
function dimensionScore(item: any) { return `${Math.round(dimensionScoreNumber(item) * 10) / 10}%` }
function distributionWidth(value: unknown) { const max = Math.max(...jobDistribution.value.map((item: any) => Number(item.value || 0)), 1); return `${Number(value || 0) / max * 100}%` }
function tick() { clock.value = new Intl.DateTimeFormat('zh-CN', { dateStyle: 'medium', timeStyle: 'medium', hour12: false }).format(new Date()) }
async function loadData() {
  loading.value = true; error.value = ''
  const results = await Promise.allSettled([api.overview(), api.datasets(), api.dataSourceStatus(), api.governanceHealth(), api.hallucinationStats(), api.reviewTasks(), api.aiStatus(), api.ragStatus()])
  const read = <T,>(index: number, fallback: T): T => results[index].status === 'fulfilled' ? (results[index] as PromiseFulfilledResult<T>).value : fallback
  overview.value = read(0, {}); sources.value = read(1, []); syncStatus.value = read(2, {}); governance.value = read(3, {}); hallucination.value = read(4, {}); reviews.value = read(5, []); aiStatus.value = read(6, {}); ragStatus.value = read(7, {})
  const failures = results.filter((item) => item.status === 'rejected').length
  if (failures) error.value = `${failures} 个后端数据接口暂不可用，其余区域仍展示已成功读取的真实数据。`
  loading.value = false
}
onMounted(() => { tick(); timer = window.setInterval(tick, 1000); loadData() })
onBeforeUnmount(() => { if (timer) window.clearInterval(timer) })
</script>

<style scoped>
.hub-screen { min-height: 100vh; overflow: auto; color: #eaf8ff; background: radial-gradient(900px 470px at 50% -10%, rgba(24, 93, 180, .28), transparent 68%), #020817; font-family: "Microsoft YaHei", sans-serif; }
.hub-header { position: sticky; z-index: 5; top: 0; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 20px; min-height: 80px; border-bottom: 1px solid rgba(74, 171, 234, .24); padding: 0 28px; background: rgba(2, 12, 34, .9); backdrop-filter: blur(18px); }.brand { display: grid; gap: 4px; }.brand b { color: #72e5ff; font-size: 18px; }.brand span { color: #6e91ae; font-size: 10px; }.title { text-align: center; }.title small,.panel-header small { color: #4fdcff; font: 700 9px Consolas, monospace; letter-spacing: 1.5px; }.title h1 { margin: 4px 0 0; font-size: 22px; letter-spacing: 0; }.header-actions { display: flex; justify-content: flex-end; align-items: center; gap: 8px; }.clock { margin-right: 8px; color: #8fb2ca; font: 11px Consolas, monospace; }.header-actions button,.panel-action { display: inline-flex; align-items: center; gap: 6px; border: 1px solid rgba(80, 195, 250, .3); border-radius: 5px; padding: 8px 10px; color: #bdefff; background: rgba(15, 75, 139, .2); cursor: pointer; }.header-actions button:disabled { opacity: .5; }
.hub-body { max-width: 1760px; margin: 0 auto; padding: 18px 24px 35px; }.kpi-row { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 10px; }.kpi-card { display: grid; grid-template-columns: 38px 1fr; align-items: center; gap: 10px; min-height: 90px; border: 1px solid rgba(65, 166, 229, .22); border-radius: 6px; padding: 13px; background: linear-gradient(145deg, rgba(6, 38, 80, .78), rgba(3, 20, 50, .82)); }.kpi-card > .el-icon { width: 35px; height: 35px; border-radius: 5px; color: #58dcff; background: rgba(40, 137, 216, .18); font-size: 19px; }.kpi-card div { min-width: 0; display: grid; }.kpi-card span,.kpi-card small { overflow: hidden; color: #7f9fb8; font-size: 9px; text-overflow: ellipsis; white-space: nowrap; }.kpi-card strong { margin: 4px 0; color: #f1fbff; font: 800 22px Consolas, monospace; }.load-error { margin-top: 12px; border: 1px solid rgba(255, 166, 80, .3); border-radius: 5px; padding: 10px 13px; color: #ffd29a; background: rgba(113, 63, 14, .15); font-size: 11px; }
.dashboard-grid { display: grid; grid-template-columns: minmax(280px, .9fr) minmax(430px, 1.35fr) minmax(280px, .9fr); gap: 12px; margin-top: 12px; }.panel { min-height: 330px; overflow: hidden; border: 1px solid rgba(67, 172, 235, .22); border-radius: 6px; background: linear-gradient(145deg, rgba(5, 32, 70, .78), rgba(2, 17, 43, .86)); }.panel-header { border-bottom: 1px solid rgba(71, 164, 219, .16); padding: 16px 18px; }.panel-header h2 { margin: 5px 0 0; font-size: 15px; letter-spacing: 0; }.panel-action { margin: 14px 18px 18px; font: inherit; font-size: 10px; }.empty-state { display: grid; min-height: 160px; place-items: center; color: #718fa8; font-size: 11px; }
.source-list { padding: 8px 16px 0; }.source-row { display: grid; grid-template-columns: 8px minmax(0, 1fr) auto auto; align-items: center; gap: 9px; border-bottom: 1px solid rgba(67, 146, 199, .13); padding: 10px 0; }.source-state { width: 6px; height: 6px; border-radius: 50%; }.source-state.ok { background: #42e2b3; box-shadow: 0 0 7px #42e2b3; }.source-state.warn { background: #ffbd63; }.source-state.bad { background: #ff6984; }.source-row b,.source-row small { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }.source-row b { font-size: 11px; }.source-row small { margin-top: 3px; color: #6f91aa; font-size: 9px; }.source-row em { color: #83a7bf; font-size: 9px; font-style: normal; }.source-row > strong { color: #68dfff; font: 10px Consolas, monospace; }
.core-visual { position: relative; min-height: 280px; overflow: hidden; }.core-node { position: absolute; z-index: 2; top: 50%; left: 50%; display: grid; width: 140px; height: 140px; place-content: center; border: 1px solid #64ddff; border-radius: 50%; text-align: center; background: radial-gradient(circle, #124e8b, #03152e 68%); box-shadow: 0 0 45px rgba(47, 183, 255, .35); transform: translate(-50%, -50%); }.core-node small,.core-node span { color: #7fa9c2; font-size: 9px; }.core-node strong { margin: 6px 0; color: #7ceaff; font: 800 28px Consolas, monospace; }.core-ring { position: absolute; top: 50%; left: 50%; border: 1px dashed rgba(89, 208, 255, .25); border-radius: 50%; transform: translate(-50%, -50%); }.ring-one { width: 230px; height: 230px; }.ring-two { width: 340px; height: 340px; }.satellite { position: absolute; z-index: 3; top: 50%; left: 50%; display: grid; width: 72px; min-height: 48px; place-content: center; border: 1px solid rgba(78, 204, 255, .32); border-radius: 5px; text-align: center; background: rgba(5, 38, 79, .9); transform: translate(-50%, -50%) rotate(var(--angle)) translateX(160px) rotate(calc(-1 * var(--angle))); }.satellite b { color: #61e2ff; font: 700 13px Consolas, monospace; }.satellite span { margin-top: 3px; color: #8ba8bd; font-size: 8px; }.source-sync { display: flex; justify-content: space-between; gap: 10px; border-top: 1px solid rgba(67, 151, 207, .15); padding: 13px 18px; color: #86a6bd; font-size: 9px; }.source-sync i { display: inline-block; width: 6px; height: 6px; margin-right: 6px; border-radius: 50%; }.source-sync i.ok { background: #41e0af; }.source-sync i.warn { background: #ffb95a; }
.governance-score { display: grid; grid-template-columns: repeat(3, 1fr); gap: 7px; padding: 14px 15px 8px; }.governance-score div { display: grid; min-height: 68px; place-content: center; border: 1px solid rgba(66, 168, 227, .18); border-radius: 4px; text-align: center; background: rgba(8, 50, 94, .3); }.governance-score strong { color: #64e4ff; font: 800 18px Consolas, monospace; }.governance-score span { margin-top: 5px; color: #7e9db4; font-size: 8px; }.dimension-list,.quality-list { display: grid; gap: 11px; padding: 12px 18px; }.dimension-list > div,.quality-list > div { display: grid; grid-template-columns: 1fr auto; gap: 7px; align-items: center; }.dimension-list span,.quality-list span { color: #9cbbce; font-size: 10px; }.dimension-list b,.quality-list strong { color: #e3f8ff; font: 10px Consolas, monospace; }.dimension-list i,.quality-list i { grid-column: 1 / -1; height: 4px; overflow: hidden; border-radius: 3px; background: rgba(61, 125, 175, .18); }.dimension-list em,.quality-list em { display: block; height: 100%; background: linear-gradient(90deg, #278bea, #50e1d0); }.evidence-note,.monitor-note { margin: 5px 18px 12px; color: #708fa8; font-size: 9px; line-height: 1.6; }
.distribution-list { display: grid; gap: 13px; padding: 21px 18px; }.distribution-list > div { display: grid; grid-template-columns: 95px 1fr 36px; align-items: center; gap: 8px; }.distribution-list span { overflow: hidden; color: #9bbace; font-size: 10px; text-overflow: ellipsis; white-space: nowrap; }.distribution-list i { height: 6px; overflow: hidden; border-radius: 3px; background: rgba(64, 126, 177, .18); }.distribution-list em { display: block; height: 100%; border-radius: inherit; }.distribution-list b { color: #dff6ff; font: 10px Consolas, monospace; text-align: right; }.service-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; padding: 18px; }.service-grid div { min-height: 72px; display: grid; place-content: center; border: 1px solid rgba(65, 161, 218, .18); border-radius: 4px; text-align: center; background: rgba(7, 45, 87, .3); }.service-grid span { color: #7899b1; font-size: 9px; }.service-grid b { max-width: 150px; margin-top: 6px; overflow: hidden; color: #dff7ff; font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }.service-grid b.healthy { color: #4be2b5; }.service-grid b.warning { color: #ffbd68; }
@media (max-width: 1200px) { .kpi-row { grid-template-columns: repeat(3, 1fr); }.dashboard-grid { grid-template-columns: 1fr 1fr; }.core-panel { grid-column: span 2; }.hub-header { grid-template-columns: 1fr auto; }.title { display: none; } } @media (max-width: 720px) { .hub-header { padding: 0 12px; }.brand span,.clock { display: none; }.hub-body { padding: 12px; }.kpi-row,.dashboard-grid { grid-template-columns: 1fr; }.core-panel { grid-column: auto; }.service-grid { grid-template-columns: 1fr; } }
</style>

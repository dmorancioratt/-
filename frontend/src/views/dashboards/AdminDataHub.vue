<template>
  <div ref="screenRef" class="hub-screen">
    <div class="hub-stage" :style="stageStyle">
      <!-- ============ 背景装饰 ============ -->
      <div class="stage-grid" aria-hidden="true"></div>
      <div class="stage-glow" aria-hidden="true"></div>

      <!-- ============ 顶部标题栏 ============ -->
      <header class="hub-header">
        <div class="hh-left">
          <div class="hh-logo">
            <svg viewBox="0 0 40 40" class="hh-logo__mark">
              <polygon points="20,3 35,11.5 35,28.5 20,37 5,28.5 5,11.5" fill="none" stroke="url(#lg-logo)" stroke-width="2" />
              <polygon points="20,10 29,15 29,25 20,30 11,25 11,15" fill="rgba(64,150,255,.18)" stroke="#58c6ff" stroke-width="1.2" />
              <circle cx="20" cy="20" r="3.4" fill="#58c6ff" />
              <defs>
                <linearGradient id="lg-logo" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0" stop-color="#6fd6ff" /><stop offset="1" stop-color="#2f7bff" />
                </linearGradient>
              </defs>
            </svg>
            <div class="hh-logo__name">数融智联</div>
          </div>
          <div class="hh-brand-divider"></div>
          <div class="hh-brand-desc">多源异构数据驱动的<br />岗位能力图谱动态演化与智能构建系统</div>
        </div>

        <div class="hh-center">
          <div class="hh-wing hh-wing--l"></div>
          <div class="hh-frame-wrap">
            <div class="hh-frame">
              <h1>数融智联 · 管理员数据中枢</h1>
              <p>智能洞察 · 风险先知 · 决策赋能</p>
            </div>
          </div>
          <div class="hh-wing hh-wing--r"></div>
        </div>

        <div class="hh-right">
          <div class="hh-clock">
            <div class="hh-clock__time font-tech">{{ clock.time }}</div>
            <div class="hh-clock__date">{{ clock.date }} {{ clock.weekday }}</div>
          </div>
          <span class="hh-status"><i></i>系统状态</span>
          <button class="hh-btn" type="button" @click="goOverview" title="返回系统概览">
            <el-icon><HomeFilled /></el-icon>返回
          </button>
          <button class="hh-btn" type="button" @click="toggleFullscreen">
            <el-icon><FullScreen /></el-icon>{{ isFullscreen ? '退出全屏' : '全屏' }}
          </button>
        </div>
      </header>

      <!-- ============ KPI 指标行 ============ -->
      <section class="kpi-row">
        <article v-for="(card, i) in kpiCards" :key="card.key" class="kpi-card" :style="{ animationDelay: `${i * 70}ms` }">
          <div class="kpi-icon" :class="`kpi-icon--${card.tone}`">
            <el-icon><component :is="card.icon" /></el-icon>
          </div>
          <div class="kpi-meta">
            <span class="kpi-label">{{ card.label }}</span>
            <div class="kpi-value font-tech">
              <b>{{ card.format(kpiDisplay[card.key]) }}</b>
              <span v-if="card.suffix" class="kpi-suffix">{{ card.suffix }}</span>
            </div>
          </div>
          <div class="kpi-side">
            <template v-if="card.key !== 'health'">
              <b class="kpi-delta" :class="card.dir === 'up' ? 'is-up' : 'is-down'">{{ card.delta }}</b>
              <span class="kpi-foot">{{ card.foot }}</span>
            </template>
            <b v-else class="kpi-verdict">优秀</b>
          </div>
          <i class="kpi-corner kpi-corner--tr"></i>
          <i class="kpi-corner kpi-corner--bl"></i>
        </article>
      </section>

      <!-- ============ 主体三栏 ============ -->
      <main class="hub-body">
        <!-- ---------- 左栏 ---------- -->
        <section class="col col-left">
          <article class="panel panel--health">
            <div class="panel-head">
              <h2><i class="title-bar"></i>数据源健康度 TOP5</h2>
            </div>
            <div class="health-list">
              <div v-for="(s, i) in healthTop" :key="s.name" class="health-row">
                <div class="health-row__top">
                  <span class="health-ico"><el-icon><component :is="s.icon" /></el-icon></span>
                  <span class="health-name">{{ s.name }}</span>
                  <b class="health-pct font-tech">{{ s.value }}%</b>
                </div>
                <div class="health-track">
                  <i class="health-fill" :style="{ width: healthWidth(i), transitionDelay: `${i * 120}ms` }"></i>
                </div>
              </div>
            </div>
          </article>

          <article class="panel panel--quality">
            <div class="panel-head">
              <h2><i class="title-bar"></i>数据质量趋势</h2>
            </div>
            <div ref="qualityChartEl" class="quality-chart"></div>
          </article>

          <article class="panel panel--alerts">
            <div class="panel-head">
              <h2><i class="title-bar"></i>实时告警</h2>
              <button class="panel-more" type="button" @click="router.push('/review-tasks')">查看更多 &gt;</button>
            </div>
            <TransitionGroup name="alert" tag="div" class="alert-list">
              <div v-for="a in alerts" :key="a.id" class="alert-row">
                <span class="alert-ico" :class="`alert-ico--${a.tone}`">
                  <el-icon><component :is="a.icon" /></el-icon>
                </span>
                <p class="alert-text"><b :class="`alert-tag--${a.tone}`">【{{ a.type }}】</b>{{ a.text }}</p>
                <span class="alert-time font-tech">{{ a.time }}</span>
              </div>
            </TransitionGroup>
          </article>
        </section>

        <!-- ---------- 中栏 ---------- -->
        <section class="col col-center">
          <div class="hub-visual">
            <img class="hub-core" :src="hubCoreImg" alt="数据中枢" draggable="false" />
            <canvas ref="hubCanvasEl" class="hub-fx"></canvas>
            <div class="hub-vignette" aria-hidden="true"></div>
          </div>

          <div class="center-bottom">
            <article class="panel panel--flow">
              <div class="panel-head">
                <h2><i class="title-bar"></i>数据流向监控<span class="live-badge"><i></i>实时</span></h2>
              </div>
              <div class="flow-content">
                <canvas ref="flowCanvasEl" class="flow-canvas"></canvas>
                <div
                  v-for="(chip, i) in flowLeft"
                  :key="`fl-${chip}`"
                  class="flow-chip flow-chip--l"
                  :style="flowChipStyle(i, 'l')"
                >
                  <i class="flow-dot flow-dot--in"></i>{{ chip }}
                </div>
                <div class="flow-hub">
                  <svg viewBox="0 0 24 24" class="flow-hub__ico"><circle cx="12" cy="7" r="3" fill="#7fd4ff" /><circle cx="6.5" cy="16" r="2.4" fill="#4da6ff" /><circle cx="17.5" cy="16" r="2.4" fill="#4da6ff" /><path d="M12 10v4M8.4 14.6 10.4 12M15.6 14.6 13.6 12" stroke="#7fd4ff" stroke-width="1.3" /></svg>
                  <span>数据中台</span>
                </div>
                <div
                  v-for="(chip, i) in flowRight"
                  :key="`fr-${chip}`"
                  class="flow-chip flow-chip--r"
                  :style="flowChipStyle(i, 'r')"
                >
                  <i class="flow-dot flow-dot--out"></i>{{ chip }}
                </div>
              </div>
            </article>

            <article class="panel panel--models">
              <div class="panel-head">
                <h2><i class="title-bar"></i>模型服务调用 TOP5</h2>
              </div>
              <div class="model-list">
                <div v-for="(m, i) in modelTop" :key="m.name" class="model-row">
                  <span class="model-rank font-tech" :class="`model-rank--${i + 1}`">{{ i + 1 }}</span>
                  <div class="model-main">
                    <div class="model-row__top">
                      <span class="model-name">{{ m.name }}</span>
                      <span class="model-val"><b class="font-tech">{{ m.value }}</b> 万次</span>
                      <b class="model-delta">+{{ m.delta }}%</b>
                    </div>
                    <div class="model-track">
                      <i class="model-fill" :style="{ width: `${(m.value / modelTop[0].value) * 100}%`, transitionDelay: `${i * 120}ms` }"></i>
                    </div>
                  </div>
                </div>
              </div>
            </article>
          </div>
        </section>

        <!-- ---------- 右栏 ---------- -->
        <section class="col col-right">
          <article class="panel panel--dist">
            <div class="panel-head">
              <h2><i class="title-bar"></i>数据类型分布</h2>
            </div>
            <div class="dist-content">
              <div ref="distChartEl" class="dist-chart"></div>
              <div class="dist-legend">
                <div v-for="d in typeDist" :key="d.name" class="dist-row">
                  <i class="dist-swatch" :style="{ background: d.color, boxShadow: `0 0 8px ${d.color}66` }"></i>
                  <div class="dist-copy">
                    <span class="dist-name">{{ d.name }}</span>
                    <span class="dist-pct">{{ d.pct }}</span>
                  </div>
                  <b class="dist-val font-tech">{{ d.value.toFixed(2) }} <small>PB</small></b>
                </div>
              </div>
            </div>
          </article>

          <article class="panel panel--tasks">
            <div class="panel-head">
              <h2><i class="title-bar"></i>任务处理趋势</h2>
              <div class="panel-legend">
                <span><i style="background:#3f8cff"></i>成功任务</span>
                <span><i style="background:#ff5d6a"></i>失败任务</span>
              </div>
            </div>
            <div ref="taskChartEl" class="task-chart"></div>
          </article>

          <article class="panel panel--resource">
            <div class="panel-head">
              <h2><i class="title-bar"></i>系统资源监控</h2>
            </div>
            <div class="gauge-row">
              <div v-for="g in gauges" :key="g.label" class="gauge">
                <div class="gauge-ring">
                  <svg viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="42" class="gauge-track" />
                    <circle
                      cx="50" cy="50" r="42"
                      class="gauge-arc"
                      :stroke="g.color"
                      :style="{ strokeDasharray: `${(g.value / 100) * 263.9}, 263.9` }"
                    />
                  </svg>
                  <b class="gauge-num font-tech">{{ Math.round(g.value) }}<small>%</small></b>
                </div>
                <span class="gauge-label">{{ g.label }}</span>
              </div>
            </div>
            <div class="res-footer">
              <span>负载均衡: <b class="is-ok">良好</b></span>
              <span>集群状态: <b class="is-ok">稳定</b></span>
              <span>节点数量: <b class="font-tech res-nodes">{{ resNodes }}</b></span>
            </div>
          </article>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, markRaw, nextTick, onActivated, onDeactivated, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import {
  Box, Clock, CircleCloseFilled, Collection, Connection, Document, Files, FullScreen,
  HomeFilled, OfficeBuilding, Odometer, School, User, Warning, WarningFilled
} from '@element-plus/icons-vue'
import hubCoreImg from '@/assets/images/admin-hub-core.png'

const router = useRouter()

/* ================= 舞台缩放（1920 x 1080 设计稿等比适配） ================= */
const STAGE_W = 1920
const STAGE_H = 1080
const stageScale = ref(1)
const screenRef = ref<HTMLElement | null>(null)
const stageStyle = computed(() => ({
  width: `${STAGE_W}px`,
  height: `${STAGE_H}px`,
  transform: `translate(-50%, -50%) scale(${stageScale.value})`
}))
function fitStage() {
  const el = screenRef.value
  const w = el?.clientWidth || document.documentElement.clientWidth || window.innerWidth
  const h = el?.clientHeight || document.documentElement.clientHeight || window.innerHeight
  stageScale.value = Math.min(w / STAGE_W, h / STAGE_H)
}
let stageObserver: ResizeObserver | null = null

/* ================= 时钟 ================= */
const WEEKDAYS = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
const pad = (n: number) => String(n).padStart(2, '0')
const clock = reactive({ time: '--:--:--', date: '----', weekday: '' })
function tickClock() {
  const d = new Date()
  clock.time = `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
  clock.date = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
  clock.weekday = WEEKDAYS[d.getDay()]
}

/* ================= 全屏 ================= */
const isFullscreen = ref(false)
async function toggleFullscreen() {
  try {
    if (!document.fullscreenElement) await document.documentElement.requestFullscreen()
    else await document.exitFullscreen()
  } catch { /* 浏览器拒绝时静默 */ }
}
function onFullscreenChange() { isFullscreen.value = Boolean(document.fullscreenElement) }
function goOverview() { router.push('/overview') }

/* ================= KPI ================= */
type KpiKey = 'total' | 'sources' | 'tasks' | 'risks' | 'calls' | 'health'
const kpiBase: Record<KpiKey, number> = { total: 2.44, sources: 128, tasks: 8342, risks: 37, calls: 92.1, health: 98.7 }
const kpiDisplay = reactive<Record<KpiKey, number>>({ total: 0, sources: 0, tasks: 0, risks: 0, calls: 0, health: 0 })

const kpiCards = [
  { key: 'total' as KpiKey, label: '数据总量', icon: Box, tone: 'blue', delta: '+12.6%', dir: 'up', foot: '较昨日增长', suffix: 'PB', format: (v: number) => v.toFixed(2) },
  { key: 'sources' as KpiKey, label: '数据源数量', icon: Files, tone: 'cyan', delta: '+8', dir: 'up', foot: '较昨日增长', suffix: '个', format: (v: number) => String(Math.round(v)) },
  { key: 'tasks' as KpiKey, label: '处理任务数', icon: Document, tone: 'gold', delta: '+18.3%', dir: 'up', foot: '较昨日增长', suffix: '个', format: (v: number) => Math.round(v).toLocaleString() },
  { key: 'risks' as KpiKey, label: '风险预警数', icon: Warning, tone: 'red', delta: '-5.6%', dir: 'down', foot: '较昨日下降', suffix: '条', format: (v: number) => String(Math.round(v)) },
  { key: 'calls' as KpiKey, label: '模型服务调用', icon: User, tone: 'violet', delta: '+24.7%', dir: 'up', foot: '较昨日增长', suffix: '万次', format: (v: number) => v.toFixed(1) },
  { key: 'health' as KpiKey, label: '系统健康度', icon: Odometer, tone: 'green', delta: '', dir: 'up', foot: '', suffix: '/100', format: (v: number) => v.toFixed(1) }
]

const kpiRafs: Partial<Record<KpiKey, number>> = {}
function tweenValue(key: KpiKey, to: number, dur = 900) {
  const from = kpiDisplay[key]
  const t0 = performance.now()
  if (kpiRafs[key]) cancelAnimationFrame(kpiRafs[key]!)
  const step = (now: number) => {
    const k = Math.min(1, (now - t0) / dur)
    const e = 1 - Math.pow(1 - k, 3)
    kpiDisplay[key] = from + (to - from) * e
    if (k < 1) kpiRafs[key] = requestAnimationFrame(step)
    else kpiRafs[key] = undefined
  }
  kpiRafs[key] = requestAnimationFrame(step)
}
function setKpi(key: KpiKey, value: number) { tweenValue(key, value, 700) }

/* ================= 数据源健康度 TOP5 ================= */
const healthTop = [
  { name: '人社部数据源', value: 98.6, icon: OfficeBuilding },
  { name: '智联招聘数据源', value: 96.2, icon: User },
  { name: '企业库数据源', value: 94.8, icon: Collection },
  { name: '教育部数据源', value: 93.1, icon: School },
  { name: '行业协会数据源', value: 91.3, icon: Connection }
]
const healthMounted = ref(false)
const healthWidth = (i: number) => (healthMounted.value ? `${healthTop[i].value}%` : '0%')

/* ================= 实时告警 ================= */
type AlertTone = 'red' | 'orange' | 'cyan'
interface AlertItem { id: number; type: string; tone: AlertTone; text: string; time: string; icon: any }
const alertIconClose = markRaw(CircleCloseFilled)
const alertIconWarning = markRaw(WarningFilled)
const alertIconClock = markRaw(Clock)
let alertSeq = 1
function fmtClockOffset(secondsAgo: number) {
  const d = new Date(Date.now() - secondsAgo * 1000)
  return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}
const alerts = ref<AlertItem[]>([
  { id: alertSeq++, type: '数据缺失', tone: 'red', text: '企业库数据源部分字段缺失', time: fmtClockOffset(137), icon: alertIconClose },
  { id: alertSeq++, type: '风险预警', tone: 'orange', text: '检测到异常访问行为', time: fmtClockOffset(285), icon: alertIconWarning },
  { id: alertSeq++, type: '任务失败', tone: 'red', text: '岗位图谱构建任务失败', time: fmtClockOffset(475), icon: alertIconClose },
  { id: alertSeq++, type: '模型异常', tone: 'red', text: '风险预测模型置信度下降', time: fmtClockOffset(610), icon: alertIconClose },
  { id: alertSeq++, type: '数据延迟', tone: 'cyan', text: '行业析能数据更新延迟', time: fmtClockOffset(726), icon: alertIconClock }
])
const alertPool: Omit<AlertItem, 'id' | 'time'>[] = [
  { type: '风险预警', tone: 'orange', text: '监测到批量爬取疑似行为', icon: alertIconWarning },
  { type: '数据质量', tone: 'orange', text: '智联招聘字段格式异常率上升', icon: alertIconWarning },
  { type: '数据延迟', tone: 'cyan', text: '简历解析队列出现积压', icon: alertIconClock },
  { type: '任务完成', tone: 'cyan', text: '岗位匹配批处理任务已完成', icon: alertIconClock },
  { type: '模型异常', tone: 'red', text: '薪酬预测模型检测到数据漂移', icon: alertIconClose },
  { type: '风险预警', tone: 'orange', text: '检测到异地账号登录尝试', icon: alertIconWarning },
  { type: '数据缺失', tone: 'red', text: '行业协会月度样本缺失 3 条', icon: alertIconClose }
]
function pushAlert() {
  const tpl = alertPool[Math.floor(Math.random() * alertPool.length)]
  alerts.value.unshift({ ...tpl, id: alertSeq++, time: fmtClockOffset(0) })
  if (alerts.value.length > 6) alerts.value.pop()
}

/* ================= 数据类型分布 / 任务趋势 ================= */
const typeDist = [
  { name: '结构化数据', value: 1.32, pct: '54.1%', color: '#2f7bff' },
  { name: '半结构化数据', value: 0.68, pct: '27.9%', color: '#2fd8b0' },
  { name: '非结构化数据', value: 0.44, pct: '18.0%', color: '#ffb03a' }
]
const trendDays = ['08/22', '08/23', '08/24', '08/25', '08/26', '08/27', '08/28']
const qualitySeries = [
  { name: '完整性', color: '#35e08d', data: [96.2, 95.8, 96.5, 97.1, 96.8, 97.3, 97.6] },
  { name: '准确性', color: '#ffb03a', data: [78, 62, 84, 55, 88, 72, 86] },
  { name: '一致性', color: '#58c6ff', data: [90, 88, 91, 89, 92, 90, 93] }
]
const taskSuccess = [7.2, 8.1, 8.6, 8.3, 8.9, 8.2, 8.7]
const taskFail = [0.35, 0.28, 0.31, 0.22, 0.26, 0.24, 0.3]

/* ================= 模型服务调用 TOP5 ================= */
const modelTop = [
  { name: '风险预测模型', value: 28.7, delta: 15.2 },
  { name: '能力评估模型', value: 22.1, delta: 12.8 },
  { name: '岗位匹配模型', value: 18.3, delta: 9.7 },
  { name: '薪酬预测模型', value: 12.6, delta: 8.3 },
  { name: '趋势分析模型', value: 10.4, delta: 7.1 }
]

/* ================= 系统资源监控 ================= */
const gauges = reactive([
  { label: 'CPU使用率', value: 32, color: '#35e08d' },
  { label: '内存使用率', value: 68, color: '#4da6ff' },
  { label: '存储使用率', value: 41, color: '#ffb03a' },
  { label: '网络使用率', value: 25, color: '#9b8cff' }
])
const resNodes = ref(24)
function driftGauges() {
  gauges.forEach((g) => {
    const next = g.value + (Math.random() * 5 - 2.5)
    g.value = Math.round(Math.min(92, Math.max(8, next)) * 10) / 10
  })
  if (Math.random() < 0.12) resNodes.value = 24 + (Math.random() < 0.5 ? 0 : Math.round(Math.random() * 2 - 1))
}

/* ================= 数据流向监控 ================= */
const flowLeft = ['人社部', '教育部', '企业库', '行业协会', '其他数据源']
const flowRight = ['岗位图谱', '风险预警', '能力评估', '智能推荐', '其他应用']
const FLOW_CONTENT_W = 532
const FLOW_CONTENT_H = 258
const FLOW_CHIP_W = 118
const FLOW_CHIP_H = 32
function flowChipStyle(i: number, side: 'l' | 'r') {
  const top = 6 + i * ((FLOW_CONTENT_H - 12 - FLOW_CHIP_H) / 4)
  return {
    top: `${top}px`,
    left: side === 'l' ? '0px' : `${FLOW_CONTENT_W - FLOW_CHIP_W}px`
  }
}

/* ================= 中央枢纽粒子特效 ================= */
const hubCanvasEl = ref<HTMLCanvasElement | null>(null)
const HUB_W = 980
const HUB_H = 503
// 中央 PNG 在舞台中的显示区域（高 503 等比 → 宽 777，水平居中）
const IMG_W = 777
const IMG_H = 503
const IMG_X = (HUB_W - IMG_W) / 2
const IMG_Y = 0
const HUB_CENTER = { x: IMG_X + 0.501 * IMG_W, y: IMG_Y + 0.476 * IMG_H }
// 六大中心的六边形图标锚点（相对裁剪图的比例坐标）
const HUB_NODES = [
  { fx: 0.576, fy: 0.103 },
  { fx: 0.275, fy: 0.299 },
  { fx: 0.773, fy: 0.271 },
  { fx: 0.284, fy: 0.578 },
  { fx: 0.787, fy: 0.578 },
  { fx: 0.531, fy: 0.821 }
].map((n) => ({ x: IMG_X + n.fx * IMG_W, y: IMG_Y + n.fy * IMG_H, period: 0, phase: Math.random() * 10 }))

interface HubDust { x: number; y: number; vy: number; sway: number; phase: number; r: number; life: number; maxLife: number; hue: number }
interface HubPulse { node: number; t: number; speed: number; size: number }
interface HubOrbiter { theta: number; speed: number; rx: number; ry: number; tilt: number; r: number }
interface HubRing { t: number }

let hubCtx: CanvasRenderingContext2D | null = null
let hubDust: HubDust[] = []
let hubPulses: HubPulse[] = []
let hubOrbiters: HubOrbiter[] = []
let hubRings: HubRing[] = []

function initHubFx() {
  const canvas = hubCanvasEl.value
  if (!canvas) return
  hubCtx = canvas.getContext('2d')
  const dpr = Math.min(2, window.devicePixelRatio || 1)
  canvas.width = HUB_W * dpr
  canvas.height = HUB_H * dpr
  hubCtx?.setTransform(dpr, 0, 0, dpr, 0, 0)

  hubDust = Array.from({ length: 64 }, () => spawnDust(true))
  hubPulses = HUB_NODES.map((_, i) => ({ node: i, t: Math.random(), speed: 0.28 + Math.random() * 0.2, size: 1.6 + Math.random() * 1.4 }))
  hubOrbiters = Array.from({ length: 4 }, (_, i) => ({
    theta: Math.random() * Math.PI * 2,
    speed: (0.25 + Math.random() * 0.3) * (i % 2 === 0 ? 1 : -1),
    rx: 130 + Math.random() * 70,
    ry: 42 + Math.random() * 26,
    tilt: -0.22 + Math.random() * 0.14,
    r: 1.4 + Math.random() * 1.2
  }))
  hubRings = [{ t: 0 }]
  HUB_NODES.forEach((n) => { n.period = 2.2 + Math.random() * 1.8 })
}

function spawnDust(anywhere = false): HubDust {
  const maxLife = 4 + Math.random() * 4
  return {
    x: IMG_X + 40 + Math.random() * (IMG_W - 80),
    y: anywhere ? HUB_CENTER.y + 40 + Math.random() * (HUB_H - HUB_CENTER.y - 60) : HUB_H - Math.random() * 30,
    vy: 10 + Math.random() * 18,
    sway: 8 + Math.random() * 14,
    phase: Math.random() * Math.PI * 2,
    r: 0.6 + Math.random() * 1.4,
    life: anywhere ? Math.random() * maxLife : 0,
    maxLife,
    hue: Math.random() < 0.7 ? 200 : Math.random() < 0.5 ? 185 : 215
  }
}

function drawHubFx(dt: number, now: number) {
  const ctx = hubCtx
  if (!ctx) return
  ctx.clearRect(0, 0, HUB_W, HUB_H)
  ctx.globalCompositeOperation = 'lighter'

  // 1. 上升粒子
  for (const p of hubDust) {
    p.life += dt
    if (p.life > p.maxLife) Object.assign(p, spawnDust())
    p.y -= p.vy * dt
    const x = p.x + Math.sin(now * 0.001 + p.phase) * p.sway
    const k = p.life / p.maxLife
    const alpha = Math.sin(Math.PI * k) * 0.55
    ctx.beginPath()
    ctx.fillStyle = `hsla(${p.hue}, 95%, 72%, ${alpha})`
    ctx.arc(x, p.y, p.r, 0, Math.PI * 2)
    ctx.fill()
  }

  // 2. 六中心 → 数据中枢 的能量脉冲
  HUB_NODES.forEach((n, i) => {
    const cycle = n.period
    const local = (now * 0.001 + n.phase * 0.7) % cycle
    const t = local / cycle
    // 控制点：垂直于连线方向偏移，形成轻弧线
    const mx = (n.x + HUB_CENTER.x) / 2
    const my = (n.y + HUB_CENTER.y) / 2
    const dx = HUB_CENTER.x - n.x
    const dy = HUB_CENTER.y - n.y
    const len = Math.hypot(dx, dy) || 1
    const cx = mx + (-dy / len) * 34 * (i % 2 === 0 ? 1 : -1)
    const cy = my + (dx / len) * 34 * (i % 2 === 0 ? 1 : -1)
    const point = (u: number) => {
      const a = 1 - u
      return {
        x: a * a * n.x + 2 * a * u * cx + u * u * HUB_CENTER.x,
        y: a * a * n.y + 2 * a * u * cy + u * u * HUB_CENTER.y
      }
    }
    // 常亮的引导细线
    ctx.beginPath()
    ctx.moveTo(n.x, n.y)
    ctx.quadraticCurveTo(cx, cy, HUB_CENTER.x, HUB_CENTER.y)
    ctx.strokeStyle = 'rgba(88, 198, 255, 0.10)'
    ctx.lineWidth = 1
    ctx.stroke()
    // 脉冲光点 + 拖尾
    for (let k = 0; k < 4; k++) {
      const tt = t - k * 0.035
      if (tt < 0) continue
      const pos = point(tt)
      const alpha = (1 - k / 4) * Math.sin(Math.PI * Math.min(1, t)) * 0.9
      const r = (3.2 - k * 0.55) * 1.15
      ctx.beginPath()
      ctx.fillStyle = `rgba(120, 210, 255, ${alpha})`
      ctx.arc(pos.x, pos.y, Math.max(0.5, r), 0, Math.PI * 2)
      ctx.fill()
    }
  })

  // 3. 环绕电子
  for (const o of hubOrbiters) {
    o.theta += o.speed * dt
    const ox = Math.cos(o.theta) * o.rx
    const oy = Math.sin(o.theta) * o.ry
    const x = HUB_CENTER.x + ox * Math.cos(o.tilt) - oy * Math.sin(o.tilt)
    const y = HUB_CENTER.y + ox * Math.sin(o.tilt) + oy * Math.cos(o.tilt)
    const tw = 0.45 + 0.4 * Math.sin(now * 0.004 + o.theta * 3)
    ctx.beginPath()
    ctx.fillStyle = `rgba(140, 220, 255, ${Math.max(0.1, tw)})`
    ctx.arc(x, y, o.r, 0, Math.PI * 2)
    ctx.fill()
  }

  // 4. 底部扩散光环
  const ring = hubRings[0]
  ring.t += dt / 5
  if (ring.t > 1) ring.t = 0
  const rr = ring.t * 250
  const rg = ctx.createRadialGradient(HUB_CENTER.x, HUB_CENTER.y + 128, rr * 0.72, HUB_CENTER.x, HUB_CENTER.y + 128, rr)
  rg.addColorStop(0, 'rgba(64, 150, 255, 0)')
  rg.addColorStop(0.85, `rgba(64, 170, 255, ${0.14 * (1 - ring.t)})`)
  rg.addColorStop(1, 'rgba(64, 170, 255, 0)')
  ctx.fillStyle = rg
  ctx.beginPath()
  ctx.ellipse(HUB_CENTER.x, HUB_CENTER.y + 128, rr, rr * 0.32, 0, 0, Math.PI * 2)
  ctx.fill()

  ctx.globalCompositeOperation = 'source-over'
}

/* ================= 数据流向曲线 ================= */
const flowCanvasEl = ref<HTMLCanvasElement | null>(null)
let flowCtx: CanvasRenderingContext2D | null = null
interface FlowDot { curve: number; t: number; speed: number }
let flowDots: FlowDot[] = []
let flowFlashes: { side: 'l' | 'r'; y: number; t: number }[] = []

const FLOW_HUB = { w: 72, h: 148 }
const flowChipCy = (i: number) => 6 + i * ((FLOW_CONTENT_H - 12 - FLOW_CHIP_H) / 4) + FLOW_CHIP_H / 2
const flowHubCy = (i: number) => (FLOW_CONTENT_H - FLOW_HUB.h) / 2 + 24 + i * ((FLOW_HUB.h - 48) / 4)
const flowHubLeft = FLOW_CONTENT_W / 2 - FLOW_HUB.w / 2
const flowHubRight = FLOW_CONTENT_W / 2 + FLOW_HUB.w / 2

interface FlowCurve { x0: number; y0: number; x1: number; y1: number; side: 'l' | 'r' }
const flowCurves: FlowCurve[] = [
  ...flowLeft.map((_, i) => ({ x0: FLOW_CHIP_W, y0: flowChipCy(i), x1: flowHubLeft, y1: flowHubCy(i), side: 'l' as const })),
  ...flowRight.map((_, i) => ({ x0: flowHubRight, y0: flowHubCy(i), x1: FLOW_CONTENT_W - FLOW_CHIP_W, y1: flowChipCy(i), side: 'r' as const }))
]

function initFlowFx() {
  const canvas = flowCanvasEl.value
  if (!canvas) return
  flowCtx = canvas.getContext('2d')
  const dpr = Math.min(2, window.devicePixelRatio || 1)
  canvas.width = FLOW_CONTENT_W * dpr
  canvas.height = FLOW_CONTENT_H * dpr
  flowCtx?.setTransform(dpr, 0, 0, dpr, 0, 0)
  flowDots = []
  flowCurves.forEach((_, ci) => {
    for (let k = 0; k < 2; k++) flowDots.push({ curve: ci, t: Math.random(), speed: 0.22 + Math.random() * 0.2 })
  })
  flowFlashes = []
}

function flowPoint(c: FlowCurve, t: number) {
  const cpx1 = c.x0 + (c.x1 - c.x0) * 0.42
  const cpx2 = c.x0 + (c.x1 - c.x0) * 0.58
  const a = 1 - t
  return {
    x: a * a * a * c.x0 + 3 * a * a * t * cpx1 + 3 * a * t * t * cpx2 + t * t * t * c.x1,
    y: a * a * a * c.y0 + 3 * a * a * t * c.y0 + 3 * a * t * t * c.y1 + t * t * t * c.y1
  }
}

function drawFlowFx(dt: number) {
  const ctx = flowCtx
  if (!ctx) return
  ctx.clearRect(0, 0, FLOW_CONTENT_W, FLOW_CONTENT_H)

  // 基础曲线
  for (const c of flowCurves) {
    ctx.beginPath()
    ctx.moveTo(c.x0, c.y0)
    ctx.bezierCurveTo(c.x0 + (c.x1 - c.x0) * 0.42, c.y0, c.x0 + (c.x1 - c.x0) * 0.58, c.y1, c.x1, c.y1)
    ctx.strokeStyle = c.side === 'l' ? 'rgba(63, 140, 255, 0.26)' : 'rgba(53, 224, 160, 0.2)'
    ctx.lineWidth = 1.4
    ctx.stroke()
  }

  // 流动光点
  ctx.globalCompositeOperation = 'lighter'
  for (const d of flowDots) {
    d.t += (d.speed * dt) / 1.1
    if (d.t >= 1) {
      d.t = 0
      const c = flowCurves[d.curve]
      flowFlashes.push({ side: c.side, y: c.side === 'l' ? c.y1 : c.y0, t: 0 })
    }
    const c = flowCurves[d.curve]
    const pos = flowPoint(c, d.t)
    const grad = ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, 7)
    const main = c.side === 'l' ? '120, 190, 255' : '110, 235, 195'
    grad.addColorStop(0, `rgba(${main}, 0.9)`)
    grad.addColorStop(1, `rgba(${main}, 0)`)
    ctx.fillStyle = grad
    ctx.beginPath()
    ctx.arc(pos.x, pos.y, 7, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.fillStyle = 'rgba(235, 248, 255, 0.95)'
    ctx.arc(pos.x, pos.y, 1.6, 0, Math.PI * 2)
    ctx.fill()
  }

  // 中台边缘闪烁
  flowFlashes = flowFlashes.filter((f) => f.t < 1)
  for (const f of flowFlashes) {
    f.t += dt * 2.4
    const alpha = Math.max(0, 0.5 * (1 - f.t))
    const x = f.side === 'l' ? flowHubLeft : flowHubRight
    ctx.beginPath()
    ctx.fillStyle = `rgba(130, 210, 255, ${alpha})`
    ctx.arc(x, f.y, 3 + f.t * 9, 0, Math.PI * 2)
    ctx.fill()
  }
  ctx.globalCompositeOperation = 'source-over'
}

/* ================= ECharts ================= */
const qualityChartEl = ref<HTMLElement | null>(null)
const distChartEl = ref<HTMLElement | null>(null)
const taskChartEl = ref<HTMLElement | null>(null)
let qualityChart: echarts.ECharts | null = null
let distChart: echarts.ECharts | null = null
let taskChart: echarts.ECharts | null = null

const AXIS_STYLE = {
  axisLabel: { color: '#8fb0d8', fontSize: 11 },
  axisLine: { lineStyle: { color: 'rgba(88, 140, 220, 0.35)' } },
  axisTick: { show: false }
}

function initCharts() {
  if (qualityChartEl.value) {
    qualityChart = echarts.init(qualityChartEl.value)
    qualityChart.setOption({
      legend: {
        top: 0, left: 4, itemWidth: 14, itemHeight: 4, icon: 'roundRect', itemGap: 14,
        textStyle: { color: '#a8c6ee', fontSize: 11 }
      },
      grid: { left: 38, right: 14, top: 32, bottom: 24 },
      xAxis: { type: 'category', boundaryGap: false, data: trendDays, ...AXIS_STYLE },
      yAxis: {
        type: 'value', min: 0, max: 100,
        axisLabel: { ...AXIS_STYLE.axisLabel, formatter: '{value}%' },
        splitLine: { lineStyle: { color: 'rgba(80, 140, 255, 0.12)' } }
      },
      series: qualitySeries.map((s) => ({
        name: s.name,
        type: 'line',
        smooth: 0.45,
        showSymbol: false,
        data: s.data,
        lineStyle: { width: 2, color: s.color },
        itemStyle: { color: s.color },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: `${s.color}1c` },
            { offset: 1, color: `${s.color}00` }
          ])
        }
      }))
    })
  }

  if (distChartEl.value) {
    distChart = echarts.init(distChartEl.value)
    distChart.setOption({
      title: {
        text: '2.44PB',
        subtext: '总量',
        left: 'center', top: '38%',
        textStyle: { color: '#eaf4ff', fontSize: 22, fontWeight: 700 },
        subtextStyle: { color: '#8fb0d8', fontSize: 12 }
      },
      series: [
        {
          type: 'pie',
          radius: ['64%', '84%'],
          center: ['50%', '50%'],
          startAngle: 90,
          label: { show: false },
          labelLine: { show: false },
          itemStyle: { borderColor: '#041024', borderWidth: 4, shadowBlur: 16, shadowColor: 'rgba(47, 123, 255, 0.35)' },
          data: typeDist.map((d) => ({ name: d.name, value: d.value, itemStyle: { color: d.color } }))
        },
        {
          type: 'pie',
          radius: ['90%', '91%'],
          center: ['50%', '50%'],
          silent: true,
          label: { show: false },
          labelLine: { show: false },
          data: [{ value: 1, itemStyle: { color: 'rgba(88, 160, 255, 0.28)' } }]
        }
      ]
    })
  }

  if (taskChartEl.value) {
    taskChart = echarts.init(taskChartEl.value)
    taskChart.setOption({
      grid: { left: 40, right: 14, top: 26, bottom: 24 },
      xAxis: { type: 'category', data: trendDays, ...AXIS_STYLE },
      yAxis: {
        type: 'value', max: 10,
        axisLabel: { ...AXIS_STYLE.axisLabel, formatter: (v: number) => `${v}K` },
        splitLine: { lineStyle: { color: 'rgba(80, 140, 255, 0.12)' } }
      },
      series: [
        {
          name: '成功任务', type: 'bar', data: taskSuccess, barWidth: 11, barGap: '60%',
          itemStyle: {
            borderRadius: [3, 3, 0, 0],
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#7cc8ff' }, { offset: 1, color: '#2f7bff' }
            ])
          }
        },
        {
          name: '失败任务', type: 'bar', data: taskFail, barWidth: 6,
          itemStyle: { borderRadius: [2, 2, 0, 0], color: '#ff5d6a' }
        }
      ]
    })
  }
}

function refreshChartTail() {
  qualitySeries.forEach((s, i) => {
    const last = s.data[s.data.length - 1]
    s.data[s.data.length - 1] = Math.round(Math.min(99.4, Math.max(50, last + (Math.random() * 1.4 - 0.7))) * 10) / 10
    qualitySeries[i] = s
  })
  taskSuccess[taskSuccess.length - 1] = Math.round(Math.min(9.6, Math.max(6.4, taskSuccess[taskSuccess.length - 1] + (Math.random() * 0.5 - 0.25))) * 10) / 10
  taskFail[taskFail.length - 1] = Math.round(Math.min(0.6, Math.max(0.1, taskFail[taskFail.length - 1] + (Math.random() * 0.08 - 0.04))) * 100) / 100
  qualityChart?.setOption({ series: qualitySeries.map((s) => ({ name: s.name, data: s.data })) })
  taskChart?.setOption({
    series: [
      { name: '成功任务', data: taskSuccess },
      { name: '失败任务', data: taskFail }
    ]
  })
}

/* ================= 生命周期 / 定时器 ================= */
let clockTimer: number | undefined
let kpiTimer: number | undefined
let alertTimer: number | undefined
let gaugeTimer: number | undefined
let chartTimer: number | undefined
let rafId = 0
let lastFrame = 0
let fxRunning = false

function kpiTick() {
  kpiBase.tasks += Math.round(3 + Math.random() * 26)
  kpiBase.calls += 0.02 + Math.random() * 0.1
  kpiBase.total += 0.0008 + Math.random() * 0.0015
  if (Math.random() < 0.15) kpiBase.sources += 1
  if (Math.random() < 0.4) kpiBase.risks = Math.min(44, Math.max(32, kpiBase.risks + (Math.random() < 0.5 ? -1 : 1)))
  kpiBase.health = Math.round((98.4 + Math.random() * 0.8) * 10) / 10
  setKpi('tasks', kpiBase.tasks)
  setKpi('calls', kpiBase.calls)
  setKpi('total', kpiBase.total)
  setKpi('sources', kpiBase.sources)
  setKpi('risks', kpiBase.risks)
  setKpi('health', kpiBase.health)
}

function frame(now: number) {
  if (!fxRunning) return
  const elapsed = (now - lastFrame) / 1000
  const dt = elapsed > 0 ? Math.min(0.05, elapsed) : 0.016
  lastFrame = now
  if (!document.hidden) {
    drawHubFx(dt, now)
    drawFlowFx(dt)
  }
  rafId = requestAnimationFrame(frame)
}

function startLoops() {
  if (fxRunning) return
  fxRunning = true
  lastFrame = performance.now()
  rafId = requestAnimationFrame(frame)
  clockTimer = window.setInterval(tickClock, 1000)
  kpiTimer = window.setInterval(kpiTick, 5000)
  alertTimer = window.setInterval(pushAlert, 7000)
  gaugeTimer = window.setInterval(driftGauges, 4000)
  chartTimer = window.setInterval(refreshChartTail, 6000)
}

function stopLoops() {
  fxRunning = false
  cancelAnimationFrame(rafId)
  ;(Object.keys(kpiRafs) as KpiKey[]).forEach((key) => {
    if (kpiRafs[key]) cancelAnimationFrame(kpiRafs[key]!)
    kpiRafs[key] = undefined
  })
  if (clockTimer) window.clearInterval(clockTimer)
  if (kpiTimer) window.clearInterval(kpiTimer)
  if (alertTimer) window.clearInterval(alertTimer)
  if (gaugeTimer) window.clearInterval(gaugeTimer)
  if (chartTimer) window.clearInterval(chartTimer)
}

onMounted(async () => {
  fitStage()
  tickClock()
  window.addEventListener('resize', fitStage)
  document.addEventListener('fullscreenchange', onFullscreenChange)
  if (screenRef.value && 'ResizeObserver' in window) {
    stageObserver = new ResizeObserver(fitStage)
    stageObserver.observe(screenRef.value)
  }

  await nextTick()
  initHubFx()
  initFlowFx()
  initCharts()

  // 布局稳定后校正一次图表尺寸（防止首帧容器尺寸为 0）
  requestAnimationFrame(() => {
    qualityChart?.resize()
    distChart?.resize()
    taskChart?.resize()
  })

  // 入场动画
  requestAnimationFrame(() => { healthMounted.value = true })
  ;(Object.keys(kpiBase) as KpiKey[]).forEach((key) => setKpi(key, kpiBase[key]))

  startLoops()
})

onActivated(() => {
  fitStage()
  qualityChart?.resize()
  distChart?.resize()
  taskChart?.resize()
  startLoops()
})
onDeactivated(stopLoops)
onBeforeUnmount(() => {
  stopLoops()
  window.removeEventListener('resize', fitStage)
  document.removeEventListener('fullscreenchange', onFullscreenChange)
  stageObserver?.disconnect()
  stageObserver = null
  qualityChart?.dispose()
  distChart?.dispose()
  taskChart?.dispose()
  qualityChart = null
  distChart = null
  taskChart = null
})
</script>

<style scoped>
.hub-screen {
  position: relative;
  height: 100vh;
  overflow: hidden;
  background:
    radial-gradient(1100px 520px at 50% -8%, rgba(24, 74, 160, 0.28), transparent 65%),
    radial-gradient(900px 500px at 50% 108%, rgba(10, 46, 110, 0.22), transparent 62%),
    linear-gradient(180deg, #010409 0%, #030b1d 52%, #010409 100%);
  font-family: Inter, 'Microsoft YaHei', 'PingFang SC', 'Segoe UI', Arial, sans-serif;
  color: #dbe9ff;
}
.font-tech {
  font-family: 'Bahnschrift', 'DIN Alternate', 'Segoe UI', Arial, sans-serif;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.5px;
}

/* ---------- 舞台 ---------- */
.hub-stage {
  position: absolute;
  left: 50%;
  top: 50%;
  transform-origin: center center;
  display: flex;
  flex-direction: column;
  padding: 0 20px 18px;
}
.stage-grid {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    repeating-linear-gradient(0deg, rgba(70, 130, 220, 0.045) 0 1px, transparent 1px 64px),
    repeating-linear-gradient(90deg, rgba(70, 130, 220, 0.045) 0 1px, transparent 1px 64px);
  mask-image: radial-gradient(1200px 700px at 50% 42%, #000 30%, transparent 82%);
  -webkit-mask-image: radial-gradient(1200px 700px at 50% 42%, #000 30%, transparent 82%);
}
.stage-glow {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(620px 300px at 50% 34%, rgba(38, 108, 220, 0.14), transparent 70%),
    linear-gradient(180deg, rgba(20, 60, 140, 0.12), transparent 22%);
}

/* ---------- 顶部 ---------- */
.hub-header {
  position: relative;
  z-index: 3;
  height: 92px;
  flex: none;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}
.hub-header::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(64, 150, 255, 0.55) 18%, rgba(130, 210, 255, 0.95) 50%, rgba(64, 150, 255, 0.55) 82%, transparent);
  filter: drop-shadow(0 0 6px rgba(64, 150, 255, 0.6));
}
.hh-left { display: flex; align-items: center; gap: 14px; min-width: 430px; }
.hh-logo { display: flex; align-items: center; gap: 10px; }
.hh-logo__mark { width: 44px; height: 44px; filter: drop-shadow(0 0 10px rgba(64, 150, 255, 0.5)); }
.hh-logo__name {
  font-size: 26px;
  font-weight: 800;
  letter-spacing: 4px;
  background: linear-gradient(180deg, #ffffff, #9cc8ff);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hh-brand-divider { width: 1px; height: 40px; background: linear-gradient(180deg, transparent, rgba(110, 170, 255, 0.6), transparent); }
.hh-brand-desc { font-size: 12px; line-height: 1.55; color: #8fb0d8; letter-spacing: 1px; }

.hh-center { position: relative; flex: 1; display: flex; align-items: center; justify-content: center; gap: 18px; }
.hh-wing {
  position: relative;
  width: 120px;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(100, 180, 255, 0.8));
}
.hh-wing--r { background: linear-gradient(270deg, transparent, rgba(100, 180, 255, 0.8)); }
.hh-wing::after {
  content: '';
  position: absolute;
  top: -3px;
  width: 8px;
  height: 8px;
  background: #7fd0ff;
  transform: rotate(45deg);
  box-shadow: 0 0 10px rgba(127, 208, 255, 0.9);
}
.hh-wing--l::after { right: -2px; }
.hh-wing--r::after { left: -2px; }
.hh-frame-wrap { filter: drop-shadow(0 6px 22px rgba(40, 120, 255, 0.4)); }
.hh-frame {
  position: relative;
  min-width: 560px;
  padding: 9px 52px 11px;
  text-align: center;
  background: linear-gradient(180deg, rgba(24, 58, 122, 0.92), rgba(7, 18, 42, 0.94));
  clip-path: polygon(0 0, 100% 0, calc(100% - 34px) 100%, 34px 100%);
}
.hh-frame::before {
  content: '';
  position: absolute;
  inset: 0;
  padding: 1.5px;
  background: linear-gradient(180deg, rgba(140, 205, 255, 0.95), rgba(50, 120, 220, 0.18) 70%, rgba(80, 160, 255, 0.5));
  clip-path: inherit;
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  mask-composite: exclude;
  pointer-events: none;
}
.hh-frame h1 {
  margin: 0;
  font-size: 29px;
  font-weight: 800;
  letter-spacing: 3px;
  background: linear-gradient(180deg, #ffffff 30%, #8fd0ff);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hh-frame p { margin: 3px 0 0; font-size: 12px; letter-spacing: 6px; color: #6fc0ff; }

.hh-right { display: flex; align-items: center; gap: 12px; min-width: 430px; justify-content: flex-end; }
.hh-clock { text-align: right; margin-right: 4px; }
.hh-clock__time { font-size: 24px; font-weight: 700; color: #eaf4ff; line-height: 1.1; }
.hh-clock__date { font-size: 12px; color: #8fb0d8; letter-spacing: 1px; }
.hh-status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  font-size: 13px;
  color: #bfe0ff;
  border: 1px solid rgba(70, 150, 255, 0.35);
  border-radius: 8px;
  background: rgba(14, 34, 72, 0.6);
}
.hh-status i {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #35e08d;
  box-shadow: 0 0 0 0 rgba(53, 224, 141, 0.6);
  animation: hub-ping 1.8s ease-out infinite;
}
.hh-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  font-size: 13px;
  color: #cfe6ff;
  border: 1px solid rgba(70, 150, 255, 0.4);
  border-radius: 8px;
  background: linear-gradient(180deg, rgba(38, 86, 170, 0.55), rgba(14, 34, 72, 0.65));
  cursor: pointer;
  transition: all 0.2s ease;
}
.hh-btn:hover { border-color: rgba(130, 200, 255, 0.8); box-shadow: 0 0 14px rgba(64, 150, 255, 0.35); color: #fff; }
@keyframes hub-ping {
  0% { box-shadow: 0 0 0 0 rgba(53, 224, 141, 0.55); }
  75%, 100% { box-shadow: 0 0 0 8px rgba(53, 224, 141, 0); }
}

/* ---------- KPI 行 ---------- */
.kpi-row {
  position: relative;
  z-index: 2;
  flex: none;
  margin-top: 10px;
  height: 116px;
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 14px;
}
.kpi-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 0 16px;
  border: 1px solid rgba(64, 138, 255, 0.22);
  border-radius: 10px;
  background: linear-gradient(160deg, rgba(12, 30, 64, 0.72), rgba(5, 14, 32, 0.8));
  box-shadow: inset 0 0 26px rgba(30, 80, 180, 0.12);
  animation: hub-rise 0.6s ease both;
  overflow: hidden;
}
.kpi-card::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(115deg, transparent 42%, rgba(120, 190, 255, 0.07) 50%, transparent 58%);
  pointer-events: none;
}
.kpi-corner { position: absolute; width: 14px; height: 14px; border: 2px solid rgba(120, 195, 255, 0.85); pointer-events: none; }
.kpi-corner--tr { top: -1px; right: -1px; border-left: 0; border-bottom: 0; border-radius: 0 8px 0 0; }
.kpi-corner--bl { bottom: -1px; left: -1px; border-right: 0; border-top: 0; border-radius: 0 0 0 8px; }
.kpi-icon {
  flex: none;
  width: 54px;
  height: 54px;
  display: grid;
  place-items: center;
  font-size: 26px;
  border-radius: 50%;
  border: 1px solid;
}
.kpi-icon--blue { color: #6fc3ff; border-color: rgba(111, 195, 255, 0.5); background: radial-gradient(circle, rgba(47, 123, 255, 0.3), rgba(10, 26, 58, 0.2)); box-shadow: 0 0 16px rgba(47, 123, 255, 0.4); }
.kpi-icon--cyan { color: #64e6d2; border-color: rgba(100, 230, 210, 0.5); background: radial-gradient(circle, rgba(47, 216, 176, 0.28), rgba(10, 26, 58, 0.2)); box-shadow: 0 0 16px rgba(47, 216, 176, 0.35); }
.kpi-icon--gold { color: #ffc94d; border-color: rgba(255, 201, 77, 0.5); background: radial-gradient(circle, rgba(255, 176, 58, 0.28), rgba(10, 26, 58, 0.2)); box-shadow: 0 0 16px rgba(255, 176, 58, 0.35); }
.kpi-icon--red { color: #ff8a93; border-color: rgba(255, 93, 106, 0.55); background: radial-gradient(circle, rgba(255, 93, 106, 0.3), rgba(10, 26, 58, 0.2)); box-shadow: 0 0 16px rgba(255, 93, 106, 0.4); }
.kpi-icon--violet { color: #b3a6ff; border-color: rgba(155, 140, 255, 0.5); background: radial-gradient(circle, rgba(140, 120, 255, 0.3), rgba(10, 26, 58, 0.2)); box-shadow: 0 0 16px rgba(140, 120, 255, 0.4); }
.kpi-icon--green { color: #5ff0a8; border-color: rgba(53, 224, 141, 0.55); background: radial-gradient(circle, rgba(53, 224, 141, 0.3), rgba(10, 26, 58, 0.2)); box-shadow: 0 0 16px rgba(53, 224, 141, 0.4); }
.kpi-meta { min-width: 0; }
.kpi-label { display: block; font-size: 14px; color: #a8c6ee; letter-spacing: 1px; }
.kpi-value { display: flex; align-items: baseline; gap: 4px; margin-top: 2px; }
.kpi-value b { font-size: 34px; font-weight: 700; color: #f2f8ff; text-shadow: 0 0 18px rgba(88, 170, 255, 0.55); line-height: 1.05; }
.kpi-suffix { font-size: 13px; color: #8fb0d8; }
.kpi-side { margin-left: auto; text-align: right; display: flex; flex-direction: column; gap: 5px; }
.kpi-delta { font-size: 15px; font-weight: 700; }
.kpi-delta.is-up { color: #35e08d; }
.kpi-delta.is-down { color: #ff5d6a; }
.kpi-foot { font-size: 11px; color: #7d9cc4; }
.kpi-verdict { font-size: 17px; font-weight: 800; color: #35e08d; text-shadow: 0 0 12px rgba(53, 224, 141, 0.5); }
@keyframes hub-rise {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ---------- 主体 ---------- */
.hub-body {
  position: relative;
  z-index: 2;
  flex: 1;
  margin-top: 12px;
  display: grid;
  grid-template-columns: 436px 1fr 436px;
  gap: 14px;
  min-height: 0;
}
.col { display: flex; flex-direction: column; gap: 13px; min-height: 0; }
.col-left .panel--health { flex: none; height: 258px; }
.col-left .panel--quality { flex: none; height: 280px; }
.col-left .panel--alerts { flex: 1; min-height: 0; }
.col-right .panel--dist { flex: none; height: 264px; }
.col-right .panel--tasks { flex: none; height: 280px; }
.col-right .panel--resource { flex: 1; min-height: 0; }
.col-center { min-height: 0; }

/* ---------- 面板通用 ---------- */
.panel {
  position: relative;
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(64, 138, 255, 0.22);
  border-radius: 10px;
  background: linear-gradient(165deg, rgba(11, 27, 58, 0.66), rgba(4, 12, 28, 0.78));
  box-shadow: inset 0 0 24px rgba(30, 80, 180, 0.1);
  padding: 12px 14px;
  min-height: 0;
  animation: hub-rise 0.6s ease both;
}
.panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 14px;
  right: 14px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(110, 185, 255, 0.5), transparent);
}
.panel-head {
  flex: none;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.panel-head h2 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 1.5px;
  color: #eaf4ff;
}
.title-bar {
  width: 4px;
  height: 15px;
  border-radius: 2px;
  background: linear-gradient(180deg, #7fd0ff, #2f7bff);
  box-shadow: 0 0 8px rgba(88, 180, 255, 0.8);
}
.panel-more {
  border: 0;
  background: none;
  font-size: 12px;
  color: #6fa8dd;
  cursor: pointer;
}
.panel-more:hover { color: #9fd0ff; }
.panel-legend { display: flex; gap: 14px; font-size: 12px; color: #a8c6ee; }
.panel-legend span { display: inline-flex; align-items: center; gap: 6px; }
.panel-legend i { width: 9px; height: 9px; border-radius: 2px; }

.live-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-left: 10px;
  padding: 2px 8px;
  font-size: 11px;
  letter-spacing: 1px;
  color: #5ff0a8;
  border: 1px solid rgba(53, 224, 141, 0.4);
  border-radius: 20px;
}
.live-badge i { width: 6px; height: 6px; border-radius: 50%; background: #35e08d; animation: hub-blink 1.2s ease infinite; }
@keyframes hub-blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.25; } }

/* ---------- 左栏：健康度 TOP5 ---------- */
.health-list { flex: 1; display: flex; flex-direction: column; justify-content: space-evenly; min-height: 0; }
.health-row__top { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.health-ico {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  font-size: 15px;
  color: #6fc3ff;
  border-radius: 7px;
  border: 1px solid rgba(80, 150, 255, 0.35);
  background: rgba(20, 48, 100, 0.45);
}
.health-name { font-size: 14px; color: #cfe3ff; }
.health-pct { margin-left: auto; font-size: 16px; font-weight: 700; color: #58c6ff; }
.health-track { height: 6px; border-radius: 4px; background: rgba(30, 60, 120, 0.5); overflow: hidden; }
.health-fill {
  display: block;
  height: 100%;
  border-radius: 4px;
  background: linear-gradient(90deg, #2f7bff, #58c6ff 70%, #a5e6ff);
  box-shadow: 0 0 10px rgba(88, 198, 255, 0.7);
  transition: width 1s cubic-bezier(0.22, 0.8, 0.3, 1);
  position: relative;
}
.health-fill::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(115deg, transparent 30%, rgba(255, 255, 255, 0.45) 50%, transparent 70%);
  animation: hub-shimmer 2.6s linear infinite;
}
@keyframes hub-shimmer {
  from { transform: translateX(-100%); }
  to { transform: translateX(100%); }
}

/* ---------- 左栏：趋势 / 告警 ---------- */
.quality-chart { flex: 1; min-height: 0; }
.task-chart { flex: 1; min-height: 0; }
.alert-list { flex: 1; min-height: 0; overflow: hidden; display: flex; flex-direction: column; justify-content: space-evenly; }
.alert-row { display: flex; align-items: center; gap: 10px; padding: 4px 0; }
.alert-ico {
  flex: none;
  width: 26px;
  height: 26px;
  display: grid;
  place-items: center;
  font-size: 15px;
  border-radius: 50%;
}
.alert-ico--red { color: #ff8a93; background: rgba(255, 93, 106, 0.14); border: 1px solid rgba(255, 93, 106, 0.45); }
.alert-ico--orange { color: #ffc94d; background: rgba(255, 176, 58, 0.14); border: 1px solid rgba(255, 176, 58, 0.45); }
.alert-ico--cyan { color: #6fd6ff; background: rgba(88, 198, 255, 0.12); border: 1px solid rgba(88, 198, 255, 0.4); }
.alert-text { flex: 1; margin: 0; font-size: 13px; color: #b9d4f2; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.alert-tag--red { color: #ff8a93; font-weight: 600; }
.alert-tag--orange { color: #ffc94d; font-weight: 600; }
.alert-tag--cyan { color: #6fd6ff; font-weight: 600; }
.alert-time { flex: none; font-size: 12px; color: #7d9cc4; }
.alert-enter-active { transition: all 0.5s ease; }
.alert-enter-from { opacity: 0; transform: translateX(-18px); }
.alert-leave-active { display: none; }

/* ---------- 中栏：中央枢纽 ---------- */
.hub-visual { position: relative; flex: none; height: 503px; overflow: hidden; }
.hub-core {
  position: absolute;
  left: 50%;
  top: 0;
  height: 503px;
  width: auto;
  transform: translateX(-50%);
  user-select: none;
  animation: hub-breathe 6s ease-in-out infinite;
}
@keyframes hub-breathe {
  0%, 100% { filter: brightness(1) drop-shadow(0 0 18px rgba(40, 110, 230, 0.18)); }
  50% { filter: brightness(1.12) drop-shadow(0 0 30px rgba(60, 140, 255, 0.32)); }
}
.hub-fx { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
.hub-vignette {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: radial-gradient(ellipse 62% 60% at 50% 48%, transparent 58%, rgba(2, 7, 18, 0.42) 86%, rgba(2, 7, 18, 0.78) 100%);
}

/* ---------- 中栏：底部两块 ---------- */
.center-bottom { flex: 1; min-height: 0; margin-top: 13px; display: grid; grid-template-columns: 556px 1fr; gap: 14px; }
.center-bottom .panel { height: 100%; }
.flow-content { position: relative; flex: 1; min-height: 0; }
.flow-canvas { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
.flow-chip {
  position: absolute;
  width: 118px;
  height: 32px;
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 0 10px;
  font-size: 12.5px;
  color: #cfe3ff;
  border: 1px solid rgba(80, 150, 255, 0.4);
  border-radius: 7px;
  background: linear-gradient(180deg, rgba(24, 56, 116, 0.75), rgba(10, 26, 56, 0.8));
  box-shadow: 0 0 10px rgba(30, 90, 200, 0.25);
  white-space: nowrap;
}
.flow-dot { width: 7px; height: 7px; border-radius: 50%; flex: none; }
.flow-dot--in { background: #4da6ff; box-shadow: 0 0 7px rgba(77, 166, 255, 0.9); }
.flow-dot--out { background: #35e0a0; box-shadow: 0 0 7px rgba(53, 224, 160, 0.9); }
.flow-hub {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 72px;
  height: 148px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: 1px solid rgba(110, 190, 255, 0.65);
  border-radius: 12px;
  background: linear-gradient(180deg, rgba(30, 74, 150, 0.85), rgba(10, 28, 62, 0.9));
  box-shadow: 0 0 22px rgba(50, 130, 255, 0.45), inset 0 0 18px rgba(70, 150, 255, 0.25);
  animation: hub-pulse-border 2.4s ease-in-out infinite;
}
@keyframes hub-pulse-border {
  0%, 100% { box-shadow: 0 0 16px rgba(50, 130, 255, 0.35), inset 0 0 14px rgba(70, 150, 255, 0.2); }
  50% { box-shadow: 0 0 30px rgba(70, 160, 255, 0.65), inset 0 0 22px rgba(90, 180, 255, 0.35); }
}
.flow-hub__ico { width: 26px; height: 26px; }
.flow-hub span {
  writing-mode: vertical-rl;
  letter-spacing: 7px;
  font-size: 13.5px;
  font-weight: 600;
  color: #eaf4ff;
}

/* ---------- 模型调用 TOP5 ---------- */
.model-list { flex: 1; min-height: 0; display: flex; flex-direction: column; justify-content: space-evenly; }
.model-row { display: flex; align-items: center; gap: 11px; }
.model-rank {
  flex: none;
  width: 24px;
  height: 24px;
  display: grid;
  place-items: center;
  font-size: 13px;
  font-weight: 700;
  color: #0a1c3c;
  border-radius: 50%;
  background: #5a7ba6;
}
.model-rank--1 { background: linear-gradient(180deg, #ffd35c, #ff9f2e); box-shadow: 0 0 10px rgba(255, 176, 58, 0.6); }
.model-rank--2 { background: linear-gradient(180deg, #7cecd0, #2fd8b0); box-shadow: 0 0 10px rgba(47, 216, 176, 0.55); }
.model-rank--3 { background: linear-gradient(180deg, #7cb8ff, #2f7bff); box-shadow: 0 0 10px rgba(47, 123, 255, 0.55); }
.model-rank--4, .model-rank--5 { color: #b9d4f2; background: rgba(70, 105, 160, 0.55); }
.model-main { flex: 1; min-width: 0; }
.model-row__top { display: flex; align-items: baseline; gap: 8px; margin-bottom: 5px; }
.model-name { font-size: 13.5px; color: #cfe3ff; }
.model-val { margin-left: auto; font-size: 11px; color: #8fb0d8; }
.model-val b { font-size: 15px; color: #eaf4ff; }
.model-delta { font-size: 12px; color: #35e08d; }
.model-track { height: 5px; border-radius: 3px; background: rgba(30, 60, 120, 0.5); overflow: hidden; }
.model-fill {
  display: block;
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, #2456d8, #4da6ff 75%, #9fd9ff);
  box-shadow: 0 0 8px rgba(77, 166, 255, 0.7);
  transition: width 1s cubic-bezier(0.22, 0.8, 0.3, 1);
}

/* ---------- 右栏：类型分布 ---------- */
.dist-content { flex: 1; min-height: 0; display: flex; align-items: center; gap: 8px; }
.dist-chart { flex: none; width: 200px; height: 200px; }
.dist-legend { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 10px; }
.dist-row { display: flex; align-items: center; gap: 10px; }
.dist-swatch { flex: none; width: 11px; height: 11px; border-radius: 3px; }
.dist-copy { min-width: 0; }
.dist-name { display: block; font-size: 13px; color: #cfe3ff; }
.dist-pct { font-size: 11px; color: #7d9cc4; }
.dist-val { margin-left: auto; font-size: 16px; font-weight: 700; color: #eaf4ff; white-space: nowrap; }
.dist-val small { font-size: 11px; color: #8fb0d8; font-weight: 400; }

/* ---------- 右栏：资源监控 ---------- */
.gauge-row { flex: 1; min-height: 0; display: grid; grid-template-columns: repeat(4, 1fr); align-items: center; }
.gauge { display: flex; flex-direction: column; align-items: center; gap: 7px; }
.gauge-ring { position: relative; width: 92px; height: 92px; }
.gauge-ring svg { width: 100%; height: 100%; transform: rotate(-90deg); }
.gauge-track { fill: none; stroke: rgba(36, 70, 130, 0.55); stroke-width: 8; }
.gauge-arc {
  fill: none;
  stroke-width: 8;
  stroke-linecap: round;
  filter: drop-shadow(0 0 5px rgba(120, 200, 255, 0.45));
  transition: stroke-dasharray 0.9s cubic-bezier(0.22, 0.8, 0.3, 1);
}
.gauge-num {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  font-size: 20px;
  font-weight: 700;
  color: #f2f8ff;
}
.gauge-num small { font-size: 11px; color: #8fb0d8; margin-left: 1px; }
.gauge-label { font-size: 12px; color: #a8c6ee; }
.res-footer {
  flex: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 9px 6px 2px;
  border-top: 1px solid rgba(64, 138, 255, 0.18);
  font-size: 12.5px;
  color: #8fb0d8;
}
.res-footer .is-ok { color: #35e08d; font-weight: 700; }
.res-nodes { color: #eaf4ff; font-size: 15px; font-weight: 700; }
</style>

<template>
  <div class="hr-cockpit">
    <!-- Header -->
    <header class="cockpit-header">
      <div class="cockpit-header__live">
        <span class="live-dot"></span>
        <span>AI 智能赋能招聘大脑 v3.5</span>
      </div>
      <div class="cockpit-header__title">
        <h1>
          <el-icon class="brain-icon"><MagicStick /></el-icon>
          <span class="title-gradient">岗位缺什么，人才库里谁最接近</span>
        </h1>
        <p>以岗位必备技能为口径，对比候选人画像，直接给出供需缺口和下一步招聘动作</p>
      </div>
      <div class="cockpit-header__actions">
        <div class="live-clock font-digits">{{ liveClock }}</div>
        <button class="refresh-btn" :class="{ 'is-spinning': refreshing }" @click="triggerDataRefresh">
          <el-icon :class="{ 'fa-spin': refreshing }"><Refresh /></el-icon>
          <span>{{ refreshing ? '刷新中' : '实时数据' }}</span>
        </button>
      </div>
    </header>

    <!-- KPI Strip -->
    <section class="kpi-strip">
      <div
        v-for="card in kpiCards"
        :key="card.key"
        class="kpi-card cockpit-kpi"
        role="button"
        tabindex="0"
        @click="goKpi(card)"
        @keydown.enter="goKpi(card)"
      >
        <div class="kpi-icon" :class="`kpi-icon--${card.tone}`">
          <el-icon><component :is="card.icon" /></el-icon>
        </div>
        <div class="kpi-meta">
          <div class="kpi-label">{{ card.label }}</div>
          <div class="kpi-value font-digits">
            <span>{{ card.value }}</span><span class="kpi-unit">{{ card.unit }}</span>
          </div>
          <div class="kpi-foot">
            <span class="kpi-foot__hint">{{ card.hint }}</span>
            <span class="kpi-foot__delta" :class="card.delta && card.delta.startsWith('↑') ? 'up' : 'down'">{{ card.delta }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Main Grid -->
    <main class="cockpit-main">
      <!-- LEFT COLUMN -->
      <section class="col col-left">
        <article class="cockpit-panel panel-demand-supply">
          <div class="panel-head">
            <h2><span class="title-bar"></span><span>技能需求与人才供给对比</span></h2>
            <span class="panel-head__hint">单位：人</span>
          </div>
          <div class="panel-body chart-body"><EChart :option="demandSupplyOption" /></div>
        </article>

        <article class="cockpit-panel panel-gap-top5">
          <div class="panel-head">
            <h2><span class="title-bar"></span><span>技能缺口 TOP5</span></h2>
            <span class="panel-head__hint">单位：人</span>
          </div>
          <div v-if="hasGapData" class="gap-circles">
            <div v-for="gap in gapTop5" :key="gap.name" class="gap-circle" :class="`gap-circle--${gap.tone}`">
              <div class="gap-circle__inner">
                <span class="gap-circle__hint">{{ gap.name }}</span>
                <span class="gap-circle__value font-digits">{{ gap.value.toLocaleString() }}</span>
              </div>
              <span class="gap-circle__caption">{{ gap.name }}</span>
            </div>
          </div>
          <div v-else class="empty-chart">暂无技能缺口数据</div>
        </article>

        <article class="cockpit-panel panel-actions">
          <div class="panel-head">
            <h2><span class="title-bar"></span><span>招聘建议动作</span></h2>
          </div>
          <div class="action-list">
            <div v-for="action in recruitmentActions" :key="action.title" class="action-row">
              <div class="action-row__lead">
                <div class="action-row__icon" :class="`action-row__icon--${action.tone}`">
                  <el-icon><component :is="action.icon" /></el-icon>
                </div>
                <div class="action-row__copy">
                  <div class="action-row__title">{{ action.title }}</div>
                  <div class="action-row__desc">{{ action.desc }}</div>
                </div>
              </div>
              <button class="action-row__btn" @click="goAction(action)">
                {{ action.cta }} &gt;
              </button>
            </div>
          </div>
        </article>
      </section>

      <!-- CENTER COLUMN -->
      <section class="col col-center">
        <article class="cockpit-panel panel-panorama">
          <div class="panorama-placeholder">
            <!-- 背景图 -->
            <img src="/hr_dashboard.png" alt="" class="panorama-placeholder__img" />
            <!-- 文字覆盖层 -->
            <div class="panorama-overlay">
              <!-- 左侧：人才供给 -->
              <div class="overlay-left">
                <div class="overlay-section-title">人才供给</div>
                <div class="talent-supply-list">
                  <div class="talent-supply-item">
                    <div class="talent-supply-info">
                      <div class="talent-supply-name">刘厉宏</div>
                      <div class="talent-supply-row">
                        <div class="talent-supply-num">4,580</div>
                        <div class="talent-supply-label">人才储备</div>
                      </div>
                    </div>
                  </div>
                  <div class="talent-supply-item">
                    <div class="talent-supply-info">
                      <div class="talent-supply-name">卫维情</div>
                      <div class="talent-supply-row">
                        <div class="talent-supply-num">621</div>
                        <div class="talent-supply-label">人才储备</div>
                      </div>
                    </div>
                  </div>
                  <div class="talent-supply-item">
                    <div class="talent-supply-info">
                      <div class="talent-supply-name">赵宇辰</div>
                      <div class="talent-supply-row">
                        <div class="talent-supply-num">890</div>
                        <div class="talent-supply-label">人才储备</div>
                      </div>
                    </div>
                  </div>
                  <div class="talent-supply-item">
                    <div class="talent-supply-info">
                      <div class="talent-supply-name">周子墨</div>
                      <div class="talent-supply-row">
                        <div class="talent-supply-num">769</div>
                        <div class="talent-supply-label">人才储备</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 中间：漏斗核心数据 -->
              <div class="overlay-center">
                <div class="funnel-title">人才流动地图</div>
                <div class="funnel-match">匹配度 87%</div>
                <div class="funnel-row">主动候选人 3,860</div>
                <div class="funnel-highlight">高匹配人才 1,089</div>
                <div class="funnel-row">供需缺口 131</div>
                <div class="funnel-big">127</div>
              </div>

              <!-- 右侧：指标 -->
              <div class="overlay-right">
                <div class="right-metric-card">
                  <div class="right-metric-main">
                    <div class="right-metric-name">冯韵皓</div>
                    <div class="right-metric-sub">内推待入职</div>
                  </div>
                  <div class="right-metric-num">586</div>
                </div>
                <div class="right-metric-card">
                  <div class="right-metric-main">
                    <div class="right-metric-name">待面试人数</div>
                    <div class="right-metric-sub">紧急需求</div>
                  </div>
                  <div class="right-metric-num">186</div>
                </div>
                <div class="right-metric-card">
                  <div class="right-metric-main">
                    <div class="right-metric-name right-metric-name--big">127</div>
                    <div class="right-metric-sub">岗位需求</div>
                  </div>
                </div>
                <div class="right-metric-card">
                  <div class="right-metric-main">
                    <div class="right-metric-name">平均响应周期</div>
                  </div>
                  <div class="right-metric-num right-metric-num--small">21天</div>
                </div>
              </div>

              <!-- 底部：行动建议 -->
              <div class="overlay-bottom">
                <div class="bottom-circle">
                  <div class="bottom-circle-label">HR行动建议</div>
                  <div class="bottom-circle-num">32%</div>
                  <div class="bottom-circle-sub">较同期提升</div>
                </div>
                <div class="bottom-advice">
                  <div class="bottom-advice-title">HR行动建议</div>
                  <div class="bottom-advice-line">优先跟进：研发工程师、销售经理、生产主管</div>
                  <div class="bottom-advice-line">建议激活：高匹配备选人才 189</div>
                </div>
                <div class="bottom-circle">
                  <div class="bottom-circle-label">岗位填充率</div>
                  <div class="bottom-circle-num">217</div>
                  <div class="bottom-circle-sub">较同期提升</div>
                </div>
              </div>
            </div>
          </div>
        </article>

        <div class="dual-charts">
          <article class="cockpit-panel">
            <div class="panel-head">
              <h3><span class="title-bar title-bar--sm"></span><span>产业需求趋势</span></h3>
              <span class="panel-head__hint">权威行业指标（{{ model.overview?.trend?.[0]?.unit || '暂无数据' }}）</span>
            </div>
            <div class="chart-body chart-body--sm"><EChart :option="industryTrendOption" /></div>
          </article>

          <article class="cockpit-panel">
            <div class="panel-head">
              <h3><span class="title-bar title-bar--sm"></span><span>技能需求当前信号</span></h3>
              <div class="panel-head__legend">
                <span><span class="legend-swatch legend-swatch--bar"></span>需求热度</span>
              </div>
            </div>
            <div class="chart-body chart-body--sm"><EChart :option="gapTrendOption" /></div>
          </article>
        </div>
      </section>

      <!-- RIGHT COLUMN -->
      <section class="col col-right">
        <article class="cockpit-panel panel-priority">
          <div class="panel-head">
            <h2><span class="title-bar"></span><span>优先联系人才</span></h2>
            <button class="text-link" @click="goPath('/hr-candidates')">查看更多</button>
          </div>
          <div class="talent-list">
            <div v-for="talent in priorityTalents" :key="talent.id" class="talent-row">
              <div class="talent-row__lead">
                <div class="talent-row__avatar" :style="{ background: avatarGradient(talent.name) }">{{ surnameChar(talent.name) }}</div>
                <div class="talent-row__meta">
                  <div class="talent-row__name">{{ talent.name }}</div>
                  <div class="talent-row__role">{{ talent.role }} · {{ talent.experience }}</div>
                  <div class="talent-row__tags">
                    <span v-for="tag in talent.tags" :key="tag">{{ tag }}</span>
                  </div>
                </div>
              </div>
              <div class="talent-row__score">
                <div class="talent-row__score-label">匹配度</div>
                <div class="talent-row__score-value font-digits">{{ talent.match ? `${talent.match}%` : '—' }}</div>
                <button class="talent-row__contact" @click="contactTalent(talent)">立即沟通</button>
              </div>
            </div>
            <div v-if="priorityTalents.length === 0" class="empty-chart">暂无候选人数据</div>
          </div>
        </article>

        <article class="cockpit-panel panel-emerging">
          <div class="panel-head">
            <h2><span class="title-bar"></span><span>新兴岗位观察</span></h2>
          </div>
          <div class="emerging-body">
            <div class="emerging-chart"><EChart :option="emergingRolesOption" /></div>
            <div class="emerging-legend">
              <div v-for="item in emergingLegend" :key="item.name" class="emerging-legend__row">
                <span><span class="legend-dot" :style="{ background: item.color }"></span>{{ item.name }}</span>
                <span class="font-digits">{{ item.count }} ({{ item.percent }}%)</span>
              </div>
            </div>
          </div>
        </article>

        <article class="cockpit-panel panel-region">
          <div class="panel-head">
            <h2><span class="title-bar"></span><span>区域人才分布</span></h2>
            <span class="panel-head__hint">单位：人</span>
          </div>
          <div class="region-canvas">
            <EChart :option="regionMapOption" class="region-chart" />
          </div>
          <div class="region-top">
            <div v-for="(city, idx) in topCities" :key="city.name" class="region-top__row">
              <span><span class="region-rank" :class="regionRankClass(idx)">TOP{{ idx + 1 }}</span> {{ city.name }}</span>
              <span class="font-digits">{{ city.count.toLocaleString() }}</span>
            </div>
          </div>
        </article>
      </section>
    </main>

    <!-- Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="modalOpen" class="info-modal" @click.self="closeModal">
          <div class="info-modal__inner cockpit-panel">
            <div class="info-modal__icon"><el-icon><Promotion /></el-icon></div>
            <h3>{{ modalTitle }}</h3>
            <p>{{ modalContent }}</p>
            <button class="info-modal__btn" @click="closeModal">确定并关闭</button>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Aim,
  Bottom,
  Briefcase,
  ChatLineRound,
  DataAnalysis,
  DataBoard,
  DataLine,
  Histogram,
  MagicStick,
  Plus,
  Promotion,
  Refresh,
  Tickets,
  Top,
  TrendCharts,
  User,
  UserFilled,
  ZoomIn
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import chinaGeo from '@/assets/china.json'
import EChart from '@/components/EChart.vue'
import { api } from '@/api/http'
import {
  readDashboardSnapshot,
  writeDashboardSnapshot,
  settledValue,
  formatSnapshotTime
} from '@/utils/dashboardCache'
import {
  aggregateByProvince,
  hotspotsFromProvinces,
  aggregateSkillDemand,
  aggregateEmergingByCategory
} from '@/utils/cityAggregate'
import { useAuthStore } from '@/stores/auth'

echarts.registerMap('china', chinaGeo as any)

const router = useRouter()
const auth = useAuthStore()

// ======== State ========
type HrModel = {
  overview: any
  candidates: any[]
  emerging: any[]
  hotspot: { rising: any[]; declining: any[]; emerging: any[] }
  graph: { nodes: any[]; edges: any[] }
  skillDemand: { names: string[]; demand: number[]; supply: number[] }
  provinces: { name: string; value: number }[]
  hotspots: { name: string; value: [number, number, number] }[]
  emergingLegend: { name: string; count: number; percent: number; color: string }[]
  gapTop5: { name: string; value: number; tone: string }[]
  topRisingSkills: string[]
}

const EMPTY_MODEL: HrModel = {
  overview: {},
  candidates: [],
  emerging: [],
  hotspot: { rising: [], declining: [], emerging: [] },
  graph: { nodes: [], edges: [] },
  skillDemand: { names: [], demand: [], supply: [] },
  provinces: [],
  hotspots: [],
  emergingLegend: [],
  gapTop5: [],
  topRisingSkills: []
}

const model = ref<HrModel>({ ...EMPTY_MODEL })
const loading = ref(true)
const refreshing = ref(false)
const updatedAt = ref('')
const cacheKey = computed(() => `hr-dashboard:${auth.user?.id || auth.user?.username || 'default'}`)

const hasOverview = computed(() => !!model.value.overview && (model.value.overview.resume_count != null || model.value.overview.job_count != null))
const hasCandidates = computed(() => model.value.candidates.length > 0)
const hasEmerging = computed(() => model.value.emerging.length > 0)
const hasRising = computed(() => model.value.hotspot.rising.length > 0)
const hasTrend = computed(() => Array.isArray(model.value.overview?.trend) && model.value.overview.trend.length > 0)
const hasSkills = computed(() => model.value.skillDemand.names.length > 0)

// ======== Derived view-model ========
const totalTalent = computed(() => {
  const v = model.value.overview?.resume_count
  return v != null ? Number(v) : 0
})

const kpiCards = computed(() => {
  const o = model.value.overview
  const num = (v: any) => (v == null ? '—' : Number(v).toLocaleString())
  return [
    { key: 'kpi1', label: '权威数据源覆盖', value: o.unit_test_coverage != null ? `${o.unit_test_coverage}%` : '—', unit: '', hint: '覆盖率', delta: o.business_case_pass_rate != null ? `↑ ${o.business_case_pass_rate}%` : '—', tone: 'cyan', icon: UserFilled, route: '/skill-graph' },
    { key: 'kpi2', label: '人才库可筛选', value: num(o.resume_count), unit: '人', hint: '当前在册简历', delta: o.job_count != null ? `岗位 ${num(o.job_count)}` : '—', tone: 'blue', icon: Aim, route: '/hr-candidates' },
    { key: 'kpi3', label: '关键技能缺口', value: num(o.skill_count), unit: '项', hint: '已建立技能实体', delta: o.evolution_event_count != null ? `事件 ${num(o.evolution_event_count)}` : '—', tone: 'sky', icon: Tickets, route: '/skill-graph' },
    { key: 'kpi4', label: '岗位画像覆盖', value: num(o.parsed_jd_count), unit: '个', hint: '已解析 JD', delta: o.jd_count != null ? `原始 ${num(o.jd_count)}` : '—', tone: 'indigo', icon: User, route: '/jobs' },
    { key: 'kpi5', label: '新兴岗位信号', value: num(o.emerging_job_count), unit: '个', hint: '能力图谱识别', delta: '实时', tone: 'teal', icon: TrendCharts, route: '/emerging-jobs' },
    { key: 'kpi6', label: '人才匹配成功率', value: o.match_accuracy != null ? String(o.match_accuracy) : '—', unit: '%', hint: '评测准确率', delta: o.benchmark_sample_count != null ? `样本 ${num(o.benchmark_sample_count)}` : '—', tone: 'cyan-bright', icon: Aim, route: '/skill-graph' }
  ]
})

const gapTop5 = computed(() => model.value.gapTop5)
const hasGapData = computed(() => gapTop5.value.length > 0)

const recruitmentActions = computed(() => {
  if (!hasRising.value) return []
  const [s1, s2, s3] = model.value.topRisingSkills
  return [
    {
      title: s1 ? `优先补充 ${s1} 人才` : '优先补充关键技能人才',
      desc: s1 ? `当前 ${s1} 人才需求旺盛，建议优先招聘` : '当前关键技能人才供给不足，建议优先招聘',
      cta: '查看人才', route: '/hr-candidates', query: s1 ? { skill: s1 } : undefined, tone: 'cyan', icon: Plus
    },
    {
      title: s2 ? `围绕 ${s2} 技能扩大人才储备` : '围绕关键技能扩大人才储备',
      desc: s2 ? `${s2} 技能需求增长明显，建议加大挖掘力度` : '关键技能需求增长明显，建议加大挖掘力度',
      cta: '查看策略', route: '/emerging-jobs', query: undefined, tone: 'blue', icon: ZoomIn
    },
    {
      title: s3 ? `完善 ${s3} 技能人才画像` : '完善关键技能人才画像',
      desc: s3 ? `建议完善 ${s3} 技能人才画像，提高匹配精度` : '建议完善技能人才画像，提高匹配精度',
      cta: '进入画像', route: '/skill-graph', query: s3 ? { keyword: s3 } : undefined, tone: 'indigo', icon: DataBoard
    }
  ]
})

const panoramaMetrics = computed(() => {
  const o = model.value.overview
  const demand = model.value.skillDemand.demand.reduce((sum, value) => sum + Number(value || 0), 0)
  const supply = Number(o.resume_count || 0)
  const gap = Math.max(demand - supply, 0)
  const ratio = supply > 0 && demand > 0 ? (supply / demand).toFixed(2) : '—'
  const fmt = (v: number) => v > 0 ? v.toLocaleString() : '—'
  return [
    { label: '供需比', value: ratio, unit: '', variant: 'ratio', sub: '供给 / 需求' },
    { label: '需求总量', value: fmt(demand), unit: '人', delta: '—', deltaTone: 'up' },
    { label: '供给总量', value: fmt(supply), unit: '人', delta: '—', deltaTone: 'up' },
    { label: '缺口总量', value: fmt(gap), unit: '人', delta: '—', deltaTone: 'down' },
    { label: '平均匹配度', value: o.match_accuracy != null ? String(o.match_accuracy) : '—', unit: '%', delta: '—', deltaTone: 'up' }
  ]
})

const priorityTalents = computed(() => {
  if (!hasCandidates.value) return []
  return model.value.candidates.slice(0, 3).map((c, i) => {
    const u = c?.user || {}
    const p = c?.profile || {}
    const name = u.display_name || u.username || `候选人${i + 1}`
    const role = p.target_role || '—'
    const years = p.years_experience
    const experience = years != null ? `${years}年经验` : '经验待评估'
    const skills = (p.skills || []).slice(0, 3)
    const id = u.id ?? c?.user_id ?? i
    return { id, name, role, experience, tags: skills, match: 0 }
  })
})

function surnameChar(name: string) {
  return name ? name.charAt(0) : '·'
}
function avatarGradient(name: string) {
  const palettes = [
    ['#0d3b44', '#22f7ff'],
    ['#1d3a70', '#6ea8ff'],
    ['#0a3d44', '#22f7ff'],
    ['#2b2b7a', '#9aa3ff'],
    ['#304b7a', '#67c8f5']
  ]
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = (hash * 31 + name.charCodeAt(i)) >>> 0
  const [c1, c2] = palettes[hash % palettes.length]
  return `linear-gradient(135deg, ${c1}, ${c2})`
}

const emergingLegend = computed(() => model.value.emergingLegend)

const topCities = computed(() => {
  if (!hasCandidates.value) return []
  const list = model.value.provinces.slice(0, 5).map((p) => ({ name: p.name.replace(/[省市区]$/, ''), count: p.value }))
  return list
})

const talentByProvince = computed(() => model.value.provinces)

const topHotspots = computed(() => model.value.hotspots)

const skillsList = computed(() => model.value.skillDemand.names)
const demandData = computed(() => model.value.skillDemand.demand)
const supplyData = computed(() => model.value.skillDemand.supply)
const hasSkillData = computed(() => skillsList.value.length > 0)

// ======== ECharts options ========
const demandSupplyOption = computed(() => {
  const names = skillsList.value
  const demand = demandData.value
  const supply = supplyData.value
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(10, 20, 42, 0.9)',
      borderColor: '#22f7ff',
      textStyle: { color: '#e2e8f0', fontSize: 11 }
    },
    legend: {
      data: ['岗位需求', '人才供给'],
      textStyle: { color: '#94a3b8', fontSize: 10 },
      right: 0, top: -5, itemWidth: 10, itemHeight: 10
    },
    grid: { top: 25, left: '2%', right: '12%', bottom: '2%', containLabel: true },
    xAxis: {
      type: 'value',
      axisLabel: { color: '#64748b', fontSize: 9, formatter: (val: number) => (val >= 1000 ? `${val / 1000}K` : val) },
      splitLine: { lineStyle: { color: 'rgba(51, 65, 85, 0.3)', type: 'dashed' } }
    },
    yAxis: {
      type: 'category',
      data: names,
      axisLabel: { color: '#cbd5e1', fontSize: 10 },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    series: [
      {
        name: '岗位需求', type: 'bar', barWidth: 6,
        data: demand,
        itemStyle: {
          color: { type: 'linear', x: 1, y: 0, x2: 0, y2: 0, colorStops: [{ offset: 0, color: '#00c9d2' }, { offset: 1, color: '#066a72' }] },
          borderRadius: [0, 4, 4, 0]
        }
      },
      {
        name: '人才供给', type: 'bar', barWidth: 6,
        data: supply,
        itemStyle: {
          color: { type: 'linear', x: 1, y: 0, x2: 0, y2: 0, colorStops: [{ offset: 0, color: '#00c9d2' }, { offset: 1, color: '#042a30' }] },
          borderRadius: [0, 4, 4, 0]
        }
      }
    ]
  }
})

const industryTrendOption = computed(() => {
  const trend = model.value.overview?.trend || []
  const labels = trend.map((t: any) => t.date || t.period || '')
  const values = trend.map((t: any) => Number(t.value ?? t.amount ?? 0))
  const maxVal = values.length ? Math.max(...values, 1) : 1
  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(10, 20, 42, 0.9)',
      borderColor: '#22f7ff',
      textStyle: { color: '#e2e8f0', fontSize: 11 }
    },
    grid: { top: 20, left: '2%', right: '4%', bottom: '5%', containLabel: true },
    xAxis: {
      type: 'category', boundaryGap: false,
      data: labels,
      axisLabel: { color: '#64748b', fontSize: 9 },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: {
      type: 'value', min: 0, max: maxVal,
      axisLabel: { color: '#64748b', fontSize: 9 },
      splitLine: { lineStyle: { color: 'rgba(51, 65, 85, 0.3)', type: 'dashed' } }
    },
    series: [{
      name: '权威行业指标', type: 'line', smooth: true, symbol: 'circle', symbolSize: 6,
      itemStyle: { color: '#22f7ff', borderWidth: 2, borderColor: '#ffffff' },
      lineStyle: { width: 3, color: '#0284c7' },
      areaStyle: {
        color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(56, 189, 248, 0.4)' }, { offset: 1, color: 'rgba(56, 189, 248, 0.0)' }] }
      },
      data: values
    }],
    graphic: values.length ? undefined : { type: 'text', left: 'center', top: 'middle', style: { text: '暂无趋势数据', fill: '#88a9c4', fontSize: 12 } }
  }
})

const gapTrendOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(10, 20, 42, 0.9)',
    borderColor: '#22f7ff',
    textStyle: { color: '#e2e8f0', fontSize: 11 }
  },
  grid: { top: 20, left: '2%', right: '8%', bottom: '5%', containLabel: true },
  xAxis: {
    type: 'category',
    data: gapTop5.value.map((item) => item.name),
    axisLabel: { color: '#64748b', fontSize: 9 },
    axisLine: { lineStyle: { color: '#334155' } }
  },
  yAxis: { type: 'value', name: '热度', min: 0, axisLabel: { color: '#64748b', fontSize: 9 }, splitLine: { lineStyle: { color: 'rgba(51, 65, 85, 0.3)', type: 'dashed' } } },
  series: [
    {
      name: '需求热度', type: 'bar', barWidth: 8,
      itemStyle: {
        color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#22f7ff' }, { offset: 1, color: '#066a72' }] },
        borderRadius: [3, 3, 0, 0]
      },
      data: gapTop5.value.map((item) => item.value)
    }
  ],
  graphic: gapTop5.value.length ? undefined : { type: 'text', left: 'center', top: 'middle', style: { text: '暂无技能需求信号', fill: '#88a9c4', fontSize: 12 } }
}))

const emergingRolesOption = computed(() => {
  const total = emergingLegend.value.reduce((s, x) => s + x.count, 0)
  const data = emergingLegend.value.map((item) => ({ value: item.count, name: item.name, itemStyle: { color: item.color } }))
  return {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(10, 20, 42, 0.9)',
      borderColor: '#066a72',
      textStyle: { color: '#e2e8f0', fontSize: 11 }
    },
    series: [{
      name: '新兴岗位',
      type: 'pie',
      radius: ['55%', '80%'], center: ['50%', '50%'], avoidLabelOverlap: false,
      label: {
        show: true, position: 'center',
        formatter: total > 0 ? `{title|${total}个}\n{sub|新兴岗位}` : `{title|—}\n{sub|暂无新兴岗位}`,
        rich: {
          title: { fontSize: 16, fontWeight: 'bold', color: '#00c9d2', fontFamily: 'Orbitron' },
          sub: { fontSize: 10, color: '#94a3b8', padding: [4, 0, 0, 0] }
        }
      },
      labelLine: { show: false },
      data
    }]
  }
})

// ======== Region Map (ECharts 中国地图) ========
const regionMapOption = computed(() => {
  const provinces = talentByProvince.value || []
  const hotspots = topHotspots.value || []
  const maxVal = provinces.length ? Math.max(...provinces.map((p: any) => p.value || 0), 1) : 1
  return {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(8, 42, 92, 0.92)',
      borderColor: 'rgba(54, 215, 255, 0.45)',
      borderWidth: 1,
      textStyle: { color: '#eefaff', fontSize: 11 },
      formatter: (params: any) => {
        if (params.seriesType === 'effectScatter') {
          return `<b style="color:#22f7ff">${params.name}</b><br/>人才：<b>${params.value?.[2] ?? 0}</b> 人`
        }
        if (params.data == null) return `${params.name}<br/><span style="color:#88a9c4">暂无数据</span>`
        return `${params.name}<br/><span style="color:#22f7ff;font-weight:700">${params.value}</span> 人`
      }
    },
    visualMap: {
      type: 'continuous',
      min: 0,
      max: maxVal,
      left: 14,
      bottom: 4, /* 下调 10px，让左侧条状图整体下移，与 TOP 列表/地图对齐 */
      text: ['高', '低'],
      textGap: 8,
      textStyle: { color: '#c2dceb', fontSize: 11, fontWeight: 600 },
      inRange: { color: ['#042a30', '#053340', '#0aa9b4', '#4feaff', '#22f7ff'] },
      calculable: false,
      itemWidth: 10,
      itemHeight: 70,
      show: provinces.length > 0
    },
    graphic: provinces.length ? undefined : { type: 'text', left: 'center', top: 'middle', style: { text: '当前样本量过小，暂无区域分布', fill: '#88a9c4', fontSize: 12 } },
    series: [
      {
        name: '人才分布',
        type: 'map',
        map: 'china',
        roam: false,
        zoom: 1.1,
        aspectScale: 0.85,
        layoutCenter: ['50%', '57%'], /* 水平居中不变，垂直下移 7%，让地图整体下沉、与左条和 TOP 卡同一水平线 */
        layoutSize: '102%',
        itemStyle: {
          areaColor: 'rgba(8, 42, 92, 0.25)',
          borderColor: 'rgba(78, 200, 255, 0.3)',
          borderWidth: 0.5
        },
        emphasis: {
          itemStyle: {
            areaColor: 'rgba(54, 215, 255, 0.35)',
            borderColor: '#22f7ff',
            borderWidth: 1.2
          },
          label: { show: true, color: '#eefaff', fontSize: 10, fontWeight: 600 }
        },
        select: { disabled: true },
        data: provinces,
        regions: [
          {
            name: '南海诸岛',
            itemStyle: { areaColor: 'transparent', borderColor: 'transparent', opacity: 0 },
            label: { show: false },
            emphasis: { disabled: true }
          }
        ]
      },
      {
        name: '热点城市',
        type: 'effectScatter',
        coordinateSystem: 'geo',
        data: hotspots,
        symbolSize: (val: any) => 5 + Math.pow(val[2] / Math.max(maxVal, 1), 0.5) * 10,
        showEffectOn: 'render',
        rippleEffect: {
          brushType: 'stroke',
          scale: 2.2,
          period: 2.4
        },
        label: {
          show: true,
          position: 'right',
          formatter: '{b}',
          color: '#eefaff',
          fontSize: 10,
          fontWeight: 700,
          textBorderColor: 'rgba(8, 42, 92, 0.9)',
          textBorderWidth: 2,
          offset: [6, 0]
        },
        itemStyle: {
          color: '#22f7ff',
          borderColor: '#bae6fd',
          borderWidth: 1,
          shadowBlur: 16,
          shadowColor: 'rgba(54, 215, 255, 0.9)'
        },
        zlevel: 2
      }
    ]
  }
})

function regionRankClass(idx: number) {
  if (idx === 0) return 'region-rank--gold'
  if (idx === 1) return 'region-rank--silver'
  if (idx === 2) return 'region-rank--bronze'
  return 'region-rank--grey'
}

// ======== Live Clock ========
const liveClock = ref('')
let clockTimer: ReturnType<typeof setInterval> | null = null
function updateClock() {
  const now = new Date()
  const pad = (n: number) => String(n).padStart(2, '0')
  liveClock.value = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`
}

// ======== Navigation ========
function goKpi(card: any) {
  if (!card?.route) return
  router.push(card.route)
}
function goAction(action: any) {
  if (!action?.route) return
  router.push({ path: action.route, query: action.query || undefined })
}
function goPath(path: string) {
  router.push(path)
}
function contactTalent(talent: any) {
  router.push({
    path: '/match-analysis',
    query: {
      candidateId: String(talent?.id ?? ''),
      name: talent?.name || ''
    }
  })
}

// ======== Modal ========
const modalOpen = ref(false)
const modalTitle = ref('操作提示')
const modalContent = ref('详情信息加载中...')
function openModal(title: string, content: string) {
  modalTitle.value = title
  modalContent.value = content
  modalOpen.value = true
}
function closeModal() {
  modalOpen.value = false
}

// ======== Refresh ========
async function refresh(force = false) {
  if (!force) {
    const cached = readDashboardSnapshot<HrModel>(cacheKey.value)
    if (cached) {
      model.value = cached.data
      updatedAt.value = cached.updatedAt
      return
    }
  }
  loading.value = !force
  refreshing.value = force
  try {
    const results = await Promise.allSettled([
      api.overview(),
      api.hrCandidates(),
      api.emergingJobs(),
      api.evolutionHotspot(),
      api.skillGraph(),
      api.jobs()
    ])
    const overview = settledValue(results[0], {}) as any
    const candidates = settledValue(results[1], []) as any[]
    const emerging = settledValue(results[2], []) as any[]
    const hotspot = settledValue(results[3], { rising: [], declining: [], emerging: [] }) as { rising: any[]; declining: any[]; emerging: any[] }
    const graph = settledValue(results[4], { nodes: [], edges: [] }) as { nodes: any[]; edges: any[] }
    const jobs = settledValue(results[5], []) as any[]

    const skillDemand = aggregateSkillDemand(jobs, candidates, graph)
    const provinces = aggregateByProvince(candidates)
    const hotspots = hotspotsFromProvinces(provinces, 5)
    const emergingLegendData = aggregateEmergingByCategory(emerging)
    const gapTop5Data = (hotspot.rising || []).slice(0, 5).map((r: any, i: number) => ({
      name: r.name || `技能${i + 1}`,
      value: Number(r.demand ?? r.heat ?? 0),
      tone: ['cyan', 'blue', 'sky', 'indigo', 'teal'][i] || 'cyan'
    }))
    const topRisingSkills = (hotspot.rising || []).slice(0, 3).map((r: any) => r.name).filter(Boolean) as string[]

    const next: HrModel = {
      overview,
      candidates,
      emerging,
      hotspot,
      graph,
      skillDemand,
      provinces,
      hotspots,
      emergingLegend: emergingLegendData,
      gapTop5: gapTop5Data,
      topRisingSkills
    }
    const snap = writeDashboardSnapshot(cacheKey.value, next)
    model.value = snap.data
    updatedAt.value = snap.updatedAt
    if (force) ElMessage.success('HR 大屏数据已更新')
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || 'HR 大屏加载失败')
  } finally {
    loading.value = false
    refreshing.value = false
    window.dispatchEvent(new Event('resize'))
  }
}

async function triggerDataRefresh() {
  await refresh(true)
}

// ======== Three.js particle wave ========
let animationFrame = 0
let resizeHandler: (() => void) | null = null
let pointerHandler: ((e: PointerEvent) => void) | null = null

onMounted(() => {
  updateClock()
  clockTimer = setInterval(updateClock, 1000)
  refresh(false)
})

onBeforeUnmount(() => {
  if (clockTimer) clearInterval(clockTimer)
  if (animationFrame) cancelAnimationFrame(animationFrame)
  if (resizeHandler) window.removeEventListener('resize', resizeHandler)
  if (pointerHandler) pointerHandler = null
})
</script>

<style scoped>
/* ============ Layout root ============ */
.hr-cockpit {
  position: relative;
  min-height: 100vh;
  padding: 18px 24px 32px;
  color: #eefaff;
  background: transparent;
}
.hr-cockpit > * { position: relative; z-index: 1; }

/* ============ Header (aligns with project .cockpit-heading) ============ */
.cockpit-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 18px;
  padding: 4px 0 14px;
  border-bottom: 1px solid rgba(78, 200, 255, 0.16);
}
.cockpit-header__live { display: none; align-items: center; gap: 8px; color: #6f91ad; font-size: 12px; flex: 0 0 auto; }
.cockpit-header__live::before { width: 22px; height: 2px; content: ""; background: #22f7ff; }
@media (min-width: 900px) { .cockpit-header__live { display: inline-flex; } }
.live-dot { width: 6px; height: 6px; border-radius: 50%; background: #22f7ff; box-shadow: 0 0 8px #22f7ff; animation: ping 1.6s cubic-bezier(0,0,.2,1) infinite; }

.cockpit-header__title { flex: 1; min-width: 0; text-align: center; }
.cockpit-header__title h1 { display: inline-flex; gap: 12px; align-items: center; margin: 0; color: #f3fcff; font-size: clamp(22px, 1.8vw, 30px); font-weight: 850; letter-spacing: .02em; }
.brain-icon { color: #22f7ff; font-size: 22px; }
.title-gradient { background: linear-gradient(90deg, #c4f4ff, #ffffff, #92e4ff); -webkit-background-clip: text; background-clip: text; color: transparent; }
.cockpit-header__title p { margin: 6px 0 0; color: #88a9c4; font-size: 13px; line-height: 1.65; }

.cockpit-header__actions { display: flex; align-items: center; gap: 10px; flex: 0 0 auto; }
.live-clock { font-size: 12px; color: #88a9c4; letter-spacing: 1px; }
.cockpit-button { display: inline-flex; align-items: center; gap: 6px; padding: 7px 12px; font-size: 12px; color: #c2eaff; background: rgba(8, 42, 92, 0.45); border: 1px solid rgba(78, 200, 255, 0.32); border-radius: 8px; cursor: pointer; transition: border-color .2s, background .2s, transform .15s; box-shadow: 0 4px 14px rgba(0, 10, 40, .25); }
.cockpit-button:hover { border-color: rgba(93, 224, 255, 0.7); background: rgba(18, 117, 194, .34); transform: translateY(-1px); }
.cockpit-button:disabled { cursor: wait; opacity: .65; transform: none; }
.cockpit-button .el-icon { color: #22f7ff; }
.cockpit-button.is-spinning .el-icon { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ============ KPI strip ============ */
.kpi-strip { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; margin-bottom: 14px; }
@media (min-width: 640px) { .kpi-strip { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 1100px) { .kpi-strip { grid-template-columns: repeat(6, 1fr); } }

.kpi-card { position: relative; overflow: hidden; min-height: 94px; padding: 14px 16px; display: flex; align-items: center; gap: 12px; cursor: pointer; transition: border-color .2s, background .2s, transform .15s; }
.kpi-card:hover { transform: translateY(-2px); }
.kpi-card:focus-visible { outline: 2px solid rgba(54, 215, 255, .65); outline-offset: 2px; }
.kpi-card::after { position: absolute; right: 14px; bottom: 0; width: 72px; height: 24px; border-top-left-radius: 14px; pointer-events: none; content: ""; background: linear-gradient(135deg, transparent 50%, rgba(54, 215, 255, .14) 50%); }
.kpi-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }
.kpi-icon--cyan { background: rgba(54, 215, 255, .14); color: #22f7ff; border: 1px solid rgba(54, 215, 255, .28); }
.kpi-icon--cyan-bright { background: rgba(54, 215, 255, .18); color: #8ff7f4; border: 1px solid rgba(54, 215, 255, .35); }
.kpi-icon--blue { background: rgba(61, 134, 255, .14); color: #6ea8ff; border: 1px solid rgba(61, 134, 255, .28); }
.kpi-icon--sky { background: rgba(56, 189, 248, .14); color: #67c8f5; border: 1px solid rgba(56, 189, 248, .28); }
.kpi-icon--indigo { background: rgba(125, 138, 255, .14); color: #9aa3ff; border: 1px solid rgba(125, 138, 255, .28); }
.kpi-icon--teal { background: rgba(56, 189, 248, .14); color: #67c8f5; border: 1px solid rgba(56, 189, 248, .28); }
.kpi-meta { min-width: 0; flex: 1; }
.kpi-label { color: #88a9c4; font-size: 11px; }
.kpi-value { color: #22f7ff; font-size: 20px; font-weight: 800; margin-top: 4px; line-height: 1.1; }
.kpi-unit { color: #88a9c4; font-size: 11px; font-weight: 500; margin-left: 3px; }
.kpi-foot { margin-top: 6px; display: flex; gap: 6px; align-items: center; font-size: 10px; color: #6f91ad; }
.kpi-foot__delta.up { color: #22f7ff; font-weight: 600; }
.kpi-foot__delta.down { color: #ff6682; font-weight: 600; }

/* ============ Main grid ============ */
.cockpit-main { display: grid; grid-template-columns: 1fr; gap: 14px; }
@media (min-width: 1100px) { .cockpit-main { grid-template-columns: minmax(320px, 3fr) minmax(560px, 6fr) minmax(320px, 3fr); } }
.col { display: flex; flex-direction: column; gap: 14px; min-width: 0; }

/* ============ Panel head (project style) ============ */
.panel-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 14px; padding: 14px 16px 10px; }
.panel-head h2, .panel-head h3 { display: flex; align-items: center; gap: 9px; margin: 0; color: #eefaff; font-size: 14px; font-weight: 800; }
.panel-head h2::before, .panel-head h3::before { width: 3px; height: 16px; border-radius: 6px; content: ""; background: #22f7ff; box-shadow: 0 0 9px rgba(54, 215, 255, 0.65); }
.panel-head__hint { color: #7394af; font-size: 11px; white-space: nowrap; }
.panel-head__legend { display: flex; gap: 10px; color: #7394af; font-size: 10px; }
.legend-swatch { display: inline-block; margin-right: 4px; }
.legend-swatch--bar { width: 8px; height: 8px; background: #3d86ff; border-radius: 1px; }
.legend-swatch--line { width: 8px; height: 2px; background: #22f7ff; border-radius: 1px; }

/* ============ Chart body ============ */
.chart-body { padding: 4px 16px 16px; min-height: 280px; flex: 1; }
.chart-body--sm { min-height: 180px; }

/* ============ Left column ============ */
.panel-demand-supply { flex: 1; display: flex; flex-direction: column; min-height: 360px; }
.panel-gap-top5 .gap-circles { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; padding: 4px 16px 18px; text-align: center; }
.gap-circle { display: flex; flex-direction: column; align-items: center; gap: 6px; }
.gap-circle__inner { width: 64px; height: 64px; border-radius: 50%; border-width: 1.5px; border-style: solid; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.gap-circle__hint { font-size: 9px; color: #88a9c4; }
.gap-circle__value { font-size: 12px; font-weight: 800; }
.gap-circle--cyan .gap-circle__inner { border-color: rgba(54, 215, 255, .55); background: rgba(54, 215, 255, .08); }
.gap-circle--cyan .gap-circle__value { color: #22f7ff; }
.gap-circle--blue .gap-circle__inner { border-color: rgba(61, 134, 255, .55); background: rgba(61, 134, 255, .08); }
.gap-circle--blue .gap-circle__value { color: #6ea8ff; }
.gap-circle--sky .gap-circle__inner { border-color: rgba(56, 189, 248, .55); background: rgba(56, 189, 248, .08); }
.gap-circle--sky .gap-circle__value { color: #67c8f5; }
.gap-circle--indigo .gap-circle__inner { border-color: rgba(125, 138, 255, .55); background: rgba(125, 138, 255, .08); }
.gap-circle--indigo .gap-circle__value { color: #9aa3ff; }
.gap-circle--teal .gap-circle__inner { border-color: rgba(56, 189, 248, .55); background: rgba(56, 189, 248, .08); }
.gap-circle--teal .gap-circle__value { color: #67c8f5; }
.gap-circle__caption { font-size: 11px; color: #88a9c4; }

.panel-actions .action-list { display: flex; flex-direction: column; gap: 8px; padding: 4px 16px 16px; }
.action-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 10px 12px; border: 1px solid rgba(76, 146, 194, .16); border-radius: 8px; background: rgba(6, 31, 64, .42); transition: border-color .2s; }
.action-row:hover { border-color: rgba(74, 207, 240, .4); }
.action-row__lead { display: flex; align-items: center; gap: 10px; min-width: 0; flex: 1; }
.action-row__icon { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 13px; flex-shrink: 0; }
.action-row__icon--cyan { background: rgba(54, 215, 255, .12); color: #22f7ff; border: 1px solid rgba(54, 215, 255, .28); }
.action-row__icon--blue { background: rgba(61, 134, 255, .12); color: #6ea8ff; border: 1px solid rgba(61, 134, 255, .28); }
.action-row__icon--indigo { background: rgba(125, 138, 255, .12); color: #9aa3ff; border: 1px solid rgba(125, 138, 255, .28); }
.action-row__title { color: #eefaff; font-size: 12px; font-weight: 700; }
.action-row__desc { color: #7394af; font-size: 10px; margin-top: 3px; }
.action-row__btn { padding: 5px 9px; font-size: 11px; color: #22f7ff; background: rgba(8, 42, 92, .55); border: 1px solid rgba(54, 215, 255, .32); border-radius: 6px; cursor: pointer; white-space: nowrap; transition: background .2s, border-color .2s; }
.action-row__btn:hover { background: rgba(18, 117, 194, .34); border-color: rgba(93, 224, 255, .55); }

/* ============ Center column ============ */
.panel-panorama { padding: 0; flex: 1; display: flex; flex-direction: column; position: relative; overflow: hidden; min-height: 440px; }
.panorama-placeholder {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0;
  overflow: hidden;
  background: linear-gradient(180deg, rgba(8, 25, 60, 0.35), rgba(4, 17, 42, 0.35));
}
.panorama-placeholder__img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}

/* 文字覆盖层 — 纯文字，无卡片背景 */
.panorama-overlay {
  position: absolute;
  inset: 0;
  z-index: 2;
  display: grid;
  grid-template-columns: 180px 1fr 180px;
  grid-template-rows: 1fr auto;
  gap: 0;
  padding: 16px 20px 12px;
  pointer-events: none;
}
.panorama-overlay > * { pointer-events: auto; }

/* 左侧人才供给 — 在 grid 中占位，内部全部 absolute 固定，不影响中间/右侧位置 */
.overlay-left {
  position: relative;
  /* 必须保留 grid 子项的空间占位，避免 middle / right 列补位 */
  grid-column: 1 / 2;
  width: 100%;
  height: 100%;
  padding: 0;
}
.overlay-section-title {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  color: #c4f4ff;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.1em;
  margin: 0;
}
.talent-supply-list {
  position: absolute;
  top: 28px;
  left: 50px;
  width: 130px;
  height: 360px;
  flex: none;
}
.talent-supply-item {
  background: transparent;
  border: none;
  padding: 0;
  margin: 0;
  position: absolute;
  left: 0;
  width: 100%;
  height: 64px;
}
.talent-supply-item:nth-child(1) { top: 0; }
.talent-supply-item:nth-child(2) { top: 96px; }
.talent-supply-item:nth-child(3) { top: 192px; }
.talent-supply-item:nth-child(4) { top: 288px; }
.talent-supply-info {
  position: absolute;
  top: 25px;
  left: 0;
  width: 100%;
  height: 100%;
}
/* 第 3 条（赵宇辰 890）单独微调 */
.talent-supply-item:nth-child(3) > .talent-supply-info {
  top: 12px;
}
/* 第 4 条（周子墨 769）单独微调 */
.talent-supply-item:nth-child(4) > .talent-supply-info {
  top: 2px;
}
.talent-supply-name {
  color: #c4f4ff;
  font-size: 15px;
  font-weight: 700;
}
.talent-supply-num {
  color: #22f7ff;
  font-size: 20px;
  font-weight: 800;
  line-height: 1.2;
}
.talent-supply-row {
  display: flex;
  align-items: baseline;
  justify-content: flex-start;
  gap: 8px;
  margin-top: 2px;
}
.talent-supply-label {
  color: #6f91ad;
  font-size: 10px;
}

/* 中间漏斗数据 — 父容器显式 relative，确保子元素 absolute 坐标系锚定在中间列自身 */
.panorama-overlay > .overlay-center {
  position: relative !important;
  display: block !important;
  width: 100%;
  height: 100%;
  padding: 0;
  grid-column: 2 / 3;
}
.panorama-overlay > .overlay-center > .funnel-title {
  position: absolute !important;
  top: 100px !important;
  left: 50%;
  transform: translateX(-50%);
}
.panorama-overlay > .overlay-center > .funnel-match {
  position: absolute !important;
  top: 120px !important;
  left: 50%;
  transform: translateX(-50%);
}

/* ===== Element 1：主动候选人 3,860（DOM 第 3 个子节点）===== */
.panorama-overlay > .overlay-center > div.funnel-row:nth-child(3) {
  position: absolute !important;
  left: 250px !important;
  top: 150px !important;
}

/* ===== Element 2：供需缺口 131（DOM 第 5 个子节点）===== */
.panorama-overlay > .overlay-center > div.funnel-row:nth-child(5) {
  position: absolute !important;
  left: 260px !important;
  top: 50px !important;
}

.panorama-overlay > .overlay-center > .funnel-highlight {
  position: absolute !important;
  top: 215px !important;
  left: 220px !important;
}
/* ===== 基础样式（颜色/字号/发光）===== */
.panorama-overlay > .overlay-center { text-align: center; }
.funnel-row {
  color: rgba(200, 235, 255, 0.85);
  font-size: 13px;
  font-weight: 500;
}
.panorama-overlay > .overlay-center > .funnel-title {
  color: #ffffff;
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 0.15em;
  text-shadow: 0 0 20px rgba(54, 215, 255, 0.4);
}
.panorama-overlay > .overlay-center > .funnel-match {
  color: #22f7ff;
  font-size: 26px;
  font-weight: 900;
  text-shadow: 0 0 16px rgba(54, 215, 255, 0.5);
}
.panorama-overlay > .overlay-center > .funnel-highlight {
  color: #ffffff;
  font-size: 20px;
  font-weight: 800;
  text-shadow: 0 0 12px rgba(54, 215, 255, 0.35);
}
.panorama-overlay > .overlay-center > .funnel-big {
  color: #22f7ff;
  font-size: 36px;
  font-weight: 900;
  text-shadow: 0 0 24px rgba(54, 215, 255, 0.6);
  position: absolute !important;
  top: 280px !important;
  left: 50%;
  transform: translateX(-50%);
}

/* 右侧指标 — 在 grid 中占位，内部 absolute 固定，避免随左列 flex 漂移 */
.overlay-right {
  position: relative;
  grid-column: 3 / 4;
  width: 100%;
  height: 100%;
  padding: 0;
}
.right-metric-card {
  position: absolute;
  left: 0;
  width: 100%;
  background: transparent;
  border: none;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  height: 60px;
}
.right-metric-card:nth-child(1) { top: 50px; }
.right-metric-card:nth-child(2) { top: 140px; }
.right-metric-card:nth-child(3) { top: 220px; }
.right-metric-card:nth-child(4) { top: 310px; }
.right-metric-name {
  color: #c4f4ff;
  font-size: 12px;
  font-weight: 700;
}
.right-metric-name--big {
  color: #22f7ff;
  font-size: 22px;
  font-weight: 900;
}
.right-metric-sub {
  color: #6f91ad;
  font-size: 10px;
  margin-top: 2px;
}
.right-metric-num {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  color: #22f7ff;
  font-size: 22px;
  font-weight: 800;
}
/* Element 1/3/6：3 个带数字的卡片把数字右移 100px */
.overlay-right > .right-metric-card:nth-child(1) > .right-metric-num,
.overlay-right > .right-metric-card:nth-child(2) > .right-metric-num,
.overlay-right > .right-metric-card:nth-child(4) > .right-metric-num {
  left: 100px;
}
.right-metric-num--small {
  font-size: 14px;
  color: #c4f4ff;
}

/* 底部行动建议 */
.overlay-bottom {
  position: relative;
  grid-column: 1 / -1;
  /* 固定占位高度，避免 flex/grid 自动分配导致内容漂移 */
  width: 100%;
  height: 100px;
  padding: 0;
  box-sizing: border-box;
}
.bottom-circle {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 90px;
  height: 90px;
  background: transparent;
  border: none;
  flex-shrink: 0;
}
/* 底部左圆圈（HR行动建议 32%）— 单独定位 */
.overlay-bottom .bottom-circle:nth-of-type(1) {
  top: -20px;
  left: 775px;
}
/* 底部右圆圈（岗位填充率 217）— 单独定位 */
.overlay-bottom .bottom-circle:nth-of-type(2),
.overlay-bottom > div:nth-child(3).bottom-circle {
  right: auto;
  left: 85px;
  top: -19px;
}
.bottom-advice {
  position: absolute;
  top: 15px;
  left: 50%;
  transform: translateX(-50%);
  width: calc(100% - 260px);
  text-align: center;
  background: transparent;
  border: none;
  padding: 6px 0;
}
.bottom-circle-label {
  color: #88a9c4;
  font-size: 10px;
  font-weight: 600;
}
.bottom-circle-num {
  color: #22f7ff;
  font-size: 20px;
  font-weight: 900;
  line-height: 1.1;
}
.bottom-circle-sub {
  color: #6f91ad;
  font-size: 9px;
}
.bottom-advice {
  flex: 1;
  text-align: center;
  background: transparent;
  border: none;
  padding: 6px 0;
}
.bottom-advice-title {
  color: #c4f4ff;
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 4px;
}
.bottom-advice-line {
  color: rgba(200, 235, 255, 0.8);
  font-size: 11px;
  line-height: 1.6;
}

.panorama-metrics--supply { position: relative; z-index: 2; margin: auto 20px 8px; display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; padding: 8px 10px; background: linear-gradient(135deg, rgba(4, 26, 58, 0.42), rgba(8, 42, 92, 0.32)); border: 1px solid rgba(78, 200, 255, 0.12); border-radius: 14px; backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); box-shadow: 0 4px 16px rgba(0, 80, 160, 0.08); }
.pano-kpi {
  position: relative;
  padding: 8px 12px 10px;
  border-radius: 12px;
  background:
    linear-gradient(180deg, rgba(30, 120, 220, 0.03), rgba(4, 26, 58, 0.16)),
    radial-gradient(circle at 50% 0%, rgba(54, 215, 255, 0.07), transparent 60%);
  border: 1px solid rgba(78, 200, 255, 0.09);
  transition: transform 220ms ease, border-color 220ms ease, box-shadow 220ms ease;
}
.pano-kpi:hover { transform: translateY(-2px); border-color: rgba(54, 215, 255, 0.26); box-shadow: 0 6px 16px rgba(54, 215, 255, 0.1); }
.pano-kpi::before {
  position: absolute; top: 0; left: 14px; right: 14px; height: 1.5px;
  content: "";
  border-radius: 99px;
  background: linear-gradient(90deg, transparent, rgba(54, 215, 255, 0.42), transparent);
  opacity: 0.7;
}
.pano-kpi__title { font-size: 10.5px; font-weight: 700; color: #89b2d6; letter-spacing: 0.02em; }
.pano-kpi__row { margin-top: 4px; }
.pano-kpi__value {
  font-size: 22px; font-weight: 900; letter-spacing: -0.01em;
  color: #e6f2ff;
  text-shadow: 0 0 10px rgba(54, 215, 255, 0.22);
}
.pano-kpi__unit {
  margin-left: 4px;
  font-size: 11.5px; font-weight: 500; color: #77a0c6;
}
.pano-kpi__delta {
  margin-top: 4px;
  display: inline-flex; align-items: center; gap: 3px;
  font-size: 10px; font-weight: 600;
  padding: 1px 7px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.14);
  border: 1px solid rgba(78, 200, 255, 0.08);
}
.pano-kpi__delta-prefix { color: #77a0c6; font-weight: 500; margin-right: 2px; }
.pano-kpi__delta.up   { color: #22f7ff; border-color: rgba(34, 211, 238, 0.18); }
.pano-kpi__delta.down { color: #fca5a5; border-color: rgba(252, 165, 165, 0.16); }
.pano-kpi__delta .el-icon { font-size: 9px; }
.pano-kpi__sub { margin-top: 4px; font-size: 10px; font-weight: 600; letter-spacing: 0.04em; }
.pano-kpi__sub--info { color: #8b9cb3; padding: 1px 2px; }

.dual-charts { display: grid; grid-template-columns: 1fr; gap: 14px; height: 350px; }
@media (min-width: 768px) { .dual-charts { grid-template-columns: 1fr 1fr; } }
.dual-charts > article { min-height: 220px; display: flex; flex-direction: column; }

/* ============ Right column ============ */
.panel-priority .talent-list { display: flex; flex-direction: column; padding: 0 0 14px; }
.talent-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 11px 16px; border-top: 1px solid rgba(78, 200, 255, .1); transition: background .2s; }
.talent-row:hover { background: rgba(15, 68, 112, .18); }
.talent-row__lead { display: flex; gap: 10px; align-items: center; min-width: 0; flex: 1; }
.talent-row__avatar { width: 36px; height: 36px; border-radius: 50%; flex-shrink: 0; display: flex; align-items: center; justify-content: center; color: #eefaff; font-size: 13px; font-weight: 700; border: 1px solid rgba(54, 215, 255, .35); box-shadow: 0 0 10px rgba(54, 215, 255, .25); }
.talent-row__name { color: #eefaff; font-size: 12px; font-weight: 700; }
.talent-row__role { color: #7394af; font-size: 10px; margin-top: 3px; }
.talent-row__tags { display: flex; gap: 4px; margin-top: 5px; flex-wrap: wrap; }
.talent-row__tags span { font-size: 9px; padding: 1px 5px; border-radius: 3px; background: rgba(8, 42, 92, .55); color: #88a9c4; border: 1px solid rgba(78, 200, 255, .15); }
.talent-row__score { text-align: right; flex-shrink: 0; }
.talent-row__score-label { color: #7394af; font-size: 10px; }
.talent-row__score-value { color: #ffb85c; font-size: 16px; font-weight: 800; }
.talent-row__contact { margin-top: 5px; padding: 3px 9px; font-size: 10px; color: #eefaff; background: rgba(54, 215, 255, .14); border: 1px solid rgba(54, 215, 255, .35); border-radius: 5px; cursor: pointer; transition: background .2s; }
.talent-row__contact:hover { background: rgba(54, 215, 255, .22); }

.text-link { background: transparent; border: 0; color: #22f7ff; font-size: 11px; cursor: pointer; padding: 0; transition: color .2s; }
.text-link:hover { color: #8ff7f4; }

.panel-emerging .emerging-body { display: grid; grid-template-columns: 5fr 7fr; gap: 8px; align-items: center; padding: 4px 16px 16px; }
.emerging-chart { position: relative; height: 150px; overflow: visible; }
.emerging-chart :deep(canvas[data-zr-dom-id]) { top: -70px !important; }
.emerging-legend { display: flex; flex-direction: column; gap: 6px; font-size: 11px; color: #c2dceb; }
.emerging-legend__row { display: flex; align-items: center; justify-content: space-between; }
.legend-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }

.panel-region { position: relative; flex: 1; display: flex; flex-direction: column; min-height: 220px; }
.region-canvas { position: relative; flex: 1; min-height: 200px; margin: 4px 16px 16px; background: rgba(2, 6, 23, .35); border: 1px solid rgba(78, 200, 255, .14); border-radius: 10px; overflow: hidden; }
.region-chart { width: 100%; height: 100%; min-height: 200px; }
.region-top { position: absolute; top: 190px; left: 70px; background: rgba(8, 42, 92, .7); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); padding: 8px 10px; border-radius: 8px; border: 1px solid rgba(78, 200, 255, .22); font-size: 10px; width: 116px; display: flex; flex-direction: column; gap: 4px; box-shadow: 0 6px 18px rgba(0, 10, 40, .35); z-index: 3; }
.region-top__row { display: flex; justify-content: space-between; align-items: center; color: #88a9c4; }
.region-top__row .font-digits { color: #22f7ff; }
.region-rank { font-weight: 700; margin-right: 4px; }
.region-rank--gold { color: #ffb85c; }
.region-rank--silver { color: #c2dceb; }
.region-rank--bronze { color: #d99450; }
.region-rank--grey { color: #6f91ad; }

/* ============ Modal ============ */
.info-modal { position: fixed; inset: 0; background: rgba(2, 6, 23, .65); backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px); z-index: 100; display: flex; align-items: center; justify-content: center; padding: 16px; }
.info-modal__inner { max-width: 420px; width: 100%; padding: 24px; text-align: center; display: flex; flex-direction: column; gap: 12px; border-color: rgba(54, 215, 255, .45) !important; }
.info-modal__icon { width: 48px; height: 48px; border-radius: 50%; background: rgba(54, 215, 255, .14); border: 1px solid rgba(54, 215, 255, .4); display: flex; align-items: center; justify-content: center; margin: 0 auto; color: #22f7ff; font-size: 20px; animation: bounce 1.4s infinite; }
.info-modal__inner h3 { color: #eefaff; font-size: 16px; font-weight: 800; margin: 0; }
.info-modal__inner p { color: #c2dceb; font-size: 12px; line-height: 1.6; margin: 0; }
.info-modal__btn { padding: 8px 22px; background: rgba(54, 215, 255, .18); color: #eefaff; font-weight: 600; font-size: 12px; border-radius: 6px; border: 1px solid rgba(54, 215, 255, .45); cursor: pointer; transition: background .2s; }
.info-modal__btn:hover { background: rgba(54, 215, 255, .28); }

.modal-enter-active, .modal-leave-active { transition: opacity .25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }

/* ============ Empty chart placeholder ============ */
.empty-chart { padding: 24px 16px; color: #7394af; font-size: 12px; text-align: center; }

/* ============ Font digit token ============ */
.font-digits { font-family: 'Orbitron', 'JetBrains Mono', 'Consolas', monospace; }

/* ============ Scrollbar (project style) ============ */
.hr-cockpit ::-webkit-scrollbar { width: 6px; height: 6px; }
.hr-cockpit ::-webkit-scrollbar-track { background: rgba(15, 23, 42, .6); }
.hr-cockpit ::-webkit-scrollbar-thumb { background: #066a72; border-radius: 3px; }
.hr-cockpit ::-webkit-scrollbar-thumb:hover { background: #2c4ea1; }

/* ============ Animations ============ */
@keyframes ping { 0%, 100% { opacity: .75; transform: scale(1); } 75%, 100% { opacity: 0; transform: scale(2.2); } }
@keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
</style>

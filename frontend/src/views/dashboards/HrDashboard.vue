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
          <div class="panorama-head">
            <h2>人才供需全景图</h2>
            <div class="panorama-total">
              <span>人才总量</span>
              <span class="font-digits">{{ totalTalent.toLocaleString() }}</span>
              <span>人</span>
            </div>
          </div>
          <div ref="threeContainer" class="panorama-canvas"></div>
          <div class="panorama-metrics panorama-metrics--supply">
            <div v-for="(m, i) in panoramaMetrics" :key="i" class="pano-kpi">
              <div class="pano-kpi__title">{{ m.label }}</div>
              <div class="pano-kpi__row">
                <div class="font-digits pano-kpi__value">
                  {{ m.value }}<span v-if="m.unit" class="pano-kpi__unit">{{ m.unit }}</span>
                </div>
              </div>
              <div v-if="m.variant === 'ratio'" class="pano-kpi__sub pano-kpi__sub--info">{{ m.sub }}</div>
              <div v-else class="pano-kpi__delta" :class="m.deltaTone">
                <span class="pano-kpi__delta-prefix">较上周</span>
                <el-icon><Top v-if="m.deltaTone === 'up'" /><Bottom v-else /></el-icon>
                <span class="font-digits">{{ m.delta }}</span>
              </div>
            </div>
          </div>
        </article>

        <div class="dual-charts">
          <article class="cockpit-panel">
            <div class="panel-head">
              <h3><span class="title-bar title-bar--sm"></span><span>产业需求趋势</span></h3>
              <span class="panel-head__hint">软件人才需求估计值(万人)</span>
            </div>
            <div class="chart-body chart-body--sm"><EChart :option="industryTrendOption" /></div>
          </article>

          <article class="cockpit-panel">
            <div class="panel-head">
              <h3><span class="title-bar title-bar--sm"></span><span>岗位缺口趋势</span></h3>
              <div class="panel-head__legend">
                <span><span class="legend-swatch legend-swatch--bar"></span>缺口数量</span>
                <span><span class="legend-swatch legend-swatch--line"></span>增减速度</span>
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
import * as THREE from 'three'
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

// ======== Mock Fallback（无真实数据时填充，保证大屏视觉完整） ========
const MOCK_TOTAL_TALENT = 6260

const MOCK_KPI = [
  { key: 'kpi1', label: '人才库低偏重覆盖', value: '107', unit: '个', hint: '覆盖率 73.5%', delta: '↑ 16', tone: 'cyan', icon: UserFilled, route: '/skill-graph' },
  { key: 'kpi2', label: '人才库可筛选', value: '6,260', unit: '人', hint: '较上期 ↑ 8.6%', delta: '↑ 8.6%', tone: 'blue', icon: Aim, route: '/hr-candidates' },
  { key: 'kpi3', label: '关键技能缺口', value: '10', unit: '项', hint: '较上期 ↑ 2', delta: '↑ 2', tone: 'sky', icon: Tickets, route: '/skill-graph' },
  { key: 'kpi4', label: '岗位画像覆盖', value: '107', unit: '个', hint: '较上期 ↑ 16', delta: '↑ 16', tone: 'indigo', icon: User, route: '/jobs' },
  { key: 'kpi5', label: '新兴岗位信号', value: '17', unit: '个', hint: '较上期 ↑ 5', delta: '↑ 5', tone: 'teal', icon: TrendCharts, route: '/emerging-jobs' },
  { key: 'kpi6', label: '人才匹配成功率', value: '68.45', unit: '%', hint: '较上期 ↑ 6.3%', delta: '↑ 6.3%', tone: 'cyan-bright', icon: Aim, route: '/skill-graph' }
]

const MOCK_GAP = [
  { name: 'Linux', value: 7129, tone: 'cyan' },
  { name: 'SQL', value: 5931, tone: 'blue' },
  { name: 'Python', value: 4667, tone: 'sky' },
  { name: '数据分析', value: 3976, tone: 'indigo' },
  { name: '安全合规', value: 2842, tone: 'teal' }
]

const MOCK_ACTIONS = [
  { title: '优先补充数据分析人才', desc: '当前数据分析人才供给不足，建议优先招聘', cta: '查看人才', route: '/hr-candidates', query: { skill: '数据分析' }, tone: 'cyan', icon: Plus },
  { title: '围绕 Linux 技能扩大人才储备', desc: 'Linux 技能缺口较大，建议加大挖掘力度', cta: '查看策略', route: '/emerging-jobs', query: undefined, tone: 'blue', icon: ZoomIn },
  { title: '完善 SQL 技能人才的画像', desc: '建议完善 SQL 技能人才画像，提高匹配精度', cta: '进入画像', route: '/skill-graph', query: { keyword: 'SQL' }, tone: 'indigo', icon: DataBoard }
]

const MOCK_PANORAMA = [
  { label: '供需比', value: '6.74', unit: '', variant: 'ratio', sub: '供给 / 需求' },
  { label: '需求总量', value: '46,521', unit: '人', delta: '8.3%', deltaTone: 'up' },
  { label: '供给总量', value: '34,267', unit: '人', delta: '7.1%', deltaTone: 'up' },
  { label: '缺口总量', value: '12,254', unit: '人', delta: '1.2%', deltaTone: 'down' },
  { label: '平均匹配度', value: '68.45', unit: '%', delta: '6.3%', deltaTone: 'up' }
]

const MOCK_TALENTS = [
  { id: 1, name: '李明宇', role: '数据分析师', experience: '5年经验', tags: ['Python', 'SQL', '数据可视化'], match: 92 },
  { id: 2, name: '张晓雨', role: '数据工程师', experience: '4年经验', tags: ['Linux', 'SQL', '数据仓库'], match: 89 },
  { id: 3, name: '王思语', role: '后端开发工程师', experience: '3年经验', tags: ['Java', 'Docker', '微服务'], match: 87 }
]

const MOCK_EMERGING = [
  { name: '人工智能工程师', count: 6, percent: 35, color: '#1e3a8a' },
  { name: '数据安全工程师', count: 4, percent: 24, color: '#1d4ed8' },
  { name: '机器学习工程师', count: 3, percent: 18, color: '#3b82f6' },
  { name: '云原生工程师', count: 2, percent: 12, color: '#60a5fa' },
  { name: '其他', count: 2, percent: 11, color: '#93c5fd' }
]

const MOCK_TOP_CITIES = [
  { name: '北京', count: 1265 }, { name: '上海', count: 1023 }, { name: '广东', count: 856 }, { name: '浙江', count: 654 }, { name: '四川', count: 521 }
]

const MOCK_PROVINCES = [
  { name: '北京市', value: 1265 }, { name: '上海市', value: 1023 }, { name: '广东省', value: 856 }, { name: '浙江省', value: 654 },
  { name: '四川省', value: 521 }, { name: '江苏省', value: 432 }, { name: '山东省', value: 398 }, { name: '湖北省', value: 312 },
  { name: '陕西省', value: 256 }, { name: '福建省', value: 198 }, { name: '安徽省', value: 176 }, { name: '河南省', value: 154 },
  { name: '湖南省', value: 132 }, { name: '辽宁省', value: 118 }, { name: '重庆市', value: 96 }, { name: '天津市', value: 82 }
]

const MOCK_HOTSPOTS = [
  { name: '北京', value: [116.4074, 39.9042, 1265] as [number, number, number] },
  { name: '上海', value: [121.4737, 31.2304, 1023] as [number, number, number] },
  { name: '广州', value: [113.2644, 23.1291, 856] as [number, number, number] },
  { name: '杭州', value: [120.1535, 30.2874, 654] as [number, number, number] },
  { name: '成都', value: [104.0657, 30.6594, 521] as [number, number, number] }
]

const MOCK_SKILLS = ['云原生', '板块管理', '机器学习', '数据可视化', 'Docker', '安全合规', 'Python', 'SQL', 'Linux', '数据分析']
const MOCK_DEMAND = [1562, 2269, 3125, 4215, 4325, 5232, 6985, 8326, 9865, 18562]
const MOCK_SUPPLY = [1100, 1800, 2400, 3100, 3400, 3900, 5200, 6100, 7200, 12400]

const MOCK_TREND_LABELS = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月']
const MOCK_TREND_VALUES = [700, 800, 900, 1000, 1150, 1300, 1500, 1800]

// 真实数据是否就绪（用于决定走真实 vs mock）
const hasOverview = computed(() => !!model.value.overview && (model.value.overview.resume_count != null || model.value.overview.job_count != null))
const hasCandidates = computed(() => model.value.candidates.length > 0)
const hasEmerging = computed(() => model.value.emerging.length > 0)
const hasRising = computed(() => model.value.hotspot.rising.length > 0)
const hasTrend = computed(() => Array.isArray(model.value.overview?.trend) && model.value.overview.trend.length > 0)
const hasSkills = computed(() => model.value.skillDemand.names.length > 0)

// ======== Derived view-model ========
const totalTalent = computed(() => {
  const v = model.value.overview?.resume_count
  return v != null ? Number(v) : MOCK_TOTAL_TALENT
})

const kpiCards = computed(() => {
  if (!hasOverview.value) return MOCK_KPI
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

const gapTop5 = computed(() => hasRising.value && model.value.gapTop5.length > 0 ? model.value.gapTop5 : MOCK_GAP)
const hasGapData = computed(() => gapTop5.value.length > 0)

const recruitmentActions = computed(() => {
  if (!hasRising.value) return MOCK_ACTIONS
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
  if (!hasOverview.value) return MOCK_PANORAMA
  const o = model.value.overview
  const demand = Number(o.job_count || 0) * 10
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
  if (!hasCandidates.value) return MOCK_TALENTS
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
    ['#14426b', '#36d7ff'],
    ['#1d3a70', '#6ea8ff'],
    ['#104d6b', '#4be3c4'],
    ['#2b2b7a', '#9aa3ff'],
    ['#304b7a', '#67c8f5']
  ]
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = (hash * 31 + name.charCodeAt(i)) >>> 0
  const [c1, c2] = palettes[hash % palettes.length]
  return `linear-gradient(135deg, ${c1}, ${c2})`
}

const emergingLegend = computed(() => hasEmerging.value && model.value.emergingLegend.length > 0 ? model.value.emergingLegend : MOCK_EMERGING)

const topCities = computed(() => {
  if (!hasCandidates.value) return MOCK_TOP_CITIES
  const list = model.value.provinces.slice(0, 5).map((p) => ({ name: p.name.replace(/[省市区]$/, ''), count: p.value }))
  return list.length ? list : MOCK_TOP_CITIES
})

const talentByProvince = computed(() => model.value.provinces.length > 0 ? model.value.provinces : MOCK_PROVINCES)

const topHotspots = computed(() => model.value.hotspots.length > 0 ? model.value.hotspots : MOCK_HOTSPOTS)

const skillsList = computed(() => hasSkills.value ? model.value.skillDemand.names : MOCK_SKILLS)
const demandData = computed(() => hasSkills.value ? model.value.skillDemand.demand : MOCK_DEMAND)
const supplyData = computed(() => hasSkills.value ? model.value.skillDemand.supply : MOCK_SUPPLY)
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
      borderColor: '#38bdf8',
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
          color: { type: 'linear', x: 1, y: 0, x2: 0, y2: 0, colorStops: [{ offset: 0, color: '#3b82f6' }, { offset: 1, color: '#1e3a8a' }] },
          borderRadius: [0, 4, 4, 0]
        }
      },
      {
        name: '人才供给', type: 'bar', barWidth: 6,
        data: supply,
        itemStyle: {
          color: { type: 'linear', x: 1, y: 0, x2: 0, y2: 0, colorStops: [{ offset: 0, color: '#06b6d4' }, { offset: 1, color: '#083344' }] },
          borderRadius: [0, 4, 4, 0]
        }
      }
    ]
  }
})

const industryTrendOption = computed(() => {
  const trend = model.value.overview?.trend || []
  const useReal = hasTrend.value
  const labels = useReal ? trend.map((t: any) => t.date || t.period || '') : MOCK_TREND_LABELS
  const values = useReal ? trend.map((t: any) => Number(t.value ?? t.amount ?? 0)) : MOCK_TREND_VALUES
  const maxVal = values.length ? Math.max(...values, 100) : 2000
  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(10, 20, 42, 0.9)',
      borderColor: '#38bdf8',
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
      name: '软件人才需求', type: 'line', smooth: true, symbol: 'circle', symbolSize: 6,
      itemStyle: { color: '#38bdf8', borderWidth: 2, borderColor: '#ffffff' },
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
    borderColor: '#38bdf8',
    textStyle: { color: '#e2e8f0', fontSize: 11 }
  },
  grid: { top: 20, left: '2%', right: '8%', bottom: '5%', containLabel: true },
  xAxis: {
    type: 'category',
    data: ['8/7', '8/8', '8/9', '8/10', '8/11', '8/12', '8/13', '8/14'],
    axisLabel: { color: '#64748b', fontSize: 9 },
    axisLine: { lineStyle: { color: '#334155' } }
  },
  yAxis: [
    { type: 'value', name: '缺口', min: 0, max: 80, axisLabel: { color: '#64748b', fontSize: 9 }, splitLine: { lineStyle: { color: 'rgba(51, 65, 85, 0.3)', type: 'dashed' } } },
    { type: 'value', name: '增速', min: -40, max: 40, axisLabel: { color: '#64748b', fontSize: 9, formatter: '{value}%' }, splitLine: { show: false } }
  ],
  series: [
    {
      name: '缺口数量', type: 'bar', barWidth: 8,
      itemStyle: {
        color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#38bdf8' }, { offset: 1, color: '#0369a1' }] },
        borderRadius: [3, 3, 0, 0]
      },
      data: [35, 42, 50, 58, 65, 70, 72, 78]
    },
    {
      name: '增减速度', type: 'line', yAxisIndex: 1, smooth: true, symbol: 'diamond', symbolSize: 6,
      itemStyle: { color: '#22d3ee' }, lineStyle: { width: 2, color: '#22d3ee' },
      data: [-10, 5, 12, 18, 24, 15, 8, 25]
    }
  ]
}))

const emergingRolesOption = computed(() => {
  const total = emergingLegend.value.reduce((s, x) => s + x.count, 0)
  const data = emergingLegend.value.map((item) => ({ value: item.count, name: item.name, itemStyle: { color: item.color } }))
  return {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(10, 20, 42, 0.9)',
      borderColor: '#1d4ed8',
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
          title: { fontSize: 16, fontWeight: 'bold', color: '#3b82f6', fontFamily: 'Orbitron' },
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
          return `<b style="color:#36d7ff">${params.name}</b><br/>人才：<b>${params.value?.[2] ?? 0}</b> 人`
        }
        if (params.data == null) return `${params.name}<br/><span style="color:#88a9c4">暂无数据</span>`
        return `${params.name}<br/><span style="color:#36d7ff;font-weight:700">${params.value}</span> 人`
      }
    },
    visualMap: {
      type: 'continuous',
      min: 0,
      max: maxVal,
      left: 14,
      bottom: 14,
      text: ['高', '低'],
      textGap: 8,
      textStyle: { color: '#c2dceb', fontSize: 11, fontWeight: 600 },
      inRange: { color: ['#061b36', '#0f3d72', '#1a66b0', '#2b96d9', '#36d7ff'] },
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
        layoutCenter: ['50%', '50%'],
        layoutSize: '102%',
        itemStyle: {
          areaColor: 'rgba(8, 42, 92, 0.25)',
          borderColor: 'rgba(78, 200, 255, 0.3)',
          borderWidth: 0.5
        },
        emphasis: {
          itemStyle: {
            areaColor: 'rgba(54, 215, 255, 0.35)',
            borderColor: '#36d7ff',
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
          color: '#36d7ff',
          borderColor: '#a5f3fc',
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
const threeContainer = ref<HTMLDivElement | null>(null)
let renderer: THREE.WebGLRenderer | null = null
let animationFrame = 0
let resizeHandler: (() => void) | null = null
let pointerHandler: ((e: PointerEvent) => void) | null = null

function initThree() {
  const container = threeContainer.value
  if (!container) return
  const width = container.clientWidth
  const height = container.clientHeight

  const scene = new THREE.Scene()
  scene.fog = new THREE.FogExp2(0x030712, 0.0018)

  const camera = new THREE.PerspectiveCamera(55, width / height, 1, 2000)
  camera.position.set(0, 220, 400)
  camera.lookAt(0, -30, 0)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(window.devicePixelRatio)
  container.appendChild(renderer.domElement)

  const amountX = 80
  const amountY = 80
  const separation = 14
  const numParticles = amountX * amountY
  const positions = new Float32Array(numParticles * 3)
  const scales = new Float32Array(numParticles)
  let i = 0, j = 0
  for (let ix = 0; ix < amountX; ix++) {
    for (let iy = 0; iy < amountY; iy++) {
      positions[i] = ix * separation - (amountX * separation) / 2
      positions[i + 1] = 0
      positions[i + 2] = iy * separation - (amountY * separation) / 2
      scales[j] = 1
      i += 3
      j++
    }
  }
  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geometry.setAttribute('scale', new THREE.BufferAttribute(scales, 1))

  const material = new THREE.PointsMaterial({
    color: 0x38bdf8, size: 3.2, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending
  })
  const particles = new THREE.Points(geometry, material)
  scene.add(particles)

  const planeGeo = new THREE.PlaneGeometry(1000, 1000, 32, 32)
  const planeMat = new THREE.MeshBasicMaterial({ color: 0x0284c7, wireframe: true, transparent: true, opacity: 0.12 })
  const wireMesh = new THREE.Mesh(planeGeo, planeMat)
  wireMesh.rotation.x = -Math.PI / 2
  wireMesh.position.y = -40
  scene.add(wireMesh)

  let count = 0
  let mouseX = 0, mouseY = 0

  pointerHandler = (event: PointerEvent) => {
    const rect = container.getBoundingClientRect()
    mouseX = (event.clientX - rect.left - width / 2) * 0.2
    mouseY = (event.clientY - rect.top - height / 2) * 0.2
  }
  container.addEventListener('pointermove', pointerHandler)

  resizeHandler = () => {
    const newWidth = container.clientWidth
    const newHeight = container.clientHeight
    camera.aspect = newWidth / newHeight
    camera.updateProjectionMatrix()
    renderer?.setSize(newWidth, newHeight)
  }
  window.addEventListener('resize', resizeHandler)

  function animate() {
    animationFrame = requestAnimationFrame(animate)
    camera.position.x += (mouseX - camera.position.x) * 0.03
    camera.position.y += (-mouseY + 220 - camera.position.y) * 0.03
    camera.lookAt(0, -20, 0)
    const buf = particles.geometry.attributes.position.array as Float32Array
    let k = 0, l = 0
    for (let ix = 0; ix < amountX; ix++) {
      for (let iy = 0; iy < amountY; iy++) {
        buf[k + 1] = Math.sin((ix + count) * 0.25) * 35 + Math.sin((iy + count) * 0.4) * 35
        k += 3
        l++
      }
    }
    particles.geometry.attributes.position.needsUpdate = true
    count += 0.04
    renderer?.render(scene, camera)
  }
  animate()
}

onMounted(() => {
  updateClock()
  clockTimer = setInterval(updateClock, 1000)
  initThree()
  refresh(false)
})

onBeforeUnmount(() => {
  if (clockTimer) clearInterval(clockTimer)
  if (animationFrame) cancelAnimationFrame(animationFrame)
  if (resizeHandler) window.removeEventListener('resize', resizeHandler)
  if (pointerHandler && threeContainer.value) threeContainer.value.removeEventListener('pointermove', pointerHandler)
  if (renderer) {
    renderer.dispose()
    renderer.forceContextLoss?.()
    renderer = null
  }
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
.cockpit-header__live::before { width: 22px; height: 2px; content: ""; background: #36d7ff; }
@media (min-width: 900px) { .cockpit-header__live { display: inline-flex; } }
.live-dot { width: 6px; height: 6px; border-radius: 50%; background: #36d7ff; box-shadow: 0 0 8px #36d7ff; animation: ping 1.6s cubic-bezier(0,0,.2,1) infinite; }

.cockpit-header__title { flex: 1; min-width: 0; text-align: center; }
.cockpit-header__title h1 { display: inline-flex; gap: 12px; align-items: center; margin: 0; color: #f3fcff; font-size: clamp(22px, 1.8vw, 30px); font-weight: 850; letter-spacing: .02em; }
.brain-icon { color: #36d7ff; font-size: 22px; }
.title-gradient { background: linear-gradient(90deg, #c4f4ff, #ffffff, #92e4ff); -webkit-background-clip: text; background-clip: text; color: transparent; }
.cockpit-header__title p { margin: 6px 0 0; color: #88a9c4; font-size: 13px; line-height: 1.65; }

.cockpit-header__actions { display: flex; align-items: center; gap: 10px; flex: 0 0 auto; }
.live-clock { font-size: 12px; color: #88a9c4; letter-spacing: 1px; }
.cockpit-button { display: inline-flex; align-items: center; gap: 6px; padding: 7px 12px; font-size: 12px; color: #c2eaff; background: rgba(8, 42, 92, 0.45); border: 1px solid rgba(78, 200, 255, 0.32); border-radius: 8px; cursor: pointer; transition: border-color .2s, background .2s, transform .15s; box-shadow: 0 4px 14px rgba(0, 10, 40, .25); }
.cockpit-button:hover { border-color: rgba(93, 224, 255, 0.7); background: rgba(18, 117, 194, .34); transform: translateY(-1px); }
.cockpit-button:disabled { cursor: wait; opacity: .65; transform: none; }
.cockpit-button .el-icon { color: #36d7ff; }
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
.kpi-icon--cyan { background: rgba(54, 215, 255, .14); color: #36d7ff; border: 1px solid rgba(54, 215, 255, .28); }
.kpi-icon--cyan-bright { background: rgba(54, 215, 255, .18); color: #67e8f9; border: 1px solid rgba(54, 215, 255, .35); }
.kpi-icon--blue { background: rgba(61, 134, 255, .14); color: #6ea8ff; border: 1px solid rgba(61, 134, 255, .28); }
.kpi-icon--sky { background: rgba(56, 189, 248, .14); color: #67c8f5; border: 1px solid rgba(56, 189, 248, .28); }
.kpi-icon--indigo { background: rgba(125, 138, 255, .14); color: #9aa3ff; border: 1px solid rgba(125, 138, 255, .28); }
.kpi-icon--teal { background: rgba(36, 215, 177, .14); color: #4be3c4; border: 1px solid rgba(36, 215, 177, .28); }
.kpi-meta { min-width: 0; flex: 1; }
.kpi-label { color: #88a9c4; font-size: 11px; }
.kpi-value { color: #36d7ff; font-size: 20px; font-weight: 800; margin-top: 4px; line-height: 1.1; }
.kpi-unit { color: #88a9c4; font-size: 11px; font-weight: 500; margin-left: 3px; }
.kpi-foot { margin-top: 6px; display: flex; gap: 6px; align-items: center; font-size: 10px; color: #6f91ad; }
.kpi-foot__delta.up { color: #24d7b1; font-weight: 600; }
.kpi-foot__delta.down { color: #ff6682; font-weight: 600; }

/* ============ Main grid ============ */
.cockpit-main { display: grid; grid-template-columns: 1fr; gap: 14px; }
@media (min-width: 1100px) { .cockpit-main { grid-template-columns: minmax(320px, 3fr) minmax(560px, 6fr) minmax(320px, 3fr); } }
.col { display: flex; flex-direction: column; gap: 14px; min-width: 0; }

/* ============ Panel head (project style) ============ */
.panel-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 14px; padding: 14px 16px 10px; }
.panel-head h2, .panel-head h3 { display: flex; align-items: center; gap: 9px; margin: 0; color: #eefaff; font-size: 14px; font-weight: 800; }
.panel-head h2::before, .panel-head h3::before { width: 3px; height: 16px; border-radius: 6px; content: ""; background: #36d7ff; box-shadow: 0 0 9px rgba(54, 215, 255, 0.65); }
.panel-head__hint { color: #7394af; font-size: 11px; white-space: nowrap; }
.panel-head__legend { display: flex; gap: 10px; color: #7394af; font-size: 10px; }
.legend-swatch { display: inline-block; margin-right: 4px; }
.legend-swatch--bar { width: 8px; height: 8px; background: #3d86ff; border-radius: 1px; }
.legend-swatch--line { width: 8px; height: 2px; background: #36d7ff; border-radius: 1px; }

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
.gap-circle--cyan .gap-circle__value { color: #36d7ff; }
.gap-circle--blue .gap-circle__inner { border-color: rgba(61, 134, 255, .55); background: rgba(61, 134, 255, .08); }
.gap-circle--blue .gap-circle__value { color: #6ea8ff; }
.gap-circle--sky .gap-circle__inner { border-color: rgba(56, 189, 248, .55); background: rgba(56, 189, 248, .08); }
.gap-circle--sky .gap-circle__value { color: #67c8f5; }
.gap-circle--indigo .gap-circle__inner { border-color: rgba(125, 138, 255, .55); background: rgba(125, 138, 255, .08); }
.gap-circle--indigo .gap-circle__value { color: #9aa3ff; }
.gap-circle--teal .gap-circle__inner { border-color: rgba(36, 215, 177, .55); background: rgba(36, 215, 177, .08); }
.gap-circle--teal .gap-circle__value { color: #4be3c4; }
.gap-circle__caption { font-size: 11px; color: #88a9c4; }

.panel-actions .action-list { display: flex; flex-direction: column; gap: 8px; padding: 4px 16px 16px; }
.action-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 10px 12px; border: 1px solid rgba(76, 146, 194, .16); border-radius: 8px; background: rgba(6, 31, 64, .42); transition: border-color .2s; }
.action-row:hover { border-color: rgba(74, 207, 240, .4); }
.action-row__lead { display: flex; align-items: center; gap: 10px; min-width: 0; flex: 1; }
.action-row__icon { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 13px; flex-shrink: 0; }
.action-row__icon--cyan { background: rgba(54, 215, 255, .12); color: #36d7ff; border: 1px solid rgba(54, 215, 255, .28); }
.action-row__icon--blue { background: rgba(61, 134, 255, .12); color: #6ea8ff; border: 1px solid rgba(61, 134, 255, .28); }
.action-row__icon--indigo { background: rgba(125, 138, 255, .12); color: #9aa3ff; border: 1px solid rgba(125, 138, 255, .28); }
.action-row__title { color: #eefaff; font-size: 12px; font-weight: 700; }
.action-row__desc { color: #7394af; font-size: 10px; margin-top: 3px; }
.action-row__btn { padding: 5px 9px; font-size: 11px; color: #36d7ff; background: rgba(8, 42, 92, .55); border: 1px solid rgba(54, 215, 255, .32); border-radius: 6px; cursor: pointer; white-space: nowrap; transition: background .2s, border-color .2s; }
.action-row__btn:hover { background: rgba(18, 117, 194, .34); border-color: rgba(93, 224, 255, .55); }

/* ============ Center column ============ */
.panel-panorama { padding: 0; flex: 1; display: flex; flex-direction: column; position: relative; overflow: hidden; min-height: 440px; }
.panorama-head { text-align: center; padding: 12px 16px 6px; }
.panorama-head h2 { display: flex; align-items: center; justify-content: center; gap: 9px; margin: 0; color: #eefaff; font-size: 14px; font-weight: 800; }
.panorama-head h2::before { width: 3px; height: 16px; border-radius: 6px; content: ""; background: #36d7ff; box-shadow: 0 0 9px rgba(54, 215, 255, 0.65); }
.panorama-total { display: inline-flex; align-items: center; gap: 8px; margin-top: 8px; padding: 4px 14px; border-radius: 999px; background: rgba(8, 42, 92, .5); border: 1px solid rgba(78, 200, 255, .28); font-size: 12px; color: #88a9c4; }
.panorama-total .font-digits { color: #36d7ff; font-size: 18px; font-weight: 800; }
.panorama-canvas { position: absolute; inset: 0; width: 100%; height: 100%; cursor: grab; z-index: 0; pointer-events: auto; }
.panorama-canvas:active { cursor: grabbing; }

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
.pano-kpi__delta.up   { color: #22d3ee; border-color: rgba(34, 211, 238, 0.18); }
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

.text-link { background: transparent; border: 0; color: #36d7ff; font-size: 11px; cursor: pointer; padding: 0; transition: color .2s; }
.text-link:hover { color: #67e8f9; }

.panel-emerging .emerging-body { display: grid; grid-template-columns: 5fr 7fr; gap: 8px; align-items: center; padding: 4px 16px 16px; }
.emerging-chart { position: relative; height: 150px; overflow: visible; }
.emerging-chart :deep(canvas[data-zr-dom-id]) { top: -70px !important; }
.emerging-legend { display: flex; flex-direction: column; gap: 6px; font-size: 11px; color: #c2dceb; }
.emerging-legend__row { display: flex; align-items: center; justify-content: space-between; }
.legend-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }

.panel-region { position: relative; flex: 1; display: flex; flex-direction: column; min-height: 220px; }
.region-canvas { position: relative; flex: 1; min-height: 200px; margin: 4px 16px 16px; background: rgba(2, 6, 23, .35); border: 1px solid rgba(78, 200, 255, .14); border-radius: 10px; overflow: hidden; }
.region-chart { width: 100%; height: 100%; min-height: 200px; }
.region-top { position: absolute; top: 180px; left: 70px; background: rgba(8, 42, 92, .7); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); padding: 8px 10px; border-radius: 8px; border: 1px solid rgba(78, 200, 255, .22); font-size: 10px; width: 116px; display: flex; flex-direction: column; gap: 4px; box-shadow: 0 6px 18px rgba(0, 10, 40, .35); z-index: 3; }
.region-top__row { display: flex; justify-content: space-between; align-items: center; color: #88a9c4; }
.region-top__row .font-digits { color: #36d7ff; }
.region-rank { font-weight: 700; margin-right: 4px; }
.region-rank--gold { color: #ffb85c; }
.region-rank--silver { color: #c2dceb; }
.region-rank--bronze { color: #d99450; }
.region-rank--grey { color: #6f91ad; }

/* ============ Modal ============ */
.info-modal { position: fixed; inset: 0; background: rgba(2, 6, 23, .65); backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px); z-index: 100; display: flex; align-items: center; justify-content: center; padding: 16px; }
.info-modal__inner { max-width: 420px; width: 100%; padding: 24px; text-align: center; display: flex; flex-direction: column; gap: 12px; border-color: rgba(54, 215, 255, .45) !important; }
.info-modal__icon { width: 48px; height: 48px; border-radius: 50%; background: rgba(54, 215, 255, .14); border: 1px solid rgba(54, 215, 255, .4); display: flex; align-items: center; justify-content: center; margin: 0 auto; color: #36d7ff; font-size: 20px; animation: bounce 1.4s infinite; }
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
.hr-cockpit ::-webkit-scrollbar-thumb { background: #1e3a8a; border-radius: 3px; }
.hr-cockpit ::-webkit-scrollbar-thumb:hover { background: #2c4ea1; }

/* ============ Animations ============ */
@keyframes ping { 0%, 100% { opacity: .75; transform: scale(1); } 75%, 100% { opacity: 0; transform: scale(2.2); } }
@keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
</style>
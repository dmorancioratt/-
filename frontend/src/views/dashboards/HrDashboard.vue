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
      <div v-for="card in kpiCards" :key="card.key" class="kpi-card glass-panel">
        <span class="corner corner-tl"></span><span class="corner corner-tr"></span>
        <span class="corner corner-bl"></span><span class="corner corner-br"></span>
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
            <span class="kpi-foot__delta" :class="card.delta.startsWith('↑') ? 'up' : 'down'">{{ card.delta }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Main Grid -->
    <main class="cockpit-main">
      <!-- LEFT COLUMN -->
      <section class="col col-left">
        <article class="glass-panel panel-demand-supply">
          <span class="corner corner-tl"></span><span class="corner corner-tr"></span>
          <span class="corner corner-bl"></span><span class="corner corner-br"></span>
          <div class="panel-head">
            <h2><span class="title-bar"></span><span>技能需求与人才供给对比</span></h2>
            <span class="panel-head__hint">单位：人</span>
          </div>
          <div class="panel-body chart-body"><EChart :option="demandSupplyOption" /></div>
        </article>

        <article class="glass-panel panel-gap-top5">
          <span class="corner corner-tl"></span><span class="corner corner-tr"></span>
          <span class="corner corner-bl"></span><span class="corner corner-br"></span>
          <div class="panel-head">
            <h2><span class="title-bar"></span><span>技能缺口 TOP5</span></h2>
            <span class="panel-head__hint">单位：人</span>
          </div>
          <div class="gap-circles">
            <div v-for="gap in gapTop5" :key="gap.name" class="gap-circle" :class="`gap-circle--${gap.tone}`">
              <div class="gap-circle__inner">
                <span class="gap-circle__hint">{{ gap.name }}</span>
                <span class="gap-circle__value font-digits">{{ gap.value.toLocaleString() }}</span>
              </div>
              <span class="gap-circle__caption">{{ gap.name }}</span>
            </div>
          </div>
        </article>

        <article class="glass-panel panel-actions">
          <span class="corner corner-tl"></span><span class="corner corner-tr"></span>
          <span class="corner corner-bl"></span><span class="corner corner-br"></span>
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
              <button class="action-row__btn" @click="openModal(action.modalTitle, action.modalContent)">
                {{ action.cta }} &gt;
              </button>
            </div>
          </div>
        </article>
      </section>

      <!-- CENTER COLUMN -->
      <section class="col col-center">
        <article class="glass-panel panel-panorama">
          <span class="corner corner-tl"></span><span class="corner corner-tr"></span>
          <span class="corner corner-bl"></span><span class="corner corner-br"></span>
          <div class="panorama-head">
            <h2>人才供需全景图</h2>
            <div class="panorama-total">
              <span>人才总量</span>
              <span class="font-digits">{{ totalTalent.toLocaleString() }}</span>
              <span>人</span>
            </div>
          </div>
          <div ref="threeContainer" class="panorama-canvas"></div>
          <div class="panorama-badges">
            <div class="badge badge--cyan"><div>高匹配人才</div><div class="badge__value font-digits">2,180 <span>人</span></div><div>占比 <b>34.8%</b></div></div>
            <div class="badge badge--blue text-right"><div>中匹配人才</div><div class="badge__value font-digits">2,960 <span>人</span></div><div>占比 <b>47.3%</b></div></div>
            <div class="badge badge--amber"><div>低匹配人才</div><div class="badge__value font-digits">1,120 <span>人</span></div><div>占比 <b>17.9%</b></div></div>
          </div>
          <div class="panorama-metrics">
            <div v-for="metric in panoramaMetrics" :key="metric.label" class="panorama-metric">
              <div class="panorama-metric__label">
                <el-icon><component :is="metric.icon" /></el-icon><span>{{ metric.label }}</span>
              </div>
              <div class="font-digits panorama-metric__value">{{ metric.value }} <span>{{ metric.unit }}</span></div>
            </div>
          </div>
        </article>

        <div class="dual-charts">
          <article class="glass-panel">
            <span class="corner corner-tl"></span><span class="corner corner-tr"></span>
            <span class="corner corner-bl"></span><span class="corner corner-br"></span>
            <div class="panel-head">
              <h3><span class="title-bar title-bar--sm"></span><span>产业需求趋势</span></h3>
              <span class="panel-head__hint">软件人才需求估计值(万人)</span>
            </div>
            <div class="chart-body chart-body--sm"><EChart :option="industryTrendOption" /></div>
          </article>

          <article class="glass-panel">
            <span class="corner corner-tl"></span><span class="corner corner-tr"></span>
            <span class="corner corner-bl"></span><span class="corner corner-br"></span>
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
        <article class="glass-panel panel-priority">
          <span class="corner corner-tl"></span><span class="corner corner-tr"></span>
          <span class="corner corner-bl"></span><span class="corner corner-br"></span>
          <div class="panel-head">
            <h2><span class="title-bar"></span><span>优先联系人才</span></h2>
            <button class="text-link" @click="openModal('查看更多人才', '正在调取全球高匹配人才库信息...')">查看更多</button>
          </div>
          <div class="talent-list">
            <div v-for="talent in priorityTalents" :key="talent.name" class="talent-row">
              <div class="talent-row__lead">
                <img :src="talent.avatar" :alt="talent.name" class="talent-row__avatar" />
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
                <div class="talent-row__score-value font-digits">{{ talent.match }}%</div>
                <button class="talent-row__contact" @click="openModal(`与${talent.name}沟通`, '正在为您发起加密即时沟通会话...')">立即沟通</button>
              </div>
            </div>
          </div>
        </article>

        <article class="glass-panel panel-emerging">
          <span class="corner corner-tl"></span><span class="corner corner-tr"></span>
          <span class="corner corner-bl"></span><span class="corner corner-br"></span>
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

        <article class="glass-panel panel-region">
          <span class="corner corner-tl"></span><span class="corner corner-tr"></span>
          <span class="corner corner-bl"></span><span class="corner corner-br"></span>
          <div class="panel-head">
            <h2><span class="title-bar"></span><span>区域人才分布</span></h2>
            <span class="panel-head__hint">单位：人</span>
          </div>
          <div class="region-canvas" v-html="regionMapSvg"></div>
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
          <div class="info-modal__inner glass-panel">
            <span class="corner corner-tl"></span><span class="corner corner-tr"></span>
            <span class="corner corner-bl"></span><span class="corner corner-br"></span>
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
import {
  Aim,
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
  TrendCharts,
  User,
  UserFilled,
  ZoomIn
} from '@element-plus/icons-vue'
import * as THREE from 'three'
import EChart from '@/components/EChart.vue'

// ======== Mock Data ========
const totalTalent = 6260

const kpiCards = [
  { key: 'kpi1', label: '人才库低偏重覆盖', value: '107', unit: '个', hint: '覆盖率 73.5%', delta: '↑ 16', tone: 'cyan', icon: UserFilled },
  { key: 'kpi2', label: '人才库可筛选', value: '6,260', unit: '人', hint: '较上期 ↑ 8.6%', delta: '↑ 8.6%', tone: 'blue', icon: Aim },
  { key: 'kpi3', label: '关键技能缺口', value: '10', unit: '项', hint: '较上期 ↑ 2', delta: '↑ 2', tone: 'sky', icon: Tickets },
  { key: 'kpi4', label: '岗位画像覆盖', value: '107', unit: '个', hint: '较上期 ↑ 16', delta: '↑ 16', tone: 'indigo', icon: User },
  { key: 'kpi5', label: '新兴岗位信号', value: '17', unit: '个', hint: '较上期 ↑ 5', delta: '↑ 5', tone: 'teal', icon: TrendCharts },
  { key: 'kpi6', label: '人才匹配成功率', value: '68.45', unit: '%', hint: '较上期 ↑ 6.3%', delta: '↑ 6.3%', tone: 'cyan-bright', icon: Aim }
]

const gapTop5 = [
  { name: 'Linux', value: 7129, tone: 'cyan' },
  { name: 'SQL', value: 5931, tone: 'blue' },
  { name: 'Python', value: 4667, tone: 'sky' },
  { name: '数据分析', value: 3976, tone: 'indigo' },
  { name: '安全合规', value: 2842, tone: 'teal' }
]

const recruitmentActions = [
  {
    title: '优先补充数据分析人才',
    desc: '当前数据分析人才供给不足，建议优先招聘',
    cta: '查看人才',
    modalTitle: '查看人才',
    modalContent: '优先补充数据分析人才：正在筛选符合条件的124名高匹配数据分析专家...',
    tone: 'cyan',
    icon: Plus
  },
  {
    title: '围绕 Linux 技能扩大人才储备',
    desc: 'Linux 技能缺口较大，建议加大挖掘力度',
    cta: '查看策略',
    modalTitle: '查看策略',
    modalContent: 'Linux技能人才储备策略：启动针对Linux内核与云计算运维方向的定向挖角计划...',
    tone: 'blue',
    icon: ZoomIn
  },
  {
    title: '完善 SQL 技能人才的画像',
    desc: '建议完善 SQL 技能人才画像，提高匹配精度',
    cta: '进入画像',
    modalTitle: '进入画像',
    modalContent: 'SQL技能人才画像配置：系统已自动根据最新业务场景更新SQL调优与架构能力模型...',
    tone: 'indigo',
    icon: DataBoard
  }
]

const panoramaMetrics = [
  { label: '活跃候选人', value: '680', unit: '人', icon: UserFilled, tone: 'cyan' },
  { label: '新入库本周', value: '156', unit: '人', icon: Plus, tone: 'blue' },
  { label: '面试中', value: '245', unit: '人', icon: ChatLineRound, tone: 'sky' },
  { label: '已入职', value: '98', unit: '人', icon: Briefcase, tone: 'teal' },
  { label: '人才流失率', value: '1.32', unit: '%', icon: DataAnalysis, tone: 'indigo' }
]

const priorityTalents = [
  { name: '李明宇', role: '数据分析师', experience: '5年经验', tags: ['Python', 'SQL', '数据可视化'], match: 92, avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80' },
  { name: '张晓雨', role: '数据工程师', experience: '4年经验', tags: ['Linux', 'SQL', '数据仓库'], match: 89, avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop&q=80' },
  { name: '王思语', role: '后端开发工程师', experience: '3年经验', tags: ['Java', 'Docker', '微服务'], match: 87, avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&auto=format&fit=crop&q=80' }
]

const emergingLegend = [
  { name: '人工智能工程师', count: 6, percent: 35, color: '#3b82f6' },
  { name: '数据安全工程师', count: 4, percent: 24, color: '#22d3ee' },
  { name: '机器学习工程师', count: 3, percent: 18, color: '#38bdf8' },
  { name: '云原生工程师', count: 2, percent: 12, color: '#14b8a6' },
  { name: '其他', count: 2, percent: 11, color: '#a855f7' }
]

const topCities = [
  { name: '北京', count: 1265 },
  { name: '上海', count: 1023 },
  { name: '深圳', count: 856 },
  { name: '杭州', count: 654 },
  { name: '成都', count: 521 }
]

// ======== ECharts options ========
const skillsList = ['云原生', '板块管理', '机器学习', '数据可视化', 'Docker', '安全合规', 'Python', 'SQL', 'Linux', '数据分析']
const demandData = [1562, 2269, 3125, 4215, 4325, 5232, 6985, 8326, 9865, 18562]
const supplyData = [1100, 1800, 2400, 3100, 3400, 3900, 5200, 6100, 7200, 12400]

const demandSupplyOption = computed(() => ({
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
    data: skillsList,
    axisLabel: { color: '#cbd5e1', fontSize: 10 },
    axisLine: { lineStyle: { color: '#334155' } }
  },
  series: [
    {
      name: '岗位需求', type: 'bar', barWidth: 6,
      data: demandData,
      itemStyle: {
        color: { type: 'linear', x: 1, y: 0, x2: 0, y2: 0, colorStops: [{ offset: 0, color: '#3b82f6' }, { offset: 1, color: '#1e3a8a' }] },
        borderRadius: [0, 4, 4, 0]
      }
    },
    {
      name: '人才供给', type: 'bar', barWidth: 6,
      data: supplyData,
      itemStyle: {
        color: { type: 'linear', x: 1, y: 0, x2: 0, y2: 0, colorStops: [{ offset: 0, color: '#06b6d4' }, { offset: 1, color: '#083344' }] },
        borderRadius: [0, 4, 4, 0]
      }
    }
  ]
}))

const industryTrendOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(10, 20, 42, 0.9)',
    borderColor: '#38bdf8',
    textStyle: { color: '#e2e8f0', fontSize: 11 }
  },
  grid: { top: 20, left: '2%', right: '4%', bottom: '5%', containLabel: true },
  xAxis: {
    type: 'category', boundaryGap: false,
    data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月'],
    axisLabel: { color: '#64748b', fontSize: 9 },
    axisLine: { lineStyle: { color: '#334155' } }
  },
  yAxis: {
    type: 'value', min: 0, max: 2000, interval: 500,
    axisLabel: { color: '#64748b', fontSize: 9 },
    splitLine: { lineStyle: { color: 'rgba(51, 65, 85, 0.3)', type: 'dashed' } }
  },
  series: [{
    name: '人才需求值', type: 'line', smooth: true, symbol: 'circle', symbolSize: 6,
    itemStyle: { color: '#38bdf8', borderWidth: 2, borderColor: '#ffffff' },
    lineStyle: { width: 3, color: '#0284c7' },
    areaStyle: {
      color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(56, 189, 248, 0.4)' }, { offset: 1, color: 'rgba(56, 189, 248, 0.0)' }] }
    },
    data: [700, 800, 900, 1000, 1150, 1300, 1500, 1800]
  }]
}))

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

const emergingRolesOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    backgroundColor: 'rgba(10, 20, 42, 0.9)',
    borderColor: '#38bdf8',
    textStyle: { color: '#e2e8f0', fontSize: 11 }
  },
  series: [{
    name: '新兴岗位', type: 'pie',
    radius: ['55%', '80%'], center: ['50%', '50%'], avoidLabelOverlap: false,
    label: {
      show: true, position: 'center',
      formatter: '{title|17个}\n{sub|新兴岗位}',
      rich: {
        title: { fontSize: 16, fontWeight: 'bold', color: '#38bdf8', fontFamily: 'Orbitron' },
        sub: { fontSize: 10, color: '#94a3b8', padding: [4, 0, 0, 0] }
      }
    },
    labelLine: { show: false },
    data: emergingLegend.map((item) => ({ value: item.count, name: item.name, itemStyle: { color: item.color } }))
  }]
}))

// ======== Region Map SVG (China stylized outline) ========
const regionMapSvg = `
<svg viewBox="0 0 500 400" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%">
  <path d="M 120 180 Q 150 140 220 130 T 320 110 T 400 120 T 440 180 T 390 280 T 300 340 T 220 320 T 150 280 T 110 220 Z"
        fill="rgba(14, 116, 144, 0.12)" stroke="rgba(56, 189, 248, 0.35)" stroke-width="1.5" stroke-dasharray="4 2"/>
  <path d="M 160 160 Q 240 140 310 160 T 360 220 T 310 300 T 210 280 T 150 220 Z"
        fill="rgba(2, 132, 199, 0.15)" stroke="rgba(56, 189, 248, 0.2)" stroke-width="1"/>
  <line x1="330" y1="170" x2="320" y2="230" stroke="rgba(56, 189, 248, 0.4)" stroke-width="1" stroke-dasharray="2 2"/>
  <line x1="320" y1="230" x2="310" y2="280" stroke="rgba(56, 189, 248, 0.4)" stroke-width="1" stroke-dasharray="2 2"/>
  <line x1="310" y1="280" x2="280" y2="240" stroke="rgba(56, 189, 248, 0.4)" stroke-width="1" stroke-dasharray="2 2"/>
  <g transform="translate(330, 170)">
    <circle r="12" fill="rgba(56, 189, 248, 0.25)" class="ping"/>
    <circle r="5" fill="#38bdf8"/>
    <circle r="2" fill="#ffffff"/>
    <text x="10" y="4" fill="#e2e8f0" font-size="11" font-weight="bold">北京</text>
  </g>
  <g transform="translate(360, 230)">
    <circle r="10" fill="rgba(56, 189, 248, 0.25)" class="ping"/>
    <circle r="4.5" fill="#38bdf8"/>
    <text x="8" y="4" fill="#cbd5e1" font-size="10">上海</text>
  </g>
  <g transform="translate(310, 290)">
    <circle r="10" fill="rgba(56, 189, 248, 0.25)" class="ping"/>
    <circle r="4.5" fill="#38bdf8"/>
    <text x="8" y="4" fill="#cbd5e1" font-size="10">深圳</text>
  </g>
  <g transform="translate(340, 245)">
    <circle r="4" fill="#0284c7"/>
    <text x="7" y="3" fill="#94a3b8" font-size="9">杭州</text>
  </g>
  <g transform="translate(240, 240)">
    <circle r="4" fill="#0284c7"/>
    <text x="-26" y="3" fill="#94a3b8" font-size="9">成都</text>
  </g>
</svg>`

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

// ======== Refresh (simulate) ========
const refreshing = ref(false)
async function triggerDataRefresh() {
  refreshing.value = true
  await new Promise((resolve) => setTimeout(resolve, 600))
  // 模拟 KPI 微抖
  const kpi2 = kpiCards.find((c) => c.key === 'kpi2')
  if (kpi2) kpi2.value = (6200 + Math.floor(Math.random() * 120)).toLocaleString()
  const kpi6 = kpiCards.find((c) => c.key === 'kpi6')
  if (kpi6) kpi6.value = (68 + Math.random() * 1.5).toFixed(2)
  window.dispatchEvent(new Event('resize'))
  refreshing.value = false
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
/* ============ Theme tokens ============ */
.hr-cockpit {
  --bg-deep: #030712;
  --cyan-300: #67e8f9;
  --cyan-400: #22d3ee;
  --cyan-500: #06b6d4;
  --cyan-700: #0e7490;
  --slate-200: #e2e8f0;
  --slate-300: #cbd5e1;
  --slate-400: #94a3b8;
  --slate-500: #64748b;
  --slate-800: #1e293b;
  --slate-900: #0f172a;
  --slate-950: #020617;

  font-family: 'Inter', system-ui, -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  color: var(--slate-200);
  background: var(--bg-deep);
  background-image:
    radial-gradient(circle at 50% 0%, rgba(14, 116, 144, .22) 0%, transparent 70%),
    radial-gradient(circle at 10% 30%, rgba(30, 58, 138, .16) 0%, transparent 50%),
    radial-gradient(circle at 90% 70%, rgba(15, 23, 42, .8) 0%, transparent 60%);
  min-height: 100vh;
  padding: 10px 14px 24px;
  overflow-x: hidden;
}

.font-digits { font-family: 'Orbitron', 'JetBrains Mono', 'Consolas', monospace; }
.text-right { text-align: right; }

/* ============ Glass panel base ============ */
.glass-panel {
  position: relative;
  background: rgba(10, 20, 42, .7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(56, 189, 248, .18);
  box-shadow: 0 8px 32px rgba(0, 0, 0, .4), inset 0 0 12px rgba(56, 189, 248, .05);
  border-radius: 8px;
  transition: border-color .3s ease, box-shadow .3s ease;
}
.glass-panel:hover {
  border-color: rgba(56, 189, 248, .35);
  box-shadow: 0 8px 32px rgba(0, 0, 0, .5), inset 0 0 16px rgba(56, 189, 248, .1);
}
.corner { position: absolute; width: 8px; height: 8px; }
.corner-tl { top: -1px; left: -1px; border-top: 2px solid #38bdf8; border-left: 2px solid #38bdf8; }
.corner-tr { top: -1px; right: -1px; border-top: 2px solid #38bdf8; border-right: 2px solid #38bdf8; }
.corner-bl { bottom: -1px; left: -1px; border-bottom: 2px solid #38bdf8; border-left: 2px solid #38bdf8; }
.corner-br { bottom: -1px; right: -1px; border-bottom: 2px solid #38bdf8; border-right: 2px solid #38bdf8; }

/* ============ Header ============ */
.cockpit-header {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  margin-bottom: 12px;
  border-bottom: 2px solid rgba(56, 189, 248, .5);
  background: linear-gradient(90deg, transparent 0%, rgba(14, 116, 144, .3) 30%, rgba(14, 116, 144, .3) 70%, transparent 100%);
  border-radius: 8px 8px 0 0;
}
.cockpit-header__live { display: none; align-items: center; gap: 6px; color: var(--cyan-300); font-size: 11px; }
@media (min-width: 768px) { .cockpit-header__live { display: flex; } }
.live-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--cyan-300); box-shadow: 0 0 8px var(--cyan-300); animation: ping 1.6s cubic-bezier(0,0,.2,1) infinite; }
.cockpit-header__title { flex: 1; text-align: center; padding: 4px 8px; }
.cockpit-header__title h1 { font-size: 18px; font-weight: 700; letter-spacing: 2px; display: flex; gap: 12px; justify-content: center; align-items: center; margin: 0; color: #fff; }
.brain-icon { color: var(--cyan-400); font-size: 22px; animation: glowPulse 3s ease-in-out infinite; }
.title-gradient { background: linear-gradient(90deg, #a5f3fc, #fff, #7dd3fc); -webkit-background-clip: text; background-clip: text; color: transparent; }
.cockpit-header__title p { font-size: 11px; color: var(--slate-400); margin: 4px 0 0; letter-spacing: 1px; }
.cockpit-header__actions { display: flex; align-items: center; gap: 12px; }
.live-clock { font-size: 12px; color: var(--cyan-300); letter-spacing: 1px; background: rgba(2, 6, 23, .8); padding: 5px 10px; border-radius: 4px; border: 1px solid rgba(8, 145, 178, .6); box-shadow: inset 0 2px 6px rgba(0,0,0,.5); }
.refresh-btn { display: flex; align-items: center; gap: 6px; padding: 5px 10px; font-size: 11px; font-weight: 500; color: var(--cyan-300); background: rgba(8, 47, 73, .7); border: 1px solid rgba(6, 182, 212, .4); border-radius: 4px; cursor: pointer; transition: background .2s, border-color .2s, transform .15s; box-shadow: 0 4px 12px rgba(8, 47, 73, .5); }
.refresh-btn:hover { background: rgba(8, 47, 73, .9); border-color: var(--cyan-400); }
.refresh-btn:active { transform: scale(.95); }
.refresh-btn .el-icon { color: var(--cyan-400); }

/* ============ KPI strip ============ */
.kpi-strip { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 12px; }
@media (min-width: 640px) { .kpi-strip { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 1024px) { .kpi-strip { grid-template-columns: repeat(6, 1fr); } }
.kpi-card { display: flex; align-items: center; justify-content: space-between; padding: 10px; min-height: 78px; }
.kpi-icon { width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0; box-shadow: 0 4px 12px rgba(0,0,0,.4); }
.kpi-icon--cyan { background: rgba(8, 47, 73, .8); border: 1px solid rgba(34, 211, 238, .4); color: var(--cyan-300); }
.kpi-icon--cyan-bright { background: rgba(8, 47, 73, .9); border: 1px solid rgba(34, 211, 238, .55); color: var(--cyan-300); }
.kpi-icon--blue { background: rgba(23, 37, 84, .8); border: 1px solid rgba(96, 165, 250, .4); color: #60a5fa; }
.kpi-icon--sky { background: rgba(12, 74, 110, .8); border: 1px solid rgba(56, 189, 248, .4); color: #38bdf8; }
.kpi-icon--indigo { background: rgba(30, 27, 75, .8); border: 1px solid rgba(129, 140, 248, .4); color: #818cf8; }
.kpi-icon--teal { background: rgba(17, 78, 73, .8); border: 1px solid rgba(45, 212, 191, .4); color: #2dd4bf; }
.kpi-meta { text-align: right; min-width: 0; }
.kpi-label { font-size: 11px; color: var(--slate-400); }
.kpi-value { font-size: 18px; font-weight: 700; color: var(--cyan-300); margin: 2px 0; }
.kpi-unit { font-size: 11px; font-weight: 400; margin-left: 2px; }
.kpi-foot { font-size: 10px; color: var(--slate-400); display: flex; gap: 6px; justify-content: flex-end; }
.kpi-foot__delta.up { color: #34d399; font-weight: 500; }
.kpi-foot__delta.down { color: #f87171; font-weight: 500; }

/* ============ Main grid ============ */
.cockpit-main { display: grid; grid-template-columns: 1fr; gap: 12px; }
@media (min-width: 1024px) { .cockpit-main { grid-template-columns: 3fr 6fr 3fr; } }
.col { display: flex; flex-direction: column; gap: 12px; }
.panel-head { display: flex; align-items: center; justify-content: space-between; padding-bottom: 6px; margin-bottom: 8px; border-bottom: 1px solid rgba(8, 145, 178, .6); }
.panel-head h2, .panel-head h3 { display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 700; color: var(--cyan-300); margin: 0; }
.title-bar { width: 4px; height: 14px; background: var(--cyan-400); border-radius: 2px; display: inline-block; }
.title-bar--sm { width: 3px; height: 12px; }
.panel-head__hint { font-size: 10px; color: var(--slate-400); }
.panel-head__legend { display: flex; gap: 10px; font-size: 9px; color: var(--slate-400); }
.legend-swatch { display: inline-block; margin-right: 4px; }
.legend-swatch--bar { width: 8px; height: 8px; background: #3b82f6; border-radius: 1px; }
.legend-swatch--line { width: 8px; height: 2px; background: var(--cyan-400); border-radius: 1px; }
.chart-body { width: 100%; min-height: 280px; flex: 1; }
.chart-body--sm { min-height: 180px; }

/* ============ Left column ============ */
.panel-demand-supply { flex: 1; display: flex; flex-direction: column; min-height: 360px; padding: 12px; }
.panel-gap-top5 { padding: 12px; }
.gap-circles { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; text-align: center; }
.gap-circle { display: flex; flex-direction: column; align-items: center; }
.gap-circle__inner { width: 56px; height: 56px; border-radius: 50%; border-width: 2px; border-style: solid; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,.4); }
.gap-circle__hint { font-size: 9px; color: var(--slate-300); }
.gap-circle__value { font-size: 11px; font-weight: 700; }
.gap-circle--cyan .gap-circle__inner { border-color: rgba(34, 211, 238, .8); background: rgba(8, 47, 73, .6); box-shadow: 0 4px 12px rgba(8, 47, 73, .7); }
.gap-circle--cyan .gap-circle__value { color: var(--cyan-300); }
.gap-circle--blue .gap-circle__inner { border-color: rgba(96, 165, 250, .8); background: rgba(23, 37, 84, .6); box-shadow: 0 4px 12px rgba(23, 37, 84, .7); }
.gap-circle--blue .gap-circle__value { color: #93c5fd; }
.gap-circle--sky .gap-circle__inner { border-color: rgba(56, 189, 248, .8); background: rgba(12, 74, 110, .6); box-shadow: 0 4px 12px rgba(12, 74, 110, .7); }
.gap-circle--sky .gap-circle__value { color: #7dd3fc; }
.gap-circle--indigo .gap-circle__inner { border-color: rgba(129, 140, 248, .8); background: rgba(30, 27, 75, .6); box-shadow: 0 4px 12px rgba(30, 27, 75, .7); }
.gap-circle--indigo .gap-circle__value { color: #a5b4fc; }
.gap-circle--teal .gap-circle__inner { border-color: rgba(45, 212, 191, .8); background: rgba(17, 78, 73, .6); box-shadow: 0 4px 12px rgba(17, 78, 73, .7); }
.gap-circle--teal .gap-circle__value { color: #5eead4; }
.gap-circle__caption { font-size: 11px; color: var(--slate-400); margin-top: 6px; }

.panel-actions { padding: 12px; }
.action-list { display: flex; flex-direction: column; gap: 8px; }
.action-row { padding: 8px 10px; border-radius: 4px; background: rgba(15, 23, 42, .6); border: 1px solid var(--slate-800); display: flex; align-items: center; justify-content: space-between; gap: 12px; transition: border-color .2s; }
.action-row:hover { border-color: rgba(6, 182, 212, .5); }
.action-row__lead { display: flex; gap: 10px; align-items: center; min-width: 0; flex: 1; }
.action-row__icon { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0; }
.action-row__icon--cyan { background: rgba(8, 47, 73, .9); border: 1px solid rgba(34, 211, 238, .35); color: var(--cyan-300); }
.action-row__icon--blue { background: rgba(23, 37, 84, .9); border: 1px solid rgba(96, 165, 250, .35); color: #60a5fa; }
.action-row__icon--indigo { background: rgba(30, 27, 75, .9); border: 1px solid rgba(129, 140, 248, .35); color: #818cf8; }
.action-row__title { font-size: 12px; font-weight: 600; color: var(--slate-200); }
.action-row__desc { font-size: 10px; color: var(--slate-400); margin-top: 2px; }
.action-row__btn { padding: 4px 8px; font-size: 11px; color: var(--cyan-300); background: rgba(8, 47, 73, .9); border: 1px solid rgba(8, 145, 178, .5); border-radius: 4px; cursor: pointer; transition: background .2s; white-space: nowrap; }
.action-row__btn:hover { background: rgba(8, 47, 73, .95); }

/* ============ Center column ============ */
.panel-panorama { padding: 12px; flex: 1; display: flex; flex-direction: column; position: relative; overflow: hidden; min-height: 440px; }
.panorama-head { text-align: center; position: relative; z-index: 2; padding-top: 4px; }
.panorama-head h2 { font-size: 16px; font-weight: 700; color: var(--cyan-300); letter-spacing: 2px; margin: 0; }
.panorama-total { display: inline-flex; align-items: center; gap: 8px; margin-top: 6px; padding: 4px 14px; border-radius: 999px; background: rgba(15, 23, 42, .8); border: 1px solid rgba(6, 182, 212, .4); backdrop-filter: blur(6px); font-size: 12px; color: var(--slate-300); }
.panorama-total .font-digits { font-size: 20px; font-weight: 700; color: var(--cyan-400); }
.panorama-canvas { position: absolute; inset: 0; width: 100%; height: 100%; cursor: grab; z-index: 1; }
.panorama-canvas:active { cursor: grabbing; }
.panorama-badges { position: absolute; inset: 12px 16px 80px; pointer-events: none; display: flex; flex-direction: column; justify-content: space-between; z-index: 3; }
.badge { padding: 8px 10px; border-radius: 6px; backdrop-filter: blur(8px); pointer-events: auto; min-width: 140px; }
.badge div:not(.badge__value) { font-size: 11px; }
.badge__value { font-size: 20px; font-weight: 700; color: #fff; margin: 2px 0; }
.badge__value span { font-size: 11px; font-weight: 400; color: var(--slate-300); }
.badge div:last-child { font-size: 10px; }
.badge div:last-child b { font-weight: 700; }
.badge--cyan { background: rgba(14, 165, 233, .12); border: 1px solid rgba(56, 189, 248, .4); box-shadow: 0 0 18px rgba(14, 165, 233, .25); }
.badge--cyan div:first-child { color: var(--cyan-300); }
.badge--cyan div:last-child { color: #a5f3fc; }
.badge--blue { background: rgba(59, 130, 246, .12); border: 1px solid rgba(96, 165, 250, .4); box-shadow: 0 0 18px rgba(59, 130, 246, .25); }
.badge--blue div:first-child { color: #93c5fd; }
.badge--blue div:last-child { color: #bfdbfe; }
.badge--amber { background: rgba(245, 158, 11, .12); border: 1px solid rgba(251, 191, 36, .4); box-shadow: 0 0 18px rgba(245, 158, 11, .25); align-self: flex-start; }
.badge--amber div:first-child { color: #fcd34d; }
.badge--amber div:last-child { color: #fde68a; }
.panorama-metrics { position: relative; z-index: 3; margin-top: auto; display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; padding: 8px; text-align: center; background: rgba(2, 6, 23, .7); border: 1px solid rgba(8, 145, 178, .4); border-radius: 6px; backdrop-filter: blur(8px); }
.panorama-metric + .panorama-metric { border-left: 1px solid rgba(30, 41, 59, .8); padding-left: 6px; }
.panorama-metric__label { font-size: 10px; color: var(--slate-400); display: flex; align-items: center; justify-content: center; gap: 4px; }
.panorama-metric__value { font-size: 14px; font-weight: 700; color: var(--cyan-300); margin-top: 4px; }
.panorama-metric__value span { font-size: 10px; font-weight: 400; }

.dual-charts { display: grid; grid-template-columns: 1fr; gap: 12px; }
@media (min-width: 768px) { .dual-charts { grid-template-columns: 1fr 1fr; } }
.dual-charts > article { padding: 12px; min-height: 220px; display: flex; flex-direction: column; }

/* ============ Right column ============ */
.panel-priority { padding: 12px; }
.text-link { background: transparent; border: 0; color: var(--cyan-400); font-size: 10px; cursor: pointer; padding: 0; transition: color .2s; }
.text-link:hover { color: #a5f3fc; }
.talent-list { display: flex; flex-direction: column; gap: 8px; }
.talent-row { padding: 8px 10px; border-radius: 4px; background: rgba(15, 23, 42, .6); border: 1px solid var(--slate-800); display: flex; align-items: center; justify-content: space-between; gap: 12px; transition: border-color .2s; }
.talent-row:hover { border-color: rgba(6, 182, 212, .4); }
.talent-row__lead { display: flex; gap: 10px; align-items: center; min-width: 0; flex: 1; }
.talent-row__avatar { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; border: 1px solid rgba(34, 211, 238, .5); flex-shrink: 0; }
.talent-row__name { font-size: 12px; font-weight: 600; color: var(--slate-100); }
.talent-row__role { font-size: 10px; color: var(--slate-400); margin-top: 1px; }
.talent-row__tags { display: flex; gap: 4px; margin-top: 4px; flex-wrap: wrap; }
.talent-row__tags span { font-size: 9px; padding: 1px 4px; border-radius: 2px; background: var(--slate-800); color: var(--cyan-300); border: 1px solid rgba(8, 145, 178, .7); }
.talent-row__score { text-align: right; flex-shrink: 0; }
.talent-row__score-label { font-size: 10px; color: var(--slate-400); }
.talent-row__score-value { font-size: 16px; font-weight: 700; color: #fbbf24; }
.talent-row__contact { margin-top: 4px; padding: 2px 8px; font-size: 10px; color: #fff; background: linear-gradient(90deg, #2563eb, #0891b2); border: 0; border-radius: 4px; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,.3); transition: filter .2s; }
.talent-row__contact:hover { filter: brightness(1.15); }

.panel-emerging { padding: 12px; }
.emerging-body { display: grid; grid-template-columns: 6fr 6fr; gap: 8px; align-items: center; }
.emerging-chart { height: 150px; }
.emerging-legend { display: flex; flex-direction: column; gap: 6px; font-size: 11px; }
.emerging-legend__row { display: flex; align-items: center; justify-content: space-between; color: var(--slate-300); }
.legend-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }

.panel-region { padding: 12px; flex: 1; display: flex; flex-direction: column; }
.region-canvas { position: relative; flex: 1; min-height: 200px; background: rgba(2, 6, 23, .4); border-radius: 6px; overflow: hidden; border: 1px solid rgba(30, 41, 59, .8); }
.region-canvas :deep(.ping) { transform-origin: center; animation: ping 1.6s cubic-bezier(0,0,.2,1) infinite; }
.region-top { position: absolute; top: 12px; right: 12px; background: rgba(15, 23, 42, .85); backdrop-filter: blur(8px); padding: 6px 8px; border-radius: 4px; border: 1px solid rgba(8, 145, 178, .6); font-size: 10px; width: 110px; display: flex; flex-direction: column; gap: 3px; box-shadow: 0 4px 12px rgba(0,0,0,.5); z-index: 4; }
.panel-region { position: relative; }
.region-top__row { display: flex; justify-content: space-between; align-items: center; color: var(--slate-400); }
.region-top__row .font-digits { color: var(--cyan-300); }
.region-rank { font-weight: 700; margin-right: 4px; }
.region-rank--gold { color: #fbbf24; }
.region-rank--silver { color: #cbd5e1; }
.region-rank--bronze { color: #d97706; }
.region-rank--grey { color: var(--slate-500); }

/* ============ Modal ============ */
.info-modal { position: fixed; inset: 0; background: rgba(2, 6, 23, .8); backdrop-filter: blur(6px); z-index: 100; display: flex; align-items: center; justify-content: center; padding: 16px; }
.info-modal__inner { max-width: 420px; width: 100%; padding: 24px; text-align: center; display: flex; flex-direction: column; gap: 12px; border-color: rgba(6, 182, 212, .6) !important; box-shadow: 0 16px 48px rgba(0,0,0,.5) !important; }
.info-modal__icon { width: 48px; height: 48px; border-radius: 50%; background: rgba(8, 47, 73, .9); border: 1px solid rgba(34, 211, 238, .55); display: flex; align-items: center; justify-content: center; margin: 0 auto; color: var(--cyan-300); font-size: 20px; animation: bounce 1.4s infinite; }
.info-modal__inner h3 { font-size: 16px; font-weight: 700; color: var(--cyan-300); margin: 0; }
.info-modal__inner p { font-size: 12px; color: var(--slate-300); line-height: 1.6; margin: 0; }
.info-modal__btn { padding: 8px 22px; background: linear-gradient(90deg, #0891b2, #2563eb); color: #fff; font-weight: 500; font-size: 12px; border-radius: 4px; border: 1px solid rgba(34, 211, 238, .5); cursor: pointer; box-shadow: 0 6px 16px rgba(8, 47, 73, .5); transition: filter .2s; }
.info-modal__btn:hover { filter: brightness(1.1); }

.modal-enter-active, .modal-leave-active { transition: opacity .25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }

/* ============ Scrollbar ============ */
.hr-cockpit ::-webkit-scrollbar { width: 4px; height: 4px; }
.hr-cockpit ::-webkit-scrollbar-track { background: rgba(15, 23, 42, .6); }
.hr-cockpit ::-webkit-scrollbar-thumb { background: #0284c7; border-radius: 2px; }
.hr-cockpit ::-webkit-scrollbar-thumb:hover { background: #38bdf8; }

/* ============ Animations ============ */
@keyframes ping { 0%, 100% { opacity: .75; transform: scale(1); } 75%, 100% { opacity: 0; transform: scale(2); } }
@keyframes glowPulse { 0%, 100% { filter: drop-shadow(0 0 6px rgba(56, 189, 248, .6)); } 50% { filter: drop-shadow(0 0 14px rgba(56, 189, 248, .9)); } }
@keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
</style>
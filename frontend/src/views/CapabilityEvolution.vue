<template>
  <div class="page evolution-page">
    <PageHeader title="能力演化" desc="岗位能力随时间的新增、淘汰与迁移趋势分析">
      <el-radio-group v-if="isAdminSide" v-model="tab" @change="onTabChange">
        <el-radio-button value="version">版本对比</el-radio-button>
        <el-radio-button value="compare">领域对比</el-radio-button>
      </el-radio-group>
      <el-button type="primary" :loading="loading" @click="loadAll">刷新数据</el-button>
    </PageHeader>

    <!-- 求职者端：能力热点（生命树）为主视觉放顶部 + 演化时间线放底部，避免时间线过长把树挤到看不见 -->
    <template v-if="!isAdminSide">
      <div class="evo-merge-label">能力热点 · 生命演化树</div>
      <EvolutionViews mode="hotspot" :hotspot="hotspot" :compare="compare" :cards="versionCards" />
      <div class="evo-merge-label evo-merge-label--secondary">
        <span>岗位演化时间线</span>
        <small>（时间线过长时可在本区域内滚动）</small>
      </div>
      <div class="evo-timeline-wrap">
        <EvolutionTimeline :timeline="timeline" />
      </div>
    </template>
    <!-- HR/管理端：版本对比 / 领域对比（已迁移，后续用于大屏展示） -->
    <EvolutionViews v-else :mode="tab" :hotspot="hotspot" :compare="compare" :cards="versionCards" />

    <!-- Legacy view code retained but disabled while the new dashboard is active. -->
    <template v-if="false">
      <div class="metric-grid evo-metrics">
        <div class="metric-card"><div class="metric-label">更新事件</div><div class="metric-value">{{ timeline.total || 0 }}</div></div>
        <div class="metric-card"><div class="metric-label">新增技能</div><div class="metric-value">{{ sum('added') }}</div></div>
        <div class="metric-card"><div class="metric-label">淘汰技能</div><div class="metric-value">{{ sum('removed') }}</div></div>
        <div class="metric-card"><div class="metric-label">修改技能</div><div class="metric-value">{{ sum('modified') }}</div></div>
      </div>
      <div class="content-grid">
        <section class="panel span-7">
          <div class="panel-heading"><div><span>能力变更趋势</span><small>SKILL DELTA OVER TIME</small></div></div>
          <EChart :option="timelineOption" style="height: 380px" />
        </section>
        <section class="panel span-5">
          <div class="panel-heading"><div><span>更新事件明细</span><small>EVENT LOG</small></div></div>
          <div class="event-list">
            <div v-for="(e, i) in timeline.events" :key="i" class="event-item">
              <div class="event-top">
                <span class="event-job">{{ e.jobName }}</span>
                <el-tag size="small" effect="plain">{{ e.version }}</el-tag>
                <span class="event-date">{{ e.date }}</span>
              </div>
              <p class="event-note">{{ e.note }}</p>
              <div class="event-tags">
                <el-tag v-for="s in e.added" :key="'a' + s" size="small" type="success" effect="light">+{{ s }}</el-tag>
                <el-tag v-for="s in e.removed" :key="'r' + s" size="small" type="danger" effect="light">−{{ s }}</el-tag>
                <el-tooltip v-for="s in e.modified" :key="'m' + s.name" :content="s.change" :disabled="!s.change" placement="top">
                  <el-tag size="small" type="warning" effect="light">~{{ s.name }}</el-tag>
                </el-tooltip>
              </div>
              <div class="event-conf">置信度 {{ (e.confidence * 100).toFixed(0) }}%</div>
            </div>
            <el-empty v-if="!timeline.events?.length" description="暂无更新事件" :image-size="80" />
          </div>
        </section>
      </div>
    </template>

    <!-- Hotspot -->
    <template v-if="false">
      <div class="content-grid">
        <section class="panel span-8">
          <div class="panel-heading"><div><span>能力热度排行</span><small>RISING SKILLS</small></div></div>
          <EChart :option="hotspotOption" style="height: 440px" />
        </section>
        <aside class="span-4 hot-side">
          <section class="panel side-block">
            <div class="panel-heading"><div><span>新兴能力</span><small>EMERGING</small></div></div>
            <div class="chip-wrap">
              <span v-for="e in hotspot.emerging" :key="e.name" class="emerging-chip">
                {{ e.name }}<b>×{{ e.growth }}</b>
              </span>
              <el-empty v-if="!hotspot.emerging?.length" description="暂无新兴能力" :image-size="60" />
            </div>
          </section>
          <section class="panel side-block">
            <div class="panel-heading"><div><span>淘汰能力</span><small>DECLINING</small></div></div>
            <div class="decline-list">
              <div v-for="d in hotspot.declining" :key="d.name" class="decline-row">
                <span>{{ d.name }}</span>
                <el-tag size="small" type="danger" effect="light">淘汰 {{ d.removed }}</el-tag>
              </div>
              <el-empty v-if="!hotspot.declining?.length" description="暂无淘汰能力" :image-size="60" />
            </div>
          </section>
        </aside>
      </div>
    </template>

    <!-- Version comparison -->
    <template v-if="false">
      <div class="version-hint">
        <el-icon><InfoFilled /></el-icon>
        <span>由岗位能力更新事件重建「上一版 vs 当前版」的能力画像，直观展示每个岗位新增、淘汰、调整了哪些能力及依据。</span>
      </div>
      <div class="content-grid version-cards">
        <section v-for="card in versionCards" :key="card.jobId" class="panel span-6 version-card">
          <div class="version-card__head">
            <div class="version-card__title">
              <span class="vc-job">{{ card.jobName }}</span>
              <el-tag size="small" effect="plain">{{ card.domain }}</el-tag>
            </div>
            <div class="version-badges">
              <span class="ver ver--from">{{ card.fromVersion }}</span>
              <span class="ver-arrow">→</span>
              <span class="ver ver--to">{{ card.toVersion }}</span>
            </div>
          </div>
          <p class="version-note">{{ card.note }}</p>
          <div class="diff-grid">
            <div class="diff-col diff-col--add">
              <div class="diff-label">新增能力 <b>{{ card.added.length }}</b></div>
              <div class="diff-tags">
                <el-tag v-for="s in card.added" :key="'a' + s" size="small" type="success" effect="light">+ {{ s }}</el-tag>
                <span v-if="!card.added.length" class="diff-empty">无</span>
              </div>
            </div>
            <div class="diff-col diff-col--mod">
              <div class="diff-label">调整/替代 <b>{{ card.modified.length }}</b></div>
              <div class="diff-tags">
                <el-tooltip v-for="s in card.modified" :key="'m' + s.name" :content="s.change" :disabled="!s.change" placement="top">
                  <el-tag size="small" type="warning" effect="light">~ {{ s.name }}</el-tag>
                </el-tooltip>
                <span v-if="!card.modified.length" class="diff-empty">无</span>
              </div>
            </div>
            <div class="diff-col diff-col--del">
              <div class="diff-label">淘汰能力 <b>{{ card.removed.length }}</b></div>
              <div class="diff-tags">
                <el-tag v-for="s in card.removed" :key="'r' + s" size="small" type="danger" effect="light">− {{ s }}</el-tag>
                <span v-if="!card.removed.length" class="diff-empty">无</span>
              </div>
            </div>
          </div>
          <div class="version-foot">
            <span class="version-conf">证据置信度 {{ (card.confidence * 100).toFixed(0) }}%</span>
            <span class="version-count">当前能力 {{ card.currentSkills.length }} 项 · 上一版 {{ card.previousSkills.length }} 项</span>
          </div>
        </section>
        <el-empty v-if="!versionCards.length" description="暂无岗位版本更新记录" :image-size="90" />
      </div>
    </template>

    <!-- Compare -->
    <template v-if="false">
      <section class="panel">
        <div class="panel-heading"><div><span>领域能力结构对比</span><small>DOMAIN × CATEGORY</small></div></div>
        <EChart :option="compareOption" style="height: 420px" />
      </section>
      <div class="content-grid compare-cards">
        <section v-for="row in compare.matrix" :key="row.domain" class="panel span-4 domain-card">
          <div class="domain-title">{{ row.domain }}</div>
          <div class="domain-skills">
            <div v-for="s in row.topSkills" :key="s.name" class="domain-skill">
              <span class="domain-skill__name">{{ s.name }}</span>
              <span class="domain-skill__bar"><i :style="{ width: skillBar(s.weight) }"></i></span>
            </div>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { InfoFilled } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import EChart from '@/components/EChart.vue'
import EvolutionTimeline from '@/components/EvolutionTimeline.vue'
import EvolutionViews from '@/components/EvolutionViews.vue'
import { api } from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
// 版本对比 / 领域对比 已迁移至管理端（后续用于大屏展示）；求职者端为时间线+热点单页
const isAdminSide = computed(() => auth.role === 'hr' || auth.role === 'admin')
const tab = ref('version')
const loading = ref(false)
const timeline = ref<any>({ timeline: [], events: [], total: 0 })
const hotspot = ref<any>({ rising: [], declining: [], emerging: [] })
const compare = ref<any>({ categories: [], domains: [], matrix: [] })
const versionCards = ref<any[]>([])

const PALETTE = ['#52ddff', '#0aa9b4', '#8cc8d8', '#52ddff', '#ffc048', '#c19aff', '#7fd4ff']

function sum(key: string) {
  return (timeline.value.timeline || []).reduce((acc: number, b: any) => acc + (b[key] || 0), 0)
}

const timelineOption = computed(() => {
  const rows = timeline.value.timeline || []
  return {
    textStyle: { color: '#78a4a9' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['新增', '淘汰', '修改'], top: 0, textStyle: { color: '#8fb7bd' } },
    grid: { left: 40, right: 20, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: rows.map((r: any) => r.date), axisLine: { lineStyle: { color: 'rgba(82, 221, 255,0.20)' } }, axisLabel: { color: '#78a4a9' } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(82, 221, 255,0.10)' } }, axisLabel: { color: '#78a4a9' } },
    series: [
      { name: '新增', type: 'bar', stack: 'x', data: rows.map((r: any) => r.added), itemStyle: { color: '#52ddff', borderRadius: [4, 4, 0, 0], shadowColor: 'rgba(82, 221, 255,0.28)', shadowBlur: 8 } },
      { name: '淘汰', type: 'bar', stack: 'x', data: rows.map((r: any) => r.removed), itemStyle: { color: '#ff5d7d' } },
      { name: '修改', type: 'bar', stack: 'x', data: rows.map((r: any) => r.modified), itemStyle: { color: '#ffc048' } },
      {
        name: '事件',
        type: 'line',
        smooth: true,
        data: rows.map((r: any) => r.events),
        lineStyle: { color: '#0aa9b4', width: 3 },
        itemStyle: { color: '#52ddff', shadowColor: 'rgba(82, 221, 255,0.45)', shadowBlur: 8 },
        areaStyle: { color: 'rgba(10, 169, 180,0.10)' }
      }
    ]
  }
})

const hotspotOption = computed(() => {
  const rows = [...(hotspot.value.rising || [])].reverse()
  return {
    textStyle: { color: '#78a4a9' },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 90, right: 30, top: 20, bottom: 30 },
    xAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(82, 221, 255,0.10)' } }, axisLabel: { color: '#78a4a9' } },
    yAxis: {
      type: 'category',
      data: rows.map((r: any) => r.name),
      axisLine: { lineStyle: { color: 'rgba(82, 221, 255,0.20)' } },
      axisLabel: { color: '#bcd8dd' }
    },
    series: [
      {
        type: 'bar',
        data: rows.map((r: any, i: number) => ({
          value: r.heat,
          itemStyle: { color: PALETTE[i % PALETTE.length], borderRadius: [0, 6, 6, 0], shadowColor: 'rgba(82, 221, 255,0.25)', shadowBlur: 6 }
        })),
        barWidth: '58%',
        label: { show: true, position: 'right', formatter: '{c}', color: '#bcd8dd', fontWeight: 700 }
      }
    ]
  }
})

const compareOption = computed(() => {
  const cats = compare.value.categories || []
  const domains = compare.value.domains || []
  const matrix = compare.value.matrix || []
  return {
    textStyle: { color: '#78a4a9' },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: cats, top: 0, type: 'scroll', textStyle: { color: '#8fb7bd' } },
    grid: { left: 40, right: 20, top: 40, bottom: 60 },
    xAxis: { type: 'category', data: domains, axisLabel: { interval: 0, rotate: 24, color: '#bcd8dd' }, axisLine: { lineStyle: { color: 'rgba(82, 221, 255,0.20)' } } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(82, 221, 255,0.10)' } }, axisLabel: { color: '#78a4a9' } },
    series: cats.map((cat: string, i: number) => ({
      name: cat,
      type: 'bar',
      stack: 'total',
      data: matrix.map((row: any) => row.categories[cat] || 0),
      itemStyle: { color: PALETTE[i % PALETTE.length] }
    }))
  }
})

const maxWeight = computed(() => {
  let m = 1
  for (const row of compare.value.matrix || []) {
    for (const s of row.topSkills || []) m = Math.max(m, s.weight)
  }
  return m
})

function skillBar(weight: number) {
  return `${Math.round((weight / maxWeight.value) * 100)}%`
}

async function loadAll() {
  loading.value = true
  try {
    const [t, h, c, v] = await Promise.all([
      api.evolutionTimeline(),
      api.evolutionHotspot(),
      api.evolutionCompare(),
      api.evolutionVersionCompare()
    ])
    timeline.value = t
    hotspot.value = h
    compare.value = c
    versionCards.value = Array.isArray(v?.cards) ? v.cards : []
  } finally {
    loading.value = false
  }
}

function onTabChange() {
  /* charts are reactive via computed options */
}

onMounted(loadAll)
</script>

<style scoped>
/* ===== 系统概览风格（荧光青 + 高通透玻璃） ===== */
.evolution-page {
  min-width: 0;
  overflow-x: clip;
  position: relative;
  background: transparent;
  --panel: rgba(2, 24, 30, .38);
  --edge: rgba(21, 197, 199, .10);
  --cyan: #15c5c7;
  --teal: #079ea2;
  --text: #d8f2f3;
  --muted: #6f999e;
  --primary: #15c5c7;
  --success: #8ad8bb;
  --warn: #ffc048;
  --danger: #ff5d7d;
  color: var(--text);
}
.evolution-page :deep(.page-header) { border-color: var(--edge) !important; color: var(--text); }
.evolution-page :deep(.content-grid),
.evolution-page :deep(.metric-grid) { gap: 14px; }
.evolution-page :deep(.panel),
.evolution-page :deep(.metric-card),
.version-card, .version-hint, .event-item, .domain-card, .side-block {
  border: 1px solid var(--edge);
  border-radius: 20px;
  background: linear-gradient(145deg, rgba(4, 46, 54, .28), rgba(2, 20, 24, .32));
  box-shadow: 0 24px 62px rgba(0, 10, 14, .16), inset 0 1px 0 rgba(141, 255, 255, .025);
  backdrop-filter: blur(26px) saturate(1.18);
  color: var(--text);
}

.evolution-page :deep(.page-toolbar) {
  min-height: 42px;
  margin-bottom: 14px;
  border: 1px solid rgba(82, 221, 255, 0.14);
  border-radius: 12px;
  padding: 6px 10px;
  background: linear-gradient(90deg, rgba(2, 18, 22, 0.22), rgba(4, 54, 63, 0.24));
  box-shadow: inset 0 0 24px rgba(82, 221, 255, 0.04);
  backdrop-filter: blur(20px) saturate(1.15);
}

.evolution-page :deep(.page-toolbar .el-radio-button__inner) {
  min-width: 86px;
  border-color: rgba(82, 221, 255, 0.18);
  color: #8fb7bd;
  background: rgba(3, 36, 44, 0.26);
  box-shadow: none;
}

.evolution-page :deep(.page-toolbar .el-radio-button__original-radio:checked + .el-radio-button__inner) {
  color: #eaffff;
  background: linear-gradient(180deg, rgba(0, 178, 188, 0.55), rgba(4, 44, 54, 0.58));
  box-shadow: inset 0 -2px rgba(141, 255, 255, 0.38), 0 0 12px rgba(82, 221, 255, 0.28);
}

/* 求职者端顶部紧凑化：能力演化树是主视觉，必须一进页面就看到，
   不允许被上方页头 + 空白把它挤到视口之外 */
.evolution-page :deep(.page-toolbar) {
  margin-bottom: 4px !important;
  min-height: 36px !important;
}

.evo-merge-label {
  display: flex;
  align-items: center;
  gap: 12px;
  /* 顶部由 22px 压缩到 4px，整体向上贴近页头 */
  margin: 4px 0 6px;
  color: var(--cyan);
  font-size: 14px;
  font-weight: 850;
  letter-spacing: 0.06em;
  text-shadow: 0 0 8px rgba(82, 221, 255, .30);
}

.evo-merge-label::before {
  width: 4px;
  height: 16px;
  border-radius: 2px;
  background: linear-gradient(180deg, var(--teal), var(--cyan));
  content: "";
  flex: 0 0 auto;
}

.evo-merge-label::after {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, rgba(82, 221, 255, 0.28), transparent);
  content: "";
}

/* 能力热点（主树）的标签与舞台之间不留 14→6px 的大空，
   让 3D 生命树尽量贴着标签，用户一进页面就能看到完整树冠 */
.evolution-page :deep(.hotspot-tree-view) {
  /* 舞台与上方标签的间距控制：外层 wrapper 没有额外 margin，
     所以直接把舞台顶部向上拉 4px，消除装饰性空隙 */
  margin-top: -4px;
  /* 原 calc(100vh - 180px) 基于旧布局的页头+空白估计。
     现在页头/标签已被压缩，把 180 改为 110，相当于舞台整体向上多延伸了 70px，
     树冠（平均 top 约 15%）会从 y=300 提到 y=240 左右，首屏完整可见 */
  height: calc(100vh - 110px);
  min-height: 680px;
}

.evo-merge-label--secondary {
  color: #78b9c0;
  letter-spacing: 0.04em;
  text-shadow: none;
  margin-top: 36px;
}

.evo-merge-label--secondary::before {
  width: 3px;
  height: 12px;
  background: linear-gradient(180deg, #3a797f, #1299a2);
}

.evo-merge-label--secondary::after {
  background: linear-gradient(90deg, rgba(82, 221, 255, 0.14), transparent);
}

.evo-merge-label--secondary span {
  flex: 0 0 auto;
}

.evo-merge-label--secondary small {
  font-size: 11px;
  color: var(--muted);
  font-weight: 500;
  letter-spacing: 0.02em;
  margin-left: 8px;
  flex: 0 0 auto;
}

/* 时间线外层限高 —— 主视觉是生命树，时间线作为次要内容放在容器内滚动阅读，
   避免把能力树推到页面底部导致用户"往下滑看不到树" */
.evo-timeline-wrap {
  max-height: 560px;
  overflow-y: auto;
  overflow-x: clip;
  padding-right: 6px;
  border: 1px solid rgba(82, 221, 255, 0.08);
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(3, 36, 44, 0.14), rgba(2, 18, 22, 0.18));
  backdrop-filter: blur(14px) saturate(1.10);
  scrollbar-width: thin;
  scrollbar-color: rgba(82, 221, 255, 0.28) transparent;
}

.evo-timeline-wrap::-webkit-scrollbar {
  width: 6px;
}

.evo-timeline-wrap::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, rgba(10, 169, 180, 0.55), rgba(82, 221, 255, 0.45));
  border-radius: 3px;
}

.evo-timeline-wrap::-webkit-scrollbar-track {
  background: transparent;
}

.evo-metrics {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.panel-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(82, 221, 255, .08);
}

.panel-heading span {
  color: var(--text);
  font-size: 16px;
  font-weight: 900;
}

.panel-heading small {
  margin-left: 8px;
  color: var(--cyan);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-shadow: 0 0 8px rgba(82, 221, 255, .30);
}

/* Version comparison */
.version-hint {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid rgba(82, 221, 255, 0.16);
  border-radius: 14px;
  padding: 12px 16px;
  background: rgba(3, 36, 44, 0.20);
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
  backdrop-filter: blur(18px) saturate(1.12);
}

.version-hint .el-icon {
  flex: 0 0 auto;
  color: var(--cyan);
  font-size: 18px;
  text-shadow: 0 0 6px rgba(82, 221, 255, .35);
}

.version-cards {
  margin-top: 4px;
}

.version-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 18px 20px;
}

.version-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.version-card__title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.vc-job {
  color: var(--text);
  font-size: 16px;
  font-weight: 900;
}

.version-badges {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 0 0 auto;
}

.ver {
  border-radius: 8px;
  padding: 3px 10px;
  font-size: 12px;
  font-weight: 800;
}

.ver--from {
  border: 1px solid rgba(82, 221, 255, 0.16);
  background: rgba(3, 36, 44, 0.18);
  color: var(--muted);
}

.ver--to {
  border: 1px solid rgba(82, 221, 255, 0.28);
  background: linear-gradient(135deg, rgba(0, 178, 188, 0.18), rgba(82, 221, 255, 0.16));
  color: var(--cyan);
  text-shadow: 0 0 6px rgba(82, 221, 255, .35);
}

.ver-arrow {
  color: var(--muted);
  font-weight: 800;
}

.version-note {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.7;
}

.diff-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.diff-col {
  border-radius: 14px;
  padding: 12px;
  background: rgba(3, 36, 44, 0.20);
  border: 1px solid rgba(82, 221, 255, 0.12);
  backdrop-filter: blur(16px) saturate(1.12);
}

.diff-col--add {
  border-color: rgba(154, 216, 197, 0.26);
  background: linear-gradient(160deg, rgba(24, 70, 56, .22), rgba(3, 36, 44, .18));
}

.diff-col--mod {
  border-color: rgba(255, 192, 72, 0.26);
  background: linear-gradient(160deg, rgba(80, 58, 10, .22), rgba(3, 36, 44, .18));
}

.diff-col--del {
  border-color: rgba(255, 93, 125, 0.24);
  background: linear-gradient(160deg, rgba(80, 20, 34, .22), rgba(3, 36, 44, .18));
}

.diff-label {
  margin-bottom: 10px;
  color: var(--text);
  font-size: 12px;
  font-weight: 850;
}

.diff-label b {
  color: var(--cyan);
  text-shadow: 0 0 6px rgba(82, 221, 255, .35);
}

.diff-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.diff-empty {
  color: var(--muted);
  font-size: 12px;
}

.version-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  border-top: 1px solid rgba(82, 221, 255, 0.08);
  padding-top: 10px;
}

.version-conf {
  color: var(--cyan);
  font-size: 12px;
  font-weight: 800;
  text-shadow: 0 0 6px rgba(82, 221, 255, .35);
}

.version-count {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
}

.event-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 380px;
  overflow-y: auto;
  padding-right: 6px;
}

.event-item {
  border: 1px solid rgba(82, 221, 255, 0.12);
  border-radius: 14px;
  padding: 12px 14px;
  background: rgba(3, 36, 44, 0.22);
  backdrop-filter: blur(16px) saturate(1.12);
}

.event-top {
  display: flex;
  align-items: center;
  gap: 8px;
}

.event-job {
  color: var(--text);
  font-weight: 850;
}

.event-date {
  margin-left: auto;
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
}

.event-note {
  margin: 8px 0;
  color: #a4c6cb;
  font-size: 13px;
  line-height: 1.65;
}

.event-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.event-conf {
  margin-top: 8px;
  color: var(--cyan);
  font-size: 12px;
  font-weight: 800;
  text-shadow: 0 0 6px rgba(82, 221, 255, .35);
}

.hot-side {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.side-block {
  padding: 18px;
}

.chip-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.emerging-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid rgba(193, 154, 255, 0.26);
  border-radius: 999px;
  padding: 6px 12px;
  background: linear-gradient(135deg, rgba(60, 30, 108, 0.22), rgba(3, 36, 44, 0.20));
  backdrop-filter: blur(14px) saturate(1.10);
  color: #c19aff;
  font-size: 13px;
  font-weight: 800;
}

.emerging-chip b {
  color: var(--cyan);
  font-size: 11px;
  text-shadow: 0 0 6px rgba(82, 221, 255, .35);
}

.decline-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.decline-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(82, 221, 255, 0.08);
  padding: 8px 2px;
  color: var(--text);
  font-weight: 700;
}

.compare-cards {
  margin-top: 18px;
}

.domain-card {
  padding: 16px 18px;
}

.domain-title {
  margin-bottom: 12px;
  color: var(--text);
  font-size: 15px;
  font-weight: 900;
}

.domain-skills {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.domain-skill {
  display: grid;
  grid-template-columns: 100px 1fr;
  align-items: center;
  gap: 10px;
}

.domain-skill__name {
  overflow: hidden;
  color: var(--muted);
  font-size: 12px;
  font-weight: 750;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.domain-skill__bar {
  height: 8px;
  border-radius: 99px;
  background: rgba(0, 142, 156, 0.18);
  overflow: hidden;
}

.domain-skill__bar i {
  display: block;
  height: 100%;
  border-radius: 99px;
  background: linear-gradient(90deg, var(--teal), var(--cyan));
  box-shadow: 0 0 8px rgba(82, 221, 255, .42);
}

@media (max-width: 1100px) {
  .evo-metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .span-7,
  .span-5,
  .span-8,
  .span-6,
  .span-4 {
    grid-column: span 12;
  }
}
</style>

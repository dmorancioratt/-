<template>
  <section v-if="mode === 'version'" class="version-dashboard">
<div class="v-top-bar">
      <div class="v-title-box">
        <div class="v-title-main">版本对比战场态势</div>
        <div class="v-title-sub">VERSION COMPARISON BATTLEFIELD SITUATION</div>
      </div>
    </div>

    <div class="v-main-layout">
      <aside class="v-col v-col-left">
        <section class="v-panel">
          <div class="v-panel-head"><span>版本概览</span><small>VERSION DATA</small></div>
          <div class="v-metric-grid">
            <div class="v-metric">
              <div class="v-m-val">{{ previousCount }}</div>
              <div class="v-m-label">上一版</div>
              <div class="v-m-delta cyan">{{ activeCard.fromVersion || '—' }}</div>
            </div>
            <div class="v-metric">
              <div class="v-mini-ring"><span class="v-m-val" style="font-size:.9em">{{ signedDelta }}</span></div>
              <div class="v-m-label">净变化</div>
              <div class="v-m-delta" :class="delta >= 0 ? 'up' : 'down'">{{ changeCount }}项变更</div>
            </div>
            <div class="v-metric">
              <div class="v-m-val">{{ currentCount }}</div>
              <div class="v-m-label">当前版</div>
              <div class="v-m-delta gold">{{ activeCard.toVersion || '—' }}</div>
            </div>
          </div>
        </section>

        <section class="v-panel">
          <div class="v-panel-head"><span>差异转向</span><small>DELTA AVISIONS</small></div>
          <div class="v-gauge-grid">
            <div class="v-gauge">
              <div class="v-gauge-ring green"><span class="v-g-num">{{ addedItems.length }}</span></div>
              <div class="v-g-label">新增能力</div>
            </div>
            <div class="v-gauge">
              <div class="v-gauge-ring gold"><span class="v-g-num">{{ modifiedItems.length }}</span></div>
              <div class="v-g-label">调整能力</div>
            </div>
          </div>
        </section>

        <section class="v-panel">
          <div class="v-panel-head"><span>能力变化方向</span><small>EVOLUTION</small></div>
          <div class="v-skill-grid">
            <div class="v-skill" v-for="(s, i) in versionSkillBalls" :key="i">
              <div class="v-skill-ball" :class="s.color">{{ s.val }}</div>
              <label>{{ s.name }}</label>
            </div>
          </div>
        </section>
      </aside>

      <main class="v-col v-col-center">
        <section class="v-hero-panel">
          <div class="v-corner-tl"></div>
          <div class="v-corner-br"></div>
          <div class="v-hero-bg"></div>
          <div class="v-hero-glow"></div>
          <div class="v-hero-grid-floor"></div>
          <div class="v-scan-line"></div>
          <div class="v-holo-row">
            <div v-for="(h, i) in versionHoloCards" :key="i" class="v-holo-card" :style="{ '--glow': h.glow }">
              <div class="v-holo-title">{{ h.title }}<span class="v-holo-count">{{ h.count }}</span></div>
              <div class="v-holo-frame">
                <img :src="h.img" :class="['v-core-img', h.imgClass]" />
                <div class="v-core-mask"></div>
                <div class="v-holo-corner-l"></div>
                <div class="v-holo-corner-r"></div>
                <div class="v-holo-pillar"></div>
                <div class="v-holo-halo"></div>
                <div v-for="o in 3" :key="'fr'+i+o" class="v-holo-float" :class="'r'+o"></div>
                <div v-for="o in 4" :key="'ob'+i+o" class="v-holo-orbit" :class="'o'+o"></div>
                <div class="v-holo-stage-label">{{ h.stage }}</div>
                <div class="v-holo-skills">
                  <span v-for="(sk, si) in h.skills.slice(0, 3)" :key="si" class="v-holo-skill-tag">{{ sk }}</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="v-chart-panel" style="flex:1;">
          <div class="v-corner-tl"></div>
          <div class="v-corner-br"></div>
          <div class="v-chart-empty">当前接口仅提供相邻版本差异，未提供连续历史序列，因此不绘制趋势曲线。</div>
        </section>
      </main>

      <aside class="v-col v-col-right">
        <section class="v-panel">
          <div class="v-panel-head"><span>版本匹配分析</span><small>INTELLIGENCE</small></div>
          <div class="v-intel-body">
            <div class="v-big-ring">
              <div><div class="v-big-t">匹配置信度</div><div class="v-big-v">{{ confidence }}%</div></div>
            </div>
          </div>
        </section>

        <section class="v-panel">
          <div class="v-panel-head"><span>变化维度</span><small>CHANGE DIM</small></div>
          <div class="v-dim-list">
            <div v-for="(item, i) in vDimList" :key="i" class="v-list-row">
              <span class="v-item-label"><i class="v-row-bullet" :class="item.color"></i>{{ item.name }}</span>
              <span class="v-item-val">{{ item.val }}</span>
            </div>
          </div>
        </section>

        <section class="v-panel">
          <div class="v-panel-head"><span>版本演进分项指标</span><small>METRICS</small></div>
          <div class="v-metrics-body">
            <div class="v-bar-group">
              <div v-for="(b, i) in vBarMetrics" :key="i" class="v-bar-line">
                <span>{{ b.name }}</span>
                <div class="v-bar-bg"><div class="v-bar-fill" :style="{width: b.val + '%'}"></div></div>
              </div>
            </div>
            <div class="v-num-row">
              <div v-for="(n, i) in vNumSet1" :key="i" class="v-num-cell"><b>{{ n.val }}</b><small>{{ n.label }}</small></div>
            </div>
            <div class="v-num-row">
              <div v-for="(n, i) in vNumSet2" :key="i" class="v-num-cell"><b>{{ n.val }}</b><small>{{ n.label }}</small></div>
            </div>
          </div>
        </section>
      </aside>
    </div>

    <footer class="v-footer-strip">
      <button class="v-strip-arrow" type="button" @click="cycleCard(-1)">‹</button>
      <div class="v-strip-title"><small>QUICK SWITCH</small><b>其他岗位快速对比</b></div>
      <div class="v-role-cards">
        <button
          v-for="(card, index) in roleCards"
          :key="card.jobId || index"
          type="button"
          class="v-role-card"
          :class="{ active: index === activeCardIndex }"
          @click="activeCardIndex = index"
        >
          <span><i>◇</i>{{ card.jobName }}</span>
          <em>{{ card.domain }}</em>
          <b><strong class="up">+{{ card.added?.length || 0 }}</strong> / <span class="warn">{{ card.modified?.length || 0 }}</span> / <i class="down">-{{ card.removed?.length || 0 }}</i></b>
        </button>
      </div>
      <button class="v-strip-arrow" type="button" @click="cycleCard(1)">›</button>
    </footer>
  </section>

  <section v-else-if="mode === 'hotspot'" class="hotspot-tree-view">
    <div class="hotspot-tree-main">
      <SkillEvolutionTree 
        mode="hotspot"
        :hot-skills="allHotSkills"
        @select-fruit="onHotFruitSelect"
      />
    </div>
    
    <div class="hotspot-float-panels">
      <div class="float-panel top-left">
        <h3>能力热点总览</h3>
        <div class="summary-stats">
          <div class="stat-item">
            <b>{{ allHotSkills.length }}</b>
            <span>能力总数</span>
          </div>
          <div class="stat-item">
            <b>{{ heatBuckets.high }}</b>
            <span>高热能力</span>
          </div>
          <div class="stat-item">
            <b>{{ rising.length }}</b>
            <span>升温能力</span>
          </div>
          <div class="stat-item">
            <b>{{ declining.length }}</b>
            <span>降温能力</span>
          </div>
        </div>
      </div>
      
      <div class="float-panel bottom-left">
        <h3>热度分布</h3>
        <div class="heat-bars">
          <div class="heat-bar-row">
            <span class="bar-label hot">高热 ≥16</span>
            <div class="bar-track"><div class="bar-fill hot" :style="{width: (heatBuckets.high / Math.max(hotSkills.length,1) * 100) + '%'}"></div></div>
            <b>{{ heatBuckets.high }}</b>
          </div>
          <div class="heat-bar-row">
            <span class="bar-label warm">中热 12-16</span>
            <div class="bar-track"><div class="bar-fill warm" :style="{width: (heatBuckets.mid / Math.max(hotSkills.length,1) * 100) + '%'}"></div></div>
            <b>{{ heatBuckets.mid }}</b>
          </div>
          <div class="heat-bar-row">
            <span class="bar-label cool">低热 8-12</span>
            <div class="bar-track"><div class="bar-fill cool" :style="{width: (heatBuckets.warm / Math.max(hotSkills.length,1) * 100) + '%'}"></div></div>
            <b>{{ heatBuckets.warm }}</b>
          </div>
        </div>
      </div>
      
      <div class="float-panel right-top">
        <h3>新兴能力 TOP 5</h3>
        <div class="mini-skill-list">
          <button v-for="(item, index) in emerging.slice(0, 5)" :key="item.name" type="button" class="mini-skill-btn" @click="selectSkill(item.name)">
            <i>{{ index + 1 }}</i>
            <span>{{ item.name }}</span>
            <em class="up">↗</em>
          </button>
        </div>
      </div>
      
      <div class="float-panel right-bottom">
        <h3>需要关注</h3>
        <div class="mini-skill-list">
          <button v-for="(item, index) in declining.slice(0, 5)" :key="item.name" type="button" class="mini-skill-btn" @click="selectSkill(item.name)">
            <i>{{ index + 1 }}</i>
            <span>{{ item.name }}</span>
            <em class="down">↘</em>
          </button>
        </div>
      </div>
    </div>
  </section>

  <section v-else class="evo-view compare-view">
    <aside class="domain-stack">
      <button v-for="domain in leftDomains" :key="domain.domain" type="button" class="hud-panel domain-card" :class="{ active: activeDomainName === domain.domain }" @click="activeDomainName = domain.domain">
        <span class="domain-icon">{{ domainIcon(domain.domain) }}</span><div><h3>{{ domain.domain }}</h3><b>{{ domainShare(domain) }}%</b></div><ul><li v-for="skill in domain.topSkills?.slice(0, 5) || []" :key="skill.name"><span>{{ skill.name }}</span><em>{{ skillWeight(skill, domain) }}%</em></li></ul>
      </button>
    </aside>

    <main class="hud-panel domain-command">
      <div class="graph-title"><div><small>DOMAIN CAPABILITY PANORAMA</small><h2>领域能力结构全景</h2></div><span>点击扇区联动领域详情</span></div>
      <EChart :option="sunburstOption" class="domain-chart" @click="handleDomainClick" />
      <div class="domain-focus"><small>ACTIVE DOMAIN</small><b>{{ activeDomain.domain }}</b><strong>{{ domainShare(activeDomain) }}%</strong><span>{{ activeDomain.topSkills?.slice(0, 3).map((item: any) => item.name).join(' · ') }}</span></div>
      <div class="wheel-note">
        <span>占比最高领域 <b>{{ topDomain?.domain || '暂无数据' }}</b><em>{{ topDomain ? domainShare(topDomain) : 0 }}%</em></span>
        <span>领域数量 <b>{{ domains.length }}</b><em>实时聚合</em></span>
        <span>能力项数 <b>{{ compareSkillCount }}</b><em>去重统计</em></span>
        <span>数据口径 <b>岗位-技能</b><em>关系聚合</em></span>
      </div>
    </main>

    <aside class="domain-stack">
      <button v-for="domain in rightDomains" :key="domain.domain" type="button" class="hud-panel domain-card" :class="{ active: activeDomainName === domain.domain }" @click="activeDomainName = domain.domain">
        <span class="domain-icon">{{ domainIcon(domain.domain) }}</span><div><h3>{{ domain.domain }}</h3><b>{{ domainShare(domain) }}%</b></div><ul><li v-for="skill in domain.topSkills?.slice(0, 5) || []" :key="skill.name"><span>{{ skill.name }}</span><em>{{ skillWeight(skill, domain) }}%</em></li></ul>
      </button>
    </aside>
  </section>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, ref, watch } from 'vue'
import EChart from '@/components/EChart.vue'
import SkillEvolutionTree from '@/components/SkillEvolutionTree.vue'
import holoNewSkills from '@/assets/images/holo-new-skills.png'
import holoModified from '@/assets/images/holo-modified.png'
import holoRemoved from '@/assets/images/holo-removed.png'

const props = defineProps<{ mode: string; hotspot: any; compare: any; cards: any[] }>()

const PanelTitle = defineComponent({
  props: { title: { type: String, required: true }, code: { type: String, default: '' } },
  setup(panelProps) {
    return () => h('div', { class: 'panel-title' }, [h('h3', panelProps.title), h('small', panelProps.code)])
  }
})

const displayCards = computed(() => props.cards || [])
const roleCards = computed(() => displayCards.value.slice(0, 5))
const activeCardIndex = ref(0)
const activeWell = ref('add')
const activeCard = computed(() => displayCards.value[activeCardIndex.value] || {})
const previousCount = computed(() => activeCard.value.previousSkills?.length || 0)
const currentCount = computed(() => activeCard.value.currentSkills?.length || 0)
const delta = computed(() => currentCount.value - previousCount.value)
const signedDelta = computed(() => `${delta.value > 0 ? '+' : ''}${delta.value}`)
const confidence = computed(() => Math.round(Number(activeCard.value.confidence || 0) * 100))
const addedItems = computed(() => activeCard.value.added || [])
const modifiedItems = computed(() => activeCard.value.modified || [])
const removedItems = computed(() => activeCard.value.removed || [])
const changeCount = computed(() => addedItems.value.length + modifiedItems.value.length + removedItems.value.length)

const versionSkillBalls = computed(() => [
  { val: addedItems.value.length, name: '新增能力', color: 'green' },
  { val: modifiedItems.value.length, name: '调整能力', color: 'gold' },
  { val: removedItems.value.length, name: '淘汰能力', color: 'red' },
  { val: currentCount.value, name: '当前总数', color: 'cyan' },
  { val: previousCount.value, name: '上版总数', color: 'cyan' },
  { val: confidence.value, name: '置信度%', color: 'cyan' }
])

const versionHoloCards = computed(() => [
  { title: '新增能力', count: `${addedItems.value.length}项`, glow: '#54f2ff', stage: 'NEW SKILLS', img: holoNewSkills, imgClass: 'core-left', skills: addedItems.value.map((i: any) => typeof i === 'string' ? i : i.name) },
  { title: '调整/替代', count: `${modifiedItems.value.length}项`, glow: '#ffe066', stage: 'MODIFIED', img: holoModified, imgClass: 'core-center', skills: modifiedItems.value.map((i: any) => i.name || i) },
  { title: '淘汰能力', count: `${removedItems.value.length}项`, glow: '#ff785f', stage: 'REMOVED', img: holoRemoved, imgClass: 'core-right', skills: removedItems.value.map((i: any) => typeof i === 'string' ? i : i.name) }
])

const vDimList = computed(() => [
  { name: '技术栈更新', val: `${addedItems.value.length}项`, color: 'cyan' },
  { name: '能力升级', val: `${modifiedItems.value.length}项`, color: 'gold' },
  { name: '旧技术淘汰', val: `${removedItems.value.length}项`, color: 'red' }
])

const vBarMetrics = computed(() => [
  { name: '证据置信度', val: confidence.value },
  { name: '变更率', val: Math.min(100, Math.round(changeCount.value / Math.max(previousCount.value, 1) * 100)) }
])

const vNumSet1 = computed(() => [
  { val: addedItems.value.length, label: '新增' },
  { val: modifiedItems.value.length, label: '调整' },
  { val: removedItems.value.length, label: '淘汰' },
  { val: signedDelta.value, label: '净变' }
])
const vNumSet2 = computed(() => [
  { val: confidence.value + '%', label: '置信度' },
  { val: currentCount.value, label: '当前' },
  { val: previousCount.value, label: '上版' },
  { val: Math.round(changeCount.value / Math.max(previousCount.value, 1) * 100) + '%', label: '变更率' }
])

function skillLabel(item: any) { return typeof item === 'string' ? item : item?.name || '能力项' }
function cycleCard(step: number) { if (displayCards.value.length) activeCardIndex.value = (activeCardIndex.value + step + displayCards.value.length) % displayCards.value.length }

const rising = computed<any[]>(() => props.hotspot?.rising || [])
const declining = computed<any[]>(() => props.hotspot?.declining || [])
const emerging = computed<any[]>(() => props.hotspot?.emerging || [])
const hotSkills = computed(() => {
  const merged = [...rising.value, ...emerging.value].filter((item, index, arr) => item?.name && arr.findIndex((row) => row.name === item.name) === index)
  return merged.slice(0, 10).map((item: any) => ({ ...item, heat: Number(item.heat ?? item.growth ?? 0).toFixed(2) }))
})
const activeSkillName = ref('')
const activeSkill = computed(() => {
  const all = [...hotSkills.value, ...rising.value, ...emerging.value, ...declining.value]
  const selected = all.find((item) => item.name === activeSkillName.value)
  return selected ? { ...selected, heat: Number(selected.heat ?? selected.growth ?? selected.removed ?? 0).toFixed(2) } : hotSkills.value[0] || {}
})
watch(hotSkills, (skills) => { if (!skills.some((item) => item.name === activeSkillName.value)) activeSkillName.value = skills[0]?.name || '' }, { immediate: true })
const emergingList = computed(() => emerging.value.slice(0, 5))
const heatBuckets = computed(() => allHotSkills.value.reduce((acc, item) => { const heat = Number(item.heat); if (heat >= 16) acc.high++; else if (heat >= 14) acc.mid++; else if (heat >= 12) acc.warm++; else acc.low++; return acc }, { high: 0, mid: 0, warm: 0, low: 0 }))

function heatColor(heat: number) { return heat >= 16 ? '#ffb52e' : heat >= 12 ? '#37e6a1' : heat >= 8 ? '#a26cff' : '#28cfff' }
function selectSkill(name: string) { if (name) activeSkillName.value = name }
function handleSkillClick(params: any) { if (params?.data?.skillName) selectSkill(params.data.skillName) }
function onHotFruitSelect(skill: any) { if (skill?.name) selectSkill(skill.name) }

const allHotSkills = computed<any[]>(() => {
  const merged = [...hotSkills.value, ...emerging.value, ...rising.value].filter((item, index, arr) => 
    item?.name && arr.findIndex((row) => row.name === item.name) === index
  )
  return merged.slice(0, 16)
})
function hotNodeHitStyle(index: number) { const angle = index / Math.max(hotSkills.value.length, 1) * Math.PI * 2 - Math.PI / 2; return { left: `${50 + Math.cos(angle) * 36}%`, top: `${50 + Math.sin(angle) * 34}%` } }
function formatHeat(item: any) { return Number(item.heat ?? item.growth ?? item.removed ?? 0).toFixed(2) }
function growthLabel(item: any) { const value = item?.growth; return value == null ? '—' : `${Number(value).toFixed(1)}%` }

const hotspotGraphOption = computed(() => {
  const cx = 410; const cy = 308; const radiusX = 322; const radiusY = 222
  const hexSymbol = 'path://M0,-34 L29,-17 L29,17 L0,34 L-29,17 L-29,-17 Z'
  const nodes: any[] = [{
    id: 'core', name: '能力热点\n总览', x: cx, y: cy, symbol: hexSymbol, symbolSize: 150, fixed: true,
    itemStyle: {
      color: { type: 'radial', x: .5, y: .38, r: .78, colorStops: [{ offset: 0, color: '#1686ba' }, { offset: .46, color: '#06345f' }, { offset: 1, color: '#010711' }] },
      borderColor: '#73e9ff', borderWidth: 2, shadowBlur: 24, shadowColor: 'rgba(31,186,255,.65)'
    },
    label: { show: true, position: 'inside', color: '#effdff', fontSize: 20, fontWeight: 900, lineHeight: 29, textShadowBlur: 10, textShadowColor: '#28cfff' }
  }]
  const links: any[] = []
  hotSkills.value.forEach((skill, index) => {
    const angle = (index / hotSkills.value.length) * Math.PI * 2 - Math.PI / 2
    const heat = Number(skill.heat); const color = heatColor(heat)
    nodes.push({
      id: `skill-${index}`, name: `${skill.name}\n${skill.heat}`, skillName: skill.name, value: heat,
      x: cx + Math.cos(angle) * radiusX, y: cy + Math.sin(angle) * radiusY, symbol: hexSymbol,
      symbolSize: activeSkillName.value === skill.name ? 72 : 58,
      itemStyle: {
        color: { type: 'radial', x: .44, y: .34, r: .82, colorStops: [{ offset: 0, color: `${color}88` }, { offset: .52, color: '#071b31' }, { offset: 1, color: '#01060d' }] },
        borderColor: color, borderWidth: activeSkillName.value === skill.name ? 3 : 1.4,
        shadowBlur: activeSkillName.value === skill.name ? 20 : 10, shadowColor: color
      },
      label: { show: true, position: 'bottom', distance: 8, color: '#dff9ff', fontSize: 10, fontWeight: 750, lineHeight: 17, textShadowBlur: 6, textShadowColor: '#001' }
    })
    links.push({ source: 'core', target: `skill-${index}`, lineStyle: { color, width: activeSkillName.value === skill.name ? 2.6 : 1, opacity: activeSkillName.value === skill.name ? .95 : .55, curveness: index % 2 ? .1 : -.1, shadowBlur: 9, shadowColor: color } })
  })
  return {
    backgroundColor: 'transparent',
    animationDurationUpdate: 650,
    tooltip: { backgroundColor: 'rgba(3,20,54,.35)', borderColor: '#27cfff', textStyle: { color: '#dffaff' }, formatter: (p: any) => p.data?.skillName ? `<b>${p.data.skillName}</b><br/>热度：${p.data.value}<br/>点击聚焦该能力` : '能力热点总览' },
    graphic: [
      { type: 'circle', shape: { cx, cy, r: 178 }, style: { fill: 'transparent', stroke: 'rgba(72,206,255,.32)', lineWidth: 1.5, shadowBlur: 8, shadowColor: '#1fa8ff' } },
      { type: 'circle', shape: { cx, cy, r: 205 }, style: { fill: 'transparent', stroke: 'rgba(35,158,255,.18)', lineWidth: 1, lineDash: [2, 6] } },
      { type: 'circle', shape: { cx, cy, r: 260 }, style: { fill: 'transparent', stroke: 'rgba(35,158,255,.18)', lineWidth: 1, lineDash: [10, 9] } },
      { type: 'circle', shape: { cx, cy, r: 305 }, style: { fill: 'transparent', stroke: 'rgba(35,158,255,.12)', lineWidth: 1 } }
    ],
    series: [{ type: 'graph', layout: 'none', coordinateSystem: null, roam: false, data: nodes, links, edgeSymbol: ['none', 'circle'], edgeSymbolSize: [0, 5], lineStyle: { opacity: .6 }, emphasis: { focus: 'adjacency', scale: 1.16, lineStyle: { width: 4, opacity: 1 } } }]
  }
})

const trendOption = computed(() => ({
  animationDuration: 900, grid: { left: 22, right: 16, top: 16, bottom: 22 },
  tooltip: { trigger: 'axis', backgroundColor: 'rgba(3,20,54,.3)', borderColor: '#21cfff', textStyle: { color: '#e9fbff' } },
  xAxis: { type: 'category', boundaryGap: false, data: [], axisLine: { lineStyle: { color: 'rgba(83,190,255,.26)' } }, axisLabel: { color: '#78a9c8', fontSize: 9 } },
  yAxis: { type: 'value', splitNumber: 3, axisLabel: { color: '#78a9c8', fontSize: 9 }, splitLine: { lineStyle: { color: 'rgba(83,190,255,.10)' } } },
  series: [],
  graphic: { type: 'text', left: 'center', top: 'middle', style: { text: '接口暂未提供单技能历史趋势', fill: '#78a9c8', fontSize: 12 } }
}))

const categories = computed<string[]>(() => props.compare?.categories || [])
const domains = computed<any[]>(() => props.compare?.matrix?.slice(0, 8) || [])
const compareSkillCount = computed(() => new Set(domains.value.flatMap((row) => (row.topSkills || []).map((item: any) => item.name).filter(Boolean))).size)
const leftDomains = computed(() => domains.value.slice(0, 4))
const rightDomains = computed(() => domains.value.slice(4, 8))
const activeDomainName = ref('')
watch(domains, (rows) => { if (!rows.some((row) => row.domain === activeDomainName.value)) activeDomainName.value = rows[0]?.domain || '' }, { immediate: true })
const activeDomain = computed(() => domains.value.find((row) => row.domain === activeDomainName.value) || domains.value[0] || { domain: '暂无数据', topSkills: [], categories: {} })
const topDomain = computed(() => [...domains.value].sort((a, b) => domainRawTotal(b) - domainRawTotal(a))[0])
const palette = ['#1ba7ff', '#20ded0', '#8f61ff', '#24d17f', '#ff8b2e', '#ee4e9d', '#3c87ff', '#3be4ff']

function domainRawTotal(domain: any) { return Object.values(domain?.categories || {}).reduce((sum: number, value: any) => sum + Number(value || 0), 0) }
function domainShare(domain: any) { const total = domains.value.reduce((sum, row) => sum + domainRawTotal(row), 0) || 1; return Math.max(1, Math.round(domainRawTotal(domain) / total * 100)) }
function skillWeight(skill: any, domain: any) { const max = Math.max(...(domain?.topSkills || []).map((item: any) => Number(item.weight || 0)), 1); return Math.max(8, Math.round(Number(skill.weight || 0) / max * 31)) }
function domainIcon(name: string) { if (name.includes('人工')) return 'AI'; if (name.includes('云')) return '☁'; if (name.includes('安全')) return '⬡'; if (name.includes('数据')) return '▦'; if (name.includes('物联')) return '⌁'; if (name.includes('软件')) return '</>'; return '◇' }
function handleDomainClick(params: any) { const rootName = params?.treePathInfo?.[1]?.name || params?.data?.domainName; if (rootName && domains.value.some((row) => row.domain === rootName)) activeDomainName.value = rootName }

const sunburstOption = computed(() => {
  const activeIndex = Math.max(0, domains.value.findIndex((row) => row.domain === activeDomainName.value))
  const activeColor = palette[activeIndex % palette.length]
  const activeSkills = (activeDomain.value.topSkills || []).slice(0, 5)

  return {
    backgroundColor: 'transparent',
    animationDuration: 850,
    animationDurationUpdate: 850,
    animationEasingUpdate: 'cubicInOut',
    tooltip: {
      backgroundColor: 'rgba(1,12,28,.35)',
      borderColor: '#5be5ff',
      borderWidth: 1,
      padding: [9, 12],
      textStyle: { color: '#e9fbff', fontSize: 12 },
      formatter: (params: any) => params.seriesName === '领域结构'
        ? `<b>${params.data.domainName}</b><br/>领域占比：${params.percent.toFixed(1)}%<br/><span style="color:#67dcff">点击展开核心技能</span>`
        : `<b>${params.data.fullName}</b><br/>能力权重：${params.value}`
    },
    series: [
      {
        name: '领域结构',
        type: 'pie',
        center: ['50%', '47%'],
        radius: ['27%', '58%'],
        startAngle: 90,
        clockwise: true,
        selectedMode: 'single',
        selectedOffset: 7,
        avoidLabelOverlap: true,
        itemStyle: { borderColor: '#010810', borderWidth: 4 },
        emphasis: { scale: true, scaleSize: 8, label: { fontSize: 14 } },
        labelLine: { show: false },
        label: {
          show: true,
          position: 'inside',
          color: '#effcff',
          fontSize: 11,
          fontWeight: 800,
          lineHeight: 17,
          textShadowBlur: 6,
          textShadowColor: '#000',
          formatter: (params: any) => `${params.name}\n${params.percent.toFixed(0)}%`
        },
        data: domains.value.map((domain, index) => ({
          name: domain.domain,
          domainName: domain.domain,
          value: Math.max(1, domainRawTotal(domain)),
          selected: domain.domain === activeDomainName.value,
          itemStyle: {
            color: {
              type: 'linear', x: 0, y: 0, x2: 1, y2: 1,
              colorStops: [
                { offset: 0, color: '#05111e' },
                { offset: .38, color: `${palette[index % palette.length]}66` },
                { offset: .72, color: palette[index % palette.length] },
                { offset: 1, color: '#07101a' }
              ]
            },
            borderColor: domain.domain === activeDomainName.value ? '#c8f8ff' : '#020a12',
            borderWidth: domain.domain === activeDomainName.value ? 4 : 3,
            shadowBlur: domain.domain === activeDomainName.value ? 20 : 5,
            shadowColor: palette[index % palette.length]
          }
        }))
      },
      {
        name: `${activeDomain.value.domain}核心技能`,
        type: 'pie',
        center: ['50%', '47%'],
        radius: ['67%', '84%'],
        startAngle: 90,
        clockwise: true,
        minAngle: 12,
        avoidLabelOverlap: true,
        labelLine: { show: false },
        emphasis: { scale: true, scaleSize: 5 },
        label: {
          show: true,
          position: 'inside',
          color: '#f0fcff',
          fontSize: 10,
          fontWeight: 700,
          lineHeight: 15,
          textShadowBlur: 6,
          textShadowColor: '#000',
          formatter: (params: any) => `${params.data.shortName}\n${params.percent.toFixed(0)}%`
        },
        itemStyle: { borderColor: '#010810', borderWidth: 3 },
        data: activeSkills.map((skill: any, index: number) => ({
          name: skill.name,
          fullName: skill.name,
          shortName: String(skill.name).length > 7 ? `${String(skill.name).slice(0, 7)}…` : skill.name,
          value: Math.max(.1, Number(skill.weight || 1)),
          itemStyle: {
            color: {
              type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
              colorStops: [
                { offset: 0, color: '#07111b' },
                { offset: .42, color: `${activeColor}88` },
                { offset: .78, color: palette[(activeIndex + index + 1) % palette.length] },
                { offset: 1, color: '#0d1d27' }
              ]
            },
            shadowBlur: 6,
            shadowColor: activeColor
          }
        }))
      }
    ],
    graphic: [
      { type: 'circle', left: 'center', top: 'center', shape: { r: 99 }, style: { fill: 'transparent', stroke: 'rgba(89,222,255,.22)', lineWidth: 1 } },
      { type: 'circle', left: 'center', top: 'center', shape: { r: 176 }, style: { fill: 'transparent', stroke: 'rgba(89,222,255,.12)', lineWidth: 1, lineDash: [3, 7] } },
      { type: 'text', left: 'center', top: '39%', silent: true, style: { text: '领域能力\n结构全景', fill: '#e9fbff', font: '800 20px sans-serif', textAlign: 'center', lineHeight: 29 } },
      { type: 'text', left: 'center', top: '51%', silent: true, style: { text: activeDomain.value.domain, fill: activeColor, font: '900 17px sans-serif', textAlign: 'center', textShadowBlur: 10, textShadowColor: activeColor } }
    ]
  }
})
</script>

<style scoped>
.version-dashboard {
  --v-bg: #020915;
  --v-panel: #06162a;
  --v-cyan: #55efff;
  --v-cyan2: #00b7e8;
  --v-line: rgba(76, 216, 255, .55);
  --v-gold: #ffd66b;
  --v-white: #eafcff;
  --v-muted: #78a9c7;
  --v-red: #ff785f;
  --v-green: #4bffd0;
  position: relative;
  width: 100%;
  min-height: 900px;
  color: var(--v-white);
  font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
  background: rgba(3, 16, 30, 0.15);
  overflow: hidden;
  padding-bottom: 100px;
  border-radius: 12px;
  backdrop-filter: blur(10px) saturate(1.1);
  border: 1px solid rgba(70, 200, 255, 0.2);
}



.v-top-bar {
  position: relative;
  height: 10.6%;
  min-height: 70px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  overflow: hidden;
}
.v-top-bar::before, .v-top-bar::after {
  content: "";
  position: absolute;
  top: 5px;
  width: 34%;
  height: 35px;
  border-top: 1px solid #1ddfff;
  opacity: .45;
}
.v-top-bar::before {
  left: 0;
  clip-path: polygon(0 0, 93% 0, 100% 100%, 12% 100%, 7% 62%, 0 62%);
  background: linear-gradient(180deg, rgba(0,174,255,.12), transparent);
}
.v-top-bar::after {
  right: 0;
  clip-path: polygon(7% 0, 100% 0, 100% 62%, 93% 62%, 88% 100%, 0 100%);
  background: linear-gradient(180deg, rgba(0,174,255,.12), transparent);
}
.v-title-box {
  margin-top: 0;
  width: 31%;
  min-width: 380px;
  height: 72%;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  clip-path: polygon(9% 0, 91% 0, 86% 70%, 80% 100%, 20% 100%, 14% 70%);
  background: linear-gradient(180deg, rgba(13,89,128,.46), rgba(1,25,45,.9));
  border-top: 1px solid #47ebff;
  filter: drop-shadow(0 0 8px rgba(42,218,255,.65));
}
.v-title-box::after {
  content: "";
  position: absolute;
  inset: 1px;
  clip-path: inherit;
  border: 1px solid rgba(99,238,255,.75);
}
.v-title-main {
  font-size: clamp(18px, 2vw, 28px);
  font-weight: 900;
  letter-spacing: 2px;
  color: #fff;
  text-shadow: 0 0 7px #6fefff, 0 0 18px #00aede;
  z-index: 1;
}
.v-title-sub {
  font-size: clamp(10px, .95vw, 14px);
  font-weight: 700;
  margin-top: 4px;
  text-shadow: 0 0 6px #49d9ff;
  z-index: 1;
}

.v-main-layout {
  position: relative;
  display: grid;
  grid-template-columns: 16.4% 1fr 16.7%;
  gap: 0 1.1%;
  padding: 0 .7% .8%;
  height: calc(89.4% - 10px);
  min-height: 700px;
}
.v-col { display: flex; flex-direction: column; gap: 1.25%; min-height: 0; }
.v-col-left { grid-column: 1; }
.v-col-center { grid-column: 2; display: grid; grid-template-rows: 57% 43%; gap: 1.2%; min-width: 0; min-height: 0; }
.v-col-right { grid-column: 3; }

.v-panel {
  position: relative;
  background: linear-gradient(180deg, rgba(6,28,53,.10), rgba(4,18,35,.12));
  border: 1px solid rgba(67,208,255,.25);
  box-shadow: inset 0 0 28px rgba(0,141,211,.04), 0 0 10px rgba(0,148,213,.03);
  overflow: hidden;
  backdrop-filter: blur(6px) saturate(1.05);
  border-radius: 8px;
}
.v-col-left .v-panel {
  border-color: rgba(91,228,255,.5);
  box-shadow: inset 0 0 30px rgba(0,166,227,.08), inset 3px 0 0 rgba(85,239,255,.35), 0 0 0 1px rgba(71,210,255,.1), 0 0 12px rgba(0,148,213,.05);
}
.v-panel::before, .v-panel::after {
  content: "";
  position: absolute;
  width: 18px;
  height: 10px;
  z-index: 2;
}
.v-panel::before {
  left: -1px; top: -1px;
  border-left: 3px solid var(--v-cyan);
  border-top: 3px solid var(--v-cyan);
  box-shadow: 0 0 8px rgba(108,239,255,.45);
}
.v-panel::after {
  right: -1px; bottom: -1px;
  border-right: 3px solid var(--v-cyan);
  border-bottom: 3px solid var(--v-cyan);
  box-shadow: 0 0 8px rgba(108,239,255,.35);
}
.v-col-left .v-panel::before {
  width: 20px; height: 12px;
  border-left: 3px solid #6cefff;
  border-top: 3px solid #6cefff;
  box-shadow: 0 0 8px rgba(108,239,255,.45);
}
.v-col-left .v-panel::after {
  width: 20px; height: 12px;
  border-right: 3px solid #6cefff;
  border-bottom: 3px solid #6cefff;
  box-shadow: 0 0 8px rgba(108,239,255,.35);
}

.v-panel-head {
  height: 17%;
  min-height: 30px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 7%;
  font-size: clamp(12px, 1vw, 16px);
  font-weight: 800;
  color: #eefcff;
  letter-spacing: .5px;
  background: linear-gradient(90deg, rgba(0,182,234,.10), transparent 75%);
}
.v-col-left .v-panel-head {
  background: linear-gradient(90deg, rgba(0,193,243,.18), rgba(0,122,177,.08) 46%, transparent 92%);
  border-bottom: 1px solid rgba(91,228,255,.24);
}
.v-panel-head small {
  font-size: .52em;
  color: #a5d9ee;
  letter-spacing: 1px;
}

.v-col-left .v-panel > :not(.v-panel-head) {
  position: relative;
}
.v-col-left .v-panel > :not(.v-panel-head)::before {
  content: "";
  position: absolute;
  inset: 6px;
  border: 1px solid rgba(93,231,255,.15);
  pointer-events: none;
  clip-path: polygon(0 7px, 7px 0, calc(100% - 7px) 0, 100% 7px, 100% calc(100% - 7px), calc(100% - 7px) 100%, 7px 100%, 0 calc(100% - 7px));
}
.v-col-left .v-panel > :not(.v-panel-head)::after {
  content: "";
  position: absolute;
  left: 9px;
  top: 9px;
  width: 28px;
  height: 8px;
  border-top: 1px solid rgba(96,235,255,.35);
  border-left: 1px solid rgba(96,235,255,.35);
  opacity: .55;
  pointer-events: none;
}
.v-metric, .v-gauge, .v-skill {
  position: relative;
  z-index: 1;
}

.v-col-left .v-panel:nth-child(1) { height: 28%; }
.v-col-left .v-panel:nth-child(2) { height: 24%; }
.v-col-left .v-panel:nth-child(3) { flex: 1; }

.v-metric-grid {
  height: 83%;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  align-items: center;
  padding: 0 5% 6%;
}
.v-metric {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
.v-m-val {
  font-size: clamp(18px, 1.7vw, 28px);
  font-weight: 900;
  color: #eaffff;
  text-shadow: 0 0 8px #69eaff;
}
.v-m-label {
  font-size: clamp(8px, .58vw, 11px);
  color: #a6c9dc;
}
.v-m-delta {
  font-size: clamp(11px, .7vw, 14px);
  font-weight: 900;
}
.v-m-delta.up { color: var(--v-green); }
.v-m-delta.warn { color: var(--v-gold); }
.v-m-delta.down { color: var(--v-red); }
.v-m-delta.cyan { color: var(--v-cyan); }
.v-m-delta.gold { color: var(--v-gold); }

.v-mini-ring {
  width: clamp(34px, 3vw, 52px);
  aspect-ratio: 1;
  border-radius: 50%;
  display: grid;
  place-items: center;
  border: 2px solid rgba(75,238,255,.35);
  position: relative;
  background: radial-gradient(circle, rgba(34,146,194,.15), transparent 63%);
}
.v-mini-ring::after {
  content: "";
  position: absolute;
  inset: 3px;
  border-radius: 50%;
  border: 2px solid var(--v-cyan);
  border-left-color: transparent;
  filter: drop-shadow(0 0 4px var(--v-cyan));
}

.v-gauge-grid {
  height: 83%;
  display: grid;
  grid-template-columns: 1fr 1fr;
  place-items: center;
  padding: 0 8% 5%;
}
.v-gauge {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.v-gauge-ring {
  width: clamp(54px, 5.5vw, 80px);
  aspect-ratio: 1;
  border-radius: 50%;
  position: relative;
  display: grid;
  place-items: center;
  background: radial-gradient(circle, rgba(6,39,68,.45) 0 47%, transparent 49%);
  --gc: var(--v-cyan);
}
.v-gauge-ring.green { --gc: var(--v-green); }
.v-gauge-ring.gold { --gc: var(--v-gold); }
.v-gauge-ring.red { --gc: var(--v-red); }
.v-gauge-ring::before {
  content: "";
  position: absolute;
  inset: 2px;
  border-radius: 50%;
  background: conic-gradient(var(--gc) 0 78%, rgba(53,124,160,.3) 78%);
  mask: radial-gradient(circle, transparent 0 58%, #000 59%);
  filter: drop-shadow(0 0 5px var(--gc));
}
.v-g-num {
  font-size: clamp(20px, 1.7vw, 28px);
  font-weight: 900;
  position: relative;
  z-index: 1;
}
.v-g-label {
  font-size: clamp(9px, .62vw, 12px);
  color: #b4d8e9;
}

.v-skill-grid {
  height: 83%;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 6%;
  padding: 6% 6% 10%;
}
.v-skill {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
.v-skill-ball {
  width: clamp(38px, 3.4vw, 56px);
  aspect-ratio: 1;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-weight: 900;
  font-size: clamp(12px, 1vw, 16px);
  border: 2px solid rgba(74,233,255,.66);
  box-shadow: inset 0 0 16px rgba(0,177,230,.24), 0 0 8px rgba(71,233,255,.14);
  color: var(--v-white);
}
.v-skill-ball.green { border-color: var(--v-green); color: #a5ffe4; }
.v-skill-ball.gold { border-color: var(--v-gold); color: #ffe393; }
.v-skill-ball.red { border-color: var(--v-red); color: #ff9f8d; }
.v-skill label {
  font-size: clamp(8px, .55vw, 11px);
  color: #9ec8db;
}

.v-hero-panel {
  position: relative;
  min-height: 0;
  overflow: hidden;
  background: linear-gradient(180deg, rgba(6,28,53,.32), rgba(4,18,35,.38));
  border: 1px solid rgba(67,208,255,.45);
  box-shadow: inset 0 0 28px rgba(0,141,211,.08), 0 0 10px rgba(0,148,213,.06);
  backdrop-filter: blur(12px) saturate(1.08);
  border-radius: 8px;
}
.v-corner-tl, .v-corner-br {
  position: absolute;
  width: 20px;
  height: 12px;
  z-index: 6;
  pointer-events: none;
}
.v-corner-tl {
  left: -1px; top: -1px;
  border-left: 3px solid #6cefff;
  border-top: 3px solid #6cefff;
  box-shadow: 0 0 8px rgba(108,239,255,.45);
}
.v-corner-br {
  right: -1px; bottom: -1px;
  border-right: 3px solid #6cefff;
  border-bottom: 3px solid #6cefff;
  box-shadow: 0 0 8px rgba(108,239,255,.35);
}
.v-hero-bg {
  content: "";
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at 50% 72%, rgba(2,150,203,.11), transparent 48%),
    linear-gradient(180deg, rgba(1,19,31,.04), rgba(1,10,20,.34));
  pointer-events: none;
}
.v-hero-glow {
  content: "";
  position: absolute;
  inset: 8% 14% auto 14%;
  height: 55%;
  pointer-events: none;
  opacity: .18;
  background:
    radial-gradient(circle at 18% 55%, rgba(84,242,255,.35), transparent 35%),
    radial-gradient(circle at 50% 52%, rgba(255,216,110,.28), transparent 35%),
    radial-gradient(circle at 82% 55%, rgba(219,232,255,.30), transparent 35%);
}
.v-hero-grid-floor {
  position: absolute;
  left: 0; right: 0; bottom: 0;
  height: 35%;
  opacity: .28;
  background-image:
    linear-gradient(rgba(72,225,255,.18) 1px, transparent 1px),
    linear-gradient(90deg, rgba(72,225,255,.18) 1px, transparent 1px);
  background-size: 33px 20px;
  transform: perspective(340px) rotateX(61deg);
  transform-origin: bottom center;
}
.v-scan-line {
  position: absolute;
  left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, #ff6a54 50%, transparent);
  box-shadow: 0 0 7px #ff704c;
  opacity: .65;
  animation: v-scan 5s linear infinite;
  z-index: 5;
}
@keyframes v-scan {
  0% { top: 20%; opacity: 0; }
  10% { opacity: .7; }
  60% { opacity: .3; }
  100% { top: 95%; opacity: 0; }
}

.v-holo-row {
  position: absolute;
  inset: 5% 1% 0;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5%;
}
.v-holo-card {
  position: relative;
  text-align: center;
  min-width: 0;
  --glow: var(--v-cyan);
}
.v-holo-card::before {
  content: "";
  position: absolute;
  inset: 6% 7% 6% 7%;
  clip-path: polygon(6% 0, 94% 0, 100% 12%, 100% 88%, 94% 100%, 6% 100%, 0 88%, 0 12%);
  border: 1px solid color-mix(in srgb, var(--glow) 40%, transparent);
  background: linear-gradient(180deg, rgba(5,37,61,.06), rgba(5,28,46,.02));
  box-shadow: inset 0 0 18px rgba(71,225,255,.05);
  pointer-events: none;
}
.v-holo-title {
  font-size: clamp(11px, .95vw, 16px);
  font-weight: 800;
  color: #eefcff;
  text-shadow: 0 0 6px var(--glow);
  position: absolute;
  top: 1%;
  left: 0; right: 0;
  z-index: 6;
}
.v-holo-count {
  display: block;
  font-size: clamp(20px, 1.7vw, 28px);
  line-height: 1;
  margin-top: 3px;
  color: var(--glow);
}
.v-holo-frame {
  position: absolute;
  left: -5%; right: -5%; top: 2%; bottom: 8%;
  z-index: 3;
  overflow: hidden;
}
.v-core-img {
  position: absolute;
  left: 50%;
  top: 48%;
  transform: translate(-50%, -50%);
  width: 125%;
  height: 120%;
  object-fit: contain;
  mix-blend-mode: screen;
  opacity: 1;
  filter: brightness(1.2) saturate(1.25) drop-shadow(0 0 20px var(--glow));
  z-index: 1;
}
.v-core-img.core-left {
  width: 120%;
  height: 125%;
  clip-path: inset(0 0 0 0);
}
.v-core-img.core-center {
  width: 125%;
  height: 115%;
  top: 47%;
}
.v-core-img.core-right {
  width: 130%;
  height: 120%;
  clip-path: inset(0 0 0 0);
}
.v-core-mask {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 48%, rgba(255,255,255,.06), transparent 32%);
  pointer-events: none;
  z-index: 2;
}
.v-holo-corner-l, .v-holo-corner-r {
  position: absolute;
  top: 5%;
  width: 18%;
  height: 10%;
  border-top: 1px solid rgba(255,255,255,.18);
  opacity: .3;
  z-index: 4;
}
.v-holo-corner-l {
  left: 6%;
  border-left: 1px solid rgba(255,255,255,.18);
  clip-path: polygon(0 0, 100% 0, 75% 100%, 0 100%);
}
.v-holo-corner-r {
  right: 6%;
  border-right: 1px solid rgba(255,255,255,.18);
  clip-path: polygon(25% 0, 100% 0, 100% 100%, 0 100%);
}
.v-holo-pillar {
  position: absolute;
  left: 50%;
  bottom: 25%;
  transform: translateX(-50%);
  width: 10%;
  height: 35%;
  background: linear-gradient(180deg, rgba(255,255,255,.18), rgba(255,255,255,0) 12%, color-mix(in srgb, var(--glow) 60%, transparent) 60%, transparent 100%);
  filter: blur(1px);
  opacity: .38;
  z-index: 4;
}
.v-holo-halo {
  position: absolute;
  left: 12%; right: 12%; top: 50%;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--glow) 30%, var(--glow) 70%, transparent);
  opacity: .18;
  z-index: 4;
}
.v-holo-float {
  position: absolute;
  left: 50%;
  transform: translateX(-50%) rotate(-5deg);
  width: 44%;
  height: 8%;
  border-radius: 50%;
  border: 1.5px solid color-mix(in srgb, var(--glow) 70%, white 30%);
  opacity: .45;
  box-shadow: 0 0 8px color-mix(in srgb, var(--glow) 60%, transparent);
  z-index: 4;
}
.v-holo-float.r1 { top: 15%; }
.v-holo-float.r2 { top: 28%; width: 34%; height: 6%; transform: translateX(-50%) rotate(6deg); opacity: .35; }
.v-holo-float.r3 { top: 40%; width: 28%; height: 5%; transform: translateX(-50%) rotate(-8deg); opacity: .22; }
.v-holo-orbit {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  border-radius: 50%;
  border: 1.6px solid color-mix(in srgb, var(--glow) 72%, white 28%);
  box-shadow: 0 0 8px color-mix(in srgb, var(--glow) 55%, transparent);
  opacity: .58;
  z-index: 4;
}
.v-holo-orbit.o1 { bottom: 18%; width: 82%; height: 14%; }
.v-holo-orbit.o2 { bottom: 22%; width: 64%; height: 10%; opacity: .42; }
.v-holo-orbit.o3 { bottom: 26%; width: 46%; height: 7%; opacity: .34; }
.v-holo-orbit.o4 { bottom: 30%; width: 28%; height: 4.4%; opacity: .25; }
.v-holo-stage-label {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  font-size: clamp(9px, .7vw, 12px);
  font-weight: 700;
  color: var(--glow);
  padding: 2px 10px;
  background: rgba(2,24,39,.35);
  border: 1px solid rgba(76,219,255,.25);
  z-index: 6;
  backdrop-filter: blur(6px);
}
.v-holo-skills {
  position: absolute;
  bottom: 8%;
  left: 0;
  right: 0;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 4px;
  padding: 0 5%;
  z-index: 5;
}
.v-holo-skill-tag {
  border: 1px solid color-mix(in srgb, var(--glow) 50%, transparent);
  padding: 2px 6px;
  font-size: 9px;
  color: var(--v-white);
  background: rgba(2, 24, 39, .3);
  white-space: nowrap;
  backdrop-filter: blur(4px);
}

.v-chart-panel {
  position: relative;
  background: linear-gradient(180deg, rgba(6,28,53,.32), rgba(4,18,35,.38));
  border: 1px solid rgba(67,208,255,.45);
  box-shadow: inset 0 0 28px rgba(0,141,211,.08), 0 0 10px rgba(0,148,213,.06);
  padding: 0 .7% .7%;
  backdrop-filter: blur(12px) saturate(1.08);
  border-radius: 8px;
}
.v-chart-empty { display: grid; height: 100%; min-height: 210px; place-items: center; padding: 24px; color: #78a9c8; font-size: 12px; text-align: center; }

.v-tree-panel {
  height: 460px;
  padding: 12px;
}

.v-panel-title {
  position: absolute;
  top: 12px;
  left: 16px;
  z-index: 10;
  font-size: 13px;
  font-weight: 600;
  color: #71efff;
  letter-spacing: 1px;
  text-shadow: 0 0 10px rgba(113, 239, 255, 0.5);
}

.v-tree-panel :deep(.skill-tree-container) {
  position: absolute;
  inset: 0;
  border-radius: 8px;
}
.v-trend-svg {
  width: 100%;
  height: 100%;
}

.v-col-right .v-panel:nth-child(1) { height: 31%; }
.v-col-right .v-panel:nth-child(2) { height: 37%; }
.v-col-right .v-panel:nth-child(3) { flex: 1; }

.v-intel-body {
  height: 83%;
  display: grid;
  place-items: center;
  position: relative;
}
.v-big-ring {
  width: clamp(92px, 8.5vw, 130px);
  aspect-ratio: 1;
  border-radius: 50%;
  position: relative;
  display: grid;
  place-items: center;
  background: radial-gradient(circle, rgba(17,63,92,.4) 0 46%, transparent 47%);
}
.v-big-ring::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: conic-gradient(#ffe56e 0 18%, #80f4ff 18% 74%, rgba(42,97,124,.28) 74%);
  mask: radial-gradient(circle, transparent 0 65%, #000 66%);
  filter: drop-shadow(0 0 5px #55eaff);
}
.v-big-ring::after {
  content: "";
  position: absolute;
  inset: 10%;
  border-radius: 50%;
  border: 1px solid rgba(96,231,255,.25);
}
.v-big-v {
  font-size: clamp(22px, 2.2vw, 34px);
  font-weight: 900;
  color: #fff;
  text-align: center;
  position: relative;
  z-index: 1;
}
.v-big-t {
  font-size: clamp(9px, .7vw, 12px);
  color: #b9ddec;
  text-align: center;
}

.v-dim-list {
  height: 83%;
  padding: 3% 7%;
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
}
.v-list-row {
  height: 15%;
  border: 1px solid rgba(71,192,232,.22);
  background: rgba(3,40,65,.25);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 6%;
  font-size: clamp(8px, .62vw, 11px);
  color: #d7f6ff;
  backdrop-filter: blur(6px);
}
.v-item-label {
  display: flex;
  align-items: center;
}
.v-item-val {
  font-weight: 800;
  color: var(--v-cyan);
}
.v-row-bullet {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #62f3ff;
  box-shadow: 0 0 6px #62f3ff;
  margin-right: 6px;
  display: inline-block;
}
.v-row-bullet.gold { background: var(--v-gold); box-shadow: 0 0 6px var(--v-gold); }
.v-row-bullet.red { background: var(--v-red); box-shadow: 0 0 6px var(--v-red); }
.v-row-bullet.green { background: var(--v-green); box-shadow: 0 0 6px var(--v-green); }

.v-metrics-body {
  height: 83%;
  padding: 4% 6%;
  display: flex;
  flex-direction: column;
  gap: 4%;
}
.v-bar-group {
  display: flex;
  flex-direction: column;
  gap: 6%;
  flex: 0 0 auto;
}
.v-bar-line {
  display: grid;
  grid-template-columns: 1fr 42%;
  align-items: center;
  font-size: clamp(8px, .55vw, 10px);
  color: #b7d8e7;
  gap: 4px;
}
.v-bar-bg {
  height: 6px;
  border: 1px solid rgba(76,222,255,.28);
  background: rgba(28,87,111,.25);
}
.v-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #188be8, #66f3ff);
  box-shadow: 0 0 5px #47e9ff;
}
.v-num-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2%;
  text-align: center;
  border-top: 1px solid rgba(73,209,255,.2);
  padding-top: 4%;
}
.v-num-cell b {
  display: block;
  font-size: clamp(13px, 1vw, 17px);
  color: #dffcff;
}
.v-num-cell small {
  font-size: clamp(7px, .48vw, 9px);
  color: #81aabf;
}
.v-spark-line {
  flex: 1;
  min-height: 42px;
  border-top: 1px solid rgba(57,198,238,.18);
  padding-top: 4%;
}
.v-spark-line svg {
  width: 100%;
  height: 100%;
}

.v-footer-strip {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 90px;
  display: flex;
  align-items: stretch;
  gap: 8px;
  padding: 10px;
  background: linear-gradient(180deg, rgba(6,28,53,.35), rgba(4,18,35,.45));
  border-top: 1px solid rgba(67,208,255,.35);
  z-index: 10;
  backdrop-filter: blur(12px) saturate(1.08);
}
.v-strip-arrow {
  width: 34px;
  flex: 0 0 auto;
  border: 1px solid rgba(70, 205, 255, .4);
  color: #70eaff;
  font-size: 25px;
  background: rgba(5, 45, 96, .35);
  cursor: pointer;
  backdrop-filter: blur(8px);
}
.v-strip-title {
  display: flex;
  width: 128px;
  flex: 0 0 auto;
  flex-direction: column;
  justify-content: center;
}
.v-strip-title small {
  color: #34d7ff;
  font-size: 8px;
  letter-spacing: .14em;
}
.v-strip-title b {
  color: #dff9ff;
  font-size: 12px;
}
.v-role-cards {
  display: flex;
  flex: 1;
  gap: 8px;
  overflow-x: auto;
}
.v-role-card {
  display: flex;
  min-width: 180px;
  flex: 1 1 0;
  flex-direction: column;
  gap: 5px;
  border: 1px solid rgba(63, 178, 237, .25);
  padding: 9px;
  color: #b9def0;
  text-align: left;
  background: rgba(4, 33, 75, .35);
  cursor: pointer;
  transition: .2s ease;
  backdrop-filter: blur(8px);
}
.v-role-card:hover, .v-role-card.active {
  border-color: #33d9ff;
  background: rgba(7, 66, 126, .45);
  box-shadow: inset 0 -2px #2bd9ff, 0 0 14px rgba(38, 207, 255, .17);
  transform: translateY(-2px);
}
.v-role-card span {
  overflow: hidden;
  color: #e3f9ff;
  font-size: 11px;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.v-role-card span i {
  margin-right: 6px;
  color: #35ddff;
  font-style: normal;
}
.v-role-card em {
  color: #66bde5;
  font-size: 9px;
  font-style: normal;
}
.v-role-card > b {
  font-size: 11px;
}
.v-role-card strong.up { color: #4bffd0; }
.v-role-card span.warn { color: #ffd25c; }
.v-role-card i.down { color: #ff785f; font-style: normal; }

.evo-view { --cyan: #5ce7ff; --line: rgba(83, 203, 255, .24); --panel: rgba(1, 9, 23, .94); position: relative; isolation: isolate; display: grid; gap: 14px; min-height: 690px; color: #c9ecff; background: rgba(4, 22, 50, 0.06); border-radius: 12px; backdrop-filter: blur(4px) saturate(1.02); border: 1px solid rgba(70, 200, 255, 0.12); padding: 8px; }
.evo-view::before { position: absolute; z-index: -1; inset: 22% 0 0; content: ''; opacity: .25; background: repeating-linear-gradient(90deg, transparent 0 61px, rgba(45, 141, 203, .04) 62px 63px), repeating-linear-gradient(0deg, transparent 0 48px, rgba(45, 141, 203, .03) 49px 50px); mask-image: linear-gradient(to bottom, transparent, #000 34%, #000); transform: perspective(520px) rotateX(61deg) scale(1.25); transform-origin: bottom; pointer-events: none; }
button { font: inherit; }
.hud-panel { position: relative; border: 1px solid rgba(83, 203, 255, .2); color: inherit; background: linear-gradient(145deg, rgba(4, 18, 39, .15), rgba(0, 6, 18, .12) 72%); box-shadow: inset 0 1px rgba(205, 246, 255, .05), inset 0 0 44px rgba(17, 94, 146, .02), 0 18px 36px rgba(0, 2, 12, .08); clip-path: polygon(0 12px, 12px 0, calc(100% - 22px) 0, 100% 22px, 100% calc(100% - 12px), calc(100% - 12px) 100%, 14px 100%, 0 calc(100% - 14px)); backdrop-filter: blur(6px) saturate(1.05); }
.hud-panel::before, .hud-panel::after { position: absolute; z-index: 2; width: 36px; height: 2px; content: ''; background: #31dfff; box-shadow: 0 0 10px #22cfff; pointer-events: none; }
.hud-panel::before { top: 0; left: 22px; }.hud-panel::after { right: 22px; bottom: 0; }
.hud-stack, .domain-stack { display: flex; min-width: 0; flex-direction: column; gap: 13px; }
.hud-stack > .hud-panel { padding: 15px; }
.panel-title { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 12px; }
.panel-title h3 { margin: 0; color: #eafaff; font-size: 15px; letter-spacing: .02em; }.panel-title h3::before { margin-right: 8px; color: var(--cyan); content: '‹'; }.panel-title small { color: #45dfff; font-size: 9px; font-weight: 800; letter-spacing: .14em; }
.tone-add { color: #34efb6 !important; }.tone-mod { color: #ffbd3e !important; }.tone-remove { color: #ff7797 !important; }

.hotspot-view, .compare-view { grid-template-columns: 260px minmax(640px, 1fr) 315px; }.hot-summary { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }.hot-summary span { position: relative; border: 1px solid rgba(55, 182, 244, .15); padding: 10px; color: #85b7d2; font-size: 9px; background: rgba(5, 47, 96, .1); backdrop-filter: blur(4px); }.hot-summary span > i { float: left; margin-right: 8px; color: #35ddff; font-size: 20px; font-style: normal; }.hot-summary b { display: block; color: #e9fcff; font-size: 22px; }.hot-summary em { display: block; margin-top: 3px; color: #37e8ad; font-style: normal; }.hot-summary em.down { color: #ff7895; }
.hot-trend-panel { min-height: 195px; }.mini-echart { height: 145px; }.heat-distribution { min-height: 168px; }.heat-donut { float: left; display: grid; place-items: center; width: 96px; height: 96px; margin-right: 12px; border-radius: 50%; background: radial-gradient(circle, rgba(5,35,84,.15) 54%, transparent 56%), conic-gradient(#ffb52e 0 10%, #37e6a1 10% 34%, #a26cff 34% 69%, #28cfff 69%); }.heat-donut b { color: #effdff; font-size: 23px; }.heat-donut small { color: #8cb8d0; font-size: 9px; }.heat-distribution ul { display: grid; gap: 7px; margin: 0; padding: 0; list-style: none; }.heat-distribution li { display: flex; align-items: center; color: #8fbad1; font-size: 9px; }.heat-distribution li i { width: 7px; height: 7px; margin-right: 6px; border-radius: 50%; background: currentColor; }.heat-distribution li b { margin-left: auto; color: #dff7ff; }.insight-panel.compact { min-height: 105px; }.insight-panel.compact b { color: #48e1ff; }
.graph-command, .domain-command { position: relative; min-width: 0; overflow: hidden; background: linear-gradient(180deg, rgba(4,18,39,.1), rgba(0,6,18,.12)); border: 1px solid rgba(83,203,255,.2); backdrop-filter: blur(6px) saturate(1.05); border-radius: 8px; }.graph-command { min-height: 690px; }.graph-command::after, .domain-command::after { width: auto; height: auto; inset: 0; opacity: .15; background-image: radial-gradient(circle, rgba(104, 222, 255, .32) 0 1px, transparent 1px), linear-gradient(rgba(34, 142, 217, .03) 1px, transparent 1px), linear-gradient(90deg, rgba(34, 142, 217, .03) 1px, transparent 1px); background-size: 31px 31px, 58px 58px, 58px 58px; box-shadow: none; }.graph-title { position: absolute; z-index: 5; top: 17px; left: 21px; display: flex; right: 21px; align-items: end; justify-content: space-between; }.graph-title > span { color: #6fb9db; font-size: 9px; }.hotspot-chart { position: relative; z-index: 2; height: 640px; margin-top: 36px; }.hotspot-chart::before, .hotspot-chart::after { position: absolute; z-index: 1; top: 50%; left: 50%; border: 1px solid rgba(85, 222, 255, .15); border-radius: 50%; content: ''; pointer-events: none; }.hotspot-chart::before { width: 440px; height: 210px; box-shadow: 0 0 28px rgba(22, 165, 255, .06), inset 0 0 24px rgba(22, 165, 255, .04); transform: translate(-50%, -50%) rotate(17deg); animation: gyroA 13s cubic-bezier(.45,.05,.55,.95) infinite alternate; }.hotspot-chart::after { width: 300px; height: 520px; border-style: dashed; opacity: .4; transform: translate(-50%, -50%) rotate(-28deg); animation: gyroB 17s cubic-bezier(.45,.05,.55,.95) infinite alternate; }.active-skill-readout { position: absolute; z-index: 6; top: 79px; right: 18px; display: grid; min-width: 130px; border-right: 1px solid #83edff; padding: 7px 10px; text-align: right; background: linear-gradient(90deg, transparent, rgba(1, 22, 40, .2)); backdrop-filter: blur(6px); }.active-skill-readout span { color: #32dfff; font-size: 7px; letter-spacing: .18em; }.active-skill-readout b { color: #effdff; font-size: 12px; }.active-skill-readout strong { color: #45edbf; font-size: 21px; }.active-skill-readout em { color: #72aeca; font-size: 8px; font-style: normal; }.graph-legend { position: absolute; z-index: 6; bottom: 16px; left: 50%; display: flex; gap: 15px; border: 1px solid rgba(65, 193, 255, .15); padding: 7px 14px; color: #a5d5e9; font-size: 9px; background: rgba(0, 8, 19, .2); transform: translateX(-50%); backdrop-filter: blur(6px); }.graph-legend span::before { display: inline-block; width: 7px; height: 7px; margin-right: 5px; border-radius: 0; background: currentColor; content: ''; transform: rotate(45deg); }.level-high { color: #ffb52e !important; }.level-mid { color: #37e6a1 !important; }.level-warm { color: #a26cff !important; }.level-low { color: #28cfff !important; }
.graph-hit-targets { position: absolute; z-index: 5; inset: 60px 0 45px; pointer-events: none; }.graph-hit-targets button { position: absolute; width: 82px; height: 82px; border: 0; background: transparent; cursor: pointer; pointer-events: auto; transform: translate(-50%, -50%); clip-path: polygon(50% 0, 92% 25%, 92% 75%, 50% 100%, 8% 75%, 8% 25%); }.graph-hit-targets button:hover { outline: 1px dashed rgba(116, 238, 255, .5); outline-offset: 4px; box-shadow: 0 0 20px rgba(50, 217, 255, .1); }
.skill-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }.skill-chips button { border: 1px solid rgba(91, 214, 255, .2); padding: 4px 9px; color: #bff4ff; font-size: 10px; background: rgba(6, 45, 89, .12); cursor: pointer; backdrop-filter: blur(4px); }.skill-chips button:hover { border-color: #69efff; color: #fff; box-shadow: 0 0 10px rgba(42, 201, 255, .15); }
.sparkline { height: 28px; margin-bottom: 10px; border-radius: 4px; background: linear-gradient(90deg, rgba(54, 215, 255, .04), transparent); }.sparkline.red-line { background: linear-gradient(90deg, rgba(255, 117, 149, .04), transparent); }
.ranking-list { display: grid; gap: 6px; }.ranking-list button { display: grid; grid-template-columns: 20px 1fr auto; gap: 8px; align-items: center; width: 100%; border: 1px solid rgba(63, 178, 237, .12); padding: 7px 9px; color: #bce4f4; font-size: 10px; text-align: left; background: rgba(3, 32, 67, .1); cursor: pointer; backdrop-filter: blur(4px); }.ranking-list button:hover { border-color: rgba(95, 222, 255, .3); background: rgba(8, 52, 99, .15); }.ranking-list button i { display: grid; place-items: center; width: 18px; height: 18px; border-radius: 4px; color: #19d3ff; font-size: 9px; font-style: normal; background: rgba(13, 72, 118, .15); backdrop-filter: blur(4px); }.ranking-list button b { color: #e8fbff; font-weight: 800; }.ranking-list button em { color: #54d1aa; font-size: 9px; font-style: normal; }.declining-panel .ranking-list button em { color: #ff7e94; }
.domain-command { min-height: 640px; }.domain-chart { position: relative; z-index: 2; height: 560px; margin-top: 30px; }
.domain-focus { position: absolute; z-index: 6; top: 74px; left: 50%; display: grid; justify-items: center; gap: 2px; transform: translateX(-50%); text-align: center; }.domain-focus small { color: #3fdcff; font-size: 8px; letter-spacing: .16em; }.domain-focus b { color: #effcff; font-size: 19px; font-weight: 900; text-shadow: 0 0 12px rgba(50, 195, 255, .25); }.domain-focus strong { color: #7ef3ff; font-size: 31px; font-weight: 900; text-shadow: 0 0 16px rgba(50, 202, 255, .35); }.domain-focus span { max-width: 320px; color: #7ab0ca; font-size: 10px; line-height: 1.5; }
.wheel-note { position: absolute; z-index: 6; right: 18px; bottom: 22px; display: grid; gap: 9px; min-width: 160px; }.wheel-note span { display: flex; align-items: center; justify-content: space-between; gap: 10px; color: #89b8cf; font-size: 10px; }.wheel-note span b { color: #dff8ff; font-weight: 800; }.wheel-note span em { color: #5fe6ff; font-weight: 800; }
.domain-stack { gap: 11px; }.domain-card { display: grid; grid-template-columns: 34px 1fr; gap: 10px; padding: 12px; text-align: left; cursor: pointer; }.domain-card.active { border-color: #56e6ff; box-shadow: inset 0 0 22px rgba(14, 120, 193, .12), 0 0 16px rgba(39, 187, 255, .1); transform: translateX(-2px); }.domain-icon { display: grid; place-items: center; width: 34px; height: 34px; border-radius: 8px; color: #89f2ff; font-size: 12px; font-weight: 800; background: radial-gradient(circle at 30% 30%, rgba(76, 212, 255, .12), rgba(4, 35, 75, .18) 70%); box-shadow: inset 0 0 8px rgba(99, 222, 255, .08); backdrop-filter: blur(4px); }.domain-card h3 { margin: 0 0 3px; color: #ebfbff; font-size: 13px; font-weight: 900; }.domain-card b { color: #4ee0ff; font-size: 18px; font-weight: 900; }.domain-card ul { display: grid; gap: 4px; margin: 6px 0 0; padding: 0; list-style: none; }.domain-card li { display: flex; align-items: center; justify-content: space-between; color: #97c5da; font-size: 9px; }.domain-card li em { color: #5ed2ff; font-weight: 800; font-style: normal; }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes beamPulse { 0%, 100% { opacity: .18; transform: translateX(-40%); } 50% { opacity: .4; transform: translateX(40%); } }
@keyframes particlesRise { 0% { transform: translateY(18px); opacity: .2; } 50% { opacity: .7; } 100% { transform: translateY(-26px); opacity: .1; } }
@keyframes gyroA { 0% { transform: translate(-50%, -50%) rotate(12deg) scale(1); } 100% { transform: translate(-50%, -50%) rotate(22deg) scale(1.06); } }
@keyframes gyroB { 0% { transform: translate(-50%, -50%) rotate(-32deg) scale(1); } 100% { transform: translate(-50%, -50%) rotate(-22deg) scale(1.04); } }
@keyframes floatIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

.hotspot-tree-view {
  position: relative;
  width: 100%;
  min-height: 780px;
  height: calc(100vh - 180px);
  border-radius: 12px;
  overflow: hidden;
  background: linear-gradient(180deg, #041022 0%, #071a35 50%, #041022 100%);
}

.hotspot-tree-main {
  position: absolute;
  inset: 0;
}

.hotspot-float-panels {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 20;
}

.float-panel {
  position: absolute;
  background: rgba(4, 22, 50, 0.78);
  backdrop-filter: blur(16px) saturate(1.1);
  border: 1px solid rgba(78, 216, 255, 0.28);
  border-radius: 12px;
  padding: 16px 20px;
  pointer-events: auto;
  animation: floatIn 0.5s ease-out;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.float-panel.top-left {
  top: 20px;
  left: 20px;
  width: 220px;
}

.float-panel.bottom-left {
  bottom: 20px;
  left: 20px;
  width: 240px;
}

.float-panel.right-top {
  top: 20px;
  right: 20px;
  width: 200px;
}

.float-panel.right-bottom {
  bottom: 20px;
  right: 20px;
  width: 200px;
}

.float-panel h3 {
  margin: 0 0 12px;
  font-size: 13px;
  font-weight: 700;
  color: #eafcff;
  letter-spacing: 1px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(78, 216, 255, 0.2);
  display: flex;
  align-items: center;
  gap: 8px;
}

.float-panel h3::before {
  content: '';
  width: 4px;
  height: 14px;
  background: linear-gradient(180deg, #4ed8ff, #36d7ff);
  border-radius: 2px;
}

.summary-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 10px;
  background: rgba(78, 216, 255, 0.06);
  border-radius: 8px;
  border: 1px solid rgba(78, 216, 255, 0.1);
}

.stat-item b {
  font-size: 22px;
  font-weight: 900;
  color: #eafcff;
  text-shadow: 0 0 12px rgba(78, 216, 255, 0.5);
}

.stat-item span {
  font-size: 11px;
  color: #78a9c8;
}

.stat-item em {
  font-size: 10px;
  font-style: normal;
  font-weight: 600;
}

.stat-item em.up { color: #36d7ff; }
.stat-item em.down { color: #ff7088; }

.heat-bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.heat-bar-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
}

.bar-label {
  width: 70px;
  color: #b8e0f0;
  font-size: 10px;
  flex-shrink: 0;
}

.bar-track {
  flex: 1;
  height: 6px;
  background: rgba(78, 216, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s ease;
}

.bar-fill.hot { background: linear-gradient(90deg, #ff6b35, #ffb65c); box-shadow: 0 0 8px rgba(255, 107, 53, 0.5); }
.bar-fill.warm { background: linear-gradient(90deg, #ffb65c, #69f0ae); box-shadow: 0 0 8px rgba(105, 240, 174, 0.4); }
.bar-fill.cool { background: linear-gradient(90deg, #69f0ae, #4ed8ff); box-shadow: 0 0 8px rgba(78, 216, 255, 0.4); }

.heat-bar-row b {
  width: 24px;
  text-align: right;
  color: #eafcff;
  font-size: 12px;
  font-weight: 700;
}

.mini-skill-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.mini-skill-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 8px 10px;
  background: rgba(78, 216, 255, 0.05);
  border: 1px solid rgba(78, 216, 255, 0.12);
  border-radius: 8px;
  color: #b8e0f0;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.mini-skill-btn:hover {
  background: rgba(78, 216, 255, 0.12);
  border-color: rgba(78, 216, 255, 0.35);
  transform: translateX(4px);
}

.mini-skill-btn i {
  display: grid;
  place-items: center;
  width: 20px;
  height: 20px;
  border-radius: 4px;
  background: linear-gradient(135deg, rgba(78, 216, 255, 0.2), rgba(54, 215, 255, 0.2));
  color: #4ed8ff;
  font-size: 10px;
  font-style: normal;
  font-weight: 700;
  flex-shrink: 0;
}

.mini-skill-btn span {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mini-skill-btn em {
  font-style: normal;
  font-weight: 700;
  font-size: 12px;
}

.mini-skill-btn em.up { color: #36d7ff; }
.mini-skill-btn em.down { color: #ff7088; }
</style>

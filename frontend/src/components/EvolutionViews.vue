<template>
  <section v-if="mode === 'version'" class="evo-view version-view">
    <aside class="hud-stack">
      <article class="hud-panel version-summary">
        <PanelTitle title="版本对比总览" code="VERSION DELTA" />
        <div class="version-gauge">
          <div><small>上一版</small><b>{{ previousCount }}</b><em>{{ activeCard.fromVersion }}</em></div>
          <span class="gauge-core"><i>净变化</i><strong>{{ signedDelta }}</strong><small>SKILLS</small></span>
          <div><small>当前版</small><b>{{ currentCount }}</b><em>{{ activeCard.toVersion }}</em></div>
        </div>
        <div class="delta-counters">
          <span class="tone-add"><b>+{{ addedItems.length }}</b>新增</span>
          <span class="tone-mod"><b>{{ modifiedItems.length }}</b>调整</span>
          <span class="tone-remove"><b>-{{ removedItems.length }}</b>淘汰</span>
        </div>
      </article>

      <article class="hud-panel trend-panel">
        <PanelTitle title="演化趋势" code="4 VERSIONS" />
        <div class="mini-chart" aria-hidden="true">
          <svg viewBox="0 0 280 118" preserveAspectRatio="none">
            <path class="grid-line" d="M0 24H280M0 59H280M0 94H280" />
            <path class="trend add" d="M5 88 C52 76 72 47 108 54 S158 28 194 48 S242 35 275 20" />
            <path class="trend mod" d="M5 96 C48 92 80 75 111 77 S168 64 198 68 S245 55 275 62" />
            <path class="trend remove" d="M5 104 C52 99 80 91 110 95 S166 88 198 91 S244 82 275 87" />
            <circle v-for="x in [5, 94, 184, 275]" :key="x" :cx="x" cy="54" r="3" />
          </svg>
        </div>
        <div class="mini-axis"><span>v1.0</span><span>v1.1</span><span class="active">{{ activeCard.toVersion || 'v1.2' }}</span><span>v1.3</span></div>
      </article>

      <article class="hud-panel insight-panel">
        <PanelTitle title="能力演化洞察" code="AI INSIGHT" />
        <p>{{ activeCard.note || '本次更新聚焦工程效率与岗位核心能力，能力结构正在向高复用、可落地方向收敛。' }}</p>
        <ul>
          <li class="tone-add"><i>01</i>云原生与框架能力增强</li>
          <li class="tone-mod"><i>02</i>技术栈完成迭代与替代</li>
          <li class="tone-remove"><i>03</i>低关联能力逐步退出</li>
        </ul>
      </article>
    </aside>

    <main class="hud-panel version-command">
      <div class="command-head">
        <div><small>ROLE COMPARISON COCKPIT</small><h2>角色对比驾驶舱</h2></div>
        <button class="role-selector" type="button" @click="cycleCard(1)">{{ activeCard.jobName || 'AI 智能体开发工程师' }} <span>⌄</span></button>
        <span class="domain-chip">{{ activeCard.domain || '人工智能' }}</span>
        <div class="version-switch"><b>{{ activeCard.fromVersion || 'v1.1' }}</b><i>→</i><strong>{{ activeCard.toVersion || 'v1.2' }}</strong></div>
      </div>
      <p class="command-note">{{ activeCard.note || '通过版本更新事件重建岗位能力画像，清晰展示新增、调整与淘汰能力。' }}</p>

      <div class="version-lab">
        <button
          v-for="well in wells"
          :key="well.key"
          type="button"
          class="energy-well"
          :class="[`energy-well--${well.key}`, { active: activeWell === well.key }]"
          @click="activeWell = well.key"
        >
          <span class="well-label">{{ well.title }} <b>{{ well.items.length }} 项</b></span>
          <span class="well-chamber">
            <i class="well-particles"></i><i class="well-particles well-particles--far"></i><i class="well-beam"></i><i class="well-core"><b></b></i>
            <em v-for="item in well.items.slice(0, 3)" :key="skillLabel(item)">{{ well.prefix }} {{ skillLabel(item) }}</em>
            <em v-if="!well.items.length">暂无变更</em>
          </span>
          <span class="well-base"><i></i><b></b><em></em></span><span class="well-plinth"><i></i></span>
        </button>
      </div>

      <div class="focused-change">
        <span :class="`tone-${activeWell}`">{{ activeWellData.title }}</span>
        <p>{{ activeWellDescription }}</p>
        <div><i v-for="item in activeWellData.items.slice(0, 5)" :key="skillLabel(item)">{{ skillLabel(item) }}</i></div>
      </div>
      <div class="confidence-rail">
        <span>上一版能力 <b>{{ previousCount }} 项</b></span>
        <i><b :style="{ width: `${confidence}%` }"></b></i>
        <span>证据置信度 <strong>{{ confidence }}%</strong></span>
        <span>当前能力 <b>{{ currentCount }} 项</b></span>
      </div>
    </main>

    <aside class="hud-stack">
      <article class="hud-panel diff-panel">
        <PanelTitle title="差异说明" code="CHANGE LOG" />
        <p>本次版本共发生 <b>{{ changeCount }}</b> 项变化，净变化 <strong>{{ signedDelta }}</strong> 项。</p>
        <button v-for="well in wells" :key="well.key" type="button" :class="[well.key, { active: activeWell === well.key }]" @click="activeWell = well.key">
          <i>{{ well.items.length }}</i><span><b>{{ well.title }}</b><em>{{ well.items.slice(0, 2).map(skillLabel).join('、') || '暂无变化' }}</em></span>
        </button>
      </article>
      <article class="hud-panel evidence-panel">
        <PanelTitle title="证据来源分布" code="EVIDENCE" />
        <div class="evidence-ring" :style="{ '--confidence': `${confidence * 3.6}deg` }"><b>{{ confidence }}%</b><small>高置信度</small></div>
        <div class="evidence-bars"><span><i style="width: 76%"></i>高置信度 76%</span><span><i style="width: 18%"></i>中等置信度 18%</span><span><i style="width: 6%"></i>低置信度 6%</span></div>
      </article>
      <article class="hud-panel impact-panel">
        <PanelTitle title="变更影响范围" code="IMPACT" />
        <div><span class="tone-add"><b>5</b>无影响</span><span class="tone-mod"><b>3</b>中等影响</span><span class="tone-remove"><b>1</b>局部影响</span></div>
      </article>
    </aside>

    <footer class="hud-panel role-strip">
      <button class="strip-arrow" type="button" @click="cycleCard(-1)">‹</button>
      <div class="strip-title"><small>QUICK SWITCH</small><b>其他角色快速对比</b></div>
      <button
        v-for="(card, index) in roleCards"
        :key="card.jobId || index"
        type="button"
        class="role-card"
        :class="{ active: index === activeCardIndex }"
        @click="activeCardIndex = index"
      >
        <span><i>◇</i>{{ card.jobName }}</span><em>{{ card.domain }}</em><b><strong>+{{ card.added?.length || 0 }}</strong> / {{ card.modified?.length || 0 }} / <i>-{{ card.removed?.length || 0 }}</i></b>
      </button>
      <button class="strip-arrow" type="button" @click="cycleCard(1)">›</button>
    </footer>
  </section>

  <section v-else-if="mode === 'hotspot'" class="evo-view hotspot-view">
    <aside class="hud-stack">
      <article class="hud-panel">
        <PanelTitle title="能力热点总览" code="2026-06" />
        <div class="hot-summary">
          <span><i>◇</i><b>{{ Math.max(124, hotSkills.length) }}</b>能力总数<em>▲ 6.2%</em></span>
          <span><i>♨</i><b>{{ Math.max(12, emerging.length) }}</b>高热能力<em>▲ {{ emerging.length }}</em></span>
          <span><i>↗</i><b>{{ Math.max(28, rising.length) }}</b>升温能力<em>▲ 3</em></span>
          <span><i>↘</i><b>{{ Math.max(18, declining.length) }}</b>降温能力<em class="down">▼ 2</em></span>
        </div>
      </article>
      <article class="hud-panel hot-trend-panel">
        <PanelTitle title="能力热度趋势" code="TOP 10" />
        <EChart :option="trendOption" class="mini-echart" />
      </article>
      <article class="hud-panel heat-distribution">
        <PanelTitle title="热度分布" code="DISTRIBUTION" />
        <div class="heat-donut"><b>{{ hotSkills.length }}</b><small>总能力</small></div>
        <ul><li><i class="level-high"></i>高热（≥16）<b>{{ heatBuckets.high }}</b></li><li><i class="level-mid"></i>中高热（12-16）<b>{{ heatBuckets.mid }}</b></li><li><i class="level-warm"></i>中热（8-12）<b>{{ heatBuckets.warm }}</b></li><li><i class="level-low"></i>低热（&lt;8）<b>{{ heatBuckets.low }}</b></li></ul>
      </article>
      <article class="hud-panel insight-panel compact">
        <PanelTitle title="洞察摘要" code="AI" />
        <p><b>{{ activeSkill.name }}</b> 当前热度 {{ activeSkill.heat }}，{{ activeSkill.category || '核心能力' }}方向关注度持续变化，建议结合岗位需求进行课程与人才培养调整。</p>
      </article>
    </aside>

    <main class="hud-panel graph-command">
      <div class="graph-title"><div><small>INTERACTIVE SKILL ORBIT</small><h2>热门技能关系星图</h2></div><span>悬停查看 · 点击聚焦</span></div>
      <EChart :option="hotspotGraphOption" class="hotspot-chart" @click="handleSkillClick" />
      <div class="graph-hit-targets" aria-label="能力热点节点">
        <button
          v-for="(skill, index) in hotSkills"
          :key="skill.name"
          type="button"
          :title="`聚焦 ${skill.name}`"
          :aria-label="`聚焦 ${skill.name}`"
          :style="hotNodeHitStyle(index)"
          @click="selectSkill(skill.name)"
        ></button>
      </div>
      <div class="active-skill-readout">
        <span>FOCUS</span><b>{{ activeSkill.name }}</b><strong>{{ activeSkill.heat }}</strong><em>{{ activeSkill.category || '能力热点' }}</em>
      </div>
      <div class="graph-legend"><span class="level-high">高热 ≥16</span><span class="level-mid">中高热 12-16</span><span class="level-warm">中热 8-12</span><span class="level-low">低热 &lt;8</span></div>
    </main>

    <aside class="hud-stack">
      <article class="hud-panel ranking-panel rising-panel">
        <PanelTitle title="新兴能力" code="EMERGING ↗" />
        <div class="skill-chips"><button v-for="item in emerging.slice(0, 5)" :key="item.name" type="button" @click="selectSkill(item.name)">{{ item.name }}</button></div>
        <div class="sparkline green-line"></div>
        <div class="ranking-list"><button v-for="(item, index) in emergingList" :key="item.name" type="button" @click="selectSkill(item.name)"><i>{{ index + 1 }}</i><span>{{ item.name }}</span><b>{{ formatHeat(item) }}</b><em>▲ {{ growthLabel(item, index) }}</em></button></div>
      </article>
      <article class="hud-panel ranking-panel declining-panel">
        <PanelTitle title="淘汰能力" code="DECLINING ↘" />
        <div class="skill-chips"><button v-for="item in declining.slice(0, 4)" :key="item.name" type="button" @click="selectSkill(item.name)">{{ item.name }}</button></div>
        <div class="sparkline red-line"></div>
        <div class="ranking-list"><button v-for="(item, index) in declining.slice(0, 7)" :key="item.name" type="button" @click="selectSkill(item.name)"><i>{{ index + 1 }}</i><span>{{ item.name }}</span><b>{{ formatHeat(item) }}</b><em>▼ {{ 14 + index * 2 }}.{{ index }}%</em></button></div>
      </article>
    </aside>
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
        <span>最强领域 <b>{{ topDomain?.domain || '软件研发' }}</b><em>{{ topDomain ? domainShare(topDomain) : 0 }}%</em></span>
        <span>增长最快 <b>{{ fastestDomain?.domain || '人工智能' }}</b><em>▲ 18.7%</em></span>
        <span>结构均衡度 <b>78/100</b><em>良好</em></span>
        <span>能力覆盖率 <b>92.6%</b><em>主流技能</em></span>
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

const props = defineProps<{ mode: string; hotspot: any; compare: any; cards: any[] }>()

const PanelTitle = defineComponent({
  props: { title: { type: String, required: true }, code: { type: String, default: '' } },
  setup(panelProps) {
    return () => h('div', { class: 'panel-title' }, [h('h3', panelProps.title), h('small', panelProps.code)])
  }
})

const fallbackCards = [{
  jobId: 0, jobName: 'AI 智能体开发工程师', domain: '人工智能', fromVersion: 'v1.1', toVersion: 'v1.2',
  added: ['Kubernetes', 'Spring Boot'], modified: [{ name: 'Vue', change: '升级为 Vue 3 工程化能力' }], removed: ['Spring Cloud'],
  previousSkills: Array.from({ length: 13 }), currentSkills: Array.from({ length: 12 }), confidence: .76,
  note: '岗位画像在最近样本中更强调业务场景、证据来源与可落地成果。'
}]
const displayCards = computed(() => props.cards?.length ? props.cards : fallbackCards)
const roleCards = computed(() => displayCards.value.slice(0, 5))
const activeCardIndex = ref(0)
const activeWell = ref('add')
const activeCard = computed(() => displayCards.value[activeCardIndex.value] || displayCards.value[0])
const previousCount = computed(() => activeCard.value.previousSkills?.length || 0)
const currentCount = computed(() => activeCard.value.currentSkills?.length || 0)
const delta = computed(() => currentCount.value - previousCount.value)
const signedDelta = computed(() => `${delta.value > 0 ? '+' : ''}${delta.value}`)
const confidence = computed(() => Math.round((activeCard.value.confidence || .76) * 100))
const addedItems = computed(() => activeCard.value.added || [])
const modifiedItems = computed(() => activeCard.value.modified || [])
const removedItems = computed(() => activeCard.value.removed || [])
const changeCount = computed(() => addedItems.value.length + modifiedItems.value.length + removedItems.value.length)
const wells = computed(() => [
  { key: 'add', title: '新增能力', prefix: '+', items: addedItems.value },
  { key: 'mod', title: '调整/替代', prefix: '~', items: modifiedItems.value },
  { key: 'remove', title: '淘汰能力', prefix: '−', items: removedItems.value }
])
const activeWellData = computed(() => wells.value.find((item) => item.key === activeWell.value) || wells.value[0])
const activeWellDescription = computed(() => ({ add: '新增能力将直接补强岗位交付边界与工程效率。', mod: '调整项代表技能要求已升级或被新技术栈替代。', remove: '淘汰项从核心画像退出，降低学习路径冗余。' }[activeWell.value] || ''))

function skillLabel(item: any) { return typeof item === 'string' ? item : item?.name || '能力项' }
function cycleCard(step: number) { activeCardIndex.value = (activeCardIndex.value + step + displayCards.value.length) % displayCards.value.length }

const rising = computed<any[]>(() => props.hotspot?.rising || [])
const declining = computed<any[]>(() => props.hotspot?.declining || [])
const emerging = computed<any[]>(() => props.hotspot?.emerging || [])
const fallbackSkills = ['项目管理', '安全合规', 'SQL', '数据质量', 'Linux', '业务流程建模', '数据可视化', '需求分析', '权限管理', 'Python'].map((name, index) => ({ name, heat: 17.7 - index * .85, category: '核心能力' }))
const hotSkills = computed(() => {
  const merged = [...rising.value, ...emerging.value].filter((item, index, arr) => item?.name && arr.findIndex((row) => row.name === item.name) === index)
  return (merged.length ? merged : fallbackSkills).slice(0, 10).map((item: any, index: number) => ({ ...item, heat: Number(item.heat ?? (13 + Number(item.growth || 0) * 1.5) ?? (17 - index)).toFixed(2) }))
})
const activeSkillName = ref('')
const activeSkill = computed(() => {
  const all = [...hotSkills.value, ...rising.value, ...emerging.value, ...declining.value]
  const selected = all.find((item) => item.name === activeSkillName.value)
  return selected ? { ...selected, heat: Number(selected.heat ?? selected.growth ?? selected.removed ?? 0).toFixed(2) } : hotSkills.value[0] || fallbackSkills[0]
})
watch(hotSkills, (skills) => { if (!skills.some((item) => item.name === activeSkillName.value)) activeSkillName.value = skills[0]?.name || '' }, { immediate: true })
const emergingList = computed(() => emerging.value.length ? emerging.value.slice(0, 5) : hotSkills.value.slice(0, 5))
const heatBuckets = computed(() => hotSkills.value.reduce((acc, item) => { const heat = Number(item.heat); if (heat >= 16) acc.high++; else if (heat >= 12) acc.mid++; else if (heat >= 8) acc.warm++; else acc.low++; return acc }, { high: 0, mid: 0, warm: 0, low: 0 }))

function heatColor(heat: number) { return heat >= 16 ? '#ffb52e' : heat >= 12 ? '#37e6a1' : heat >= 8 ? '#a26cff' : '#28cfff' }
function selectSkill(name: string) { if (name) activeSkillName.value = name }
function handleSkillClick(params: any) { if (params?.data?.skillName) selectSkill(params.data.skillName) }
function hotNodeHitStyle(index: number) { const angle = index / Math.max(hotSkills.value.length, 1) * Math.PI * 2 - Math.PI / 2; return { left: `${50 + Math.cos(angle) * 36}%`, top: `${50 + Math.sin(angle) * 34}%` } }
function formatHeat(item: any) { return Number(item.heat ?? item.growth ?? item.removed ?? 0).toFixed(2) }
function growthLabel(_item: any, index: number) { return `${28 - index * 3}.${index}%` }

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
    backgroundColor: '#01060c',
    animationDurationUpdate: 650,
    tooltip: { backgroundColor: 'rgba(3,20,54,.96)', borderColor: '#27cfff', textStyle: { color: '#dffaff' }, formatter: (p: any) => p.data?.skillName ? `<b>${p.data.skillName}</b><br/>热度：${p.data.value}<br/>点击聚焦该能力` : '能力热点总览' },
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
  tooltip: { trigger: 'axis', backgroundColor: 'rgba(3,20,54,.95)', borderColor: '#21cfff', textStyle: { color: '#e9fbff' } },
  xAxis: { type: 'category', boundaryGap: false, data: ['01', '02', '03', '04', '05', '06'], axisLine: { lineStyle: { color: 'rgba(83,190,255,.26)' } }, axisLabel: { color: '#78a9c8', fontSize: 9 } },
  yAxis: { type: 'value', splitNumber: 3, axisLabel: { color: '#78a9c8', fontSize: 9 }, splitLine: { lineStyle: { color: 'rgba(83,190,255,.10)' } } },
  series: [{ type: 'line', smooth: .45, data: [6.4, 10.8, 7.1, 13.9, 9.2, Number(activeSkill.value.heat || 14.2)], symbolSize: 7, lineStyle: { color: '#27d9ff', width: 2 }, itemStyle: { color: '#8ff7ff', shadowBlur: 10, shadowColor: '#21d8ff' }, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(28,171,255,.42)' }, { offset: 1, color: 'rgba(28,171,255,0)' }] } } }]
}))

const categories = computed<string[]>(() => props.compare?.categories || ['产品与交付', '人工智能', '安全合规', '工具工程', '开发技术', '数据技术', '通用能力'])
const fallbackDomains = ['云计算', '产业数字化', '人工智能', '基础设施', '物联网', '数据技术', '安全合规', '软件研发'].map((domain, index) => ({ domain, categories: { [categories.value[index % categories.value.length]]: 8 + index }, topSkills: [{ name: ['Kubernetes', '业务流程建模', '机器学习', '网络基础', '设备接入', 'SQL', '权限管理', 'Python'][index], weight: 6 + index }] }))
const domains = computed<any[]>(() => props.compare?.matrix?.length ? props.compare.matrix.slice(0, 8) : fallbackDomains)
const leftDomains = computed(() => domains.value.slice(0, 4))
const rightDomains = computed(() => domains.value.slice(4, 8))
const activeDomainName = ref('')
watch(domains, (rows) => { if (!rows.some((row) => row.domain === activeDomainName.value)) activeDomainName.value = rows[0]?.domain || '' }, { immediate: true })
const activeDomain = computed(() => domains.value.find((row) => row.domain === activeDomainName.value) || domains.value[0] || fallbackDomains[0])
const topDomain = computed(() => [...domains.value].sort((a, b) => domainRawTotal(b) - domainRawTotal(a))[0])
const fastestDomain = computed(() => domains.value.find((row) => String(row.domain).includes('人工智能')) || domains.value[1])
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
    backgroundColor: '#01060c',
    animationDuration: 850,
    animationDurationUpdate: 850,
    animationEasingUpdate: 'cubicInOut',
    tooltip: {
      backgroundColor: 'rgba(1,12,28,.97)',
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
.evo-view { --cyan: #5ce7ff; --line: rgba(83, 203, 255, .24); --panel: rgba(1, 9, 23, .94); position: relative; isolation: isolate; display: grid; gap: 14px; min-height: 690px; color: #c9ecff; background: radial-gradient(circle at 52% 48%, rgba(0, 112, 187, .11), transparent 34%), linear-gradient(180deg, rgba(1, 8, 20, .36), rgba(0, 4, 13, .72)); }
.evo-view::before { position: absolute; z-index: -1; inset: 22% 0 0; content: ''; opacity: .44; background: repeating-linear-gradient(90deg, transparent 0 61px, rgba(45, 141, 203, .06) 62px 63px), repeating-linear-gradient(0deg, transparent 0 48px, rgba(45, 141, 203, .05) 49px 50px); mask-image: linear-gradient(to bottom, transparent, #000 34%, #000); transform: perspective(520px) rotateX(61deg) scale(1.25); transform-origin: bottom; pointer-events: none; }
button { font: inherit; }
.hud-panel { position: relative; border: 1px solid var(--line); color: inherit; background: linear-gradient(145deg, rgba(4, 18, 39, .97), rgba(0, 6, 18, .96) 72%); box-shadow: inset 0 1px rgba(205, 246, 255, .08), inset 0 0 44px rgba(17, 94, 146, .055), 0 18px 36px rgba(0, 2, 12, .32); clip-path: polygon(0 12px, 12px 0, calc(100% - 22px) 0, 100% 22px, 100% calc(100% - 12px), calc(100% - 12px) 100%, 14px 100%, 0 calc(100% - 14px)); }
.hud-panel::before, .hud-panel::after { position: absolute; z-index: 2; width: 36px; height: 2px; content: ''; background: #31dfff; box-shadow: 0 0 10px #22cfff; pointer-events: none; }
.hud-panel::before { top: 0; left: 22px; }.hud-panel::after { right: 22px; bottom: 0; }
.hud-stack, .domain-stack { display: flex; min-width: 0; flex-direction: column; gap: 13px; }
.hud-stack > .hud-panel { padding: 15px; }
.panel-title { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 12px; }
.panel-title h3 { margin: 0; color: #eafaff; font-size: 15px; letter-spacing: .02em; }.panel-title h3::before { margin-right: 8px; color: var(--cyan); content: '‹'; }.panel-title small { color: #45dfff; font-size: 9px; font-weight: 800; letter-spacing: .14em; }
.tone-add { color: #34efb6 !important; }.tone-mod { color: #ffbd3e !important; }.tone-remove { color: #ff7797 !important; }

.version-view { grid-template-columns: 265px minmax(620px, 1fr) 285px; }
.version-summary { min-height: 190px; }.version-gauge { display: grid; grid-template-columns: 1fr 104px 1fr; align-items: center; text-align: center; }
.version-gauge > div small, .version-gauge > div em { display: block; color: #84b8d7; font-size: 10px; font-style: normal; }.version-gauge > div b { display: block; color: #e8fbff; font-size: 29px; }
.gauge-core { position: relative; display: grid; place-items: center; width: 92px; height: 92px; border: 2px solid #42dfff; border-radius: 50%; background: radial-gradient(circle, rgba(28, 157, 255, .42), rgba(2, 20, 62, .9) 64%); box-shadow: 0 0 24px rgba(39, 208, 255, .5), inset 0 0 18px rgba(91, 231, 255, .22); }
.gauge-core::before, .gauge-core::after { position: absolute; inset: -9px; border: 1px dashed rgba(67, 220, 255, .5); border-radius: 50%; content: ''; animation: spin 12s linear infinite; }.gauge-core::after { inset: 9px; border-style: solid; border-color: transparent #60ebff; animation-direction: reverse; animation-duration: 7s; }
.gauge-core i, .gauge-core small { color: #72badb; font-size: 9px; font-style: normal; letter-spacing: .1em; }.gauge-core strong { color: #fff; font-size: 24px; line-height: 1; }
.delta-counters { display: grid; grid-template-columns: repeat(3, 1fr); margin-top: 13px; text-align: center; }.delta-counters span { color: #86b8d3; font-size: 10px; }.delta-counters b { display: block; font-size: 21px; }
.trend-panel { min-height: 160px; }.mini-chart { height: 96px; }.mini-chart svg { width: 100%; height: 100%; overflow: visible; }.grid-line { fill: none; stroke: rgba(75, 174, 231, .13); }.trend { fill: none; stroke-width: 2; filter: drop-shadow(0 0 5px currentColor); }.trend.add { color: #34eab5; stroke: currentColor; }.trend.mod { color: #ffbd3e; stroke: currentColor; }.trend.remove { color: #ff6f94; stroke: currentColor; }.mini-chart circle { fill: #9af8ff; filter: drop-shadow(0 0 5px #25d9ff); }.mini-axis { display: flex; justify-content: space-between; color: #6698b8; font-size: 9px; }.mini-axis .active { color: #dffbff; font-weight: 900; }
.insight-panel { flex: 1; }.insight-panel p { margin: 0; color: #9fc7dd; font-size: 12px; line-height: 1.65; }.insight-panel ul { display: grid; gap: 10px; margin: 16px 0 0; padding: 0; list-style: none; }.insight-panel li { display: flex; align-items: center; gap: 8px; font-size: 11px; }.insight-panel li i { display: grid; place-items: center; width: 24px; height: 24px; border: 1px solid currentColor; border-radius: 50%; font-size: 8px; font-style: normal; box-shadow: 0 0 10px currentColor; }
.version-command { min-width: 0; overflow: hidden; padding: 18px 20px 15px; background: radial-gradient(ellipse at 50% 82%, rgba(0, 120, 210, .15), transparent 46%), linear-gradient(180deg, rgba(2, 14, 32, .98), rgba(0, 5, 14, .98)); }.version-command::after { width: auto; height: auto; inset: 42% -10% -18%; opacity: .56; border: 1px solid rgba(48, 176, 255, .16); border-radius: 50%; background: repeating-radial-gradient(ellipse, transparent 0 31px, rgba(38, 151, 224, .11) 32px 33px), repeating-linear-gradient(90deg, transparent 0 45px, rgba(33, 161, 255, .08) 46px 47px); box-shadow: inset 0 0 44px rgba(0, 129, 221, .1); transform: perspective(480px) rotateX(62deg); }
.command-head { position: relative; z-index: 3; display: flex; align-items: center; gap: 10px; }.command-head h2, .graph-title h2 { margin: 2px 0 0; color: #effdff; font-size: 19px; }.command-head small, .graph-title small { color: #45dcff; font-size: 8px; font-weight: 850; letter-spacing: .17em; }
.role-selector, .domain-chip { border: 1px solid rgba(68, 210, 255, .38); padding: 6px 10px; color: #dff8ff; background: rgba(5, 50, 104, .72); cursor: pointer; }.role-selector:hover { border-color: #4fe7ff; box-shadow: 0 0 14px rgba(31, 212, 255, .25); }.domain-chip { color: #5be8ff; font-size: 11px; }.version-switch { display: flex; align-items: center; gap: 10px; margin-left: auto; }.version-switch b, .version-switch strong { border: 1px solid rgba(57, 192, 255, .35); padding: 5px 12px; color: #b2d9ed; background: rgba(4, 37, 84, .7); }.version-switch strong { color: #e9fcff; box-shadow: inset 0 -2px #2cceff; }.version-switch i { color: #61dfff; font-style: normal; }
.command-note { position: relative; z-index: 3; margin: 10px 0 0; color: #8dbbd4; font-size: 11px; }
.version-lab { position: relative; z-index: 3; display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; min-height: 365px; padding: 34px 16px 8px; perspective: 900px; }
.energy-well { display: flex; min-width: 0; flex-direction: column; align-items: center; border: 0; color: #35efb7; background: transparent; cursor: pointer; transition: transform .25s ease, filter .25s ease; }.energy-well:hover, .energy-well.active { transform: translateY(-8px); filter: brightness(1.2); }.energy-well--mod { color: #ffc048; }.energy-well--remove { color: #ff7596; }
.well-label { margin-bottom: 10px; font-size: 17px; font-weight: 850; }.well-label b { display: block; margin-top: 4px; font-size: 24px; }
.well-chamber { position: relative; display: flex; width: 94%; height: 232px; flex-direction: column; align-items: center; justify-content: center; gap: 12px; border: 0; border-radius: 0; background: linear-gradient(90deg, transparent 5%, color-mix(in srgb, currentColor 6%, transparent) 23%, color-mix(in srgb, currentColor 24%, transparent) 50%, color-mix(in srgb, currentColor 6%, transparent) 77%, transparent 95%); filter: drop-shadow(0 18px 22px color-mix(in srgb, currentColor 24%, transparent)); clip-path: polygon(37% 0, 63% 0, 96% 100%, 4% 100%); overflow: hidden; }
.well-chamber::before { position: absolute; inset: 0 16%; content: ''; opacity: .8; background: repeating-linear-gradient(90deg, transparent 0 11px, color-mix(in srgb, currentColor 19%, transparent) 12px 13px), linear-gradient(180deg, transparent, color-mix(in srgb, currentColor 25%, transparent)); transform: perspective(380px) rotateX(-8deg); }.well-chamber::after { position: absolute; right: 11%; bottom: 10px; left: 11%; height: 34px; border: 1px solid currentColor; border-radius: 50%; content: ''; opacity: .55; box-shadow: 0 0 20px currentColor, inset 0 0 16px currentColor; }.well-beam { position: absolute; width: 16%; height: 112%; background: linear-gradient(90deg, transparent, #fff, currentColor, #fff, transparent); opacity: .24; filter: blur(8px); animation: beamPulse 3.7s cubic-bezier(.32,.72,0,1) infinite; }.well-particles { position: absolute; inset: 0; opacity: .64; background-image: radial-gradient(circle, #fff 0 1px, transparent 1.7px), radial-gradient(circle, currentColor 0 1px, transparent 2px); background-position: 0 0, 7px 11px; background-size: 19px 27px, 31px 23px; animation: particlesRise 6.5s cubic-bezier(.32,.72,0,1) infinite; }
.well-chamber em { z-index: 2; border: 1px solid currentColor; border-radius: 99px; padding: 6px 13px; color: #effdff; font-size: 11px; font-style: normal; background: rgba(2, 24, 61, .84); box-shadow: 0 0 12px color-mix(in srgb, currentColor 30%, transparent); }
.well-base { position: relative; width: 116%; height: 58px; margin-top: -16px; border: 2px solid color-mix(in srgb, currentColor 75%, #fff); border-radius: 50%; background: repeating-radial-gradient(ellipse, #030a12 0 8px, #0d1b27 9px 12px, #02050a 13px 17px); box-shadow: 0 0 17px color-mix(in srgb, currentColor 55%, transparent), inset 0 0 24px #000, inset 0 -7px 12px color-mix(in srgb, currentColor 25%, transparent); transform: perspective(300px) rotateX(64deg); }.well-base::before, .well-base::after, .well-base i, .well-base b { position: absolute; inset: 7px 12px; border: 1px solid currentColor; border-radius: 50%; content: ''; }.well-base::after { inset: 14px 27px; border-width: 2px; }.well-base i { inset: -13px -18px; border-style: dashed; opacity: .65; animation: spin 13s linear infinite; }.well-base b { inset: 21px 43px; background: radial-gradient(ellipse, #fff, currentColor 24%, #02101a 58%); box-shadow: 0 0 19px currentColor; }
.focused-change { position: relative; z-index: 4; min-height: 68px; border: 1px solid rgba(61, 202, 255, .25); padding: 9px 12px; background: rgba(3, 31, 73, .72); }.focused-change > span { font-size: 11px; font-weight: 900; }.focused-change p { display: inline; margin-left: 10px; color: #8fbcd5; font-size: 10px; }.focused-change div { display: flex; gap: 6px; margin-top: 7px; }.focused-change div i { border: 1px solid rgba(79, 210, 255, .28); padding: 3px 7px; color: #ccefff; font-size: 9px; font-style: normal; }
.confidence-rail { position: relative; z-index: 4; display: flex; align-items: center; gap: 12px; margin-top: 10px; color: #82aec7; font-size: 10px; }.confidence-rail > i { height: 5px; flex: 1; overflow: hidden; background: rgba(48, 121, 173, .25); }.confidence-rail > i b { display: block; height: 100%; background: linear-gradient(90deg, #1ab6ff, #62f2ff); box-shadow: 0 0 10px #35dfff; }.confidence-rail strong { color: #48e8ff; font-size: 15px; }
.diff-panel p { color: #91bed7; font-size: 11px; line-height: 1.6; }.diff-panel p b, .diff-panel p strong { color: #eafcff; }.diff-panel button { display: flex; width: 100%; align-items: center; gap: 10px; margin-top: 9px; border: 1px solid transparent; border-left: 2px solid currentColor; padding: 8px; color: #35efb7; text-align: left; background: rgba(4, 37, 79, .45); cursor: pointer; }.diff-panel button.mod { color: #ffc048; }.diff-panel button.remove { color: #ff7596; }.diff-panel button:hover, .diff-panel button.active { border-color: currentColor; box-shadow: inset 0 0 15px color-mix(in srgb, currentColor 12%, transparent); }.diff-panel button > i { font-size: 20px; font-style: normal; font-weight: 900; }.diff-panel button span { min-width: 0; }.diff-panel button b, .diff-panel button em { display: block; }.diff-panel button em { overflow: hidden; color: #91b9cf; font-size: 9px; font-style: normal; text-overflow: ellipsis; white-space: nowrap; }
.evidence-ring { display: grid; place-items: center; width: 112px; height: 112px; margin: 4px auto 12px; border-radius: 50%; background: radial-gradient(circle, #062452 54%, transparent 56%), conic-gradient(#28d9ff 0 var(--confidence), rgba(36, 120, 178, .18) var(--confidence)); box-shadow: 0 0 20px rgba(30, 205, 255, .28); }.evidence-ring b { color: #effdff; font-size: 24px; }.evidence-ring small { color: #80b6d2; font-size: 9px; }.evidence-bars { display: grid; gap: 7px; }.evidence-bars span { position: relative; display: flex; justify-content: flex-end; overflow: hidden; color: #8db7ce; font-size: 9px; background: rgba(55, 127, 173, .18); }.evidence-bars i { position: absolute; inset: 0 auto 0 0; background: linear-gradient(90deg, rgba(31, 167, 255, .35), rgba(40, 229, 230, .5)); }
.impact-panel div { display: grid; grid-template-columns: repeat(3, 1fr); text-align: center; }.impact-panel span { color: #8ebbd3; font-size: 8px; }.impact-panel b { display: block; font-size: 20px; }
.role-strip { grid-column: 1 / -1; display: flex; min-width: 0; align-items: stretch; gap: 8px; min-height: 108px; overflow: hidden; padding: 10px; }.strip-title { display: flex; width: 128px; flex: 0 0 auto; flex-direction: column; justify-content: center; }.strip-title small { color: #34d7ff; font-size: 8px; letter-spacing: .14em; }.strip-title b { color: #dff9ff; font-size: 12px; }.strip-arrow { width: 34px; flex: 0 0 auto; border: 1px solid rgba(70, 205, 255, .4); color: #70eaff; font-size: 25px; background: rgba(5, 45, 96, .6); cursor: pointer; }.role-card { display: flex; min-width: 0; flex: 1 1 0; flex-direction: column; gap: 5px; border: 1px solid rgba(63, 178, 237, .25); padding: 9px; color: #b9def0; text-align: left; background: rgba(4, 33, 75, .58); cursor: pointer; transition: .2s ease; }.role-card:hover, .role-card.active { border-color: #33d9ff; background: rgba(7, 66, 126, .68); box-shadow: inset 0 -2px #2bd9ff, 0 0 14px rgba(38, 207, 255, .17); transform: translateY(-2px); }.role-card span { overflow: hidden; color: #e3f9ff; font-size: 11px; font-weight: 800; text-overflow: ellipsis; white-space: nowrap; }.role-card span i { margin-right: 6px; color: #35ddff; font-style: normal; }.role-card em { color: #66bde5; font-size: 9px; font-style: normal; }.role-card > b { color: #ffbd3e; font-size: 11px; }.role-card strong { color: #35ebb5; }.role-card > b i { color: #ff7897; font-style: normal; }

.hotspot-view, .compare-view { grid-template-columns: 260px minmax(640px, 1fr) 315px; }.hot-summary { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }.hot-summary span { position: relative; border: 1px solid rgba(55, 182, 244, .24); padding: 10px; color: #85b7d2; font-size: 9px; background: rgba(5, 47, 96, .5); }.hot-summary span > i { float: left; margin-right: 8px; color: #35ddff; font-size: 20px; font-style: normal; }.hot-summary b { display: block; color: #e9fcff; font-size: 22px; }.hot-summary em { display: block; margin-top: 3px; color: #37e8ad; font-style: normal; }.hot-summary em.down { color: #ff7895; }
.hot-trend-panel { min-height: 195px; }.mini-echart { height: 145px; }.heat-distribution { min-height: 168px; }.heat-donut { float: left; display: grid; place-items: center; width: 96px; height: 96px; margin-right: 12px; border-radius: 50%; background: radial-gradient(circle, #052354 54%, transparent 56%), conic-gradient(#ffb52e 0 10%, #37e6a1 10% 34%, #a26cff 34% 69%, #28cfff 69%); }.heat-donut b { color: #effdff; font-size: 23px; }.heat-donut small { color: #8cb8d0; font-size: 9px; }.heat-distribution ul { display: grid; gap: 7px; margin: 0; padding: 0; list-style: none; }.heat-distribution li { display: flex; align-items: center; color: #8fbad1; font-size: 9px; }.heat-distribution li i { width: 7px; height: 7px; margin-right: 6px; border-radius: 50%; background: currentColor; }.heat-distribution li b { margin-left: auto; color: #dff7ff; }.insight-panel.compact { min-height: 105px; }.insight-panel.compact b { color: #48e1ff; }
.graph-command, .domain-command { position: relative; min-width: 0; overflow: hidden; background: radial-gradient(circle at 50% 47%, rgba(0, 112, 176, .14), transparent 33%), linear-gradient(180deg, #020a13, #00050c 72%); }.graph-command { min-height: 690px; }.graph-command::after, .domain-command::after { width: auto; height: auto; inset: 0; opacity: .28; background-image: radial-gradient(circle, rgba(104, 222, 255, .52) 0 1px, transparent 1px), linear-gradient(rgba(34, 142, 217, .055) 1px, transparent 1px), linear-gradient(90deg, rgba(34, 142, 217, .055) 1px, transparent 1px); background-size: 31px 31px, 58px 58px, 58px 58px; box-shadow: none; }.graph-title { position: absolute; z-index: 5; top: 17px; left: 21px; display: flex; right: 21px; align-items: end; justify-content: space-between; }.graph-title > span { color: #6fb9db; font-size: 9px; }.hotspot-chart { position: relative; z-index: 2; height: 640px; margin-top: 36px; }.hotspot-chart::before, .hotspot-chart::after { position: absolute; z-index: 1; top: 50%; left: 50%; border: 1px solid rgba(85, 222, 255, .22); border-radius: 50%; content: ''; pointer-events: none; }.hotspot-chart::before { width: 440px; height: 210px; box-shadow: 0 0 28px rgba(22, 165, 255, .1), inset 0 0 24px rgba(22, 165, 255, .08); transform: translate(-50%, -50%) rotate(17deg); animation: gyroA 13s cubic-bezier(.45,.05,.55,.95) infinite alternate; }.hotspot-chart::after { width: 300px; height: 520px; border-style: dashed; opacity: .68; transform: translate(-50%, -50%) rotate(-28deg); animation: gyroB 17s cubic-bezier(.45,.05,.55,.95) infinite alternate; }.active-skill-readout { position: absolute; z-index: 6; top: 79px; right: 18px; display: grid; min-width: 130px; border-right: 1px solid #83edff; padding: 7px 10px; text-align: right; background: linear-gradient(90deg, transparent, rgba(1, 22, 40, .9)); }.active-skill-readout span { color: #32dfff; font-size: 7px; letter-spacing: .18em; }.active-skill-readout b { color: #effdff; font-size: 12px; }.active-skill-readout strong { color: #45edbf; font-size: 21px; }.active-skill-readout em { color: #72aeca; font-size: 8px; font-style: normal; }.graph-legend { position: absolute; z-index: 6; bottom: 16px; left: 50%; display: flex; gap: 15px; border: 1px solid rgba(65, 193, 255, .24); padding: 7px 14px; color: #a5d5e9; font-size: 9px; background: rgba(0, 8, 19, .92); transform: translateX(-50%); }.graph-legend span::before { display: inline-block; width: 7px; height: 7px; margin-right: 5px; border-radius: 0; background: currentColor; content: ''; transform: rotate(45deg); }.level-high { color: #ffb52e !important; }.level-mid { color: #37e6a1 !important; }.level-warm { color: #a26cff !important; }.level-low { color: #28cfff !important; }
.graph-hit-targets { position: absolute; z-index: 5; inset: 60px 0 45px; pointer-events: none; }.graph-hit-targets button { position: absolute; width: 82px; height: 82px; border: 0; background: transparent; cursor: pointer; pointer-events: auto; transform: translate(-50%, -50%); clip-path: polygon(50% 0, 92% 25%, 92% 75%, 50% 100%, 8% 75%, 8% 25%); }.graph-hit-targets button:hover { outline: 1px dashed rgba(116, 238, 255, .72); outline-offset: 4px; box-shadow: 0 0 20px rgba(50, 217, 255, .18); }
.ranking-panel { flex: 1; }.rising-panel .panel-title h3 { color: #49ebc1; }.declining-panel .panel-title h3 { color: #ff7d9d; }.skill-chips { display: flex; flex-wrap: wrap; gap: 6px; }.skill-chips button { border: 1px solid rgba(59, 206, 255, .42); border-radius: 99px; padding: 4px 9px; color: #ccefff; font-size: 9px; background: rgba(4, 45, 93, .65); cursor: pointer; }.skill-chips button:hover { color: #fff; border-color: #4de8ff; box-shadow: 0 0 10px rgba(42, 215, 255, .25); }.sparkline { height: 45px; margin: 10px 0 3px; background: linear-gradient(170deg, transparent 0 45%, currentColor 46% 48%, transparent 49%), linear-gradient(12deg, transparent 0 52%, currentColor 53% 55%, transparent 56%); opacity: .8; filter: drop-shadow(0 0 5px currentColor); }.green-line { color: #32e8b3; }.red-line { color: #ff6d91; transform: scaleY(-1); }.ranking-list { display: grid; }.ranking-list button { display: grid; grid-template-columns: 20px minmax(0, 1fr) 44px 58px; align-items: center; gap: 5px; border: 0; border-bottom: 1px solid rgba(65, 175, 230, .16); padding: 7px 2px; color: #c8e9f6; text-align: left; background: transparent; cursor: pointer; }.ranking-list button:hover { background: rgba(20, 119, 184, .16); }.ranking-list i { color: #ffbd3b; font-style: normal; }.ranking-list span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }.ranking-list b { color: #dffaff; font-size: 10px; }.ranking-list em { color: #34e6b0; font-size: 9px; font-style: normal; text-align: right; }.declining-panel .ranking-list em { color: #ff7596; }

.compare-view { min-height: 690px; }.domain-stack { justify-content: space-between; }.domain-card { display: grid; grid-template-columns: 42px 82px 1fr; align-items: start; gap: 8px; min-height: 132px; padding: 14px; text-align: left; cursor: pointer; transition: .2s ease; }.domain-card:hover, .domain-card.active { border-color: #35dfff; background: linear-gradient(145deg, rgba(7, 64, 126, .94), rgba(2, 19, 51, .92)); box-shadow: inset 0 0 22px rgba(30, 186, 255, .16), 0 0 18px rgba(29, 197, 255, .16); transform: translateX(4px); }.domain-stack:last-child .domain-card:hover, .domain-stack:last-child .domain-card.active { transform: translateX(-4px); }.domain-icon { display: grid; place-items: center; width: 38px; height: 38px; border: 1px solid #35dfff; border-radius: 50%; color: #6eeaff; font-size: 13px; font-weight: 900; background: rgba(8, 79, 139, .46); box-shadow: 0 0 14px rgba(39, 211, 255, .34); }.domain-card h3 { margin: 0 0 5px; color: #e9faff; font-size: 13px; }.domain-card > div > b { color: #4c8fff; font-size: 22px; }.domain-card ul { display: grid; gap: 4px; margin: 0; padding: 0; list-style: none; }.domain-card li { display: flex; gap: 5px; color: #9bc3d8; font-size: 9px; }.domain-card li span { overflow: hidden; flex: 1; text-overflow: ellipsis; white-space: nowrap; }.domain-card li em { color: #ccecff; font-style: normal; }
.domain-command { min-height: 690px; }.domain-chart { position: relative; z-index: 2; height: 610px; margin-top: 35px; filter: drop-shadow(0 24px 26px rgba(0, 0, 0, .5)); }.domain-chart::before { position: absolute; z-index: 0; top: 47%; left: 50%; width: 510px; height: 510px; border: 18px solid rgba(16, 48, 68, .3); border-radius: 50%; content: ''; box-shadow: inset 0 0 28px #000, 0 0 18px rgba(38, 190, 255, .12); transform: translate(-50%, -50%); pointer-events: none; }.domain-focus { position: absolute; z-index: 6; top: 78px; right: 20px; display: flex; flex-direction: column; align-items: flex-end; border-right: 1px solid #73e9ff; padding: 6px 10px; background: linear-gradient(90deg, transparent, rgba(1, 22, 40, .9)); }.domain-focus small { color: #36ddff; font-size: 7px; letter-spacing: .16em; }.domain-focus b { color: #effdff; font-size: 13px; }.domain-focus strong { color: #45eece; font-size: 24px; text-shadow: 0 0 12px currentColor; }.domain-focus span { max-width: 190px; color: #76abc5; font-size: 8px; text-align: right; }.wheel-note { position: absolute; z-index: 7; right: 10px; bottom: 9px; left: 10px; display: grid; grid-template-columns: repeat(4, 1fr); border: 1px solid rgba(58, 198, 255, .22); background: rgba(0, 7, 17, .94); }.wheel-note span { padding: 9px 12px; border-right: 1px solid rgba(58, 198, 255, .13); color: #79a9c4; font-size: 8px; }.wheel-note span:last-child { border: 0; }.wheel-note b, .wheel-note em { display: block; }.wheel-note b { color: #e9fbff; font-size: 13px; }.wheel-note em { color: #39e7bb; font-size: 9px; font-style: normal; }

/* Premium holographic reactor pass for version comparison */
.version-command { background: radial-gradient(ellipse at 50% 76%, rgba(0, 106, 181, .16), transparent 43%), linear-gradient(180deg, #020914, #00040a 74%); }
.version-lab { min-height: 390px; padding-top: 28px; }
.version-lab::before { position: absolute; z-index: -1; right: -8%; bottom: -12px; left: -8%; height: 205px; border: 1px solid rgba(63, 180, 246, .13); border-radius: 50%; content: ''; background: repeating-radial-gradient(ellipse, transparent 0 25px, rgba(48, 157, 221, .085) 26px 27px), repeating-linear-gradient(90deg, transparent 0 46px, rgba(48, 157, 221, .055) 47px 48px); box-shadow: inset 0 -24px 42px rgba(0,0,0,.55); transform: perspective(450px) rotateX(65deg); }
.energy-well { filter: saturate(.9); transition: transform .7s cubic-bezier(.32,.72,0,1), filter .7s cubic-bezier(.32,.72,0,1); }.energy-well:hover, .energy-well.active { filter: saturate(1.08) brightness(1.12); transform: translateY(-11px); }
.well-label { margin-bottom: 2px; color: currentColor; font-size: 16px; letter-spacing: .04em; text-shadow: 0 0 12px color-mix(in srgb, currentColor 42%, transparent); }.well-label b { font-size: 27px; }
.well-chamber { width: 98%; height: 255px; clip-path: polygon(42% 0, 58% 0, 97% 100%, 3% 100%); background: linear-gradient(90deg, transparent 1%, color-mix(in srgb, currentColor 3%, transparent) 18%, color-mix(in srgb, currentColor 18%, transparent) 48%, color-mix(in srgb, currentColor 3%, transparent) 82%, transparent 99%); filter: drop-shadow(0 18px 18px color-mix(in srgb, currentColor 16%, transparent)); }
.well-chamber::before { inset: 0 11%; opacity: .58; background: repeating-linear-gradient(90deg, transparent 0 16px, color-mix(in srgb, currentColor 15%, transparent) 17px 18px), repeating-linear-gradient(0deg, transparent 0 28px, color-mix(in srgb, currentColor 12%, transparent) 29px 30px), linear-gradient(180deg, transparent, color-mix(in srgb, currentColor 24%, transparent)); }
.well-chamber::after { right: 6%; bottom: 4px; left: 6%; height: 42px; border-color: color-mix(in srgb, currentColor 72%, #fff); opacity: .76; box-shadow: 0 0 16px currentColor, inset 0 0 17px color-mix(in srgb, currentColor 48%, transparent); }
.well-particles { opacity: .7; background-size: 21px 28px, 34px 25px; animation-duration: 7.5s; }.well-particles--far { opacity: .22; background-size: 37px 41px, 51px 36px; filter: blur(.7px); animation-duration: 11s; animation-direction: reverse; }
.well-beam { width: 11%; opacity: .22; filter: blur(9px); animation-duration: 4.8s; }
.well-core { position: absolute; z-index: 1; bottom: 17px; left: 50%; width: 78px; height: 28px; border: 1px solid color-mix(in srgb, currentColor 76%, #fff); border-radius: 50%; background: radial-gradient(ellipse, #fff 0 5%, currentColor 18%, color-mix(in srgb, currentColor 36%, transparent) 42%, transparent 72%); box-shadow: 0 0 22px currentColor, inset 0 0 13px #fff; transform: translateX(-50%); }.well-core b { position: absolute; bottom: 7px; left: 50%; width: 10px; height: 170px; background: linear-gradient(180deg, transparent, currentColor 75%, #fff); opacity: .22; filter: blur(6px); transform: translateX(-50%); }
.well-chamber em { z-index: 3; border-color: color-mix(in srgb, currentColor 54%, #fff); border-radius: 4px; padding: 6px 13px; background: linear-gradient(180deg, rgba(7, 25, 42, .92), rgba(0, 8, 17, .94)); box-shadow: inset 0 1px rgba(255,255,255,.08), 0 0 10px color-mix(in srgb, currentColor 18%, transparent); letter-spacing: .02em; }
.well-base { width: 120%; height: 66px; margin-top: -22px; border-color: color-mix(in srgb, currentColor 65%, #dffcff); background: repeating-radial-gradient(ellipse, #010306 0 8px, #111f28 9px 12px, #020609 13px 17px); box-shadow: 0 0 15px color-mix(in srgb, currentColor 43%, transparent), inset 0 -15px 22px #000, inset 0 0 18px color-mix(in srgb, currentColor 19%, transparent); }.well-base em { position: absolute; inset: 27px 62px; border: 1px solid currentColor; border-radius: 50%; background: radial-gradient(ellipse, #fff, currentColor 18%, #02070b 58%); box-shadow: 0 0 17px currentColor; }
.well-plinth { position: relative; z-index: 1; width: 92%; height: 28px; margin-top: -28px; border: 1px solid color-mix(in srgb, currentColor 44%, #fff); border-radius: 50%; background: linear-gradient(180deg, #182833, #020609 64%); box-shadow: inset 0 5px 9px rgba(255,255,255,.07), 0 11px 18px rgba(0,0,0,.65); transform: perspective(260px) rotateX(65deg); }.well-plinth::before, .well-plinth i { position: absolute; border-radius: 50%; content: ''; }.well-plinth::before { inset: 6px 19px; border: 1px solid color-mix(in srgb, currentColor 32%, transparent); }.well-plinth i { inset: -6px -19px; border: 1px dashed color-mix(in srgb, currentColor 28%, transparent); animation: spin 18s cubic-bezier(.45,.05,.55,.95) infinite; }
.focused-change { border-color: rgba(78, 192, 243, .18); background: linear-gradient(90deg, rgba(2, 20, 37, .94), rgba(0, 6, 15, .94)); }

@keyframes spin { to { transform: rotate(360deg); } }
@keyframes beamPulse { 50% { opacity: .4; transform: scaleX(1.45); } }
@keyframes particlesRise { to { background-position: 0 -92px; } }
@keyframes gyroA { to { transform: translate(-50%, -50%) rotate(48deg) scaleX(.92); opacity: .42; } }
@keyframes gyroB { to { transform: translate(-50%, -50%) rotate(7deg) scaleY(.92); opacity: .34; } }
.graph-command, .domain-command { background: radial-gradient(circle at 50% 47%, rgba(0, 74, 116, .08), transparent 28%), #01060c; }
.domain-chart { filter: none; }
@media (max-width: 1250px) { .version-view, .hotspot-view, .compare-view { grid-template-columns: 230px minmax(520px, 1fr); }.version-view > .hud-stack:nth-of-type(2), .hotspot-view > .hud-stack:nth-of-type(2), .compare-view > .domain-stack:last-child { grid-column: 1 / -1; display: grid; grid-template-columns: repeat(3, 1fr); }.role-strip { grid-column: 1 / -1; }.domain-stack:last-child { grid-template-columns: repeat(4, 1fr) !important; } }
@media (max-width: 900px) { .version-view, .hotspot-view, .compare-view { display: flex; flex-direction: column; }.hud-stack, .domain-stack, .version-view > .hud-stack:nth-of-type(2), .hotspot-view > .hud-stack:nth-of-type(2), .compare-view > .domain-stack:last-child { display: grid; grid-template-columns: 1fr; }.role-strip { overflow-x: auto; }.energy-well { min-width: 150px; }.version-lab { overflow-x: auto; }.domain-stack:last-child { grid-template-columns: 1fr !important; } }
</style>

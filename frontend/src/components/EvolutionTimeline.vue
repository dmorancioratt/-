<template>
  <section class="timeline-workbench">
    <div class="metric-deck">
      <button
        v-for="metric in metrics"
        :key="metric.key"
        type="button"
        class="metric-module"
        :class="[`metric-module--${metric.key}`, { active: activeMetric === metric.key }]"
        @click="activeMetric = metric.key"
      >
        <span class="metric-cube"><i>{{ metric.symbol }}</i></span>
        <span class="metric-copy"><small>{{ metric.label }}</small><b>{{ metric.value }}</b><em>较上月 <strong>{{ metric.delta }}</strong></em></span>
        <i class="metric-scan"></i>
      </button>
    </div>

    <div class="timeline-grid">
      <main class="hud-shell timeline-command">
        <div class="particle-field" aria-hidden="true"><i v-for="particle in particles" :key="particle.id" :style="particle.style"></i></div>
        <div class="command-head">
          <div><small>EVOLUTION ENERGY CHANNEL</small><h2>能力演化时间线</h2></div>
          <div class="stream-legend"><button v-for="item in streamLegend" :key="item.key" type="button" :class="[`legend-${item.key}`, { active: activeMetric === item.key }]" @click="activeMetric = item.key"><i></i>{{ item.label }}</button></div>
          <span class="live-state"><i></i>LIVE DATA</span>
        </div>

        <div class="energy-stage">
          <svg class="energy-streams" viewBox="0 0 1000 430" preserveAspectRatio="none" aria-hidden="true">
            <defs>
              <linearGradient id="flowAdd" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2af0b6" stop-opacity=".05"/><stop offset=".48" stop-color="#58ffd2"/><stop offset="1" stop-color="#2af0b6" stop-opacity=".05"/></linearGradient>
              <linearGradient id="flowRemove" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ff648a" stop-opacity=".05"/><stop offset=".48" stop-color="#ff96ad"/><stop offset="1" stop-color="#ff648a" stop-opacity=".05"/></linearGradient>
              <linearGradient id="flowModify" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffb637" stop-opacity=".05"/><stop offset=".48" stop-color="#ffd16a"/><stop offset="1" stop-color="#ffb637" stop-opacity=".05"/></linearGradient>
              <filter id="flowGlow" x="-30%" y="-100%" width="160%" height="300%"><feGaussianBlur stdDeviation="6" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
            </defs>
            <g class="flow-group flow-group--add" :class="{ muted: activeMetric !== 'all' && activeMetric !== 'add' }">
              <path class="flow-haze" d="M245 155 C360 84 420 219 500 164 S650 92 755 145" stroke="url(#flowAdd)"/>
              <path class="flow-band" d="M245 155 C360 84 420 219 500 164 S650 92 755 145" stroke="url(#flowAdd)"/>
              <path class="flow-filament" transform="translate(0 -8)" d="M245 155 C360 84 420 219 500 164 S650 92 755 145" stroke="url(#flowAdd)"/>
              <path class="flow-filament" transform="translate(0 8)" d="M245 155 C360 84 420 219 500 164 S650 92 755 145" stroke="url(#flowAdd)"/>
              <path class="flow-line" d="M245 155 C360 84 420 219 500 164 S650 92 755 145" stroke="url(#flowAdd)"/>
              <circle r="5" fill="#71ffda" filter="url(#flowGlow)"><animateMotion dur="3.3s" repeatCount="indefinite" path="M245 155 C360 84 420 219 500 164 S650 92 755 145"/></circle>
              <circle r="3" fill="#d7fff5"><animateMotion dur="4.7s" begin="-1.8s" repeatCount="indefinite" path="M245 155 C360 84 420 219 500 164 S650 92 755 145"/></circle>
            </g>
            <g class="flow-group flow-group--remove" :class="{ muted: activeMetric !== 'all' && activeMetric !== 'remove' }">
              <path class="flow-haze" d="M245 230 C355 285 421 169 505 222 S644 284 755 224" stroke="url(#flowRemove)"/>
              <path class="flow-band" d="M245 230 C355 285 421 169 505 222 S644 284 755 224" stroke="url(#flowRemove)"/>
              <path class="flow-filament" transform="translate(0 -8)" d="M245 230 C355 285 421 169 505 222 S644 284 755 224" stroke="url(#flowRemove)"/>
              <path class="flow-filament" transform="translate(0 8)" d="M245 230 C355 285 421 169 505 222 S644 284 755 224" stroke="url(#flowRemove)"/>
              <path class="flow-line" d="M245 230 C355 285 421 169 505 222 S644 284 755 224" stroke="url(#flowRemove)"/>
              <circle r="5" fill="#ff9ab0" filter="url(#flowGlow)"><animateMotion dur="3.9s" repeatCount="indefinite" path="M245 230 C355 285 421 169 505 222 S644 284 755 224"/></circle>
              <circle r="3" fill="#ffe1e8"><animateMotion dur="5.1s" begin="-2.4s" repeatCount="indefinite" path="M245 230 C355 285 421 169 505 222 S644 284 755 224"/></circle>
            </g>
            <g class="flow-group flow-group--modify" :class="{ muted: activeMetric !== 'all' && activeMetric !== 'modify' }">
              <path class="flow-haze" d="M245 304 C348 260 423 346 505 294 S650 266 755 300" stroke="url(#flowModify)"/>
              <path class="flow-band" d="M245 304 C348 260 423 346 505 294 S650 266 755 300" stroke="url(#flowModify)"/>
              <path class="flow-filament" transform="translate(0 -8)" d="M245 304 C348 260 423 346 505 294 S650 266 755 300" stroke="url(#flowModify)"/>
              <path class="flow-filament" transform="translate(0 8)" d="M245 304 C348 260 423 346 505 294 S650 266 755 300" stroke="url(#flowModify)"/>
              <path class="flow-line" d="M245 304 C348 260 423 346 505 294 S650 266 755 300" stroke="url(#flowModify)"/>
              <circle r="5" fill="#ffd575" filter="url(#flowGlow)"><animateMotion dur="3.5s" repeatCount="indefinite" path="M245 304 C348 260 423 346 505 294 S650 266 755 300"/></circle>
              <circle r="3" fill="#fff0c7"><animateMotion dur="4.4s" begin="-1.2s" repeatCount="indefinite" path="M245 304 C348 260 423 346 505 294 S650 266 755 300"/></circle>
            </g>
          </svg>

          <div class="delta-stack">
            <span class="delta-add"><small>新增</small><b>{{ signedDelta('added') }}</b></span>
            <span class="delta-remove"><small>淘汰</small><b>{{ signedDelta('removed') }}</b></span>
            <span class="delta-modify"><small>修改</small><b>{{ signedDelta('modified') }}</b></span>
          </div>

          <button
            v-for="(period, index) in periods"
            :key="`${period.date}-${index}`"
            type="button"
            class="energy-tower"
            :class="[{ active: activePeriodIndex === index }, index === 0 ? 'tower-left' : 'tower-right']"
            @click="activePeriodIndex = index"
          >
            <span class="tower-date"><small>TIME NODE 0{{ index + 1 }}</small><b>{{ period.date }}</b></span>
            <span class="tower-cap"><i></i><b></b></span>
            <span class="tower-glass">
              <i class="glass-grid"></i><i class="glass-scan"></i><i class="glass-beam"></i><i class="glass-reflection reflection-a"></i><i class="glass-reflection reflection-b"></i>
              <span class="tower-stat stat-add"><i>+</i><small>新增</small><b>{{ period.added }}</b></span>
              <span class="tower-stat stat-remove"><i>×</i><small>淘汰</small><b>{{ period.removed }}</b></span>
              <span class="tower-stat stat-modify"><i>✦</i><small>修改</small><b>{{ period.modified }}</b></span>
            </span>
            <span class="tower-base"><i></i><b></b><em></em></span><span class="tower-plinth"><i></i></span>
            <span class="tower-total">TOTAL <b>{{ period.total }}</b></span>
          </button>

          <div class="time-scale"><i></i><button v-for="(period, index) in periods" :key="period.date" type="button" :class="{ active: activePeriodIndex === index }" @click="activePeriodIndex = index"><span></span>{{ period.date }}</button></div>
        </div>

        <div class="selected-event" v-if="selectedEvent">
          <span class="selected-icon">{{ eventIcon(selectedEventIndex) }}</span>
          <div><small>SELECTED EVENT · {{ selectedEvent.version || 'LATEST' }}</small><b>{{ selectedEvent.jobName }}</b><p>{{ selectedEvent.note || '该岗位能力画像已完成版本更新。' }}</p></div>
          <div class="selected-tags"><i v-for="skill in selectedEvent.added?.slice(0, 2) || []" :key="skill" class="tag-add">+ {{ skill }}</i><i v-for="skill in selectedEvent.removed?.slice(0, 1) || []" :key="skill" class="tag-remove">− {{ skill }}</i><i v-for="skill in selectedEvent.modified?.slice(0, 1) || []" :key="skill.name" class="tag-modify">~ {{ skill.name }}</i></div>
          <strong>{{ Math.round((selectedEvent.confidence || 0) * 100) }}<small>%</small></strong>
        </div>

        <div class="analysis-deck">
          <div class="analysis-copy"><span class="analysis-radar"><i></i></span><p><b>分析摘要</b>当前选中 {{ periods[activePeriodIndex]?.date }} 节点，本期能力变更以新增与调整为主，三路粒子流展示技能迁移方向与强度。</p></div>
          <div class="analysis-cell"><small>净变化</small><b>{{ netChange >= 0 ? '+' : '' }}{{ netChange }}</b><em>新增 − 淘汰</em></div>
          <div class="analysis-cell tone-add"><small>新增占比</small><b>{{ percentages.add }}%</b><em>持续扩展</em></div>
          <div class="analysis-cell tone-remove"><small>淘汰占比</small><b>{{ percentages.remove }}%</b><em>及时收敛</em></div>
          <div class="analysis-cell tone-modify"><small>修改占比</small><b>{{ percentages.modify }}%</b><em>结构优化</em></div>
        </div>
      </main>

      <aside class="hud-shell event-console">
        <div class="console-head"><div><small>EVENT LOG</small><h3>更新事件明细</h3></div><button type="button">全部角色⌄</button></div>
        <div class="console-filter"><button type="button" :class="{ active: eventFilter === 'all' }" @click="eventFilter = 'all'">全部</button><button type="button" :class="{ active: eventFilter === 'high' }" @click="eventFilter = 'high'">高置信</button><span>{{ filteredEvents.length }} EVENTS</span></div>
        <div class="event-list">
          <button
            v-for="(event, index) in visibleEvents"
            :key="`${event.jobName}-${index}`"
            type="button"
            class="event-card"
            :class="{ active: selectedEvent === event }"
            @click="selectEvent(event)"
          >
            <span class="event-icon">{{ eventIcon(index) }}</span>
            <span class="event-body">
              <span class="event-title"><b>{{ event.jobName }}</b><i>{{ event.version || 'v1.0' }}</i><time>{{ event.date }}</time></span>
              <p>{{ event.note || '岗位能力画像发生更新，证据链已同步。' }}</p>
              <span class="event-tags"><i v-for="skill in event.added?.slice(0, 2) || []" :key="`a-${skill}`" class="tag-add">+{{ skill }}</i><i v-for="skill in event.removed?.slice(0, 1) || []" :key="`r-${skill}`" class="tag-remove">−{{ skill }}</i><i v-for="skill in event.modified?.slice(0, 1) || []" :key="`m-${skill.name}`" class="tag-modify">~{{ skill.name }}</i></span>
              <span class="confidence"><small>置信度 {{ Math.round((event.confidence || 0) * 100) }}%</small><i><b :style="{ width: `${Math.round((event.confidence || 0) * 100)}%` }"></b></i></span>
            </span>
          </button>
          <div v-if="!visibleEvents.length" class="empty-log">暂无符合条件的更新事件</div>
        </div>
        <button class="expand-events" type="button" @click="showAll = !showAll">{{ showAll ? '收起事件' : '查看全部事件' }} <span>{{ showAll ? '↑' : '↓' }}</span></button>
      </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

const props = defineProps<{ timeline: any }>()
type EvolutionPeriod = { date: string; added: number; removed: number; modified: number; total: number }

const activeMetric = ref('all')
const activePeriodIndex = ref(1)
const eventFilter = ref('all')
const showAll = ref(false)
const selectedEventIndex = ref(0)

const particles = Array.from({ length: 34 }, (_, index) => ({
  id: index,
  style: {
    '--x': `${(index * 37) % 97}%`, '--y': `${(index * 61) % 91}%`, '--s': `${2 + (index % 3)}px`,
    '--delay': `${-(index % 8) * .7}s`, '--duration': `${4.5 + (index % 5)}s`
  }
}))
const streamLegend = [{ key: 'add', label: '新增' }, { key: 'remove', label: '淘汰' }, { key: 'modify', label: '修改' }]

const periods = computed<EvolutionPeriod[]>(() => {
  const rows = props.timeline?.timeline || []
  const source = rows.length >= 2 ? rows.slice(-2) : rows
  const fallback = [{ date: '2026-06', added: 12, removed: 6, modified: 8 }, { date: '2026-07', added: 12, removed: 6, modified: 6 }]
  return (source.length >= 2 ? source : fallback).map((row: any) => ({
    date: row.date || '当前', added: Number(row.added || 0), removed: Number(row.removed || 0), modified: Number(row.modified || 0),
    total: Number(row.added || 0) + Number(row.removed || 0) + Number(row.modified || 0)
  }))
})
watch(periods, (rows) => { activePeriodIndex.value = Math.max(0, rows.length - 1) }, { immediate: true })

const allEvents = computed<any[]>(() => props.timeline?.events || [])
const fallbackEvent = computed(() => ({ jobName: 'AI 产品经理', version: 'v1.2', date: periods.value.at(-1)?.date, note: '岗位画像更强调业务场景、证据来源和可落地成果。', added: ['Milvus', 'Faiss'], removed: ['旧版流程'], modified: [{ name: 'OpenAPI' }], confidence: .91 }))
const filteredEvents = computed(() => {
  const source = allEvents.value.length ? allEvents.value : [fallbackEvent.value]
  return eventFilter.value === 'high' ? source.filter((item) => Number(item.confidence || 0) >= .8) : source
})
const visibleEvents = computed(() => filteredEvents.value.slice(0, showAll.value ? 8 : 4))
const selectedEvent = computed(() => {
  const source = allEvents.value.length ? allEvents.value : [fallbackEvent.value]
  return source[selectedEventIndex.value] || source[0]
})

const total = computed(() => periods.value.reduce((sum, row) => sum + row.total, 0))
const added = computed(() => periods.value.reduce((sum, row) => sum + row.added, 0))
const removed = computed(() => periods.value.reduce((sum, row) => sum + row.removed, 0))
const modified = computed(() => periods.value.reduce((sum, row) => sum + row.modified, 0))
const netChange = computed(() => added.value - removed.value)
const percentages = computed(() => {
  const denominator = added.value + removed.value + modified.value || 1
  return { add: (added.value / denominator * 100).toFixed(0), remove: (removed.value / denominator * 100).toFixed(0), modify: (modified.value / denominator * 100).toFixed(0) }
})
const metrics = computed(() => [
  { key: 'all', symbol: '↻', label: '更新事件', value: props.timeline?.total || allEvents.value.length || total.value, delta: '9.1%' },
  { key: 'add', symbol: '+', label: '新增技能', value: added.value, delta: '14.3%' },
  { key: 'remove', symbol: '×', label: '淘汰技能', value: removed.value, delta: '4.8%' },
  { key: 'modify', symbol: '✦', label: '修改技能', value: modified.value, delta: '6.7%' }
])

function signedDelta(key: 'added' | 'removed' | 'modified') {
  const first = periods.value[0]?.[key] || 0; const last = periods.value.at(-1)?.[key] || 0; const value = last - first
  return `${value > 0 ? '+' : ''}${value}`
}
function selectEvent(event: any) {
  const source = allEvents.value.length ? allEvents.value : [fallbackEvent.value]
  selectedEventIndex.value = Math.max(0, source.indexOf(event))
  const periodIndex = periods.value.findIndex((period) => period.date === event.date)
  if (periodIndex >= 0) activePeriodIndex.value = periodIndex
}
function eventIcon(index: number) { return ['◇', 'AI', '▦', '✦', '⌁'][index % 5] }
</script>

<style scoped>
.timeline-workbench { --cyan: #2bdcff; --panel-line: rgba(49, 195, 255, .34); display: flex; flex-direction: column; gap: 14px; color: #c9edff; }
button { font: inherit; }
.metric-deck { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 13px; }
.metric-module { position: relative; display: flex; min-height: 116px; align-items: center; gap: 14px; overflow: hidden; border: 1px solid rgba(55, 197, 255, .34); padding: 15px 18px; color: inherit; text-align: left; background: linear-gradient(135deg, rgba(5, 47, 102, .88), rgba(2, 17, 51, .88)); clip-path: polygon(0 11px, 11px 0, calc(100% - 25px) 0, 100% 24px, 100% calc(100% - 10px), calc(100% - 10px) 100%, 13px 100%, 0 calc(100% - 13px)); cursor: pointer; transition: .22s ease; }
.metric-module::before { position: absolute; top: 0; left: 20px; width: 46%; height: 2px; content: ''; background: #32dfff; box-shadow: 0 0 12px #24ceff; }.metric-module:hover, .metric-module.active { border-color: #48e5ff; transform: translateY(-3px); box-shadow: inset 0 0 28px rgba(27, 153, 237, .15), 0 10px 26px rgba(0, 7, 35, .3); }
.metric-cube { position: relative; display: grid; width: 68px; height: 68px; flex: 0 0 auto; place-items: center; border: 1px solid #36dfff; color: #70edff; background: radial-gradient(circle, rgba(20, 154, 255, .38), rgba(2, 27, 70, .72) 64%); clip-path: polygon(25% 7%, 75% 7%, 100% 50%, 75% 93%, 25% 93%, 0 50%); box-shadow: inset 0 0 20px rgba(38, 210, 255, .25); }.metric-cube::before, .metric-cube::after { position: absolute; inset: 8px; border: 1px solid currentColor; content: ''; clip-path: inherit; opacity: .4; }.metric-cube::after { inset: 18px; opacity: .75; }.metric-cube i { z-index: 2; font-size: 30px; font-style: normal; font-weight: 900; text-shadow: 0 0 12px currentColor; }
.metric-copy { display: flex; flex-direction: column; }.metric-copy small { color: #b8e4f5; font-size: 12px; font-weight: 800; }.metric-copy b { color: #f0fdff; font-size: 32px; line-height: 1.15; }.metric-copy em { color: #78aac7; font-size: 10px; font-style: normal; }.metric-copy strong { color: #37eab2; }.metric-scan { position: absolute; right: 0; bottom: 6px; left: 0; height: 1px; background: linear-gradient(90deg, transparent, #32dfff, transparent); animation: metricScan 3.8s linear infinite; }
.metric-module--remove .metric-cube { border-color: #ff7195; color: #ff8ea9; background: radial-gradient(circle, rgba(255, 50, 106, .3), rgba(45, 5, 38, .7) 65%); }.metric-module--remove::before, .metric-module--remove .metric-scan { background: #ff7195; box-shadow: 0 0 12px #ff547f; }.metric-module--remove .metric-copy strong { color: #ff7898; }.metric-module--modify .metric-cube { border-color: #ffc14b; color: #ffd06c; background: radial-gradient(circle, rgba(255, 171, 33, .28), rgba(55, 28, 4, .72) 65%); }.metric-module--modify::before, .metric-module--modify .metric-scan { background: #ffc14b; box-shadow: 0 0 12px #ffb52e; }
.timeline-grid { display: grid; grid-template-columns: minmax(700px, 1fr) 340px; gap: 14px; min-height: 720px; }
.hud-shell { position: relative; overflow: hidden; border: 1px solid var(--panel-line); background: linear-gradient(145deg, rgba(4, 31, 75, .9), rgba(2, 14, 43, .9)); clip-path: polygon(0 14px, 14px 0, calc(100% - 24px) 0, 100% 24px, 100% calc(100% - 13px), calc(100% - 13px) 100%, 13px 100%, 0 calc(100% - 13px)); box-shadow: inset 0 0 40px rgba(12, 107, 183, .08), 0 18px 38px rgba(0, 5, 29, .3); }.hud-shell::before, .hud-shell::after { position: absolute; z-index: 8; width: 48px; height: 2px; content: ''; background: #31dcff; box-shadow: 0 0 12px #21cfff; }.hud-shell::before { top: 0; left: 25px; }.hud-shell::after { right: 25px; bottom: 0; }
.timeline-command { min-width: 0; padding: 18px 20px 14px; }.particle-field { position: absolute; inset: 0; pointer-events: none; }.particle-field::before { position: absolute; inset: 0; content: ''; opacity: .45; background-image: linear-gradient(rgba(39, 148, 219, .07) 1px, transparent 1px), linear-gradient(90deg, rgba(39, 148, 219, .07) 1px, transparent 1px); background-size: 48px 48px; mask-image: linear-gradient(to bottom, transparent, #000 38%, #000); }.particle-field i { position: absolute; top: var(--y); left: var(--x); width: var(--s); height: var(--s); border-radius: 50%; background: #55e8ff; box-shadow: 0 0 9px #2acfff; animation: drift var(--duration) ease-in-out var(--delay) infinite; }
.command-head { position: relative; z-index: 10; display: flex; align-items: center; gap: 18px; }.command-head small { color: #39dfff; font-size: 8px; font-weight: 850; letter-spacing: .17em; }.command-head h2 { margin: 2px 0 0; color: #eefcff; font-size: 18px; }.stream-legend { display: flex; gap: 7px; margin-left: auto; }.stream-legend button { border: 1px solid rgba(69, 191, 247, .28); padding: 5px 9px; color: #8fbad1; font-size: 9px; background: rgba(4, 40, 85, .55); cursor: pointer; }.stream-legend button i { display: inline-block; width: 7px; height: 7px; margin-right: 5px; border-radius: 2px; background: currentColor; }.stream-legend button.active { border-color: currentColor; color: #fff; box-shadow: 0 0 10px color-mix(in srgb, currentColor 35%, transparent); }.legend-add { color: #35edb6 !important; }.legend-remove { color: #ff7796 !important; }.legend-modify { color: #ffc04a !important; }.live-state { color: #62dfff; font-size: 8px; font-weight: 800; letter-spacing: .12em; }.live-state i { display: inline-block; width: 6px; height: 6px; margin-right: 5px; border-radius: 50%; background: #2ef0b3; box-shadow: 0 0 9px #2ef0b3; animation: pulse 1.5s ease-in-out infinite; }
.energy-stage { position: relative; z-index: 3; min-height: 470px; margin-top: 5px; }.energy-stage::after { position: absolute; right: 5%; bottom: 27px; left: 5%; height: 135px; border: 1px solid rgba(30, 156, 255, .24); border-radius: 50%; content: ''; background: repeating-radial-gradient(ellipse, transparent 0 21px, rgba(31, 147, 230, .13) 22px 23px), linear-gradient(180deg, transparent, rgba(4, 66, 126, .19)); box-shadow: 0 0 35px rgba(22, 127, 218, .18); transform: perspective(500px) rotateX(66deg); }
.energy-streams { position: absolute; z-index: 3; inset: 12px 0 auto; width: 100%; height: 420px; overflow: visible; }.flow-haze, .flow-line { fill: none; stroke-linecap: round; }.flow-haze { stroke-width: 18; opacity: .17; filter: blur(7px); }.flow-line { stroke-width: 3; stroke-dasharray: 14 9; filter: url(#flowGlow); animation: flowDash 2.2s linear infinite; }.flow-group { transition: opacity .25s ease; }.flow-group.muted { opacity: .12; }.flow-group--remove .flow-line { animation-delay: -.8s; }.flow-group--modify .flow-line { animation-delay: -1.4s; }
.delta-stack { position: absolute; z-index: 8; top: 122px; left: 50%; display: grid; gap: 45px; transform: translateX(-50%); }.delta-stack span { display: grid; grid-template-columns: 35px 48px; align-items: center; border: 1px solid currentColor; color: #36efb8; background: rgba(3, 34, 72, .92); box-shadow: 0 0 18px color-mix(in srgb, currentColor 30%, transparent); clip-path: polygon(8px 0, calc(100% - 8px) 0, 100% 50%, calc(100% - 8px) 100%, 8px 100%, 0 50%); }.delta-stack small { padding-left: 9px; color: #8fbcd2; font-size: 7px; }.delta-stack b { padding: 5px 8px; color: #effdff; font-size: 15px; text-align: center; }.delta-stack .delta-remove { color: #ff7797; }.delta-stack .delta-modify { color: #ffc04a; }
.energy-tower { position: absolute; z-index: 7; top: 45px; display: flex; width: 235px; flex-direction: column; align-items: center; border: 0; color: #39dfff; background: transparent; cursor: pointer; transition: transform .28s ease, filter .28s ease; }.energy-tower:hover, .energy-tower.active { filter: brightness(1.23); transform: translateY(-7px); }.tower-left { left: 3%; }.tower-right { right: 3%; }
.tower-date { position: absolute; z-index: 8; top: -32px; display: flex; flex-direction: column; align-items: center; }.tower-date small { color: #4bccea; font-size: 7px; letter-spacing: .15em; }.tower-date b { color: #effdff; font-size: 17px; text-shadow: 0 0 10px #32cfff; }
.tower-cap { position: relative; z-index: 4; width: 158px; height: 48px; border: 2px solid currentColor; border-radius: 50%; background: rgba(4, 39, 88, .82); box-shadow: 0 0 22px currentColor, inset 0 0 18px rgba(50, 216, 255, .4); transform: translateY(18px); }.tower-cap::before, .tower-cap::after, .tower-cap i, .tower-cap b { position: absolute; inset: 7px 14px; border: 1px solid currentColor; border-radius: 50%; content: ''; }.tower-cap::after { inset: 13px 32px; }.tower-cap i { inset: -8px -16px; border-style: dashed; animation: spin 9s linear infinite; }.tower-cap b { inset: 18px 51px; background: currentColor; box-shadow: 0 0 13px currentColor; }
.tower-glass { position: relative; z-index: 3; display: flex; width: 150px; height: 300px; flex-direction: column; align-items: center; justify-content: center; gap: 9px; border-right: 2px solid rgba(69, 221, 255, .8); border-left: 2px solid rgba(69, 221, 255, .8); background: linear-gradient(90deg, rgba(23, 147, 255, .06), rgba(40, 194, 255, .22) 48%, rgba(23, 147, 255, .06)); box-shadow: inset 18px 0 25px rgba(20, 138, 255, .12), inset -18px 0 25px rgba(20, 138, 255, .12), 0 0 25px rgba(29, 189, 255, .35); clip-path: polygon(4% 0, 96% 0, 88% 100%, 12% 100%); }.tower-glass::before, .tower-glass::after { position: absolute; inset: 0 18px; border-right: 1px solid rgba(99, 233, 255, .38); border-left: 1px solid rgba(99, 233, 255, .38); content: ''; }.tower-glass::after { inset: 0 36px; opacity: .48; }
.glass-grid { position: absolute; inset: 0; opacity: .42; background: repeating-linear-gradient(0deg, transparent 0 24px, rgba(72, 204, 255, .16) 25px 26px); }.glass-scan { position: absolute; z-index: 1; right: 0; left: 0; height: 4px; background: #72efff; box-shadow: 0 0 18px #48ddff; animation: scanTower 3.6s ease-in-out infinite; }.glass-beam { position: absolute; top: 0; bottom: 0; width: 35px; background: linear-gradient(90deg, transparent, rgba(89, 226, 255, .5), transparent); filter: blur(5px); animation: beamPulse 2.8s ease-in-out infinite; }
.tower-stat { position: relative; z-index: 4; display: grid; grid-template-columns: 21px 43px 32px; align-items: center; border: 1px solid rgba(65, 226, 255, .24); padding: 6px 7px; background: rgba(2, 34, 73, .72); }.tower-stat > i { color: #37efb7; font-size: 16px; font-style: normal; font-weight: 900; }.tower-stat small { color: #9cc9dc; font-size: 10px; }.tower-stat b { color: #effdff; font-size: 22px; }.stat-remove > i { color: #ff7898; }.stat-modify > i { color: #ffc04a; }
.tower-base { position: relative; z-index: 5; width: 218px; height: 64px; margin-top: -21px; border: 3px solid currentColor; border-radius: 50%; background: rgba(3, 31, 73, .94); box-shadow: 0 0 25px currentColor, inset 0 0 22px rgba(41, 211, 255, .55); transform: perspective(300px) rotateX(64deg); }.tower-base::before, .tower-base::after, .tower-base i, .tower-base b, .tower-base em { position: absolute; border: 1px solid currentColor; border-radius: 50%; content: ''; }.tower-base::before { inset: 8px 15px; }.tower-base::after { inset: 17px 35px; }.tower-base i { inset: -13px -18px; border-style: dashed; animation: spin 12s linear infinite reverse; }.tower-base b { inset: 23px 58px; background: rgba(48, 211, 255, .34); box-shadow: inset 0 0 11px currentColor; }.tower-base em { inset: 30px 84px; background: currentColor; box-shadow: 0 0 18px currentColor; }
.tower-total { margin-top: -6px; color: #5acfe9; font-size: 8px; letter-spacing: .14em; }.tower-total b { color: #effdff; font-size: 15px; }
.time-scale { position: absolute; z-index: 10; right: 12%; bottom: 1px; left: 12%; display: flex; justify-content: space-between; }.time-scale > i { position: absolute; top: 7px; right: 0; left: 0; height: 1px; background: linear-gradient(90deg, transparent, #36cbff, transparent); }.time-scale button { z-index: 2; display: flex; align-items: center; gap: 6px; border: 0; color: #75a9c5; font-size: 9px; background: transparent; cursor: pointer; }.time-scale button span { width: 9px; height: 9px; border: 2px solid #37dfff; border-radius: 50%; background: #04275c; box-shadow: 0 0 8px #2bd7ff; }.time-scale button.active { color: #e4faff; }
.selected-event { position: relative; z-index: 9; display: grid; grid-template-columns: 44px minmax(0, 1fr) auto 66px; align-items: center; gap: 11px; min-height: 82px; border: 1px solid rgba(57, 198, 255, .3); padding: 10px 13px; background: linear-gradient(90deg, rgba(7, 71, 133, .66), rgba(3, 32, 76, .74)); }.selected-icon { display: grid; place-items: center; width: 42px; height: 42px; border: 1px solid #43dfff; border-radius: 50%; color: #76eeff; font-weight: 900; background: rgba(12, 103, 176, .35); box-shadow: 0 0 15px rgba(39, 210, 255, .38); }.selected-event small { color: #48dfff; font-size: 7px; letter-spacing: .13em; }.selected-event div b { display: block; color: #effdff; font-size: 12px; }.selected-event p { margin: 3px 0 0; color: #8dbbd3; font-size: 9px; }.selected-tags { display: flex; gap: 5px; }.selected-tags i { padding: 3px 6px; font-size: 8px; font-style: normal; }.selected-event > strong { color: #41e7ff; font-size: 25px; text-align: center; }.selected-event > strong small { font-size: 10px; }
.tag-add { border: 1px solid rgba(49, 235, 177, .4); color: #63f5c7; background: rgba(25, 137, 106, .2); }.tag-remove { border: 1px solid rgba(255, 106, 143, .4); color: #ff99b0; background: rgba(150, 32, 67, .2); }.tag-modify { border: 1px solid rgba(255, 189, 62, .4); color: #ffd078; background: rgba(149, 92, 15, .2); }
.analysis-deck { position: relative; z-index: 9; display: grid; grid-template-columns: 1.8fr repeat(4, 1fr); margin-top: 10px; border: 1px solid rgba(56, 191, 255, .28); background: rgba(3, 30, 70, .72); }.analysis-copy { display: flex; align-items: center; gap: 10px; padding: 10px; border-right: 1px solid rgba(59, 191, 247, .2); }.analysis-radar { display: grid; width: 44px; height: 44px; flex: 0 0 auto; place-items: center; border: 1px solid #34dfff; border-radius: 50%; background: repeating-radial-gradient(circle, transparent 0 7px, rgba(53, 216, 255, .3) 8px 9px); }.analysis-radar i { width: 2px; height: 22px; background: #61eaff; transform-origin: bottom; animation: radar 2.4s linear infinite; }.analysis-copy p { margin: 0; color: #87b2cb; font-size: 9px; line-height: 1.5; }.analysis-copy p b { display: block; color: #dff8ff; font-size: 11px; }.analysis-cell { display: flex; flex-direction: column; justify-content: center; border-right: 1px solid rgba(59, 191, 247, .16); padding: 10px; }.analysis-cell small, .analysis-cell em { color: #7faac3; font-size: 8px; font-style: normal; }.analysis-cell b { color: #effdff; font-size: 22px; }.tone-add b { color: #34efb7; }.tone-remove b { color: #ff7898; }.tone-modify b { color: #ffc04a; }
.event-console { display: flex; min-height: 0; flex-direction: column; padding: 15px; }.console-head { display: flex; align-items: center; justify-content: space-between; }.console-head small { color: #3cddff; font-size: 8px; letter-spacing: .15em; }.console-head h3 { margin: 2px 0 0; color: #effcff; font-size: 16px; }.console-head button { border: 1px solid rgba(66, 193, 250, .34); padding: 5px 8px; color: #b5dcec; font-size: 9px; background: rgba(4, 42, 89, .7); cursor: pointer; }.console-filter { display: flex; align-items: center; gap: 5px; margin: 12px 0; border-bottom: 1px solid rgba(61, 186, 239, .2); padding-bottom: 8px; }.console-filter button { border: 1px solid transparent; padding: 4px 8px; color: #76a8c3; font-size: 9px; background: transparent; cursor: pointer; }.console-filter button.active { border-color: #32d9ff; color: #ddfaff; background: rgba(18, 114, 175, .23); }.console-filter span { margin-left: auto; color: #3bcfff; font-size: 8px; letter-spacing: .1em; }
.event-list { display: flex; min-height: 0; flex: 1; flex-direction: column; gap: 9px; overflow-y: auto; padding-right: 3px; }.event-card { display: flex; gap: 9px; border: 1px solid rgba(52, 172, 232, .2); padding: 10px; color: inherit; text-align: left; background: linear-gradient(135deg, rgba(4, 29, 58, .86), rgba(0, 8, 22, .9)); cursor: pointer; transition: transform .55s cubic-bezier(.32,.72,0,1), border-color .55s cubic-bezier(.32,.72,0,1), box-shadow .55s cubic-bezier(.32,.72,0,1); }.event-card:hover, .event-card.active { border-color: #73eaff; box-shadow: inset 0 0 24px rgba(27, 190, 255, .08), 0 0 18px rgba(27, 190, 255, .1); transform: translateX(-5px); }.event-icon { display: grid; width: 39px; height: 39px; flex: 0 0 auto; place-items: center; border: 1px solid rgba(113, 231, 255, .58); border-radius: 0; color: #a4f3ff; font-size: 11px; font-weight: 900; background: linear-gradient(145deg, rgba(15, 91, 137, .3), rgba(0, 8, 18, .8)); box-shadow: inset 0 0 12px rgba(51, 202, 255, .1); clip-path: polygon(50% 0, 100% 50%, 50% 100%, 0 50%); }.event-body { min-width: 0; flex: 1; }.event-title { display: flex; align-items: center; gap: 6px; }.event-title b { overflow: hidden; color: #effcff; font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }.event-title i { border: 1px solid rgba(65, 196, 250, .28); border-radius: 0; padding: 2px 5px; color: #8fd8ef; font-size: 7px; font-style: normal; }.event-title time { margin-left: auto; color: #75a2bc; font-size: 7px; }.event-card p { margin: 5px 0; color: #8fb7cd; font-size: 8px; line-height: 1.45; }.event-tags { display: flex; flex-wrap: wrap; gap: 4px; }.event-tags i { padding: 2px 4px; font-size: 7px; font-style: normal; }.confidence { display: flex; align-items: center; gap: 7px; margin-top: 6px; color: #4fcae8; }.confidence small { width: 63px; font-size: 7px; }.confidence > i { height: 2px; flex: 1; overflow: hidden; background: rgba(48, 125, 174, .2); }.confidence > i b { display: block; height: 100%; background: linear-gradient(90deg, #1e9cff, #a3f8ff); box-shadow: 0 0 7px #2bdcff; }.empty-log { display: grid; flex: 1; place-items: center; color: #739cb4; font-size: 11px; }.expand-events { border: 0; padding: 10px 0 0; color: #40dcff; font-size: 9px; font-weight: 800; background: transparent; cursor: pointer; }.expand-events span { margin-left: 5px; }

/* Cinematic industrial material pass */
.timeline-workbench { background: radial-gradient(circle at 50% 42%, rgba(0, 105, 178, .085), transparent 31%), linear-gradient(180deg, rgba(0, 5, 15, .2), rgba(0, 3, 10, .58)); }
.metric-module { border-color: rgba(93, 210, 255, .22); background: linear-gradient(145deg, rgba(5, 22, 43, .96), rgba(0, 7, 19, .98)); box-shadow: inset 0 1px rgba(207, 247, 255, .07), inset 0 -18px 32px rgba(0, 0, 0, .22); }
.metric-cube { width: 62px; height: 62px; border-color: rgba(126, 232, 255, .66); color: #b2f5ff; background: radial-gradient(circle at 42% 32%, rgba(112, 229, 255, .24), rgba(4, 27, 50, .78) 48%, #01050b 76%); box-shadow: inset 0 0 20px rgba(38, 210, 255, .11), 0 0 12px rgba(41, 205, 255, .1); }
.timeline-command { background: radial-gradient(ellipse at 50% 71%, rgba(0, 108, 188, .14), transparent 42%), linear-gradient(180deg, #020b16, #00050c 68%, #010814); }
.event-console { background: linear-gradient(160deg, rgba(3, 18, 35, .99), rgba(0, 5, 15, .99)); }
.energy-stage::after { height: 176px; border-color: rgba(72, 191, 255, .17); background: repeating-radial-gradient(ellipse, transparent 0 21px, rgba(31, 147, 230, .1) 22px 23px), repeating-linear-gradient(90deg, transparent 0 52px, rgba(47, 158, 223, .075) 53px 54px), linear-gradient(180deg, transparent, rgba(1, 42, 77, .2)); box-shadow: 0 0 54px rgba(22, 127, 218, .11), inset 0 -22px 42px rgba(0, 0, 0, .5); }
.flow-haze { stroke-width: 26; opacity: .13; filter: blur(11px); }.flow-line { stroke-width: 2.2; stroke-dasharray: 3 7; }
.tower-cap { border-color: rgba(162, 245, 255, .82); background: repeating-radial-gradient(ellipse, #020910 0 7px, #0b2635 8px 10px, #02070c 11px 15px); box-shadow: 0 0 18px rgba(72, 220, 255, .55), inset 0 -9px 18px #000, inset 0 0 13px rgba(84, 229, 255, .24); }
.tower-glass { width: 158px; border-color: rgba(148, 239, 255, .64); background: linear-gradient(90deg, rgba(255,255,255,.02), rgba(44, 173, 226, .08) 18%, rgba(170, 244, 255, .22) 49%, rgba(44, 173, 226, .08) 81%, rgba(255,255,255,.02)), linear-gradient(180deg, rgba(67, 211, 255, .08), rgba(2, 26, 47, .22)); box-shadow: inset 18px 0 31px rgba(21, 129, 193, .08), inset -18px 0 31px rgba(21, 129, 193, .08), 0 0 17px rgba(29, 189, 255, .22); }
.tower-glass::before { border-color: rgba(207, 250, 255, .24); }.tower-glass::after { border-color: rgba(121, 225, 255, .17); }
.glass-grid { opacity: .28; background: repeating-linear-gradient(0deg, transparent 0 23px, rgba(157, 236, 255, .12) 24px 25px), repeating-linear-gradient(90deg, transparent 0 29px, rgba(157, 236, 255, .065) 30px 31px); }
.tower-stat { border-color: rgba(136, 229, 255, .13); background: linear-gradient(90deg, rgba(0, 8, 17, .6), rgba(3, 38, 65, .72), rgba(0, 8, 17, .6)); }
.tower-base { width: 232px; height: 72px; border-color: rgba(157, 241, 255, .78); background: repeating-radial-gradient(ellipse, #010408 0 8px, #10202a 9px 12px, #020609 13px 17px); box-shadow: 0 0 20px rgba(52, 218, 255, .52), inset 0 -13px 24px #000, inset 0 0 16px rgba(96, 229, 255, .24); }
.selected-event, .analysis-deck { background: linear-gradient(90deg, rgba(3, 25, 45, .92), rgba(0, 7, 18, .94)); border-color: rgba(72, 196, 244, .2); }
.flow-band, .flow-filament { fill: none; stroke-linecap: round; pointer-events: none; }
.flow-band { stroke-width: 12; opacity: .17; filter: url(#flowGlow); }
.flow-filament { stroke-width: 1.1; opacity: .42; stroke-dasharray: 2 11; animation: flowDash 4.8s cubic-bezier(.32,.72,0,1) infinite; }
.flow-line { stroke-width: 3.2; stroke-dasharray: 2 8; opacity: .92; }
.flow-haze { stroke-width: 34; opacity: .13; filter: blur(14px); }
.energy-streams { height: 438px; }
.energy-tower { width: 260px; }
.tower-left { left: 1.5%; }.tower-right { right: 1.5%; }
.tower-cap { width: 184px; height: 56px; }
.tower-glass { width: 176px; height: 318px; background: linear-gradient(90deg, rgba(255,255,255,.015), rgba(33, 142, 194, .055) 16%, rgba(196, 249, 255, .2) 48%, rgba(33, 142, 194, .055) 84%, rgba(255,255,255,.015)), linear-gradient(180deg, rgba(100, 229, 255, .07), rgba(0, 19, 35, .3)); box-shadow: inset 24px 0 38px rgba(11, 90, 139, .08), inset -24px 0 38px rgba(11, 90, 139, .08), 0 0 18px rgba(45, 207, 255, .19); }
.glass-reflection { position: absolute; z-index: 2; top: 0; bottom: 0; width: 10px; background: linear-gradient(180deg, transparent, rgba(219, 252, 255, .34) 25%, rgba(95, 223, 255, .08) 70%, transparent); filter: blur(.3px); transform: skewX(-6deg); }.reflection-a { left: 24px; opacity: .7; }.reflection-b { right: 33px; width: 4px; opacity: .42; }
.tower-stat { width: 122px; grid-template-columns: 20px 1fr 30px; border-color: rgba(142, 231, 255, .1); background: linear-gradient(90deg, transparent, rgba(3, 37, 62, .72), transparent); }
.tower-base { width: 248px; height: 78px; margin-top: -24px; }
.tower-plinth { position: relative; z-index: 4; width: 198px; height: 28px; margin-top: -25px; border: 1px solid rgba(121, 230, 255, .48); border-radius: 50%; background: linear-gradient(180deg, #152a34, #02070b 62%); box-shadow: inset 0 5px 10px rgba(148, 238, 255, .12), 0 9px 16px rgba(0, 0, 0, .65); transform: perspective(250px) rotateX(62deg); }.tower-plinth::before, .tower-plinth::after, .tower-plinth i { position: absolute; border-radius: 50%; content: ''; }.tower-plinth::before { inset: 5px 15px; border: 1px solid rgba(135, 232, 255, .25); }.tower-plinth::after { inset: 10px 34px; background: #010408; box-shadow: inset 0 0 8px #000; }.tower-plinth i { inset: -5px -18px; border: 1px dashed rgba(85, 215, 255, .24); animation: spin 16s cubic-bezier(.45,.05,.55,.95) infinite; }
.delta-stack span { min-width: 94px; grid-template-columns: 42px 1fr; border-color: color-mix(in srgb, currentColor 62%, #fff); background: linear-gradient(180deg, rgba(7, 29, 45, .96), rgba(0, 7, 16, .96)); box-shadow: inset 0 1px rgba(255,255,255,.08), 0 0 12px color-mix(in srgb, currentColor 16%, transparent); }
.metric-module { transition: transform .65s cubic-bezier(.32,.72,0,1), border-color .65s cubic-bezier(.32,.72,0,1), box-shadow .65s cubic-bezier(.32,.72,0,1); }
@keyframes metricScan { from { transform: translateX(-100%); } to { transform: translateX(100%); } }
@keyframes drift { 50% { opacity: .25; transform: translate(12px, -18px) scale(.6); } }
@keyframes pulse { 50% { opacity: .35; transform: scale(.7); } }
@keyframes flowDash { to { stroke-dashoffset: -46; } }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes scanTower { 0%, 100% { top: 8%; opacity: .2; } 50% { top: 88%; opacity: 1; } }
@keyframes beamPulse { 50% { opacity: .35; transform: scaleX(1.5); } }
@keyframes radar { to { transform: rotate(360deg); } }
@media (max-width: 1200px) { .timeline-grid { grid-template-columns: 1fr; }.event-console { max-height: 520px; }.metric-deck { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 760px) { .metric-deck { grid-template-columns: 1fr; }.timeline-command { overflow-x: auto; }.energy-stage { min-width: 720px; }.selected-event { grid-template-columns: 44px 1fr; }.selected-tags, .selected-event > strong { display: none; }.analysis-deck { grid-template-columns: 1fr 1fr; }.analysis-copy { grid-column: 1 / -1; }.command-head { min-width: 700px; } }
</style>

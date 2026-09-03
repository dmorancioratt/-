<template>
  <section class="timeline-dashboard">
    <div class="summary-row">
      <article v-for="item in summaryCards" :key="item.label" class="summary-card" :class="item.tone">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
        <small>{{ item.hint }}</small>
      </article>
    </div>

    <div class="evolution-workspace">
      <article class="timeline-panel">
        <header>
          <div><small>EVOLUTION TREND</small><h2>岗位能力迭代趋势</h2></div>
          <span>{{ rows.length }} 个时间窗口</span>
        </header>
        <EChart v-if="rows.length" :option="trendOption" class="trend-chart" />
        <div v-else class="empty-state">数据库中暂无能力演化记录</div>
        <div v-if="rows.length" class="period-strip">
          <button v-for="row in rows" :key="row.date" type="button">
            <time>{{ row.date || '时间未知' }}</time>
            <span><i class="added"></i>{{ number(row.added) }}</span>
            <span><i class="modified"></i>{{ number(row.modified) }}</span>
            <span><i class="removed"></i>{{ number(row.removed) }}</span>
          </button>
        </div>
      </article>

      <article class="events-panel">
        <header>
          <div><small>EVIDENCE EVENTS</small><h2>最近演化证据</h2></div>
          <span>可追溯数据</span>
        </header>
        <div v-if="recentEvents.length" class="event-list">
          <div v-for="(event, index) in recentEvents" :key="event.id || `${event.jobId}-${event.date}-${index}`" class="event-card">
            <div class="event-head">
              <b>{{ event.jobName || event.job_name || event.job || '岗位能力画像' }}</b>
              <time>{{ event.createdAt || event.created_at || event.date || '时间未知' }}</time>
            </div>
            <p>{{ event.description || event.note || event.change || '暂无事件说明' }}</p>
            <div class="event-tags">
              <span class="added">+{{ event.added?.length || 0 }} 新增</span>
              <span class="modified">{{ event.modified?.length || 0 }} 调整</span>
              <span class="removed">-{{ event.removed?.length || 0 }} 淘汰</span>
              <em>{{ Math.round(Number(event.confidence || 0) * 100) }}% 置信度</em>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">暂无可展示的演化证据</div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import EChart from '@/components/EChart.vue'

const props = defineProps<{ timeline?: { timeline?: any[]; events?: any[]; total?: number; derived?: boolean } }>()
const rows = computed(() => props.timeline?.timeline || [])
const events = computed(() => props.timeline?.events || [])
const recentEvents = computed(() => [...events.value].reverse().slice(0, 5))
const number = (value: unknown) => Number(value || 0).toLocaleString()
const totalFor = (key: string) => rows.value.reduce((sum, row) => sum + Number(row?.[key] || 0), 0)
const summaryCards = computed(() => [
  { label: '演化事件', value: number(props.timeline?.total ?? totalFor('events')), hint: `${rows.value.length} 个迭代周期`, tone: 'cyan' },
  { label: '新增能力', value: number(totalFor('added')), hint: '进入岗位能力模型', tone: 'green' },
  { label: '调整能力', value: number(totalFor('modified')), hint: '权重或定位发生变化', tone: 'gold' },
  { label: '淘汰能力', value: number(totalFor('removed')), hint: '退出当前能力模型', tone: 'red' }
])

const trendOption = computed(() => ({
  animationDuration: 800,
  color: ['#52ddff', '#ffc048', '#ff7088'],
  tooltip: { trigger: 'axis', backgroundColor: 'rgba(2, 18, 34, .94)', borderColor: 'rgba(82, 221, 255, .45)', textStyle: { color: '#e9fcff' } },
  legend: { top: 12, right: 22, data: ['新增能力', '调整能力', '淘汰能力'], textStyle: { color: '#8fb9cb', fontSize: 11 }, itemWidth: 18, itemHeight: 8 },
  grid: { left: 48, right: 26, top: 58, bottom: 42 },
  xAxis: { type: 'category', boundaryGap: false, data: rows.value.map((row) => row.date), axisLine: { lineStyle: { color: 'rgba(82, 221, 255, .22)' } }, axisLabel: { color: '#77a8ba' }, axisTick: { show: false } },
  yAxis: { type: 'value', minInterval: 1, axisLabel: { color: '#77a8ba' }, splitLine: { lineStyle: { color: 'rgba(82, 221, 255, .08)', type: 'dashed' } } },
  series: [
    { name: '新增能力', type: 'line', smooth: .35, symbol: 'circle', symbolSize: 8, data: rows.value.map((row) => Number(row.added || 0)), lineStyle: { width: 3 }, areaStyle: { color: 'rgba(82, 221, 255, .10)' } },
    { name: '调整能力', type: 'line', smooth: .35, symbol: 'diamond', symbolSize: 7, data: rows.value.map((row) => Number(row.modified || 0)), lineStyle: { width: 2 } },
    { name: '淘汰能力', type: 'line', smooth: .35, symbol: 'triangle', symbolSize: 7, data: rows.value.map((row) => Number(row.removed || 0)), lineStyle: { width: 2 } }
  ]
}))
</script>

<style scoped>
.timeline-dashboard { display: grid; gap: 14px; min-width: 0; color: #e5ffff; --edge: rgba(220, 242, 249, .12); --muted: #78a9bc; --text: #e8fbff; }
.summary-row { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.summary-card, .timeline-panel, .events-panel { border: 1px solid var(--edge); background: linear-gradient(145deg, rgba(28, 54, 71, .44), rgba(7, 23, 40, .28)); box-shadow: inset 0 1px 0 rgba(241, 251, 255, .075), 0 18px 46px rgba(0, 3, 14, .22); backdrop-filter: blur(26px) saturate(1.10); -webkit-backdrop-filter: blur(26px) saturate(1.10); }
.summary-card { border-radius: 16px; }
.timeline-panel, .events-panel { border-radius: 18px; }
.summary-card { position: relative; display: grid; grid-template-columns: 1fr auto; align-items: center; min-height: 94px; overflow: hidden; padding: 16px 18px; }
.summary-card::before { position: absolute; inset: 0 auto 0 0; width: 3px; background: #52ddff; content: ''; box-shadow: 0 0 12px #52ddff; }
.summary-card.gold::before { background: #ffc048; }.summary-card.red::before { background: #ff7088; }
.summary-card span { color: var(--muted); font-size: 12px; font-weight: 750; }
.summary-card strong { grid-row: 1 / span 2; grid-column: 2; color: var(--text); font: 900 32px/1 Consolas, monospace; text-shadow: 0 0 12px rgba(82, 221, 255, .28); }
.summary-card small { margin-top: 7px; color: #537f92; font-size: 10px; }
.evolution-workspace { display: grid; grid-template-columns: minmax(0, 1.65fr) minmax(340px, .75fr); gap: 14px; min-width: 0; }
.timeline-panel, .events-panel { min-width: 0; overflow: hidden; }
header { display: flex; align-items: center; justify-content: space-between; gap: 16px; border-bottom: 1px solid rgba(82, 221, 255, .10); padding: 16px 18px; }
header small { color: #52ddff; font: 800 9px Consolas, monospace; letter-spacing: .16em; }
header h2 { margin: 5px 0 0; color: var(--text); font-size: 17px; }
header > span { color: var(--muted); font-size: 11px; }
.trend-chart { width: 100%; height: 370px; }
.period-strip { display: grid; grid-template-columns: repeat(auto-fit, minmax(112px, 1fr)); border-top: 1px solid rgba(82, 221, 255, .09); padding: 10px; gap: 7px; }
.period-strip button { display: grid; grid-template-columns: 1fr repeat(3, auto); align-items: center; gap: 6px; min-width: 0; border: 1px solid rgba(220, 242, 249, .09); border-radius: 10px; padding: 8px; color: #8eb9ca; background: rgba(231, 247, 252, .035); }
.period-strip time { grid-column: 1 / -1; color: #c8eef5; font: 700 10px Consolas, monospace; }
.period-strip span { display: flex; align-items: center; gap: 3px; font-size: 9px; }.period-strip i { width: 5px; height: 5px; border-radius: 50%; background: currentColor; }
.event-list { display: grid; gap: 0; }
.event-card { min-width: 0; border-bottom: 1px solid rgba(82, 221, 255, .08); padding: 14px 16px; background: rgba(4, 31, 46, .22); }
.event-card:last-child { border-bottom: 0; }.event-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.event-head b { min-width: 0; overflow: hidden; color: var(--text); font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }.event-head time { flex: 0 0 auto; color: #6591a4; font: 700 9px Consolas, monospace; }
.event-card p { display: -webkit-box; min-height: 36px; margin: 7px 0 9px; overflow: hidden; color: #91b8c7; font-size: 11px; line-height: 1.6; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.event-tags { display: flex; align-items: center; flex-wrap: wrap; gap: 5px; }.event-tags span { border-radius: 4px; padding: 3px 6px; font-size: 9px; background: rgba(255, 255, 255, .035); }.event-tags em { margin-left: auto; color: #6f9caf; font-size: 9px; font-style: normal; }
.added { color: #52ddff; }.modified { color: #ffc048; }.removed { color: #ff7088; }.empty-state { display: grid; min-height: 300px; place-items: center; color: var(--muted); font-size: 12px; }
@media (max-width: 1100px) { .evolution-workspace { grid-template-columns: 1fr; } }
@media (max-width: 760px) { .summary-row { grid-template-columns: 1fr 1fr; }.summary-card { min-height: 82px; }.trend-chart { height: 320px; } }
</style>

<template>
  <section class="timeline-dashboard">
    <div class="summary-row">
      <article v-for="item in summaryCards" :key="item.label" class="summary-card">
        <strong>{{ item.value }}</strong>
        <span>{{ item.label }}</span>
      </article>
    </div>

    <article class="timeline-panel">
      <header>
        <div>
          <small>EVOLUTION RECORDS</small>
          <h2>岗位能力演化时间线</h2>
        </div>
        <span>{{ rows.length }} 个时间窗口</span>
      </header>
      <div v-if="rows.length" class="timeline-list">
        <div v-for="row in rows" :key="row.date" class="timeline-item">
          <time>{{ row.date || '时间未知' }}</time>
          <div class="event-counts">
            <span class="added">新增 {{ number(row.added) }}</span>
            <span class="modified">调整 {{ number(row.modified) }}</span>
            <span class="removed">淘汰 {{ number(row.removed) }}</span>
          </div>
          <strong>{{ number(row.events) }} 个演化事件</strong>
        </div>
      </div>
      <div v-else class="empty-state">数据库中暂无能力演化记录</div>
    </article>

    <article class="events-panel">
      <header>
        <div>
          <small>EVIDENCE EVENTS</small>
          <h2>最近演化证据</h2>
        </div>
      </header>
      <div v-if="events.length" class="event-grid">
        <div v-for="(event, index) in events" :key="event.id || index" class="event-card">
          <b>{{ event.job_name || event.job || '未命名岗位' }}</b>
          <p>{{ event.description || event.note || event.change || '暂无事件说明' }}</p>
          <time>{{ event.created_at || event.date || '时间未知' }}</time>
        </div>
      </div>
      <div v-else class="empty-state">暂无可展示的演化证据</div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ timeline?: { timeline?: any[]; events?: any[]; total?: number } }>()
const rows = computed(() => props.timeline?.timeline || [])
const events = computed(() => props.timeline?.events || [])
const number = (value: unknown) => Number(value || 0).toLocaleString()
const totalFor = (key: string) => rows.value.reduce((sum, row) => sum + Number(row?.[key] || 0), 0)
const summaryCards = computed(() => [
  { label: '演化事件', value: number(props.timeline?.total ?? totalFor('events')) },
  { label: '新增能力', value: number(totalFor('added')) },
  { label: '调整能力', value: number(totalFor('modified')) },
  { label: '淘汰能力', value: number(totalFor('removed')) }
])
</script>

<style scoped>
.timeline-dashboard { display: grid; gap: 16px; color: #eaf9ff; }
.summary-row { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.summary-card,.timeline-panel,.events-panel { border: 1px solid rgba(79, 196, 255, .27); border-radius: 8px; background: linear-gradient(145deg, rgba(4, 32, 72, .82), rgba(2, 17, 45, .88)); box-shadow: inset 0 1px rgba(150, 231, 255, .06); }
.summary-card { min-height: 94px; display: grid; place-content: center; text-align: center; }
.summary-card strong { color: #6be7ff; font: 800 30px/1.1 Consolas, monospace; }
.summary-card span { margin-top: 8px; color: #83a8c5; font-size: 12px; }
header { display: flex; align-items: center; justify-content: space-between; gap: 16px; border-bottom: 1px solid rgba(74, 171, 229, .18); padding: 18px 20px; }
header small { color: #48d7ff; font: 700 9px Consolas, monospace; letter-spacing: 1.5px; }
header h2 { margin: 5px 0 0; font-size: 17px; letter-spacing: 0; }
header > span { color: #7da4c2; font-size: 11px; }
.timeline-list { padding: 8px 20px 18px; }
.timeline-item { display: grid; grid-template-columns: 130px 1fr auto; align-items: center; gap: 18px; border-bottom: 1px solid rgba(68, 153, 211, .14); padding: 15px 0; }
.timeline-item time,.event-card time { color: #7699b7; font: 11px Consolas, monospace; }
.timeline-item > strong { color: #dff8ff; font-size: 12px; }
.event-counts { display: flex; flex-wrap: wrap; gap: 7px; }
.event-counts span { border-radius: 4px; padding: 4px 7px; font-size: 10px; }
.added { color: #64edca; background: rgba(30, 181, 137, .13); }.modified { color: #ffd274; background: rgba(213, 151, 39, .13); }.removed { color: #ff91a5; background: rgba(219, 61, 91, .13); }
.event-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; padding: 16px 20px 20px; }
.event-card { border: 1px solid rgba(65, 171, 235, .18); border-radius: 6px; padding: 14px; background: rgba(6, 42, 88, .35); }
.event-card b { font-size: 13px; }.event-card p { min-height: 36px; margin: 8px 0 12px; color: #8db0ca; font-size: 11px; line-height: 1.6; }
.empty-state { display: grid; min-height: 170px; place-items: center; color: #789bb6; font-size: 12px; }
@media (max-width: 760px) { .summary-row { grid-template-columns: 1fr 1fr; }.timeline-item { grid-template-columns: 1fr; gap: 7px; }.event-grid { grid-template-columns: 1fr; } }
</style>

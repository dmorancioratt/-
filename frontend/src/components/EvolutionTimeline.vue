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
/* ===== 荧光青玻璃态（与 SkillGraph / 概览页顶部一致） ===== */
.timeline-dashboard {
  display: grid;
  gap: 16px;
  color: #e5ffff;
  --panel: rgba(3, 28, 36, .28);
  --edge: rgba(34, 247, 255, .11);
  --cyan: #22f7ff;
  --teal: #00c9d2;
  --muted: #78a4a9;
  --text: #e5ffff;
}

.summary-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.summary-card,
.timeline-panel,
.events-panel {
  border: 1px solid var(--edge);
  border-radius: 20px;
  background: linear-gradient(145deg, rgba(4, 46, 54, .26), rgba(2, 20, 24, .30));
  box-shadow: 0 24px 62px rgba(0, 10, 14, .16), inset 0 1px 0 rgba(141, 255, 255, .025);
  backdrop-filter: blur(26px) saturate(1.18);
}

.summary-card {
  min-height: 96px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 10px;
  text-align: center;
  padding: 14px 16px;
  position: relative;
  overflow: hidden;
}

.summary-card::before {
  content: "";
  position: absolute;
  left: 50%;
  top: 0;
  transform: translateX(-50%);
  width: 34%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(34, 247, 255, 0.42), transparent);
}

.summary-card::after {
  content: "";
  position: absolute;
  left: 14px;
  right: 14px;
  bottom: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(34, 247, 255, 0.10), transparent);
}

.summary-card strong {
  color: var(--cyan);
  font: 800 34px/1.1 Consolas, monospace;
  text-shadow: 0 0 10px rgba(34, 247, 255, .30);
  letter-spacing: 0.02em;
}

.summary-card span {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
}

header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border-bottom: 1px solid rgba(34, 247, 255, .08);
  padding: 18px 22px;
}

header small {
  color: var(--cyan);
  font: 800 10px Consolas, monospace;
  letter-spacing: 0.20em;
  text-shadow: 0 0 8px rgba(34, 247, 255, .28);
}

header h2 {
  margin: 6px 0 0;
  font-size: 18px;
  font-weight: 900;
  letter-spacing: 0.01em;
  color: var(--text);
}

header > span {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
}

.timeline-list {
  padding: 10px 22px 22px;
}

.timeline-item {
  display: grid;
  grid-template-columns: 140px 1fr auto;
  align-items: center;
  gap: 18px;
  border-bottom: 1px solid rgba(34, 247, 255, .07);
  padding: 16px 2px;
}

.timeline-item:last-child {
  border-bottom: none;
}

.timeline-item time,
.event-card time {
  color: var(--muted);
  font: 700 12px Consolas, monospace;
}

.timeline-item > strong {
  color: var(--text);
  font-size: 13px;
  font-weight: 850;
}

.event-counts {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.event-counts span {
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 800;
  border: 1px solid transparent;
}

.added {
  color: #8fe7c8;
  border-color: rgba(154, 216, 197, 0.22);
  background: rgba(24, 70, 56, .14);
}

.modified {
  color: #ffd18a;
  border-color: rgba(255, 192, 72, 0.22);
  background: rgba(80, 58, 10, .14);
}

.removed {
  color: #ff9eb0;
  border-color: rgba(255, 93, 125, 0.22);
  background: rgba(80, 20, 34, .14);
}

.event-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  padding: 20px 22px 24px;
}

.event-card {
  border: 1px solid rgba(34, 247, 255, .12);
  border-radius: 14px;
  padding: 14px 16px;
  background: linear-gradient(150deg, rgba(4, 46, 54, .20), rgba(2, 20, 24, .22));
  backdrop-filter: blur(18px) saturate(1.12);
  box-shadow: inset 0 1px 0 rgba(141, 255, 255, .02);
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: border-color .2s ease, transform .2s ease, box-shadow .2s ease;
}

.event-card:hover {
  border-color: rgba(34, 247, 255, .24);
  transform: translateY(-1px);
  box-shadow: 0 12px 30px rgba(0, 10, 14, .18), 0 0 18px rgba(34, 247, 255, .08);
}

.event-card b {
  font-size: 13px;
  font-weight: 850;
  color: var(--text);
}

.event-card p {
  min-height: 38px;
  margin: 0;
  color: #a4c6cb;
  font-size: 12px;
  line-height: 1.7;
}

.event-card time {
  margin-top: auto;
  align-self: flex-end;
  font-size: 11px;
}

.empty-state {
  display: grid;
  min-height: 190px;
  place-items: center;
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

@media (max-width: 960px) {
  .event-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 760px) {
  .summary-row { grid-template-columns: 1fr 1fr; }
  .timeline-item { grid-template-columns: 1fr; gap: 8px; }
  .event-grid { grid-template-columns: 1fr; }
}
</style>

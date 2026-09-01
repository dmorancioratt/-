<template>
  <div class="stage-log-card">
    <div class="card-header">
      <span class="card-title">
        <el-icon :size="14"><Connection /></el-icon> 运行链路
      </span>
      <span class="count-tag" v-if="store.runtime.logs.length">
        {{ store.runtime.logs.length }} 步
      </span>
    </div>

    <div v-if="store.runtime.logs.length === 0" class="empty-stage">
      尚未运行 · 点击右上「运行测试」查看检索→生成→校验链路
    </div>

    <div v-else class="stage-list">
      <div v-for="(s, i) in store.runtime.logs" :key="i" class="stage-item">
        <span class="stage-idx">{{ i + 1 }}</span>
        <div class="stage-main">
          <div class="stage-name">{{ s.stage }}</div>
          <div class="stage-out" :title="s.output">{{ s.output || '—' }}</div>
        </div>
        <span class="stage-status" :class="`s-${s.status}`">{{ s.status }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Connection } from '@element-plus/icons-vue'
import { useWorkflowStore } from '@/stores/workflow'

const store = useWorkflowStore()
</script>

<style scoped>
.stage-log-card {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(91, 155, 213, 0.12);
  background: rgba(15, 23, 42, 0.5);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #e2e8f0;
}
.card-title .el-icon {
  color: #a78bfa;
}

.count-tag {
  font-size: 11px;
  color: #64748b;
  font-family: ui-monospace, Menlo, monospace;
}

.empty-stage {
  font-size: 11px;
  color: #475569;
  line-height: 1.5;
  padding: 4px 0;
}

.stage-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 160px;
  overflow-y: auto;
}

.stage-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 6px 8px;
  background: rgba(30, 41, 59, 0.4);
  border: 1px solid rgba(91, 155, 213, 0.1);
  border-radius: 6px;
}

.stage-idx {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: rgba(167, 139, 250, 0.15);
  color: #a78bfa;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 1px;
}

.stage-main {
  flex: 1;
  min-width: 0;
}

.stage-name {
  font-size: 12px;
  color: #cbd5e1;
  font-weight: 500;
}

.stage-out {
  font-size: 10px;
  color: #64748b;
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stage-status {
  font-size: 10px;
  font-family: ui-monospace, Menlo, monospace;
  flex-shrink: 0;
  padding-top: 2px;
}
.stage-status.s-done { color: #34d399; }
.stage-status.s-error { color: #f43f5e; }
.stage-status.s-warn { color: #fbbf24; }
.stage-status.s-running { color: #93c5fd; }
</style>
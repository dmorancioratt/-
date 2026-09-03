<template>
  <div class="close-loop-bar">
    <span class="loop-title">
      <el-icon :size="13"><Aim /></el-icon> 数据闭环
    </span>

    <div class="loop-chain">
      <template v-for="(s, i) in STEPS" :key="s.key">
        <div class="loop-chip" :class="stepClass(s.key)" :title="stepMeta(s.key)" @click="onStepClick(s.key)">
          <span class="chip-dot">
            <el-icon v-if="stepStatus(s.key) === 'done'" :size="11"><Check /></el-icon>
            <el-icon v-else-if="stepStatus(s.key) === 'running'" :size="11" class="spin"><Loading /></el-icon>
            <span v-else>{{ i + 1 }}</span>
          </span>
          <span class="chip-label">{{ s.label }}</span>
          <span class="chip-meta" v-if="stepMeta(s.key)">{{ stepMeta(s.key) }}</span>
        </div>
        <el-icon v-if="i < STEPS.length - 1" :size="12" class="chip-arrow"><ArrowRight /></el-icon>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Aim, ArrowRight, Check, Loading } from '@element-plus/icons-vue'
import { useWorkflowStore } from '@/stores/workflow'

const store = useWorkflowStore()

const STEPS = [
  { key: 'upload', label: '上传' },
  { key: 'parse', label: '解析' },
  { key: 'embed', label: '向量化' },
  { key: 'retrieve', label: '检索' },
  { key: 'generate', label: '生成' },
  { key: 'citation', label: '引用校验' },
]

const RUNTIME_STAGE: Record<string, string> = {
  retrieve: '向量检索',
  generate: '大模型生成',
  citation: '引用校验',
}

function stepStatus(key: string): string {
  if (key === 'upload' || key === 'parse') return store.totalDocs > 0 ? 'done' : 'idle'
  if (key === 'embed') return store.totalChunks > 0 ? 'done' : 'idle'
  const log = store.runtime.logs.find((l) => l.stage === RUNTIME_STAGE[key])
  if (!log) return 'idle'
  if (log.status === 'running') return 'running'
  return log.status === 'done' || log.status === 'warn' ? 'done' : 'idle'
}

function stepMeta(key: string): string {
  if (key === 'upload') return store.totalDocs > 0 ? `${store.totalDocs} 文档` : ''
  if (key === 'parse') return ''
  if (key === 'embed') return store.totalChunks > 0 ? `${store.totalChunks} chunks` : ''
  return ''
}

function stepClass(key: string): Record<string, boolean> {
  return { [`s-${stepStatus(key)}`]: true }
}

function onStepClick(key: string) {
  if (key === 'upload' || key === 'parse' || key === 'embed') {
    const node = store.nodes.find((n) => n.data.kind === 'knowledge')
    if (node) store.openDrawer(node.id)
    return
  }
  store.openTestDialog()
}
</script>

<style scoped>
.close-loop-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.85), rgba(30, 41, 59, 0.65));
  border-bottom: 1px solid rgba(91, 155, 213, 0.14);
}

.loop-title {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 600;
  color: #cbd5e1;
  white-space: nowrap;
  flex-shrink: 0;
}
.loop-title .el-icon {
  color: #88ddff;
}

.loop-chain {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 4px;
  min-width: 0;
}

.loop-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px 3px 4px;
  border-radius: 999px;
  border: 1px solid rgba(91, 155, 213, 0.18);
  background: rgba(30, 41, 59, 0.5);
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.loop-chip:hover {
  border-color: rgba(96, 165, 250, 0.6);
}

.chip-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
  color: #64748b;
  background: #1e293b;
  flex-shrink: 0;
}

.chip-label {
  font-size: 12px;
  color: #94a3b8;
}

.chip-meta {
  font-size: 10px;
  color: #64748b;
  font-family: ui-monospace, Menlo, monospace;
}

.chip-arrow {
  color: #475569;
  flex-shrink: 0;
}

/* 状态 */
.loop-chip.s-done {
  border-color: rgba(70, 200, 255, 0.5);
  background: rgba(70, 200, 255, 0.12);
}
.loop-chip.s-done .chip-dot {
  color: #0b1220;
  background: #46c8ff;
}
.loop-chip.s-done .chip-label { color: #46c8ff; }
.loop-chip.s-done .chip-meta { color: #46c8ff; }

.loop-chip.s-running {
  border-color: rgba(96, 165, 250, 0.6);
  background: rgba(96, 165, 250, 0.14);
}
.loop-chip.s-running .chip-dot {
  color: #fff;
  background: #0aa9b4;
  box-shadow: 0 0 8px rgba(96, 165, 250, 0.8);
}
.loop-chip.s-running .chip-label { color: #a5fffc; }

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>

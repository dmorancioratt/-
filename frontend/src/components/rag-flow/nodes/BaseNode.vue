<template>
  <div
    class="rag-base-node"
    :class="[`tone-${data.kind}`, `status-${data.status}`, { selected: isSelected }]"
    @click="handleClick"
  >
    <Handle type="target" :position="Position.Left" class="rag-handle" />

    <div class="node-header">
      <div class="node-icon">
        <el-icon :size="14"><component :is="iconComponent" /></el-icon>
      </div>
      <div class="node-title-block">
        <div class="node-title">{{ data.label }}</div>
        <div class="node-kind">{{ data.kind }}</div>
      </div>
      <div class="node-status">
        <span class="status-dot" :title="data.status"></span>
      </div>
    </div>

    <div class="node-desc" v-if="data.description">{{ data.description }}</div>

    <div class="node-output" v-if="data.output">{{ data.output }}</div>

    <div class="node-config-preview" v-if="data.config && Object.keys(data.config).length > 0">
      <span v-for="(val, key) in data.config" :key="key" class="config-chip">
        {{ key }}: {{ typeof val === 'object' ? JSON.stringify(val) : val }}
      </span>
    </div>

    <Handle type="source" :position="Position.Right" class="rag-handle" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import {
  Aim,
  ChatLineRound,
  Check,
  Connection,
  Cpu,
  DataAnalysis,
  Document,
  Filter,
  Promotion,
  Search,
  Star,
  Tickets,
} from '@element-plus/icons-vue'
import type { FlowNodeData, NodeKind } from '@/types/workflow'

const props = defineProps<{
  id: string
  data: Omit<FlowNodeData, 'status'> & { status: string }
  selected?: boolean
}>()

const emit = defineEmits<{
  (e: 'node-click', id: string): void
}>()

const ICON_MAP: Record<NodeKind, any> = {
  input: ChatLineRound,
  parser: Aim,
  knowledge: Document,
  chunker: Tickets,
  embedding: Cpu,
  vector: Connection,
  retrieve: Search,
  relevance: Filter,
  llm: Promotion,
  guard: Check,
  citation: Star,
  output: DataAnalysis,
}

const iconComponent = computed(() => ICON_MAP[props.data.kind] || DataAnalysis)

const isSelected = computed(() => !!props.selected)

function handleClick() {
  emit('node-click', props.id)
}
</script>

<style scoped>
.rag-base-node {
  position: relative;
  min-width: 180px;
  max-width: 220px;
  padding: 10px 12px;
  border-radius: 10px;
  background: linear-gradient(160deg, rgba(91,155,213,0.12) 0%, rgba(91,155,213,0.04) 100%);
  border: 1px solid rgba(148,163,184,0.25);
  cursor: pointer;
  transition: all 0.18s ease;
  color: #e2e8f0;
}
.rag-base-node:hover {
  border-color: rgba(91,155,213,0.6);
  transform: translateY(-1px);
  box-shadow: 0 6px 16px -8px rgba(91,155,213,0.45);
}
.rag-base-node.selected {
  border-color: rgba(91,155,213,0.95);
  box-shadow: 0 0 0 2px rgba(91,155,213,0.35);
}

/* 节点状态颜色 */
.rag-base-node.status-idle { border-left: 3px solid rgba(148,163,184,0.5); }
.rag-base-node.status-running { border-left: 3px solid #fbbf24; animation: pulse-running 1.2s ease-in-out infinite; }
.rag-base-node.status-done { border-left: 3px solid #46c8ff; }
.rag-base-node.status-error { border-left: 3px solid #f43f5e; }
.rag-base-node.status-warn { border-left: 3px solid #fbbf24; }

@keyframes pulse-running {
  0%, 100% { box-shadow: 0 0 0 0 rgba(251,191,36,0.0); }
  50% { box-shadow: 0 0 0 6px rgba(251,191,36,0.18); }
}

.tone-knowledge { border-left-color: #ec4899; }
.tone-chunker { border-left-color: #f59e0b; }
.tone-embedding { border-left-color: #3b82f6; }
.tone-vector { border-left-color: #46c8ff; }
.tone-retrieve { border-left-color: #5B9BD5; }
.tone-relevance { border-left-color: #a78bfa; }
.tone-llm { border-left-color: #6366f1; }
.tone-guard { border-left-color: #258dff; }
.tone-citation { border-left-color: #fbbf24; }
.tone-output { border-left-color: #f43f5e; }

.node-header {
  display: flex;
  align-items: center;
  gap: 8px;
}
.node-icon {
  width: 26px; height: 26px;
  border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  background: rgba(91,155,213,0.16);
  color: #93c5fd;
  flex-shrink: 0;
}
.tone-knowledge .node-icon { background: rgba(236,72,153,0.18); color: #f9a8d4; }
.tone-chunker .node-icon { background: rgba(245,158,11,0.18); color: #fcd34d; }
.tone-embedding .node-icon { background: rgba(59,130,246,0.18); color: #93c5fd; }
.tone-vector .node-icon { background: rgba(70,200,255,0.18); color: #6ed8ff; }
.tone-retrieve .node-icon { background: rgba(91,155,213,0.18); color: #93c5fd; }
.tone-relevance .node-icon { background: rgba(167,139,250,0.18); color: #c4b5fd; }
.tone-llm .node-icon { background: rgba(99,102,241,0.18); color: #a5b4fc; }
.tone-guard .node-icon { background: rgba(37,141,255,0.18); color: #75b9ff; }
.tone-citation .node-icon { background: rgba(251,191,36,0.18); color: #fcd34d; }
.tone-output .node-icon { background: rgba(244,63,94,0.18); color: #fda4af; }

.node-title-block {
  flex: 1;
  min-width: 0;
}
.node-title {
  font-size: 13px;
  font-weight: 700;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.node-kind {
  font-size: 10px;
  color: #94a3b8;
  font-family: ui-monospace, Menlo, monospace;
  margin-top: 2px;
}
.node-status .status-dot {
  width: 8px; height: 8px;
  border-radius: 999px;
  display: inline-block;
  background: rgba(148,163,184,0.6);
}
.status-idle .status-dot { background: rgba(148,163,184,0.6); }
.status-running .status-dot { background: #fbbf24; animation: pulse-dot 1s ease-in-out infinite; }
.status-done .status-dot { background: #46c8ff; }
.status-error .status-dot { background: #f43f5e; }
.status-warn .status-dot { background: #fbbf24; }

@keyframes pulse-dot {
  0%, 100% { box-shadow: 0 0 0 0 rgba(251,191,36,0.6); }
  50% { box-shadow: 0 0 0 6px rgba(251,191,36,0); }
}

.node-desc {
  font-size: 11px;
  color: #94a3b8;
  line-height: 1.4;
  margin-top: 6px;
}

.node-output {
  margin-top: 8px;
  padding: 6px 8px;
  background: rgba(15,23,42,0.6);
  border: 1px solid rgba(91,155,213,0.18);
  border-radius: 6px;
  font-size: 10px;
  color: #cbd5e1;
  line-height: 1.45;
  max-height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.node-config-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 8px;
}

.config-chip {
  padding: 2px 6px;
  font-size: 10px;
  background: rgba(91,155,213,0.12);
  border: 1px solid rgba(91,155,213,0.2);
  border-radius: 4px;
  color: #93c5fd;
  font-family: ui-monospace, Menlo, monospace;
  line-height: 1.4;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* handle 样式 */
:deep(.rag-handle) {
  width: 8px !important;
  height: 8px !important;
  background: #7BC4E8 !important;
  border: 2px solid rgba(15,23,42,0.9) !important;
}
</style>

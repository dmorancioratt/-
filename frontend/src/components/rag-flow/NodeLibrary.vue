<template>
  <div class="node-library">
    <div class="library-header">
      <div class="header-tabs">
        <div class="tab active">节点库</div>
        <div class="tab">我的节点</div>
      </div>
    </div>

    <div class="library-body">
      <div class="section-title">基础节点</div>
      <div class="node-list">
        <div
          v-for="node in nodeList"
          :key="node.kind"
          class="node-item"
          :class="`item-${node.kind}`"
          draggable="true"
          @dragstart="onDragStart($event, node.kind)"
        >
          <div class="node-icon">
            <el-icon :size="16"><component :is="node.icon" /></el-icon>
          </div>
          <div class="node-info">
            <div class="node-name">{{ node.label }}</div>
            <div class="node-desc">{{ node.description }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="library-footer">
      <div class="tip-text">拖拽节点到画布，右键节点可配置</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { markRaw } from 'vue'
import type { NodeKind } from '@/types/workflow'
import { NODE_KIND_META } from '@/utils/workflowTemplate'
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

const nodeList = Object.entries(NODE_KIND_META).map(([kind, meta]) => ({
  kind: kind as NodeKind,
  label: meta.label,
  description: meta.description,
  icon: markRaw(ICON_MAP[kind as NodeKind]),
}))

function onDragStart(e: DragEvent, kind: NodeKind) {
  if (e.dataTransfer) {
    e.dataTransfer.setData('application/node-kind', kind)
    e.dataTransfer.effectAllowed = 'copy'
  }
}
</script>

<style scoped>
.node-library {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.library-header {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(91, 155, 213, 0.15);
}

.header-tabs {
  display: flex;
  gap: 16px;
}

.tab {
  font-size: 14px;
  color: #94a3b8;
  cursor: pointer;
  padding-bottom: 4px;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab.active {
  color: #60a5fa;
  border-bottom-color: #60a5fa;
  font-weight: 600;
}

.tab:hover {
  color: #cbd5e1;
}

.library-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.section-title {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.node-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.node-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(91, 155, 213, 0.1);
  border-radius: 8px;
  cursor: grab;
  transition: all 0.2s;
}

.node-item:hover {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.4);
  transform: translateX(2px);
}

.node-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: rgba(91, 155, 213, 0.15);
  color: #60a5fa;
}

.item-input .node-icon { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
.item-parser .node-icon { background: rgba(139, 92, 246, 0.15); color: #a78bfa; }
.item-knowledge .node-icon { background: rgba(236, 72, 153, 0.15); color: #f472b6; }
.item-chunker .node-icon { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
.item-embedding .node-icon { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
.item-vector .node-icon { background: rgba(20, 184, 166, 0.15); color: #2dd4bf; }
.item-retrieve .node-icon { background: rgba(91, 155, 213, 0.15); color: #60a5fa; }
.item-relevance .node-icon { background: rgba(167, 139, 250, 0.15); color: #a78bfa; }
.item-llm .node-icon { background: rgba(99, 102, 241, 0.15); color: #818cf8; }
.item-guard .node-icon { background: rgba(52, 211, 153, 0.15); color: #34d399; }
.item-citation .node-icon { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }
.item-output .node-icon { background: rgba(244, 63, 94, 0.15); color: #fb7185; }

.node-info {
  flex: 1;
  min-width: 0;
}

.node-name {
  font-size: 13px;
  font-weight: 500;
  color: #e2e8f0;
  margin-bottom: 2px;
}

.node-desc {
  font-size: 11px;
  color: #64748b;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.library-footer {
  padding: 10px 16px;
  border-top: 1px solid rgba(91, 155, 213, 0.1);
  background: rgba(15, 23, 42, 0.3);
}

.tip-text {
  font-size: 11px;
  color: #475569;
  text-align: center;
}

/* 自定义滚动条 */
.library-body::-webkit-scrollbar {
  width: 6px;
}

.library-body::-webkit-scrollbar-track {
  background: transparent;
}

.library-body::-webkit-scrollbar-thumb {
  background: rgba(91, 155, 213, 0.3);
  border-radius: 3px;
}

.library-body::-webkit-scrollbar-thumb:hover {
  background: rgba(91, 155, 213, 0.5);
}
</style>

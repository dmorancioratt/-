<template>
  <div class="rag-flow-canvas">
    <div class="phase-overlay">
      <div
        v-for="p in PHASE_HEADERS"
        :key="p.id"
        class="phase-chip"
        :class="[`tone-${p.tone}`]"
        :style="phaseStyle(p)"
      >
        <div class="phase-badge">{{ p.index }}</div>
        <div class="phase-text">
          <div class="phase-label">{{ p.label }}</div>
          <div class="phase-hint">{{ p.hint }}</div>
        </div>
      </div>
    </div>

    <VueFlow
      v-model:nodes="store.nodes"
      v-model:edges="store.edges"
      :node-types="nodeTypes"
      :default-edge-options="{ markerEnd: { type: MarkerType.ArrowClosed, color: '#7BC4E8' }, style: { stroke: '#7BC4E8', strokeWidth: 1.5 } }"
      :default-viewport="{ x: 0, y: 0, zoom: 1 }"
      :min-zoom="0.4"
      :max-zoom="2"
      :nodes-draggable="true"
      :nodes-connectable="true"
      :elements-selectable="true"
      :delete-key-code="['Delete', 'Backspace']"
      class="rag-flow"
      @connect="onConnect"
      @node-click="onNodeClick"
      @node-drag-stop="onNodeDragStop"
      @edge-click="onEdgeClick"
    >
      <Background pattern-color="#1f2937" :gap="20" />
      <Controls position="bottom-right" />
      <MiniMap pannable zoomable node-color="#5B9BD5" mask-color="rgba(15,23,42,0.7)" />
    </VueFlow>
  </div>
</template>

<script setup lang="ts">
import { computed, markRaw } from 'vue'
import { VueFlow, MarkerType, type Connection } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'

import { useWorkflowStore } from '@/stores/workflow'
import { PHASE_HEADERS, type PhaseHeader } from '@/utils/workflowTemplate'

import InputNode from './nodes/InputNode.vue'
import ParserNode from './nodes/ParserNode.vue'
import KnowledgeNode from './nodes/KnowledgeNode.vue'
import ChunkerNode from './nodes/ChunkerNode.vue'
import EmbeddingNode from './nodes/EmbeddingNode.vue'
import VectorNode from './nodes/VectorNode.vue'
import RetrieveNode from './nodes/RetrieveNode.vue'
import RelevanceNode from './nodes/RelevanceNode.vue'
import LlmNode from './nodes/LlmNode.vue'
import GuardNode from './nodes/GuardNode.vue'
import CitationNode from './nodes/CitationNode.vue'
import OutputNode from './nodes/OutputNode.vue'

const store = useWorkflowStore()

const nodeTypes = markRaw({
  input: InputNode,
  parser: ParserNode,
  knowledge: KnowledgeNode,
  chunker: ChunkerNode,
  embedding: EmbeddingNode,
  vector: VectorNode,
  retrieve: RetrieveNode,
  relevance: RelevanceNode,
  llm: LlmNode,
  guard: GuardNode,
  citation: CitationNode,
  output: OutputNode,
})

function onConnect(connection: Connection) {
  if (!connection.source || !connection.target) return
  store.addEdge(connection.source, connection.target)
}

function onNodeClick(event: any) {
  const node = event?.node
  if (node?.id) store.openDrawer(node.id)
}

function onNodeDragStop(event: any) {
  const node = event?.node
  if (node?.id && node.position) {
    store.updateNodePosition(node.id, node.position)
  }
}

function onEdgeClick(event: any) {
  const edge = event?.edge
  if (!edge?.id) return
  if (window.confirm('删除这条连线？')) {
    store.removeEdge(edge.id)
  }
}

function phaseStyle(p: PhaseHeader) {
  // 画布固定 viewport zoom=1，phase 标题直接使用画布坐标
  return {
    left: `${p.x}px`,
    top: `${p.y}px`,
    width: `${p.width}px`,
  }
}
</script>

<style scoped>
.rag-flow-canvas {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 540px;
}
.rag-flow {
  background: rgba(15,23,42,0.55);
  border-radius: 12px;
  border: 1px solid rgba(148,163,184,0.18);
}

.phase-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 2;
  overflow: hidden;
}
.phase-chip {
  position: absolute;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 14px 6px 8px;
  background: rgba(15,23,42,0.65);
  border: 1px solid rgba(148,163,184,0.22);
  border-radius: 999px;
  backdrop-filter: blur(6px);
  box-shadow: 0 4px 12px -6px rgba(0,0,0,0.4);
}
.phase-badge {
  width: 26px;
  height: 26px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  color: #0f172a;
  background: rgba(148,163,184,0.85);
  flex-shrink: 0;
}
.phase-text {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}
.phase-label {
  font-size: 13px;
  font-weight: 700;
  color: #e2e8f0;
  line-height: 1.2;
  white-space: nowrap;
}
.phase-hint {
  font-size: 10px;
  color: #94a3b8;
  line-height: 1.2;
  white-space: nowrap;
}

.phase-chip.tone-blue   .phase-badge { background: rgba(91,155,213,0.95); color: #0f172a; }
.phase-chip.tone-cyan   .phase-badge { background: rgba(20,184,166,0.95); color: #0f172a; }
.phase-chip.tone-purple .phase-badge { background: rgba(167,139,250,0.95); color: #0f172a; }
.phase-chip.tone-amber  .phase-badge { background: rgba(251,191,36,0.95);  color: #0f172a; }

.phase-chip.tone-blue   { border-color: rgba(91,155,213,0.45); }
.phase-chip.tone-cyan   { border-color: rgba(20,184,166,0.45); }
.phase-chip.tone-purple { border-color: rgba(167,139,250,0.45); }
.phase-chip.tone-amber  { border-color: rgba(251,191,36,0.45); }

:deep(.vue-flow__node) {
  font-family: inherit;
}
:deep(.vue-flow__edge-path) {
  stroke-linecap: round;
}
:deep(.vue-flow__controls-button) {
  background: rgba(15,23,42,0.85);
  border-color: rgba(91,155,213,0.35);
  color: #93c5fd;
  fill: currentColor;
}
:deep(.vue-flow__controls-button:hover) {
  background: rgba(91,155,213,0.25);
}
:deep(.vue-flow__minimap) {
  background: rgba(15,23,42,0.85);
  border: 1px solid rgba(91,155,213,0.3);
  border-radius: 6px;
}
</style>
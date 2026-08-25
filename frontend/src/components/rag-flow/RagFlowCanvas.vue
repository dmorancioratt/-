<template>
  <div class="rag-flow-canvas">
    <VueFlow
      v-model:nodes="store.nodes"
      v-model:edges="store.edges"
      :node-types="nodeTypes"
      :default-edge-options="{ markerEnd: { type: MarkerType.ArrowClosed, color: '#7BC4E8' }, style: { stroke: '#7BC4E8', strokeWidth: 1.5 } }"
      :default-viewport="{ x: 0, y: 0, zoom: 0.85 }"
      :min-zoom="0.3"
      :max-zoom="2"
      :nodes-draggable="true"
      :nodes-connectable="true"
      :elements-selectable="true"
      :delete-key-code="['Delete', 'Backspace']"
      class="rag-flow"
      fit-view-on-init
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
  // 简单确认删除
  if (window.confirm('删除这条连线？')) {
    store.removeEdge(edge.id)
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
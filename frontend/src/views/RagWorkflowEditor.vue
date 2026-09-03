<template>
  <div class="rag-admin-page">
    <!-- 顶部工具栏 -->
    <div class="top-bar">
      <WorkflowToolbar />
    </div>

    <!-- 主体内容区 -->
    <div class="main-content">
      <!-- 左侧：节点库 -->
      <div class="left-sidebar">
        <NodeLibrary />
      </div>

      <!-- 中间：画布 -->
      <div class="canvas-area">
        <div class="canvas-top">
          <CloseLoopBar />
        </div>
        <div class="canvas-canvas">
          <RagFlowCanvas />
        </div>
        <div class="canvas-progress">
          <RunProgressBar />
        </div>
      </div>

      <!-- 右侧：工作流状态 + 节点配置 -->
      <div class="right-sidebar">
        <div class="status-indicator">
          <div class="status-row">
            <span class="status-label">工作流状态</span>
            <span class="status-group">
              <span class="status-item" :class="{ active: !store.runtime.running }">空闲</span>
              <span class="status-item" :class="{ active: store.runtime.running }">运行</span>
            </span>
          </div>
          <div class="status-row">
            <span class="status-label">上次运行</span>
            <span class="status-value">{{ lastRunLabel }}</span>
          </div>
          <button type="button" class="status-link" @click="focusRunLog">查看日志</button>
        </div>
        <RagEngineStatus />
        <RunStageLog />
        <div class="config-area">
          <NodeConfigDrawer />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useWorkflowStore } from '@/stores/workflow'
import WorkflowToolbar from '@/components/rag-flow/WorkflowToolbar.vue'
import NodeLibrary from '@/components/rag-flow/NodeLibrary.vue'
import RagFlowCanvas from '@/components/rag-flow/RagFlowCanvas.vue'
import NodeConfigDrawer from '@/components/rag-flow/NodeConfigDrawer.vue'
import RagEngineStatus from '@/components/rag-flow/RagEngineStatus.vue'
import RunStageLog from '@/components/rag-flow/RunStageLog.vue'
import RunProgressBar from '@/components/rag-flow/RunProgressBar.vue'
import CloseLoopBar from '@/components/rag-flow/CloseLoopBar.vue'

const store = useWorkflowStore()
const lastRunLabel = computed(() => store.runtime.lastRunAt
  ? new Date(store.runtime.lastRunAt).toLocaleTimeString('zh-CN', { hour12: false })
  : '尚未运行')

function focusRunLog() {
  document.getElementById('workflow-run-log')?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  document.getElementById('workflow-run-log')?.focus({ preventScroll: true })
}

onMounted(async () => {
  store.loadDraft()
  await store.ensureConfig()
  await store.fetchDocs()
  if (store.totalChunks === 0) store.openKnowledgeBase()
})
</script>

<style scoped>
.rag-admin-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 70px);
  width: 100%;
  color: #e2e8f0;
  overflow: hidden;
}

.top-bar {
  flex-shrink: 0;
  z-index: 10;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  gap: 0;
}

.left-sidebar {
  width: 320px;
  flex-shrink: 0;
  background: rgba(15, 23, 42, 0.7);
  border-right: 1px solid rgba(91, 155, 213, 0.15);
  display: flex;
  flex-direction: column;
}

.canvas-area {
  flex: 1;
  min-width: 0;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.canvas-top {
  flex-shrink: 0;
}

.canvas-canvas {
  flex: 1;
  min-height: 0;
  position: relative;
}

.canvas-progress {
  position: absolute;
  left: 16px;
  right: 220px;
  bottom: 12px;
  z-index: 5;
}

.right-sidebar {
  width: 320px;
  flex-shrink: 0;
  background: rgba(15, 23, 42, 0.7);
  border-left: 1px solid rgba(91, 155, 213, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.config-area {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.status-indicator {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(91, 155, 213, 0.12);
  background: rgba(15, 23, 42, 0.5);
}

.status-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 12px;
}

.status-row:last-of-type {
  margin-bottom: 0;
}

.status-label {
  color: #64748b;
}

.status-group {
  display: inline-flex;
  gap: 6px;
}

.status-item {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  color: #64748b;
  background: rgba(30, 41, 59, 0.6);
  cursor: pointer;
}

.status-item.active {
  color: #46c8ff;
  background: rgba(70, 200, 255, 0.15);
}

.status-value {
  color: #94a3b8;
  font-family: ui-monospace, Menlo, monospace;
  font-size: 11px;
}

.status-link {
  display: inline-block;
  padding: 0;
  border: 0;
  background: transparent;
  font-size: 11px;
  color: #88ddff;
  cursor: pointer;
  margin-top: 6px;
}

.status-link:hover {
  text-decoration: underline;
}
</style>

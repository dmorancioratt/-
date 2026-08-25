<template>
  <div class="rag-editor-page">
    <PageHeader
      title="RAG 工作流编辑器"
      desc="拖拽节点、配置参数、保存与回放 ｜ 防幻觉 + 引用校验的完整可视化编排"
    />

    <WorkflowToolbar />

    <div class="editor-canvas-wrap">
      <RagFlowCanvas />
    </div>

    <NodeConfigDrawer />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import RagFlowCanvas from '@/components/rag-flow/RagFlowCanvas.vue'
import WorkflowToolbar from '@/components/rag-flow/WorkflowToolbar.vue'
import NodeConfigDrawer from '@/components/rag-flow/NodeConfigDrawer.vue'
import { useWorkflowStore } from '@/stores/workflow'

const store = useWorkflowStore()

onMounted(() => {
  store.loadDraft()
  store.fetchDocs().catch(() => {})
})
</script>

<style scoped>
.rag-editor-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
  min-height: 600px;
}
.editor-canvas-wrap {
  flex: 1;
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 12px;
}
</style>
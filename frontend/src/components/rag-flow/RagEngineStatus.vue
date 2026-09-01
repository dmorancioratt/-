<template>
  <div class="engine-status-card">
    <div class="card-header">
      <span class="card-title">
        <el-icon :size="14"><Cpu /></el-icon> RAG 引擎
      </span>
      <el-button text size="small" @click="refresh" :loading="loading">
        <el-icon><Refresh /></el-icon>
      </el-button>
    </div>

    <div class="model-row">
      <span class="model-name" :title="status?.embedder?.model_name">
        {{ status?.embedder?.model_name || '—' }}
      </span>
      <el-tag :type="modelTone" size="small" effect="dark">{{ modelLabel }}</el-tag>
    </div>
    <div class="dim-row">向量维度 {{ status?.embedder?.dim ?? '—' }}</div>

    <div class="divider" />

    <div class="source-list">
      <div v-for="src in sources" :key="src.source_type" class="source-item">
        <span class="source-dot" :class="`dot-${src.status}`"></span>
        <span class="source-name">{{ SOURCE_LABELS[src.source_type] || src.source_type }}</span>
        <span class="source-count" :title="src.error_message">{{ src.chunk_count }} chunks</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Cpu, Refresh } from '@element-plus/icons-vue'
import { api } from '@/api/http'
import type { RagEngineStatus } from '@/types/workflow'

const status = ref<RagEngineStatus | null>(null)
const loading = ref(false)

const SOURCE_LABELS: Record<string, string> = {
  jd: 'JD 原文',
  job_skill: '岗位技能',
  skill: '技能图谱',
  candidate: '候选人',
}

const sources = computed(() => status.value?.sources || [])

const modelLabel = computed(() =>
  status.value?.embedder?.is_fake ? 'Fake 降级' : 'BGE 中文模型'
)
const modelTone = computed(() =>
  status.value?.embedder?.is_fake ? 'warning' : 'success'
)

async function refresh() {
  loading.value = true
  try {
    status.value = await api.ragStatus()
  } catch {
    status.value = null
  } finally {
    loading.value = false
  }
}

onMounted(refresh)
</script>

<style scoped>
.engine-status-card {
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
  color: #93c5fd;
}

.model-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.model-name {
  font-size: 12px;
  color: #cbd5e1;
  font-family: ui-monospace, Menlo, monospace;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.dim-row {
  font-size: 11px;
  color: #64748b;
  margin-top: 3px;
}

.divider {
  height: 1px;
  background: rgba(91, 155, 213, 0.1);
  margin: 10px 0;
}

.source-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.source-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}
.source-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
  background: #64748b;
}
.source-dot.dot-success { background: #46c8ff; }
.source-dot.dot-failed { background: #f43f5e; }
.source-dot.dot-running { background: #fbbf24; }
.source-dot.dot-never { background: #475569; }

.source-name {
  flex: 1;
  color: #94a3b8;
}
.source-count {
  color: #64748b;
  font-family: ui-monospace, Menlo, monospace;
  font-size: 11px;
}
</style>

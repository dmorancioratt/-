<template>
  <div class="config-panel">
    <!-- 顶部标题栏 -->
    <div class="panel-header">
      <div class="header-left">
        <div class="title">节点配置</div>
      </div>
      <div class="header-right">
        <el-button text circle size="small" @click="store.closeDrawer()" v-if="store.selectedNode">
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
    </div>

    <div class="panel-body" v-if="store.selectedNode">
      <!-- 节点基础信息 -->
      <div class="node-info-card" :class="`tone-${store.selectedNode.data.kind}`">
        <div class="node-header">
          <div class="node-icon-box">
            <el-icon :size="18"><component :is="getIcon(store.selectedNode.data.kind)" /></el-icon>
          </div>
          <div class="node-title-area">
            <div class="node-name">{{ store.selectedNode.data.label }}</div>
            <div class="node-type">{{ store.selectedNode.data.kind }}</div>
          </div>
          <div class="node-status-tag">
            <span class="status-dot" :class="`status-${store.selectedNode.data.status}`"></span>
            {{ store.selectedNode.data.status }}
          </div>
        </div>
        <div class="node-desc" v-if="store.selectedNode.data.description">
          {{ store.selectedNode.data.description }}
        </div>
        <div class="node-id-row">
          <span class="id-label">节点ID</span>
          <span class="id-value">{{ store.selectedNode.id }}</span>
        </div>
      </div>

      <!-- 配置表单区 -->
      <div class="form-section">
        <div class="section-header">
          <div class="section-title">{{ formTitle }}</div>
        </div>
        <div class="form-content">
          <component :is="formComponent" :node="store.selectedNode" />
        </div>
      </div>

      <!-- 高级配置区 (仅特定节点显示) -->
      <div class="form-section advanced" v-if="showAdvanced">
        <div class="section-header">
          <div class="section-title">高级配置</div>
        </div>
        <div class="advanced-content">
          <div class="advanced-item">
            <div class="adv-label">启用重排序</div>
            <el-switch v-model="localCfg.rerank" size="small" />
          </div>
          <div class="advanced-item">
            <div class="adv-label">混合检索</div>
            <el-switch v-model="localCfg.hybrid" size="small" />
          </div>
          <div class="advanced-item">
            <div class="adv-label">时间衰减</div>
            <el-switch v-model="localCfg.time_decay" size="small" />
          </div>
        </div>

        <!-- 权重设置 (仅检索节点显示) -->
        <div class="weight-section" v-if="showWeight">
          <div class="section-header">
            <div class="section-title">权重设置</div>
          </div>
          <div class="weight-content">
            <div class="weight-item">
              <div class="weight-label">向量权重</div>
              <el-slider v-model="localCfg.vector_weight" :min="0" :max="1" :step="0.01" show-input size="small" />
            </div>
            <div class="weight-item">
              <div class="weight-label">关键词权重</div>
              <el-slider v-model="localCfg.keyword_weight" :min="0" :max="1" :step="0.01" show-input size="small" />
            </div>
          </div>
        </div>
      </div>

      <!-- 删除按钮 -->
      <div class="action-bar" v-if="canDelete">
        <el-button type="danger" plain @click="onDelete">删除节点</el-button>
      </div>
    </div>

    <!-- 空状态提示 -->
    <div class="empty-state" v-else>
      <el-icon :size="48" color="#475569"><Pointer /></el-icon>
      <div class="empty-text">点击画布中的节点进行配置</div>
    </div>

    <!-- 测试运行对话框 -->
    <el-dialog v-model="store.testDialogVisible" title="测试运行 RAG 工作流" width="560px" append-to-body>
      <div class="test-run-form">
        <label>问题</label>
        <el-input v-model="store.testQuestion" type="textarea" :rows="3" placeholder="输入测试问题" />
        <div class="tip" v-if="!store.configId">
          <el-icon><InfoFilled /></el-icon>
          当前为草稿状态，请先保存工作流后再测试运行。
        </div>
      </div>
      <template #footer>
        <el-button @click="store.closeTestDialog()">取消</el-button>
        <el-button type="primary" :loading="store.runtime.running" :disabled="!store.configId" @click="onRunTest">
          开始运行
        </el-button>
      </template>
    </el-dialog>

    <!-- 测试结果展示对话框 -->
    <el-dialog v-model="resultVisible" title="RAG 工作流运行结果" width="720px" :show-close="true" append-to-body>
      <div v-if="store.runtime.lastResult" class="test-result">
        <h4>答案</h4>
        <div class="answer-block">{{ store.runtime.lastResult.answer || '(无)' }}</div>

        <h4>证据 ({{ store.runtime.lastResult.evidence.length }})</h4>
        <div class="evidence-list">
          <div v-for="(ev, i) in store.runtime.lastResult.evidence" :key="i" class="evidence-item">
            <div class="evidence-head">
              <span class="ev-source">#{{ ev.chunk_id }} · {{ ev.source_type }}/{{ ev.ref_id }}</span>
              <span class="ev-score">score={{ ev.score }}</span>
            </div>
            <div class="ev-text">{{ ev.text }}</div>
          </div>
        </div>

        <h4>阶段日志</h4>
        <div class="stage-log">
          <div v-for="(s, i) in store.runtime.lastResult.stages_log" :key="i" class="stage-row">
            <span class="stage-name">{{ s.stage }}</span>
            <span class="stage-status" :class="`s-${s.status}`">{{ s.status }}</span>
            <span class="stage-out">{{ s.output }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="resultVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { Close, InfoFilled, Pointer } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useWorkflowStore } from '@/stores/workflow'
import type { NodeKind } from '@/types/workflow'
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
import KnowledgeBaseForm from './node-forms/KnowledgeBaseForm.vue'
import ChunkerForm from './node-forms/ChunkerForm.vue'
import EmbeddingForm from './node-forms/EmbeddingForm.vue'
import VectorForm from './node-forms/VectorForm.vue'
import RetrieveForm from './node-forms/RetrieveForm.vue'
import RelevanceForm from './node-forms/RelevanceForm.vue'
import LlmForm from './node-forms/LlmForm.vue'
import GuardForm from './node-forms/GuardForm.vue'
import CitationForm from './node-forms/CitationForm.vue'
import InputForm from './node-forms/InputForm.vue'
import ParserForm from './node-forms/ParserForm.vue'
import OutputForm from './node-forms/OutputForm.vue'

const store = useWorkflowStore()
const resultVisible = ref(false)

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

function getIcon(kind: string) {
  return ICON_MAP[kind as NodeKind] || DataAnalysis
}

const FORM_MAP: Record<string, any> = {
  knowledge: KnowledgeBaseForm,
  chunker: ChunkerForm,
  embedding: EmbeddingForm,
  vector: VectorForm,
  retrieve: RetrieveForm,
  relevance: RelevanceForm,
  llm: LlmForm,
  guard: GuardForm,
  citation: CitationForm,
  input: InputForm,
  parser: ParserForm,
  output: OutputForm,
}

const formComponent = computed(() => {
  const kind = store.selectedNode?.data.kind
  if (!kind) return null
  return FORM_MAP[kind] || null
})

const formTitle = computed(() => {
  const kind = store.selectedNode?.data.kind
  const labels: Record<string, string> = {
    input: '输入配置',
    parser: '解析配置',
    knowledge: '知识库配置',
    chunker: '切片配置',
    embedding: '向量化配置',
    vector: '向量库配置',
    retrieve: '检索配置',
    relevance: '相关性配置',
    llm: '大模型配置',
    guard: '幻觉检测配置',
    citation: '引用配置',
    output: '输出配置',
  }
  return labels[kind || ''] || '配置'
})

const showAdvanced = computed(() => {
  const kind = store.selectedNode?.data.kind
  return ['retrieve', 'vector', 'llm'].includes(kind || '')
})

const showWeight = computed(() => {
  const kind = store.selectedNode?.data.kind
  return kind === 'retrieve'
})

const canDelete = computed(() => {
  const id = store.selectedNode?.id
  return id && id !== 'node-input' && id !== 'node-output'
})

const localCfg = computed({
  get: () => ({
    rerank: false,
    hybrid: false,
    time_decay: false,
    vector_weight: 0.8,
    keyword_weight: 0.2,
    ...(store.selectedNode?.data.config || {}),
  }),
  set: (v) => {
    if (store.selectedNode) {
      store.setNodeConfig(store.selectedNode.id, v)
    }
  },
})

function onDelete() {
  const id = store.selectedNode?.id
  if (!id) return
  ElMessageBox.confirm('删除该节点？连线会一并清理。', '删除节点', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
    .then(() => {
      store.deleteNode(id)
      store.closeDrawer()
      ElMessage.success('已删除')
    })
    .catch(() => {})
}

async function onRunTest() {
  if (!store.configId) {
    ElMessage.warning('请先保存工作流再测试运行')
    return
  }
  const q = store.testQuestion.trim()
  if (!q) {
    ElMessage.warning('请输入测试问题')
    return
  }
  try {
    await store.testRunStream(q, 5)
    resultVisible.value = true
    store.closeTestDialog()
  } catch (e: any) {
    ElMessage.error(e?.message || '测试运行失败')
  }
}
</script>

<style scoped>
.config-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid rgba(91, 155, 213, 0.15);
  background: rgba(15, 23, 42, 0.5);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title {
  font-size: 15px;
  font-weight: 600;
  color: #e2e8f0;
}

.panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 节点信息卡片 */
.node-info-card {
  padding: 14px;
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(91, 155, 213, 0.2);
  border-radius: 10px;
}

.node-info-card.tone-input { border-color: rgba(59, 130, 246, 0.3); }
.node-info-card.tone-parser { border-color: rgba(139, 92, 246, 0.3); }
.node-info-card.tone-knowledge { border-color: rgba(236, 72, 153, 0.3); }
.node-info-card.tone-chunker { border-color: rgba(245, 158, 11, 0.3); }
.node-info-card.tone-embedding { border-color: rgba(59, 130, 246, 0.3); }
.node-info-card.tone-vector { border-color: rgba(20, 184, 166, 0.3); }
.node-info-card.tone-retrieve { border-color: rgba(91, 155, 213, 0.3); }
.node-info-card.tone-relevance { border-color: rgba(167, 139, 250, 0.3); }
.node-info-card.tone-llm { border-color: rgba(99, 102, 241, 0.3); }
.node-info-card.tone-guard { border-color: rgba(52, 211, 153, 0.3); }
.node-info-card.tone-citation { border-color: rgba(251, 191, 36, 0.3); }
.node-info-card.tone-output { border-color: rgba(244, 63, 94, 0.3); }

.node-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.node-icon-box {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(91, 155, 213, 0.15);
  color: #60a5fa;
  flex-shrink: 0;
}

.tone-knowledge .node-icon-box { background: rgba(236, 72, 153, 0.15); color: #f472b6; }
.tone-chunker .node-icon-box { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
.tone-embedding .node-icon-box { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
.tone-vector .node-icon-box { background: rgba(20, 184, 166, 0.15); color: #2dd4bf; }
.tone-retrieve .node-icon-box { background: rgba(91, 155, 213, 0.15); color: #60a5fa; }
.tone-relevance .node-icon-box { background: rgba(167, 139, 250, 0.15); color: #a78bfa; }
.tone-llm .node-icon-box { background: rgba(99, 102, 241, 0.15); color: #818cf8; }
.tone-guard .node-icon-box { background: rgba(52, 211, 153, 0.15); color: #34d399; }
.tone-citation .node-icon-box { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }
.tone-output .node-icon-box { background: rgba(244, 63, 94, 0.15); color: #fb7185; }

.node-title-area {
  flex: 1;
  min-width: 0;
}

.node-name {
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 2px;
}

.node-type {
  font-size: 11px;
  color: #64748b;
  font-family: monospace;
}

.node-status-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #94a3b8;
  padding: 3px 8px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 4px;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #64748b;
}

.status-idle .status-dot { background: #64748b; }
.status-running .status-dot { background: #fbbf24; }
.status-done .status-dot { background: #34d399; }
.status-error .status-dot { background: #f43f5e; }
.status-warn .status-dot { background: #fbbf24; }

.node-desc {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 10px;
  line-height: 1.5;
}

.node-id-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(91, 155, 213, 0.1);
}

.id-label {
  font-size: 11px;
  color: #64748b;
}

.id-value {
  font-size: 11px;
  color: #94a3b8;
  font-family: monospace;
}

/* 表单区 */
.form-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(91, 155, 213, 0.1);
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #e2e8f0;
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* 高级配置 */
.advanced-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.advanced-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(91, 155, 213, 0.1);
  border-radius: 6px;
}

.adv-label {
  font-size: 13px;
  color: #cbd5e1;
}

/* 权重设置 */
.weight-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(91, 155, 213, 0.1);
}

.weight-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.weight-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.weight-label {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 500;
}

/* 操作栏 */
.action-bar {
  padding-top: 8px;
  margin-top: auto;
}

/* 空状态 */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.empty-text {
  font-size: 13px;
  color: #64748b;
}

/* 自定义滚动条 */
.panel-body::-webkit-scrollbar {
  width: 6px;
}

.panel-body::-webkit-scrollbar-track {
  background: transparent;
}

.panel-body::-webkit-scrollbar-thumb {
  background: rgba(91, 155, 213, 0.3);
  border-radius: 3px;
}

.panel-body::-webkit-scrollbar-thumb:hover {
  background: rgba(91, 155, 213, 0.5);
}

/* 测试结果相关样式 */
.test-run-form label {
  display: block;
  font-size: 12px;
  color: #cbd5e1;
  margin-bottom: 6px;
}

.tip {
  margin-top: 10px;
  padding: 8px 12px;
  background: rgba(251, 191, 36, 0.08);
  border: 1px solid rgba(251, 191, 36, 0.25);
  border-radius: 6px;
  font-size: 12px;
  color: #fcd34d;
  display: flex;
  align-items: center;
  gap: 6px;
}

.test-result h4 {
  font-size: 13px;
  color: #93c5fd;
  margin: 14px 0 8px;
}

.answer-block {
  padding: 12px 14px;
  background: rgba(91, 155, 213, 0.06);
  border: 1px solid rgba(91, 155, 213, 0.18);
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 13px;
  line-height: 1.6;
}

.evidence-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 220px;
  overflow-y: auto;
}

.evidence-item {
  padding: 8px 10px;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(91, 155, 213, 0.12);
  border-radius: 6px;
}

.evidence-head {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #94a3b8;
  margin-bottom: 4px;
}

.ev-source { font-family: ui-monospace, Menlo, monospace; }
.ev-score { color: #93c5fd; font-family: ui-monospace, Menlo, monospace; }
.ev-text { font-size: 12px; color: #cbd5e1; line-height: 1.45; }

.stage-log { display: flex; flex-direction: column; gap: 4px; }
.stage-row {
  display: grid;
  grid-template-columns: 110px 80px 1fr;
  align-items: center;
  padding: 6px 10px;
  background: rgba(15, 23, 42, 0.45);
  border: 1px solid rgba(91, 155, 213, 0.12);
  border-radius: 6px;
  font-size: 12px;
}
.stage-name { color: #93c5fd; font-weight: 600; }
.stage-status { font-family: ui-monospace, Menlo, monospace; font-size: 11px; }
.stage-status.s-done { color: #34d399; }
.stage-status.s-error { color: #f43f5e; }
.stage-status.s-warn { color: #fbbf24; }
.stage-out { color: #cbd5e1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* Element Plus 深色主题适配 */
:deep(.el-dialog) {
  background: #1e293b;
  border: 1px solid rgba(91, 155, 213, 0.2);
}

:deep(.el-dialog__title) {
  color: #e2e8f0;
}

:deep(.el-dialog__body) {
  color: #cbd5e1;
}

:deep(.el-dialog__headerbtn .el-dialog__close) {
  color: #94a3b8;
}

/* 输入数字加减按钮 — 蓝色主题 */
:deep(.el-input-number__decrease),
:deep(.el-input-number__increase) {
  background: rgba(59, 130, 246, 0.12);
  color: #60a5fa;
  border-color: rgba(59, 130, 246, 0.22);
}

:deep(.el-input-number__decrease:hover),
:deep(.el-input-number__increase:hover) {
  color: #93c5fd;
  background: rgba(59, 130, 246, 0.22);
}

:deep(.el-input-number__decrease .el-icon),
:deep(.el-input-number__increase .el-icon) {
  color: #60a5fa;
}

:deep(.el-input-number__decrease.is-disabled),
:deep(.el-input-number__increase.is-disabled) {
  color: #475569;
  background: rgba(30, 41, 59, 0.4);
  border-color: rgba(91, 155, 213, 0.12);
}

/* 滑块 — 蓝色主题 */
:deep(.el-slider__runway) {
  background: rgba(59, 130, 246, 0.18);
}

:deep(.el-slider__bar) {
  background: #3b82f6;
}

:deep(.el-slider__button) {
  border-color: #3b82f6;
}

:deep(.el-slider__button:hover),
:deep(.el-slider__button.hover) {
  border-color: #60a5fa;
}
</style>

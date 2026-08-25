<template>
  <el-drawer
    v-model="store.drawerOpen"
    direction="rtl"
    size="480px"
    :with-header="false"
    :destroy-on-close="false"
  >
    <template #default>
      <div v-if="store.selectedNode" class="config-drawer">
        <div class="drawer-header" :class="`tone-${store.selectedNode.data.kind}`">
          <div class="title-row">
            <div class="kind-badge">{{ store.selectedNode.data.kind }}</div>
            <div class="title">{{ store.selectedNode.data.label }}</div>
            <el-button text circle size="small" @click="store.closeDrawer()" class="close-btn">
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
          <div v-if="store.selectedNode.data.description" class="desc">
            {{ store.selectedNode.data.description }}
          </div>
          <div class="status-row">
            <span class="status-dot" :class="`status-${store.selectedNode.data.status}`"></span>
            状态：<strong>{{ store.selectedNode.data.status }}</strong>
          </div>
        </div>

        <div class="drawer-body">
          <component :is="formComponent" :node="store.selectedNode" />
        </div>

        <div class="drawer-footer">
          <el-button @click="onDelete" type="danger" plain v-if="canDelete">删除节点</el-button>
          <el-button @click="store.closeDrawer()">关闭</el-button>
        </div>
      </div>
    </template>
  </el-drawer>

  <!-- 测试运行对话框 -->
  <el-dialog v-model="store.testDialogVisible" title="测试运行 RAG 工作流" width="560px">
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
  <el-dialog v-model="resultVisible" title="RAG 工作流运行结果" width="720px" :show-close="true">
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
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { Close, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useWorkflowStore } from '@/stores/workflow'
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

const FORM_MAP = {
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
  return (FORM_MAP as any)[kind] || null
})

const canDelete = computed(() => {
  const id = store.selectedNode?.id
  return id && id !== 'node-input' && id !== 'node-output'
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
    await store.testRun(q, 5)
    resultVisible.value = true
    store.closeTestDialog()
  } catch (e: any) {
    ElMessage.error(e?.message || '测试运行失败')
  }
}
</script>

<style scoped>
.config-drawer { display: flex; flex-direction: column; height: 100%; }
.drawer-header {
  padding: 18px 20px 14px;
  border-bottom: 1px solid rgba(91,155,213,0.18);
  background: linear-gradient(160deg, rgba(91,155,213,0.10), rgba(91,155,213,0.02));
}
.title-row { display: flex; align-items: center; gap: 10px; }
.kind-badge {
  padding: 2px 8px;
  font-size: 10px;
  background: rgba(91,155,213,0.18);
  color: #93c5fd;
  border-radius: 4px;
  font-family: ui-monospace, Menlo, monospace;
}
.title { font-size: 16px; font-weight: 700; color: #f1f5f9; flex: 1; }
.close-btn { color: #94a3b8; }
.desc { font-size: 12px; color: #94a3b8; margin-top: 6px; line-height: 1.5; }
.status-row { font-size: 11px; color: #94a3b8; margin-top: 8px; display: flex; align-items: center; gap: 6px; }
.status-row strong { color: #cbd5e1; font-family: ui-monospace, Menlo, monospace; }
.status-dot { width: 8px; height: 8px; border-radius: 999px; background: rgba(148,163,184,0.6); display: inline-block; }
.status-running .status-dot { background: #fbbf24; }
.status-done .status-dot { background: #34d399; }
.status-error .status-dot { background: #f43f5e; }
.status-warn .status-dot { background: #fbbf24; }

.drawer-body { flex: 1; overflow-y: auto; padding: 18px 20px; }
.drawer-footer {
  padding: 12px 20px;
  border-top: 1px solid rgba(91,155,213,0.18);
  display: flex; gap: 8px; justify-content: flex-end;
  background: rgba(15,23,42,0.55);
}

.test-run-form label { display: block; font-size: 12px; color: #cbd5e1; margin-bottom: 6px; }
.tip {
  margin-top: 10px;
  padding: 8px 12px;
  background: rgba(251,191,36,0.08);
  border: 1px solid rgba(251,191,36,0.25);
  border-radius: 6px;
  font-size: 12px;
  color: #fcd34d;
  display: flex; align-items: center; gap: 6px;
}

.test-result h4 { font-size: 13px; color: #93c5fd; margin: 14px 0 8px; }
.answer-block {
  padding: 12px 14px;
  background: rgba(91,155,213,0.06);
  border: 1px solid rgba(91,155,213,0.18);
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 13px;
  line-height: 1.6;
}
.evidence-list { display: flex; flex-direction: column; gap: 6px; max-height: 220px; overflow-y: auto; }
.evidence-item {
  padding: 8px 10px;
  background: rgba(15,23,42,0.5);
  border: 1px solid rgba(91,155,213,0.12);
  border-radius: 6px;
}
.evidence-head { display: flex; justify-content: space-between; font-size: 11px; color: #94a3b8; margin-bottom: 4px; }
.ev-source { font-family: ui-monospace, Menlo, monospace; }
.ev-score { color: #93c5fd; font-family: ui-monospace, Menlo, monospace; }
.ev-text { font-size: 12px; color: #cbd5e1; line-height: 1.45; }
.stage-log { display: flex; flex-direction: column; gap: 4px; }
.stage-row {
  display: grid;
  grid-template-columns: 110px 80px 1fr;
  align-items: center;
  padding: 6px 10px;
  background: rgba(15,23,42,0.45);
  border: 1px solid rgba(91,155,213,0.12);
  border-radius: 6px;
  font-size: 12px;
}
.stage-name { color: #93c5fd; font-weight: 600; }
.stage-status { font-family: ui-monospace, Menlo, monospace; font-size: 11px; }
.stage-status.s-done { color: #34d399; }
.stage-status.s-error { color: #f43f5e; }
.stage-status.s-warn { color: #fbbf24; }
.stage-out { color: #cbd5e1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>
<template>
  <div class="cfg-form">
    <el-upload
      drag
      action="#"
      :auto-upload="false"
      :show-file-list="false"
      :on-change="handleChange"
      :disabled="uploading"
      accept=".pdf,.docx,.txt,.md"
      class="kb-uploader"
    >
      <el-icon class="upload-icon" :class="{ spinning: uploading }"><Loading v-if="uploading" /><UploadFilled v-else /></el-icon>
      <div class="upload-text">{{ uploading ? '正在上传并建立索引...' : '点击或拖拽上传文档' }}</div>
      <div class="upload-tip">支持 .pdf / .docx / .txt / .md，单文件 10MB 以内</div>
    </el-upload>

    <div class="docs-header">
      <span>文档列表 ({{ docs.length }})</span>
      <el-button text size="small" @click="refreshDocs" :loading="loading">刷新</el-button>
    </div>

    <el-table :data="docs" size="small" :empty-text="'暂无文档'">
      <el-table-column prop="id" label="ID" width="50" />
      <el-table-column prop="filename" label="文件名" show-overflow-tooltip />
      <el-table-column prop="file_type" label="类型" width="70" />
      <el-table-column label="字符" width="70">
        <template #default="{ row }">{{ row.char_count }}</template>
      </el-table-column>
      <el-table-column label="chunks" width="80">
        <template #default="{ row }">
          <el-tag v-if="row.indexed" type="success" size="small">{{ row.chunk_count }}</el-tag>
          <el-tag v-else type="info" size="small">未索引</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" plain :loading="chunkingId === row.id" @click="onChunk(row)" v-if="!row.indexed">
            切片
          </el-button>
          <el-button size="small" type="danger" plain :loading="deletingId === row.id" @click="onDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="kb-stats">
      总文档 <strong>{{ docs.length }}</strong>
      · 总字符 <strong>{{ totalChars.toLocaleString() }}</strong>
      · 已索引 chunks <strong>{{ totalChunks }}</strong>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, UploadFilled } from '@element-plus/icons-vue'
import { useWorkflowStore } from '@/stores/workflow'
import type { DocumentInfo } from '@/types/workflow'

const store = useWorkflowStore()
const docs = ref<DocumentInfo[]>([])
const loading = ref(false)
const uploading = ref(false)
const chunkingId = ref<number | null>(null)
const deletingId = ref<number | null>(null)

const totalChars = computed(() => docs.value.reduce((acc, d) => acc + d.char_count, 0))
const totalChunks = computed(() => docs.value.reduce((acc, d) => acc + d.chunk_count, 0))

async function refreshDocs() {
  loading.value = true
  try {
    await store.fetchDocs()
    docs.value = store.docs
  } finally {
    loading.value = false
  }
}

async function handleChange(file: any) {
  if (!file?.raw) return
  uploading.value = true
  try {
    const doc = await store.uploadDoc(file.raw)
    const indexed = await store.chunkDoc(doc.id, 500, 50)
    ElMessage.success(`已上传并索引 ${doc.filename}（${indexed.chunk_count} 个 chunks）`)
    await refreshDocs()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '上传或索引失败')
  } finally {
    uploading.value = false
    await refreshDocs()
  }
}

async function onChunk(doc: DocumentInfo) {
  chunkingId.value = doc.id
  try {
    const res = await store.chunkDoc(doc.id, 500, 50)
    ElMessage.success(`已切片 ${res.chunk_count} 个 chunks`)
    await refreshDocs()
  } catch (e: any) {
    ElMessage.error(e?.message || '切片失败')
  } finally {
    chunkingId.value = null
  }
}

async function onDelete(doc: DocumentInfo) {
  deletingId.value = doc.id
  try {
    await store.deleteDoc(doc.id)
    ElMessage.success(`已删除 ${doc.filename}`)
    await refreshDocs()
  } catch (e: any) {
    ElMessage.error(e?.message || '删除失败')
  } finally {
    deletingId.value = null
  }
}

onMounted(refreshDocs)
</script>

<style scoped>
.cfg-form { display: flex; flex-direction: column; gap: 14px; }
.kb-uploader {
  width: 100%;
}
.kb-uploader :deep(.el-upload-dragger) {
  padding: 18px;
  background: rgba(91,155,213,0.04);
  border: 1px dashed rgba(91,155,213,0.4);
  border-radius: 8px;
}
.kb-uploader :deep(.el-upload-dragger:hover) { border-color: rgba(91,155,213,0.7); }
.upload-icon { font-size: 28px; color: #93c5fd; margin-bottom: 6px; }
.upload-icon.spinning { animation: spin 1s linear infinite; }
.upload-text { font-size: 13px; color: #cbd5e1; }
.upload-tip { font-size: 11px; color: #94a3b8; margin-top: 4px; }

.docs-header {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 12px; color: #cbd5e1;
}
.kb-stats {
  font-size: 12px; color: #94a3b8;
  padding: 8px 12px;
  background: rgba(91,155,213,0.05);
  border-radius: 6px;
}
.kb-stats strong {
  color: #e2e8f0;
  font-family: ui-monospace, Menlo, monospace;
  margin: 0 4px;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>

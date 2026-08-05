<template>
  <div class="page">
    <PageHeader title="JD解析" desc="输入岗位 JD 文本，提取岗位名称、职责、技能、工具、证书、场景和证据来源">
      <el-button type="primary" :loading="loading" @click="submit">{{ result ? '重新解析 JD' : '解析 JD' }}</el-button>
    </PageHeader>
    <div class="content-grid">
      <div class="panel span-5">
        <el-input v-model="text" type="textarea" :rows="18" placeholder="请输入 JD 文本" />
      </div>
      <div class="panel span-7">
        <el-empty v-if="!result" description="解析结果将在这里展示" />
        <template v-else>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="岗位名称">{{ result.job_name }}</el-descriptions-item>
            <el-descriptions-item label="所属领域">{{ result.domain }}</el-descriptions-item>
            <el-descriptions-item label="岗位等级">{{ result.level }}</el-descriptions-item>
            <el-descriptions-item label="经验要求">{{ result.experience }}</el-descriptions-item>
            <el-descriptions-item label="置信度">{{ result.confidence }}</el-descriptions-item>
            <el-descriptions-item label="防控状态">{{ result.guard_status }}</el-descriptions-item>
          </el-descriptions>
          <h3>核心职责</h3>
          <el-timeline>
            <el-timeline-item v-for="item in result.responsibilities" :key="item">{{ item }}</el-timeline-item>
          </el-timeline>
          <h3>必备技能</h3>
          <div class="tag-list"><el-tag v-for="item in result.required_skills" :key="item">{{ item }}</el-tag></div>
          <h3>加分技能与工具平台</h3>
          <div class="tag-list">
            <el-tag v-for="item in [...result.preferred_skills, ...result.tools]" :key="item" type="info">{{ item }}</el-tag>
          </div>
          <h3>证据来源</h3>
          <el-table :data="result.evidence_sources" size="small">
            <el-table-column prop="source" label="来源" />
            <el-table-column prop="quote" label="证据片段" />
          </el-table>
        </template>
      </div>
    </div>
    <section class="panel history-panel">
      <div class="history-head">
        <div><h3>解析历史</h3><p>每次点击解析都会保存结果；相同原文只保存一份原始 JD。</p></div>
        <el-button text :loading="historyLoading" @click="loadHistory">刷新</el-button>
      </div>
      <el-table :data="history" stripe @row-click="restoreHistory">
        <el-table-column prop="job_name" label="岗位" min-width="180" />
        <el-table-column prop="domain" label="领域" min-width="120" />
        <el-table-column prop="level" label="等级" width="90" />
        <el-table-column label="核心技能" min-width="240">
          <template #default="{ row }">{{ (row.required_skills || []).slice(0, 4).join('、') || '未提取' }}</template>
        </el-table-column>
        <el-table-column label="置信度" width="90">
          <template #default="{ row }">{{ Math.round(Number(row.confidence || 0) * 100) }}%</template>
        </el-table-column>
        <el-table-column label="操作" width="90"><template #default><el-button link type="primary">查看</el-button></template></el-table-column>
      </el-table>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { onMounted, ref, watch } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'
import { loadPageState, savePageState } from '@/utils/pageState'

const loading = ref(false)
const historyLoading = ref(false)
const history = ref<any[]>([])
const result = ref<any>()
const text = ref('大模型应用工程师，负责企业知识库 RAG 应用建设，需要 Python、FastAPI、LangChain、向量数据库、Docker、Prompt Engineering，熟悉智能制造或智慧教育场景。')

async function submit() {
  loading.value = true
  try {
    result.value = await api.parseJd(text.value)
    await loadHistory()
    persistState()
  } catch {
    ElMessage.error('解析失败，请确认后端服务已启动')
  } finally {
    loading.value = false
  }
}

async function loadHistory() {
  historyLoading.value = true
  try {
    history.value = await api.jdHistory()
  } catch {
    history.value = []
  } finally {
    historyLoading.value = false
  }
}

function restoreHistory(row: any) {
  text.value = row.source_text || ''
  result.value = row
  persistState()
}

function persistState() {
  savePageState('jd-parser', { text: text.value, result: result.value })
}

watch(text, persistState)

onMounted(async () => {
  const cached = loadPageState<{ text?: string; result?: any }>('jd-parser')
  if (cached) {
    if (typeof cached.text === 'string') text.value = cached.text
    result.value = cached.result
  }
  await loadHistory()
})
</script>

<style scoped>
.history-panel { margin-top: 18px; padding: 20px; }
.history-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 12px; }
.history-head h3 { margin: 0; color: var(--text); font-size: 17px; }
.history-head p { margin: 5px 0 0; color: var(--muted); font-size: 13px; }
</style>

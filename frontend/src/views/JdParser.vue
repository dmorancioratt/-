<template>
  <div class="page jd-parser-page">
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
const text = ref('')

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

<style>
/* Unscoped glass overrides — specificity must beat theme-fixes.css (loaded after page styles).
   theme-fixes: body.theme-dark .app-main:not(.app-main--dashboard) :is(.panel,.page-toolbar,...) { background:#0a1c2b!important; box-shadow:none!important }
   styles.css:  body:not(.login-active) .app-main :is(.panel,.page-toolbar,...) { background:linear-gradient(...)!important }
   Both ≈ 0-0-41. We add .page.jd-parser-page + per-element classes to reach 0-0-61+. */

/* === 1. .page-toolbar 工具栏 === */
body.theme-dark .app-main:not(.app-main--dashboard) .page.jd-parser-page .page-toolbar,
body:not(.login-active) .app-main .page.jd-parser-page .page-toolbar {
  border: 1px solid rgba(78, 200, 255, 0.18) !important;
  border-radius: 13px !important;
  padding: 12px 16px !important;
  background: rgba(8, 42, 92, 0.35) !important;
  box-shadow:
    inset 0 1px 0 rgba(161, 231, 255, 0.08),
    0 8px 32px rgba(0, 10, 40, 0.25) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  animation: none !important;
}
body.theme-dark .app-main:not(.app-main--dashboard) .page.jd-parser-page .page-toolbar::before,
body:not(.login-active) .app-main .page.jd-parser-page .page-toolbar::before {
  display: none !important;
}

/* === 2. .panel.span-5 输入区 === */
body.theme-dark .app-main:not(.app-main--dashboard) .page.jd-parser-page .panel.span-5,
body:not(.login-active) .app-main .page.jd-parser-page .panel.span-5 {
  border: 1px solid rgba(78, 200, 255, 0.18) !important;
  border-radius: 13px !important;
  background: rgba(8, 42, 92, 0.35) !important;
  box-shadow:
    inset 0 1px 0 rgba(161, 231, 255, 0.08),
    0 8px 32px rgba(0, 10, 40, 0.25) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  animation: none !important;
}
body.theme-dark .app-main:not(.app-main--dashboard) .page.jd-parser-page .panel.span-5::before,
body:not(.login-active) .app-main .page.jd-parser-page .panel.span-5::before {
  display: none !important;
}

/* === 3. .panel.span-7 结果展示区 === */
body.theme-dark .app-main:not(.app-main--dashboard) .page.jd-parser-page .panel.span-7,
body:not(.login-active) .app-main .page.jd-parser-page .panel.span-7 {
  border: 1px solid rgba(78, 200, 255, 0.18) !important;
  border-radius: 13px !important;
  background: rgba(8, 42, 92, 0.35) !important;
  box-shadow:
    inset 0 1px 0 rgba(161, 231, 255, 0.08),
    0 8px 32px rgba(0, 10, 40, 0.25) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  animation: none !important;
}
body.theme-dark .app-main:not(.app-main--dashboard) .page.jd-parser-page .panel.span-7::before,
body:not(.login-active) .app-main .page.jd-parser-page .panel.span-7::before {
  display: none !important;
}

/* === 4. section.panel.history-panel 解析历史 === */
body.theme-dark .app-main:not(.app-main--dashboard) .page.jd-parser-page .panel.history-panel,
body:not(.login-active) .app-main .page.jd-parser-page .panel.history-panel {
  margin-top: 18px;
  padding: 20px;
  border: 1px solid rgba(78, 200, 255, 0.18) !important;
  border-radius: 13px !important;
  background: rgba(8, 42, 92, 0.35) !important;
  box-shadow:
    inset 0 1px 0 rgba(161, 231, 255, 0.08),
    0 8px 32px rgba(0, 10, 40, 0.25) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  animation: none !important;
}
body.theme-dark .app-main:not(.app-main--dashboard) .page.jd-parser-page .panel.history-panel::before,
body:not(.login-active) .app-main .page.jd-parser-page .panel.history-panel::before {
  display: none !important;
}

/* === 5. textarea 输入框（theme-fixes 将 .el-textarea__inner 强制 #0a1d2c 实色） === */
body.theme-dark .app-main:not(.app-main--dashboard) .page.jd-parser-page .el-textarea__inner,
body:not(.login-active) .app-main .page.jd-parser-page .el-textarea__inner {
  border: 1px solid rgba(78, 200, 255, 0.18) !important;
  border-radius: 10px !important;
  background: rgba(8, 42, 92, 0.35) !important;
  box-shadow: inset 0 1px 0 rgba(161, 231, 255, 0.08) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: #d6f1ff !important;
}
body.theme-dark .app-main:not(.app-main--dashboard) .page.jd-parser-page .el-textarea__inner::placeholder,
body:not(.login-active) .app-main .page.jd-parser-page .el-textarea__inner::placeholder {
  color: #6f91ad !important;
}
body.theme-dark .app-main:not(.app-main--dashboard) .page.jd-parser-page .el-textarea__inner:focus,
body:not(.login-active) .app-main .page.jd-parser-page .el-textarea__inner:focus {
  border-color: rgba(78, 200, 255, 0.45) !important;
  box-shadow: inset 0 1px 0 rgba(161, 231, 255, 0.08), 0 0 0 3px rgba(54, 215, 255, 0.12) !important;
}
</style>

<style scoped>
.history-panel { margin-top: 18px; padding: 20px; }
.history-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 12px; }
.history-head h3 { margin: 0; color: var(--text); font-size: 17px; }
.history-head p { margin: 5px 0 0; color: var(--muted); font-size: 13px; }
</style>

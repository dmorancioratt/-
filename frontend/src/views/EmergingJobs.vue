<template>
  <div class="page emerging-jobs-page">
    <PageHeader title="新岗位发现" desc="基于技能增长、多源一致性、技能组合新颖度、标题稳定性和场景扩散度计算新岗位指数">
      <div class="toolbar">
        <el-tag v-if="lastUpdated" effect="plain">上次更新 {{ formatTime(lastUpdated) }}</el-tag>
        <el-button type="primary" :loading="loading" @click="generate(true)">
          {{ rows.length ? '更新分析' : '生成分析' }}
        </el-button>
      </div>
    </PageHeader>
    <div class="content-grid">
      <div class="panel span-7">
        <el-table :data="rows" highlight-current-row @current-change="selectCurrent">
          <el-table-column prop="job_name" label="岗位名称" min-width="180" />
          <el-table-column label="新岗位指数" min-width="160">
            <template #default="{ row }"><el-progress :percentage="Math.round(row.emerging_index * 100)" /></template>
          </el-table-column>
          <el-table-column label="关联技能" min-width="220">
            <template #default="{ row }"><el-tag v-for="skill in row.related_skills.slice(0, 3)" :key="skill">{{ skill }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="review_status" label="审核状态" />
        </el-table>
      </div>
      <div class="panel span-5">
        <el-empty v-if="!current" description="选择一个候选岗位查看详情" />
        <template v-else>
          <h3>{{ current.job_name }}</h3>
          <p>{{ current.definition }}</p>
          <el-divider />
          <h4>核心职责</h4>
          <ul><li v-for="item in current.responsibilities" :key="item">{{ item }}</li></ul>
          <h4>必备技能</h4>
          <div class="tag-list"><el-tag v-for="item in current.required_skills" :key="item">{{ item }}</el-tag></div>
          <h4>应用场景</h4>
          <div class="tag-list"><el-tag v-for="item in current.scenarios" :key="item" type="info">{{ item }}</el-tag></div>
          <h4>建议证书</h4>
          <div class="tag-list">
            <el-tag v-for="item in current.requirements?.recommended_certificates || []" :key="item.id" type="warning" effect="light">{{ item.name }}</el-tag>
            <span v-if="!current.requirements?.recommended_certificates?.length">暂无明确证书建议</span>
          </div>
          <h4>证据来源</h4>
          <el-alert v-for="item in current.evidence" :key="item.quote" :title="item.quote" :description="item.source" type="info" :closable="false" />
          <div class="detail-actions">
            <el-button :disabled="!current.job_id" @click="openGraph">在能力图谱中查看</el-button>
            <el-button type="primary" :disabled="!current.job_id" @click="startMatch">用于匹配分析</el-button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'
import { loadPageState, savePageState } from '@/utils/pageState'

type EmergingJobsState = {
  rows: any[]
  currentJobName?: string
  lastUpdated?: string
}

const rows = ref<any[]>([])
const router = useRouter()
const current = ref<any>()
const loading = ref(false)
const lastUpdated = ref<string>()

function persistState() {
  savePageState<EmergingJobsState>('emerging-jobs', {
    rows: rows.value,
    currentJobName: current.value?.job_name,
    lastUpdated: lastUpdated.value
  })
}

function selectCurrent(row?: any) {
  current.value = row
  persistState()
}

function openGraph() {
  if (current.value?.job_id) router.push({ path: '/skill-graph', query: { jobId: String(current.value.job_id) } })
}

function startMatch() {
  if (current.value?.job_id) router.push({ path: '/match-analysis', query: { jobId: String(current.value.job_id) } })
}

async function generate(notify = false) {
  loading.value = true
  try {
    rows.value = await api.emergingJobs()
    current.value = rows.value[0]
    lastUpdated.value = new Date().toISOString()
    persistState()
    if (notify) ElMessage.success('新岗位分析已更新')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '新岗位分析生成失败')
  } finally {
    loading.value = false
  }
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'
  }).format(new Date(value))
}

onMounted(async () => {
  const cached = loadPageState<EmergingJobsState>('emerging-jobs')
  const cacheMatchesCatalog = cached?.rows?.length && cached.rows.every((item) => item.job_id && item.requirements && item.authority)
  if (cacheMatchesCatalog) {
    rows.value = cached.rows
    lastUpdated.value = cached.lastUpdated
    current.value = rows.value.find((item) => item.job_name === cached.currentJobName) || rows.value[0]
    return
  }
  await generate()
})
</script>

<style>
/* Unscoped glass overrides — specificity must beat theme-fixes.css (loaded after page styles).
   theme-fixes: body.theme-dark .app-main:not(.app-main--dashboard) :is(.panel,.page-toolbar,...) { background:#0a1c2b!important; box-shadow:none!important }
   styles.css:  body:not(.login-active) .app-main :is(.panel,.page-toolbar,...) { background:linear-gradient(...)!important }
   Both ≈ 0-0-41. We add .page.emerging-jobs-page + per-element classes to reach 0-0-61+. */

/* === 1. .page-toolbar 工具栏（生成分析按钮容器） === */
body.theme-dark .app-main:not(.app-main--dashboard) .page.emerging-jobs-page .page-toolbar,
body:not(.login-active) .app-main .page.emerging-jobs-page .page-toolbar {
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
body.theme-dark .app-main:not(.app-main--dashboard) .page.emerging-jobs-page .page-toolbar::before,
body:not(.login-active) .app-main .page.emerging-jobs-page .page-toolbar::before {
  display: none !important;
}

/* === 2. .panel.span-7 表格区 === */
body.theme-dark .app-main:not(.app-main--dashboard) .page.emerging-jobs-page .panel.span-7,
body:not(.login-active) .app-main .page.emerging-jobs-page .panel.span-7 {
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
body.theme-dark .app-main:not(.app-main--dashboard) .page.emerging-jobs-page .panel.span-7::before,
body:not(.login-active) .app-main .page.emerging-jobs-page .panel.span-7::before {
  display: none !important;
}

/* === 3. .panel.span-5 详情区 === */
body.theme-dark .app-main:not(.app-main--dashboard) .page.emerging-jobs-page .panel.span-5,
body:not(.login-active) .app-main .page.emerging-jobs-page .panel.span-5 {
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
body.theme-dark .app-main:not(.app-main--dashboard) .page.emerging-jobs-page .panel.span-5::before,
body:not(.login-active) .app-main .page.emerging-jobs-page .panel.span-5::before {
  display: none !important;
}
</style>

<style scoped>
.detail-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 18px; }
</style>

<template>
  <div class="page">
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
          <h4>证据来源</h4>
          <el-alert v-for="item in current.evidence" :key="item.quote" :title="item.quote" :description="item.source" type="info" :closable="false" />
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
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
  if (cached?.rows?.length) {
    rows.value = cached.rows
    lastUpdated.value = cached.lastUpdated
    current.value = rows.value.find((item) => item.job_name === cached.currentJobName) || rows.value[0]
    return
  }
  await generate()
})
</script>

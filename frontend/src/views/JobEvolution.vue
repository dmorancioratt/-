<template>
  <div class="page job-evolution-page">
    <PageHeader title="岗位能力更新" desc="按能力演化统一口径查看岗位版本、能力增删调整和迭代趋势">
      <el-select v-model="jobId" placeholder="选择有版本记录的岗位" class="job-select">
        <el-option v-for="job in jobOptions" :key="job.id" :label="`${job.name} · ${job.domain}`" :value="job.id" />
      </el-select>
      <el-button type="primary" :loading="loading" @click="loadEvolution">刷新数据</el-button>
    </PageHeader>

    <EvolutionViews
      v-if="selectedCards.length"
      :key="jobId"
      mode="version"
      :hotspot="emptyHotspot"
      :compare="emptyCompare"
      :cards="selectedCards"
    />
    <section v-else class="empty-panel">
      <b>{{ loading ? '正在读取岗位版本记录' : '暂无可展示的岗位能力版本' }}</b>
      <span>{{ loading ? '请稍候' : '岗位发生能力更新或数据源迭代后，会在这里形成版本对比。' }}</span>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import EvolutionViews from '@/components/EvolutionViews.vue'
import { api } from '@/api/http'

const loading = ref(false)
const jobId = ref<number>()
const versionCards = ref<any[]>([])
const emptyHotspot = { rising: [], declining: [], emerging: [] }
const emptyCompare = { categories: [], domains: [], matrix: [] }

const jobOptions = computed(() => {
  const seen = new Set<number>()
  return versionCards.value.reduce((result: any[], card: any) => {
    if (!card.jobId || seen.has(card.jobId)) return result
    seen.add(card.jobId)
    result.push({ id: card.jobId, name: card.jobName || `岗位 ${card.jobId}`, domain: card.domain || '其他' })
    return result
  }, [])
})

const selectedCards = computed(() => versionCards.value.filter((card) => card.jobId === jobId.value))

async function loadEvolution() {
  loading.value = true
  try {
    const payload = await api.evolutionVersionCompare()
    versionCards.value = Array.isArray(payload?.cards) ? payload.cards : []
    if (!jobOptions.value.some((job) => job.id === jobId.value)) jobId.value = jobOptions.value[0]?.id
  } finally {
    loading.value = false
  }
}

onMounted(loadEvolution)
</script>

<style scoped>
.job-evolution-page { min-width: 0; overflow-x: clip; }
.job-select { width: min(360px, 42vw); }
.empty-panel { display: grid; min-height: 420px; place-items: center; align-content: center; gap: 8px; border: 1px solid rgba(82, 221, 255, .16); border-radius: 8px; color: #79aabd; background: rgba(3, 22, 36, .66); }
.empty-panel b { color: #dffaff; font-size: 16px; }.empty-panel span { font-size: 12px; }
@media (max-width: 700px) { .job-select { width: 100%; } }
</style>

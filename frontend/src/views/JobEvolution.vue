<template>
  <div class="page">
    <PageHeader title="岗位能力更新" desc="选择岗位后查看新增、删除、修改技能和版本记录">
      <el-select v-model="jobId" placeholder="选择岗位" style="width: 260px" @change="loadEvolution">
        <el-option v-for="job in jobs" :key="job.id" :label="job.name" :value="job.id" />
      </el-select>
    </PageHeader>
    <div class="content-grid">
      <div class="panel span-6">
        <h3>技能变化</h3>
        <el-table :data="changeRows">
          <el-table-column prop="type" label="类型" width="120" />
          <el-table-column prop="skill" label="技能/说明" />
        </el-table>
      </div>
      <div class="panel span-6">
        <h3>版本记录</h3>
        <el-timeline>
          <el-timeline-item v-for="item in evolution?.timeline || []" :key="item.time" :timestamp="String(item.time)">
            {{ item.content }}
          </el-timeline-item>
        </el-timeline>
        <el-alert v-if="evolution" :title="evolution.update_note" :description="`证据：${evolution.evidence}`" type="info" :closable="false" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'

const jobs = ref<any[]>([])
const jobId = ref<number>()
const evolution = ref<any>()
const changeRows = computed(() => {
  if (!evolution.value) return []
  return [
    ...evolution.value.added_skills.map((skill: string) => ({ type: '新增技能', skill })),
    ...evolution.value.removed_skills.map((skill: string) => ({ type: '删除技能', skill })),
    ...evolution.value.modified_skills.map((skill: any) => ({ type: '修改技能', skill: typeof skill === 'string' ? skill : `${skill.skill}：${skill.change}` }))
  ]
})

async function loadEvolution() {
  if (!jobId.value) return
  evolution.value = await api.jobEvolution(jobId.value)
}

onMounted(async () => {
  jobs.value = await api.jobs()
  jobId.value = jobs.value[0]?.id
  await loadEvolution()
})
</script>

<style scoped>
.panel {
  border-color: rgba(105, 213, 255, 0.3) !important;
  background:
    radial-gradient(circle at 88% 4%, rgba(44, 194, 255, 0.16), transparent 32%),
    linear-gradient(145deg, rgba(7, 38, 91, 0.82), rgba(3, 20, 58, 0.74)) !important;
  box-shadow: inset 0 1px 0 rgba(180, 240, 255, 0.1), 0 20px 44px rgba(0, 5, 28, 0.2);
}

.panel :deep(.el-table),
.panel :deep(.el-table__inner-wrapper),
.panel :deep(.el-table tr),
.panel :deep(.el-table td.el-table__cell) {
  color: #dff5ff !important;
  background: rgba(4, 27, 70, 0.58) !important;
}

.panel :deep(.el-table th.el-table__cell) {
  color: #a7e8ff !important;
  background: rgba(13, 66, 131, 0.7) !important;
}

.panel :deep(.el-table__row:hover > td.el-table__cell) {
  background: rgba(21, 109, 180, 0.42) !important;
}

.panel :deep(.el-table__inner-wrapper::before),
.panel :deep(.el-table--border::after),
.panel :deep(.el-table--group::after),
.panel :deep(.el-table::before) {
  background-color: rgba(105, 213, 255, 0.24) !important;
}

.panel :deep(.el-timeline-item__tail) {
  border-left-color: rgba(82, 213, 255, 0.45);
}

.panel :deep(.el-timeline-item__node) {
  background-color: #58ddff;
  box-shadow: 0 0 12px rgba(88, 221, 255, 0.8);
}

.panel :deep(.el-timeline-item__timestamp) {
  color: #86c9ed;
}

.panel :deep(.el-timeline-item__content) {
  color: #e4f7ff;
}

.panel :deep(.el-alert) {
  border: 1px solid rgba(98, 213, 255, 0.34) !important;
  color: #dff5ff !important;
  background: linear-gradient(135deg, rgba(11, 73, 137, 0.72), rgba(4, 34, 84, 0.88)) !important;
  box-shadow: inset 0 1px 0 rgba(184, 242, 255, 0.1);
}

.panel :deep(.el-alert__title) {
  color: #effbff !important;
  font-weight: 800;
}

.panel :deep(.el-alert__description) {
  color: #a8d9f5 !important;
}
</style>

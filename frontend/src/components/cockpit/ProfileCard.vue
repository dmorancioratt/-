<template>
  <section class="cc-profile cc-glass cc-reveal" aria-label="个人成长档案">
    <div class="cc-profile-main">
      <div class="cc-avatar"><span>张</span></div>
      <div><div class="cc-name-row"><h2>{{ student.name }}</h2><span>{{ student.level }}</span></div><p>目标岗位：{{ student.role }}</p><p class="cc-profile-stage">当前阶段 · 能力进阶期</p></div>
    </div>
    <div class="cc-growth-orbit"><div class="cc-growth-inner"><small>成长指数</small><strong>{{ displayGrowth }}</strong><span>/100</span><em>↑</em></div></div>
    <div class="cc-profile-metrics">
      <div v-for="metric in metrics" :key="metric.label"><small>{{ metric.label }}</small><strong>{{ metric.value }}</strong><span>{{ metric.unit }}</span></div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
const props = defineProps<{ student: { name: string; level: string; role: string; growth: number; days: number; hours: number; skills: number; projects: number } }>()
const current = ref(0)
onMounted(() => { const id = window.setInterval(() => { current.value += 1; if (current.value >= props.student.growth) window.clearInterval(id) }, 18) })
const displayGrowth = computed(() => String(current.value).padStart(2, '0'))
const metrics = computed(() => [
  { label: '成长里程', value: props.student.days, unit: '天' }, { label: '学习时长', value: props.student.hours, unit: 'h' },
  { label: '掌握技能', value: props.student.skills, unit: '项' }, { label: '项目经验', value: props.student.projects, unit: '个' }
])
</script>

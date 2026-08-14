<template>
  <component :is="dashboardComponent" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import CandidateDashboard from '@/views/dashboards/CandidateDashboard.vue'
import HrDashboard from '@/views/dashboards/HrDashboard.vue'
import AdminDashboard from '@/views/dashboards/AdminDashboard.vue'

const auth = useAuthStore()
const dashboardComponent = computed(() => {
  if (auth.role === 'admin') return AdminDashboard
  if (auth.role === 'hr') return HrDashboard
  return CandidateDashboard
})
</script>

<style>
html body.theme-dark .app-main .cockpit {
  background: transparent !important;
}
html body.theme-dark .app-main .app-titlebar {
  background: rgba(8, 35, 80, 0.6) !important;
  backdrop-filter: blur(10px) !important;
}
</style>

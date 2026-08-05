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

<template>
  <div class="step-list">
    <div v-for="(it, i) in items" :key="i" class="step-list-row">
      <span class="step-list-label">{{ it.label }}</span>
      <strong v-if="it.score" class="step-list-score">{{ it.score }}</strong>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ items: { label: string; score?: string }[] }>()
</script>

<style scoped>
.step-list { font-size: 10px; color: #cbd5e1; line-height: 1.6; display: flex; flex-direction: column; gap: 3px; }
.step-list-row { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.step-list-label { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.step-list-score { color: #94a3b8; font-family: ui-monospace, Menlo, monospace; flex-shrink: 0; }
</style>
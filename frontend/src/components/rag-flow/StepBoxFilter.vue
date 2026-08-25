<template>
  <div class="step-list">
    <div class="step-list-kept">过滤后保留 {{ kept }} 条 · 丢弃 {{ dropped }} 条</div>
    <div v-for="(it, i) in items" :key="i" class="step-list-text">{{ it }}</div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ kept: number; dropped?: number; items: string[] }>()
</script>

<style scoped>
.step-list { font-size: 10px; color: #cbd5e1; line-height: 1.6; display: flex; flex-direction: column; gap: 3px; }
.step-list-kept { font-weight: 700; color: #fbbf24; margin-bottom: 2px; }
.step-list-text { color: #cbd5e1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>
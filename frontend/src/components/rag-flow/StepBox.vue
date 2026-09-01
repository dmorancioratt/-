<template>
  <div class="step-list">
    <p v-for="(line, i) in lines" :key="i" class="step-quote">{{ line }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{ lines: string[] }>()
</script>

<style scoped>
.step-list { font-size: 10px; color: #cbd5e1; line-height: 1.6; display: flex; flex-direction: column; gap: 3px; }
.step-quote { font-size: 11px; color: #cbd5e1; line-height: 1.45; margin: 0; }
</style>
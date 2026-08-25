<template>
  <div class="step-list step-list-block">
    <p v-for="(line, i) in lines" :key="i" class="step-list-text">{{ line }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{ lines: string[] }>()
</script>

<style scoped>
.step-list { font-size: 10px; color: #cbd5e1; line-height: 1.6; display: flex; flex-direction: column; gap: 3px; }
.step-list-block { gap: 4px; }
.step-list-text { color: #cbd5e1; margin: 0; line-height: 1.5; }
</style>
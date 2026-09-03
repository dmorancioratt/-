<template>
  <div class="cfg-form">
    <p class="hint">最终回答节点用于向用户呈现完整 RAG 输出，无需额外配置。</p>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ node: any }>()
</script>

<style scoped>
.hint { font-size: 12px; color: #94a3b8; line-height: 1.6; margin: 0; }
</style>
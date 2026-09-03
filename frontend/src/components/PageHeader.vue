<template>
  <div v-if="$slots.default" class="page-toolbar page-toolbar--bare" aria-label="页面快捷操作">
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; desc?: string }>()
</script>

<style scoped>
.page-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  margin: -2px 0 16px;
  min-height: 40px;
}

.page-toolbar :deep(.el-button--primary) {
  border: 0;
  border-radius: 13px;
  background: linear-gradient(135deg, #0aa9b4, #0aa9b4);
  box-shadow: 0 10px 22px rgba(30, 123, 255, 0.2);
  font-weight: 850;
}

@media (max-width: 900px) {
  .page-toolbar {
    justify-content: flex-start;
  }
}
</style>

<style>
html body #app .app-main .page .page-toolbar.page-toolbar--bare {
  min-height: 0;
  border: 0 !important;
  padding: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
  animation: none !important;
}

html body #app .app-main .page .page-toolbar.page-toolbar--bare::before,
html body #app .app-main .page .page-toolbar.page-toolbar--bare::after {
  display: none !important;
  content: none !important;
}
</style>

<template>
  <div v-if="$slots.default" class="page-toolbar" aria-label="页面快捷操作">
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
  background: linear-gradient(135deg, #1e7bff, #00bdeb);
  box-shadow: 0 10px 22px rgba(30, 123, 255, 0.2);
  font-weight: 850;
}

@media (max-width: 900px) {
  .page-toolbar {
    justify-content: flex-start;
  }
}
</style>

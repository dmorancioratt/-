<template>
  <BaseNode v-bind="$attrs" :data="data" :selected="selected" @node-click="$emit('node-click', id)" />
</template>

<script setup lang="ts">
import BaseNode from './BaseNode.vue'
defineProps<{
  id: string
  data: { kind: 'knowledge'; label: string; description?: string; status: string; output?: string; config: Record<string, any> }
  selected?: boolean
}>()
defineEmits<{ (e: 'node-click', id: string): void }>()
</script>

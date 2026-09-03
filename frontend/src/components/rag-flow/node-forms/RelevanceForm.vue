<template>
  <div class="cfg-form">
    <label>相关性阈值</label>
    <el-slider v-model="localCfg.threshold" :min="0" :max="1" :step="0.05" show-input />
    <p class="hint">低于此分数的检索结果会被丢弃。</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{ node: any }>()
const emit = defineEmits<{ (e: 'patch', patch: any): void }>()
const localCfg = computed({
  get: () => props.node.data.config,
  set: (v) => emit('patch', v),
})
</script>

<style scoped>
.cfg-form { display: flex; flex-direction: column; gap: 12px; }
label { font-size: 12px; color: #cbd5e1; }
.hint { font-size: 11px; color: #94a3b8; line-height: 1.5; }
</style>
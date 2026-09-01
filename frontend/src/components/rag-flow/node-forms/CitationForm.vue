<template>
  <div class="cfg-form">
    <label>最少引用数</label>
    <el-input-number v-model="localCfg.min_sources" :min="0" :max="10" />
    <p class="hint">答案附带的来源数。少于该值会触发引用校验失败。</p>
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
<template>
  <div class="cfg-form">
    <label>chunk_size</label>
    <el-input-number v-model="localCfg.chunk_size" :min="50" :max="2000" :step="50" />
    <label>chunk_overlap</label>
    <el-input-number v-model="localCfg.chunk_overlap" :min="0" :max="500" :step="10" />
    <p class="hint">文档切片参数。新上传的文档会用此参数切分。</p>
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
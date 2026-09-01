<template>
  <div class="cfg-form">
    <label>模型</label>
    <el-select v-model="localCfg.model" style="width:100%">
      <el-option label="deepseek-v4-flash" value="deepseek-v4-flash" />
      <el-option label="deepseek-v4" value="deepseek-v4" />
      <el-option label="qwen-max" value="qwen-max" />
      <el-option label="gpt-4o-mini" value="gpt-4o-mini" />
    </el-select>
    <label>temperature</label>
    <el-slider v-model="localCfg.temperature" :min="0" :max="2" :step="0.05" show-input />
    <label>max_tokens</label>
    <el-input-number v-model="localCfg.max_tokens" :min="64" :max="4096" :step="64" />
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
</style>
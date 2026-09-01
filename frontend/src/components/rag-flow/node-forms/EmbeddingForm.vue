<template>
  <div class="cfg-form">
    <label>Embedding 模型</label>
    <el-select v-model="localCfg.model" style="width:100%">
      <el-option label="BGE-small-zh（中文）" value="bge-small-zh" />
      <el-option label="text-embedding-3-small" value="text-embedding-3-small" />
      <el-option label="Fake（测试）" value="fake" />
    </el-select>
    <label>向量维度</label>
    <el-input-number v-model="localCfg.dim" :min="64" :max="3072" :step="64" />
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
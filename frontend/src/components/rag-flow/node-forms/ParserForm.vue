<template>
  <div class="cfg-form">
    <label>解析方法</label>
    <el-select v-model="localCfg.method" style="width:100%">
      <el-option label="规则解析" value="rule" />
      <el-option label="LLM 解析" value="llm" />
    </el-select>
    <label>超时 (ms)</label>
    <el-input-number v-model="localCfg.timeout_ms" :min="100" :max="5000" :step="100" />
    <p class="hint">问题解析节点负责意图识别与实体抽取。</p>
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
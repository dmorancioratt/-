<template>
  <div class="cfg-form">
    <label>占位提示</label>
    <el-input v-model="localCfg.placeholder" placeholder="输入用户问句的占位说明" />
    <p class="hint">用户问题节点作为工作流入口，可在测试运行时输入具体问题。</p>
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
label { font-size: 12px; color: #cbd5e1; margin-bottom: 4px; display: block; }
.hint { font-size: 11px; color: #94a3b8; margin: 0; line-height: 1.5; }
</style>
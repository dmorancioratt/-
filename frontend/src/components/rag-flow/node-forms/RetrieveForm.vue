<template>
  <div class="cfg-form">
    <label>top_k</label>
    <el-slider v-model="localCfg.top_k" :min="1" :max="20" show-input />
    <p class="hint">相似度召回数。Top-K 检索节点从向量库取最相似的 K 条。</p>
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
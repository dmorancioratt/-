<template>
  <div class="cfg-form">
    <label>索引路径</label>
    <el-input v-model="localCfg.index_path" />
    <label>相似度</label>
    <el-select v-model="localCfg.metric" style="width:100%">
      <el-option label="余弦" value="cosine" />
      <el-option label="内积" value="ip" />
    </el-select>
    <p class="hint">本地向量库固定走 faiss-cpu + 归一化内积。</p>
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
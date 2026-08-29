<template>
  <div class="cfg-form">
    <label>Top-K 数量</label>
    <el-slider v-model="localCfg.top_k" :min="1" :max="20" show-input size="small" />

    <label>相似度阈值</label>
    <el-slider v-model="localCfg.threshold" :min="0" :max="1" :step="0.01" show-input size="small" />

    <label>最大候选数</label>
    <el-slider v-model="localCfg.max_candidates" :min="1" :max="50" show-input size="small" />

    <label>检索策略</label>
    <el-select v-model="localCfg.strategy" size="default" class="full-width">
      <el-option label="余弦相似度" value="cosine" />
      <el-option label="点积" value="dot_product" />
      <el-option label="欧氏距离" value="euclidean" />
    </el-select>

    <div class="divider" />

    <div class="subsection-title">过滤条件</div>
    <div class="filter-list">
      <div v-for="(f, i) in filters" :key="i" class="filter-item">
        <el-select v-model="f.field" size="small" class="filter-field">
          <el-option label="来源" value="source" />
          <el-option label="类型" value="type" />
          <el-option label="标签" value="tag" />
        </el-select>
        <el-select v-model="f.op" size="small" class="filter-op">
          <el-option label="等于" value="eq" />
          <el-option label="包含" value="contains" />
          <el-option label="大于" value="gt" />
        </el-select>
        <el-input v-model="f.value" size="small" class="filter-value" />
        <el-button text size="small" @click="filters.splice(i, 1)">
          <el-icon><Delete /></el-icon>
        </el-button>
      </div>
    </div>
    <el-button plain size="small" @click="addFilter">+ 添加过滤条件</el-button>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive } from 'vue'
import { Delete } from '@element-plus/icons-vue'

const props = defineProps<{ node: any }>()
const emit = defineEmits<{ (e: 'patch', patch: any): void }>()

const localCfg = computed({
  get: () => ({
    top_k: props.node.data.config?.top_k ?? 5,
    threshold: props.node.data.config?.threshold ?? 0.7,
    max_candidates: props.node.data.config?.max_candidates ?? 20,
    strategy: props.node.data.config?.strategy ?? 'cosine',
    ...props.node.data.config,
  }),
  set: (v) => emit('patch', v),
})

const filters = reactive<any[]>([])

function addFilter() {
  filters.push({ field: 'source', op: 'eq', value: '' })
}
</script>

<style scoped>
.cfg-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

label {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 500;
}

.full-width {
  width: 100%;
}

.divider {
  height: 1px;
  background: rgba(91, 155, 213, 0.12);
  margin: 4px 0;
}

.subsection-title {
  font-size: 12px;
  color: #64748b;
  font-weight: 600;
  margin-top: 4px;
}

.filter-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.filter-field,
.filter-op {
  width: 80px;
}

.filter-value {
  flex: 1;
}

:deep(.el-slider) {
  --el-slider-button-size: 12px;
}

:deep(.el-slider__runway) {
  height: 4px;
}
</style>

<template>
  <div class="step-list">
    <div class="step-list-check ok"><span class="check-dot"></span>幻觉检测：通过</div>
    <div class="step-list-check ok"><span class="check-dot"></span>相关性评分：4.7 / 5</div>
    <div class="step-list-check ok"><span class="check-dot"></span>事实一致性：92.3%</div>
    <div class="step-list-meta">综合评分 4.7 / 5 · 通过可信认证</div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.check-dot {
  width: 6px; height: 6px; border-radius: 999px;
  background: #34d399;
  display: inline-block;
  box-shadow: 0 0 6px rgba(52,211,153,0.55);
}
.step-list-meta {
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px dashed rgba(148,163,184,0.18);
  color: #94a3b8;
  font-size: 10px;
}
</style>
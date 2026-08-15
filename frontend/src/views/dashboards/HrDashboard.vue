<template>
  <div class="cockpit hr-dashboard hr-dashboard--empty">
    <header class="empty-hero">
      <span class="empty-eyebrow">HR 大屏 · 等待重新设计</span>
      <h1>HR 大屏</h1>
      <p>请在 <code>frontend/src/views/dashboards/HrDashboard.vue</code> 中开始设计此页面。</p>
    </header>
  </div>
</template>

<script setup lang="ts">
// 新 HR 大屏骨架页：等后续设计填充。
</script>

<style scoped>
.hr-dashboard--empty { max-width: 1680px; margin: 0 auto; min-height: 60vh; display: flex; align-items: center; justify-content: center; }
.empty-hero { border: 1px dashed rgba(71, 191, 255, .28); border-radius: 12px; padding: 36px 48px; background: rgba(5, 23, 52, .55); text-align: center; max-width: 640px; }
.empty-eyebrow { display: block; color: #65daf4; font-size: 12px; font-weight: 700; letter-spacing: .04em; margin-bottom: 8px; }
.empty-hero h1 { margin: 0 0 10px; color: #f0fbff; font-size: 28px; }
.empty-hero p { margin: 0; color: #89a9bf; font-size: 13px; line-height: 1.6; }
.empty-hero code { padding: 1px 6px; border-radius: 4px; background: rgba(15, 68, 112, .45); color: #c2dceb; font-size: 12px; }
</style>
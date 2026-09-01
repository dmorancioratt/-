<template>
  <header class="cc-header">
    <a class="cc-brand" href="#top" aria-label="数融智联首页">
      <span class="cc-brand-mark"><i></i><b></b></span>
      <span>数融智联</span>
      <em>SKILLBRIDGE</em>
    </a>
    <nav class="cc-nav" aria-label="主导航">
      <a v-for="item in navItems" :key="item" :class="{ active: item === '首页' }" href="#top">{{ item }}</a>
    </nav>
    <div class="cc-header-actions">
      <label class="cc-search"><span>⌕</span><input aria-label="搜索岗位、技能或项目" placeholder="搜索岗位 / 技能 / 项目" /></label>
      <button class="cc-icon-button" aria-label="通知">♧<i></i></button>
      <button class="cc-user" type="button"><span class="cc-mini-avatar">张</span><b>张同学</b><small>⌄</small></button>
    </div>
  </header>
</template>

<script setup lang="ts">
const navItems = ['首页', '能力图谱', '学习路径', '项目实践', '成长记录', '资源中心']
</script>


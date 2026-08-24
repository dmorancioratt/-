<template>
  <aside class="cc-column cc-left-column">
    <section class="cc-glass cc-panel cc-match cc-reveal"><div class="cc-panel-title"><h3>岗位匹配度</h3><span>↗</span></div><div class="cc-match-body"><div class="cc-ring"><div><strong>{{ match.score }}</strong><span>%</span><small>匹配度</small></div></div><div><small>目标岗位</small><h4>AI算法工程师</h4><button>重新评估</button></div></div><p class="cc-up">↑ 较上次提升 <b>+{{ match.change }}%</b></p></section>
    <section class="cc-glass cc-panel cc-skill-galaxy cc-reveal"><div class="cc-panel-title"><h3>能力概览</h3><span>360°</span></div><svg viewBox="0 0 240 230" aria-label="能力六边形星图"><g class="cc-galaxy-grid"><polygon points="120,28 196,72 196,158 120,202 44,158 44,72"/><polygon points="120,58 170,87 170,143 120,172 70,143 70,87"/><path d="M120 28V202M44 72L196 158M196 72L44 158"/></g><polygon class="cc-galaxy-data" points="120,52 175,82 158,151 120,182 69,150 61,91"/><g class="cc-galaxy-points"><circle cx="120" cy="52" r="4"/><circle cx="175" cy="82" r="4"/><circle cx="158" cy="151" r="4"/><circle cx="120" cy="182" r="4"/><circle cx="69" cy="150" r="4"/><circle cx="61" cy="91" r="4"/></g><g class="cc-galaxy-label"><text x="120" y="17">学习能力 90</text><text x="206" y="73">工程能力 70</text><text x="198" y="167">算法能力 80</text><text x="120" y="223">业务理解 58</text><text x="0" y="167">沟通协作 60</text><text x="0" y="73">创新能力 75</text></g></svg><div class="cc-galaxy-legend"><span><i></i>当前水平</span><span><i></i>岗位要求</span></div></section>
    <section class="cc-glass cc-panel cc-jobs cc-reveal"><div class="cc-panel-title"><h3>推荐岗位</h3><a href="#road">更多 →</a></div><button v-for="job in jobs" :key="job.name" class="cc-job"><span>{{ job.rank }}</span><div><b>{{ job.name }}</b><small>{{ job.company }} · {{ job.salary }}</small></div><strong>{{ job.score }}<em>%</em></strong></button><button class="cc-all-jobs">查看全部岗位　→</button></section>
  </aside>
</template>

<script setup lang="ts">
defineProps<{ match: { score: number; change: number }; jobs: Array<{ rank: number; name: string; company: string; salary: string; score: number }> }>()
</script>

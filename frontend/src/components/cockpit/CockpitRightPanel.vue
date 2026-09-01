<template>
  <aside class="cc-column cc-right-column">
    <section class="cc-glass cc-panel cc-ai-card cc-reveal"><div class="cc-panel-title"><h3>下一步行动</h3><span class="cc-ai-badge">AI 推荐</span></div><div class="cc-ai-topic"><span>◇</span><div><b>深入学习 RAG 知识库构建</b><small>掌握检索增强生成核心技术</small></div><i>›</i></div><button class="cc-learn-btn" @click="$emit('openRag')">开始学习　→</button></section>
    <section class="cc-glass cc-panel cc-week-plan cc-reveal"><div class="cc-panel-title"><h3>本周成长计划</h3><strong>{{ doneCount }}/{{ plan.length }}</strong></div><div class="cc-plan-bar"><i :style="{width: `${doneCount / plan.length * 100}%`}"></i></div><button v-for="item in plan" :key="item.id" class="cc-plan-item" :class="{ done: item.done }" @click="$emit('togglePlan', item.id)"><i>{{ item.done ? '✓' : '' }}</i><span>{{ item.label }}</span></button></section>
    <section class="cc-glass cc-panel cc-interview cc-reveal"><div class="cc-panel-title"><h3>模拟面试</h3><a href="#road">去练习　›</a></div><div class="cc-interview-score"><strong>78</strong><span>/100</span><em>良好</em><svg viewBox="0 0 170 52"><path d="M0 45 C15 39 25 12 42 27 S70 45 89 35 S114 18 130 34 S150 17 170 3 V52 H0Z"/></svg></div><div class="cc-interview-stats"><div><span>技术能力</span><b>72</b></div><div><span>工程能力</span><b>75</b></div><div><span>沟通表达</span><b>83</b></div><div><span>问题解决</span><b>82</b></div></div></section>
    <section class="cc-glass cc-panel cc-timeline cc-reveal"><div class="cc-panel-title"><h3>成长时间线</h3><a href="#road">更多　›</a></div><ol><li v-for="event in timeline" :key="event.date"><span>{{ event.date }}</span><p>{{ event.text }}</p></li></ol></section>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{ plan: Array<{ id: string; label: string; done: boolean }>; timeline: Array<{ date: string; text: string }> }>()
const doneCount = computed(() => props.plan.filter(item => item.done).length)
defineEmits<{ openRag: []; togglePlan: [id: string] }>()
</script>

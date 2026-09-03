<template>
  <section class="cc-road" aria-label="AI 职业成长高速公路">
    <div class="cc-road-title"><span>◌ AI NAVIGATION</span><strong>AI 推荐路径</strong><i></i></div>
    <svg class="cc-road-svg" viewBox="0 0 1000 600" preserveAspectRatio="none" aria-hidden="true">
      <defs><linearGradient id="road" x1="0" x2="1"><stop stop-color="#1e90ff"/><stop offset=".46" stop-color="#48dbff"/><stop offset=".8" stop-color="#7c69ff"/><stop offset="1" stop-color="#b8a4ff"/></linearGradient><filter id="roadGlow"><feGaussianBlur stdDeviation="6" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
      <path d="M 155,615 C 180,470 375,470 420,345 C 460,235 585,315 600,190 C 613,99 760,160 850,26" class="cc-road-shadow"/>
      <path d="M 155,615 C 180,470 375,470 420,345 C 460,235 585,315 600,190 C 613,99 760,160 850,26" class="cc-road-line" filter="url(#roadGlow)"/>
      <path d="M 155,615 C 180,470 375,470 420,345 C 460,235 585,315 600,190 C 613,99 760,160 850,26" class="cc-road-dash"/>
      <path d="M 144,615 C 170,470 365,470 410,345 C 450,235 575,315 590,190 C 603,99 750,160 840,26" class="cc-road-edge"/>
      <path d="M 166,615 C 191,470 385,470 430,345 C 470,235 595,315 610,190 C 623,99 770,160 860,26" class="cc-road-edge"/>
    </svg>
    <button v-for="node in nodes" :key="node.id" class="cc-road-node" :class="node.state" :style="{ left: `${node.x}%`, top: `${node.y}%` }" @click="$emit('select', node.label)">
      <span class="cc-node-orbit"></span><span class="cc-node-icon">{{ node.state === 'done' ? '✓' : node.state === 'goal' ? '✦' : node.state === 'active' ? '◈' : '◇' }}</span><b>{{ node.label }}</b><small>{{ node.level }}</small>
    </button>
    <div class="cc-position"><span>⌁</span><p>你在这里</p></div>
    <div class="cc-road-suggestion cc-glass"><span>✦ 下一步建议</span><strong>完成 RAG 知识库项目实战</strong><p>预计提升成长指数 <b>+8–12</b></p><button @click="$emit('select', 'RAG')">去学习 →</button></div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ nodes: Array<{ id: string; label: string; state: string; level: string; x: number; y: number }> }>()
defineEmits<{ select: [name: string] }>()
</script>


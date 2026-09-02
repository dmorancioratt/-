<template>
  <svg class="trophy-svg" viewBox="0 0 120 150" fill="none" aria-hidden="true">
    <defs>
      <linearGradient :id="`${uid}-gold`" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#fff6d8" />
        <stop offset=".45" stop-color="#f7cf6e" />
        <stop offset=".78" stop-color="#d99b2f" />
        <stop offset="1" stop-color="#a86e14" />
      </linearGradient>
      <linearGradient :id="`${uid}-rim`" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#fff3c9" />
        <stop offset=".5" stop-color="#eec258" />
        <stop offset="1" stop-color="#b0791a" />
      </linearGradient>
      <linearGradient :id="`${uid}-base`" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#1a3566" />
        <stop offset="1" stop-color="#081426" />
      </linearGradient>
      <radialGradient :id="`${uid}-core`" cx=".5" cy=".42" r=".62">
        <stop offset="0" stop-color="#f2ffff" />
        <stop offset=".35" stop-color="#8adcff" />
        <stop offset=".75" stop-color="#1f7dff" />
        <stop offset="1" stop-color="#1f7dff" stop-opacity="0" />
      </radialGradient>
    </defs>

    <ellipse cx="60" cy="143" rx="42" ry="6" fill="rgba(90,180,255,.16)" />

    <!-- 经典奖杯 -->
    <g v-if="variant === 'cup'">
      <path d="M28 36C9 36 7 61 27 70" :stroke="`url(#${uid}-rim)`" stroke-width="7" stroke-linecap="round" />
      <path d="M92 36c19 0 21 25 1 34" :stroke="`url(#${uid}-rim)`" stroke-width="7" stroke-linecap="round" />
      <path d="M26 20h68v18c0 24-13 41-34 49-21-8-34-25-34-49V20Z" :fill="`url(#${uid}-gold)`" stroke="#8a5a12" stroke-width=".8" />
      <path d="M32 26h56v12c0 19-10 33-28 40-18-7-28-21-28-40V26Z" fill="rgba(255,255,255,.10)" />
      <circle cx="60" cy="47" r="14" :fill="`url(#${uid}-core)`" opacity=".95" />
      <circle cx="60" cy="47" r="14" stroke="#cdefff" stroke-width="1" opacity=".65" />
      <path d="M55 42l3 5h-6l3-5Zm5 8-1.6 3.4h3.2L65 50Z" fill="#fff" opacity=".9" />
      <path d="M53 87h14l4 18H49l4-18Z" :fill="`url(#${uid}-gold)`" stroke="#8a5a12" stroke-width=".6" />
      <rect x="44" y="103" width="32" height="7" rx="3" :fill="`url(#${uid}-rim)`" />
      <path d="M38 110h44l6 15H32l6-15Z" :fill="`url(#${uid}-base)`" stroke="rgba(140,200,255,.35)" stroke-width="1" />
      <rect x="28" y="125" width="64" height="9" rx="3" :fill="`url(#${uid}-base)`" stroke="rgba(140,200,255,.28)" stroke-width="1" />
      <rect x="25" y="134" width="70" height="6" rx="3" :fill="`url(#${uid}-rim)`" opacity=".92" />
    </g>

    <!-- 星盾奖杯：纯SVG绘制 -->
    <g v-else-if="variant === 'shield'">
      <!-- 顶部丝带飘带 -->
      <path d="M46 14h28l5 10h-5l-3 8H49l-3-8h-5l5-10Z" fill="#2b5cd8" stroke="#1d42a5" stroke-width=".6" />
      <path d="M46 14h5l-3 8h-5l3-8Zm22 0h-5l3 8h5l-3-8Z" fill="rgba(255,255,255,.22)" />
      <!-- 盾牌主体 -->
      <path d="M60 24c16 2 30 6 30 38 0 24-16 40-30 48-14-8-30-24-30-48 0-32 14-36 30-38Z"
            :fill="`url(#${uid}-gold)`" stroke="#8a5a12" stroke-width=".9" />
      <!-- 盾牌高光层 -->
      <path d="M60 24c16 2 30 6 30 38 0 8-2 15-6 22C78 70 68 58 60 58c-8 0-18 12-24 26-4-7-6-14-6-22 0-32 14-36 30-38Z"
            fill="rgba(255,255,255,.12)" />
      <!-- 盾牌内圈描边 -->
      <path d="M60 34c11 1.8 22 5.6 22 28 0 17.6-11.6 29.4-22 35.6C49.6 91.4 38 79.6 38 62c0-22.4 11-26.2 22-28Z"
            fill="none" stroke="#ffe9ad" stroke-width="1.2" opacity=".72" />
      <!-- 中央宝石/徽记 -->
      <circle cx="60" cy="62" r="15" :fill="`url(#${uid}-core)`" opacity=".86" />
      <circle cx="60" cy="62" r="15" stroke="#cdefff" stroke-width="1" opacity=".6" />
      <path d="M60 50l3 9h9l-7.2 5.4 2.8 9.2L60 66l-7.6 7.6 2.8-9.2L48 59h9l3-9Z" fill="#fff" opacity=".95" />
      <!-- 盾牌描边外层辉光 -->
      <path d="M60 24c16 2 30 6 30 38 0 24-16 40-30 48-14-8-30-24-30-48 0-32 14-36 30-38Z"
            fill="none" stroke="#ffe4a5" stroke-width=".4" opacity=".7" />
      <!-- 底座（与其他奖杯统一风格） -->
      <path d="M44 108h32l3 8H41l3-8Z" :fill="`url(#${uid}-base)`" stroke="rgba(140,200,255,.3)" stroke-width="1" />
      <rect x="36" y="116" width="48" height="9" rx="3" :fill="`url(#${uid}-base)`" stroke="rgba(140,200,255,.26)" stroke-width="1" />
      <rect x="32" y="125" width="56" height="6" rx="3" :fill="`url(#${uid}-rim)`" opacity=".92" />
    </g>

    <!-- 星芒奖杯 -->
    <g v-else-if="variant === 'star'">
      <path d="M53 100h14l3 12H50l3-12Z" :fill="`url(#${uid}-gold)`" stroke="#8a5a12" stroke-width=".6" />
      <circle cx="60" cy="60" r="30" :fill="`url(#${uid}-core)`" opacity=".45" />
      <polygon points="60,24 68.5,48.3 94.2,48.9 73.7,64.4 81.2,89.1 60,74.4 38.8,89.1 46.3,64.4 25.8,48.9 51.5,48.3" :fill="`url(#${uid}-gold)`" stroke="#8a5a12" stroke-width="1" />
      <polygon points="60,24 68.5,48.3 94.2,48.9 60,58 25.8,48.9 51.5,48.3" fill="rgba(255,255,255,.16)" />
      <circle cx="60" cy="60" r="9" :fill="`url(#${uid}-core)`" />
      <rect x="42" y="112" width="36" height="10" rx="3" :fill="`url(#${uid}-base)`" stroke="rgba(140,200,255,.3)" stroke-width="1" />
      <rect x="36" y="122" width="48" height="8" rx="3" :fill="`url(#${uid}-base)`" stroke="rgba(140,200,255,.26)" stroke-width="1" />
      <rect x="31" y="130" width="58" height="6" rx="3" :fill="`url(#${uid}-rim)`" opacity=".92" />
    </g>

    <!-- 晶石奖杯 -->
    <g v-else-if="variant === 'gem'">
      <circle cx="60" cy="14" r="5" :stroke="`url(#${uid}-rim)`" stroke-width="3" />
      <ellipse cx="60" cy="66" rx="12" ry="20" :fill="`url(#${uid}-core)`" opacity=".8" />
      <path d="M60 24l30 30-30 52-30-52 30-30Z" :fill="`url(#${uid}-gold)`" stroke="#8a5a12" stroke-width="1" />
      <path d="M30 54h60M60 24L44 54l16 52M60 24l16 30-16 52" stroke="rgba(255,246,210,.75)" stroke-width="1" />
      <path d="M60 24l30 30-30 52" fill="rgba(255,255,255,.08)" />
      <path d="M50 108h20l4 12H46l4-12Z" :fill="`url(#${uid}-base)`" stroke="rgba(140,200,255,.3)" stroke-width="1" />
      <rect x="40" y="120" width="40" height="9" rx="3" :fill="`url(#${uid}-base)`" stroke="rgba(140,200,255,.26)" stroke-width="1" />
      <rect x="34" y="129" width="52" height="6" rx="3" :fill="`url(#${uid}-rim)`" opacity=".92" />
    </g>

    <!-- 勋章奖杯 -->
    <g v-else>
      <path d="M44 12h13l4 32-13-5-4-27Z" fill="#2b5cd8" />
      <path d="M76 12H63l-4 32 13-5 4-27Z" fill="#1f47ad" />
      <path d="M48 14h8l3 24-10-4-1-20Z" fill="rgba(255,255,255,.22)" />
      <circle cx="60" cy="72" r="28" :fill="`url(#${uid}-gold)`" stroke="#8a5a12" stroke-width="1" />
      <circle cx="60" cy="72" r="28" fill="rgba(255,255,255,.06)" />
      <circle cx="60" cy="72" r="20" stroke="#ffe9ad" stroke-width="1.2" opacity=".6" />
      <circle cx="60" cy="72" r="15" :fill="`url(#${uid}-core)`" opacity=".65" />
      <polygon points="60,60 63,68 71.5,68.2 64.8,73.2 67.2,81.4 60,76.6 52.8,81.4 55.2,73.2 48.5,68.2 57,68" :fill="`url(#${uid}-rim)`" stroke="#8a5a12" stroke-width=".6" />
      <rect x="42" y="104" width="36" height="10" rx="3" :fill="`url(#${uid}-base)`" stroke="rgba(140,200,255,.3)" stroke-width="1" />
      <rect x="36" y="114" width="48" height="9" rx="3" :fill="`url(#${uid}-base)`" stroke="rgba(140,200,255,.26)" stroke-width="1" />
      <rect x="31" y="123" width="58" height="6" rx="3" :fill="`url(#${uid}-rim)`" opacity=".92" />
    </g>
  </svg>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ variant?: 'cup' | 'shield' | 'star' | 'gem' | 'medal' }>(), { variant: 'cup' })
const uid = `tw${Math.random().toString(36).slice(2, 9)}`
</script>

<style scoped>
.trophy-svg { display: block; width: 100%; height: auto; }
</style>


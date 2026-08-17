<template>
  <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`">
    <defs>
      <linearGradient :id="gradId" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" :stop-color="color" stop-opacity="1"/>
        <stop offset="100%" :stop-color="lightenColor" stop-opacity="0.8"/>
      </linearGradient>
      <filter :id="glowId" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="3" result="blur"/>
        <feMerge>
          <feMergeNode in="blur"/>
          <feMergeNode in="SourceGraphic"/>
        </feMerge>
      </filter>
    </defs>
    <circle
      v-if="trackColor"
      :cx="c" :cy="c" :r="r"
      fill="none"
      :stroke="trackColor"
      :stroke-width="stroke"
    />
    <circle
      :cx="c" :cy="c" :r="r"
      fill="none"
      :stroke="`url(#${gradId})`"
      :stroke-width="stroke"
      :stroke-dasharray="circumference"
      :stroke-dashoffset="dashOffset"
      stroke-linecap="round"
      :filter="`url(#${glowId})`"
      transform="rotate(-90)"
      :style="{ transformOrigin: `${c}px ${c}px`, transition: 'stroke-dashoffset 1s ease' }"
    />
    <circle v-if="showTick" :cx="c" :cy="c" :r="r - stroke - 3" fill="none" :stroke="color" stroke-opacity="0.2" stroke-width="1" stroke-dasharray="2 4"/>
    <text v-if="showCenter && centerLabel" :x="c" :y="c + centerOffsetY" text-anchor="middle" class="gauge-center" :style="{fontSize: centerFontSize+'px', fill: textColor}">
      {{ centerLabel }}
    </text>
    <text v-if="subLabel" :x="c" :y="c + subOffsetY" text-anchor="middle" class="gauge-sub" :style="{fontSize: subFontSize+'px', fill: subColor}">
      {{ subLabel }}
    </text>
  </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  value: number
  size?: number
  stroke?: number
  color?: string
  trackColor?: string
  centerLabel?: string
  subLabel?: string
  showCenter?: boolean
  showTick?: boolean
  centerScale?: number
  subScale?: number
}>(), {
  size: 80,
  stroke: 4,
  color: '#4fd8ff',
  trackColor: 'rgba(79,216,255,0.1)',
  centerLabel: '',
  subLabel: '',
  showCenter: true,
  showTick: false,
  centerScale: 1,
  subScale: 1
})

const c = computed(() => props.size / 2)
const r = computed(() => (props.size - props.stroke) / 2 - 2)
const circumference = computed(() => 2 * Math.PI * r.value)
const dashOffset = computed(() => circumference.value * (1 - Math.min(100, Math.max(0, props.value)) / 100))
const gradId = computed(() => `g-${props.color.replace('#','')}-${props.size}`)
const glowId = computed(() => `glow-${props.color.replace('#','')}-${props.size}`)

const lightenColor = computed(() => {
  const hex = props.color.replace('#','')
  const r = parseInt(hex.substr(0,2),16)
  const g = parseInt(hex.substr(2,2),16)
  const b = parseInt(hex.substr(4,2),16)
  const lr = Math.min(255, r + 60)
  const lg = Math.min(255, g + 60)
  const lb = Math.min(255, b + 60)
  return `rgb(${lr},${lg},${lb})`
})

const centerFontSize = computed(() => props.size * 0.26 * props.centerScale)
const subFontSize = computed(() => props.size * 0.13 * props.subScale)
const centerOffsetY = computed(() => props.subLabel ? -props.size * 0.04 : props.size * 0.06)
const subOffsetY = computed(() => props.size * 0.18)
const textColor = computed(() => props.color === '#ffffff' ? '#ffffff' : '#e8f6ff')
const subColor = '#79b4d4'
</script>

<style scoped>
.gauge-center {
  font-weight: 900;
  font-family: 'DIN', 'Rajdhani', 'Arial', sans-serif;
}
.gauge-sub {
  font-weight: 500;
  letter-spacing: 0.05em;
}
</style>

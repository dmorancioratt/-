<template>
  <g class="energy-edge" :class="[`energy-edge--${data.status}`, { 'is-active': data.active }]">
    <path :d="path" class="energy-edge__glow" />
    <path :id="pathId" :d="path" class="energy-edge__line" />
    <circle v-if="data.status !== 'missing'" class="energy-edge__pulse" r="2.8">
      <animateMotion :dur="duration" repeatCount="indefinite" rotate="auto">
        <mpath :href="`#${pathId}`" />
      </animateMotion>
    </circle>
  </g>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { getBezierPath, type EdgeProps } from '@vue-flow/core'
import type { EnergyEdgeData } from './talentTreeTypes'

const props = defineProps<EdgeProps<EnergyEdgeData>>()

const path = computed(() => getBezierPath({
  sourceX: props.sourceX,
  sourceY: props.sourceY,
  sourcePosition: props.sourcePosition,
  targetX: props.targetX,
  targetY: props.targetY,
  targetPosition: props.targetPosition,
  curvature: .28,
})[0])
const pathId = computed(() => `energy-path-${props.id.replace(/[^a-zA-Z0-9_-]/g, '-')}`)
const duration = computed(() => `${2.2 + (props.id.length % 5) * .22}s`)
</script>

<style scoped>
.energy-edge { --edge-color: #2e9fff; --edge-rgb: 46, 159, 255; }
.energy-edge--mastered { --edge-color: #43e7d5; --edge-rgb: 67, 231, 213; }
.energy-edge--missing { --edge-color: #9b7341; --edge-rgb: 155, 115, 65; }
.energy-edge__line,
.energy-edge__glow { fill: none; stroke-linecap: round; vector-effect: non-scaling-stroke; }
.energy-edge__glow { stroke: rgba(var(--edge-rgb), .13); stroke-width: 8; }
.energy-edge__line { stroke: rgba(var(--edge-rgb), .58); stroke-width: 1.6; }
.energy-edge__pulse { fill: var(--edge-color); filter: drop-shadow(0 0 5px rgba(var(--edge-rgb), .95)); }
.energy-edge.is-active .energy-edge__glow { stroke: rgba(var(--edge-rgb), .32); stroke-width: 11; }
.energy-edge.is-active .energy-edge__line { stroke: var(--edge-color); stroke-width: 2.4; }
.energy-edge.is-active .energy-edge__pulse { r: 3.8; }
.energy-edge--missing .energy-edge__line { stroke: rgba(var(--edge-rgb), .28); }
.energy-edge--missing .energy-edge__glow { opacity: .28; }
@media (prefers-reduced-motion: reduce) { .energy-edge__pulse { display: none; } }
</style>

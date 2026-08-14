<template>
  <div class="galaxy-container">
    <canvas ref="canvasRef" class="galaxy-canvas"></canvas>
    <div class="galaxy-filters">
      <span v-for="f in filterOptions" :key="f.key"
        class="galaxy-filter" :class="{active: filter.status === f.key}"
        @click="$emit('filterChange', { ...filter, status: f.key })">{{ f.label }}</span>
    </div>
    <svg ref="svgRef" class="galaxy-svg" viewBox="-400 -400 800 800" preserveAspectRatio="xMidYMid meet">
      <defs>
        <radialGradient id="coreGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#4ed8ff" stop-opacity="0.35"/>
          <stop offset="35%" stop-color="#8f7cff" stop-opacity="0.18"/>
          <stop offset="70%" stop-color="#4ed8ff" stop-opacity="0.06"/>
          <stop offset="100%" stop-color="#07111f" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="corePulse" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#4ed8ff" stop-opacity="0.2"/>
          <stop offset="60%" stop-color="#4ed8ff" stop-opacity="0.05"/>
          <stop offset="100%" stop-color="#4ed8ff" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="masteredGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#37d6a5" stop-opacity="0.7"/>
          <stop offset="50%" stop-color="#37d6a5" stop-opacity="0.25"/>
          <stop offset="100%" stop-color="#37d6a5" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="improvingGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#8f7cff" stop-opacity="0.65"/>
          <stop offset="50%" stop-color="#8f7cff" stop-opacity="0.2"/>
          <stop offset="100%" stop-color="#8f7cff" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="missingGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#ff7088" stop-opacity="0.55"/>
          <stop offset="50%" stop-color="#ff7088" stop-opacity="0.18"/>
          <stop offset="100%" stop-color="#ff7088" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="transferGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#ffb65c" stop-opacity="0.6"/>
          <stop offset="50%" stop-color="#ffb65c" stop-opacity="0.2"/>
          <stop offset="100%" stop-color="#ffb65c" stop-opacity="0"/>
        </radialGradient>
        <filter id="softGlow" x="-150%" y="-150%" width="400%" height="400%">
          <feGaussianBlur stdDeviation="3" result="blur"/>
          <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
        <filter id="strongGlow" x="-200%" y="-200%" width="500%" height="500%">
          <feGaussianBlur stdDeviation="6" result="blur"/>
          <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
      </defs>

      <g class="orbit-rings">
        <circle cx="0" cy="0" :r="ORBIT_RADII[0]-2" fill="none" stroke="rgba(78,216,255,0.04)" stroke-width="6"/>
        <circle cx="0" cy="0" :r="ORBIT_RADII[0]" fill="none" stroke="rgba(135,169,220,0.13)" stroke-width="1"/>
        <circle cx="0" cy="0" :r="ORBIT_RADII[0]+2" fill="none" stroke="rgba(78,216,255,0.06)" stroke-width="0.5"/>
        <circle cx="0" cy="0" :r="ORBIT_RADII[1]" fill="none" stroke="rgba(135,169,220,0.10)" stroke-width="1" stroke-dasharray="4 6"/>
        <circle cx="0" cy="0" :r="ORBIT_RADII[2]" fill="none" stroke="rgba(135,169,220,0.07)" stroke-width="0.8" stroke-dasharray="2 4"/>
      </g>

      <g class="orbit-labels">
        <text :x="ORBIT_RADII[0] + 10" y="-8" fill="rgba(78,216,255,0.45)" font-size="11" font-weight="500">核心技能</text>
        <text :x="ORBIT_RADII[1] + 10" y="-8" fill="rgba(143,124,255,0.35)" font-size="11" font-weight="500">工具 &amp; 项目</text>
        <text :x="ORBIT_RADII[2] + 10" y="-8" fill="rgba(255,182,92,0.3)" font-size="11" font-weight="500">通用能力</text>
      </g>

      <g class="core-links">
        <line v-for="skill in visibleSkills" :key="'l'+skill.id"
          v-show="isSkillVisible(skill)"
          :x1="0" :y1="0"
          :x2="getSkillPos(skill).x"
          :y2="getSkillPos(skill).y"
          :stroke="getLinkColor(skill.status)"
          stroke-width="0.8"
          stroke-linecap="round"
          :opacity="selectedSkill?.id === skill.id ? 0.7 : 0.15"/>
      </g>

      <g class="core-center">
        <circle cx="0" cy="0" r="140" fill="url(#coreGlow)" style="animation: core-breathe 4s ease-in-out infinite; transform-origin: center;"/>
        <circle class="core-pulse-ring" cx="0" cy="0" r="62" fill="none" stroke="rgba(78,216,255,0.4)" stroke-width="1.5"/>
        <circle class="core-pulse-ring-2" cx="0" cy="0" r="62" fill="none" stroke="rgba(78,216,255,0)" stroke-width="1"/>
        <g class="core-ring-outer" style="animation: core-rotate 60s linear infinite; transform-origin: center;">
          <circle cx="0" cy="0" r="96" fill="none" stroke="rgba(78,216,255,0.22)" stroke-width="1" stroke-dasharray="16 12 4 12"/>
        </g>
        <g class="core-ring-middle" style="animation: core-rotate-rev 45s linear infinite; transform-origin: center;">
          <circle cx="0" cy="0" r="82" fill="none" stroke="rgba(143,124,255,0.15)" stroke-width="1" stroke-dasharray="8 14"/>
        </g>
        <g class="core-ring-inner" style="animation: core-rotate 35s linear infinite; transform-origin: center;">
          <circle cx="0" cy="0" r="70" fill="none" stroke="rgba(55,214,165,0.12)" stroke-width="0.8" stroke-dasharray="3 8"/>
        </g>
        <circle cx="0" cy="0" r="62" fill="rgba(30, 120, 220, 0.12)" stroke="rgba(78,216,255,0.4)" stroke-width="1" filter="url(#softGlow)"/>
        <circle cx="0" cy="0" r="62" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="0.8"/>
        
        <circle cx="0" cy="-22" r="22" fill="rgba(78,216,255,0.15)" stroke="rgba(78,216,255,0.5)" stroke-width="1.2" filter="url(#softGlow)"/>
        <text x="0" y="-16" text-anchor="middle" fill="#4ed8ff" font-size="22" font-weight="700">{{ profile.name.charAt(0) }}</text>
        
        <text x="0" y="14" text-anchor="middle" fill="#f4f7fc" font-size="17" font-weight="700">{{ profile.name }}</text>
        <text x="0" y="32" text-anchor="middle" fill="#a8b4c8" font-size="12">{{ profile.currentIdentity }}</text>
        
        <g transform="translate(0, 52)" filter="url(#softGlow)">
          <rect x="-48" y="-11" width="96" height="22" rx="11" fill="rgba(78,216,255,0.18)" stroke="rgba(78,216,255,0.35)" stroke-width="1"/>
          <text x="0" y="4" text-anchor="middle" fill="#4ed8ff" font-size="13" font-weight="600">匹配度 {{ matchScore }}%</text>
        </g>
      </g>

      <g class="skill-nodes">
        <g v-for="skill in visibleSkills" :key="skill.id"
           class="skill-node-group"
           :class="{selected: selectedSkill?.id === skill.id, hovered: hoverSkill?.id === skill.id}"
           :transform="`translate(${getSkillPos(skill).x}, ${getSkillPos(skill).y})`"
           @click="$emit('select', skill)"
           @mouseenter="hoverSkill = skill"
           @mouseleave="hoverSkill = null">
          
          <circle class="node-outer-ring" :r="nodeSize(skill) + 4"
            :fill="getNodeOuterRingFill(skill)"
            :stroke="getNodeStroke(skill)"
            stroke-width="0.5"
            :opacity="hoverSkill?.id === skill.id || selectedSkill?.id === skill.id ? 0.4 : 0.15"/>

          <circle v-if="skill.status === 'mastered'" class="skill-node-glow"
            :r="nodeSize(skill) + 14" fill="url(#masteredGlow)"
            :opacity="hoverSkill?.id === skill.id || selectedSkill?.id === skill.id ? 1 : 0.7"
            style="animation: node-pulse 3s ease-in-out infinite; transform-origin: center;"/>
          <circle v-else-if="skill.status === 'improving'" class="skill-node-glow"
            :r="nodeSize(skill) + 12" fill="url(#improvingGlow)"
            :opacity="hoverSkill?.id === skill.id || selectedSkill?.id === skill.id ? 0.95 : 0.6"
            style="animation: node-pulse 3.5s ease-in-out infinite; transform-origin: center;"/>
          <circle v-else-if="skill.status === 'missing'" class="skill-node-glow"
            :r="nodeSize(skill) + 10" fill="url(#missingGlow)"
            :opacity="hoverSkill?.id === skill.id || selectedSkill?.id === skill.id ? 0.85 : 0.45"/>
          <circle v-else class="skill-node-glow"
            :r="nodeSize(skill) + 11" fill="url(#transferGlow)"
            :opacity="hoverSkill?.id === skill.id || selectedSkill?.id === skill.id ? 0.9 : 0.55"
            style="animation: node-pulse 4s ease-in-out infinite; transform-origin: center;"/>

          <circle v-if="skill.status === 'missing'" class="skill-node-circle"
            :r="nodeSize(skill)"
            fill="rgba(255,112,136,0.1)"
            stroke="#ff7088" stroke-width="1.8"
            stroke-dasharray="5 4"
            :opacity="hoverSkill?.id === skill.id ? 1 : 0.85"
            :filter="hoverSkill?.id === skill.id || selectedSkill?.id === skill.id ? 'url(#strongGlow)' : 'url(#softGlow)'"/>
          <circle v-else class="skill-node-circle"
            :r="nodeSize(skill)"
            :fill="getNodeFill(skill)"
            :stroke="getNodeStroke(skill)"
            :stroke-width="selectedSkill?.id === skill.id ? 2.5 : 1.8"
            :filter="hoverSkill?.id === skill.id || selectedSkill?.id === skill.id ? 'url(#strongGlow)' : 'url(#softGlow)'"/>

          <text class="skill-node-text"
            :y="getTextY(skill)" text-anchor="middle"
            :fill="getTextColor(skill)" :font-size="getTextSize(skill)" font-weight="600">
            {{ skill.name }}
          </text>
          
          <text v-if="nodeSize(skill) >= 20" class="skill-node-level"
            :y="nodeSize(skill) + 17" text-anchor="middle"
            fill="rgba(168,180,200,0.7)" :font-size="11" font-weight="500">
            Lv.{{ skill.currentLevel }}
          </text>
        </g>
      </g>

      <g v-if="hoverSkill" class="skill-tooltip"
         :transform="tooltipTransform"
         pointer-events="none"
         filter="url(#softGlow)">
        <rect x="0" y="0" width="210" height="96" rx="12"
          fill="rgba(15, 75, 160, 0.75)" stroke="rgba(78,216,255,0.35)" stroke-width="1"/>
        <rect x="0" y="0" width="4" height="96" rx="2" :fill="getStatusColor(hoverSkill.status)"/>
        <text x="18" y="26" fill="#f4f7fc" font-size="14" font-weight="600">{{ hoverSkill.name }}</text>
        <text x="18" y="46" fill="#a8b4c8" font-size="12">当前 Lv.{{ hoverSkill.currentLevel }} / 要求 Lv.{{ hoverSkill.requiredLevel }}</text>
        <text x="18" y="64" :fill="getStatusColor(hoverSkill.status)" font-size="12" font-weight="500">{{ getStatusLabel(hoverSkill.status) }}</text>
        <text x="18" y="82" fill="#68768d" font-size="11">证据 {{ hoverSkill.evidenceCount }} 条 · 点击查看详情</text>
      </g>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import type { Skill, SkillStatus, UserProfile, SkillOrbit, SkillSize } from './types'

const ORBIT_RADII: Record<SkillOrbit, number> = {
  1: 150,
  2: 250,
  3: 350
}

const NODE_SIZES: Record<SkillSize, number> = {
  core: 28,
  normal: 22,
  minor: 17
}

const props = defineProps<{
  skills: (Skill & { orbit: SkillOrbit; size: SkillSize; angle: number })[]
  profile: UserProfile
  selectedSkill: Skill | null
  filter: { status: string; category: string; showCoreOnly: boolean }
  matchScore: number
}>()

const emit = defineEmits<{
  select: [skill: Skill]
  filterChange: [filter: { status: string; category: string; showCoreOnly: boolean }]
}>()

const filterOptions = [
  { key: 'all', label: '全部' },
  { key: 'mastered', label: '已掌握' },
  { key: 'improving', label: '待提升' },
  { key: 'missing', label: '缺失' },
  { key: 'transferable', label: '可迁移' },
  { key: 'gap', label: '只看差距' },
]

const canvasRef = ref<HTMLCanvasElement | null>(null)
const svgRef = ref<SVGSVGElement | null>(null)
const hoverSkill = ref<Skill | null>(null)

let canvasCtx: CanvasRenderingContext2D | null = null
let canvasW = 800, canvasH = 800
let animFrameId = 0
let orbitDots: { orbit: SkillOrbit; angle: number; speed: number; size: number; alpha: number; color: string; trail: { angle: number; alpha: number }[] }[] = []
let bgStars: { x: number; y: number; size: number; alpha: number; twinkle: number; color: string }[] = []
let nebulaClouds: { x: number; y: number; r: number; color: string; alpha: number; drift: number }[] = []
let currentHoverId: string | null = null
let currentSelectedId: string | null = null

function nodeSize(skill: Skill & { size?: SkillSize }): number {
  return NODE_SIZES[skill.size || 'normal']
}

function getTextSize(skill: Skill & { size?: SkillSize }): number {
  const s = skill.size || 'normal'
  if (s === 'core') return 13
  if (s === 'normal') return 12
  return 11
}

function getTextY(skill: Skill & { size?: SkillSize }): number {
  const s = skill.size || 'normal'
  if (s === 'core') return 5
  if (s === 'normal') return 4
  return 4
}

function getSkillPos(skill: Skill & { orbit?: SkillOrbit; angle?: number }) {
  const orbit = skill.orbit || 2
  const r = ORBIT_RADII[orbit]
  const angle = ((skill.angle || 0) - 90) * Math.PI / 180
  return {
    x: Math.cos(angle) * r,
    y: Math.sin(angle) * r
  }
}

function getNodeFill(skill: Skill): string {
  switch (skill.status) {
    case 'mastered': return 'rgba(55,214,165,0.18)'
    case 'improving': return 'rgba(143,124,255,0.15)'
    case 'transferable': return 'rgba(255,182,92,0.15)'
    case 'missing': return 'rgba(255,112,136,0.08)'
    default: return 'rgba(255,255,255,0.05)'
  }
}

function getNodeOuterRingFill(skill: Skill): string {
  switch (skill.status) {
    case 'mastered': return 'rgba(55,214,165,0.05)'
    case 'improving': return 'rgba(143,124,255,0.05)'
    case 'transferable': return 'rgba(255,182,92,0.05)'
    case 'missing': return 'rgba(255,112,136,0.03)'
    default: return 'rgba(78,216,255,0.03)'
  }
}

function getNodeStroke(skill: Skill): string {
  switch (skill.status) {
    case 'mastered': return '#37d6a5'
    case 'improving': return '#8f7cff'
    case 'transferable': return '#ffb65c'
    case 'missing': return '#ff7088'
    default: return 'rgba(135,169,220,0.5)'
  }
}

function getTextColor(skill: Skill): string {
  switch (skill.status) {
    case 'mastered': return '#e6fff5'
    case 'improving': return '#f4f7fc'
    case 'transferable': return '#fff5e0'
    case 'missing': return 'rgba(255,180,190,0.9)'
    default: return '#c8d4e8'
  }
}

function getLinkColor(status: SkillStatus): string {
  switch (status) {
    case 'mastered': return 'rgba(55,214,165,0.5)'
    case 'improving': return 'rgba(143,124,255,0.4)'
    case 'transferable': return 'rgba(255,182,92,0.4)'
    case 'missing': return 'rgba(255,112,136,0.2)'
    default: return 'rgba(78,216,255,0.25)'
  }
}

function getStatusColor(status: SkillStatus): string {
  const m: Record<SkillStatus, string> = {
    mastered: '#37d6a5', improving: '#8f7cff',
    transferable: '#ffb65c', missing: '#ff7088'
  }
  return m[status]
}

function getStatusLabel(status: SkillStatus): string {
  const m: Record<SkillStatus, string> = {
    mastered: '✓ 已掌握', improving: '◈ 待提升',
    transferable: '↔ 可迁移', missing: '✗ 缺失'
  }
  return m[status]
}

const visibleSkills = computed(() => props.skills.filter(s => isSkillVisible(s)))

function isSkillVisible(skill: Skill): boolean {
  const f = props.filter
  if (f.status === 'all' || !f.status) return true
  if (f.status === 'gap') return skill.status !== 'mastered'
  return skill.status === f.status
}

const tooltipTransform = computed(() => {
  if (!hoverSkill.value) return 'translate(0,0)'
  const pos = getSkillPos(hoverSkill.value as any)
  let tx = pos.x + nodeSize(hoverSkill.value) + 20, ty = pos.y - 40
  if (tx > 160) tx = pos.x - 230
  if (ty < -340) ty = pos.y + 26
  return `translate(${tx}, ${ty})`
})

function initCanvas() {
  const canvas = canvasRef.value
  if (!canvas) return
  const parent = canvas.parentElement
  if (!parent) return
  const size = Math.min(parent.clientWidth, parent.clientHeight)
  canvas.width = size * window.devicePixelRatio
  canvas.height = size * window.devicePixelRatio
  canvas.style.width = size + 'px'
  canvas.style.height = size + 'px'
  canvasW = canvas.width
  canvasH = canvas.height
  canvasCtx = canvas.getContext('2d')
  if (canvasCtx) canvasCtx.scale(window.devicePixelRatio, window.devicePixelRatio)
  canvasW = size
  canvasH = size
  initNebula()
  initStars()
  initDots()
}

function initNebula() {
  nebulaClouds = [
    { x: -120, y: -80, r: 200, color: 'rgba(78,216,255,', alpha: 0.025, drift: 0 },
    { x: 140, y: 60, r: 180, color: 'rgba(143,124,255,', alpha: 0.02, drift: 1 },
    { x: -60, y: 140, r: 160, color: 'rgba(55,214,165,', alpha: 0.015, drift: 2 },
    { x: 100, y: -130, r: 140, color: 'rgba(255,182,92,', alpha: 0.012, drift: 3 },
  ]
}

function initStars() {
  bgStars = []
  for (let i = 0; i < 80; i++) {
    const colors = ['168,180,200,', '78,216,255,', '255,255,255,', '143,124,255,']
    bgStars.push({
      x: (Math.random() - 0.5) * canvasW * 0.96,
      y: (Math.random() - 0.5) * canvasH * 0.96,
      size: 0.3 + Math.random() * 1.2,
      alpha: 0.06 + Math.random() * 0.25,
      twinkle: Math.random() * Math.PI * 2,
      color: colors[Math.floor(Math.random() * colors.length)]
    })
  }
}

function initDots() {
  orbitDots = []
  const orbits: SkillOrbit[] = [1, 2, 3]
  const counts = [4, 6, 8]
  const orbitColors = ['rgba(78,216,255,', 'rgba(143,124,255,', 'rgba(55,214,165,']
  orbits.forEach((orbit, oi) => {
    for (let i = 0; i < counts[oi]; i++) {
      const trail: { angle: number; alpha: number }[] = []
      for (let t = 0; t < 6; t++) {
        trail.push({ angle: 0, alpha: 0 })
      }
      orbitDots.push({
        orbit,
        angle: (i / counts[oi]) * Math.PI * 2 + Math.random() * 0.5,
        speed: (0.08 + Math.random() * 0.12) * (oi % 2 === 0 ? 1 : -1),
        size: 0.8 + Math.random() * 1.2,
        alpha: 0.4 + Math.random() * 0.4,
        color: orbitColors[oi],
        trail
      })
    }
  })
}

function drawGalaxy(time: number) {
  const ctx = canvasCtx
  if (!ctx) return
  const cx = canvasW / 2, cy = canvasH / 2
  const scale = Math.min(canvasW, canvasH) / 800
  ctx.clearRect(0, 0, canvasW, canvasH)

  for (const cloud of nebulaClouds) {
    const drift = Math.sin(time * 0.0002 + cloud.drift) * 15
    const gx = cx + (cloud.x + drift) * scale
    const gy = cy + (cloud.y + drift * 0.7) * scale
    const gr = cloud.r * scale
    const grad = ctx.createRadialGradient(gx, gy, 0, gx, gy, gr)
    grad.addColorStop(0, cloud.color + cloud.alpha + ')')
    grad.addColorStop(0.5, cloud.color + (cloud.alpha * 0.4) + ')')
    grad.addColorStop(1, cloud.color + '0)')
    ctx.beginPath()
    ctx.arc(gx, gy, gr, 0, Math.PI * 2)
    ctx.fillStyle = grad
    ctx.fill()
  }

  for (const star of bgStars) {
    const twinkle = 0.4 + Math.sin(time * 0.0012 + star.twinkle) * 0.6
    const sx = cx + star.x * scale
    const sy = cy + star.y * scale
    if (star.size > 0.9) {
      const halo = ctx.createRadialGradient(sx, sy, 0, sx, sy, star.size * 4)
      halo.addColorStop(0, star.color + (star.alpha * twinkle * 0.6) + ')')
      halo.addColorStop(1, star.color + '0)')
      ctx.beginPath()
      ctx.arc(sx, sy, star.size * 4, 0, Math.PI * 2)
      ctx.fillStyle = halo
      ctx.fill()
    }
    ctx.beginPath()
    ctx.arc(sx, sy, star.size, 0, Math.PI * 2)
    ctx.fillStyle = star.color + (star.alpha * twinkle) + ')'
    ctx.fill()
  }

  for (const dot of orbitDots) {
    const r = ORBIT_RADII[dot.orbit] * scale
    dot.angle += dot.speed * 0.004
    for (let t = dot.trail.length - 1; t > 0; t--) {
      dot.trail[t].angle = dot.trail[t - 1].angle
      dot.trail[t].alpha = dot.trail[t - 1].alpha * 0.75
    }
    dot.trail[0].angle = dot.angle
    dot.trail[0].alpha = dot.alpha
    for (let t = 0; t < dot.trail.length; t++) {
      const ta = dot.trail[t].angle
      const tx = cx + Math.cos(ta) * r
      const ty = cy + Math.sin(ta) * r
      const tsize = dot.size * (1 - t * 0.12)
      const talpha = dot.trail[t].alpha * (1 - t * 0.15)
      if (talpha <= 0.02) continue
      const grad = ctx.createRadialGradient(tx, ty, 0, tx, ty, tsize * 8)
      grad.addColorStop(0, dot.color + talpha + ')')
      grad.addColorStop(0.4, dot.color + (talpha * 0.3) + ')')
      grad.addColorStop(1, dot.color + '0)')
      ctx.beginPath()
      ctx.arc(tx, ty, tsize * 8, 0, Math.PI * 2)
      ctx.fillStyle = grad
      ctx.fill()
    }
    const dx = cx + Math.cos(dot.angle) * r
    const dy = cy + Math.sin(dot.angle) * r
    const coreGrad = ctx.createRadialGradient(dx, dy, 0, dx, dy, dot.size * 5)
    coreGrad.addColorStop(0, dot.color + (dot.alpha * 1.2) + ')')
    coreGrad.addColorStop(0.3, dot.color + (dot.alpha * 0.5) + ')')
    coreGrad.addColorStop(1, dot.color + '0)')
    ctx.beginPath()
    ctx.arc(dx, dy, dot.size * 5, 0, Math.PI * 2)
    ctx.fillStyle = coreGrad
    ctx.fill()
    ctx.beginPath()
    ctx.arc(dx, dy, dot.size * 1.2, 0, Math.PI * 2)
    ctx.fillStyle = dot.color + '0.95)'
    ctx.fill()
  }

  for (const skill of props.skills) {
    if (!isSkillVisible(skill)) continue
    const pos = getSkillPos(skill)
    const phase = (skill.angle || 0) * 0.05
    const pulse = 0.5 + Math.sin(time * 0.0018 + phase) * 0.5
    const dx = cx + pos.x * scale
    const dy = cy + pos.y * scale
    const ns = nodeSize(skill) * scale
    const clr = getNodeStroke(skill)
    const baseR = ns + 10 * scale
    const pulseR = baseR + pulse * 12 * scale
    const isActive = currentHoverId === skill.id || currentSelectedId === skill.id
    const intensity = isActive ? 1.6 : 1
    const g = ctx.createRadialGradient(dx, dy, 0, dx, dy, pulseR)
    g.addColorStop(0, hexToRgba(clr, 0.35 * intensity))
    g.addColorStop(0.5, hexToRgba(clr, 0.1 * intensity))
    g.addColorStop(1, hexToRgba(clr, 0))
    ctx.beginPath()
    ctx.arc(dx, dy, pulseR, 0, Math.PI * 2)
    ctx.fillStyle = g
    ctx.fill()
  }

  const corePulse = 0.7 + Math.sin(time * 0.001) * 0.3
  const coreGrad = ctx.createRadialGradient(cx, cy, 50 * scale, cx, cy, 180 * scale)
  coreGrad.addColorStop(0, `rgba(78,216,255,${0.08 * corePulse})`)
  coreGrad.addColorStop(0.5, `rgba(143,124,255,${0.04 * corePulse})`)
  coreGrad.addColorStop(1, 'rgba(78,216,255,0)')
  ctx.beginPath()
  ctx.arc(cx, cy, 180 * scale, 0, Math.PI * 2)
  ctx.fillStyle = coreGrad
  ctx.fill()

  animFrameId = requestAnimationFrame(drawGalaxy)
}

function hexToRgba(hex: string, alpha: number): string {
  if (hex.startsWith('rgba')) return hex
  if (hex.startsWith('rgb')) {
    const m = hex.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/)
    if (m) return `rgba(${m[1]},${m[2]},${m[3]},${alpha})`
  }
  const h = hex.replace('#', '')
  if (h.length === 6) {
    const r = parseInt(h.substring(0, 2), 16)
    const g = parseInt(h.substring(2, 4), 16)
    const b = parseInt(h.substring(4, 6), 16)
    return `rgba(${r},${g},${b},${alpha})`
  }
  return hex
}

onMounted(() => {
  initCanvas()
  animFrameId = requestAnimationFrame(drawGalaxy)
  window.addEventListener('resize', initCanvas)
})

onBeforeUnmount(() => {
  cancelAnimationFrame(animFrameId)
  window.removeEventListener('resize', initCanvas)
})

watch(() => props.skills, () => initDots(), { deep: true })
watch(hoverSkill, (val) => { currentHoverId = val?.id || null })
watch(() => props.selectedSkill, (val) => { currentSelectedId = val?.id || null }, { immediate: true })
</script>

<style scoped>
.galaxy-container {
  width: 100%;
  height: 100%;
  min-height: 720px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.galaxy-canvas {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1;
  pointer-events: none;
}
.galaxy-svg {
  position: relative;
  z-index: 2;
  width: 100%;
  height: 100%;
  max-width: 880px;
  max-height: 880px;
}
.skill-node-group { cursor: pointer; transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1); }
.skill-node-group:hover { transform: scale(1.15) !important; }
.skill-node-group.selected { transform: scale(1.08); }

@keyframes core-rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
@keyframes core-rotate-rev {
  from { transform: rotate(360deg); }
  to { transform: rotate(0deg); }
}
@keyframes core-breathe {
  0%, 100% { opacity: 0.8; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.04); }
}
@keyframes node-pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.85; }
}
@keyframes pulse-ring {
  0% { r: 62; opacity: 0.6; stroke-width: 2; }
  100% { r: 120; opacity: 0; stroke-width: 0.5; }
}
.core-pulse-ring {
  animation: pulse-ring 3s ease-out infinite;
}
.core-pulse-ring-2 {
  animation: pulse-ring 3s ease-out infinite 1.5s;
  stroke: rgba(78,216,255,0.5);
}

.galaxy-filters {
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
  z-index: 6;
}
.galaxy-filter {
  font-size: 13px;
  padding: 8px 18px;
  background: rgba(20, 90, 180, 0.3);
  border: 1px solid rgba(78,216,255,0.2);
  border-radius: 20px;
  color: #d0e4ff;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
  backdrop-filter: blur(12px);
  font-weight: 500;
}
.galaxy-filter:hover {
  background: rgba(30, 110, 200, 0.45);
  border-color: rgba(78,216,255,0.45);
  color: #ffffff;
  box-shadow: 0 0 16px rgba(78,216,255,0.2);
}
.galaxy-filter.active {
  background: rgba(78,216,255,0.15);
  border-color: rgba(78,216,255,0.55);
  color: #4ed8ff;
  box-shadow: 0 0 20px rgba(78,216,255,0.2), inset 0 0 12px rgba(78,216,255,0.08);
}
</style>

<template>
  <canvas ref="canvas" class="tech-particle-canvas" aria-hidden="true"></canvas>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

type Particle = {
  x: number
  y: number
  radius: number
  speed: number
  drift: number
  phase: number
  alpha: number
}

const canvas = ref<HTMLCanvasElement | null>(null)
let context: CanvasRenderingContext2D | null = null
let frameId = 0
let width = 0
let height = 0
let particles: Particle[] = []
let reduceMotion = false

const networkNodes = [
  [0.70, 0.20, 7], [0.78, 0.28, 5], [0.85, 0.18, 4], [0.91, 0.34, 7],
  [0.76, 0.42, 4], [0.87, 0.48, 5], [0.96, 0.24, 4], [0.97, 0.46, 6]
] as const

const networkEdges = [
  [0, 1], [0, 2], [1, 3], [1, 4], [2, 3], [2, 6], [3, 5], [3, 6], [4, 5], [5, 7], [6, 7]
] as const

onMounted(() => {
  reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  context = canvas.value?.getContext('2d') || null
  resizeCanvas()
  window.addEventListener('resize', resizeCanvas)
  if (reduceMotion) {
    draw(0)
  } else {
    frameId = window.requestAnimationFrame(draw)
  }
})

onBeforeUnmount(() => {
  window.cancelAnimationFrame(frameId)
  window.removeEventListener('resize', resizeCanvas)
})

function resizeCanvas() {
  if (!canvas.value || !context) return
  const ratio = Math.min(window.devicePixelRatio || 1, 2)
  width = window.innerWidth
  height = window.innerHeight
  canvas.value.width = Math.round(width * ratio)
  canvas.value.height = Math.round(height * ratio)
  canvas.value.style.width = `${width}px`
  canvas.value.style.height = `${height}px`
  context.setTransform(ratio, 0, 0, ratio, 0, 0)

  const amount = Math.max(82, Math.min(150, Math.round(width / 12)))
  particles = Array.from({ length: amount }, (_, index) => createParticle(index))
}

function createParticle(index: number): Particle {
  return {
    x: ((index * 71) % 997) / 997,
    y: ((index * 137) % 991) / 991,
    radius: 1.1 + ((index * 11) % 12) / 10,
    speed: 0.010 + ((index * 17) % 16) / 1000,
    drift: 5 + ((index * 19) % 32),
    phase: (index * 0.71) % (Math.PI * 2),
    alpha: 0.38 + ((index * 23) % 50) / 100
  }
}

function draw(timestamp: number) {
  if (!context) return
  const time = timestamp / 1000
  context.clearRect(0, 0, width, height)
  context.save()
  context.globalCompositeOperation = 'lighter'

  drawParticles(time)
  drawNetwork(time)
  drawEnergyStreams(time)

  context.restore()
  if (!reduceMotion) {
    frameId = window.requestAnimationFrame(draw)
  }
}

function drawParticles(time: number) {
  const ctx = context
  if (!ctx) return
  for (const particle of particles) {
    const x = ((particle.x + time * particle.speed) % 1) * width
    const y = particle.y * height + Math.sin(time * 0.42 + particle.phase) * particle.drift
    const alpha = particle.alpha * (0.62 + Math.sin(time * 1.2 + particle.phase) * 0.28)
    ctx.fillStyle = `rgba(205, 249, 255, ${Math.max(0.12, alpha)})`
    ctx.beginPath()
    ctx.arc(x, y, particle.radius, 0, Math.PI * 2)
    ctx.fill()

    if (particle.radius > 1.35) {
      ctx.strokeStyle = `rgba(55, 221, 255, ${Math.max(0.1, alpha * 0.5)})`
      ctx.lineWidth = 0.75
      ctx.beginPath()
      ctx.arc(x, y, particle.radius + 3.2, 0, Math.PI * 2)
      ctx.stroke()
    }
  }
}

function drawNetwork(time: number) {
  const ctx = context
  if (!ctx) return
  const nodes = networkNodes.map(([x, y, size], index) => {
    const driftX = Math.sin(time * 0.38 + index * 1.9) * 13
    const driftY = Math.cos(time * 0.48 + index * 1.3) * 11
    return { x: x * width + driftX, y: y * height + driftY, size }
  })

  ctx.lineWidth = 1.15
  for (const [from, to] of networkEdges) {
    const start = nodes[from]
    const end = nodes[to]
    const gradient = ctx.createLinearGradient(start.x, start.y, end.x, end.y)
    gradient.addColorStop(0, 'rgba(52, 215, 255, 0.16)')
    gradient.addColorStop(0.5, `rgba(96, 234, 255, ${0.38 + Math.sin(time + from) * 0.08})`)
    gradient.addColorStop(1, 'rgba(51, 147, 255, 0.12)')
    ctx.strokeStyle = gradient
    ctx.setLineDash([4, 8])
    ctx.lineDashOffset = -time * 20
    ctx.beginPath()
    ctx.moveTo(start.x, start.y)
    ctx.lineTo(end.x, end.y)
    ctx.stroke()
  }
  ctx.setLineDash([])

  nodes.forEach((node, index) => {
    const pulse = 0.78 + Math.sin(time * 1.8 + index) * 0.22
    const radius = node.size * pulse
    ctx.strokeStyle = `rgba(92, 230, 255, ${0.36 + pulse * 0.22})`
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.arc(node.x, node.y, radius + 5, 0, Math.PI * 2)
    ctx.stroke()
    ctx.fillStyle = '#dffcff'
    ctx.beginPath()
    ctx.arc(node.x, node.y, Math.max(2.2, radius * 0.45), 0, Math.PI * 2)
    ctx.fill()
  })
}

function drawEnergyStreams(time: number) {
  const ctx = context
  if (!ctx) return
  const lanes = [0, 1, 2, 3, 4, 5]
  lanes.forEach((lane) => {
    const laneOffset = lane * 0.027
    const startY = height * (0.80 + laneOffset)
    const endY = height * (0.52 + laneOffset * 0.42)
    const gradient = ctx.createLinearGradient(0, startY, width, endY)
    gradient.addColorStop(0, 'rgba(12, 110, 255, 0.02)')
    gradient.addColorStop(0.35, `rgba(10, 163, 255, ${lane < 2 ? 0.3 : 0.18})`)
    gradient.addColorStop(0.62, `rgba(91, 242, 255, ${lane < 2 ? 0.7 : 0.42})`)
    gradient.addColorStop(1, 'rgba(66, 181, 255, 0.03)')

    ctx.strokeStyle = gradient
    ctx.lineWidth = lane < 2 ? 4.2 : 1.6
    ctx.shadowBlur = lane < 2 ? 5 : 2
    ctx.shadowColor = 'rgba(24, 207, 255, 0.46)'
    ctx.beginPath()
    ctx.moveTo(-width * 0.08, startY)
    ctx.bezierCurveTo(
      width * 0.26,
      height * (0.67 + laneOffset),
      width * 0.55,
      height * (0.98 - laneOffset),
      width * 0.77,
      endY
    )
    ctx.bezierCurveTo(width * 0.9, height * (0.43 + laneOffset), width * 1.03, height * 0.56, width * 1.12, height * 0.49)
    ctx.stroke()
    ctx.shadowBlur = 0

    if (lane < 3) {
      ctx.strokeStyle = `rgba(198, 252, 255, ${lane === 0 ? 0.74 : 0.44})`
      ctx.lineWidth = lane === 0 ? 1.05 : 0.72
      ctx.beginPath()
      ctx.moveTo(-width * 0.08, startY)
      ctx.bezierCurveTo(width * 0.26, height * (0.67 + laneOffset), width * 0.55, height * (0.98 - laneOffset), width * 0.77, endY)
      ctx.bezierCurveTo(width * 0.9, height * (0.43 + laneOffset), width * 1.03, height * 0.56, width * 1.12, height * 0.49)
      ctx.stroke()
    }

    for (let marker = 0; marker < 3; marker += 1) {
      const progress = (time * (0.06 + lane * 0.004) + marker * 0.23 + lane * 0.11) % 0.72
      const point = cubicFlowPoint(progress, laneOffset)
      ctx.fillStyle = '#e8feff'
      ctx.beginPath()
      ctx.arc(point.x, point.y, 2.2, 0, Math.PI * 2)
      ctx.fill()
      ctx.strokeStyle = 'rgba(88, 238, 255, 0.52)'
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.arc(point.x, point.y, 6.5, 0, Math.PI * 2)
      ctx.stroke()
    }
  })
}

function cubicFlowPoint(progress: number, laneOffset: number) {
  const start = { x: -width * 0.08, y: height * (0.8 + laneOffset) }
  const control1 = { x: width * 0.26, y: height * (0.67 + laneOffset) }
  const control2 = { x: width * 0.55, y: height * (0.98 - laneOffset) }
  const end = { x: width * 0.77, y: height * (0.52 + laneOffset * 0.42) }
  const t = Math.min(progress / 0.72, 1)
  const inverse = 1 - t
  return {
    x: inverse ** 3 * start.x + 3 * inverse ** 2 * t * control1.x + 3 * inverse * t ** 2 * control2.x + t ** 3 * end.x,
    y: inverse ** 3 * start.y + 3 * inverse ** 2 * t * control1.y + 3 * inverse * t ** 2 * control2.y + t ** 3 * end.y
  }
}
</script>

<style scoped>
.tech-particle-canvas {
  position: absolute;
  z-index: 2;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

@media (prefers-reduced-motion: reduce) {
  .tech-particle-canvas {
    opacity: 0.62;
  }
}
</style>

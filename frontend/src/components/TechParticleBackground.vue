<template>
  <div class="tech-bg-container" aria-hidden="true">
    <div class="blue-gradient-bg"></div>
    <canvas ref="canvas" class="tech-particle-canvas"></canvas>
    <div class="tech-grid"></div>
    <div class="tech-glow tech-glow--1"></div>
    <div class="tech-glow tech-glow--2"></div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

type Particle = {
  x: number
  y: number
  vx: number
  vy: number
  radius: number
  alpha: number
  pulse: number
  pulseSpeed: number
}

type FlowLine = {
  startX: number
  startY: number
  cp1x: number
  cp1y: number
  cp2x: number
  cp2y: number
  endX: number
  endY: number
  width: number
  speed: number
  offset: number
}

type NetNode = {
  x: number
  y: number
  radius: number
  pulse: number
  pulseSpeed: number
  connections: number[]
}

const canvas = ref<HTMLCanvasElement | null>(null)
let ctx: CanvasRenderingContext2D | null = null
let frameId = 0
let width = 0
let height = 0
let particles: Particle[] = []
let flowLines: FlowLine[] = []
let netNodes: NetNode[] = []
let reduceMotion = false

const cyan = [78, 216, 255]
const lightCyan = [140, 235, 255]

onMounted(() => {
  reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  ctx = canvas.value?.getContext('2d') || null
  resizeCanvas()
  window.addEventListener('resize', resizeCanvas)
  initFlowLines()
  initNetNodes()
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
  if (!canvas.value || !ctx) return
  const ratio = Math.min(window.devicePixelRatio || 1, 2)
  width = window.innerWidth
  height = window.innerHeight
  canvas.value.width = Math.round(width * ratio)
  canvas.value.height = Math.round(height * ratio)
  canvas.value.style.width = `${width}px`
  canvas.value.style.height = `${height}px`
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0)
  initParticles()
  initFlowLines()
  initNetNodes()
}

function initParticles() {
  const count = Math.max(60, Math.min(120, Math.round(width / 15)))
  particles = []
  for (let i = 0; i < count; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.2,
      vy: (Math.random() - 0.5) * 0.15,
      radius: 0.8 + Math.random() * 1.8,
      alpha: 0.2 + Math.random() * 0.4,
      pulse: Math.random() * Math.PI * 2,
      pulseSpeed: 0.3 + Math.random() * 1
    })
  }
}

function initFlowLines() {
  flowLines = [
    {
      startX: width + 100, startY: height * 0.3,
      cp1x: width * 0.7, cp1y: height * 0.5,
      cp2x: width * 0.4, cp2y: height * 0.4,
      endX: -100, endY: height * 0.7,
      width: 3, speed: 0.0004, offset: 0
    },
    {
      startX: width + 50, startY: height * 0.5,
      cp1x: width * 0.75, cp1y: height * 0.6,
      cp2x: width * 0.5, cp2y: height * 0.55,
      endX: -50, endY: height * 0.8,
      width: 2, speed: 0.00035, offset: 0.2
    },
    {
      startX: width + 80, startY: height * 0.4,
      cp1x: width * 0.65, cp1y: height * 0.55,
      cp2x: width * 0.45, cp2y: height * 0.48,
      endX: -80, endY: height * 0.75,
      width: 1.5, speed: 0.0005, offset: 0.4
    },
    {
      startX: -50, startY: height * 0.2,
      cp1x: width * 0.3, cp1y: height * 0.1,
      cp2x: width * 0.6, cp2y: height * 0.3,
      endX: width + 50, endY: height * 0.25,
      width: 2, speed: 0.0003, offset: 0.6
    },
    {
      startX: width + 120, startY: height * 0.6,
      cp1x: width * 0.8, cp1y: height * 0.7,
      cp2x: width * 0.3, cp2y: height * 0.65,
      endX: -120, endY: height * 0.85,
      width: 1, speed: 0.00045, offset: 0.8
    }
  ]
}

function initNetNodes() {
  netNodes = []
  const nodeCount = 15
  for (let i = 0; i < nodeCount; i++) {
    netNodes.push({
      x: Math.random() * width,
      y: Math.random() * height,
      radius: 1.5 + Math.random() * 2.5,
      pulse: Math.random() * Math.PI * 2,
      pulseSpeed: 0.5 + Math.random() * 1,
      connections: []
    })
  }
  netNodes.forEach((node, i) => {
    const connectionCount = 1 + Math.floor(Math.random() * 3)
    for (let j = 0; j < connectionCount; j++) {
      let target = Math.floor(Math.random() * netNodes.length)
      while (target === i || node.connections.includes(target)) {
        target = Math.floor(Math.random() * netNodes.length)
      }
      node.connections.push(target)
    }
  })
}

function cubicBezier(t: number, p0: number, p1: number, p2: number, p3: number): number {
  const mt = 1 - t
  return mt * mt * mt * p0 + 3 * mt * mt * t * p1 + 3 * mt * t * t * p2 + t * t * t * p3
}

function draw(timestamp: number) {
  if (!ctx) return
  const time = timestamp / 1000
  ctx.clearRect(0, 0, width, height)

  drawNetNodes(time)
  drawFlowLines(time)
  drawParticles(time)

  if (!reduceMotion) {
    frameId = window.requestAnimationFrame(draw)
  }
}

function drawParticles(time: number) {
  if (!ctx) return
  particles.forEach(p => {
    p.x += p.vx
    p.y += p.vy
    p.pulse += p.pulseSpeed * 0.016

    if (p.x < -10) p.x = width + 10
    if (p.x > width + 10) p.x = -10
    if (p.y < -10) p.y = height + 10
    if (p.y > height + 10) p.y = -10

    const pulseAlpha = p.alpha * (0.7 + Math.sin(p.pulse) * 0.3)

    const glowRadius = p.radius * 4
    const glow = ctx!.createRadialGradient(p.x, p.y, 0, p.x, p.y, glowRadius)
    glow.addColorStop(0, `rgba(${lightCyan.join(',')}, ${pulseAlpha * 0.3})`)
    glow.addColorStop(1, `rgba(${lightCyan.join(',')}, 0)`)
    ctx!.fillStyle = glow
    ctx!.beginPath()
    ctx!.arc(p.x, p.y, glowRadius, 0, Math.PI * 2)
    ctx!.fill()

    ctx!.fillStyle = `rgba(${lightCyan.join(',')}, ${pulseAlpha})`
    ctx!.beginPath()
    ctx!.arc(p.x, p.y, p.radius, 0, Math.PI * 2)
    ctx!.fill()
  })
}

function drawFlowLines(time: number) {
  if (!ctx) return
  flowLines.forEach(line => {
    const progress = ((time * line.speed * 1000) + line.offset) % 1.2

    ctx!.lineCap = 'round'
    ctx!.lineJoin = 'round'

    ctx!.lineWidth = line.width * 0.3
    ctx!.strokeStyle = `rgba(${cyan.join(',')}, 0.12)`
    ctx!.beginPath()
    ctx!.moveTo(line.startX, line.startY)
    ctx!.bezierCurveTo(line.cp1x, line.cp1y, line.cp2x, line.cp2y, line.endX, line.endY)
    ctx!.stroke()

    for (let i = 0; i < 3; i++) {
      const tOffset = (progress - i * 0.18) % 1.2
      if (tOffset < 0 || tOffset > 1) continue

      const t = tOffset
      const x = cubicBezier(t, line.startX, line.cp1x, line.cp2x, line.endX)
      const y = cubicBezier(t, line.startY, line.cp1y, line.cp2y, line.endY)

      const headLength = 0.25
      const tStart = Math.max(0, t - headLength)
      const xStart = cubicBezier(tStart, line.startX, line.cp1x, line.cp2x, line.endX)
      const yStart = cubicBezier(tStart, line.startY, line.cp1y, line.cp2y, line.endY)

      const gradient = ctx!.createLinearGradient(xStart, yStart, x, y)
      gradient.addColorStop(0, `rgba(${cyan.join(',')}, 0)`)
      gradient.addColorStop(0.4, `rgba(${cyan.join(',')}, 0.3)`)
      gradient.addColorStop(0.8, `rgba(${lightCyan.join(',')}, 0.5)`)
      gradient.addColorStop(1, `rgba(255, 255, 255, 0.9)`)
      ctx!.strokeStyle = gradient
      ctx!.lineWidth = line.width * (1 - i * 0.25)

      ctx!.beginPath()
      ctx!.moveTo(line.startX, line.startY)
      ctx!.bezierCurveTo(line.cp1x, line.cp1y, line.cp2x, line.cp2y, line.endX, line.endY)
      ctx!.setLineDash([4, 1500])
      ctx!.lineDashOffset = -tStart * 1200
      ctx!.stroke()
      ctx!.setLineDash([])

      if (i === 0) {
        const coreSize = line.width * 1.5
        const coreGlow = ctx!.createRadialGradient(x, y, 0, x, y, coreSize * 4)
        coreGlow.addColorStop(0, `rgba(${lightCyan.join(',')}, 0.8)`)
        coreGlow.addColorStop(0.3, `rgba(${cyan.join(',')}, 0.4)`)
        coreGlow.addColorStop(1, `rgba(${cyan.join(',')}, 0)`)
        ctx!.fillStyle = coreGlow
        ctx!.beginPath()
        ctx!.arc(x, y, coreSize * 4, 0, Math.PI * 2)
        ctx!.fill()

        ctx!.fillStyle = `rgba(255, 255, 255, 0.9)`
        ctx!.beginPath()
        ctx!.arc(x, y, coreSize * 0.35, 0, Math.PI * 2)
        ctx!.fill()
      }
    }
  })
}

function drawNetNodes(time: number) {
  if (!ctx) return

  netNodes.forEach(node => {
    node.pulse += node.pulseSpeed * 0.016
  })

  netNodes.forEach((node, i) => {
    node.connections.forEach(targetIdx => {
      if (targetIdx <= i) return
      const target = netNodes[targetIdx]
      const dx = target.x - node.x
      const dy = target.y - node.y
      const dist = Math.sqrt(dx * dx + dy * dy)
      if (dist > 200) return

      const alpha = (1 - dist / 200) * 0.08
      ctx!.strokeStyle = `rgba(${cyan.join(',')}, ${alpha})`
      ctx!.lineWidth = 0.5
      ctx!.beginPath()
      ctx!.moveTo(node.x, node.y)
      ctx!.lineTo(target.x, target.y)
      ctx!.stroke()
    })
  })

  netNodes.forEach(node => {
    const pulse = (Math.sin(node.pulse) + 1) / 2
    const radius = node.radius * (0.9 + pulse * 0.2)

    const glowRadius = radius + 8
    const glow = ctx!.createRadialGradient(node.x, node.y, 0, node.x, node.y, glowRadius)
    glow.addColorStop(0, `rgba(${cyan.join(',')}, ${0.2 + pulse * 0.15})`)
    glow.addColorStop(1, `rgba(${cyan.join(',')}, 0)`)
    ctx!.fillStyle = glow
    ctx!.beginPath()
    ctx!.arc(node.x, node.y, glowRadius, 0, Math.PI * 2)
    ctx!.fill()

    ctx!.strokeStyle = `rgba(${cyan.join(',')}, ${0.25 + pulse * 0.2})`
    ctx!.lineWidth = 1
    ctx!.beginPath()
    ctx!.arc(node.x, node.y, radius + 3, 0, Math.PI * 2)
    ctx!.stroke()

    ctx!.fillStyle = `rgba(232, 253, 255, ${0.5 + pulse * 0.3})`
    ctx!.beginPath()
    ctx!.arc(node.x, node.y, Math.max(1, radius * 0.4), 0, Math.PI * 2)
    ctx!.fill()
  })
}
</script>

<style scoped>
.tech-bg-container {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}

.blue-gradient-bg {
  position: absolute;
  inset: 0;
  background: 
    radial-gradient(ellipse at 80% 20%, rgba(12, 80, 160, 0.6) 0%, transparent 50%),
    radial-gradient(ellipse at 20% 80%, rgba(8, 50, 120, 0.5) 0%, transparent 50%),
    linear-gradient(180deg, #071a35 0%, #0a2463 50%, #061530 100%);
}

.tech-particle-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.tech-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(78, 216, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(78, 216, 255, 0.02) 1px, transparent 1px);
  background-size: 50px 50px;
  opacity: 0.5;
}

.tech-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  animation: floatGlow 18s ease-in-out infinite;
}

.tech-glow--1 {
  top: -10%;
  right: -5%;
  width: 40vw;
  height: 40vw;
  background: radial-gradient(circle, rgba(30, 110, 200, 0.35), transparent 70%);
  animation-duration: 22s;
}

.tech-glow--2 {
  bottom: -15%;
  left: -5%;
  width: 45vw;
  height: 45vw;
  background: radial-gradient(circle, rgba(20, 90, 180, 0.3), transparent 70%);
  animation-duration: 25s;
  animation-delay: -10s;
}

@keyframes floatGlow {
  0%, 100% {
    transform: translate(0, 0) scale(1);
    opacity: 0.7;
  }
  50% {
    transform: translate(3vw, 5vh) scale(1.08);
    opacity: 0.9;
  }
}

@media (prefers-reduced-motion: reduce) {
  .tech-glow {
    animation: none;
  }
}
</style>

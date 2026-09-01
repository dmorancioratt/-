<template>
  <canvas ref="canvasRef" class="tech-particle-canvas"></canvas>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const canvasRef = ref<HTMLCanvasElement | null>(null)
let ctx: CanvasRenderingContext2D | null = null
let width = 0
let height = 0
let animationId: number | null = null

interface GlowOrb {
  x: number
  y: number
  vx: number
  vy: number
  radius: number
  color: [number, number, number]
  pulsePhase: number
}

let glowOrbs: GlowOrb[] = []

function initGlowOrbs() {
  glowOrbs = []
  // 低饱和灰蓝光球，避免高饱和蓝色
  const orbColors: [number, number, number][] = [
    [70, 105, 145],
    [86, 120, 158],
    [60, 90, 125],
    [75, 110, 150],
  ]

  for (let i = 0; i < 8; i++) {
    glowOrbs.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.35,
      vy: (Math.random() - 0.5) * 0.35,
      radius: Math.random() * 100 + 50,
      color: orbColors[Math.floor(Math.random() * orbColors.length)],
      pulsePhase: Math.random() * Math.PI * 2
    })
  }
}

function resize() {
  if (!canvasRef.value) return
  const canvas = canvasRef.value
  width = window.innerWidth
  height = window.innerHeight
  const dpr = window.devicePixelRatio || 1
  canvas.width = width * dpr
  canvas.height = height * dpr
  canvas.style.width = width + 'px'
  canvas.style.height = height + 'px'
  ctx = canvas.getContext('2d')
  if (ctx) {
    ctx.scale(dpr, dpr)
  }
  initGlowOrbs()
}

function drawBackground() {
  if (!ctx) return
  
  // 以驾驶舱"计划日历"的青蓝 #4ed8ff 为基调，整体偏蓝去绿
  const bgGrad = ctx.createLinearGradient(0, 0, 0, height)
  bgGrad.addColorStop(0, '#0d3347')
  bgGrad.addColorStop(0.3, '#0f3b55')
  bgGrad.addColorStop(0.7, '#0b2c44')
  bgGrad.addColorStop(1, '#071f33')
  ctx.fillStyle = bgGrad
  ctx.fillRect(0, 0, width, height)

  const bgGrad2 = ctx.createRadialGradient(
    width * 0.5, height * 0.15, 0,
    width * 0.5, height * 0.15, width * 0.9
  )
  // 顶部光晕：低饱和灰蓝，降低高饱和蓝色
  bgGrad2.addColorStop(0, 'rgba(74, 108, 146, 0.20)')
  bgGrad2.addColorStop(0.4, 'rgba(62, 92, 128, 0.11)')
  bgGrad2.addColorStop(1, 'rgba(48, 74, 106, 0)')
  ctx.fillStyle = bgGrad2
  ctx.fillRect(0, 0, width, height)

  const glowCenter = ctx.createRadialGradient(
    width * 0.2, height * 0.25, 0,
    width * 0.2, height * 0.25, width * 0.45
  )
  glowCenter.addColorStop(0, 'rgba(96, 132, 168, 0.15)')
  glowCenter.addColorStop(0.5, 'rgba(70, 100, 136, 0.06)')
  glowCenter.addColorStop(1, 'rgba(56, 84, 118, 0)')
  ctx.fillStyle = glowCenter
  ctx.fillRect(0, 0, width, height)

  const glowCenter2 = ctx.createRadialGradient(
    width * 0.85, height * 0.75, 0,
    width * 0.85, height * 0.75, width * 0.4
  )
  glowCenter2.addColorStop(0, 'rgba(82, 116, 152, 0.13)')
  glowCenter2.addColorStop(0.5, 'rgba(62, 92, 128, 0.05)')
  glowCenter2.addColorStop(1, 'rgba(50, 78, 112, 0)')
  ctx.fillStyle = glowCenter2
  ctx.fillRect(0, 0, width, height)
}

function drawHexGrid(time: number) {
  if (!ctx) return
  const size = 50
  const h = size * Math.sqrt(3) / 2
  ctx.strokeStyle = 'rgba(56, 189, 248, 0.05)'
  ctx.lineWidth = 0.5
  
  for (let row = -1; row < height / h + 2; row++) {
    for (let col = -1; col < width / (size * 1.5) + 2; col++) {
      const x = col * size * 1.5 + (row % 2) * size * 0.75
      const y = row * h
      
      ctx.beginPath()
      for (let i = 0; i < 6; i++) {
        const angle = Math.PI / 3 * i - Math.PI / 6
        const px = x + size * 0.5 * Math.cos(angle)
        const py = y + size * 0.5 * Math.sin(angle)
        if (i === 0) ctx.moveTo(px, py)
        else ctx.lineTo(px, py)
      }
      ctx.closePath()
      ctx.stroke()
    }
  }
}

function drawCornerFrames(time: number) {
  if (!ctx) return
  const pulse = Math.sin(time * 0.002) * 0.2 + 0.8
  const corners = [
    { x: 30, y: 30 },
    { x: width - 30, y: 30 },
    { x: 30, y: height - 30 },
    { x: width - 30, y: height - 30 }
  ]
  const len = 40
  
  corners.forEach((c, i) => {
    const dx = i < 2 ? 1 : -1
    const dy = i % 2 === 0 ? 1 : -1
    
    ctx!.strokeStyle = `rgba(4, 80, 100, ${0.2 * pulse})`
    ctx!.lineWidth = 2
    ctx!.beginPath()
    ctx!.moveTo(c.x - dx * len, c.y)
    ctx!.lineTo(c.x, c.y)
    ctx!.lineTo(c.x, c.y - dy * len)
    ctx!.stroke()
    
    ctx!.fillStyle = `rgba(20, 80, 110, ${0.4 * pulse})`
    ctx!.beginPath()
    ctx!.arc(c.x, c.y, 3, 0, Math.PI * 2)
    ctx!.fill()
    
    ctx!.strokeStyle = `rgba(8, 50, 70, ${0.1 * pulse})`
    ctx!.lineWidth = 1
    ctx!.beginPath()
    ctx!.moveTo(c.x - dx * (len + 25), c.y)
    ctx!.lineTo(c.x - dx * len, c.y)
    ctx!.moveTo(c.x, c.y - dy * (len + 25))
    ctx!.lineTo(c.x, c.y - dy * len)
    ctx!.stroke()
  })
}

function drawGlowOrbs(time: number) {
  if (!ctx) return

  glowOrbs.forEach(orb => {
    orb.x += orb.vx
    orb.y += orb.vy
    orb.pulsePhase += 0.008

    if (orb.x < -orb.radius) orb.x = width + orb.radius
    if (orb.x > width + orb.radius) orb.x = -orb.radius
    if (orb.y < -orb.radius) orb.y = height + orb.radius
    if (orb.y > height + orb.radius) orb.y = -orb.radius

    const pulse = Math.sin(orb.pulsePhase) * 0.3 + 0.7
    const [r, g, b] = orb.color

    const grad = ctx!.createRadialGradient(orb.x, orb.y, 0, orb.x, orb.y, orb.radius * pulse)
    grad.addColorStop(0, `rgba(${Math.min(r + 12, 255)}, ${Math.min(g + 10, 255)}, ${Math.min(b + 14, 255)}, 0.10)`)
    grad.addColorStop(0.3, `rgba(${r}, ${g}, ${b}, 0.045)`)
    grad.addColorStop(0.7, `rgba(${Math.max(r - 10, 0)}, ${Math.max(g - 10, 0)}, ${Math.max(b - 8, 0)}, 0.01)`)
    grad.addColorStop(1, `rgba(${Math.max(r - 20, 0)}, ${Math.max(g - 20, 0)}, ${Math.max(b - 16, 0)}, 0)`)

    ctx!.fillStyle = grad
    ctx!.beginPath()
    ctx!.arc(orb.x, orb.y, orb.radius * pulse, 0, Math.PI * 2)
    ctx!.fill()
  })
}

function drawAmbientSpots(time: number) {
  if (!ctx) return

  const spots = [
    { x: width * 0.25, y: height * 0.35, size: width * 0.35, speed: 0.0004 },
    { x: width * 0.75, y: height * 0.6, size: width * 0.3, speed: 0.0006 },
    { x: width * 0.5, y: height * 0.45, size: width * 0.4, speed: 0.0003 },
  ]

  spots.forEach((spot, i) => {
    const pulseX = spot.x + Math.sin(time * spot.speed + i) * 60
    const pulseY = spot.y + Math.cos(time * spot.speed * 0.7 + i * 2) * 40

    const grad = ctx!.createRadialGradient(pulseX, pulseY, 0, pulseX, pulseY, spot.size)
    grad.addColorStop(0, 'rgba(64, 98, 134, 0.05)')
    grad.addColorStop(0.5, 'rgba(58, 88, 122, 0.02)')
    grad.addColorStop(1, 'rgba(48, 74, 106, 0)')
    ctx!.fillStyle = grad
    ctx!.beginPath()
    ctx!.arc(pulseX, pulseY, spot.size, 0, Math.PI * 2)
    ctx!.fill()
  })
}

function drawDataStreams(time: number) {
  if (!ctx) return
  const streamCount = 3
  const streams = [
    { x: width * 0.08, direction: 1, chars: '01' },
    { x: width * 0.92, direction: -1, chars: '01' },
    { x: width * 0.5, direction: 1, chars: '01' },
  ]
  
  ctx!.font = '10px monospace'
  ctx!.textAlign = 'center'
  
  streams.forEach((s, si) => {
    for (let i = 0; i < 15; i++) {
      const y = ((time * 0.08 * s.direction + i * 40 + si * 200) % (height + 100)) - 50
      const char = s.chars[Math.floor((time * 0.01 + i + si) % s.chars.length)]
      const alpha = (1 - Math.abs(height / 2 - y) / (height / 2)) * 0.08
      ctx!.fillStyle = `rgba(4, 80, 100, ${alpha})`
      ctx!.fillText(char, s.x, y)
    }
  })
}

function animate(time: number) {
  if (!ctx) return
  
  ctx.clearRect(0, 0, width, height)

  drawBackground()
  drawAmbientSpots(time)
  drawGlowOrbs(time)

  animationId = requestAnimationFrame(animate)
}

onMounted(() => {
  resize()
  window.addEventListener('resize', resize)
  animate(0)
})

onUnmounted(() => {
  window.removeEventListener('resize', resize)
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
})
</script>

<style scoped>
.tech-particle-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0;
  pointer-events: none;
}
</style>
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

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  radius: number
  opacity: number
  color: string
  pulsePhase: number
  pulseSpeed: number
}

interface FlowLine {
  x: number
  y: number
  length: number
  angle: number
  speed: number
  opacity: number
  width: number
}

interface GlowOrb {
  x: number
  y: number
  vx: number
  vy: number
  radius: number
  color: [number, number, number]
  pulsePhase: number
}

interface RisingDot {
  x: number
  y: number
  speed: number
  size: number
  opacity: number
  trail: { x: number; y: number }[]
}

interface TechRing {
  cx: number
  cy: number
  radius: number
  rotationSpeed: number
  arcCount: number
  opacity: number
}

let particles: Particle[] = []
let flowLines: FlowLine[] = []
let glowOrbs: GlowOrb[] = []
let risingDots: RisingDot[] = []
let techRings: TechRing[] = []

function initParticles() {
  particles = []
  const particleCount = Math.floor((width * height) / 6500)
  
  const colors = [
    'rgba(0, 220, 255,',
    'rgba(0, 240, 255,',
    'rgba(100, 220, 255,',
    'rgba(150, 230, 255,',
    'rgba(0, 190, 255,',
    'rgba(0, 255, 255,',
    'rgba(255, 255, 255,',
  ]

  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.7,
      vy: (Math.random() - 0.5) * 0.7,
      radius: Math.random() * 2.8 + 0.8,
      opacity: Math.random() * 0.7 + 0.3,
      color: colors[Math.floor(Math.random() * colors.length)],
      pulsePhase: Math.random() * Math.PI * 2,
      pulseSpeed: Math.random() * 0.03 + 0.01
    })
  }
}

function initFlowLines() {
  flowLines = []
  const lineCount = Math.floor(width / 18)
  
  for (let i = 0; i < lineCount; i++) {
    flowLines.push({
      x: Math.random() * width,
      y: Math.random() * height,
      length: Math.random() * 180 + 80,
      angle: Math.random() * Math.PI * 2,
      speed: Math.random() * 1.8 + 0.7,
      opacity: Math.random() * 0.35 + 0.12,
      width: Math.random() * 2.5 + 0.8
    })
  }
}

function initGlowOrbs() {
  glowOrbs = []
  const orbColors: [number, number, number][] = [
    [0, 180, 255],
    [0, 220, 255],
    [80, 200, 255],
    [0, 200, 230],
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

function initRisingDots() {
  risingDots = []
  const count = Math.floor(width / 50)
  for (let i = 0; i < count; i++) {
    const x = Math.random() * width
    risingDots.push({
      x,
      y: height + Math.random() * height,
      speed: Math.random() * 1.5 + 0.5,
      size: Math.random() * 2 + 1,
      opacity: Math.random() * 0.5 + 0.2,
      trail: []
    })
  }
}

function initTechRings() {
  techRings = [
    { cx: width * 0.1, cy: height * 0.15, radius: Math.min(width, height) * 0.08, rotationSpeed: 0.003, arcCount: 4, opacity: 0.12 },
    { cx: width * 0.9, cy: height * 0.2, radius: Math.min(width, height) * 0.1, rotationSpeed: -0.004, arcCount: 6, opacity: 0.08 },
    { cx: width * 0.15, cy: height * 0.85, radius: Math.min(width, height) * 0.07, rotationSpeed: 0.005, arcCount: 3, opacity: 0.1 },
    { cx: width * 0.85, cy: height * 0.8, radius: Math.min(width, height) * 0.09, rotationSpeed: -0.0035, arcCount: 5, opacity: 0.09 },
  ]
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
  initParticles()
  initFlowLines()
  initGlowOrbs()
  initRisingDots()
  initTechRings()
}

function drawBackground() {
  if (!ctx) return
  
  const bgGrad = ctx.createLinearGradient(0, 0, 0, height)
  bgGrad.addColorStop(0, '#0d5cb8')
  bgGrad.addColorStop(0.3, '#0c52a8')
  bgGrad.addColorStop(0.7, '#094494')
  bgGrad.addColorStop(1, '#063880')
  ctx.fillStyle = bgGrad
  ctx.fillRect(0, 0, width, height)

  const bgGrad2 = ctx.createRadialGradient(
    width * 0.5, height * 0.15, 0,
    width * 0.5, height * 0.15, width * 0.9
  )
  bgGrad2.addColorStop(0, 'rgba(40, 140, 240, 0.5)')
  bgGrad2.addColorStop(0.4, 'rgba(25, 100, 200, 0.2)')
  bgGrad2.addColorStop(1, 'rgba(0, 70, 160, 0)')
  ctx.fillStyle = bgGrad2
  ctx.fillRect(0, 0, width, height)

  const glowCenter = ctx.createRadialGradient(
    width * 0.2, height * 0.25, 0,
    width * 0.2, height * 0.25, width * 0.45
  )
  glowCenter.addColorStop(0, 'rgba(0, 200, 255, 0.22)')
  glowCenter.addColorStop(0.5, 'rgba(0, 150, 240, 0.08)')
  glowCenter.addColorStop(1, 'rgba(0, 100, 200, 0)')
  ctx.fillStyle = glowCenter
  ctx.fillRect(0, 0, width, height)

  const glowCenter2 = ctx.createRadialGradient(
    width * 0.85, height * 0.75, 0,
    width * 0.85, height * 0.75, width * 0.4
  )
  glowCenter2.addColorStop(0, 'rgba(0, 220, 255, 0.18)')
  glowCenter2.addColorStop(0.5, 'rgba(0, 170, 245, 0.07)')
  glowCenter2.addColorStop(1, 'rgba(0, 120, 220, 0)')
  ctx.fillStyle = glowCenter2
  ctx.fillRect(0, 0, width, height)
}

function drawHexGrid(time: number) {
  if (!ctx) return
  const size = 50
  const h = size * Math.sqrt(3) / 2
  ctx.strokeStyle = 'rgba(100, 200, 255, 0.04)'
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
    
    ctx!.strokeStyle = `rgba(0, 220, 255, ${0.3 * pulse})`
    ctx!.lineWidth = 2
    ctx!.beginPath()
    ctx!.moveTo(c.x - dx * len, c.y)
    ctx!.lineTo(c.x, c.y)
    ctx!.lineTo(c.x, c.y - dy * len)
    ctx!.stroke()
    
    ctx!.fillStyle = `rgba(0, 240, 255, ${0.6 * pulse})`
    ctx!.beginPath()
    ctx!.arc(c.x, c.y, 3, 0, Math.PI * 2)
    ctx!.fill()
    
    ctx!.strokeStyle = `rgba(0, 200, 255, ${0.15 * pulse})`
    ctx!.lineWidth = 1
    ctx!.beginPath()
    ctx!.moveTo(c.x - dx * (len + 25), c.y)
    ctx!.lineTo(c.x - dx * len, c.y)
    ctx!.moveTo(c.x, c.y - dy * (len + 25))
    ctx!.lineTo(c.x, c.y - dy * len)
    ctx!.stroke()
  })
}

function drawTechRings(time: number) {
  if (!ctx) return
  
  techRings.forEach(ring => {
    for (let layer = 0; layer < 3; layer++) {
      ctx!.save()
      ctx!.translate(ring.cx, ring.cy)
      const r = ring.radius + layer * 18
      const dir = layer % 2 === 0 ? 1 : -1
      ctx!.rotate(time * ring.rotationSpeed * dir)
      
      ctx!.strokeStyle = `rgba(0, 210, 255, ${ring.opacity * (1 - layer * 0.28)})`
      ctx!.lineWidth = 1.5 - layer * 0.35
      ctx!.setLineDash(layer === 0 ? [] : [8, 6])
      
      for (let a = 0; a < ring.arcCount; a++) {
        const startAngle = (Math.PI * 2 / ring.arcCount) * a
        const arcLen = Math.PI * 2 / ring.arcCount * 0.65
        ctx!.beginPath()
        ctx!.arc(0, 0, r, startAngle, startAngle + arcLen)
        ctx!.stroke()
      }
      ctx!.setLineDash([])
      ctx!.restore()
    }
    
    ctx!.save()
    ctx!.translate(ring.cx, ring.cy)
    ctx!.rotate(time * ring.rotationSpeed * 2.5)
    const dotCount = 8
    for (let d = 0; d < dotCount; d++) {
      const angle = (Math.PI * 2 / dotCount) * d
      const dr = ring.radius
      const dx = Math.cos(angle) * dr
      const dy = Math.sin(angle) * dr
      const dotAlpha = ring.opacity * 2.5 * (Math.sin(time * 0.005 + d) * 0.4 + 0.6)
      ctx!.fillStyle = `rgba(180, 240, 255, ${dotAlpha})`
      ctx!.beginPath()
      ctx!.arc(dx, dy, 2.5, 0, Math.PI * 2)
      ctx!.fill()
    }
    ctx!.restore()
  })
}

function drawScanLine(time: number) {
  if (!ctx) return
  const scanY = ((time * 0.15) % (height + 100)) - 50
  
  const scanGrad = ctx.createLinearGradient(0, scanY - 40, 0, scanY + 40)
  scanGrad.addColorStop(0, 'rgba(0, 220, 255, 0)')
  scanGrad.addColorStop(0.4, 'rgba(0, 220, 255, 0.03)')
  scanGrad.addColorStop(0.5, 'rgba(0, 240, 255, 0.08)')
  scanGrad.addColorStop(0.6, 'rgba(0, 220, 255, 0.03)')
  scanGrad.addColorStop(1, 'rgba(0, 220, 255, 0)')
  
  ctx.fillStyle = scanGrad
  ctx.fillRect(0, scanY - 40, width, 80)
  
  ctx.strokeStyle = 'rgba(0, 240, 255, 0.15)'
  ctx.lineWidth = 1
  ctx.beginPath()
  ctx.moveTo(0, scanY)
  ctx.lineTo(width, scanY)
  ctx.stroke()
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
    grad.addColorStop(0, `rgba(${r + 40}, ${g + 30}, ${b}, 0.22)`)
    grad.addColorStop(0.3, `rgba(${r}, ${g}, ${b}, 0.1)`)
    grad.addColorStop(0.7, `rgba(${r - 20}, ${g - 20}, ${b}, 0.03)`)
    grad.addColorStop(1, `rgba(${r - 30}, ${g - 30}, ${b}, 0)`)
    
    ctx!.fillStyle = grad
    ctx!.beginPath()
    ctx!.arc(orb.x, orb.y, orb.radius * pulse, 0, Math.PI * 2)
    ctx!.fill()
  })
}

function drawFlowLines(time: number) {
  if (!ctx) return
  
  flowLines.forEach(line => {
    line.x += Math.cos(line.angle) * line.speed
    line.y += Math.sin(line.angle) * line.speed
    
    if (line.x < -200) line.x = width + 200
    if (line.x > width + 200) line.x = -200
    if (line.y < -200) line.y = height + 200
    if (line.y > height + 200) line.y = -200
    
    const endX = line.x + Math.cos(line.angle) * line.length
    const endY = line.y + Math.sin(line.angle) * line.length
    
    const grad = ctx!.createLinearGradient(line.x, line.y, endX, endY)
    const pulse = Math.sin(time * 0.003 + line.x * 0.01) * 0.3 + 0.7
    grad.addColorStop(0, `rgba(100, 220, 255, 0)`)
    grad.addColorStop(0.25, `rgba(150, 235, 255, ${line.opacity * pulse * 1.5})`)
    grad.addColorStop(0.5, `rgba(200, 245, 255, ${line.opacity * pulse * 1.8})`)
    grad.addColorStop(0.75, `rgba(150, 235, 255, ${line.opacity * pulse * 1.2})`)
    grad.addColorStop(1, `rgba(200, 245, 255, 0)`)
    
    ctx!.strokeStyle = grad
    ctx!.lineWidth = line.width
    ctx!.lineCap = 'round'
    ctx!.beginPath()
    ctx!.moveTo(line.x, line.y)
    ctx!.lineTo(endX, endY)
    ctx!.stroke()
    
    const headPulse = Math.sin(time * 0.005 + line.y * 0.02) * 0.4 + 0.6
    ctx!.fillStyle = `rgba(220, 250, 255, ${headPulse * line.opacity * 2})`
    ctx!.beginPath()
    ctx!.arc(endX, endY, line.width * 1.5, 0, Math.PI * 2)
    ctx!.fill()
  })
}

function drawRisingDots(time: number) {
  if (!ctx) return
  
  risingDots.forEach(dot => {
    dot.y -= dot.speed
    dot.trail.unshift({ x: dot.x, y: dot.y })
    if (dot.trail.length > 12) dot.trail.pop()
    
    if (dot.y < -20) {
      dot.y = height + 20
      dot.x = Math.random() * width
      dot.trail = []
    }
    
    dot.trail.forEach((t, i) => {
      const alpha = (1 - i / dot.trail.length) * dot.opacity * 0.4
      const size = dot.size * (1 - i / dot.trail.length)
      ctx!.fillStyle = `rgba(0, 200, 255, ${alpha})`
      ctx!.beginPath()
      ctx!.arc(t.x, t.y, size * 0.5, 0, Math.PI * 2)
      ctx!.fill()
    })
    
    const glowGrad = ctx!.createRadialGradient(dot.x, dot.y, 0, dot.x, dot.y, dot.size * 6)
    glowGrad.addColorStop(0, `rgba(0, 230, 255, ${dot.opacity * 0.8})`)
    glowGrad.addColorStop(0.3, `rgba(0, 200, 255, ${dot.opacity * 0.3})`)
    glowGrad.addColorStop(1, 'rgba(0, 180, 255, 0)')
    ctx!.fillStyle = glowGrad
    ctx!.beginPath()
    ctx!.arc(dot.x, dot.y, dot.size * 6, 0, Math.PI * 2)
    ctx!.fill()
    
    ctx!.fillStyle = `rgba(255, 255, 255, ${dot.opacity})`
    ctx!.beginPath()
    ctx!.arc(dot.x, dot.y, dot.size, 0, Math.PI * 2)
    ctx!.fill()
  })
}

function drawParticles(time: number) {
  if (!ctx) return
  
  particles.forEach(p => {
    p.x += p.vx
    p.y += p.vy
    p.pulsePhase += p.pulseSpeed
    
    if (p.x < -10) p.x = width + 10
    if (p.x > width + 10) p.x = -10
    if (p.y < -10) p.y = height + 10
    if (p.y > height + 10) p.y = -10
    
    const pulse = Math.sin(p.pulsePhase) * 0.35 + 0.65
    const currentOpacity = p.opacity * pulse
    const currentRadius = p.radius * (0.8 + pulse * 0.5)
    
    const glowRadius = currentRadius * 6
    const glow = ctx!.createRadialGradient(p.x, p.y, 0, p.x, p.y, glowRadius)
    glow.addColorStop(0, p.color + (currentOpacity * 0.9) + ')')
    glow.addColorStop(0.25, p.color + (currentOpacity * 0.4) + ')')
    glow.addColorStop(0.6, p.color + (currentOpacity * 0.1) + ')')
    glow.addColorStop(1, p.color + '0)')
    ctx!.fillStyle = glow
    ctx!.beginPath()
    ctx!.arc(p.x, p.y, glowRadius, 0, Math.PI * 2)
    ctx!.fill()
    
    ctx!.fillStyle = p.color + Math.min(currentOpacity * 1.3, 1) + ')'
    ctx!.beginPath()
    ctx!.arc(p.x, p.y, currentRadius, 0, Math.PI * 2)
    ctx!.fill()
    
    ctx!.fillStyle = 'rgba(255, 255, 255, ' + (currentOpacity * 0.9) + ')'
    ctx!.beginPath()
    ctx!.arc(p.x, p.y, currentRadius * 0.45, 0, Math.PI * 2)
    ctx!.fill()
    
    if (currentRadius > 2) {
      ctx!.fillStyle = 'rgba(255, 255, 255, ' + (currentOpacity * 0.5) + ')'
      ctx!.beginPath()
      ctx!.arc(p.x - currentRadius * 0.3, p.y - currentRadius * 0.3, currentRadius * 0.2, 0, Math.PI * 2)
      ctx!.fill()
    }
  })
}

function drawConnections(time: number) {
  if (!ctx) return
  
  const connectionDistance = 140
  
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const dx = particles[i].x - particles[j].x
      const dy = particles[i].y - particles[j].y
      const dist = Math.sqrt(dx * dx + dy * dy)
      
      if (dist < connectionDistance) {
        const opacity = (1 - dist / connectionDistance) * 0.35
        const pulse = Math.sin(time * 0.002 + i * 0.1) * 0.25 + 0.75
        
        ctx!.strokeStyle = `rgba(100, 210, 255, ${opacity * pulse})`
        ctx!.lineWidth = 0.7
        ctx!.beginPath()
        ctx!.moveTo(particles[i].x, particles[i].y)
        ctx!.lineTo(particles[j].x, particles[j].y)
        ctx!.stroke()
      }
    }
  }
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
    grad.addColorStop(0, 'rgba(0, 150, 230, 0.06)')
    grad.addColorStop(0.5, 'rgba(0, 110, 200, 0.02)')
    grad.addColorStop(1, 'rgba(0, 70, 170, 0)')
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
      ctx!.fillStyle = `rgba(0, 230, 255, ${alpha})`
      ctx!.fillText(char, s.x, y)
    }
  })
}

function animate(time: number) {
  if (!ctx) return
  
  ctx.clearRect(0, 0, width, height)
  
  drawBackground()
  drawHexGrid(time)
  drawAmbientSpots(time)
  drawGlowOrbs(time)
  drawDataStreams(time)
  drawTechRings(time)
  drawScanLine(time)
  drawRisingDots(time)
  drawFlowLines(time)
  drawConnections(time)
  drawParticles(time)
  drawCornerFrames(time)
  
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

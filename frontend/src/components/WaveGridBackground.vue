<template>
  <div class="wave-grid-container" aria-hidden="true">
    <canvas ref="canvas" class="wave-grid-canvas"></canvas>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

type WaveParticle = {
  x: number
  y: number
  z: number
  vx: number
  vz: number
  size: number
  alpha: number
  color: number[]
  trail: { x: number; y: number; alpha: number }[]
}

const canvas = ref<HTMLCanvasElement | null>(null)
let ctx: CanvasRenderingContext2D | null = null
let frameId = 0
let width = 0
let height = 0
let particles: WaveParticle[] = []
let reduceMotion = false
let time = 0

const cyan = [78, 216, 255]
const lightCyan = [140, 235, 255]
const gold = [255, 214, 107]

const gridConfig = {
  horizonRatio: 0.35,
  cellSize: 60,
  rows: 25,
  cols: 40,
  waveAmplitude: 18,
  waveSpeed: 0.8,
  waveFrequency: 0.025
}

function safeNum(v: number, fallback = 0): number {
  return isFinite(v) ? v : fallback
}

onMounted(() => {
  try {
    reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    ctx = canvas.value?.getContext('2d') || null
    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)
    if (reduceMotion) {
      draw(0)
    } else {
      frameId = window.requestAnimationFrame(draw)
    }
  } catch (e) {
    console.error('WaveGridBackground init error:', e)
  }
})

onBeforeUnmount(() => {
  window.cancelAnimationFrame(frameId)
  window.removeEventListener('resize', resizeCanvas)
})

function resizeCanvas() {
  try {
    if (!canvas.value || !ctx) return
    const ratio = Math.min(window.devicePixelRatio || 1, 2)
    width = Math.max(320, window.innerWidth || 800)
    height = Math.max(240, window.innerHeight || 600)
    canvas.value.width = Math.round(width * ratio)
    canvas.value.height = Math.round(height * ratio)
    canvas.value.style.width = `${width}px`
    canvas.value.style.height = `${height}px`
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0)
    initParticles()
  } catch (e) {
    console.error('WaveGridBackground resize error:', e)
  }
}

function initParticles() {
  particles = []
  const count = Math.max(40, Math.min(80, Math.round(width / 20)))
  for (let i = 0; i < count; i++) {
    const isGold = Math.random() < 0.15
    particles.push({
      x: (Math.random() - 0.5) * gridConfig.cols * gridConfig.cellSize,
      y: 0,
      z: 200 + Math.random() * (gridConfig.rows * gridConfig.cellSize - 400),
      vx: (Math.random() - 0.5) * 0.3,
      vz: 0.8 + Math.random() * 1.2,
      size: 1.5 + Math.random() * 2,
      alpha: 0.3 + Math.random() * 0.5,
      color: isGold ? gold : lightCyan,
      trail: []
    })
  }
}

function project(x: number, y: number, z: number): { sx: number; sy: number; scale: number } {
  const horizonY = height * gridConfig.horizonRatio
  const focalLength = height * 0.8
  const depth = Math.max(z + 1, 100)
  const scale = focalLength / depth
  const sx = width / 2 + x * scale
  const sy = horizonY + (y - horizonY * 0.3) * scale
  return {
    sx: safeNum(sx, width / 2),
    sy: safeNum(sy, height / 2),
    scale: safeNum(scale / focalLength, 0.001)
  }
}

function waveOffset(x: number, z: number, t: number): number {
  try {
    const dist = Math.sqrt(x * x + z * z) * gridConfig.waveFrequency
    const wave1 = Math.sin(dist - t * gridConfig.waveSpeed) * gridConfig.waveAmplitude
    const wave2 = Math.sin(x * gridConfig.waveFrequency * 0.7 + t * gridConfig.waveSpeed * 0.6) * gridConfig.waveAmplitude * 0.5
    const wave3 = Math.cos(z * gridConfig.waveFrequency * 0.5 - t * gridConfig.waveSpeed * 0.4) * gridConfig.waveAmplitude * 0.3
    return safeNum(wave1 + wave2 + wave3, 0)
  } catch {
    return 0
  }
}

function draw(timestamp: number) {
  try {
    if (!ctx || width <= 0 || height <= 0) return
    time = safeNum(timestamp / 1000, 0)

    ctx.fillStyle = 'rgba(2, 8, 20, 0.25)'
    ctx.fillRect(0, 0, width, height)

    drawSky()
    drawWavyGrid()
    updateAndDrawParticles()
  } catch (e) {
    console.error('WaveGridBackground draw error:', e)
  }

  if (!reduceMotion) {
    frameId = window.requestAnimationFrame(draw)
  }
}

function drawSky() {
  if (!ctx || width <= 0 || height <= 0) return
  try {
    const horizonY = height * gridConfig.horizonRatio
    if (!isFinite(horizonY) || horizonY <= 0) return

    const skyGrad = ctx.createLinearGradient(0, 0, 0, horizonY)
    skyGrad.addColorStop(0, 'rgba(4, 12, 28, 1)')
    skyGrad.addColorStop(0.6, 'rgba(6, 22, 48, 0.95)')
    skyGrad.addColorStop(1, 'rgba(8, 32, 64, 0.9)')
    ctx.fillStyle = skyGrad
    ctx.fillRect(0, 0, width, horizonY + 2)

    const glowRadius = width * 0.6
    if (isFinite(glowRadius) && glowRadius > 0) {
      const glowGrad = ctx.createRadialGradient(width / 2, horizonY, 0, width / 2, horizonY, glowRadius)
      glowGrad.addColorStop(0, 'rgba(78, 216, 255, 0.12)')
      glowGrad.addColorStop(0.3, 'rgba(78, 216, 255, 0.05)')
      glowGrad.addColorStop(1, 'rgba(78, 216, 255, 0)')
      ctx.fillStyle = glowGrad
      ctx.fillRect(0, 0, width, horizonY + 50)
    }
  } catch (e) {
    console.error('WaveGridBackground drawSky error:', e)
  }
}

function drawWavyGrid() {
  if (!ctx || width <= 0 || height <= 0) return
  try {
    const cellSize = gridConfig.cellSize
    const halfCols = gridConfig.cols / 2

    for (let row = 0; row < gridConfig.rows; row++) {
      const z1 = row * cellSize
      const z2 = (row + 1) * cellSize
      const rowFade = 1 - row / gridConfig.rows
      const alpha = safeNum(0.15 + rowFade * 0.35, 0.2)

      ctx.beginPath()
      let started = false
      for (let col = -halfCols; col <= halfCols; col++) {
        const x = col * cellSize
        const y1 = waveOffset(x, z1, time)
        const y2 = waveOffset(x, z2, time)
        const p1 = project(x, y1, z1)
        const p2 = project(x, y2, z2)

        if (!isFinite(p1.sx) || !isFinite(p1.sy) || !isFinite(p2.sx) || !isFinite(p2.sy)) continue

        if (!started) {
          ctx.moveTo(p1.sx, p1.sy)
          started = true
        }

        const nextX = (col + 1) * cellSize
        const ny1 = waveOffset(nextX, z1, time)
        const np1 = project(nextX, ny1, z1)
        if (isFinite(np1.sx) && isFinite(np1.sy)) {
          ctx.lineTo(np1.sx, np1.sy)
        }

        if (row < gridConfig.rows - 1 && col >= -halfCols) {
          ctx.moveTo(p1.sx, p1.sy)
          ctx.lineTo(p2.sx, p2.sy)
        }
      }
      ctx.strokeStyle = `rgba(${cyan.join(',')}, ${alpha})`
      ctx.lineWidth = safeNum(0.8 + rowFade * 1.2, 1)
      ctx.stroke()
    }

    for (let col = -halfCols; col <= halfCols; col += 2) {
      const x = col * cellSize
      const colCenter = Math.abs(col) / halfCols
      const alpha = safeNum(0.1 + (1 - colCenter) * 0.25, 0.15)

      ctx.beginPath()
      let started = false
      for (let row = 0; row < gridConfig.rows; row++) {
        const z = row * cellSize
        const y = waveOffset(x, z, time)
        const p = project(x, y, z)
        if (!isFinite(p.sx) || !isFinite(p.sy)) continue
        if (!started) {
          ctx.moveTo(p.sx, p.sy)
          started = true
        } else {
          ctx.lineTo(p.sx, p.sy)
        }
      }
      ctx.strokeStyle = `rgba(${cyan.join(',')}, ${alpha})`
      ctx.lineWidth = safeNum(0.6 + (1 - colCenter) * 1, 0.6)
      ctx.stroke()
    }

    const horizonY = height * gridConfig.horizonRatio
    if (isFinite(horizonY)) {
      ctx.strokeStyle = `rgba(${cyan.join(',')}, 0.5)`
      ctx.lineWidth = 1.5
      ctx.beginPath()
      ctx.moveTo(0, horizonY)
      ctx.lineTo(width, horizonY)
      ctx.stroke()

      const horizonGlow = ctx.createLinearGradient(0, horizonY - 30, 0, horizonY + 40)
      horizonGlow.addColorStop(0, `rgba(${cyan.join(',')}, 0)`)
      horizonGlow.addColorStop(0.5, `rgba(${cyan.join(',')}, 0.25)`)
      horizonGlow.addColorStop(1, `rgba(${cyan.join(',')}, 0)`)
      ctx.fillStyle = horizonGlow
      ctx.fillRect(0, horizonY - 30, width, 70)
    }
  } catch (e) {
    console.error('WaveGridBackground drawWavyGrid error:', e)
  }
}

function updateAndDrawParticles() {
  if (!ctx || width <= 0 || height <= 0) return
  try {
    const cellSize = gridConfig.cellSize
    const maxZ = gridConfig.rows * cellSize
    const halfCols = gridConfig.cols / 2

    particles.forEach(p => {
      try {
        p.x += p.vx
        p.z -= p.vz

        if (p.z < 200) {
          p.z = gridConfig.rows * gridConfig.cellSize - 100
          p.x = (Math.random() - 0.5) * gridConfig.cols * gridConfig.cellSize
          p.trail = []
        }
        if (Math.abs(p.x) > halfCols * cellSize) {
          p.x = (p.x > 0 ? -1 : 1) * halfCols * cellSize
        }

        p.y = waveOffset(p.x, p.z, time)

        const pos = project(p.x, p.y, p.z)

        if (!isFinite(pos.sx) || !isFinite(pos.sy) || !isFinite(pos.scale) || pos.scale <= 0) {
          return
        }

        p.trail.unshift({ x: pos.sx, y: pos.sy, alpha: p.alpha })
        if (p.trail.length > 12) p.trail.pop()

        p.trail.forEach((t, i) => {
          t.alpha = safeNum(p.alpha * (1 - i / p.trail.length) * 0.5, 0)
        })

        const depthAlpha = Math.max(0.1, 1 - p.z / maxZ)
        const finalAlpha = safeNum(p.alpha * depthAlpha, 0.1)

        if (!isFinite(finalAlpha) || finalAlpha <= 0) return

        if (p.trail.length > 1) {
          ctx!.beginPath()
          ctx!.moveTo(safeNum(p.trail[0].x, pos.sx), safeNum(p.trail[0].y, pos.sy))
          for (let i = 1; i < p.trail.length; i++) {
            ctx!.lineTo(safeNum(p.trail[i].x, pos.sx), safeNum(p.trail[i].y, pos.sy))
          }
          const x0 = safeNum(p.trail[0].x, pos.sx)
          const y0 = safeNum(p.trail[0].y, pos.sy)
          const x1 = safeNum(p.trail[p.trail.length - 1].x, pos.sx)
          const y1 = safeNum(p.trail[p.trail.length - 1].y, pos.sy)
          if (isFinite(x0) && isFinite(y0) && isFinite(x1) && isFinite(y1)) {
            const trailGrad = ctx!.createLinearGradient(x0, y0, x1, y1)
            trailGrad.addColorStop(0, `rgba(${p.color.join(',')}, ${Math.min(1, Math.max(0, finalAlpha * 0.6))})`)
            trailGrad.addColorStop(1, `rgba(${p.color.join(',')}, 0)`)
            ctx!.strokeStyle = trailGrad
            ctx!.lineWidth = Math.max(0.1, safeNum(p.size * pos.scale * 1.5, 0.5))
            ctx!.lineCap = 'round'
            ctx!.stroke()
          }
        }

        const glowSize = Math.max(3, safeNum(p.size * pos.scale * 8, 4))
        if (isFinite(glowSize) && glowSize > 0 && isFinite(pos.sx) && isFinite(pos.sy)) {
          const glow = ctx!.createRadialGradient(pos.sx, pos.sy, 0, pos.sx, pos.sy, glowSize)
          glow.addColorStop(0, `rgba(${p.color.join(',')}, ${Math.min(1, Math.max(0, finalAlpha * 0.9))})`)
          glow.addColorStop(0.25, `rgba(${p.color.join(',')}, ${Math.min(1, Math.max(0, finalAlpha * 0.5))})`)
          glow.addColorStop(0.5, `rgba(${p.color.join(',')}, ${Math.min(1, Math.max(0, finalAlpha * 0.15))})`)
          glow.addColorStop(1, `rgba(${p.color.join(',')}, 0)`)
          ctx!.fillStyle = glow
          ctx!.beginPath()
          ctx!.arc(pos.sx, pos.sy, glowSize, 0, Math.PI * 2)
          ctx!.fill()
        }

        if (isFinite(pos.sx) && isFinite(pos.sy)) {
          ctx!.fillStyle = `rgba(255, 255, 255, ${Math.min(1, Math.max(0, finalAlpha * 0.95))})`
          ctx!.beginPath()
          ctx!.arc(pos.sx, pos.sy, Math.max(0.3, safeNum(p.size * pos.scale * 0.8, 0.6)), 0, Math.PI * 2)
          ctx!.fill()
        }
      } catch (e) {
        // silently skip individual particle errors
      }
    })
  } catch (e) {
    console.error('WaveGridBackground updateAndDrawParticles error:', e)
  }
}
</script>

<style scoped>
.wave-grid-container {
  position: fixed;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
  background: linear-gradient(180deg, #01040a 0%, #020a16 40%, #030f1c 100%);
}

.wave-grid-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}
</style>

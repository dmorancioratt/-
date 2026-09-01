<template>
  <svg
    v-if="layer.w > 0 && layer.h > 0"
    class="auto-fit-frames"
    :viewBox="`0 0 ${layer.w} ${layer.h}`"
    :style="{ width: `${layer.w}px`, height: `${layer.h}px` }"
    aria-hidden="true"
  >
    <defs>
      <linearGradient id="affStroke" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#5ee7ff" stop-opacity=".95"/>
        <stop offset="48%" stop-color="#7ce2ff" stop-opacity=".78"/>
        <stop offset="100%" stop-color="#9ab7ff" stop-opacity=".88"/>
      </linearGradient>
      <linearGradient id="affGlow" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#5ee7ff" stop-opacity=".16"/>
        <stop offset="55%" stop-color="#7ce2ff" stop-opacity=".08"/>
        <stop offset="100%" stop-color="#6ad9ff" stop-opacity=".14"/>
      </linearGradient>
      <filter id="affBlur" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="2.2"/>
      </filter>
    </defs>

    <g v-for="f in rendered" :key="f.id" :opacity="f.opacity">
      <!-- 成就墙：平行四边形（左下斜切接地面，右下包全） -->
      <template v-if="f.kind === 'parallelogram'">
        <polygon :points="f.shape" fill="url(#affGlow)" opacity=".95" filter="url(#affBlur)"/>
        <polygon :points="f.shape" fill="none" stroke="url(#affStroke)" :stroke-width="f.ui.stroke" stroke-linejoin="round"/>
        <path :d="f.groundLine" fill="none" stroke="#6ae2ff" :stroke-width="f.ui.stroke * .8" opacity=".95"/>
        <circle v-for="c in f.corners" :key="c.x + '-' + c.y" :cx="c.x" :cy="c.y" :r="f.ui.dot" fill="#e7fbff"/>
        <rect :x="f.ui.tag.x" :y="f.ui.tag.y" rx="8" ry="8" :width="f.ui.tag.w" :height="f.ui.tag.h"
              fill="rgba(6, 34, 61, .92)" stroke="url(#affStroke)" stroke-width="1.2"/>
        <text :x="f.ui.tag.x + f.ui.tag.w / 2" :y="f.ui.tag.y + f.ui.tag.h * .64" text-anchor="middle"
              fill="#d6f7ff" :font-size="f.ui.font" font-weight="700"
              font-family="Microsoft YaHei, PingFang SC, sans-serif" letter-spacing="2">{{ f.title }}</text>
        <rect :x="f.ui.btn.x" :y="f.ui.btn.y" rx="19" ry="19" :width="f.ui.btn.w" :height="f.ui.btn.h"
              fill="rgba(5, 35, 68, .94)" stroke="url(#affStroke)" stroke-width="1.4"/>
        <circle :cx="f.ui.btn.x + f.ui.btn.h / 2" :cy="f.ui.btn.y + f.ui.btn.h / 2" :r="f.ui.btn.h * .16" fill="#6ae2ff" opacity=".95"/>
        <text :x="f.ui.btn.x + f.ui.btn.h * .9" :y="f.ui.btn.y + f.ui.btn.h * .64"
              fill="#dff9ff" :font-size="f.ui.font" font-weight="700"
              font-family="Microsoft YaHei, PingFang SC, sans-serif">点击进入{{ f.title }}</text>
      </template>

      <!-- 资源库：长方形外框 + 下底座（贴在一起） -->
      <template v-else-if="f.kind === 'rectBase'">
        <rect :x="f.box.x" :y="f.box.y" :width="f.box.w" :height="f.box.h" :rx="radius" :ry="radius"
              fill="url(#affGlow)" opacity=".9" filter="url(#affBlur)"/>
        <rect :x="f.box.x" :y="f.box.y" :width="f.box.w" :height="f.box.h" :rx="radius" :ry="radius"
              fill="none" stroke="url(#affStroke)" :stroke-width="f.ui.stroke * 1.1"/>
        <rect :x="f.base.x" :y="f.base.y" :width="f.base.w" :height="f.base.h"
              :ry="Math.min(18, f.base.h / 2)"
              fill="rgba(78, 216, 255, .12)" stroke="url(#affStroke)" stroke-width="1.4"/>
        <line :x1="f.base.x + f.base.w * .18" :y1="f.base.y + f.base.h * .3"
              :x2="f.base.x + f.base.w * .82" :y2="f.base.y + f.base.h * .3"
              stroke="url(#affStroke)" stroke-width="2.4" stroke-linecap="round" opacity=".95"/>
        <line :x1="f.base.x + f.base.w * .26" :y1="f.base.y + f.base.h - 6"
              :x2="f.base.x + f.base.w * .74" :y2="f.base.y + f.base.h - 6"
              stroke="#8ec9ff" stroke-width="1.6" stroke-linecap="round" opacity=".55"/>
        <circle v-for="c in f.corners" :key="c.x + '-' + c.y" :cx="c.x" :cy="c.y" :r="f.ui.dot * .85" fill="#e7fbff"/>
        <rect :x="f.ui.tag.x" :y="f.ui.tag.y" rx="8" ry="8" :width="f.ui.tag.w" :height="f.ui.tag.h"
              fill="rgba(6, 34, 61, .92)" stroke="url(#affStroke)" stroke-width="1.2"/>
        <text :x="f.ui.tag.x + f.ui.tag.w / 2" :y="f.ui.tag.y + f.ui.tag.h * .64" text-anchor="middle"
              fill="#d6f7ff" :font-size="f.ui.font" font-weight="700"
              font-family="Microsoft YaHei, PingFang SC, sans-serif" letter-spacing="2">{{ f.title }}</text>
      </template>

      <!-- 其他模块：轻量虚线光边 -->
      <template v-else>
        <rect :x="f.box.x" :y="f.box.y" :width="f.box.w" :height="f.box.h" :rx="radius * .8" :ry="radius * .8"
              fill="url(#affGlow)" opacity=".7" filter="url(#affBlur)"/>
        <rect :x="f.box.x" :y="f.box.y" :width="f.box.w" :height="f.box.h" :rx="radius * .8" :ry="radius * .8"
              fill="none" stroke="url(#affStroke)" :stroke-width="f.ui.stroke * .9" stroke-dasharray="6 5"/>
      </template>
    </g>
  </svg>
</template>

<script setup lang="ts">
import { reactive, watch, onBeforeUnmount } from 'vue'

export type RawFrame = {
  id: string
  kind: 'parallelogram' | 'rectBase' | 'rect'
  title: string
  box: { x: number; y: number; w: number; h: number }
  visible: boolean
}

type SmoothBox = { x: number; y: number; w: number; h: number }

const props = withDefaults(defineProps<{
  frames: RawFrame[]
  layerW: number
  layerH: number
  /** 框内边距比例（0~1，相对框宽） */
  padding?: number
  /** 成就墙左下斜切比例（0~0.4，相对框宽） */
  skew?: number
  /** 描边宽度倍率 */
  strokeScale?: number
  /** 标签/按钮整体缩放（0.6~1.6） */
  uiScale?: number
  /** 整体透明度（0~1） */
  opacity?: number
  /** 平滑跟随系数（0.05~1，越小越"粘"） */
  smooth?: number
  /** 圆角半径 */
  radius?: number
}>(), {
  padding: 0.1,
  skew: 0.16,
  strokeScale: 1,
  uiScale: 1,
  opacity: 1,
  smooth: 0.22,
  radius: 18,
})

const layer = reactive({ w: 0, h: 0 })
const smooth = new Map<string, SmoothBox>()
const opacityMap = new Map<string, number>()
let rafId = 0
let running = false

const LERPS = () => Math.min(1, Math.max(0.05, props.smooth))

function charWidth(title: string) {
  let w = 0
  for (const ch of title) w += ch.charCodeAt(0) > 255 ? 14 : 7
  return w
}

// 自适应 UI 尺寸：标签/按钮宽度按文字长度自动算，整体随框大小缩放
function uiFor(box: SmoothBox, title: string) {
  const scale = Math.min(1.25, Math.max(0.7, Math.min(box.w / 320, box.h / 260))) * props.uiScale
  const font = Math.round(13 * scale)
  const tagW = charWidth(title) * scale + 34
  const tagH = Math.round(26 * scale)
  const btnW = charWidth(`点击进入${title}`) * scale + 64
  const btnH = Math.round(38 * scale)
  const cx = box.x + box.w / 2
  const tagX = Math.min(
    Math.max(6, box.x + 12),
    Math.max(6, Math.min(props.layerW - tagW - 6, cx - tagW / 2)),
  )
  return {
    scale,
    stroke: (1.2 + 0.9 * Math.min(1, box.w / 400)) * props.strokeScale,
    dot: 2 + 1.4 * Math.min(1, box.w / 400),
    font,
    tag: { x: tagX, y: box.y - tagH - 8, w: tagW, h: tagH },
    btn: {
      x: Math.min(Math.max(6, cx - btnW / 2), Math.max(6, props.layerW - btnW - 6)),
      y: box.y + box.h + 8,
      w: btnW,
      h: btnH,
    },
  }
}

function renderedFrames() {
  const lerp = LERPS()
  const pad = Math.max(0, Math.min(0.5, props.padding))
  return props.frames.map((raw) => {
    let box = smooth.get(raw.id)
    if (!box) {
      box = { ...raw.box }
      smooth.set(raw.id, box)
    }
    // 平滑跟随目标框（相机移动时不抖动）
    box.x += (raw.box.x - box.x) * lerp
    box.y += (raw.box.y - box.y) * lerp
    box.w += (raw.box.w - box.w) * lerp
    box.h += (raw.box.h - box.h) * lerp

    // 内边距可调：正值外扩，负值内收（用 -0.5~0.5 映射）
    const expand = pad * box.w
    const shown = { x: box.x - expand, y: box.y - expand * 0.6, w: box.w + expand * 2, h: box.h + expand * 1.2 }

    const targetOpacity = (raw.visible ? 1 : 0) * Math.max(0, Math.min(1, props.opacity))
    const prev = opacityMap.get(raw.id) ?? targetOpacity
    const next = prev + (targetOpacity - prev) * 0.18
    opacityMap.set(raw.id, next)

    const ui = uiFor(shown, raw.title)
    const shape: string[] = []
    let groundLine = ''
    const base = { x: 0, y: 0, w: 0, h: 0 }
    const corners = [
      { x: shown.x, y: shown.y },
      { x: shown.x + shown.w, y: shown.y },
      { x: shown.x + shown.w, y: shown.y + shown.h },
      { x: shown.x, y: shown.y + shown.h },
    ]

    if (raw.kind === 'parallelogram') {
      // 左下斜切（接地面）：比例可调，右下保持直角包全
      const skew = Math.max(6, Math.min(120, shown.w * Math.max(0, Math.min(0.4, props.skew))))
      const bl = { x: shown.x + skew, y: shown.y + shown.h }
      shape.push(`${shown.x},${shown.y}`, `${shown.x + shown.w},${shown.y}`, `${shown.x + shown.w},${shown.y + shown.h}`, `${bl.x},${bl.y}`)
      const groundExt = Math.min(56, skew + 18)
      groundLine = `M ${shown.x} ${shown.y + shown.h + 4} L ${bl.x + groundExt * .15} ${shown.y + shown.h + 1}`
      corners[3] = bl
    } else if (raw.kind === 'rectBase') {
      const baseH = Math.max(14, Math.min(36, shown.h * 0.14))
      base.x = shown.x + shown.w * 0.03
      base.y = shown.y + shown.h - 2
      base.w = shown.w * 0.94
      base.h = baseH
    }

    return {
      id: raw.id,
      kind: raw.kind,
      title: raw.title,
      box: shown,
      base,
      shape: shape.join(' '),
      groundLine,
      corners,
      ui,
      opacity: Math.round(next * 100) / 100,
    }
  })
}

const state = reactive({ list: [] as ReturnType<typeof renderedFrames> })

function tick() {
  if (!running) { rafId = 0; return }
  layer.w = props.layerW
  layer.h = props.layerH
  state.list = renderedFrames()
  rafId = requestAnimationFrame(tick)
}

watch(
  () => [props.frames, props.layerW, props.layerH],
  () => {
    layer.w = props.layerW
    layer.h = props.layerH
    if (!running) {
      running = true
      rafId = requestAnimationFrame(tick)
    }
  },
  { immediate: true },
)

onBeforeUnmount(() => { running = false; cancelAnimationFrame(rafId) })

const rendered = state.list
</script>

<style scoped>
.auto-fit-frames {
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
}
</style>

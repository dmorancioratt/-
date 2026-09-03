<template>
  <section class="image-cabin" :class="{ 'image-cabin--editing': editorEnabled }" aria-label="个人学习成长仓">
    <div class="image-cabin__ambience" aria-hidden="true"></div>

    <div v-if="false && showLayoutEditor" class="image-cabin__dev-controls" aria-label="成长仓开发工具">
      <button
        type="button"
        class="image-cabin__dev-button"
        :class="{ active: frameTunerOpen }"
        @click="toggleFrameTuner"
      >
        {{ frameTunerOpen ? '收起框调节' : '框调节' }}
      </button>
      <button
        type="button"
        class="image-cabin__dev-button"
        :class="{ active: editorEnabled }"
        @click="toggleEditor"
      >
        {{ editorEnabled ? '退出布局编辑' : '编辑布局' }}
      </button>
    </div>

    <aside
      v-if="showLayoutEditor && frameTunerOpen && selectedZone"
      class="image-cabin__tuner"
      aria-label="模块点击框调节面板"
    >
      <header>
        <span>IMAGE HOTSPOT TUNER</span>
        <strong>模块点击框调节</strong>
      </header>

      <label class="image-cabin__module-select">
        <span>当前模块</span>
        <select v-model="selectedModuleId">
          <option v-for="item in modules" :key="item.id" :value="item.id">{{ item.label }}</option>
        </select>
      </label>

      <label v-for="control in zoneControls" :key="control.key" class="image-cabin__tuner-row">
        <span>{{ control.label }}</span>
        <input
          type="range"
          :min="control.min"
          :max="controlMax(control.key)"
          :step="control.step"
          :value="selectedZone[control.key]"
          @input="updateSelectedZone(control.key, $event)"
        />
        <i>{{ selectedZone[control.key].toFixed(1) }}%</i>
      </label>

      <div class="image-cabin__tuner-actions">
        <button type="button" @click="resetSelectedZone">恢复当前</button>
        <button type="button" @click="copyZoneLayout">复制全部参数</button>
      </div>
      <p>{{ copyStatus || '点击图中框选择模块；拖动滑块会实时生效。' }}</p>
    </aside>

    <div class="image-cabin__canvas">
      <img class="image-cabin__image" src="/growth-cabin-overview-20260903.png" alt="个人学习成长仓模块总览" />
      <button
        v-for="item in modules"
        :key="item.id"
        type="button"
        class="image-cabin__zone"
        :class="[
          `image-cabin__zone--${item.id}`,
          { 'is-editing': editorEnabled, 'is-selected': editorEnabled && selectedModuleId === item.id },
        ]"
        :style="zoneStyle(item)"
        :aria-label="editorEnabled ? `选择${item.label}调节框` : `打开${item.label}`"
        @click="handleZoneClick(item)"
      >
        <span class="image-cabin__frame" aria-hidden="true"></span>
        <span class="image-cabin__hint">{{ editorEnabled ? `正在调节 ${item.label}` : `点击进入 ${item.label}` }}</span>
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { MissionCabinId } from './missionCabinData'

type ModuleZone = { id: MissionCabinId; label: string; x: number; y: number; width: number; height: number }
type ZoneMetric = 'x' | 'y' | 'width' | 'height'
type ZoneControl = { key: ZoneMetric; label: string; min: number; step: number }

const emit = defineEmits<{ select: [id: MissionCabinId] }>()
const showLayoutEditor = false

const defaultModules: ModuleZone[] = [
  { id: 'radar',            label: '能力图谱', x: 9.0,  y: 8.0,  width: 24.0, height: 30.0 },
  { id: 'path',             label: '学习路径', x: 33.5, y: 9.0,  width: 27.5, height: 29.0 },
  { id: 'avatar',           label: '成长档案', x: 63.0, y: 7.0,  width: 28.0, height: 25.0 },
  { id: 'resource-library', label: '资源库',   x: 3.0,  y: 39.0, width: 20.5, height: 52.0 },
  { id: 'ai-suggest',       label: 'AI 助手',  x: 35.5, y: 38.5, width: 22.5, height: 22.0 },
  { id: 'weekly-plan',      label: '计划日历', x: 64.5, y: 33.5, width: 25.5, height: 24.0 },
  { id: 'timeline',         label: '成就墙',   x: 64.5, y: 58.0, width: 31.0, height: 34.0 },
]

const modules = ref<ModuleZone[]>(defaultModules.map(item => ({ ...item })))
const editorEnabled = ref(false)
const frameTunerOpen = ref(false)
const selectedModuleId = ref<MissionCabinId>('radar')
const copyStatus = ref('')
let copyStatusTimer: number | undefined

const zoneControls: ZoneControl[] = [
  { key: 'x', label: '横向位置 X', min: 0, step: 0.1 },
  { key: 'y', label: '纵向位置 Y', min: 0, step: 0.1 },
  { key: 'width', label: '框宽度', min: 4, step: 0.1 },
  { key: 'height', label: '框高度', min: 4, step: 0.1 },
]

const selectedZone = computed(() => modules.value.find(item => item.id === selectedModuleId.value))

function zoneStyle(item: ModuleZone) {
  return { left: `${item.x}%`, top: `${item.y}%`, width: `${item.width}%`, height: `${item.height}%` }
}

function handleZoneClick(item: ModuleZone) {
  if (editorEnabled.value) {
    selectedModuleId.value = item.id
    return
  }
  emit('select', item.id)
}

function toggleFrameTuner() {
  frameTunerOpen.value = !frameTunerOpen.value
  if (frameTunerOpen.value) editorEnabled.value = true
}

function toggleEditor() {
  editorEnabled.value = !editorEnabled.value
  if (!editorEnabled.value) frameTunerOpen.value = false
}

function controlMax(key: ZoneMetric) {
  const zone = selectedZone.value
  if (!zone) return 100
  if (key === 'x') return 100 - zone.width
  if (key === 'y') return 100 - zone.height
  if (key === 'width') return 100 - zone.x
  return 100 - zone.y
}

function updateSelectedZone(key: ZoneMetric, event: Event) {
  const zone = selectedZone.value
  if (!zone) return
  zone[key] = Number((event.target as HTMLInputElement).value)
}

function resetSelectedZone() {
  const zone = selectedZone.value
  const defaults = defaultModules.find(item => item.id === selectedModuleId.value)
  if (!zone || !defaults) return
  Object.assign(zone, defaults)
  showCopyStatus('已恢复当前模块默认值')
}

async function copyZoneLayout() {
  try {
    await navigator.clipboard.writeText(JSON.stringify(modules.value, null, 2))
    showCopyStatus('全部模块参数已复制')
  } catch {
    showCopyStatus('复制失败，请检查浏览器剪贴板权限')
  }
}

function showCopyStatus(message: string) {
  copyStatus.value = message
  if (copyStatusTimer) window.clearTimeout(copyStatusTimer)
  copyStatusTimer = window.setTimeout(() => { copyStatus.value = '' }, 2200)
}
</script>

<style scoped>
.image-cabin { position: absolute; inset: 0; overflow: hidden; background: #020715; }
.image-cabin__ambience { position: absolute; inset: 0; background: linear-gradient(rgba(2, 7, 21, .54), rgba(2, 7, 21, .54)), url('/growth-cabin-overview-20260903.png') center / cover no-repeat; filter: blur(24px) saturate(.66) brightness(.44); transform: scale(1.08); }
/* 全屏铺满：去掉原来的 aspect-ratio 和宽高限制，让画布直接占满整个驾驶舱可视区（100% × 100%），
   图片用 object-fit: cover 按比例填满，不留黑边 */
.image-cabin__canvas { position: relative; z-index: 1; width: 100%; height: 100%; overflow: hidden; background: #020715; animation: cabin-reveal .7s ease-out both; }
.image-cabin__image { display: block; width: 100%; height: 100%; object-fit: cover; object-position: center center; user-select: none; -webkit-user-drag: none; }
.image-cabin__zone { position: absolute; z-index: 2; display: block; padding: 0; border: 0; border-radius: 8px; background: transparent; cursor: pointer; -webkit-tap-highlight-color: transparent; }
.image-cabin__frame { position: absolute; inset: 0; border: 1px solid rgba(82, 221, 255, 0); border-radius: inherit; background: rgba(17,49,66,0); box-shadow: inset 0 0 0 1px rgba(82,221,255,0), 0 0 0 rgba(82,221,255,0); transition: border-color .22s ease, background .22s ease, box-shadow .22s ease; pointer-events: none; }
.image-cabin__frame::before, .image-cabin__frame::after { content: ''; position: absolute; inset: clamp(4px, .45vw, 8px); opacity: 0; transition: opacity .22s ease; pointer-events: none; }
.image-cabin__frame::before { border-top: 2px solid #52ddff; border-left: 2px solid #52ddff; clip-path: polygon(0 0, 34% 0, 34% 2px, 2px 2px, 2px 34%, 0 34%); filter: drop-shadow(0 0 5px rgba(82,221,255,.52)); }
.image-cabin__frame::after { border-right: 2px solid #52ddff; border-bottom: 2px solid #52ddff; clip-path: polygon(66% calc(100% - 2px), calc(100% - 2px) calc(100% - 2px), calc(100% - 2px) 66%, 100% 66%, 100% 100%, 66% 100%); filter: drop-shadow(0 0 5px rgba(82,221,255,.52)); }
.image-cabin__hint { position: absolute; bottom: clamp(7px, .9vw, 15px); left: 50%; padding: clamp(4px, .45vw, 8px) clamp(8px, .8vw, 14px); border: 1px solid rgba(82,221,255,.52); border-radius: 6px; background: rgba(10,29,48,.94); box-shadow: 0 8px 24px rgba(0,3,14,.38); color: #e7f1f7; font-size: clamp(8px, .75vw, 13px); font-weight: 700; letter-spacing: 0; white-space: nowrap; opacity: 0; transform: translate(-50%, 6px); transition: opacity .2s ease, transform .2s ease; pointer-events: none; }
.image-cabin__zone:hover .image-cabin__frame, .image-cabin__zone:focus-visible .image-cabin__frame { border-color: rgba(82,221,255,.52); background: rgba(17,49,66,.28); box-shadow: inset 0 0 30px rgba(82,221,255,.08), 0 0 18px rgba(82,221,255,.12); }
.image-cabin__zone:hover .image-cabin__frame::before, .image-cabin__zone:hover .image-cabin__frame::after, .image-cabin__zone:focus-visible .image-cabin__frame::before, .image-cabin__zone:focus-visible .image-cabin__frame::after, .image-cabin__zone:hover .image-cabin__hint, .image-cabin__zone:focus-visible .image-cabin__hint { opacity: 1; }
.image-cabin__zone:hover .image-cabin__hint, .image-cabin__zone:focus-visible .image-cabin__hint { transform: translate(-50%, 0); }
.image-cabin__zone:focus-visible { outline: 2px solid #52ddff; outline-offset: 3px; }
.image-cabin__zone--ai-suggest { z-index: 4; }
.image-cabin__zone.is-editing { cursor: crosshair; }
.image-cabin__zone.is-editing .image-cabin__frame { border-color: rgba(101, 222, 255, .55); background: rgba(22, 126, 255, .055); box-shadow: inset 0 0 18px rgba(67, 197, 255, .11); }
.image-cabin__zone.is-editing .image-cabin__frame::before, .image-cabin__zone.is-editing .image-cabin__frame::after { opacity: .56; }
.image-cabin__zone.is-selected { z-index: 6; }
.image-cabin__zone.is-selected .image-cabin__frame { border-color: #d9fbff; background: radial-gradient(circle, rgba(69, 208, 255, .18), rgba(30, 115, 255, .075)); box-shadow: inset 0 0 36px rgba(78, 211, 255, .2), 0 0 32px rgba(26, 164, 255, .58); }
.image-cabin__zone.is-selected .image-cabin__frame::before, .image-cabin__zone.is-selected .image-cabin__frame::after, .image-cabin__zone.is-selected .image-cabin__hint { opacity: 1; }
.image-cabin__zone.is-selected .image-cabin__hint { transform: translate(-50%, 0); }

.image-cabin__dev-controls { position: fixed; top: 24px; right: 24px; z-index: 220; display: flex; gap: 10px; }
.image-cabin__dev-button { min-width: 94px; height: 42px; border: 1px solid rgba(109, 225, 255, .5); border-radius: 10px; padding: 0 16px; background: linear-gradient(180deg, rgba(7, 35, 78, .9), rgba(3, 18, 48, .94)); box-shadow: 0 8px 24px rgba(0, 7, 30, .38), inset 0 1px rgba(255, 255, 255, .08); color: #dff9ff; font: 700 13px/1 "Microsoft YaHei", sans-serif; cursor: pointer; backdrop-filter: blur(18px); transition: .2s ease; }
.image-cabin__dev-button:hover, .image-cabin__dev-button.active { border-color: #7ce8ff; background: linear-gradient(180deg, rgba(13, 74, 117, .94), rgba(5, 35, 76, .96)); box-shadow: 0 0 24px rgba(44, 190, 255, .32), inset 0 1px rgba(255, 255, 255, .12); color: #fff; }

.image-cabin__tuner { position: fixed; top: 78px; right: 24px; z-index: 219; width: min(328px, calc(100vw - 48px)); border: 1px solid rgba(87, 211, 255, .42); border-radius: 14px; padding: 18px; background: linear-gradient(155deg, rgba(4, 24, 61, .96), rgba(2, 13, 38, .97)); box-shadow: 0 20px 55px rgba(0, 5, 25, .56), inset 0 1px rgba(255, 255, 255, .07); color: #dff8ff; backdrop-filter: blur(22px); }
.image-cabin__tuner header { display: grid; gap: 4px; padding-bottom: 14px; border-bottom: 1px solid rgba(99, 221, 255, .16); }
.image-cabin__tuner header span { color: #6ddfff; font: 700 9px/1 Bahnschrift, sans-serif; letter-spacing: .18em; }
.image-cabin__tuner header strong { font-size: 15px; }
.image-cabin__module-select { display: grid; grid-template-columns: 76px 1fr; align-items: center; gap: 10px; margin: 15px 0 12px; }
.image-cabin__module-select > span, .image-cabin__tuner-row > span { color: #9bc9d7; font-size: 11px; }
.image-cabin__module-select select { min-width: 0; border: 1px solid rgba(88, 218, 255, .28); border-radius: 7px; padding: 7px 9px; outline: 0; background: #071c40; color: #effcff; font: inherit; font-size: 12px; }
.image-cabin__module-select select:focus { border-color: #71e6ff; box-shadow: 0 0 0 2px rgba(55, 196, 255, .12); }
.image-cabin__tuner-row { display: grid; grid-template-columns: 76px 1fr 47px; align-items: center; gap: 10px; min-height: 38px; }
.image-cabin__tuner-row input[type="range"] { width: 100%; accent-color: #55dfff; cursor: ew-resize; }
.image-cabin__tuner-row i { color: #72e5ff; font: 700 11px/1 Bahnschrift, monospace; text-align: right; }
.image-cabin__tuner-actions { display: grid; grid-template-columns: 1fr 1.25fr; gap: 8px; margin-top: 14px; }
.image-cabin__tuner-actions button { border: 1px solid rgba(94, 222, 255, .3); border-radius: 8px; padding: 9px 10px; background: rgba(12, 67, 112, .48); color: #e9fbff; font: 700 11px/1 "Microsoft YaHei", sans-serif; cursor: pointer; }
.image-cabin__tuner-actions button:hover { border-color: #78eaff; background: #0d4a75; }
.image-cabin__tuner > p { min-height: 28px; margin: 12px 0 0; color: #729ead; font-size: 10px; line-height: 1.45; }

@keyframes cabin-reveal { from { opacity: 0; transform: scale(1.025); } to { opacity: 1; transform: scale(1); } }

@media (max-width: 700px) { .image-cabin__hint { display: none; } .image-cabin__frame::before, .image-cabin__frame::after { border-width: 1px; } .image-cabin__dev-controls { top: 12px; right: 12px; gap: 6px; } .image-cabin__dev-button { min-width: 78px; height: 36px; padding: 0 10px; font-size: 11px; } .image-cabin__tuner { top: 58px; right: 12px; width: calc(100vw - 24px); max-height: calc(100vh - 70px); overflow-y: auto; padding: 14px; } }
@media (prefers-reduced-motion: reduce) { .image-cabin__canvas { animation: none; } .image-cabin__frame, .image-cabin__hint { transition: none; } }
</style>

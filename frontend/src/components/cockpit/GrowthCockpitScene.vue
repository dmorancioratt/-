<template>
  <div ref="host" class="growth-scene" aria-label="个人成长智能驾驶舱三维空间">
    <div class="growth-scene__bgwrap">
      <video class="growth-scene__bgv" src="/Digital_path_transforms_into_river_202608242002.mp4" autoplay loop muted playsinline preload="auto"></video>
    </div>
    <div v-if="loading" class="growth-scene__loading">
      <span class="growth-scene__loader-orbit"></span>
      <p>ASSEMBLING THE GROWTH LAB</p>
      <strong>{{ progress }}%</strong>
    </div>

    <div v-else-if="failedModules.length" class="growth-scene__fallback">
      <b>MODULE CONNECTION NOTICE</b>
      <span>{{ failedModules.join(' / ') }} can be reconnected after refresh.</span>
    </div>

    <div v-if="showGuide && !loading" class="growth-scene__guide">
      DRAG TO ORBIT&nbsp;&nbsp;·&nbsp;&nbsp;CLICK TO ENTER
    </div>

    <div class="growth-scene__readout" aria-hidden="true">
      <span>GROWTH LAB</span><i></i><em>07 PHYSICAL MODULES ONLINE</em>
    </div>

    <div
      v-for="reviewLabel in reviewLabels"
      :key="reviewLabel.id"
      v-show="reviewLabel.visible && !editorEnabled"
      class="growth-scene__model-label"
      :style="{ left: `${reviewLabel.x}px`, top: `${reviewLabel.y}px` }"
      aria-hidden="true"
    >
      <span>{{ reviewLabel.index }}</span>
      <b>{{ reviewLabel.subtitle }}</b>
      <small>{{ reviewLabel.label }}</small>
    </div>

    <AutoFitModuleFrames
      v-show="!editorEnabled"
      :frames="moduleFrames"
      :layer-w="frameLayer.w"
      :layer-h="frameLayer.h"
      :padding="frameOptions.padding"
      :skew="frameOptions.skew"
      :stroke-scale="frameOptions.strokeScale"
      :ui-scale="frameOptions.uiScale"
      :opacity="frameOptions.opacity"
      :smooth="frameOptions.smooth"
      :radius="frameOptions.radius"
    />

    <button
      v-if="false && showLayoutEditor"
      class="frame-tuner__toggle"
      :class="{ active: frameTunerOpen }"
      type="button"
      @click="frameTunerOpen = !frameTunerOpen"
    >
      {{ frameTunerOpen ? '收起框调节' : '框调节' }}
    </button>

    <aside v-if="frameTunerOpen" class="frame-tuner" aria-label="模块外框调节面板">
      <header>
        <span>FRAME TUNER</span>
        <strong>模块外框实时调节</strong>
      </header>

      <label class="frame-tuner__row">
        <span>框边距（外扩）</span>
        <input type="range" min="0" max="0.3" step="0.01" v-model.number="frameOptions.padding" />
        <i>{{ frameOptions.padding.toFixed(2) }}</i>
      </label>
      <label class="frame-tuner__row">
        <span>成就墙斜切比例</span>
        <input type="range" min="0" max="0.4" step="0.01" v-model.number="frameOptions.skew" />
        <i>{{ frameOptions.skew.toFixed(2) }}</i>
      </label>
      <label class="frame-tuner__row">
        <span>描边粗细</span>
        <input type="range" min="0.4" max="3" step="0.1" v-model.number="frameOptions.strokeScale" />
        <i>{{ frameOptions.strokeScale.toFixed(1) }}</i>
      </label>
      <label class="frame-tuner__row">
        <span>标签/按钮大小</span>
        <input type="range" min="0.6" max="1.6" step="0.05" v-model.number="frameOptions.uiScale" />
        <i>{{ frameOptions.uiScale.toFixed(2) }}</i>
      </label>
      <label class="frame-tuner__row">
        <span>整体透明度</span>
        <input type="range" min="0.1" max="1" step="0.05" v-model.number="frameOptions.opacity" />
        <i>{{ frameOptions.opacity.toFixed(2) }}</i>
      </label>
      <label class="frame-tuner__row">
        <span>跟随灵敏度</span>
        <input type="range" min="0.08" max="1" step="0.02" v-model.number="frameOptions.smooth" />
        <i>{{ frameOptions.smooth.toFixed(2) }}</i>
      </label>
      <label class="frame-tuner__row">
        <span>圆角半径</span>
        <input type="range" min="0" max="36" step="1" v-model.number="frameOptions.radius" />
        <i>{{ frameOptions.radius }}</i>
      </label>

      <div class="frame-tuner__actions">
        <button type="button" @click="resetFrameOptions">恢复默认</button>
        <button type="button" @click="copyFrameOptions">复制参数</button>
      </div>
      <p class="frame-tuner__hint">拖动滑块实时生效；调好后点「复制参数」粘贴到代码里固定。</p>
    </aside>

    <button
      v-if="false && showLayoutEditor"
      class="layout-editor__toggle"
      :class="{ active: editorEnabled }"
      type="button"
      @click="setEditorEnabled(!editorEnabled)"
    >
      {{ editorEnabled ? '退出布局编辑' : '编辑布局' }}
    </button>

    <aside v-if="editorEnabled" class="layout-editor" :class="{ 'layout-editor--left': editorPanelOnLeft }" aria-label="三维布局编辑器">
      <header>
        <span>LAYOUT EDITOR</span>
        <strong>{{ editorSelected?.subtitle || '选择一个模型' }}</strong>
      </header>
      <p class="layout-editor__hint">点击模型后拖动三轴；W / E / R 切换移动、旋转、缩放。</p>

      <div class="layout-editor__modes" role="group" aria-label="编辑模式">
        <button :class="{ active: editorMode === 'translate' }" type="button" @click="setEditorMode('translate')">移动 W</button>
        <button :class="{ active: editorMode === 'rotate' }" type="button" @click="setEditorMode('rotate')">旋转 E</button>
        <button :class="{ active: editorMode === 'scale' }" type="button" @click="setEditorMode('scale')">缩放 R</button>
      </div>

      <template v-if="editorSelected">
        <div class="layout-editor__section">
          <b>POSITION</b>
          <div class="layout-editor__fields">
            <label>X<input v-model.number="editorValues.x" type="number" step="0.01" @change="applyEditorValues" /></label>
            <label>Y<input v-model.number="editorValues.y" type="number" step="0.01" @change="applyEditorValues" /></label>
            <label>Z<input v-model.number="editorValues.z" type="number" step="0.01" @change="applyEditorValues" /></label>
          </div>
        </div>
        <div class="layout-editor__section">
          <b>ROTATION</b>
          <div class="layout-editor__fields">
            <label>X<input v-model.number="editorValues.rx" type="number" step="0.01" @change="applyEditorValues" /></label>
            <label>Y<input v-model.number="editorValues.ry" type="number" step="0.01" @change="applyEditorValues" /></label>
            <label>Z<input v-model.number="editorValues.rz" type="number" step="0.01" @change="applyEditorValues" /></label>
          </div>
        </div>
        <div class="layout-editor__section layout-editor__scale">
          <b>SCALE</b>
          <label><input v-model.number="editorValues.scale" type="number" min="0.05" step="0.01" @change="applyEditorValues" /></label>
        </div>
        <div class="layout-editor__actions">
          <button type="button" @click="resetSelectedModule">重置当前</button>
          <button type="button" @click="copyCurrentModule">复制当前配置</button>
        </div>
      </template>

      <details class="layout-editor__camera">
        <summary>CAMERA</summary>
        <div class="layout-editor__fields">
          <label>PX<input v-model.number="cameraValues.x" type="number" step="0.01" @change="applyCameraValues" /></label>
          <label>PY<input v-model.number="cameraValues.y" type="number" step="0.01" @change="applyCameraValues" /></label>
          <label>PZ<input v-model.number="cameraValues.z" type="number" step="0.01" @change="applyCameraValues" /></label>
          <label>TX<input v-model.number="cameraValues.tx" type="number" step="0.01" @change="applyCameraValues" /></label>
          <label>TY<input v-model.number="cameraValues.ty" type="number" step="0.01" @change="applyCameraValues" /></label>
          <label>TZ<input v-model.number="cameraValues.tz" type="number" step="0.01" @change="applyCameraValues" /></label>
        </div>
        <label class="layout-editor__fov">FOV<input v-model.number="cameraValues.fov" type="number" min="10" max="90" step="1" @change="applyCameraValues" /></label>
      </details>
      <button class="layout-editor__export" type="button" @click="exportAllLayouts">导出全部布局 JSON</button>
      <small v-if="editorMessage" class="layout-editor__message">{{ editorMessage }}</small>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { TransformControls } from 'three/examples/jsm/controls/TransformControls.js'
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js'
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js'
import { OutlinePass } from 'three/examples/jsm/postprocessing/OutlinePass.js'
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js'
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js'
import { cockpitModules, defaultCamera, type CockpitModuleConfig } from './cockpitModuleConfig'
import AutoFitModuleFrames, { type RawFrame } from './AutoFitModuleFrames.vue'

type MaterialState = {
  material: THREE.MeshStandardMaterial
  baseColor: THREE.Color
  baseEmissiveIntensity: number
}

type TransformMode = 'translate' | 'rotate' | 'scale'
type SavedTransform = {
  position: [number, number, number]
  rotation: [number, number, number]
  scale: number
}

type ReviewLabel = {
  id: CockpitModuleConfig['id']
  index: string
  subtitle: string
  label: string
  x: number
  y: number
  visible: boolean
}

const props = defineProps<{ activeModule?: string | null }>()
const emit = defineEmits<{ focus: [panel: CockpitModuleConfig['panel']] }>()
const host = ref<HTMLElement | null>(null)
const loading = ref(true)
const progress = ref(0)
const showGuide = ref(true)
const failedModules = ref<string[]>([])
const showLayoutEditor = import.meta.env.DEV
const showReviewLabels = ref(import.meta.env.DEV)
const reviewLabels = ref<ReviewLabel[]>([])
const frameLayer = reactive({ w: 1920, h: 1080 })
const moduleFrames = ref<RawFrame[]>([])
const bboxByRoot = new WeakMap<THREE.Group, THREE.Box3>()

// 模块外框实时调节参数（通过页面上「框调节」面板拖滑块修改）
const FRAME_DEFAULTS = {
  padding: 0.1,
  skew: 0.16,
  strokeScale: 1,
  uiScale: 1,
  opacity: 1,
  smooth: 0.22,
  radius: 18,
}
const frameTunerOpen = ref(false)
const frameOptions = reactive({ ...FRAME_DEFAULTS })
function resetFrameOptions() { Object.assign(frameOptions, FRAME_DEFAULTS) }
async function copyFrameOptions() {
  const text = JSON.stringify(frameOptions, null, 2)
  try {
    await navigator.clipboard.writeText(text)
    editorMessage.value = '框参数已复制到剪贴板'
  } catch {
    editorMessage.value = '浏览器未授权剪贴板，请手动抄录'
  }
}
const editorEnabled = ref(false)
const editorMode = ref<TransformMode>('translate')
const editorSelected = ref<CockpitModuleConfig | null>(null)
const editorMessage = ref('')
const editorValues = reactive({ x: 0, y: 0, z: 0, rx: 0, ry: 0, rz: 0, scale: 1 })
const cameraValues = reactive({ x: 0, y: 0, z: 13.2, tx: 0, ty: 0, tz: 0, fov: 39 })
const editorPanelOnLeft = computed(() => ['profile', 'calendar', 'achievement'].includes(editorSelected.value?.id ?? ''))

let renderer: THREE.WebGLRenderer | undefined
let scene: THREE.Scene | undefined
let camera: THREE.PerspectiveCamera | undefined
let controls: OrbitControls | undefined
let transformControls: TransformControls | undefined
let composer: EffectComposer | undefined
let outline: OutlinePass | undefined
let environmentTarget: THREE.WebGLRenderTarget | undefined
let resizeObserver: ResizeObserver | undefined
let frameId = 0
let cameraGoal: THREE.Vector3 | undefined
let targetGoal: THREE.Vector3 | undefined
let pendingPanel: CockpitModuleConfig['panel'] | undefined
let focusLocked = false
let unlockControlsAfterMove = false
let panelTimer: number | undefined
let guideTimer: number | undefined
let hoveredRoot: THREE.Group | undefined
let selectedRoot: THREE.Group | undefined
let editorRoot: THREE.Group | undefined
let transformIsDragging = false

const raycaster = new THREE.Raycaster()
const pointer = new THREE.Vector2()
const tempPosition = new THREE.Vector3()
const tempScale = new THREE.Vector3()
const interactiveRoots: THREE.Group[] = []
const configByRoot = new WeakMap<THREE.Object3D, CockpitModuleConfig>()
const basePositionByRoot = new WeakMap<THREE.Group, THREE.Vector3>()
const materialStatesByRoot = new WeakMap<THREE.Group, MaterialState[]>()
const initialTransformsById = new Map<CockpitModuleConfig['id'], SavedTransform>()

function metalMaterial(
  color: number,
  emissive = 0x000000,
  emissiveIntensity = 0,
  metalness = .66,
  roughness = .38,
) {
  return new THREE.MeshStandardMaterial({
    color,
    metalness,
    roughness,
    emissive,
    emissiveIntensity,
  })
}

function addBox(
  group: THREE.Group,
  size: [number, number, number],
  position: [number, number, number],
  material: THREE.Material,
  rotation: [number, number, number] = [0, 0, 0],
  edge = false,
) {
  const geometry = new THREE.BoxGeometry(...size)
  const mesh = new THREE.Mesh(geometry, material)
  mesh.position.set(...position)
  mesh.rotation.set(...rotation)
  mesh.castShadow = true
  mesh.receiveShadow = true
  group.add(mesh)

  if (edge) {
    const lines = new THREE.LineSegments(
      new THREE.EdgesGeometry(geometry),
      new THREE.LineBasicMaterial({ color: 0x1b7fb8, transparent: true, opacity: .28 }),
    )
    lines.position.copy(mesh.position)
    lines.rotation.copy(mesh.rotation)
    group.add(lines)
  }
  return mesh
}

function addLightStrip(
  group: THREE.Group,
  size: [number, number, number],
  position: [number, number, number],
  rotation: [number, number, number] = [0, 0, 0],
  intensity = .48,
) {
  return addBox(group, size, position, metalMaterial(0x13517a, 0x29c8ff, intensity, .58, .24), rotation)
}

function addWallBay(
  room: THREE.Group,
  position: [number, number, number],
  width: number,
  height: number,
  rotationY = 0,
) {
  const bay = new THREE.Group()
  bay.position.set(...position)
  bay.rotation.y = rotationY
  const hull = metalMaterial(0x183f62, 0x07304e, .32, .70, .32)
  const innerFrame = metalMaterial(0x102e4d, 0x05213d, .26, .60, .38)
  const recess = metalMaterial(0x071b34, 0x041a35, .23, .40, .54)
  addBox(bay, [width + .32, height + .32, .24], [0, 0, 0], hull, [0, 0, 0], true)
  addBox(bay, [width + .10, height + .10, .16], [0, 0, .12], innerFrame, [0, 0, 0], true)
  addBox(bay, [width, height, .10], [0, 0, .22], recess)
  addLightStrip(bay, [width * .72, .035, .035], [0, height / 2 - .08, .23], [0, 0, 0], .38)
  room.add(bay)
}

function addPedestal(
  room: THREE.Group,
  position: [number, number, number],
  size: [number, number, number],
  rotationY = 0,
) {
  const pedestal = new THREE.Group()
  pedestal.position.set(...position)
  pedestal.rotation.y = rotationY
  addBox(pedestal, size, [0, 0, 0], metalMaterial(0x18344f, 0x0a365d, .38, .64, .34), [0, 0, 0], true)
  addLightStrip(pedestal, [size[0] * .72, .035, size[2] + .012], [0, size[1] / 2 + .025, 0], [0, 0, 0], .42)
  room.add(pedestal)
}

function createRoom() {
  const room = new THREE.Group()
  room.name = 'growth-lab-shell'

  const floor = metalMaterial(0x102a45, 0x05182c, .27, .48, .56)
  const wall = metalMaterial(0x102c4b, 0x06213d, .34, .58, .44)
  const frame = metalMaterial(0x1f4d73, 0x094777, .48, .70, .32)
  const deepInset = metalMaterial(0x0a2442, 0x052449, .32, .42, .50)
  const ceiling = metalMaterial(0x0b1627, 0x03101f, .18, .70, .46)
  const tileA = metalMaterial(0x123454, 0x04172c, .17, .40, .62)
  const tileB = metalMaterial(0x0f2c49, 0x04172c, .16, .42, .64)

  // The long floor and visible side walls create real perspective convergence.
  addBox(room, [11.4, .18, 9.7], [0, -1.57, .20], floor)
  addBox(room, [10.72, 5.9, .28], [0, 1.26, -3.67], wall)
  addBox(room, [.25, 5.85, 7.2], [-5.36, 1.24, -.18], wall)
  addBox(room, [.25, 5.85, 7.2], [5.36, 1.24, -.18], wall)
  addBox(room, [11.25, .18, 9.45], [0, 4.20, .15], ceiling)

  // Visible floor tiles catch the blue bounce light instead of collapsing into black.
  for (let row = 0; row < 5; row += 1) {
    for (let column = 0; column < 5; column += 1) {
      const x = -4.42 + column * 2.21
      const z = -2.72 + row * 1.82
      addBox(room, [2.10, .025, 1.70], [x, -1.455, z], (row + column) % 2 ? tileA : tileB)
    }
  }

  const grid = new THREE.GridHelper(11.1, 22, 0x11648d, 0x0a2237)
  grid.position.set(0, -1.435, .22)
  grid.material.transparent = true
  grid.material.opacity = .24
  room.add(grid)

  // Structural ribs and ceiling rails, without any painted functional UI.
  addBox(room, [.28, 5.95, .46], [-5.12, 1.25, -3.42], frame, [0, 0, 0], true)
  addBox(room, [.28, 5.95, .46], [5.12, 1.25, -3.42], frame, [0, 0, 0], true)
  addBox(room, [10.45, .26, .5], [0, 4.08, -3.40], frame, [0, 0, 0], true)
  addBox(room, [10.9, .2, .34], [0, -1.34, -3.48], frame)
  addBox(room, [10.9, .22, .34], [0, -1.36, 4.36], frame)
  addLightStrip(room, [7.8, .045, .06], [0, 3.92, -3.14], [0, 0, 0], .55)
  addLightStrip(room, [8.2, .035, .055], [0, 4.08, -1.52], [0, 0, 0], .46)
  addLightStrip(room, [6.8, .035, .055], [0, 4.08, 2.35], [0, 0, 0], .42)

  for (const x of [-4.78, -2.42, 2.42, 4.78]) {
    addBox(room, [.12, 5.3, .25], [x, 1.20, -3.43], frame)
  }
  for (const z of [-2.85, -1.15, .55, 2.25]) {
    addBox(room, [.16, 5.25, .24], [-5.18, 1.12, z], frame)
    addBox(room, [.16, 5.25, .24], [5.18, 1.12, z], frame)
  }

  // Lower wall cladding keeps the empty bays architectural rather than void-black.
  addBox(room, [2.38, 1.22, .16], [-3.72, -.18, -3.46], deepInset, [0, .04, 0], true)
  addBox(room, [2.72, 1.38, .16], [-.08, -.16, -3.47], deepInset, [0, 0, 0], true)
  addBox(room, [2.18, .92, .16], [3.70, -.76, -3.45], deepInset, [0, -.05, 0], true)

  // Back layer: three distinct recessed wall slots.
  addWallBay(room, [-3.72, 2.18, -3.46], 2.55, 2.18, .08)
  addWallBay(room, [-.05, 2.71, -3.50], 3.02, 1.62, 0)
  addWallBay(room, [3.66, 2.18, -3.45], 2.42, 2.12, -.09)

  // Middle-right angled bay makes the calendar read as a side-wall terminal.
  addWallBay(room, [3.83, .42, -2.48], 2.55, 1.35, -.24)

  // Physical floor furniture: one resource stand, one AI pedestal, one trophy plinth.
  addPedestal(room, [-3.62, -1.34, -.54], [2.18, .18, 1.66], .20)
  addPedestal(room, [3.42, -1.36, 1.72], [2.42, .18, 1.20], -.20)

  const aiBase = new THREE.Group()
  const baseBody = new THREE.Mesh(
    new THREE.CylinderGeometry(.82, .94, .22, 48),
    metalMaterial(0x173754, 0x0a416d, .46, .62, .32),
  )
  baseBody.position.set(-.10, -1.34, .62)
  baseBody.castShadow = true
  baseBody.receiveShadow = true
  aiBase.add(baseBody)
  const singleRing = new THREE.Mesh(
    new THREE.TorusGeometry(.68, .025, 10, 64),
    metalMaterial(0x17628a, 0x35d5ff, .70, .50, .22),
  )
  singleRing.rotation.x = Math.PI / 2
  singleRing.position.set(-.10, -1.20, .62)
  aiBase.add(singleRing)
  room.add(aiBase)

  // Sparse floor guidance lines reinforce depth without becoming an effect layer.
  addLightStrip(room, [3.0, .025, .035], [-3.95, -1.455, 3.90], [0, .12, 0], .35)
  addLightStrip(room, [3.0, .025, .035], [3.95, -1.455, 3.90], [0, -.12, 0], .35)
  addLightStrip(room, [2.2, .025, .035], [0, -1.455, 4.05], [0, 0, 0], .38)

  // A central floor frame and front steps reproduce the readable stage depth of the reference.
  addBox(room, [3.35, .035, 2.52], [-.08, -1.42, .70], metalMaterial(0x0a1b2d, 0x031326, .18, .32, .72), [0, 0, 0], true)
  addLightStrip(room, [3.05, .022, .035], [-.08, -1.395, -.49], [0, 0, 0], .46)
  addLightStrip(room, [3.05, .022, .035], [-.08, -1.395, 1.89], [0, 0, 0], .46)
  addBox(room, [3.30, .18, .72], [0, -1.57, 4.83], frame, [0, 0, 0], true)
  addBox(room, [2.78, .18, .64], [0, -1.73, 5.36], frame, [0, 0, 0], true)
  addBox(room, [2.25, .18, .56], [0, -1.89, 5.84], frame, [0, 0, 0], true)
  addLightStrip(room, [2.86, .035, .035], [0, -1.47, 5.18], [0, 0, 0], .58)
  addLightStrip(room, [2.35, .035, .035], [0, -1.63, 5.68], [0, 0, 0], .52)

  scene!.add(room)
}

function prepareModel(root: THREE.Group) {
  const box = new THREE.Box3().setFromObject(root)
  const center = box.getCenter(new THREE.Vector3())
  const states: MaterialState[] = []

  root.traverse((object) => {
    if (!(object instanceof THREE.Mesh)) return
    object.castShadow = true
    object.receiveShadow = true

    const source = Array.isArray(object.material) ? object.material : [object.material]
    const cloned = source.map((material) => material.clone())
    object.material = Array.isArray(object.material) ? cloned : cloned[0]

    cloned.forEach((material) => {
      if (!(material instanceof THREE.MeshStandardMaterial)) return
      // Keep the GLB's own texture maps, but lift their very dark blue tint so
      // the physical devices read clearly against the darker cabin structure.
      material.color.lerp(new THREE.Color(0xe4f4ff), .28)
      material.envMapIntensity = 1.12
      states.push({
        material,
        baseColor: material.color.clone(),
        baseEmissiveIntensity: material.emissiveIntensity,
      })
    })
  })

  root.position.sub(center)
  return states
}

async function loadModule(config: CockpitModuleConfig, loader: GLTFLoader) {
  const gltf = await loader.loadAsync(config.model)
  const root = new THREE.Group()
  root.name = config.id
  root.add(gltf.scene)
  const materialStates = prepareModel(gltf.scene)
  root.position.set(...config.position)
  root.rotation.set(...config.rotation)
  root.scale.setScalar(config.scale)
  root.userData.config = config

  basePositionByRoot.set(root, new THREE.Vector3(...config.position))
  initialTransformsById.set(config.id, {
    position: [...config.position],
    rotation: [...config.rotation],
    scale: config.scale,
  })
  materialStatesByRoot.set(root, materialStates)
  configByRoot.set(root, config)
  interactiveRoots.push(root)
  scene!.add(root)
  bboxByRoot.set(root, new THREE.Box3().setFromObject(root))
}

function roundLayoutValue(value: number) {
  return Number(value.toFixed(3))
}

function syncEditorValues(root = editorRoot) {
  if (!root || !camera || !controls) return
  editorValues.x = roundLayoutValue(root.position.x)
  editorValues.y = roundLayoutValue(root.position.y)
  editorValues.z = roundLayoutValue(root.position.z)
  editorValues.rx = roundLayoutValue(root.rotation.x)
  editorValues.ry = roundLayoutValue(root.rotation.y)
  editorValues.rz = roundLayoutValue(root.rotation.z)
  editorValues.scale = roundLayoutValue(root.scale.x)
  cameraValues.x = roundLayoutValue(camera.position.x)
  cameraValues.y = roundLayoutValue(camera.position.y)
  cameraValues.z = roundLayoutValue(camera.position.z)
  cameraValues.tx = roundLayoutValue(controls.target.x)
  cameraValues.ty = roundLayoutValue(controls.target.y)
  cameraValues.tz = roundLayoutValue(controls.target.z)
  cameraValues.fov = roundLayoutValue(camera.fov)
}

function commitRootToConfig(root = editorRoot) {
  if (!root) return
  const config = configByRoot.get(root)
  if (!config) return

  if (editorMode.value === 'scale') {
    const uniformScale = Math.max(.05, (root.scale.x + root.scale.y + root.scale.z) / 3)
    root.scale.setScalar(uniformScale)
  }

  config.position = [
    roundLayoutValue(root.position.x),
    roundLayoutValue(root.position.y),
    roundLayoutValue(root.position.z),
  ]
  config.rotation = [
    roundLayoutValue(root.rotation.x),
    roundLayoutValue(root.rotation.y),
    roundLayoutValue(root.rotation.z),
  ]
  config.scale = roundLayoutValue(root.scale.x)
  basePositionByRoot.set(root, root.position.clone())
  syncEditorValues(root)
}

function selectEditorRoot(root: THREE.Group | undefined) {
  if (!root || !transformControls) return
  editorRoot = root
  editorSelected.value = configByRoot.get(root) ?? null
  selectedRoot = root
  transformControls.attach(root)
  if (outline) outline.selectedObjects = [root]
  syncEditorValues(root)
}

function setEditorMode(mode: TransformMode) {
  editorMode.value = mode
  transformControls?.setMode(mode)
}

function setEditorEnabled(enabled: boolean) {
  editorEnabled.value = enabled
  showGuide.value = !enabled
  focusLocked = false
  hoveredRoot = undefined
  if (host.value) host.value.style.cursor = enabled ? 'crosshair' : 'default'

  if (!enabled) {
    transformControls?.detach()
    editorRoot = undefined
    editorSelected.value = null
    selectedRoot = undefined
    if (outline) outline.selectedObjects = []
    return
  }

  setEditorMode(editorMode.value)
}

function applyEditorValues() {
  if (!editorRoot) return
  editorRoot.position.set(editorValues.x, editorValues.y, editorValues.z)
  editorRoot.rotation.set(editorValues.rx, editorValues.ry, editorValues.rz)
  editorRoot.scale.setScalar(Math.max(.05, editorValues.scale))
  commitRootToConfig(editorRoot)
}

function applyCameraValues() {
  if (!camera || !controls) return
  camera.position.set(cameraValues.x, cameraValues.y, cameraValues.z)
  controls.target.set(cameraValues.tx, cameraValues.ty, cameraValues.tz)
  camera.fov = Math.min(90, Math.max(10, cameraValues.fov))
  camera.updateProjectionMatrix()
  cameraGoal = undefined
  targetGoal = undefined
}

function resetSelectedModule() {
  if (!editorRoot) return
  const config = configByRoot.get(editorRoot)
  const initial = config && initialTransformsById.get(config.id)
  if (!config || !initial) return
  editorRoot.position.set(...initial.position)
  editorRoot.rotation.set(...initial.rotation)
  editorRoot.scale.setScalar(initial.scale)
  config.position = [...initial.position]
  config.rotation = [...initial.rotation]
  config.scale = initial.scale
  basePositionByRoot.set(editorRoot, editorRoot.position.clone())
  syncEditorValues(editorRoot)
  editorMessage.value = `${config.subtitle} 已重置`
}

function layoutPayload() {
  return {
    camera: {
      position: [cameraValues.x, cameraValues.y, cameraValues.z],
      target: [cameraValues.tx, cameraValues.ty, cameraValues.tz],
      fov: cameraValues.fov,
    },
    modules: Object.fromEntries(cockpitModules.map((config) => [config.id, {
      position: config.position,
      rotation: config.rotation,
      scale: config.scale,
    }])),
  }
}

async function copyText(value: string, successMessage: string) {
  try {
    await navigator.clipboard.writeText(value)
    editorMessage.value = successMessage
  } catch {
    editorMessage.value = '浏览器未授权剪贴板，请使用导出文件。'
  }
}

function copyCurrentModule() {
  if (!editorSelected.value) return
  const config = editorSelected.value
  void copyText(JSON.stringify({
    [config.id]: { position: config.position, rotation: config.rotation, scale: config.scale },
  }, null, 2), `${config.subtitle} 配置已复制`)
}

function exportAllLayouts() {
  const json = JSON.stringify(layoutPayload(), null, 2)
  void copyText(json, '全部布局 JSON 已复制并下载')
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'growth-cabin-layout.json'
  link.click()
  URL.revokeObjectURL(url)
}

function onEditorKeydown(event: KeyboardEvent) {
  if (!editorEnabled.value) return
  if (event.target instanceof HTMLInputElement) return
  const mode = event.key.toLowerCase() === 'w'
    ? 'translate'
    : event.key.toLowerCase() === 'e'
      ? 'rotate'
      : event.key.toLowerCase() === 'r'
        ? 'scale'
        : undefined
  if (!mode) return
  event.preventDefault()
  setEditorMode(mode)
}

function findRoot(object: THREE.Object3D | null | undefined) {
  let current = object
  while (current) {
    if (configByRoot.has(current)) return current as THREE.Group
    current = current.parent
  }
}

function updatePointer(event: MouseEvent) {
  if (!host.value || !camera) return
  const rect = host.value.getBoundingClientRect()
  pointer.set(
    ((event.clientX - rect.left) / rect.width) * 2 - 1,
    -((event.clientY - rect.top) / rect.height) * 2 + 1,
  )
  raycaster.setFromCamera(pointer, camera)
}

function pick(event: MouseEvent) {
  updatePointer(event)
  return findRoot(raycaster.intersectObjects(interactiveRoots, true)[0]?.object)
}

function setHovered(root: THREE.Group | undefined) {
  if (hoveredRoot === root) return
  hoveredRoot = root
  if (host.value) host.value.style.cursor = root ? 'pointer' : 'default'
  if (outline) outline.selectedObjects = root ? [root] : selectedRoot ? [selectedRoot] : []
}

function focus(root: THREE.Group) {
  if (focusLocked || !controls) return
  focusLocked = true
  controls.enabled = false
  selectedRoot = root
  const config = configByRoot.get(root)!
  pendingPanel = config.panel
  window.clearTimeout(panelTimer)
  panelTimer = window.setTimeout(() => {
    if (focusLocked && pendingPanel) {
      const panel = pendingPanel
      pendingPanel = undefined
      emit('focus', panel)
    }
  }, 420)
  if (outline) outline.selectedObjects = [root]
}

function resetCamera() {
  if (!controls) return
  window.clearTimeout(panelTimer)
  focusLocked = false
  controls.enabled = false
  unlockControlsAfterMove = false
  selectedRoot = undefined
  pendingPanel = undefined
  cameraGoal = undefined
  targetGoal = undefined
  if (outline) outline.selectedObjects = hoveredRoot ? [hoveredRoot] : []
}

function onMove(event: PointerEvent) {
  if (editorEnabled.value) return
  if (!focusLocked) setHovered(pick(event))
}

function onLeave() {
  if (editorEnabled.value) return
  if (!focusLocked) setHovered(undefined)
}

function onClick(event: MouseEvent) {
  if (editorEnabled.value) {
    if (transformIsDragging) return
    selectEditorRoot(pick(event))
    return
  }
  if (focusLocked) return
  const root = pick(event) ?? hoveredRoot
  if (root) focus(root)
}

function resize() {
  if (!host.value || !renderer || !camera || !composer) return
  const { width, height } = host.value.getBoundingClientRect()
  camera.aspect = width / Math.max(height, 1)
  camera.updateProjectionMatrix()
  renderer.setSize(width, height, false)
  composer.setSize(width, height)
}

function projectVec(v: THREE.Vector3, w: number, h: number, cam: THREE.PerspectiveCamera) {
  v.project(cam)
  return { x: (v.x * 0.5 + 0.5) * w, y: (-v.y * 0.5 + 0.5) * h, z: v.z }
}

// 投影 3D 包围盒 → 屏幕原始矩形，交给 AutoFitModuleFrames 自适应渲染
function updateModuleFrames() {
  if (!camera || !host.value) { moduleFrames.value = []; return }
  const rect = host.value.getBoundingClientRect()
  const w = rect.width, h = rect.height
  frameLayer.w = w; frameLayer.h = h
  const cam = camera
  const v = new THREE.Vector3()

  moduleFrames.value = interactiveRoots.map((root) => {
    const config = configByRoot.get(root)!
    const bbox = bboxByRoot.get(root) ?? new THREE.Box3().setFromObject(root)
    const min = bbox.min, max = bbox.max
    const pts = [
      new THREE.Vector3(min.x, max.y, min.z), new THREE.Vector3(max.x, max.y, min.z),
      new THREE.Vector3(min.x, min.y, min.z), new THREE.Vector3(max.x, min.y, min.z),
      new THREE.Vector3(min.x, max.y, max.z), new THREE.Vector3(max.x, max.y, max.z),
      new THREE.Vector3(min.x, min.y, max.z), new THREE.Vector3(max.x, min.y, max.z),
    ].map(p => projectVec(v.copy(p), w, h, cam))
    const behind = pts.some(p => p.z <= -1.02 || p.z >= 1.02)
    const x0 = Math.min(...pts.map(p => p.x)), x1 = Math.max(...pts.map(p => p.x))
    const y0 = Math.min(...pts.map(p => p.y)), y1 = Math.max(...pts.map(p => p.y))
    const rectW = Math.max(40, x1 - x0), rectH = Math.max(32, y1 - y0)
    const padX = Math.min(w * 0.03, rectW * 0.10)
    const padTop = Math.min(h * 0.06, rectH * 0.18)
    const padBot = Math.min(h * 0.04, rectH * 0.12)
    const bx = Math.max(4, x0 - padX)
    const by = Math.max(4, y0 - padTop)
    const bw = Math.min(w - 8 - bx, rectW + padX * 2)
    const bh = Math.min(h - 8 - by, rectH + padTop + padBot)
    const id = config.id
    return {
      id,
      kind: id === 'achievement' ? 'parallelogram' : id === 'resource' ? 'rectBase' : 'rect',
      title: config.label,
      box: { x: bx, y: by, w: bw, h: bh },
      visible: !behind && bw > 60 && bh > 50,
    } satisfies RawFrame
  })
}

function updateReviewLabelProjection() {
  if (!showReviewLabels.value || editorEnabled.value || !camera || !host.value) {
    reviewLabels.value = []
    return
  }

  const activeCamera = camera
  const { width, height } = host.value.getBoundingClientRect()
  reviewLabels.value = interactiveRoots.map((root, index) => {
    const config = configByRoot.get(root)!
    root.getWorldPosition(tempPosition)
    tempPosition.y += Math.max(.45, config.tooltipLift * .7)
    tempPosition.project(activeCamera)
    return {
      id: config.id,
      index: String(index + 1).padStart(2, '0'),
      subtitle: config.subtitle,
      label: config.label,
      x: (tempPosition.x * .5 + .5) * width,
      y: (-tempPosition.y * .5 + .5) * height,
      visible: tempPosition.z > -1 && tempPosition.z < 1.05,
    }
  })
}

function animateMaterialState(root: THREE.Group, emphasis: number, emissiveBoost: number) {
  const states = materialStatesByRoot.get(root) ?? []
  states.forEach(({ material, baseColor, baseEmissiveIntensity }) => {
    const targetR = baseColor.r * emphasis
    const targetG = baseColor.g * emphasis
    const targetB = baseColor.b * emphasis
    material.color.r += (targetR - material.color.r) * .10
    material.color.g += (targetG - material.color.g) * .10
    material.color.b += (targetB - material.color.b) * .10
    const targetEmissive = baseEmissiveIntensity * emphasis + emissiveBoost
    material.emissiveIntensity += (targetEmissive - material.emissiveIntensity) * .10
  })
}

function animate() {
  frameId = requestAnimationFrame(animate)
  if (!scene || !camera || !controls || !composer) return

  if (cameraGoal && targetGoal) {
    camera.position.lerp(cameraGoal, .105)
    controls.target.lerp(targetGoal, .105)
    if (camera.position.distanceTo(cameraGoal) < .018 && controls.target.distanceTo(targetGoal) < .018) {
      camera.position.copy(cameraGoal)
      controls.target.copy(targetGoal)
      cameraGoal = undefined
      targetGoal = undefined
      if (unlockControlsAfterMove) {
        controls.enabled = true
        unlockControlsAfterMove = false
      }
    }
  }

  interactiveRoots.forEach((root) => {
    if (editorEnabled.value) {
      animateMaterialState(root, .98, 0)
      return
    }
    const config = configByRoot.get(root)!
    const base = basePositionByRoot.get(root)!
    const isHovered = root === hoveredRoot
    const isSelected = root === selectedRoot
    const active = isHovered || isSelected
    const amount = isSelected ? 1.35 : isHovered ? 1 : 0
    const offset = config.hoverOffset

    tempPosition.set(
      base.x + offset[0] * amount,
      base.y + offset[1] * amount,
      base.z + offset[2] * amount,
    )
    root.position.lerp(tempPosition, .11)

    const scaleFactor = isSelected ? 1.06 : isHovered ? 1.05 : 1
    tempScale.setScalar(config.scale * scaleFactor)
    root.scale.lerp(tempScale, .11)

    const dimmedBySibling = Boolean(hoveredRoot && !active)
    animateMaterialState(root, active ? 1.12 : dimmedBySibling ? .78 : 1.06, active ? .06 : 0)
  })

  updateReviewLabelProjection()
  updateModuleFrames()
  controls.update()
  composer.render()
}

onMounted(async () => {
  if (!host.value) return
  scene = new THREE.Scene()
  scene.background = null

  camera = new THREE.PerspectiveCamera(39, 1, .1, 70)
  camera.position.set(...defaultCamera.position)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' })
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5))
  renderer.outputColorSpace = THREE.SRGBColorSpace
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.12
  renderer.setClearColor(0x000000, 0)
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFShadowMap
  host.value.appendChild(renderer.domElement)

  const pmremGenerator = new THREE.PMREMGenerator(renderer)
  const environment = new RoomEnvironment()
  environmentTarget = pmremGenerator.fromScene(environment, .035)
  scene.environment = environmentTarget.texture
  scene.environmentIntensity = .52
  environment.dispose()
  pmremGenerator.dispose()

  controls = new OrbitControls(camera, renderer.domElement)
  controls.target.set(...defaultCamera.target)
  controls.enableDamping = false
  controls.enableRotate = false
  controls.enableZoom = false
  controls.enablePan = false
  controls.enabled = false

  if (showLayoutEditor) {
    transformControls = new TransformControls(camera, renderer.domElement)
    transformControls.setMode(editorMode.value)
    transformControls.setSize(.84)
    transformControls.addEventListener('dragging-changed', (event) => {
      transformIsDragging = (event as { value: boolean }).value
      if (!transformIsDragging) commitRootToConfig()
    })
    transformControls.addEventListener('objectChange', () => commitRootToConfig())
    // Three r185 exposes TransformControls as a controller and its visual
    // gizmo as a separate Object3D helper.
    scene.add(transformControls.getHelper())
    window.addEventListener('keydown', onEditorKeydown)
  }
  syncEditorValues()

  composer = new EffectComposer(renderer)
  composer.addPass(new RenderPass(scene, camera))
  outline = new OutlinePass(new THREE.Vector2(1, 1), scene, camera)
  outline.edgeStrength = 3.15
  outline.edgeGlow = .08
  outline.edgeThickness = 1.15
  outline.pulsePeriod = 0
  outline.visibleEdgeColor.set('#67d8ff')
  outline.hiddenEdgeColor.set('#123351')
  composer.addPass(outline)

  scene.add(new THREE.AmbientLight(0x5d95c7, .88))
  scene.add(new THREE.HemisphereLight(0xc4e6ff, 0x1b426c, 1.02))

  const key = new THREE.DirectionalLight(0xe8f5ff, 2.05)
  key.position.set(-1.2, 7.4, 6.4)
  key.castShadow = true
  key.shadow.mapSize.set(1536, 1536)
  key.shadow.camera.left = -7
  key.shadow.camera.right = 7
  key.shadow.camera.top = 7
  key.shadow.camera.bottom = -4
  scene.add(key)

  const frontFill = new THREE.DirectionalLight(0xa6daff, 1.42)
  frontFill.position.set(0, 2.8, 8.2)
  scene.add(frontFill)

  const overheadFill = new THREE.DirectionalLight(0xb9deff, .76)
  overheadFill.position.set(0, 6.8, -.8)
  scene.add(overheadFill)

  const leftRim = new THREE.PointLight(0x247dff, 4.5, 12, 2)
  leftRim.position.set(-4.4, 1.4, .6)
  scene.add(leftRim)
  const rightRim = new THREE.PointLight(0x2fd1ff, 4.2, 11, 2)
  rightRim.position.set(4.1, .7, 2.5)
  scene.add(rightRim)
  const rearFill = new THREE.PointLight(0x3478d8, 3.4, 13, 2)
  rearFill.position.set(.2, 3.3, -2.6)
  scene.add(rearFill)
  const floorBounce = new THREE.PointLight(0x176fff, 2.8, 9.5, 2)
  floorBounce.position.set(0, -.8, 2.8)
  scene.add(floorBounce)

  resize()
  resizeObserver = new ResizeObserver(resize)
  resizeObserver.observe(host.value)
  host.value.addEventListener('pointermove', onMove)
  host.value.addEventListener('pointerleave', onLeave)
  host.value.addEventListener('click', onClick)

  const manager = new THREE.LoadingManager()
  manager.onProgress = (_, loaded, total) => {
    progress.value = Math.round((loaded / total) * 100)
  }
  const loader = new GLTFLoader(manager)
  loader.setMeshoptDecoder(MeshoptDecoder)
  const results = await Promise.allSettled(cockpitModules.map((config) => loadModule(config, loader)))
  failedModules.value = results.flatMap((result, index) =>
    result.status === 'rejected' ? [cockpitModules[index].subtitle] : [],
  )
  progress.value = 100
  loading.value = false
  guideTimer = window.setTimeout(() => { showGuide.value = false }, 3600)
  animate()
})

watch(() => props.activeModule, (value, previous) => {
  if (!value && previous) resetCamera()
})

onBeforeUnmount(() => {
  cancelAnimationFrame(frameId)
  window.clearTimeout(panelTimer)
  window.clearTimeout(guideTimer)
  resizeObserver?.disconnect()
  host.value?.removeEventListener('pointermove', onMove)
  host.value?.removeEventListener('pointerleave', onLeave)
  host.value?.removeEventListener('click', onClick)
  window.removeEventListener('keydown', onEditorKeydown)

  scene?.traverse((object) => {
    if (!(object instanceof THREE.Mesh)) return
    object.geometry.dispose()
    const materials = Array.isArray(object.material) ? object.material : [object.material]
    materials.forEach((material) => material.dispose())
  })
  environmentTarget?.dispose()
  transformControls?.dispose()
  composer?.dispose()
  renderer?.dispose()
})
</script>

<style scoped>
.growth-scene {
  position: absolute;
  inset: 0;
  overflow: hidden;
  background: transparent;
  touch-action: none;
}

:global(.cockpit-scene) {
  background:
    linear-gradient(rgba(89, 159, 231, .11), rgba(15, 53, 105, .13)),
    #020713 url('/career-cabin-scene-20260902.png') center / cover no-repeat;
  background-blend-mode: screen, normal;
}


.growth-scene::after {
  position: absolute;
  inset: 0;
  z-index: 3;
  content: '';
  pointer-events: none;
  background: radial-gradient(circle at 50% 44%, transparent 75%, rgba(1, 6, 16, .035) 100%);
}

.growth-scene__bgwrap {
  position: absolute;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  background: #020713;
}
.growth-scene__bgwrap video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: .5;
  filter: saturate(1.15) blur(1px);
}
.growth-scene__bgwrap::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 50% 42%, rgba(4, 18, 48, .12), rgba(2, 7, 19, .72) 80%);
}

.growth-scene :deep(canvas) {
  position: absolute;
  inset: 0;
  z-index: 1;
  display: block;
  width: 100%;
  height: 100%;
}

.growth-scene__loading {
  position: absolute;
  inset: 0;
  z-index: 3;
  display: grid;
  place-content: center;
  justify-items: center;
  gap: 12px;
  background: radial-gradient(circle, rgba(5, 39, 91, .64), #01040b 64%);
  color: #c8f3ff;
  font: 500 11px/1.4 Bahnschrift, sans-serif;
  letter-spacing: .18em;
}

.growth-scene__loading p { margin: 0; }
.growth-scene__loading strong { color: #5be4ff; font-size: 26px; }
.growth-scene__loader-orbit {
  width: 52px;
  height: 52px;
  border: 2px solid rgba(86, 217, 255, .18);
  border-top-color: #65e6ff;
  border-radius: 50%;
  animation: spin 1.1s linear infinite;
}

.growth-scene__fallback {
  position: absolute;
  right: 22px;
  bottom: 22px;
  z-index: 2;
  display: grid;
  gap: 4px;
  max-width: 310px;
  padding: 11px 14px;
  border: 1px solid rgba(100, 219, 255, .24);
  border-radius: 6px;
  background: rgba(3, 17, 42, .78);
  color: #e9faff;
  backdrop-filter: blur(12px);
  font: 600 10px/1.4 Bahnschrift, sans-serif;
  letter-spacing: .12em;
}

.growth-scene__fallback span {
  color: #85cbe8;
  font-size: 10px;
  font-weight: 400;
  letter-spacing: .04em;
}

.growth-scene__guide {
  position: absolute;
  left: 50%;
  bottom: 24px;
  z-index: 2;
  transform: translateX(-50%);
  padding: 8px 13px;
  border: 1px solid rgba(105, 216, 255, .20);
  border-radius: 4px;
  background: rgba(1, 14, 39, .68);
  color: rgba(213, 243, 255, .68);
  font: 500 9px/1 Bahnschrift, sans-serif;
  letter-spacing: .12em;
  backdrop-filter: blur(10px);
  animation: guideOut .6s 3s both;
}

.growth-scene__readout {
  position: absolute;
  right: 28px;
  bottom: 24px;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(158, 225, 255, .5);
  font: 500 9px/1 Bahnschrift, sans-serif;
  letter-spacing: .17em;
  pointer-events: none;
}

.growth-scene__readout i {
  display: block;
  width: 28px;
  height: 1px;
  background: rgba(52, 202, 255, .72);
  box-shadow: 0 0 7px rgba(52, 202, 255, .55);
}

.growth-scene__readout em {
  color: rgba(110, 208, 255, .32);
  font-style: normal;
  font-size: 8px;
}

.growth-scene__model-label {
  position: absolute;
  z-index: 2;
  display: grid;
  min-width: 124px;
  padding: 7px 10px 8px 28px;
  transform: translate(-50%, -100%);
  border: 1px dashed rgba(111, 224, 255, .78);
  border-radius: 3px;
  background: linear-gradient(90deg, rgba(7, 28, 50, .9), rgba(8, 36, 61, .68));
  box-shadow: 0 0 18px rgba(38, 180, 255, .16);
  color: #d9f7ff;
  pointer-events: none;
}
.growth-scene__model-label::after {
  position: absolute;
  bottom: -15px;
  left: 50%;
  width: 1px;
  height: 14px;
  background: repeating-linear-gradient(to bottom, #7ce8ff 0 3px, transparent 3px 6px);
  content: '';
}
.growth-scene__model-label > span {
  position: absolute;
  top: -1px;
  bottom: -1px;
  left: -1px;
  display: grid;
  width: 21px;
  place-items: center;
  background: #4acff4;
  color: #062239;
  font: 800 9px/1 Bahnschrift, sans-serif;
  letter-spacing: .05em;
}
.growth-scene__model-label b {
  color: #ecfbff;
  font: 700 9px/1.2 Bahnschrift, sans-serif;
  letter-spacing: .1em;
}
.growth-scene__model-label small {
  margin-top: 3px;
  color: rgba(206, 243, 255, .76);
  font: 500 11px/1.15 "Microsoft YaHei", sans-serif;
}

.layout-editor__toggle {
  position: absolute;
  top: 18px;
  right: 18px;
  z-index: 5;
  padding: 9px 13px;
  border: 1px solid rgba(93, 211, 255, .5);
  border-radius: 6px;
  background: rgba(3, 18, 43, .86);
  color: #d9f6ff;
  box-shadow: 0 8px 28px rgba(0, 0, 0, .28);
  cursor: pointer;
  font: 600 11px/1 "Microsoft YaHei", sans-serif;
  backdrop-filter: blur(12px);
}

.layout-editor__toggle.active {
  border-color: #73e5ff;
  background: #0a3b5d;
  color: #fff;
}

/* ===== 模块外框调节面板 ===== */
.frame-tuner__toggle {
  position: absolute;
  top: 18px;
  right: 128px;
  z-index: 5;
  padding: 9px 13px;
  border: 1px solid rgba(93, 211, 255, .5);
  border-radius: 6px;
  background: rgba(3, 18, 43, .86);
  color: #d9f6ff;
  box-shadow: 0 8px 28px rgba(0, 0, 0, .28);
  cursor: pointer;
  font: 600 11px/1 "Microsoft YaHei", sans-serif;
  backdrop-filter: blur(12px);
}
.frame-tuner__toggle.active {
  border-color: #73e5ff;
  background: #0a3b5d;
  color: #fff;
}

.frame-tuner {
  position: absolute;
  top: 62px;
  right: 128px;
  z-index: 5;
  display: grid;
  gap: 10px;
  width: 268px;
  padding: 14px;
  border: 1px solid rgba(93, 211, 255, .35);
  border-radius: 10px;
  background: rgba(3, 18, 43, .92);
  backdrop-filter: blur(14px);
  box-shadow: 0 18px 48px rgba(0, 0, 0, .4);
}
.frame-tuner header { display: grid; gap: 3px; }
.frame-tuner header span { color: #7ce8ff; font: 700 9px/1 Bahnschrift, sans-serif; letter-spacing: .16em; }
.frame-tuner header strong { color: #eafaff; font: 600 12px/1.2 "Microsoft YaHei", sans-serif; }

.frame-tuner__row {
  display: grid;
  grid-template-columns: 88px 1fr 34px;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: rgba(217, 246, 255, .85);
}
.frame-tuner__row input[type="range"] {
  width: 100%;
  height: 14px;
  accent-color: #55d6ff;
  cursor: pointer;
}
.frame-tuner__row i {
  font: 700 10px/1 Bahnschrift, monospace;
  color: #8fe9ff;
  text-align: right;
  font-style: normal;
}

.frame-tuner__actions { display: flex; gap: 8px; }
.frame-tuner__actions button {
  flex: 1;
  padding: 8px 0;
  border: 1px solid rgba(93, 211, 255, .55);
  border-radius: 6px;
  background: rgba(10, 59, 93, .9);
  color: #dff9ff;
  cursor: pointer;
  font: 600 11px/1 "Microsoft YaHei", sans-serif;
}
.frame-tuner__actions button:hover { background: #0d4a75; }
.frame-tuner__hint {
  margin: 0;
  font-size: 10px;
  line-height: 1.5;
  color: rgba(185, 225, 245, .55);
}

.layout-editor {
  position: absolute;
  top: 62px;
  right: 18px;
  z-index: 5;
  display: grid;
  width: 254px;
  gap: 11px;
  max-height: calc(100% - 82px);
  overflow: auto;
  padding: 14px;
  border: 1px solid rgba(89, 207, 255, .42);
  border-radius: 8px;
  background: rgba(2, 14, 35, .92);
  box-shadow: 0 18px 60px rgba(0, 0, 0, .42), inset 0 0 22px rgba(33, 160, 255, .06);
  color: #dff8ff;
  backdrop-filter: blur(16px);
}
.layout-editor--left { right: auto; left: 18px; }

.layout-editor header { display: grid; gap: 4px; }
.layout-editor header span { color: #69dfff; font: 600 9px/1 Bahnschrift, sans-serif; letter-spacing: .16em; }
.layout-editor header strong { min-height: 16px; font: 600 14px/1.2 Bahnschrift, "Microsoft YaHei", sans-serif; }
.layout-editor__hint { margin: 0; color: rgba(197, 231, 244, .67); font: 400 11px/1.45 "Microsoft YaHei", sans-serif; }
.layout-editor__modes, .layout-editor__actions { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }
.layout-editor button {
  min-height: 29px;
  border: 1px solid rgba(107, 213, 255, .25);
  border-radius: 4px;
  background: rgba(67, 158, 214, .09);
  color: #bcecff;
  cursor: pointer;
  font: 500 10px/1 "Microsoft YaHei", sans-serif;
}
.layout-editor button:hover, .layout-editor button.active { border-color: #68dcff; background: rgba(56, 180, 247, .24); color: #fff; }
.layout-editor__section { display: grid; gap: 7px; padding-top: 9px; border-top: 1px solid rgba(120, 202, 236, .15); }
.layout-editor__section b, .layout-editor__camera summary { color: rgba(126, 224, 255, .78); font: 600 9px/1 Bahnschrift, sans-serif; letter-spacing: .14em; }
.layout-editor__fields { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }
.layout-editor label { display: grid; gap: 4px; color: rgba(178, 223, 239, .58); font: 600 9px/1 Bahnschrift, sans-serif; }
.layout-editor input {
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
  padding: 6px 5px;
  border: 1px solid rgba(108, 203, 238, .20);
  border-radius: 3px;
  outline: none;
  background: rgba(0, 5, 17, .65);
  color: #f0fbff;
  font: 500 11px/1 Bahnschrift, monospace;
}
.layout-editor input:focus { border-color: #52ddff; }
.layout-editor__scale { grid-template-columns: 1fr 1fr; align-items: end; }
.layout-editor__actions { grid-template-columns: 1fr 1.35fr; }
.layout-editor__camera { display: grid; gap: 9px; padding-top: 9px; border-top: 1px solid rgba(120, 202, 236, .15); }
.layout-editor__camera summary { cursor: pointer; }
.layout-editor__fov { width: 72px; }
.layout-editor__export { width: 100%; border-color: rgba(111, 229, 255, .55) !important; background: rgba(31, 145, 207, .22) !important; }
.layout-editor__message { color: #82e8ff; font: 500 10px/1.35 "Microsoft YaHei", sans-serif; }

@keyframes spin { to { transform: rotate(360deg); } }
@keyframes guideOut { to { opacity: 0; transform: translate(-50%, 6px); } }

@media (max-width: 760px) {
  .growth-scene__readout { right: 14px; bottom: 14px; }
  .growth-scene__readout em { display: none; }
  .growth-scene__guide { width: calc(100% - 32px); bottom: 14px; text-align: center; font-size: 8px; }
  .growth-scene__fallback { right: 12px; bottom: 46px; }
}
</style>

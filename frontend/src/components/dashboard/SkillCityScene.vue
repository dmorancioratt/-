<template>
  <div ref="hostRef" class="skill-city" @pointermove="handlePointerMove" @pointerleave="hoveredName = ''" @click="handleClick">
    <canvas ref="canvasRef" aria-label="可交互的个人技能三维城市"></canvas>
    <div class="skill-city__hud">
      <span><i class="dot mastered"></i>已有证据</span>
      <span><i class="dot growing"></i>正在提升</span>
      <span><i class="dot missing"></i>目标缺口</span>
    </div>
    <div v-if="hoveredName" class="skill-city__hover">{{ hoveredName }}</div>
    <div class="skill-city__axis">
      <b>{{ activeItem?.name || '个人能力核心' }}</b>
      <small>{{ activeItem ? `能力强度 ${activeItem.score}% · ${activeItem.category}` : '点击建筑查看技能证据' }}</small>
    </div>
  </div>
</template>

<script setup lang="ts">
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

export type SkillCityItem = {
  name: string
  score: number
  category: string
  status: 'mastered' | 'growing' | 'missing'
}

const props = defineProps<{ items: SkillCityItem[]; selected?: string }>()
const emit = defineEmits<{ select: [item: SkillCityItem] }>()

const hostRef = ref<HTMLDivElement>()
const canvasRef = ref<HTMLCanvasElement>()
const hoveredName = ref('')
const activeItem = computed(() => props.items.find((item) => item.name === props.selected) || props.items[0])

let scene: THREE.Scene | undefined
let camera: THREE.PerspectiveCamera | undefined
let renderer: THREE.WebGLRenderer | undefined
let controls: OrbitControls | undefined
let frame = 0
let resizeObserver: ResizeObserver | undefined
let buildings: THREE.Mesh[] = []
let lastFrame = 0
const raycaster = new THREE.Raycaster()
const pointer = new THREE.Vector2()

const colors = {
  mastered: 0x28d7f5,
  growing: 0x3e83ff,
  missing: 0xffa84d
}

function setup() {
  if (!canvasRef.value || !hostRef.value) return
  scene = new THREE.Scene()
  scene.fog = new THREE.FogExp2(0x030a1d, 0.035)
  camera = new THREE.PerspectiveCamera(42, 1, 0.1, 120)
  camera.position.set(15, 13, 18)

  renderer = new THREE.WebGLRenderer({ canvas: canvasRef.value, antialias: true, alpha: true, powerPreference: 'high-performance' })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5))
  renderer.setClearColor(0x030a1d, 0)
  renderer.outputColorSpace = THREE.SRGBColorSpace

  scene.add(new THREE.HemisphereLight(0x8feaff, 0x061123, 2.1))
  const keyLight = new THREE.DirectionalLight(0x52cfff, 2.8)
  keyLight.position.set(8, 18, 10)
  scene.add(keyLight)
  const fillLight = new THREE.PointLight(0x346dff, 45, 36)
  fillLight.position.set(-10, 8, -5)
  scene.add(fillLight)

  const ground = new THREE.Mesh(
    new THREE.CircleGeometry(18, 64),
    new THREE.MeshStandardMaterial({ color: 0x05152e, roughness: 0.88, metalness: 0.18, transparent: true, opacity: 0.92 })
  )
  ground.rotation.x = -Math.PI / 2
  ground.position.y = -0.03
  scene.add(ground)

  const grid = new THREE.GridHelper(32, 24, 0x1a7ec2, 0x0b315b)
  const materials = Array.isArray(grid.material) ? grid.material : [grid.material]
  materials.forEach((material) => { material.transparent = true; material.opacity = 0.16 })
  scene.add(grid)

  controls = new OrbitControls(camera, canvasRef.value)
  controls.enableDamping = true
  controls.dampingFactor = 0.06
  controls.enablePan = false
  controls.minDistance = 12
  controls.maxDistance = 32
  controls.maxPolarAngle = Math.PI * 0.48
  controls.target.set(0, 2.4, 0)

  buildCity()
  resize()
  resizeObserver = new ResizeObserver(resize)
  resizeObserver.observe(hostRef.value)
  document.addEventListener('visibilitychange', handleVisibility)
  animate(0)
}

function buildCity() {
  if (!scene) return
  buildings.forEach((mesh) => {
    scene?.remove(mesh)
    mesh.geometry.dispose()
    if (Array.isArray(mesh.material)) mesh.material.forEach((material) => material.dispose())
    else mesh.material.dispose()
  })
  buildings = []

  const items = props.items.length ? props.items : [
    { name: '个人能力核心', score: 72, category: '综合能力', status: 'mastered' as const }
  ]
  items.slice(0, 18).forEach((item, index) => {
    const ring = Math.floor(index / 6)
    const indexInRing = index % 6
    const count = Math.min(6, items.length - ring * 6)
    const radius = ring === 0 ? 4.1 : ring === 1 ? 8 : 11.2
    const angle = (indexInRing / Math.max(count, 1)) * Math.PI * 2 + ring * 0.36
    const height = 1.2 + Math.max(0, Math.min(100, item.score)) / 15
    const width = ring === 0 ? 1.8 : 1.45
    const geometry = new THREE.BoxGeometry(width, height, width)
    const baseColor = colors[item.status]
    const material = new THREE.MeshStandardMaterial({
      color: baseColor,
      emissive: baseColor,
      emissiveIntensity: item.name === props.selected ? 0.66 : 0.18,
      roughness: 0.42,
      metalness: 0.38,
      transparent: true,
      opacity: item.status === 'missing' ? 0.74 : 0.92
    })
    const mesh = new THREE.Mesh(geometry, material)
    mesh.position.set(Math.cos(angle) * radius, height / 2, Math.sin(angle) * radius)
    mesh.userData.skill = item
    buildings.push(mesh)
    scene?.add(mesh)

    const crown = new THREE.LineSegments(
      new THREE.EdgesGeometry(geometry),
      new THREE.LineBasicMaterial({ color: item.status === 'missing' ? 0xffd18c : 0xa9f2ff, transparent: true, opacity: 0.44 })
    )
    crown.position.copy(mesh.position)
    crown.userData.parentBuilding = mesh
    scene?.add(crown)
  })
  focusSelected(false)
}

function setPointer(event: PointerEvent | MouseEvent) {
  const rect = canvasRef.value?.getBoundingClientRect()
  if (!rect) return false
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1
  return true
}

function hitTest(event: PointerEvent | MouseEvent) {
  if (!camera || !setPointer(event)) return undefined
  raycaster.setFromCamera(pointer, camera)
  return raycaster.intersectObjects(buildings, false)[0]?.object as THREE.Mesh | undefined
}

function handlePointerMove(event: PointerEvent) {
  const mesh = hitTest(event)
  hoveredName.value = mesh?.userData.skill?.name || ''
  if (canvasRef.value) canvasRef.value.style.cursor = mesh ? 'pointer' : 'grab'
}

function handleClick(event: MouseEvent) {
  const item = hitTest(event)?.userData.skill as SkillCityItem | undefined
  if (item) emit('select', item)
}

function focusSelected(moveCamera = true) {
  const selected = buildings.find((mesh) => mesh.userData.skill?.name === props.selected) || buildings[0]
  buildings.forEach((mesh) => {
    const material = mesh.material as THREE.MeshStandardMaterial
    material.emissiveIntensity = mesh === selected ? 0.72 : 0.18
  })
  if (!selected || !controls || !camera || !moveCamera) return
  controls.target.copy(selected.position)
  controls.target.y = Math.max(1.8, selected.position.y * 0.75)
  const direction = camera.position.clone().sub(controls.target).normalize().multiplyScalar(15)
  camera.position.copy(controls.target.clone().add(direction))
  controls.update()
}

function resize() {
  if (!hostRef.value || !camera || !renderer) return
  const { clientWidth, clientHeight } = hostRef.value
  camera.aspect = clientWidth / Math.max(clientHeight, 1)
  camera.updateProjectionMatrix()
  renderer.setSize(clientWidth, clientHeight, false)
}

function animate(time: number) {
  frame = requestAnimationFrame(animate)
  if (document.hidden || time - lastFrame < 32) return
  lastFrame = time
  controls?.update()
  renderer?.render(scene!, camera!)
}

function handleVisibility() {
  if (!document.hidden) lastFrame = 0
}

watch(() => props.items, () => nextTick(buildCity), { deep: true })
watch(() => props.selected, () => focusSelected(true))

onMounted(setup)
onBeforeUnmount(() => {
  cancelAnimationFrame(frame)
  document.removeEventListener('visibilitychange', handleVisibility)
  resizeObserver?.disconnect()
  controls?.dispose()
  buildings.forEach((mesh) => {
    mesh.geometry.dispose()
    if (Array.isArray(mesh.material)) mesh.material.forEach((material) => material.dispose())
    else mesh.material.dispose()
  })
  renderer?.dispose()
  scene?.clear()
})
</script>

<style scoped>
.skill-city { position: relative; width: 100%; height: 100%; min-height: 470px; overflow: hidden; background: radial-gradient(circle at 50% 42%, rgba(23, 108, 181, 0.2), transparent 48%); }
.skill-city canvas { display: block; width: 100%; height: 100%; outline: none; }
.skill-city__hud { position: absolute; left: 16px; bottom: 14px; display: flex; flex-wrap: wrap; gap: 12px; color: #83a8c4; font-size: 10px; }
.skill-city__hud span { display: inline-flex; align-items: center; gap: 6px; }
.dot { width: 7px; height: 7px; border-radius: 50%; }
.dot.mastered { background: #28d7f5; box-shadow: 0 0 8px rgba(40, 215, 245, 0.8); }
.dot.growing { background: #3e83ff; box-shadow: 0 0 8px rgba(62, 131, 255, 0.8); }
.dot.missing { background: #ffa84d; box-shadow: 0 0 8px rgba(255, 168, 77, 0.8); }
.skill-city__axis { position: absolute; left: 16px; top: 16px; max-width: 260px; border-left: 2px solid #22f7ff; padding: 5px 0 5px 10px; }
.skill-city__axis b { display: block; color: #effbff; font-size: 15px; }
.skill-city__axis small { display: block; margin-top: 5px; color: #7fa2bd; font-size: 10px; }
.skill-city__hover { position: absolute; right: 14px; top: 14px; border: 1px solid rgba(73, 208, 255, 0.28); border-radius: 7px; padding: 6px 9px; background: rgba(3, 19, 45, 0.86); color: #b9f3ff; font-size: 11px; pointer-events: none; }
@media (max-width: 1320px) { .skill-city { min-height: 420px; } }
</style>

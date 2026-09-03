<template>
  <div ref="hostRef" class="trust-core" @pointermove="handlePointerMove" @pointerleave="hovered = ''" @click="handleClick">
    <canvas ref="canvasRef" aria-label="可信知识核心三维数据流"></canvas>
    <div class="trust-core__status">
      <span>可信知识核心</span>
      <strong>{{ trustRate }}%</strong>
      <small>事实校验通过率</small>
    </div>
    <div class="trust-core__legend">
      <span><i class="normal"></i>可信数据</span>
      <span><i class="review"></i>等待复核</span>
      <span><i class="risk"></i>风险事件</span>
    </div>
    <div v-if="hovered" class="trust-core__hover">{{ hovered }}</div>
  </div>
</template>

<script setup lang="ts">
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

export type TrustCoreNode = {
  name: string
  status: 'normal' | 'review' | 'risk'
  value: number
}

const props = defineProps<{ nodes: TrustCoreNode[]; trustRate: number }>()
const emit = defineEmits<{ select: [item: TrustCoreNode] }>()

const hostRef = ref<HTMLDivElement>()
const canvasRef = ref<HTMLCanvasElement>()
const hovered = ref('')
let scene: THREE.Scene | undefined
let camera: THREE.PerspectiveCamera | undefined
let renderer: THREE.WebGLRenderer | undefined
let controls: OrbitControls | undefined
let coreGroup: THREE.Group | undefined
let nodeMeshes: THREE.Mesh[] = []
let frame = 0
let lastFrame = 0
let resizeObserver: ResizeObserver | undefined
const raycaster = new THREE.Raycaster()
const pointer = new THREE.Vector2()

const nodeColors = { normal: 0x28d7f5, review: 0xffb85c, risk: 0xff6682 }

function setup() {
  if (!hostRef.value || !canvasRef.value) return
  scene = new THREE.Scene()
  camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100)
  camera.position.set(0, 2, 15)
  renderer = new THREE.WebGLRenderer({ canvas: canvasRef.value, antialias: true, alpha: true, powerPreference: 'high-performance' })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5))
  renderer.setClearColor(0x030a1d, 0)

  scene.add(new THREE.AmbientLight(0x6fcfff, 1.2))
  const light = new THREE.PointLight(0x37dcff, 70, 38)
  light.position.set(5, 7, 8)
  scene.add(light)
  const backLight = new THREE.PointLight(0x355dff, 55, 34)
  backLight.position.set(-7, -3, -5)
  scene.add(backLight)

  controls = new OrbitControls(camera, canvasRef.value)
  controls.enableDamping = true
  controls.dampingFactor = 0.06
  controls.enablePan = false
  controls.minDistance = 10
  controls.maxDistance = 22

  buildCore()
  resize()
  resizeObserver = new ResizeObserver(resize)
  resizeObserver.observe(hostRef.value)
  animate(0)
}

function buildCore() {
  if (!scene) return
  if (coreGroup) {
    scene.remove(coreGroup)
    coreGroup.traverse((object) => {
      const mesh = object as THREE.Mesh
      mesh.geometry?.dispose?.()
      if (Array.isArray(mesh.material)) mesh.material.forEach((material) => material.dispose())
      else mesh.material?.dispose?.()
    })
  }
  nodeMeshes = []
  coreGroup = new THREE.Group()
  scene.add(coreGroup)

  const globe = new THREE.Mesh(
    new THREE.SphereGeometry(3.2, 40, 28),
    new THREE.MeshStandardMaterial({ color: 0x063b6d, emissive: 0x086a9a, emissiveIntensity: 0.38, wireframe: true, transparent: true, opacity: 0.72 })
  )
  coreGroup.add(globe)

  const inner = new THREE.Mesh(
    new THREE.SphereGeometry(2.72, 32, 22),
    new THREE.MeshPhongMaterial({ color: 0x0a5b88, emissive: 0x0b7ca6, emissiveIntensity: 0.2, transparent: true, opacity: 0.25 })
  )
  coreGroup.add(inner)

  ;[
    { radius: 4.5, tilt: 0.26 },
    { radius: 5.6, tilt: -0.48 },
    { radius: 6.7, tilt: 0.82 }
  ].forEach((ring, index) => {
    const mesh = new THREE.Mesh(
      new THREE.TorusGeometry(ring.radius, 0.018 + index * 0.008, 8, 110),
      new THREE.MeshBasicMaterial({ color: index === 2 ? 0x0aa9b4 : 0x22f7ff, transparent: true, opacity: 0.32 })
    )
    mesh.rotation.x = Math.PI / 2 + ring.tilt
    mesh.rotation.y = index * 0.48
    coreGroup?.add(mesh)
  })

  const nodes = props.nodes.length ? props.nodes : [{ name: '知识库', status: 'normal' as const, value: 100 }]
  nodes.slice(0, 12).forEach((item, index) => {
    const angle = (index / nodes.length) * Math.PI * 2
    const radius = 4.5 + (index % 3) * 1.08
    const y = Math.sin(angle * 1.7) * 2.05
    const position = new THREE.Vector3(Math.cos(angle) * radius, y, Math.sin(angle) * radius)
    const color = nodeColors[item.status]
    const node = new THREE.Mesh(
      new THREE.SphereGeometry(0.18 + Math.min(item.value, 100) / 700, 18, 14),
      new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 0.82, roughness: 0.34 })
    )
    node.position.copy(position)
    node.userData.node = item
    nodeMeshes.push(node)
    coreGroup?.add(node)

    const points = [position.clone().normalize().multiplyScalar(3.2), position]
    const line = new THREE.Line(
      new THREE.BufferGeometry().setFromPoints(points),
      new THREE.LineBasicMaterial({ color, transparent: true, opacity: item.status === 'normal' ? 0.3 : 0.62 })
    )
    coreGroup?.add(line)
  })
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
  return raycaster.intersectObjects(nodeMeshes, false)[0]?.object as THREE.Mesh | undefined
}

function handlePointerMove(event: PointerEvent) {
  const mesh = hitTest(event)
  hovered.value = mesh?.userData.node?.name || ''
  if (canvasRef.value) canvasRef.value.style.cursor = mesh ? 'pointer' : 'grab'
}

function handleClick(event: MouseEvent) {
  const item = hitTest(event)?.userData.node as TrustCoreNode | undefined
  if (item) emit('select', item)
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
  if (coreGroup) coreGroup.rotation.y += 0.0007
  renderer?.render(scene!, camera!)
}

watch(() => props.nodes, buildCore, { deep: true })
onMounted(setup)
onBeforeUnmount(() => {
  cancelAnimationFrame(frame)
  resizeObserver?.disconnect()
  controls?.dispose()
  if (coreGroup) {
    coreGroup.traverse((object) => {
      const mesh = object as THREE.Mesh
      mesh.geometry?.dispose?.()
      if (Array.isArray(mesh.material)) mesh.material.forEach((material) => material.dispose())
      else mesh.material?.dispose?.()
    })
  }
  renderer?.dispose()
  scene?.clear()
})
</script>

<style scoped>
.trust-core { position: relative; width: 100%; height: 100%; min-height: 460px; overflow: hidden; background: radial-gradient(circle at 50% 48%, rgba(10, 117, 181, 0.2), transparent 50%); }
.trust-core canvas { display: block; width: 100%; height: 100%; }
.trust-core__status { position: absolute; left: 50%; top: 50%; display: grid; place-items: center; width: 154px; height: 154px; border-radius: 50%; color: #c9f6ff; text-align: center; pointer-events: none; transform: translate(-50%, -50%); }
.trust-core__status span { font-size: 10px; letter-spacing: 0.14em; }
.trust-core__status strong { color: #f4fdff; font-size: 30px; line-height: 1; text-shadow: 0 0 20px rgba(54, 215, 255, 0.5); }
.trust-core__status small { color: #78a1bd; font-size: 9px; }
.trust-core__legend { position: absolute; left: 14px; bottom: 13px; display: flex; flex-wrap: wrap; gap: 12px; color: #7fa2bd; font-size: 9px; }
.trust-core__legend span { display: inline-flex; align-items: center; gap: 5px; }
.trust-core__legend i { width: 6px; height: 6px; border-radius: 50%; }
.trust-core__legend .normal { background: #28d7f5; }.trust-core__legend .review { background: #ffb85c; }.trust-core__legend .risk { background: #ff6682; }
.trust-core__hover { position: absolute; right: 13px; top: 13px; border: 1px solid rgba(73, 208, 255, 0.3); border-radius: 7px; padding: 6px 9px; background: rgba(3, 19, 45, 0.88); color: #b9f3ff; font-size: 10px; pointer-events: none; }
</style>

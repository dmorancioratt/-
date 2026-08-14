<template>
  <div class="skill-tree-container" ref="containerRef">
    <canvas ref="canvasRef" class="skill-tree-canvas"></canvas>
    
    <div v-if="mode === 'hotspot'" class="hotspot-overlay">
      <div class="hotspot-header">
        <h2>能力热点树</h2>
        <p>SKILL HOTSPOT TREE · 苹果大小与颜色代表能力热度</p>
      </div>
      <div class="hotspot-legend">
        <div class="legend-item"><span class="apple-dot hot"></span><span>高热能力</span></div>
        <div class="legend-item"><span class="apple-dot warm"></span><span>中热能力</span></div>
        <div class="legend-item"><span class="apple-dot cool"></span><span>新兴能力</span></div>
      </div>
      <div v-if="selectedFruit" class="fruit-info-panel">
        <div class="fruit-info-header">
          <span class="fruit-dot" :style="{background: selectedFruit.color}"></span>
          <h3>{{ selectedFruit.name }}</h3>
        </div>
        <div class="fruit-info-meta">
          <div class="meta-row"><span>热度值</span><b>{{ selectedFruit.heat }}</b></div>
          <div class="meta-row"><span>分类</span><b>{{ selectedFruit.category }}</b></div>
          <div class="meta-row"><span>趋势</span><b :class="selectedFruit.trend">{{ selectedFruit.trendLabel }}</b></div>
        </div>
      </div>
    </div>

    <div v-if="mode === 'version'" class="tree-legend">
      <div class="legend-item"><span class="dot new"></span><span>新增嫩芽</span></div>
      <div class="legend-item"><span class="dot dead"></span><span>淘汰枯叶</span></div>
      <div class="legend-item"><span class="dot core"></span><span>核心枝干</span></div>
    </div>
    <div v-if="mode === 'version'" class="tree-version-label">
      <span class="from">{{ fromVersion }}</span>
      <span class="arrow">→</span>
      <span class="to">{{ toVersion }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import * as THREE from 'three'
import { Tree } from '@/lib/ez-tree/index.js'

interface HotSkill {
  name: string
  heat: number
  category?: string
  trend?: 'up' | 'down' | 'stable'
}

interface SkillTreeProps {
  mode?: 'version' | 'hotspot'
  addedSkills?: string[]
  removedSkills?: string[]
  coreSkills?: string[]
  fromVersion?: string
  toVersion?: string
  hotSkills?: HotSkill[]
}

const props = withDefaults(defineProps<SkillTreeProps>(), {
  mode: 'version',
  addedSkills: () => ['Python', 'FastAPI', 'RAG', 'LLM微调'],
  removedSkills: () => ['Flash', 'jQuery'],
  coreSkills: () => ['JavaScript', 'Vue', 'React', 'Node.js', 'TypeScript'],
  fromVersion: 'v1.1',
  toVersion: 'v1.2',
  hotSkills: () => [
    { name: '大模型', heat: 18.5, category: '人工智能', trend: 'up' },
    { name: 'RAG', heat: 17.2, category: '人工智能', trend: 'up' },
    { name: 'Agent', heat: 16.8, category: '人工智能', trend: 'up' },
    { name: '多模态', heat: 15.3, category: '人工智能', trend: 'up' },
    { name: 'Prompt工程', heat: 14.7, category: '人工智能', trend: 'up' },
    { name: '微调', heat: 13.9, category: '人工智能', trend: 'stable' },
    { name: 'Python', heat: 18.1, category: '编程语言', trend: 'stable' },
    { name: 'TypeScript', heat: 16.5, category: '编程语言', trend: 'up' },
    { name: 'Rust', heat: 12.4, category: '编程语言', trend: 'up' },
    { name: 'Vue', heat: 15.8, category: '前端框架', trend: 'stable' },
    { name: 'React', heat: 15.2, category: '前端框架', trend: 'stable' },
    { name: 'Kubernetes', heat: 14.1, category: '云原生', trend: 'stable' },
    { name: '微服务', heat: 13.3, category: '架构设计', trend: 'stable' },
    { name: '向量数据库', heat: 15.6, category: '数据技术', trend: 'up' },
    { name: '数据治理', heat: 11.8, category: '数据技术', trend: 'stable' },
    { name: '安全合规', heat: 12.9, category: '安全', trend: 'up' }
  ]
})

const emit = defineEmits<{
  (e: 'select-fruit', skill: HotSkill): void
}>()

const containerRef = ref<HTMLDivElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const selectedFruit = ref<(HotSkill & { color: string }) | null>(null)

let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let renderer: THREE.WebGLRenderer | null = null
let tree: Tree | null = null
let sprouts: THREE.Mesh[] = []
let deadLeaves: THREE.Mesh[] = []
let fruits: THREE.Mesh[] = []
let fruitData: Array<{ skill: HotSkill; color: string; baseScale: number }> = []
let raycaster: THREE.Raycaster | null = null
let mouse: THREE.Vector2 | null = null
let frameId = 0
let time = 0

function heatToColor(heat: number): string {
  if (heat >= 16) return '#ff6b35'
  if (heat >= 14) return '#ffb65c'
  if (heat >= 12) return '#69f0ae'
  return '#4ed8ff'
}

function heatToEmissive(heat: number): number {
  if (heat >= 16) return 0xff4400
  if (heat >= 14) return 0xff9900
  if (heat >= 12) return 0x00cc66
  return 0x0099cc
}

function getFruitPositions(count: number): Array<[number, number, number]> {
  const positions: Array<[number, number, number]> = []
  const layers = [
    { yRange: [4, 7], radiusX: 4, radiusZ: 3, count: Math.ceil(count * 0.3) },
    { yRange: [7, 11], radiusX: 6, radiusZ: 4.5, count: Math.ceil(count * 0.4) },
    { yRange: [11, 14], radiusX: 4, radiusZ: 3, count: Math.ceil(count * 0.3) }
  ]
  
  layers.forEach(layer => {
    for (let i = 0; i < layer.count && positions.length < count; i++) {
      const angle = (i / layer.count) * Math.PI * 2 + (Math.random() - 0.5) * 0.6
      const rx = layer.radiusX * (0.65 + Math.random() * 0.35)
      const rz = layer.radiusZ * (0.65 + Math.random() * 0.35)
      const x = Math.cos(angle) * rx
      const z = Math.sin(angle) * rz
      const y = layer.yRange[0] + Math.random() * (layer.yRange[1] - layer.yRange[0])
      positions.push([x, y, z])
    }
  })
  
  return positions.slice(0, count)
}

function initTree() {
  if (!canvasRef.value || !containerRef.value) return

  try {
    const w = containerRef.value.clientWidth || window.innerWidth
    const h = containerRef.value.clientHeight || window.innerHeight

    scene = new THREE.Scene()
    scene.background = null
    scene.background = new THREE.Color(0x041022)
    scene.fog = new THREE.FogExp2(0x041022, 0.015)

    camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 1000)
    
    if (props.mode === 'hotspot') {
      camera.position.set(0, 9, 28)
      camera.lookAt(0, 7, 0)
    } else {
      camera.position.set(0, 7, 24)
      camera.lookAt(0, 5, 0)
    }

    renderer = new THREE.WebGLRenderer({
      canvas: canvasRef.value,
      antialias: true,
      alpha: true
    })
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5))
    renderer.setSize(w, h)
    renderer.shadowMap.enabled = true
    renderer.shadowMap.type = THREE.PCFSoftShadowMap

    scene.add(new THREE.AmbientLight(0xffffff, props.mode === 'hotspot' ? 1.8 : 1.4))
    const sun = new THREE.DirectionalLight(0xffffee, props.mode === 'hotspot' ? 1.4 : 1.1)
    sun.position.set(8, 20, 12)
    sun.castShadow = true
    scene.add(sun)
    const fill = new THREE.DirectionalLight(0x88ddff, props.mode === 'hotspot' ? 0.7 : 0.4)
    fill.position.set(-5, 10, -5)
    scene.add(fill)
    
    if (props.mode === 'hotspot') {
      const rimLight = new THREE.PointLight(0x4ed8ff, 0.9, 60)
      rimLight.position.set(-12, 10, 12)
      scene.add(rimLight)
      const warmLight = new THREE.PointLight(0xffb65c, 0.6, 50)
      warmLight.position.set(10, 14, -8)
      scene.add(warmLight)
    }

    const ground = new THREE.Mesh(
      new THREE.CircleGeometry(props.mode === 'hotspot' ? 22 : 10, 48),
      new THREE.MeshLambertMaterial({ 
        color: 0x0a2540,
        transparent: true,
        opacity: 0.6
      })
    )
    ground.rotation.x = -Math.PI / 2
    ground.position.y = -0.1
    ground.receiveShadow = true
    scene.add(ground)

    if (props.mode === 'hotspot') {
      const groundGlow = new THREE.Mesh(
        new THREE.CircleGeometry(15, 48),
        new THREE.MeshBasicMaterial({
          color: 0x4ed8ff,
          transparent: true,
          opacity: 0.08
        })
      )
      groundGlow.rotation.x = -Math.PI / 2
      groundGlow.position.y = 0.02
      scene.add(groundGlow)
    }

    tree = new Tree()
    
    if (props.mode === 'hotspot') {
      tree.loadPreset('oak_large')
      tree.options.seed = 88
      tree.options.bark.textured = false
      tree.options.bark.flatShading = true
      tree.options.bark.tint = 0x5d4037
      tree.options.leaves.count = 50
      tree.options.leaves.size = 2.0
      tree.options.leaves.textured = false
      tree.options.leaves.tint = 0x2e7d32
      tree.options.leaves.alphaTest = 0.2
    } else {
      tree.options.seed = 42
      tree.options.bark.textured = false
      tree.options.bark.flatShading = true
      const coreRatio = Math.min(1, props.coreSkills.length / 10)
      const addRatio = Math.min(1, props.addedSkills.length / 6)
      const barkColor = new THREE.Color(0x5d4037).lerp(new THREE.Color(0x8d6e63), coreRatio)
      tree.options.bark.tint = barkColor.getHex()
      tree.options.leaves.textured = false
      tree.options.leaves.count = 18 + Math.floor(addRatio * 10)
      tree.options.leaves.size = 1.3 + addRatio * 0.4
      const leafBase = new THREE.Color(0x2e7d32)
      const leafBright = new THREE.Color(0x66bb6a)
      const leafColor = leafBase.lerp(leafBright, coreRatio * 0.6 + addRatio * 0.3)
      tree.options.leaves.tint = leafColor.getHex()
      tree.options.leaves.alphaTest = 0.3
    }
    
    tree.generate()
    
    if (props.mode === 'hotspot') {
      tree.scale.setScalar(1.5)
      addFruitsToTree()
      raycaster = new THREE.Raycaster()
      mouse = new THREE.Vector2()
      canvasRef.value.addEventListener('click', onCanvasClick)
      canvasRef.value.style.cursor = 'pointer'
    } else {
      tree.scale.setScalar(1.0)
      const addRatio = Math.min(1, props.addedSkills.length / 6)
      const removeRatio = Math.min(1, props.removedSkills.length / 4)
      addSprouts(addRatio)
      addDeadLeaves(removeRatio)
    }
    
    tree.position.y = 0
    tree.castShadow = true
    tree.receiveShadow = true
    scene.add(tree)

    const animate = () => {
      frameId = requestAnimationFrame(animate)
      time += 0.016
      
      if (tree) {
        const swayAmount = props.mode === 'hotspot' ? 0.06 : 0.15
        tree.rotation.y = Math.sin(time * 0.15) * swayAmount
        tree.update(time * 0.6)
      }
      
      if (props.mode === 'hotspot') {
        fruits.forEach((fruit, i) => {
          const data = fruitData[i]
          if (!data) return
          const breathe = 1 + Math.sin(time * 1.8 + i * 0.5) * 0.12
          const floatY = Math.sin(time * 1.2 + i * 0.7) * 0.08
          fruit.scale.setScalar(data.baseScale * breathe)
          fruit.position.y += Math.sin(time * 0.8 + i) * 0.0008
          if (fruit.userData.glow) {
            fruit.userData.glow.scale.setScalar(1.5 + Math.sin(time * 2 + i * 0.6) * 0.3)
          }
        })
      } else {
        sprouts.forEach((s, i) => {
          const breathe = 1 + Math.sin(time * 2 + i * 0.7) * 0.25
          s.scale.setScalar(breathe)
          s.position.y += Math.sin(time * 1.5 + i) * 0.002
        })
        deadLeaves.forEach((l, i) => {
          l.rotation.y = time * (0.8 + i * 0.2)
          l.rotation.x = Math.sin(time * 0.6 + i) * 0.4
          l.position.y -= 0.008 + (i % 3) * 0.003
          l.position.x += Math.sin(time * 1.2 + i * 0.5) * 0.004
          if (l.position.y < -1) {
            l.position.y = 4 + Math.random() * 4
            l.position.x = (Math.random() - 0.5) * 6
            l.position.z = (Math.random() - 0.5) * 4
          }
        })
      }
      
      renderer!.render(scene!, camera!)
    }
    animate()

    window.addEventListener('resize', handleResize)
  } catch (e) {
    console.error('Tree init failed:', e)
  }
}

function addFruitsToTree() {
  if (!tree || !scene) return
  const skills = props.hotSkills.slice(0, 16)
  const positions = getFruitPositions(skills.length)
  fruitData = []
  fruits = []

  skills.forEach((skill, i) => {
    const pos = positions[i] || [0, 7 + Math.random() * 4, (Math.random() - 0.5) * 4]
    const heat = Number(skill.heat)
    const color = heatToColor(heat)
    const emissive = heatToEmissive(heat)
    const baseScale = 0.35 + (heat / 20) * 0.35

    const fruitGeo = new THREE.SphereGeometry(0.5, 16, 16)
    const fruitMat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(color),
      emissive: new THREE.Color(emissive),
      emissiveIntensity: 0.5,
      metalness: 0.15,
      roughness: 0.25
    })
    const fruit = new THREE.Mesh(fruitGeo, fruitMat)
    fruit.position.set(
      pos[0] + (Math.random() - 0.5) * 1.0,
      pos[1] + (Math.random() - 0.5) * 0.6,
      pos[2] + (Math.random() - 0.5) * 1.0
    )
    fruit.castShadow = true
    fruit.userData.skillIndex = i

    const glowGeo = new THREE.SphereGeometry(0.9, 12, 12)
    const glowMat = new THREE.MeshBasicMaterial({
      color: new THREE.Color(color),
      transparent: true,
      opacity: 0.2
    })
    const glow = new THREE.Mesh(glowGeo, glowMat)
    fruit.add(glow)
    fruit.userData.glow = glow

    const stemGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.3, 8)
    const stemMat = new THREE.MeshLambertMaterial({ color: 0x5d4037 })
    const stem = new THREE.Mesh(stemGeo, stemMat)
    stem.position.y = 0.6
    stem.rotation.x = (Math.random() - 0.5) * 0.4
    stem.rotation.z = (Math.random() - 0.5) * 0.4
    fruit.add(stem)

    if (heat >= 16) {
      const leafGeo = new THREE.PlaneGeometry(0.35, 0.25)
      const leafMat = new THREE.MeshBasicMaterial({ 
        color: 0x4caf50, 
        side: THREE.DoubleSide, 
        transparent: true, 
        opacity: 0.85 
      })
      const leaf = new THREE.Mesh(leafGeo, leafMat)
      leaf.position.set(0.25, 0.65, 0)
      leaf.rotation.z = Math.PI / 4
      fruit.add(leaf)
    }

    tree!.add(fruit)
    fruits.push(fruit)
    fruitData.push({ skill, color, baseScale })
  })
}

function onCanvasClick(event: MouseEvent) {
  if (!canvasRef.value || !raycaster || !mouse || !camera || !scene) return
  
  const rect = canvasRef.value.getBoundingClientRect()
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1
  
  raycaster.setFromCamera(mouse, camera)
  const intersects = raycaster.intersectObjects(fruits)
  
  if (intersects.length > 0) {
    const fruit = intersects[0].object as THREE.Mesh
    const idx = fruit.userData.skillIndex as number
    if (idx !== undefined && fruitData[idx]) {
      selectedFruit.value = {
        ...fruitData[idx].skill,
        color: fruitData[idx].color,
        trendLabel: fruitData[idx].skill.trend === 'up' ? '↑ 快速上升' : fruitData[idx].skill.trend === 'down' ? '↓ 下降' : '→ 稳定'
      }
      emit('select-fruit', fruitData[idx].skill)
    }
  }
}

function addSprouts(ratio: number) {
  if (!tree || !scene) return
  const count = props.addedSkills.length
  const positions = [
    [0, 5.5, 0.3],
    [1.2, 6, -0.5],
    [-1.5, 5.2, 0.8],
    [0.8, 7, 0.5],
    [-0.6, 6.5, -0.8],
    [2, 4.5, 0.2],
    [-2, 4.8, -0.3],
  ]
  for (let i = 0; i < count; i++) {
    const pos = positions[i % positions.length]
    const sproutGeo = new THREE.SphereGeometry(0.25 + Math.random() * 0.1, 8, 8)
    const sproutMat = new THREE.MeshBasicMaterial({
      color: 0x76ff03,
      transparent: true,
      opacity: 0.9
    })
    const sprout = new THREE.Mesh(sproutGeo, sproutMat)
    sprout.position.set(pos[0] + (Math.random()-0.5)*0.4, pos[1] + (Math.random()-0.5)*0.3, pos[2])
    const glowGeo = new THREE.SphereGeometry(0.45, 8, 8)
    const glowMat = new THREE.MeshBasicMaterial({
      color: 0x69f0ae,
      transparent: true,
      opacity: 0.3
    })
    const glow = new THREE.Mesh(glowGeo, glowMat)
    sprout.add(glow)
    tree.add(sprout)
    sprouts.push(sprout)
  }
}

function addDeadLeaves(ratio: number) {
  if (!tree || !scene) return
  const count = props.removedSkills.length
  for (let i = 0; i < count + 2; i++) {
    const leafGeo = new THREE.PlaneGeometry(0.35, 0.25)
    const leafMat = new THREE.MeshBasicMaterial({
      color: i < count ? 0xbcaaa4 : 0x8d6e63,
      transparent: true,
      opacity: 0.85,
      side: THREE.DoubleSide
    })
    const leaf = new THREE.Mesh(leafGeo, leafMat)
    leaf.position.set(
      (Math.random() - 0.5) * 7,
      3 + Math.random() * 5,
      (Math.random() - 0.5) * 4
    )
    leaf.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI)
    scene.add(leaf)
    deadLeaves.push(leaf)
  }
}

function handleResize() {
  if (!containerRef.value || !camera || !renderer) return
  const w = containerRef.value.clientWidth
  const h = containerRef.value.clientHeight
  camera.aspect = w / h
  camera.updateProjectionMatrix()
  renderer.setSize(w, h)
}

function cleanup() {
  cancelAnimationFrame(frameId)
  if (canvasRef.value && props.mode === 'hotspot') {
    canvasRef.value.removeEventListener('click', onCanvasClick)
  }
  if (renderer) renderer.dispose()
  if (scene) scene.traverse((c: any) => {
    if (c.geometry) c.geometry.dispose()
    if (c.material) {
      if (Array.isArray(c.material)) c.material.forEach((m: any) => m.dispose())
      else c.material.dispose()
    }
  })
  sprouts = []
  deadLeaves = []
  fruits = []
  fruitData = []
  tree = null
  scene = null
  camera = null
  renderer = null
  raycaster = null
  mouse = null
}

onMounted(() => {
  setTimeout(initTree, 200)
})

watch(() => props.mode, () => {
  cleanup()
  setTimeout(initTree, 100)
})

onBeforeUnmount(() => {
  cleanup()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.skill-tree-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  border-radius: 8px;
}

.skill-tree-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  display: block;
}

.hotspot-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 10;
}

.hotspot-header {
  position: absolute;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
  pointer-events: none;
}

.hotspot-header h2 {
  margin: 0;
  font-size: 28px;
  font-weight: 900;
  color: #eafcff;
  text-shadow: 0 0 20px rgba(78, 216, 255, 0.6), 0 2px 10px rgba(0, 0, 0, 0.5);
  letter-spacing: 4px;
}

.hotspot-header p {
  margin: 8px 0 0;
  font-size: 12px;
  color: #78a9c8;
  letter-spacing: 2px;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.8);
}

.hotspot-legend {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 24px;
  padding: 14px 28px;
  background: rgba(4, 22, 50, 0.8);
  backdrop-filter: blur(12px);
  border-radius: 10px;
  border: 1px solid rgba(78, 216, 255, 0.3);
  pointer-events: auto;
}

.apple-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 8px;
  vertical-align: middle;
}

.apple-dot.hot { background: radial-gradient(circle at 30% 30%, #ff8a5c, #ff6b35); box-shadow: 0 0 12px rgba(255, 107, 53, 0.7); }
.apple-dot.warm { background: radial-gradient(circle at 30% 30%, #ffd080, #ffb65c); box-shadow: 0 0 10px rgba(255, 182, 92, 0.6); }
.apple-dot.cool { background: radial-gradient(circle at 30% 30%, #80ffe8, #69f0ae); box-shadow: 0 0 10px rgba(105, 240, 174, 0.6); }

.hotspot-legend .legend-item {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #b8e0f0;
  font-weight: 500;
}

.fruit-info-panel {
  position: absolute;
  top: 100px;
  right: 24px;
  width: 240px;
  padding: 20px;
  background: rgba(4, 22, 50, 0.85);
  backdrop-filter: blur(16px);
  border-radius: 12px;
  border: 1px solid rgba(78, 216, 255, 0.35);
  pointer-events: auto;
  animation: panelIn 0.3s ease-out;
}

@keyframes panelIn {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}

.fruit-info-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(78, 216, 255, 0.2);
}

.fruit-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  box-shadow: 0 0 12px currentColor;
}

.fruit-info-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #eafcff;
}

.fruit-info-meta {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.meta-row span {
  color: #78a9c8;
}

.meta-row b {
  color: #eafcff;
  font-weight: 600;
}

.meta-row b.up { color: #ff6b35; }
.meta-row b.down { color: #8f7cff; }

.tree-legend {
  position: absolute;
  bottom: 16px;
  left: 16px;
  display: flex;
  gap: 18px;
  padding: 10px 18px;
  background: rgba(4, 22, 50, 0.75);
  backdrop-filter: blur(8px);
  border-radius: 8px;
  border: 1px solid rgba(70, 200, 255, 0.25);
  z-index: 10;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  color: #b8e0f0;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot.new { background: #76ff03; box-shadow: 0 0 10px #69f0ae; }
.dot.dead { background: #bcaaa4; box-shadow: 0 0 6px #8d6e63; }
.dot.core { background: #66bb6a; }

.tree-version-label {
  position: absolute;
  top: 14px;
  right: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  background: rgba(4, 22, 50, 0.75);
  backdrop-filter: blur(8px);
  border-radius: 8px;
  border: 1px solid rgba(70, 200, 255, 0.25);
  font-size: 14px;
  font-weight: 600;
  z-index: 10;
}

.tree-version-label .from { color: #ffb74d; }
.tree-version-label .arrow { color: #66ffcc; font-size: 18px; }
.tree-version-label .to { color: #69f0ae; }
</style>

<template>
  <div ref="containerRef" class="evolution-tree-container">
    <!-- Loading overlay -->
    <div v-if="loading" class="tree-loading">
      <div class="loading-spinner"></div>
      <div class="loading-text">正在加载能力树...</div>
    </div>

    <canvas ref="canvasRef" class="tree-canvas" :class="{ 'canvas-ready': !loading }"></canvas>

    <!-- Toolbar -->
    <div v-if="!loading" class="tree-toolbar">
      <button class="toolbar-btn" @click="resetView" title="重置视角">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
        <span>重置视角</span>
      </button>
    </div>

    <div v-if="selectedFruit" class="fruit-info-panel" :class="{ visible: panelVisible }">
      <button class="panel-close" @click="closePanel">×</button>
      <div class="panel-header">
        <div class="skill-icon" :style="{ background: selectedFruit.color }">{{ selectedFruit.name?.charAt(0) }}</div>
        <div class="skill-title-wrap">
          <h3 class="skill-title">{{ selectedFruit.name }}</h3>
          <div class="skill-tags">
            <span class="tag heat-tag" :class="selectedFruit.heatLevel">{{ selectedFruit.heat }}° 热度</span>
            <span class="tag trend-tag">{{ selectedFruit.trendLabel }}</span>
          </div>
        </div>
      </div>
      <div class="panel-body">
        <div class="info-section">
          <div class="info-row">
            <span class="info-label">技能分类</span>
            <span class="info-value">{{ selectedFruit.category || '综合技能' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">热度指数</span>
            <span class="info-value" :style="{ color: selectedFruit.color }">{{ selectedFruit.heat }}°</span>
          </div>
          <div class="info-row">
            <span class="info-label">岗位数量</span>
            <span class="info-value">{{ selectedFruit.jobs }}+ 个</span>
          </div>
          <div class="info-row">
            <span class="info-label">平均薪资</span>
            <span class="info-value salary">{{ selectedFruit.salary }}</span>
          </div>
        </div>
        <div class="info-section">
          <h4 class="section-title">相关课程</h4>
          <div class="course-list">
            <div v-for="(course, i) in selectedFruit.courses" :key="i" class="course-item">
              <div class="course-icon">📚</div>
              <div class="course-info">
                <div class="course-name">{{ course.name }}</div>
                <div class="course-meta">{{ course.duration }} · {{ course.level }}</div>
              </div>
              <button class="course-btn">开始学习</button>
            </div>
          </div>
        </div>
        <div class="info-section">
          <h4 class="section-title">热门岗位</h4>
          <div class="job-tags">
            <span v-for="(job, i) in selectedFruit.relatedJobs" :key="i" class="job-tag">{{ job }}</span>
          </div>
        </div>
        <div class="panel-actions">
          <button class="action-btn primary">加入学习路径</button>
          <button class="action-btn secondary">查看岗位详情</button>
        </div>
      </div>
    </div>
    <svg v-if="selectedFruit && panelVisible" ref="connectorSvg" class="connector-svg"></svg>
    <div class="tree-hint" v-if="!selectedFruit && !loading">
      <span class="hint-icon">✦</span> 点击技能节点查看详情
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js'
import { createScene } from '../lib/ez-tree/scene/scene.js'

interface Skill {
  name: string
  heat: number
  trend: 'up' | 'down' | 'stable'
  category: string
  jobs?: number
  salary?: string
  relatedJobs?: string[]
  courses?: Array<{ name: string; duration: string; level: string; status: string }>
}

interface HotSkill {
  name: string
  heat: number
  trend?: 'up' | 'down' | 'stable'
  category?: string
  jobs?: number
  salary?: string
  relatedJobs?: string[]
  courses?: Array<{ name: string; duration: string; level: string; status: string }>
}

const props = withDefaults(defineProps<{
  mode?: 'hotspot' | 'version'
  year?: number
  compareYear?: number
  hotSkills?: HotSkill[]
}>(), {
  hotSkills: () => []
})

const emit = defineEmits<{
  (e: 'select-fruit', skill: HotSkill): void
}>()

const containerRef = ref<HTMLDivElement>()
const canvasRef = ref<HTMLCanvasElement>()
const connectorSvg = ref<SVGSVGElement>()
const selectedFruit = ref<any>(null)
const panelVisible = ref(false)
const loading = ref(true)

let renderer: THREE.WebGLRenderer | null = null
let labelRenderer: CSS2DRenderer | null = null
let sceneCtx: any = null
let fruits: THREE.Object3D[] = []
let flowers: THREE.InstancedMesh | null = null
let animFrameId: number
let raycaster: THREE.Raycaster
let mouse: THREE.Vector2
let ripples: Array<{ mesh: THREE.Mesh; startTime: number; color: THREE.Color }> = []
let particles: Array<{ mesh: THREE.Mesh; velocity: THREE.Vector3; startTime: number }> = []
let time = 0

// ─── Blue-tech color palette ───────────────────────────────────────────────
// High-heat / core: vivid cyan-blue
const COLOR_HOT = new THREE.Color(0x4ed8ff)
// Warm / important: bright ice-blue
const COLOR_WARM = new THREE.Color(0x3d86ff)
// Rising: light blue
const COLOR_RISING = new THREE.Color(0x7eb8ff)
// Cool / gap: muted blue-gray (low brightness — implies "needs growth")
const COLOR_COOL = new THREE.Color(0x5a8aaa)
// Decorative flower tints (all blue family)
const DECOR_COLORS = [0x3d6fa0, 0x4a82b8, 0x5a94c8, 0x2f6090, 0x6aaad4]
// Flower center
const COLOR_CENTER = new THREE.Color(0x8de4ff)

const defaultSkills: Skill[] = [
  { name: 'React', heat: 18, trend: 'up', category: '前端框架', salary: '25-50K', relatedJobs: ['前端工程师', '全栈工程师'], courses: [{ name: 'React高级进阶', duration: '48课时', level: '高级', status: 'available' }] },
  { name: 'TypeScript', heat: 19, trend: 'up', category: '编程语言', salary: '20-45K', relatedJobs: ['前端工程师', 'Node.js工程师'], courses: [{ name: 'TypeScript实战', duration: '36课时', level: '中级', status: 'available' }] },
  { name: 'Vue3', heat: 16, trend: 'up', category: '前端框架', salary: '20-40K', relatedJobs: ['前端工程师', 'Vue开发工程师'], courses: [{ name: 'Vue3 Composition API', duration: '32课时', level: '中级', status: 'available' }] },
  { name: 'Node.js', heat: 15, trend: 'stable', category: '后端开发', salary: '22-45K', relatedJobs: ['后端工程师', '全栈工程师'], courses: [{ name: 'Node.js企业级开发', duration: '56课时', level: '高级', status: 'available' }] },
  { name: 'Python', heat: 20, trend: 'up', category: '编程语言', salary: '18-50K', relatedJobs: ['后端工程师', 'AI工程师', '数据分析师'], courses: [{ name: 'Python数据分析', duration: '40课时', level: '入门', status: 'available' }] },
  { name: 'Java', heat: 14, trend: 'stable', category: '编程语言', salary: '18-40K', relatedJobs: ['后端工程师', 'Java开发'], courses: [{ name: 'Java微服务架构', duration: '64课时', level: '高级', status: 'available' }] },
  { name: 'Docker', heat: 13, trend: 'stable', category: 'DevOps', salary: '20-45K', relatedJobs: ['运维工程师', 'DevOps工程师'], courses: [{ name: 'Docker容器化部署', duration: '24课时', level: '中级', status: 'available' }] },
  { name: 'Kubernetes', heat: 12, trend: 'up', category: 'DevOps', salary: '28-60K', relatedJobs: ['云原生工程师', 'SRE'], courses: [{ name: 'K8s实战指南', duration: '48课时', level: '高级', status: 'available' }] },
  { name: '机器学习', heat: 17, trend: 'up', category: 'AI', salary: '30-70K', relatedJobs: ['AI工程师', '算法工程师'], courses: [{ name: '机器学习基础', duration: '60课时', level: '中级', status: 'available' }] },
  { name: '大模型开发', heat: 21, trend: 'up', category: 'AI', salary: '35-80K', relatedJobs: ['大模型工程师', 'Prompt工程师'], courses: [{ name: 'LLM应用开发', duration: '40课时', level: '高级', status: 'available' }] },
  { name: '数据结构', heat: 11, trend: 'stable', category: '基础', salary: '15-35K', relatedJobs: ['算法工程师', '后端工程师'], courses: [{ name: '数据结构与算法', duration: '56课时', level: '入门', status: 'available' }] },
  { name: 'Git', heat: 10, trend: 'stable', category: '工具', salary: '-', relatedJobs: ['所有开发岗位'], courses: [{ name: 'Git版本控制', duration: '12课时', level: '入门', status: 'available' }] },
]

function getSkills(): Skill[] {
  try {
    const hs = props.hotSkills
    if (Array.isArray(hs)) {
      if (hs.length > 0) {
        const mapped: Skill[] = []
        for (let i = 0; i < hs.length; i++) {
          const s = hs[i] as any
          mapped.push({
            name: s?.name || '未知技能',
            heat: Number(s?.heat) || 10,
            trend: (s?.trend as 'up'|'down'|'stable') || 'stable',
            category: s?.category || '技能',
            jobs: s?.jobs,
            salary: s?.salary,
            relatedJobs: s?.relatedJobs,
            courses: s?.courses
          })
        }
        if (mapped.length > 0) return mapped
      }
      return defaultSkills
    }
    return defaultSkills
  } catch (e) {
    console.error('getSkills error:', e)
    return defaultSkills
  }
}

function createNodeGeometry(nodeColor: THREE.Color): THREE.Group {
  const group = new THREE.Group()
  // Core orb
  const coreMat = new THREE.MeshStandardMaterial({
    color: nodeColor,
    roughness: 0.3,
    metalness: 0.4,
    transparent: true,
    opacity: 0.95,
    emissive: nodeColor,
    emissiveIntensity: 0.6
  })
  const coreGeom = new THREE.IcosahedronGeometry(1, 1)
  const core = new THREE.Mesh(coreGeom, coreMat)
  group.add(core)
  // Small inner highlight sphere
  const innerGeom = new THREE.SphereGeometry(0.5, 8, 6)
  const innerMat = new THREE.MeshBasicMaterial({
    color: new THREE.Color(0xffffff),
    transparent: true,
    opacity: 0.3
  })
  const inner = new THREE.Mesh(innerGeom, innerMat)
  group.add(inner)
  return group
}

function createGlowMaterial(color: THREE.Color): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    uniforms: {
      glowColor: { value: color },
      time: { value: 0 }
    },
    vertexShader: `
      varying vec3 vNormal;
      void main() {
        vNormal = normalize(normalMatrix * normal);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform vec3 glowColor;
      uniform float time;
      varying vec3 vNormal;
      void main() {
        float intensity = pow(0.75 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 3.0);
        float pulse = 0.8 + 0.2 * sin(time * 1.8);
        gl_FragColor = vec4(glowColor, intensity * pulse * 0.3);
      }
    `,
    side: THREE.BackSide,
    blending: THREE.AdditiveBlending,
    transparent: true,
    depthWrite: false
  })
}

function getFruitPositions(count: number): Array<[number, number, number]> {
  const positions: Array<[number, number, number]> = []
  // Spread nodes across three layers visible from the front view
  // Wider left-right spread, controlled depth
  const layers = [
    { yRange: [22, 34] as [number, number], radiusX: 28, radiusZ: 16, count: Math.ceil(count * 0.3) },
    { yRange: [34, 48] as [number, number], radiusX: 34, radiusZ: 20, count: Math.ceil(count * 0.5) },
    { yRange: [48, 58] as [number, number], radiusX: 18, radiusZ: 12, count: Math.ceil(count * 0.2) }
  ]
  layers.forEach(layer => {
    for (let i = 0; i < layer.count && positions.length < count; i++) {
      const angle = (i / layer.count) * Math.PI * 2 + (Math.random() - 0.5) * 0.5
      const rx = layer.radiusX * (0.8 + Math.random() * 0.3)
      const rz = layer.radiusZ * (0.7 + Math.random() * 0.4)
      const x = Math.cos(angle) * rx
      const z = Math.sin(angle) * rz
      const y = layer.yRange[0] + Math.random() * (layer.yRange[1] - layer.yRange[0])
      positions.push([x, y, z])
    }
  })
  return positions.slice(0, count)
}

function getFlowerPositions(count: number): Array<[number, number, number]> {
  const positions: Array<[number, number, number]> = []
  for (let i = 0; i < count; i++) {
    const layer = Math.random()
    let y: number, rx: number, rz: number
    if (layer < 0.12) {
      y = 18 + Math.random() * 14
      rx = 20 + Math.random() * 14
      rz = 16 + Math.random() * 10
    } else if (layer < 0.55) {
      y = 30 + Math.random() * 20
      rx = 26 + Math.random() * 20
      rz = 20 + Math.random() * 16
    } else if (layer < 0.85) {
      y = 44 + Math.random() * 18
      rx = 20 + Math.random() * 16
      rz = 16 + Math.random() * 12
    } else {
      y = 56 + Math.random() * 12
      rx = 10 + Math.random() * 10
      rz = 8 + Math.random() * 8
    }
    const angle = Math.random() * Math.PI * 2
    const distFactor = 0.6 + Math.random() * 0.5
    positions.push([Math.cos(angle) * rx * distFactor, y, Math.sin(angle) * rz * distFactor])
  }
  return positions
}

function getHeatColor(heat: number): THREE.Color {
  if (heat >= 18) return COLOR_HOT.clone()
  if (heat >= 14) return COLOR_WARM.clone()
  if (heat >= 11) return COLOR_RISING.clone()
  return COLOR_COOL.clone()
}

function getHeatLevel(heat: number): string {
  if (heat >= 18) return 'hot'
  if (heat >= 14) return 'warm'
  if (heat >= 11) return 'rising'
  return 'cool'
}

async function initTree() {
  if (!canvasRef.value || !containerRef.value) return

  renderer = new THREE.WebGLRenderer({
    canvas: canvasRef.value,
    antialias: true,
    alpha: true,
    powerPreference: 'high-performance'
  })

  labelRenderer = new CSS2DRenderer()
  labelRenderer.setSize(containerRef.value.clientWidth, containerRef.value.clientHeight)
  labelRenderer.domElement.style.position = 'absolute'
  labelRenderer.domElement.style.top = '0'
  labelRenderer.domElement.style.left = '0'
  labelRenderer.domElement.style.pointerEvents = 'none'
  labelRenderer.domElement.style.zIndex = '2'
  containerRef.value.appendChild(labelRenderer.domElement)

  sceneCtx = await createScene(canvasRef.value, renderer)
  const { scene, camera, controls, tree, composer } = sceneCtx

  // Add decorative particles first (lower visual priority)
  addDecorativeFlowers(tree)

  // Add skill nodes
  addSkillFruits(tree, camera)

  // Setup interaction
  setupInteraction(camera, scene, controls)

  // Mark loading as complete
  loading.value = false

  // Start animation
  animate(composer, controls, camera)
}

function addDecorativeFlowers(tree: THREE.Object3D) {
  const flowerCount = 100
  const flowerGeom = new THREE.SphereGeometry(0.6, 6, 4)

  const flowerMat = new THREE.MeshStandardMaterial({
    color: 0x4a82b8,
    roughness: 0.6,
    metalness: 0.1,
    transparent: true,
    opacity: 0.7,
    emissive: 0x3d6fa0,
    emissiveIntensity: 0.05
  })
  flowers = new THREE.InstancedMesh(flowerGeom, flowerMat, flowerCount)
  const dummy = new THREE.Object3D()
  const color = new THREE.Color()
  const flowerPositions = getFlowerPositions(flowerCount)
  for (let i = 0; i < flowerCount; i++) {
    const pos = flowerPositions[i]
    dummy.position.set(pos[0], pos[1], pos[2])
    const s = 0.4 + Math.random() * 0.6
    dummy.scale.set(s, s * 0.5, s)
    dummy.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI * 2, 0)
    dummy.updateMatrix()
    flowers.setMatrixAt(i, dummy.matrix)
    color.setHex(DECOR_COLORS[Math.floor(Math.random() * DECOR_COLORS.length)])
    flowers.setColorAt(i, color)
  }
  flowers.instanceMatrix.needsUpdate = true
  if (flowers.instanceColor) flowers.instanceColor.needsUpdate = true
  tree.add(flowers)
}

function addSkillFruits(tree: THREE.Object3D, _camera: THREE.Camera) {
  const skillsToUse = getSkills()
  const positions = getFruitPositions(skillsToUse.length)

  for (let i = 0; i < skillsToUse.length; i++) {
    const skill = skillsToUse[i]
    const color = getHeatColor(skill.heat)
    const fruitGroup = new THREE.Group()

    const node = createNodeGeometry(color)
    const baseScale = 0.8 + Math.random() * 0.4
    node.scale.setScalar(baseScale)
    fruitGroup.add(node)

    // Glow shell (only, no per-node PointLight — expensive)
    const glowGeom = new THREE.SphereGeometry(2.0, 12, 12)
    const glowMat = createGlowMaterial(color)
    const glow = new THREE.Mesh(glowGeom, glowMat)
    fruitGroup.add(glow)

    // Larger invisible hit area for easier clicking
    const hitGeom = new THREE.SphereGeometry(4, 10, 8)
    const hitMat = new THREE.MeshBasicMaterial({
      transparent: true,
      opacity: 0,
      depthWrite: false,
      side: THREE.DoubleSide
    })
    const hitArea = new THREE.Mesh(hitGeom, hitMat)
    hitArea.userData.isHitArea = true
    fruitGroup.add(hitArea)

    fruitGroup.position.set(positions[i][0], positions[i][1], positions[i][2])
    fruitGroup.userData.skillIndex = i
    fruitGroup.userData.baseScale = baseScale
    fruitGroup.userData.originalY = positions[i][1]
    fruitGroup.userData.color = color
    fruitGroup.userData.skill = skill

    // Skill name label
    const labelDiv = document.createElement('div')
    labelDiv.className = 'skill-label'
    const hex = '#' + color.getHexString()
    labelDiv.innerHTML = `<span class="label-text" style="border-color: ${hex}; color: ${hex}">${skill.name}</span>`
    const label = new CSS2DObject(labelDiv)
    label.position.set(0, 3, 0)
    fruitGroup.add(label)

    tree.add(fruitGroup)
    fruits.push(fruitGroup)
  }

  // Expose test function globally
  ;(window as any).__selectSkillFruit = (index: number) => {
    if (index >= 0 && index < fruits.length) {
      const fruit = fruits[index]
      selectFruit(fruit, sceneCtx.scene)
    }
  }
}

function selectFruit(fruit: THREE.Object3D, scene: THREE.Scene) {
  const data: any = {
    color: fruit.userData.color,
    baseScale: fruit.userData.baseScale,
    skill: fruit.userData.skill
  }
  data.clicked = true
  data.clickTime = time
  createClickRipple(fruit.position.clone(), data.color, scene)
  createParticleBurst(fruit.position.clone(), data.color, scene)
  fruit.scale.setScalar(data.baseScale * 1.5)
  fruit.userData.clicked = true
  fruit.userData.clickTime = time
  const skill = data.skill
  const trendLabel = skill.trend === 'up' ? '↑ 快速上升' : skill.trend === 'down' ? '↓ 下降' : '→ 稳定'
  const relatedJobs = skill.relatedJobs || [`${skill.category || '相关'}工程师`, `${skill.name}开发`, `${skill.name}专家`]
  const salary = skill.salary || ['15-30K', '20-40K', '25-50K', '30-60K'][Math.floor(Math.random() * 4)]
  const jobs = skill.jobs || Math.floor(Math.random() * 5000 + 1000)
  const courses = skill.courses || [
    { name: skill.name + '从入门到精通', duration: '48课时', level: '入门', status: 'available' },
    { name: skill.name + '实战项目', duration: '36课时', level: '中级', status: 'available' }
  ]

  selectedFruit.value = {
    ...skill,
    color: '#' + data.color.getHexString(),
    heatLevel: getHeatLevel(skill.heat),
    trendLabel,
    jobs,
    salary,
    relatedJobs,
    courses
  }
  panelVisible.value = true

  emit('select-fruit', skill)

  setTimeout(() => {
    if (sceneCtx && sceneCtx.camera) {
      updateConnectorPosition(sceneCtx.camera)
    }
  }, 100)
}

function setupInteraction(camera: THREE.Camera, scene: THREE.Scene, controls: any) {
  if (!canvasRef.value) return
  raycaster = new THREE.Raycaster()
  mouse = new THREE.Vector2()
  canvasRef.value.addEventListener('click', (e) => onCanvasClick(e, camera, scene))
  canvasRef.value.addEventListener('mousemove', (e) => onCanvasMouseMove(e, camera, scene))
  window.addEventListener('resize', () => onResize(camera, renderer!))
  onResize(camera, renderer!)
}

function onCanvasClick(event: MouseEvent, camera: THREE.Camera, scene: THREE.Scene) {
  if (!canvasRef.value) return
  const rect = canvasRef.value.getBoundingClientRect()
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1
  raycaster.setFromCamera(mouse, camera)
  const intersects = raycaster.intersectObjects(fruits, true)
  if (intersects.length > 0) {
    let fruit: THREE.Object3D | null = intersects[0].object
    while (fruit && fruit.userData.skillIndex === undefined) {
      fruit = fruit.parent
    }
    if (fruit && fruit.userData.skillIndex !== undefined) {
      selectFruit(fruit, scene)
    }
  }
}

function onCanvasMouseMove(event: MouseEvent, camera: THREE.Camera, scene: THREE.Scene) {
  if (!canvasRef.value) return
  const rect = canvasRef.value.getBoundingClientRect()
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1
  raycaster.setFromCamera(mouse, camera)
  const intersects = raycaster.intersectObjects(fruits, true)
  let foundFruit: THREE.Object3D | null = null
  if (intersects.length > 0) {
    foundFruit = intersects[0].object
    while (foundFruit && foundFruit.userData.skillIndex === undefined) {
      foundFruit = foundFruit.parent
    }
  }
  for (let i = 0; i < fruits.length; i++) {
    const f = fruits[i]
    if (f === foundFruit) {
      canvasRef.value!.style.cursor = 'pointer'
      if (!f.userData.clicked) {
        f.scale.setScalar((f.userData.baseScale || 1) * 1.25)
      }
    } else {
      if (!f.userData.clicked) {
        f.scale.setScalar(f.userData.baseScale || 1)
      }
    }
  }
  if (!foundFruit && !selectedFruit.value) {
    canvasRef.value.style.cursor = 'grab'
  }
}

function createClickRipple(pos: THREE.Vector3, color: THREE.Color, scene: THREE.Scene) {
  const rippleGeom = new THREE.RingGeometry(0.5, 1, 32)
  const rippleMat = new THREE.MeshBasicMaterial({
    color: color,
    transparent: true,
    opacity: 0.7,
    side: THREE.DoubleSide,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  })
  const ripple = new THREE.Mesh(rippleGeom, rippleMat)
  ripple.position.copy(pos)
  ripple.lookAt(sceneCtx.camera.position)
  scene.add(ripple)
  ripples.push({ mesh: ripple, startTime: time, color })
}

function createParticleBurst(pos: THREE.Vector3, color: THREE.Color, scene: THREE.Scene) {
  const count = 12
  for (let i = 0; i < count; i++) {
    const pGeom = new THREE.SphereGeometry(0.15 + Math.random() * 0.2, 4, 4)
    const isAccent = Math.random() > 0.6
    const pMat = new THREE.MeshBasicMaterial({
      color: isAccent ? COLOR_CENTER : color,
      transparent: true,
      opacity: 1,
      blending: THREE.AdditiveBlending
    })
    const p = new THREE.Mesh(pGeom, pMat)
    p.position.copy(pos)
    const velocity = new THREE.Vector3(
      (Math.random() - 0.5) * 5,
      Math.random() * 4 + 1.5,
      (Math.random() - 0.5) * 5
    )
    scene.add(p)
    particles.push({ mesh: p, velocity, startTime: time })
  }
}

function closePanel() {
  panelVisible.value = false
  setTimeout(() => {
    selectedFruit.value = null
    for (let i = 0; i < fruits.length; i++) {
      const f = fruits[i]
      f.userData.clicked = false
      f.scale.setScalar(f.userData.baseScale || 1)
    }
  }, 300)
}

function resetView() {
  if (!sceneCtx) return
  const { camera, controls, initialState } = sceneCtx
  // Smoothly animate back to default
  const startPos = camera.position.clone()
  const startTarget = controls.target.clone()
  const duration = 800
  const startTime = performance.now()

  function animateReset() {
    const elapsed = performance.now() - startTime
    const t = Math.min(elapsed / duration, 1)
    // Ease out cubic
    const ease = 1 - Math.pow(1 - t, 3)
    camera.position.lerpVectors(startPos, initialState.cameraPos, ease)
    controls.target.lerpVectors(startTarget, initialState.target, ease)
    controls.update()
    if (t < 1) {
      requestAnimationFrame(animateReset)
    }
  }
  animateReset()
}

function updateConnectorPosition(camera: THREE.Camera) {
  if (!selectedFruit.value || !connectorSvg.value || !canvasRef.value) return
  const fruit = fruits.find(f => f.userData.skill?.name === selectedFruit.value.name)
  if (!fruit) return
  const canvasRect = canvasRef.value.getBoundingClientRect()
  const screenPos = fruit.position.clone().project(camera)
  const x = (screenPos.x + 1) / 2 * canvasRect.width
  const y = (-screenPos.y + 1) / 2 * canvasRect.height
  const panel = document.querySelector('.fruit-info-panel') as HTMLElement
  if (!panel) return
  const panelRect = panel.getBoundingClientRect()
  const startX = x
  const startY = y
  const endX = canvasRect.width - panelRect.width / 2
  const endY = panelRect.top - canvasRect.top + 80
  const svg = connectorSvg.value
  svg.innerHTML = ''
  svg.setAttribute('width', String(canvasRect.width))
  svg.setAttribute('height', String(canvasRect.height))
  const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
  const midX = (startX + endX) / 2
  const d = `M ${startX} ${startY} C ${midX} ${startY}, ${midX} ${endY}, ${endX} ${endY}`
  path.setAttribute('d', d)
  path.setAttribute('stroke', selectedFruit.value.color)
  path.setAttribute('stroke-width', '2')
  path.setAttribute('fill', 'none')
  path.setAttribute('stroke-dasharray', '8,4')
  path.style.animation = 'dash 1s linear infinite'
  svg.appendChild(path)
  const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
  circle.setAttribute('cx', String(startX))
  circle.setAttribute('cy', String(startY))
  circle.setAttribute('r', '8')
  circle.setAttribute('fill', selectedFruit.value.color)
  circle.style.opacity = '0.6'
  svg.appendChild(circle)
}

function onResize(camera: THREE.Camera, r: THREE.WebGLRenderer) {
  if (!canvasRef.value || !containerRef.value) return
  const w = containerRef.value.clientWidth
  const h = containerRef.value.clientHeight
  camera.aspect = w / h
  camera.updateProjectionMatrix()
  r.setSize(w, h)
  r.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  if (sceneCtx && sceneCtx.composer) {
    sceneCtx.composer.setSize(w, h)
  }
  if (labelRenderer) {
    labelRenderer.setSize(w, h)
  }
}

function animate(composer: any, controls: any, camera: THREE.Camera) {
  animFrameId = requestAnimationFrame(() => animate(composer, controls, camera))
  time += 0.016

  // Animate skill nodes — only breathing, no continuous rotation
  for (let i = 0; i < fruits.length; i++) {
    const f = fruits[i]
    const breathe = 1 + Math.sin(time * 1.5 + i * 0.7) * 0.06
    const floatY = Math.sin(time * 0.6 + i * 0.5) * 0.1
    f.position.y = (f.userData.originalY || f.position.y) + floatY

    if (f.userData.clicked) {
      const elapsed = time - f.userData.clickTime
      if (elapsed < 0.5) {
        const t = elapsed / 0.5
        f.scale.setScalar((f.userData.baseScale || 1) * 1.5 - t * (f.userData.baseScale || 1) * 0.2)
      } else {
        f.scale.setScalar((f.userData.baseScale || 1) * 1.25 * breathe)
      }
    } else {
      f.scale.setScalar((f.userData.baseScale || 1) * breathe)
    }

    // Update glow shader time
    for (let c = 0; c < f.children.length; c++) {
      const child = f.children[c] as THREE.Mesh
      if (child.material && (child.material as THREE.ShaderMaterial).uniforms) {
        ;(child.material as THREE.ShaderMaterial).uniforms.time.value = time
      }
    }
  }

  // Decorative flowers — very subtle drift, no rotation
  if (flowers) {
    flowers.rotation.y = Math.sin(time * 0.15) * 0.01
  }

  // Update environment (grass, clouds)
  if (sceneCtx && sceneCtx.environment) {
    sceneCtx.environment.update(time)
  }

  // Ripples
  ripples = ripples.filter(r => {
    const elapsed = time - r.startTime
    if (elapsed > 1.2) {
      sceneCtx.scene.remove(r.mesh)
      r.mesh.geometry.dispose()
      ;(r.mesh.material as THREE.Material).dispose()
      return false
    }
    const scale = 1 + elapsed * 7
    r.mesh.scale.setScalar(scale)
    ;(r.mesh.material as THREE.MeshBasicMaterial).opacity = 0.7 * (1 - elapsed / 1.2)
    r.mesh.lookAt(sceneCtx.camera.position)
    return true
  })

  // Particles
  particles = particles.filter(p => {
    const elapsed = time - p.startTime
    if (elapsed > 1.5) {
      sceneCtx.scene.remove(p.mesh)
      p.mesh.geometry.dispose()
      ;(p.mesh.material as THREE.Material).dispose()
      return false
    }
    p.velocity.y -= 8 * 0.016
    p.mesh.position.add(p.velocity.clone().multiplyScalar(0.016))
    ;(p.mesh.material as THREE.MeshBasicMaterial).opacity = 1 - elapsed / 1.5
    return true
  })

  if (selectedFruit.value && panelVisible.value) {
    updateConnectorPosition(sceneCtx.camera)
  }

  controls.update()
  composer.render()
  if (labelRenderer) {
    labelRenderer.render(sceneCtx.scene, camera)
  }
}

function resetCamera() {
  resetView()
}

// Expose reset for parent components
defineExpose({ resetCamera })

onMounted(() => {
  setTimeout(initTree, 100)
})

onUnmounted(() => {
  cancelAnimationFrame(animFrameId)
  if (canvasRef.value) {
    canvasRef.value.removeEventListener('click', () => {})
    canvasRef.value.removeEventListener('mousemove', () => {})
  }
  window.removeEventListener('resize', () => {})
  if (renderer) {
    renderer.dispose()
  }
  for (const r of ripples) {
    if (sceneCtx) sceneCtx.scene.remove(r.mesh)
    r.mesh.geometry.dispose()
    ;(r.mesh.material as THREE.Material).dispose()
  }
  for (const p of particles) {
    if (sceneCtx) sceneCtx.scene.remove(p.mesh)
    p.mesh.geometry.dispose()
    ;(p.mesh.material as THREE.Material).dispose()
  }
})
</script>

<style scoped>
.evolution-tree-container {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  border-radius: 16px;
  background: radial-gradient(ellipse at 50% 80%, rgba(10, 40, 80, 0.3) 0%, transparent 70%);
}

.tree-canvas {
  width: 100%;
  height: 100%;
  display: block;
  cursor: grab;
  position: relative;
  z-index: 1;
  opacity: 0;
  transition: opacity 0.6s ease;
}

.tree-canvas.canvas-ready {
  opacity: 1;
}

.tree-canvas:active {
  cursor: grabbing;
}

/* ─── Loading overlay ─────────────────────────────────────────────── */
.tree-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  z-index: 50;
  background: rgba(7, 17, 35, 0.6);
  backdrop-filter: blur(4px);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(78, 216, 255, 0.2);
  border-top-color: #4ed8ff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: rgba(78, 216, 255, 0.8);
  font-size: 14px;
  letter-spacing: 1px;
}

/* ─── Toolbar ─────────────────────────────────────────────────────── */
.tree-toolbar {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 50;
  display: flex;
  gap: 8px;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 10px;
  border: 1px solid rgba(78, 216, 255, 0.3);
  background: rgba(7, 26, 53, 0.7);
  backdrop-filter: blur(12px);
  color: #4ed8ff;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
}

.toolbar-btn:hover {
  background: rgba(78, 216, 255, 0.15);
  border-color: rgba(78, 216, 255, 0.6);
  box-shadow: 0 0 16px rgba(78, 216, 255, 0.2);
  transform: translateY(-1px);
}

/* ─── Hint bar ────────────────────────────────────────────────────── */
.tree-hint {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(7, 26, 53, 0.7);
  backdrop-filter: blur(8px);
  padding: 8px 18px;
  border-radius: 24px;
  color: rgba(255, 255, 255, 0.75);
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(78, 216, 255, 0.25);
  animation: hintPulse 2.5s ease-in-out infinite;
  z-index: 10;
}

@keyframes hintPulse {
  0%, 100% { opacity: 0.65; transform: translateX(-50%) translateY(0); }
  50% { opacity: 1; transform: translateX(-50%) translateY(-3px); }
}

.hint-icon {
  font-size: 14px;
  color: #4ed8ff;
}

/* ─── Info panel ──────────────────────────────────────────────────── */
.fruit-info-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 340px;
  max-height: calc(100% - 40px);
  overflow-y: auto;
  background: rgba(7, 22, 50, 0.72);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(78, 216, 255, 0.2);
  padding: 20px;
  color: white;
  transform: translateX(380px);
  opacity: 0;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 8px 32px rgba(0, 50, 120, 0.3), 0 0 60px rgba(78, 216, 255, 0.08);
  z-index: 100;
}

.fruit-info-panel.visible {
  transform: translateX(0);
  opacity: 1;
}

.panel-close {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.7);
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.panel-close:hover {
  background: rgba(78, 216, 255, 0.3);
  color: #4ed8ff;
  transform: rotate(90deg);
}

.panel-header {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(78, 216, 255, 0.12);
}

.skill-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: bold;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3), 0 0 20px rgba(78, 216, 255, 0.2);
}

.skill-title-wrap {
  flex: 1;
}

.skill-title {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
}

.skill-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.heat-tag.hot {
  background: linear-gradient(135deg, rgba(78, 216, 255, 0.3), rgba(61, 134, 255, 0.3));
  color: #4ed8ff;
  border: 1px solid rgba(78, 216, 255, 0.3);
}

.heat-tag.warm {
  background: rgba(61, 134, 255, 0.2);
  color: #7eb8ff;
  border: 1px solid rgba(61, 134, 255, 0.25);
}

.heat-tag.rising {
  background: rgba(126, 184, 255, 0.15);
  color: #9ec8ff;
  border: 1px solid rgba(126, 184, 255, 0.2);
}

.heat-tag.cool {
  background: rgba(90, 138, 170, 0.2);
  color: #7aa0bb;
  border: 1px solid rgba(90, 138, 170, 0.25);
}

.trend-tag {
  background: rgba(78, 216, 255, 0.15);
  color: #4ed8ff;
  border: 1px solid rgba(78, 216, 255, 0.2);
}

.info-section {
  margin-bottom: 16px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.info-label {
  color: rgba(255, 255, 255, 0.55);
  font-size: 13px;
}

.info-value {
  font-weight: 600;
  font-size: 14px;
}

.info-value.salary {
  color: #5ce1ff;
  font-size: 16px;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
  display: flex;
  align-items: center;
  gap: 6px;
}

.section-title::before {
  content: '';
  width: 3px;
  height: 14px;
  background: linear-gradient(to bottom, #4ed8ff, #3d86ff);
  border-radius: 2px;
}

.course-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.course-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 10px;
  border: 1px solid rgba(78, 216, 255, 0.1);
  transition: all 0.2s;
}

.course-item:hover {
  background: rgba(78, 216, 255, 0.06);
  border-color: rgba(78, 216, 255, 0.2);
}

.course-icon {
  font-size: 18px;
}

.course-info {
  flex: 1;
  min-width: 0;
}

.course-name {
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.course-meta {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.45);
  margin-top: 2px;
}

.course-btn {
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid rgba(78, 216, 255, 0.4);
  background: linear-gradient(135deg, rgba(78, 216, 255, 0.2), rgba(61, 134, 255, 0.2));
  color: #4ed8ff;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.course-btn:hover {
  background: linear-gradient(135deg, rgba(78, 216, 255, 0.35), rgba(61, 134, 255, 0.35));
  box-shadow: 0 4px 12px rgba(78, 216, 255, 0.25);
  transform: scale(1.03);
}

.job-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.job-tag {
  padding: 5px 11px;
  background: rgba(78, 216, 255, 0.1);
  border: 1px solid rgba(78, 216, 255, 0.2);
  border-radius: 8px;
  font-size: 12px;
  color: #7ec8f0;
  cursor: pointer;
  transition: all 0.2s;
}

.job-tag:hover {
  background: rgba(78, 216, 255, 0.2);
  border-color: rgba(78, 216, 255, 0.4);
  transform: translateY(-1px);
}

.panel-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(78, 216, 255, 0.12);
}

.action-btn {
  flex: 1;
  padding: 10px;
  border-radius: 10px;
  border: none;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn.primary {
  background: linear-gradient(135deg, #4ed8ff, #3d86ff);
  color: #071124;
}

.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(78, 216, 255, 0.35);
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(78, 216, 255, 0.2);
}

.action-btn.secondary:hover {
  background: rgba(78, 216, 255, 0.1);
  border-color: rgba(78, 216, 255, 0.35);
}

.connector-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 99;
}

@keyframes dash {
  to { stroke-dashoffset: -24; }
}

@media (max-width: 768px) {
  .fruit-info-panel {
    width: calc(100% - 40px);
    right: 20px;
    top: auto;
    bottom: 20px;
    max-height: 50vh;
    transform: translateY(120%);
  }
  .fruit-info-panel.visible {
    transform: translateY(0);
  }
  .tree-toolbar {
    top: 10px;
    left: 10px;
  }
  .toolbar-btn span {
    display: none;
  }
}
</style>

<style>
.skill-label {
  pointer-events: none;
  user-select: none;
}
.skill-label .label-text {
  display: inline-block;
  padding: 3px 10px;
  background: rgba(7, 22, 50, 0.85);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(78, 216, 255, 0.4);
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  text-shadow: 0 1px 4px rgba(0,0,0,0.6);
  box-shadow: 0 2px 10px rgba(0,0,0,0.3);
  opacity: 0.9;
  transition: opacity 0.2s, transform 0.2s;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
</style>

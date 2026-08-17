<template>
  <div ref="containerRef" class="evolution-tree-container">
    <canvas ref="canvasRef" class="tree-canvas"></canvas>
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
    <div class="tree-hint" v-if="!selectedFruit">
      <span class="hint-icon">🌸</span> 点击树上的技能花朵查看详情
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
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
        return hs.map((s: any) => ({
          name: s?.name || '未知技能',
          heat: Number(s?.heat) || 10,
          trend: (s?.trend as 'up'|'down'|'stable') || 'stable',
          category: s?.category || '技能',
          jobs: s?.jobs,
          salary: s?.salary,
          relatedJobs: s?.relatedJobs,
          courses: s?.courses
        }))
      }
      return defaultSkills
    }
    return defaultSkills
  } catch (e) {
    console.error('getSkills error:', e)
    return defaultSkills
  }
}

function createFlowerGeometry(flowerColor: THREE.Color): THREE.Group {
  const flowerGroup = new THREE.Group()
  const petalMat = new THREE.MeshStandardMaterial({
    color: flowerColor,
    roughness: 0.35,
    metalness: 0.08,
    transparent: true,
    opacity: 0.92,
    emissive: flowerColor,
    emissiveIntensity: 0.25
  })
  for (let i = 0; i < 5; i++) {
    const petalGeom = new THREE.SphereGeometry(1, 8, 6)
    const petal = new THREE.Mesh(petalGeom, petalMat.clone())
    const angle = (i / 5) * Math.PI * 2
    petal.position.set(Math.cos(angle) * 0.7, Math.sin(i * 0.3) * 0.08, Math.sin(angle) * 0.7)
    petal.scale.set(0.7, 0.2, 0.5)
    petal.rotation.z = angle
    petal.rotation.x = -0.25
    flowerGroup.add(petal)
  }
  const centerGeom = new THREE.SphereGeometry(0.4, 8, 6)
  const centerMat = new THREE.MeshStandardMaterial({
    color: 0xffd700,
    roughness: 0.35,
    metalness: 0.2,
    emissive: 0xffaa00,
    emissiveIntensity: 0.3
  })
  const center = new THREE.Mesh(centerGeom, centerMat)
  center.position.set(0, 0.15, 0)
  flowerGroup.add(center)
  return flowerGroup
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
        float intensity = pow(0.8 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 3.0);
        float pulse = 0.8 + 0.2 * sin(time * 2.0);
        gl_FragColor = vec4(glowColor, intensity * pulse * 0.35);
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
  const layers = [
    { yRange: [20, 32], radiusX: 22, radiusZ: 18, count: Math.ceil(count * 0.3) },
    { yRange: [32, 46], radiusX: 30, radiusZ: 25, count: Math.ceil(count * 0.5) },
    { yRange: [46, 58], radiusX: 16, radiusZ: 13, count: Math.ceil(count * 0.2) }
  ]
  layers.forEach(layer => {
    for (let i = 0; i < layer.count && positions.length < count; i++) {
      const angle = (i / layer.count) * Math.PI * 2 + (Math.random() - 0.5) * 0.6
      const rx = layer.radiusX * (0.85 + Math.random() * 0.25)
      const rz = layer.radiusZ * (0.85 + Math.random() * 0.25)
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
      y = 15 + Math.random() * 15
      rx = 18 + Math.random() * 15
      rz = 15 + Math.random() * 12
    } else if (layer < 0.55) {
      y = 28 + Math.random() * 22
      rx = 25 + Math.random() * 22
      rz = 22 + Math.random() * 18
    } else if (layer < 0.85) {
      y = 42 + Math.random() * 20
      rx = 18 + Math.random() * 20
      rz = 15 + Math.random() * 16
    } else {
      y = 55 + Math.random() * 15
      rx = 8 + Math.random() * 12
      rz = 6 + Math.random() * 10
    }
    const angle = Math.random() * Math.PI * 2
    const distFactor = 0.55 + Math.random() * 0.55
    positions.push([Math.cos(angle) * rx * distFactor, y, Math.sin(angle) * rz * distFactor])
  }
  return positions
}

function getHeatColor(heat: number): THREE.Color {
  if (heat >= 18) return new THREE.Color(0xff69b4)
  if (heat >= 14) return new THREE.Color(0xff1493)
  if (heat >= 11) return new THREE.Color(0xffb6c1)
  return new THREE.Color(0xffe4e1)
}

function getHeatLevel(heat: number): string {
  if (heat >= 18) return 'hot'
  if (heat >= 14) return 'warm'
  if (heat >= 11) return 'rising'
  return 'cool'
}

async function initTree() {
  if (!canvasRef.value || !containerRef.value) return

  // Create renderer
  renderer = new THREE.WebGLRenderer({
    canvas: canvasRef.value,
    antialias: true,
    alpha: true,
    powerPreference: 'high-performance'
  })

  // Create CSS2D renderer for labels
  labelRenderer = new CSS2DRenderer()
  labelRenderer.setSize(containerRef.value.clientWidth, containerRef.value.clientHeight)
  labelRenderer.domElement.style.position = 'absolute'
  labelRenderer.domElement.style.top = '0'
  labelRenderer.domElement.style.left = '0'
  labelRenderer.domElement.style.pointerEvents = 'none'
  labelRenderer.domElement.style.zIndex = '2'
  containerRef.value.appendChild(labelRenderer.domElement)

  // Create scene using ez-tree's createScene
  sceneCtx = await createScene(canvasRef.value, renderer)
  const { scene, camera, controls, tree, composer } = sceneCtx

  // Add decorative flowers to the main tree
  addDecorativeFlowers(tree)

  // Add skill fruits (glowing pink flowers) to the main tree
  addSkillFruits(tree, camera)

  // Setup interaction
  setupInteraction(camera, scene, controls)

  // Start animation
  animate(composer, controls, camera)
}

function addDecorativeFlowers(tree: THREE.Object3D) {
  const flowerCount = 300
  const flowerColors = [0xffb6c1, 0xffc0cb, 0xffe4e1, 0xff91a4, 0xffd1dc]
  const flowerGeom = new THREE.SphereGeometry(0.8, 6, 4)
  flowerGeom.scale(1, 0.3, 1)

  const flowerMat = new THREE.MeshStandardMaterial({
    color: 0xffb6c1,
    roughness: 0.6,
    metalness: 0.05,
    transparent: true,
    opacity: 0.85,
    emissive: 0xff69b4,
    emissiveIntensity: 0.08
  })
  flowers = new THREE.InstancedMesh(flowerGeom, flowerMat, flowerCount)
  const dummy = new THREE.Object3D()
  const color = new THREE.Color()
  const flowerPositions = getFlowerPositions(flowerCount)
  flowerPositions.forEach((pos, i) => {
    dummy.position.set(pos[0], pos[1], pos[2])
    const s = 0.5 + Math.random() * 0.8
    dummy.scale.set(s, s * 0.35, s)
    dummy.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI * 2, 0)
    dummy.updateMatrix()
    flowers!.setMatrixAt(i, dummy.matrix)
    color.setHex(flowerColors[Math.floor(Math.random() * flowerColors.length)])
    flowers!.setColorAt(i, color)
  })
  flowers.instanceMatrix.needsUpdate = true
  if (flowers.instanceColor) flowers.instanceColor.needsUpdate = true
  tree.add(flowers)
}

function addSkillFruits(tree: THREE.Object3D, camera: THREE.Camera) {
  // Start with default skills
  let skillsToUse: Skill[] = defaultSkills
  
  // Try to use props.hotSkills if available and valid
  try {
    const hs = props.hotSkills as any
    if (hs && typeof hs.length === 'number' && hs.length > 0) {
      const mapped: Skill[] = []
      for (let idx = 0; idx < hs.length; idx++) {
        const s = hs[idx]
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
      if (mapped.length > 0) {
        skillsToUse = mapped
      }
    }
  } catch (e) {
    console.error('Error processing skills, using defaults:', e)
  }
  
  const positions = getFruitPositions(skillsToUse.length)
  
  for (let i = 0; i < skillsToUse.length; i++) {
    const skill = skillsToUse[i]
    const color = getHeatColor(skill.heat)
    const fruitGroup = new THREE.Group()

    const flowerTemplate = createFlowerGeometry(color)
    const baseScale = 0.7 + Math.random() * 0.3
    flowerTemplate.scale.setScalar(baseScale)
    fruitGroup.add(flowerTemplate)

    const glowGeom = new THREE.SphereGeometry(1.8, 12, 12)
    const glowMat = createGlowMaterial(color)
    const glow = new THREE.Mesh(glowGeom, glowMat)
    fruitGroup.add(glow)

    // Larger invisible hit area for easier clicking
    const hitGeom = new THREE.SphereGeometry(3.5, 12, 8)
    const hitMat = new THREE.MeshBasicMaterial({
      transparent: true,
      opacity: 0,
      depthWrite: false,
      side: THREE.DoubleSide
    })
    const hitArea = new THREE.Mesh(hitGeom, hitMat)
    hitArea.userData.isHitArea = true
    fruitGroup.add(hitArea)

    const light = new THREE.PointLight(color, 0.5, 12)
    fruitGroup.add(light)

    fruitGroup.position.set(positions[i][0], positions[i][1], positions[i][2])
    fruitGroup.userData.skillIndex = i
    fruitGroup.userData.baseScale = baseScale
    fruitGroup.userData.originalY = positions[i][1]
    fruitGroup.userData.color = color
    fruitGroup.userData.skill = skill

    // Add skill name label
    const labelDiv = document.createElement('div')
    labelDiv.className = 'skill-label'
    labelDiv.innerHTML = `<span class="label-text" style="border-color: #${color.getHexString()}">${skill.name}</span>`
    const label = new CSS2DObject(labelDiv)
    label.position.set(0, 3.5, 0)
    fruitGroup.add(label)

    tree.add(fruitGroup)
    fruits.push(fruitGroup)
  }

  // Expose test function globally
  (window as any).__selectSkillFruit = (index: number) => {
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
  // If clicking on a label, let the event pass through CSS2DRenderer layer
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
  fruits.forEach(f => {
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
  })
  if (!foundFruit && !selectedFruit.value) {
    canvasRef.value.style.cursor = 'grab'
  }
}

function createClickRipple(pos: THREE.Vector3, color: THREE.Color, scene: THREE.Scene) {
  const rippleGeom = new THREE.RingGeometry(0.5, 1, 32)
  const rippleMat = new THREE.MeshBasicMaterial({
    color: color,
    transparent: true,
    opacity: 0.8,
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
  for (let i = 0; i < 20; i++) {
    const pGeom = new THREE.SphereGeometry(0.2 + Math.random() * 0.3, 4, 4)
    const pMat = new THREE.MeshBasicMaterial({
      color: Math.random() > 0.5 ? color : new THREE.Color(0xffd700),
      transparent: true,
      opacity: 1,
      blending: THREE.AdditiveBlending
    })
    const p = new THREE.Mesh(pGeom, pMat)
    p.position.copy(pos)
    const velocity = new THREE.Vector3(
      (Math.random() - 0.5) * 6,
      Math.random() * 5 + 2,
      (Math.random() - 0.5) * 6
    )
    scene.add(p)
    particles.push({ mesh: p, velocity, startTime: time })
  }
}

function closePanel() {
  panelVisible.value = false
  setTimeout(() => {
    selectedFruit.value = null
    fruits.forEach(f => {
      f.userData.clicked = false
      f.scale.setScalar(f.userData.baseScale || 1)
    })
  }, 300)
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

function onResize(camera: THREE.Camera, renderer: THREE.WebGLRenderer) {
  if (!canvasRef.value || !containerRef.value) return
  const w = containerRef.value.clientWidth
  const h = containerRef.value.clientHeight
  camera.aspect = w / h
  camera.updateProjectionMatrix()
  renderer.setSize(w, h)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
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

  // Animate skill flowers
  fruits.forEach((f, i) => {
    const breathe = 1 + Math.sin(time * 1.5 + i * 0.7) * 0.08
    const floatY = Math.sin(time * 0.8 + i * 0.5) * 0.15
    f.position.y = (f.userData.originalY || f.position.y) + floatY
    f.rotation.y += 0.008

    if (f.userData.clicked) {
      const elapsed = time - f.userData.clickTime
      if (elapsed < 0.5) {
        const t = elapsed / 0.5
        f.scale.setScalar((f.userData.baseScale || 1) * 1.5 - t * (f.userData.baseScale || 1) * 0.25)
      } else {
        f.scale.setScalar((f.userData.baseScale || 1) * 1.25 * breathe)
      }
    } else {
      f.scale.setScalar((f.userData.baseScale || 1) * breathe)
    }

    // Update glow shader time
    f.children.forEach(child => {
      const mesh = child as THREE.Mesh
      if (mesh.material && (mesh.material as THREE.ShaderMaterial).uniforms) {
        ;(mesh.material as THREE.ShaderMaterial).uniforms.time.value = time
      }
    })

    // Make labels face camera by rotating them to counter fruit rotation
    f.children.forEach(child => {
      if (child instanceof CSS2DObject) {
        // Labels auto-face camera in CSS2DRenderer
      }
    })
  })

  // Decorative flowers gentle sway
  if (flowers) {
    flowers.rotation.y = Math.sin(time * 0.2) * 0.02
  }

  // Update environment (grass, clouds)
  if (sceneCtx && sceneCtx.environment) {
    sceneCtx.environment.update(time)
  }

  // Ripples
  ripples = ripples.filter(r => {
    const elapsed = time - r.startTime
    if (elapsed > 1.5) {
      sceneCtx.scene.remove(r.mesh)
      r.mesh.geometry.dispose()
      ;(r.mesh.material as THREE.Material).dispose()
      return false
    }
    const scale = 1 + elapsed * 6
    r.mesh.scale.setScalar(scale)
    ;(r.mesh.material as THREE.MeshBasicMaterial).opacity = 0.8 * (1 - elapsed / 1.5)
    r.mesh.lookAt(sceneCtx.camera.position)
    return true
  })

  // Particles
  particles = particles.filter(p => {
    const elapsed = time - p.startTime
    if (elapsed > 2) {
      sceneCtx.scene.remove(p.mesh)
      p.mesh.geometry.dispose()
      ;(p.mesh.material as THREE.Material).dispose()
      return false
    }
    p.velocity.y -= 10 * 0.016
    p.mesh.position.add(p.velocity.clone().multiplyScalar(0.016))
    ;(p.mesh.material as THREE.MeshBasicMaterial).opacity = 1 - elapsed / 2
    p.mesh.rotation.x += 0.1
    p.mesh.rotation.y += 0.15
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

onMounted(() => {
  setTimeout(initTree, 200)
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
  ripples.forEach(r => {
    if (sceneCtx) sceneCtx.scene.remove(r.mesh)
    r.mesh.geometry.dispose()
    ;(r.mesh.material as THREE.Material).dispose()
  })
  particles.forEach(p => {
    if (sceneCtx) sceneCtx.scene.remove(p.mesh)
    p.mesh.geometry.dispose()
    ;(p.mesh.material as THREE.Material).dispose()
  })
})
</script>

<style scoped>
.evolution-tree-container {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  border-radius: 16px;
}

.tree-canvas {
  width: 100%;
  height: 100%;
  display: block;
  cursor: grab;
  position: relative;
  z-index: 1;
}

.tree-canvas:active {
  cursor: grabbing;
}

.tree-hint {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(7, 26, 53, 0.7);
  backdrop-filter: blur(8px);
  padding: 10px 20px;
  border-radius: 24px;
  color: rgba(255, 255, 255, 0.85);
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(255, 105, 180, 0.3);
  animation: hintPulse 2s ease-in-out infinite;
}

@keyframes hintPulse {
  0%, 100% { opacity: 0.7; transform: translateX(-50%) translateY(0); }
  50% { opacity: 1; transform: translateX(-50%) translateY(-4px); }
}

.hint-icon {
  font-size: 18px;
}

.fruit-info-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 340px;
  max-height: calc(100% - 40px);
  overflow-y: auto;
  background: rgba(10, 36, 99, 0.65);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 182, 193, 0.3);
  padding: 20px;
  color: white;
  transform: translateX(380px);
  opacity: 0;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 8px 32px rgba(255, 105, 180, 0.2), 0 0 60px rgba(255, 182, 193, 0.1);
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
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.panel-close:hover {
  background: rgba(255, 105, 180, 0.4);
  transform: rotate(90deg);
}

.panel-header {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 182, 193, 0.15);
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
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
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
  background: linear-gradient(135deg, rgba(255, 105, 180, 0.4), rgba(255, 20, 147, 0.4));
  color: #ffb6c1;
}

.heat-tag.warm {
  background: rgba(255, 20, 147, 0.3);
  color: #ff69b4;
}

.heat-tag.rising {
  background: rgba(255, 182, 193, 0.2);
  color: #ffc0cb;
}

.heat-tag.cool {
  background: rgba(200, 200, 200, 0.2);
  color: #ccc;
}

.trend-tag {
  background: rgba(78, 216, 255, 0.2);
  color: #4ed8ff;
}

.info-section {
  margin-bottom: 16px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
}

.info-label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
}

.info-value {
  font-weight: 600;
  font-size: 14px;
}

.info-value.salary {
  color: #ffd700;
  font-size: 16px;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  gap: 6px;
}

.section-title::before {
  content: '';
  width: 3px;
  height: 14px;
  background: linear-gradient(to bottom, #ff69b4, #ffb6c1);
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
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  border: 1px solid rgba(255, 182, 193, 0.1);
}

.course-icon {
  font-size: 20px;
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
  color: rgba(255, 255, 255, 0.5);
  margin-top: 2px;
}

.course-btn {
  padding: 6px 12px;
  border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, #ff69b4, #ff1493);
  color: white;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.course-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(255, 105, 180, 0.4);
}

.job-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.job-tag {
  padding: 6px 12px;
  background: rgba(78, 216, 255, 0.15);
  border: 1px solid rgba(78, 216, 255, 0.3);
  border-radius: 8px;
  font-size: 12px;
  color: #4ed8ff;
  cursor: pointer;
  transition: all 0.2s;
}

.job-tag:hover {
  background: rgba(78, 216, 255, 0.3);
  transform: translateY(-2px);
}

.panel-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 182, 193, 0.15);
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
  background: linear-gradient(135deg, #ff69b4, #ff1493);
  color: white;
}

.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 105, 180, 0.4);
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.action-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.2);
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
  background: rgba(7, 26, 53, 0.85);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(78, 216, 255, 0.5);
  border-radius: 12px;
  color: #fff;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  text-shadow: 0 1px 3px rgba(0,0,0,0.5);
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  opacity: 0.9;
  transition: opacity 0.2s, transform 0.2s;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
</style>

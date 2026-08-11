<template>
  <div class="skill-tree-container" ref="containerRef">
    <canvas ref="canvasRef" class="skill-tree-canvas"></canvas>
    <div class="tree-legend">
      <div class="legend-item">
        <span class="dot new"></span>
        <span>新增嫩芽</span>
      </div>
      <div class="legend-item">
        <span class="dot dead"></span>
        <span>淘汰枯叶</span>
      </div>
      <div class="legend-item">
        <span class="dot core"></span>
        <span>核心枝干</span>
      </div>
    </div>
    <div class="tree-version-label">
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

interface SkillTreeProps {
  addedSkills?: string[]
  removedSkills?: string[]
  coreSkills?: string[]
  fromVersion?: string
  toVersion?: string
}

const props = withDefaults(defineProps<SkillTreeProps>(), {
  addedSkills: () => ['Python', 'FastAPI', 'RAG', 'LLM微调'],
  removedSkills: () => ['Flash', 'jQuery'],
  coreSkills: () => ['JavaScript', 'Vue', 'React', 'Node.js', 'TypeScript'],
  fromVersion: 'v1.1',
  toVersion: 'v1.2'
})

const containerRef = ref<HTMLDivElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)

let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let renderer: THREE.WebGLRenderer | null = null
let tree: Tree | null = null
let sprouts: THREE.Mesh[] = []
let deadLeaves: THREE.Mesh[] = []
let frameId = 0
let time = 0

function initTree() {
  if (!canvasRef.value || !containerRef.value) return

  try {
    const w = containerRef.value.clientWidth || 600
    const h = containerRef.value.clientHeight || 400

    scene = new THREE.Scene()
    scene.background = new THREE.Color(0x041022)
    camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 1000)
    camera.position.set(0, 7, 28)
    camera.lookAt(0, 5, 0)

    renderer = new THREE.WebGLRenderer({
      canvas: canvasRef.value,
      antialias: true
    })
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5))
    renderer.setSize(w, h)

    scene.add(new THREE.AmbientLight(0xffffff, 1.4))
    const sun = new THREE.DirectionalLight(0xffffee, 1.1)
    sun.position.set(8, 18, 12)
    scene.add(sun)
    const fill = new THREE.DirectionalLight(0x88ddff, 0.4)
    fill.position.set(-5, 8, -5)
    scene.add(fill)

    const ground = new THREE.Mesh(
      new THREE.CircleGeometry(10, 32),
      new THREE.MeshLambertMaterial({ color: 0x113322 })
    )
    ground.rotation.x = -Math.PI / 2
    scene.add(ground)

    const coreRatio = Math.min(1, props.coreSkills.length / 10)
    const addRatio = Math.min(1, props.addedSkills.length / 6)
    const removeRatio = Math.min(1, props.removedSkills.length / 4)

    tree = new Tree()
    tree.options.seed = 42
    tree.options.bark.textured = false
    tree.options.bark.flatShading = true
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
    tree.generate()
    tree.scale.setScalar(1.1)
    tree.position.y = 0
    scene.add(tree)

    addSprouts(addRatio)
    addDeadLeaves(removeRatio)

    const animate = () => {
      frameId = requestAnimationFrame(animate)
      time += 0.016
      if (tree) {
        tree.rotation.y = Math.sin(time * 0.2) * 0.15
        tree.update(time * 0.8)
      }
      sprouts.forEach((s, i) => {
        const breathe = 1 + Math.sin(time * 2 + i * 0.7) * 0.25
        s.scale.setScalar(breathe)
        s.position.y += Math.sin(time * 1.5 + i) * 0.003
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
      renderer!.render(scene!, camera!)
    }
    animate()

    window.addEventListener('resize', handleResize)
  } catch (e) {
    console.error('Tree init failed:', e)
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
    scene.add(sprout)
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
  tree = null
  scene = null
  camera = null
  renderer = null
}

onMounted(() => {
  setTimeout(initTree, 200)
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

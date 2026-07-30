<template>
  <div class="page skill-graph-page">
    <PageHeader title="能力图谱" desc="查看岗位、技能、工具、证书、课程与行业场景之间的关联">
      <div class="toolbar">
        <el-radio-group v-model="viewMode" size="small" @change="renderGraph">
          <el-radio-button label="all">全图聚合</el-radio-button>
          <el-radio-button label="job">岗位中心</el-radio-button>
        </el-radio-group>
        <el-select
          v-if="viewMode === 'job'"
          v-model="targetJobId"
          filterable
          placeholder="选择目标岗位"
          style="width: 220px"
          @change="handleTargetJobChange"
        >
          <el-option v-for="job in jobNodes" :key="job.id" :label="job.label" :value="job.id" />
        </el-select>
        <el-autocomplete
          v-model="keyword"
          :fetch-suggestions="queryNodeSuggestions"
          :trigger-on-focus="false"
          value-key="label"
          clearable
          highlight-first-item
          placeholder="搜索岗位、技能或证书"
          style="width: 260px"
          @select="focusSearchResult"
          @clear="clearSearchFocus"
        >
          <template #default="{ item }">
            <div class="node-search-option">
              <span>{{ item.label }}</span>
              <small>{{ typeLabels[item.type] || item.type }}</small>
            </div>
          </template>
        </el-autocomplete>
        <el-select v-model="nodeType" clearable placeholder="全部节点" style="width: 144px" @change="renderGraph">
          <el-option v-for="item in types" :key="item" :label="typeLabels[item] || item" :value="item" />
        </el-select>
        <el-button @click="resetView">重置视角</el-button>
        <el-button type="primary" :loading="loading" @click="loadGraph">刷新图谱</el-button>
      </div>
    </PageHeader>

    <section class="graph-overview" aria-label="图谱统计">
      <div v-for="item in metricCards" :key="item.label" class="graph-overview__item">
        <strong>{{ item.value }}</strong><span>{{ item.label }}</span>
      </div>
      <div class="graph-overview__item graph-overview__hint">
        <span>拖拽旋转视角，滚轮缩放，点击节点查看证据与关系。图谱已自动过滤无关联孤立节点。</span>
      </div>
    </section>

    <div class="content-grid">
      <section class="panel span-8 graph-panel">
        <div v-loading="loading" class="graph-stage">
          <div ref="containerRef" class="graph-box">
            <div class="graph-orbit graph-orbit-a"></div>
            <div class="graph-orbit graph-orbit-b"></div>
            <div v-if="hovered" class="node-tooltip" :style="{ left: `${tooltip.x}px`, top: `${tooltip.y}px` }">
              <b>{{ hovered.label }}</b>
              <span>{{ typeLabels[hovered.type] || hovered.type }}</span>
            </div>
          </div>
          <div v-if="!loading && graphError" class="graph-message">
            <el-empty description="图谱暂时无法加载">
              <el-button type="primary" @click="loadGraph">重新加载</el-button>
            </el-empty>
          </div>
          <div v-else-if="!loading && !visibleData.nodes.length" class="graph-message">
            <el-empty description="没有符合条件的节点" />
          </div>
        </div>
      </section>

      <aside class="panel span-4 graph-detail-panel">
        <div class="detail-heading">
          <span>节点详情</span>
          <small>NODE DETAIL</small>
        </div>
        <el-empty v-if="!selected" description="点击图谱节点查看详情" />
        <template v-else>
          <div class="selected-node" :style="{ '--node-color': nodeColor(selected.type) }">
            <span class="selected-node__dot"></span>
            <div>
              <h3>{{ selected.label }}</h3>
              <el-tag effect="plain">{{ typeLabels[selected.type] || selected.type }}</el-tag>
            </div>
          </div>
          <div class="detail-block">
            <span>证据来源</span>
            <p>{{ selected.evidence || '该节点已进入图谱，暂未补充来源说明。' }}</p>
          </div>
          <div v-if="selected.category" class="detail-block">
            <span>分类</span>
            <p>{{ selected.category }}</p>
          </div>
          <div class="detail-block">
            <span>关联关系</span>
            <p>{{ relationshipCount(selected.id) }} 条</p>
          </div>
          <div class="detail-block">
            <span>相邻节点</span>
            <div class="neighbor-list">
              <el-tag v-for="item in adjacentNodes(selected.id)" :key="item.id" effect="plain">{{ item.label }}</el-tag>
            </div>
          </div>
        </template>

        <section class="detail-subsection">
          <div class="detail-heading compact">
            <span>社区分布</span>
            <small>COMMUNITY</small>
          </div>
          <div class="community-list">
            <button
              v-for="item in communities"
              :key="item.index"
              class="community-row"
              :class="{ active: activeCommunity === item.index }"
              @click="toggleCommunity(item.index)"
            >
              <span class="community-dot" :style="{ background: item.color }"></span>
              <span class="community-name">{{ item.name }}</span>
              <span class="community-count">{{ item.count }}</span>
              <span class="community-bar"><i :style="{ width: communityWidth(item.count), background: item.color }"></i></span>
            </button>
            <el-empty v-if="!communities.length" description="暂无社区数据" :image-size="62" />
          </div>
        </section>

        <section class="detail-subsection">
          <div class="detail-heading compact">
            <span>技能迁移路径</span>
            <small>CAREER PATH</small>
          </div>
          <el-select v-model="pathFrom" filterable placeholder="起始岗位" class="path-select">
            <el-option v-for="job in pathJobOptions" :key="job.value" :label="job.label" :value="job.value" />
          </el-select>
          <el-select v-model="pathTo" filterable placeholder="目标岗位" class="path-select">
            <el-option v-for="job in pathJobOptions" :key="job.value" :label="job.label" :value="job.value" />
          </el-select>
          <el-button type="primary" :disabled="!pathFrom || !pathTo" :loading="pathLoading" class="path-button" @click="findPath">
            分析迁移路径
          </el-button>
          <div v-if="pathResult" class="path-result">
            <template v-if="pathResult.found">
              <div class="path-chain">
                <template v-for="(node, index) in pathResult.path" :key="`${node.label}-${index}`">
                  <span class="path-node" :class="node.type">{{ node.label }}</span>
                  <span v-if="index < pathResult.path.length - 1" class="path-arrow">→</span>
                </template>
              </div>
              <div v-if="pathResult.shared?.length" class="path-shared">
                <span>可迁移能力</span>
                <el-tag v-for="skill in pathResult.shared.slice(0, 8)" :key="skill" size="small" effect="light">{{ skill }}</el-tag>
              </div>
            </template>
            <el-empty v-else description="两个岗位之间暂无连通路径" :image-size="62" />
          </div>
        </section>
      </aside>
    </div>

    <section class="graph-legend">
      <span v-for="item in types" :key="item" class="graph-legend__item">
        <i :style="{ background: nodeColor(item) }"></i>{{ typeLabels[item] || item }}
      </span>
    </section>
  </div>
</template>

<script setup lang="ts">
import * as THREE from 'three'
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { api } from '@/api/http'

type GraphNode = {
  id: string
  label: string
  type: string
  category?: string
  evidence?: string
}

type GraphEdge = {
  source: string
  target: string
  label?: string
  evidence?: string
}

type GraphCommunity = {
  index: number
  name: string
  color: string
  count: number
}

type PathResult = {
  found: boolean
  path: { label: string; type: string }[]
  shared: string[]
}

type PositionedNode = GraphNode & {
  position: THREE.Vector3
}

const containerRef = ref<HTMLDivElement>()
const raw = ref<{ nodes: GraphNode[]; edges: GraphEdge[] }>({ nodes: [], edges: [] })
const keyword = ref('')
const nodeType = ref('')
const viewMode = ref<'all' | 'job'>('all')
const targetJobId = ref('')
const selected = ref<GraphNode>()
const hovered = ref<GraphNode>()
const loading = ref(false)
const pathLoading = ref(false)
const graphError = ref(false)
const tooltip = reactive({ x: 0, y: 0 })
const graphStats = ref<Record<string, number | string>>({})
const communities = ref<GraphCommunity[]>([])
const activeCommunity = ref<number | null>(null)
const nodeCommunityMap = ref<Record<string, number>>({})
const pathFrom = ref<number | null>(null)
const pathTo = ref<number | null>(null)
const pathResult = ref<PathResult | null>(null)

let scene: THREE.Scene | undefined
let camera: THREE.PerspectiveCamera | undefined
let renderer: THREE.WebGLRenderer | undefined
let graphGroup: THREE.Group | undefined
let resizeObserver: ResizeObserver | undefined
let animationId = 0
let isDragging = false
let dragMoved = false
let lastPointer = { x: 0, y: 0 }
let raycaster: THREE.Raycaster | undefined
let pointer = new THREE.Vector2()
let nodeMeshes: THREE.Mesh[] = []
let nodeMeshById = new Map<string, THREE.Mesh>()
let nodeCompanions = new Map<string, THREE.Object3D[]>()
let nodeHomePositions = new Map<string, THREE.Vector3>()
let nodeTargetPositions = new Map<string, THREE.Vector3>()
let nodeFocusState = new Map<string, number>()
let edgeLineGeometry: THREE.BufferGeometry | undefined
let edgeRecords: Array<{ source: string; target: string }> = []
let focusedEdgeRecords: Array<{ source: string; target: string }> = []
let highlightLineGeometry: THREE.BufferGeometry | undefined
let highlightGlowGeometry: THREE.BufferGeometry | undefined
let highlightGroup: THREE.Group | undefined
let draggedMesh: THREE.Mesh | undefined
let pendingClickNode: GraphNode | undefined
let focusedNodeId = ''
let lastClickNodeId = ''
let lastClickAt = 0
let dragPlane = new THREE.Plane()
let dragOffset = new THREE.Vector3()
let dragWorldPoint = new THREE.Vector3()
let glowTexture: THREE.Texture | undefined
let labelTextureCache = new Map<string, THREE.CanvasTexture>()
let lastFrameTime = 0
const pressedKeys = new Set<string>()
const cameraPanVelocity = new THREE.Vector2()

const typeLabels: Record<string, string> = {
  Job: '岗位',
  Skill: '技能',
  Tool: '工具平台',
  Certificate: '证书',
  Responsibility: '职责',
  IndustryScenario: '行业场景',
  Course: '课程',
  Level: '能力等级'
}

const typeRadius: Record<string, number> = {
  Job: 150,
  Level: 230,
  Skill: 330,
  Tool: 430,
  Certificate: 520,
  Responsibility: 610,
  IndustryScenario: 710,
  Course: 820
}

const types = computed(() => Array.from(new Set(raw.value.nodes.map((node) => node.type))))
const jobNodes = computed(() => raw.value.nodes.filter((node) => node.type === 'Job'))
const visibleData = computed(() => filteredData())
const metricCards = computed(() => [
  { label: '总节点', value: graphStats.value.nodeCount ?? raw.value.nodes.length },
  { label: '岗位数', value: graphStats.value.jobCount ?? raw.value.nodes.filter((node) => node.type === 'Job').length },
  { label: '能力数', value: graphStats.value.skillCount ?? raw.value.nodes.filter((node) => node.type === 'Skill').length },
  { label: '关系边', value: graphStats.value.edgeCount ?? raw.value.edges.length },
  { label: '社区数', value: graphStats.value.communityCount ?? communities.value.length },
  { label: '平均度', value: graphStats.value.avgDegree ?? averageDegree.value }
])
const maxCommunityCount = computed(() => Math.max(1, ...communities.value.map((item) => item.count)))
const pathJobOptions = computed(() =>
  jobNodes.value
    .map((node) => ({ label: node.label, value: parseGraphJobId(node.id) }))
    .filter((item): item is { label: string; value: number } => Number.isFinite(item.value))
)
const averageDegree = computed(() => {
  if (!raw.value.nodes.length) return '0'
  return ((raw.value.edges.length * 2) / raw.value.nodes.length).toFixed(2)
})

function matchingSearchNodes(queryString: string) {
  const query = queryString.trim().toLowerCase()
  if (!query) return []

  return raw.value.nodes
    .filter((node) => {
      const searchable = [node.label, node.category, typeLabels[node.type], node.type]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()
      return searchable.includes(query)
    })
    .sort((left, right) => {
      const leftLabel = left.label.toLowerCase()
      const rightLabel = right.label.toLowerCase()
      const rank = (label: string) => label === query ? 0 : label.startsWith(query) ? 1 : 2
      return rank(leftLabel) - rank(rightLabel) || left.label.localeCompare(right.label, 'zh-CN')
    })
    .slice(0, 12)
}

function queryNodeSuggestions(queryString: string, callback: (items: GraphNode[]) => void) {
  callback(matchingSearchNodes(queryString))
}

async function focusSearchResult(item: GraphNode) {
  const node = raw.value.nodes.find((candidate) => candidate.id === item.id)
  if (!node) return

  keyword.value = node.label
  nodeType.value = ''
  activeCommunity.value = null
  viewMode.value = 'all'
  clearGraphFocus()
  await renderGraph()

  if (!nodeMeshById.has(node.id)) return
  selected.value = node
  applyGraphFocus(node.id)
}

async function clearSearchFocus() {
  keyword.value = ''
  clearGraphFocus()
  await renderGraph()
}

function nodeColor(type: string) {
  const colors: Record<string, string> = {
    Job: '#2f7cff',
    Skill: '#00d6ff',
    Tool: '#15e0a4',
    Certificate: '#a77dff',
    Responsibility: '#ffb22e',
    IndustryScenario: '#35b7ff',
    Course: '#43dc6d',
    Level: '#ff6fc8'
  }
  return colors[type] || '#7ca0c8'
}

function nodeSize(type: string, isCenter: boolean) {
  if (isCenter) return 26
  const sizes: Record<string, number> = {
    Job: 22,
    Skill: 15,
    Tool: 14,
    Certificate: 14,
    Responsibility: 13,
    IndustryScenario: 13,
    Course: 13,
    Level: 15
  }
  return sizes[type] || 12
}

function filteredData() {
  const normalizedKeyword = keyword.value.trim().toLowerCase()
  if (viewMode.value === 'all') {
    if (!normalizedKeyword && !nodeType.value && activeCommunity.value === null) return raw.value

    const matchedIds = new Set<string>()
    const selectedIds = new Set<string>()

    raw.value.nodes.forEach((node) => {
      const searchableText = `${node.label} ${node.id} ${node.category || ''} ${typeLabels[node.type] || node.type}`.toLowerCase()
      const isKeywordMatch = !normalizedKeyword || searchableText.includes(normalizedKeyword)
      const isTypeMatch = !nodeType.value || node.type === nodeType.value
      const community = nodeCommunityMap.value[node.id]
      const isCommunityMatch = activeCommunity.value === null || community === activeCommunity.value || community === undefined
      if (isKeywordMatch && isTypeMatch && isCommunityMatch) {
        matchedIds.add(node.id)
        selectedIds.add(node.id)
      }
    })

    const firstRing = new Set<string>()
    raw.value.edges.forEach((edge) => {
      if (!matchedIds.has(edge.source) && !matchedIds.has(edge.target)) return
      selectedIds.add(edge.source)
      selectedIds.add(edge.target)
      firstRing.add(edge.source)
      firstRing.add(edge.target)
    })

    raw.value.edges.forEach((edge) => {
      if (!firstRing.has(edge.source) && !firstRing.has(edge.target)) return
      selectedIds.add(edge.source)
      selectedIds.add(edge.target)
    })

    const nodes = raw.value.nodes.filter((node) => selectedIds.has(node.id))
    const ids = new Set(nodes.map((node) => node.id))
    const edges = raw.value.edges.filter((edge) => ids.has(edge.source) && ids.has(edge.target))
    return { nodes, edges }
  }

  const nodeMap = new Map(raw.value.nodes.map((node) => [node.id, node]))
  const selectedIds = new Set<string>()
  const counts = new Map<string, number>()
  const focusedJob = nodeMap.get(targetJobId.value) || raw.value.nodes.find((node) => node.type === 'Job')

  function addNode(node?: GraphNode, limitOverride?: number) {
    if (!node) return false
    if (nodeType.value && node.type !== nodeType.value) return false
    if (selectedIds.has(node.id)) return true
    const current = counts.get(node.type) || 0
    const typeLimits: Record<string, number> = normalizedKeyword
      ? { Job: 12, Skill: 34, Tool: 14, Certificate: 10, Responsibility: 10, IndustryScenario: 8, Course: 7, Level: 5 }
      : { Job: 4, Skill: 24, Tool: 10, Certificate: 8, Responsibility: 8, IndustryScenario: 6, Course: 5, Level: 3 }
    const limit = limitOverride || (nodeType.value ? (normalizedKeyword ? 46 : 34) : (typeLimits[node.type] || 4))
    if (current >= limit) return false
    counts.set(node.type, current + 1)
    selectedIds.add(node.id)
    return true
  }

  if (nodeType.value) {
    raw.value.nodes.forEach((node) => {
      const isKeywordMatch = !normalizedKeyword || node.label.toLowerCase().includes(normalizedKeyword)
      if (isKeywordMatch) addNode(node)
    })
  } else {
    addNode(focusedJob, 1)

    if (normalizedKeyword) {
      raw.value.nodes.forEach((node) => {
        if (node.id !== focusedJob?.id && node.label.toLowerCase().includes(normalizedKeyword)) addNode(node)
      })
    }

    const firstRing = new Set<string>()
    raw.value.edges.forEach((edge) => {
      const sourceIsSeed = edge.source === focusedJob?.id || selectedIds.has(edge.source)
      const targetIsSeed = edge.target === focusedJob?.id || selectedIds.has(edge.target)
      if (!sourceIsSeed && !targetIsSeed) return
      if (addNode(nodeMap.get(edge.source))) firstRing.add(edge.source)
      if (addNode(nodeMap.get(edge.target))) firstRing.add(edge.target)
    })

    raw.value.edges.forEach((edge) => {
      if (!firstRing.has(edge.source) && !firstRing.has(edge.target)) return
      addNode(nodeMap.get(edge.source))
      addNode(nodeMap.get(edge.target))
    })
  }

  const nodes = raw.value.nodes.filter((node) => selectedIds.has(node.id))
  const ids = new Set(nodes.map((node) => node.id))
  const edges = raw.value.edges.filter((edge) => ids.has(edge.source) && ids.has(edge.target)).slice(0, normalizedKeyword ? 150 : 118)
  return { nodes, edges }
}

async function renderGraph() {
  await nextTick()
  if (!scene || !camera || !renderer || !graphGroup) initScene()
  if (!graphGroup) return

  const data = filteredData()
  clearGraphGroup()
  hovered.value = undefined

  if (!data.nodes.length) return

  const positionedNodes = calculatePositions(data.nodes)
  buildNodes(positionedNodes, data.nodes.length)
  buildEdges(data.edges)
  if (viewMode.value === 'all') {
    clearGraphFocus()
  } else {
    if (!selected.value || !nodeMeshById.has(selected.value.id)) {
      selected.value = data.nodes.find((node) => node.id === targetJobId.value) || data.nodes.find((node) => node.type === 'Job') || data.nodes[0]
    }
    if (selected.value) updateFocusLines(selected.value.id)
  }
  resetView(false)
}

function calculatePositions(nodes: GraphNode[]): PositionedNode[] {
  if (viewMode.value === 'all') return calculateAllGraphPositions(nodes)

  const centerId = targetJobId.value
  const centerNode = nodes.find((node) => node.id === centerId) || nodes.find((node) => node.type === 'Job')
  const grouped = new Map<string, GraphNode[]>()
  nodes.forEach((node) => {
    if (node.id === centerNode?.id) return
    if (!grouped.has(node.type)) grouped.set(node.type, [])
    grouped.get(node.type)?.push(node)
  })

  const positioned: PositionedNode[] = []
  const order = ['Job', 'Level', 'Skill', 'Tool', 'Certificate', 'Responsibility', 'IndustryScenario', 'Course']

  if (centerNode) {
    positioned.push({ ...centerNode, position: new THREE.Vector3(0, 0, 0) })
  }

  order.forEach((type, ringIndex) => {
    const items = grouped.get(type)
    if (!items?.length) return
    const radius = typeRadius[type] || 320
    const count = Math.max(items.length, 1)
    const offset = ringIndex * 0.43

    items.forEach((node, index) => {
      const angle = (Math.PI * 2 * index) / count + offset
      const breathe = Math.sin(index * 1.37 + ringIndex) * 10
      const x = Math.cos(angle) * (radius + breathe)
      const y = Math.sin(angle) * (radius * 0.54 + breathe)
      const z = Math.sin(angle * 2 + ringIndex) * (type === 'Job' ? 28 : 62) + (ringIndex - 3) * 18
      positioned.push({ ...node, position: new THREE.Vector3(x, y, z) })
    })
  })

  return positioned
}

function calculateAllGraphPositions(nodes: GraphNode[]): PositionedNode[] {
  const grouped = new Map<string, GraphNode[]>()
  nodes.forEach((node) => {
    if (!grouped.has(node.type)) grouped.set(node.type, [])
    grouped.get(node.type)?.push(node)
  })

  const positioned: PositionedNode[] = []
  const order = ['Job', 'Level', 'Skill', 'Tool', 'Certificate', 'Responsibility', 'IndustryScenario', 'Course']

  order.forEach((type, ringIndex) => {
    const items = grouped.get(type)
    if (!items?.length) return
    const baseRadius = (typeRadius[type] || 520) + 170
    const count = items.length
    const ringRows = Math.max(1, Math.ceil(count / 14))

    items.forEach((node, index) => {
      const row = index % ringRows
      const column = Math.floor(index / ringRows)
      const columns = Math.ceil(count / ringRows)
      const angle = (Math.PI * 2 * column) / columns + ringIndex * 0.48 + row * 0.23
      const radius = baseRadius + row * 86 + Math.sin(index * 0.77 + ringIndex) * 34
      const x = Math.cos(angle) * radius
      const y = Math.sin(angle) * (radius * 0.62)
      const z = Math.sin(angle * 1.7 + row) * 132 + (ringIndex - 3) * 38
      positioned.push({ ...node, position: new THREE.Vector3(x, y, z) })
    })
  })

  return positioned
}

function initScene() {
  const container = containerRef.value
  if (!container) return

  scene = new THREE.Scene()
  scene.fog = null

  camera = new THREE.PerspectiveCamera(43, container.clientWidth / container.clientHeight, 1, 3600)
  camera.position.set(0, 0, 880)

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.8))
  renderer.setSize(container.clientWidth, container.clientHeight)
  renderer.setClearColor(0x000000, 0)
  renderer.domElement.className = 'graph-canvas'
  container.appendChild(renderer.domElement)

  graphGroup = new THREE.Group()
  scene.add(graphGroup)

  raycaster = new THREE.Raycaster()
  glowTexture = createGlowTexture()

  const ambient = new THREE.AmbientLight(0x92cfff, 0.72)
  const key = new THREE.DirectionalLight(0x89d8ff, 1.42)
  key.position.set(320, 520, 640)
  const rim = new THREE.PointLight(0x1e7bff, 1.4, 1200)
  rim.position.set(-360, -180, 420)
  scene.add(ambient, key, rim, createStarField())

  renderer.domElement.addEventListener('pointerdown', handlePointerDown)
  renderer.domElement.addEventListener('pointermove', handlePointerMove)
  renderer.domElement.addEventListener('pointerup', handlePointerUp)
  renderer.domElement.addEventListener('pointerleave', handlePointerLeave)
  renderer.domElement.addEventListener('wheel', handleWheel, { passive: false })

  animate()
}

function buildNodes(nodes: PositionedNode[], total: number) {
  if (!graphGroup || !glowTexture) return
  const group = graphGroup
  nodeMeshes = []
  nodeMeshById = new Map()
  nodeCompanions = new Map()
  nodeHomePositions = new Map()
  nodeTargetPositions = new Map()
  nodeFocusState = new Map()
  const showLabels = true

  nodes.forEach((node) => {
    const isCenter = node.id === targetJobId.value
    const size = nodeSize(node.type, isCenter)
    const color = new THREE.Color(nodeColor(node.type))
    const geometry = new THREE.SphereGeometry(size, 32, 24)
    const material = new THREE.MeshBasicMaterial({
      color,
      transparent: true,
      opacity: 1,
      fog: false
    })
    const mesh = new THREE.Mesh(geometry, material)
    mesh.position.copy(node.position)
    mesh.userData.raw = node
    mesh.userData.baseScale = mesh.scale.clone()
    group.add(mesh)
    nodeMeshes.push(mesh)
    nodeMeshById.set(node.id, mesh)
    nodeHomePositions.set(node.id, node.position.clone())
    nodeTargetPositions.set(node.id, node.position.clone())
    nodeFocusState.set(node.id, 1)
    const companions: THREE.Object3D[] = []

    const glow = new THREE.Sprite(new THREE.SpriteMaterial({
      map: glowTexture,
      color,
      transparent: true,
      opacity: isCenter ? 0.86 : node.type === 'Job' ? 0.72 : 0.52,
      depthWrite: false,
      depthTest: false,
      fog: false,
      blending: THREE.AdditiveBlending
    }))
    glow.position.copy(node.position)
    const glowSize = isCenter ? 136 : node.type === 'Job' ? 112 : node.type === 'Skill' ? 84 : 78
    glow.scale.set(glowSize, glowSize, 1)
    glow.userData.offset = new THREE.Vector3(0, 0, 0)
    glow.userData.baseOpacity = isCenter ? 0.86 : node.type === 'Job' ? 0.72 : 0.52
    glow.userData.baseScale = glow.scale.clone()
    group.add(glow)
    companions.push(glow)

    if (showLabels) {
      const label = createLabelSprite(node.label, nodeColor(node.type))
      const direction = node.position.clone()
      direction.z = 0
      if (direction.lengthSq() < 1) direction.set(0, 1, 0)
      direction.normalize()
      label.position
        .copy(node.position)
        .add(new THREE.Vector3(direction.x * (size + 50), direction.y * (size + 28), 10))
      label.userData.offset = label.position.clone().sub(node.position)
      label.userData.baseOpacity = 1
      label.userData.baseScale = label.scale.clone()
      group.add(label)
      companions.push(label)
    }
    nodeCompanions.set(node.id, companions)
  })
}

function buildEdges(edges: GraphEdge[]) {
  if (!graphGroup) return

  const positions: number[] = []
  edgeRecords = []
  edges.forEach((edge) => {
    const source = nodeMeshById.get(edge.source)
    const target = nodeMeshById.get(edge.target)
    if (!source || !target) return
    positions.push(source.position.x, source.position.y, source.position.z)
    positions.push(target.position.x, target.position.y, target.position.z)
    edgeRecords.push({ source: edge.source, target: edge.target })
  })

  edgeLineGeometry = new THREE.BufferGeometry()
  edgeLineGeometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
  const line = new THREE.LineSegments(
    edgeLineGeometry,
    new THREE.LineBasicMaterial({
      color: 0x79dfff,
      transparent: true,
      opacity: 0.075,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      fog: false
    })
  )
  graphGroup.add(line)
  highlightGroup = new THREE.Group()
  graphGroup.add(highlightGroup)
}

function updateEdgeGeometry(refreshFocusLines = true) {
  if (!edgeLineGeometry) return
  const positions = edgeLineGeometry.getAttribute('position') as THREE.BufferAttribute
  edgeRecords.forEach((edge, index) => {
    const source = nodeMeshById.get(edge.source)
    const target = nodeMeshById.get(edge.target)
    if (!source || !target) return
    positions.setXYZ(index * 2, source.position.x, source.position.y, source.position.z)
    positions.setXYZ(index * 2 + 1, target.position.x, target.position.y, target.position.z)
  })
  positions.needsUpdate = true
  if (refreshFocusLines && selected.value) updateFocusLines(selected.value.id)
}

function updateFocusLines(nodeId?: string) {
  if (!highlightGroup || !nodeId) return
  highlightGroup.children.forEach((child) => {
    if ('geometry' in child && child.geometry instanceof THREE.BufferGeometry) child.geometry.dispose()
    if ('material' in child && child.material instanceof THREE.Material) child.material.dispose()
  })
  highlightGroup.clear()
  focusedEdgeRecords = []
  highlightLineGeometry = undefined
  highlightGlowGeometry = undefined

  const positions: number[] = []
  edgeRecords.forEach((edge) => {
    if (edge.source !== nodeId && edge.target !== nodeId) return
    const source = nodeMeshById.get(edge.source)
    const target = nodeMeshById.get(edge.target)
    if (!source || !target) return
    positions.push(source.position.x, source.position.y, source.position.z)
    positions.push(target.position.x, target.position.y, target.position.z)
    focusedEdgeRecords.push({ source: edge.source, target: edge.target })
  })

  if (!positions.length) return

  highlightLineGeometry = new THREE.BufferGeometry()
  highlightLineGeometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
  const line = new THREE.LineSegments(
    highlightLineGeometry,
    new THREE.LineBasicMaterial({
      color: 0xf2feff,
      transparent: true,
      opacity: 0.96,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      fog: false
    })
  )
  highlightGroup.add(line)

  highlightGlowGeometry = highlightLineGeometry.clone()
  const glowLine = new THREE.LineSegments(
    highlightGlowGeometry,
    new THREE.LineBasicMaterial({
      color: 0x48e7ff,
      transparent: true,
      opacity: 0.62,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      fog: false
    })
  )
  glowLine.scale.setScalar(1.002)
  highlightGroup.add(glowLine)
}

function updateHighlightEdgeGeometry() {
  if (!highlightLineGeometry || !highlightGlowGeometry || !focusedEdgeRecords.length) return
  const applyPositions = (geometry: THREE.BufferGeometry) => {
    const positions = geometry.getAttribute('position') as THREE.BufferAttribute
    focusedEdgeRecords.forEach((edge, index) => {
      const source = nodeMeshById.get(edge.source)
      const target = nodeMeshById.get(edge.target)
      if (!source || !target) return
      positions.setXYZ(index * 2, source.position.x, source.position.y, source.position.z)
      positions.setXYZ(index * 2 + 1, target.position.x, target.position.y, target.position.z)
    })
    positions.needsUpdate = true
  }
  applyPositions(highlightLineGeometry)
  applyPositions(highlightGlowGeometry)
}

function clearGraphGroup() {
  if (!graphGroup) return
  graphGroup.children.forEach((child) => {
    if ('geometry' in child && child.geometry instanceof THREE.BufferGeometry) child.geometry.dispose()
    if ('material' in child) {
      const material = child.material
      if (Array.isArray(material)) material.forEach((item) => item.dispose())
      else if (material instanceof THREE.Material) material.dispose()
    }
  })
  graphGroup.clear()
  nodeMeshes = []
  nodeMeshById.clear()
  nodeCompanions.clear()
  edgeRecords = []
  focusedEdgeRecords = []
  edgeLineGeometry = undefined
  highlightLineGeometry = undefined
  highlightGlowGeometry = undefined
  highlightGroup = undefined
  draggedMesh = undefined
  pendingClickNode = undefined
  focusedNodeId = ''
}

function createGlowTexture() {
  const canvas = document.createElement('canvas')
  canvas.width = 128
  canvas.height = 128
  const ctx = canvas.getContext('2d')!
  const gradient = ctx.createRadialGradient(64, 64, 4, 64, 64, 62)
  gradient.addColorStop(0, 'rgba(255,255,255,0.95)')
  gradient.addColorStop(0.22, 'rgba(115,220,255,0.62)')
  gradient.addColorStop(0.52, 'rgba(30,123,255,0.22)')
  gradient.addColorStop(1, 'rgba(30,123,255,0)')
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, 128, 128)
  return new THREE.CanvasTexture(canvas)
}

function createStarField() {
  const geometry = new THREE.BufferGeometry()
  const positions: number[] = []
  const colors: number[] = []
  const colorA = new THREE.Color(0xffffff)
  const colorB = new THREE.Color(0x65dfff)
  const colorC = new THREE.Color(0x6d8dff)

  for (let i = 0; i < 380; i += 1) {
    const radius = 520 + Math.random() * 980
    const theta = Math.random() * Math.PI * 2
    const phi = Math.acos(2 * Math.random() - 1)
    positions.push(
      Math.sin(phi) * Math.cos(theta) * radius,
      Math.sin(phi) * Math.sin(theta) * radius,
      Math.cos(phi) * radius
    )
    const color = i % 5 === 0 ? colorB : i % 11 === 0 ? colorC : colorA
    colors.push(color.r, color.g, color.b)
  }

  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
  geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3))
  const material = new THREE.PointsMaterial({
    size: 1.8,
    transparent: true,
    opacity: 0.46,
    vertexColors: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  })
  return new THREE.Points(geometry, material)
}

function createLabelSprite(text: string, color: string) {
  const shortText = text.length > 11 ? `${text.slice(0, 11)}...` : text
  const cacheKey = `${shortText}-${color}-${isDarkMode() ? 'dark' : 'light'}`
  let texture = labelTextureCache.get(cacheKey)

  if (!texture) {
    const canvas = document.createElement('canvas')
    canvas.width = 360
    canvas.height = 92
    const ctx = canvas.getContext('2d')!
    const theme = new THREE.Color(color)
    const gradient = ctx.createLinearGradient(0, 0, 360, 0)
    gradient.addColorStop(0, 'rgba(3, 14, 34, 0.82)')
    gradient.addColorStop(0.55, 'rgba(8, 32, 72, 0.78)')
    gradient.addColorStop(1, 'rgba(4, 20, 46, 0.68)')

    roundRect(ctx, 14, 18, 332, 56, 16)
    ctx.fillStyle = gradient
    ctx.fill()
    ctx.lineWidth = 2
    ctx.strokeStyle = `rgba(${Math.round(theme.r * 255)}, ${Math.round(theme.g * 255)}, ${Math.round(theme.b * 255)}, 0.72)`
    ctx.stroke()

    ctx.beginPath()
    ctx.arc(36, 46, 6, 0, Math.PI * 2)
    ctx.fillStyle = color
    ctx.shadowColor = color
    ctx.shadowBlur = 12
    ctx.fill()
    ctx.shadowBlur = 0

    ctx.font = '800 24px Microsoft YaHei, PingFang SC, Arial'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.shadowColor = 'rgba(0, 18, 44, 0.85)'
    ctx.shadowBlur = 8
    ctx.fillStyle = '#f0fbff'
    ctx.fillText(shortText, 190, 46)
    texture = new THREE.CanvasTexture(canvas)
    labelTextureCache.set(cacheKey, texture)
  }

  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({
    map: texture,
    transparent: true,
    depthWrite: false,
    depthTest: false,
    fog: false
  }))
  sprite.scale.set(168, 44, 1)
  return sprite
}

function roundRect(ctx: CanvasRenderingContext2D, x: number, y: number, width: number, height: number, radius: number) {
  ctx.beginPath()
  ctx.moveTo(x + radius, y)
  ctx.lineTo(x + width - radius, y)
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius)
  ctx.lineTo(x + width, y + height - radius)
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height)
  ctx.lineTo(x + radius, y + height)
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius)
  ctx.lineTo(x, y + radius)
  ctx.quadraticCurveTo(x, y, x + radius, y)
  ctx.closePath()
}

function handlePointerDown(event: PointerEvent) {
  dragMoved = false
  lastPointer = { x: event.clientX, y: event.clientY }
  pendingClickNode = undefined
  const hit = pickNode(event)
  if (hit && camera && graphGroup && raycaster) {
    draggedMesh = hit
    pendingClickNode = hit.userData.raw
    const cameraNormal = new THREE.Vector3()
    camera.getWorldDirection(cameraNormal)
    const hitWorld = hit.getWorldPosition(new THREE.Vector3())
    dragPlane.setFromNormalAndCoplanarPoint(cameraNormal, hitWorld)
    if (raycaster.ray.intersectPlane(dragPlane, dragWorldPoint)) {
      const localPoint = graphGroup.worldToLocal(dragWorldPoint.clone())
      dragOffset.copy(hit.position).sub(localPoint)
    } else {
      dragOffset.set(0, 0, 0)
    }
  } else {
    isDragging = true
  }
  renderer?.domElement.setPointerCapture(event.pointerId)
}

function handlePointerMove(event: PointerEvent) {
  if (!renderer || !camera || !graphGroup || !raycaster) return

  const dx = event.clientX - lastPointer.x
  const dy = event.clientY - lastPointer.y

  if (draggedMesh) {
    if (Math.abs(dx) + Math.abs(dy) > 1) dragMoved = true
    const rect = renderer.domElement.getBoundingClientRect()
    pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
    pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1
    raycaster.setFromCamera(pointer, camera)
    if (raycaster.ray.intersectPlane(dragPlane, dragWorldPoint)) {
      const nextLocal = graphGroup.worldToLocal(dragWorldPoint.clone()).add(dragOffset)
      const delta = nextLocal.clone().sub(draggedMesh.position)
      draggedMesh.position.copy(nextLocal)
      const rawNode = draggedMesh.userData.raw as GraphNode
      nodeCompanions.get(rawNode.id)?.forEach((item) => item.position.add(delta))
      nodeTargetPositions.set(rawNode.id, nextLocal.clone())
      if (!focusedNodeId) nodeHomePositions.set(rawNode.id, nextLocal.clone())
      updateEdgeGeometry()
    }
    lastPointer = { x: event.clientX, y: event.clientY }
    renderer.domElement.style.cursor = 'grabbing'
    return
  }

  if (isDragging) {
    if (Math.abs(dx) + Math.abs(dy) > 2) dragMoved = true
    graphGroup.rotation.y += dx * 0.006
    graphGroup.rotation.x += dy * 0.004
    graphGroup.rotation.x = Math.max(-1.05, Math.min(1.05, graphGroup.rotation.x))
    lastPointer = { x: event.clientX, y: event.clientY }
    return
  }

  const hit = pickNode(event)
  hovered.value = hit?.userData.raw
  if (!focusedNodeId) updateFocusLines(hit?.userData.raw?.id || selected.value?.id)
  tooltip.x = event.offsetX + 16
  tooltip.y = event.offsetY + 16
  renderer.domElement.style.cursor = hit ? 'pointer' : 'grab'
}

function handlePointerUp(event: PointerEvent) {
  if (!dragMoved && pendingClickNode) activateNode(pendingClickNode)
  isDragging = false
  draggedMesh = undefined
  pendingClickNode = undefined
  renderer?.domElement.releasePointerCapture(event.pointerId)
}

function handlePointerLeave() {
  isDragging = false
  draggedMesh = undefined
  pendingClickNode = undefined
  hovered.value = undefined
  if (!focusedNodeId) updateFocusLines(selected.value?.id)
}

function handleWheel(event: WheelEvent) {
  if (!camera) return
  event.preventDefault()
  camera.position.z = Math.max(520, Math.min(1320, camera.position.z + event.deltaY * 0.54))
}

function handleKeyDown(event: KeyboardEvent) {
  const key = event.key.toLowerCase()
  if (key === 'shift') {
    pressedKeys.add('shift')
    return
  }
  if (!['w', 'a', 's', 'd'].includes(key) || isTypingTarget(event.target)) return
  event.preventDefault()
  pressedKeys.add(key)
}

function handleKeyUp(event: KeyboardEvent) {
  const key = event.key.toLowerCase()
  if (key === 'shift') pressedKeys.delete('shift')
  if (['w', 'a', 's', 'd'].includes(key)) pressedKeys.delete(key)
}

function handleWindowBlur() {
  pressedKeys.clear()
  cameraPanVelocity.set(0, 0)
}

function isTypingTarget(target: EventTarget | null) {
  const element = target as HTMLElement | null
  const tagName = element?.tagName?.toLowerCase()
  return tagName === 'input' || tagName === 'textarea' || tagName === 'select' || Boolean(element?.isContentEditable)
}

function updateKeyboardPan(deltaSeconds: number) {
  if (!camera) return
  const direction = new THREE.Vector2(
    (pressedKeys.has('d') ? 1 : 0) - (pressedKeys.has('a') ? 1 : 0),
    (pressedKeys.has('w') ? 1 : 0) - (pressedKeys.has('s') ? 1 : 0)
  )
  if (direction.lengthSq() > 0) direction.normalize()

  const speed = pressedKeys.has('shift') ? 720 : 420
  const targetVelocity = direction.multiplyScalar(speed)
  const smoothing = direction.lengthSq() > 0 ? 1 - Math.exp(-14 * deltaSeconds) : 1 - Math.exp(-11 * deltaSeconds)
  cameraPanVelocity.lerp(targetVelocity, smoothing)

  camera.position.x += cameraPanVelocity.x * deltaSeconds
  camera.position.y += cameraPanVelocity.y * deltaSeconds
  camera.position.x = Math.max(-820, Math.min(820, camera.position.x))
  camera.position.y = Math.max(-540, Math.min(540, camera.position.y))
}

function pickNode(event: PointerEvent) {
  if (!renderer || !camera || !raycaster || !nodeMeshes.length) return undefined
  const rect = renderer.domElement.getBoundingClientRect()
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1
  raycaster.setFromCamera(pointer, camera)
  return raycaster.intersectObjects(nodeMeshes, false)[0]?.object as THREE.Mesh | undefined
}

function selectNode(node: GraphNode) {
  selected.value = node
  updateFocusLines(node.id)
}

function activateNode(node: GraphNode) {
  const now = performance.now()
  const isDoubleClick = focusedNodeId === node.id && lastClickNodeId === node.id && now - lastClickAt < 360
  lastClickNodeId = node.id
  lastClickAt = now

  if (isDoubleClick) {
    clearGraphFocus()
    return
  }

  selected.value = node
  if (viewMode.value === 'all') applyGraphFocus(node.id)
  else updateFocusLines(node.id)
}

function relatedNodeIds(nodeId: string) {
  const ids = new Set<string>([nodeId])
  edgeRecords.forEach((edge) => {
    if (edge.source === nodeId) ids.add(edge.target)
    if (edge.target === nodeId) ids.add(edge.source)
  })
  return ids
}

function applyGraphFocus(nodeId: string) {
  focusedNodeId = nodeId
  const relatedIds = relatedNodeIds(nodeId)
  const neighborIds = Array.from(relatedIds).filter((id) => id !== nodeId && nodeMeshById.has(id))
  const center = new THREE.Vector3(0, 0, 0)
  const home = nodeHomePositions.get(nodeId)
  const focusOffset = home ? home.clone().multiplyScalar(-0.18) : new THREE.Vector3()

  nodeTargetPositions.forEach((_, id) => {
    const base = nodeHomePositions.get(id) || new THREE.Vector3()
    if (id === nodeId) {
      nodeTargetPositions.set(id, center.clone())
      nodeFocusState.set(id, 1)
      return
    }

    if (relatedIds.has(id)) {
      const order = Math.max(0, neighborIds.indexOf(id))
      const ringSize = 8
      const ring = Math.floor(order / ringSize)
      const countInRing = Math.min(ringSize, Math.max(1, neighborIds.length - ring * ringSize))
      const angle = (Math.PI * 2 * (order % ringSize)) / countInRing + ring * 0.38
      const radius = 188 + ring * 92
      nodeTargetPositions.set(id, new THREE.Vector3(
        Math.cos(angle) * radius,
        Math.sin(angle) * radius * 0.74,
        Math.sin(angle * 1.35) * 86 + ring * 34
      ))
      nodeFocusState.set(id, 0.95)
      return
    }

    const direction = base.clone().add(focusOffset)
    if (direction.lengthSq() < 1) direction.set(Math.sin(id.length) || 1, Math.cos(id.length * 1.7) || 0.4, 0)
    direction.normalize()
    const distance = Math.max(960, base.length() * 1.34 + 260)
    nodeTargetPositions.set(id, direction.multiplyScalar(distance).setZ(base.z * 1.16))
    nodeFocusState.set(id, 0.14)
  })

  updateFocusLines(nodeId)
}

function clearGraphFocus() {
  focusedNodeId = ''
  selected.value = undefined
  lastClickNodeId = ''
  lastClickAt = 0
  nodeHomePositions.forEach((position, id) => {
    nodeTargetPositions.set(id, position.clone())
    nodeFocusState.set(id, 1)
  })
  if (highlightGroup) {
    highlightGroup.children.forEach((child) => {
      if ('geometry' in child && child.geometry instanceof THREE.BufferGeometry) child.geometry.dispose()
      if ('material' in child && child.material instanceof THREE.Material) child.material.dispose()
    })
    highlightGroup.clear()
  }
  focusedEdgeRecords = []
  highlightLineGeometry = undefined
  highlightGlowGeometry = undefined
}

function resetView(animateBack = true) {
  if (!camera || !graphGroup) return
  if (animateBack !== false) {
    keyword.value = ''
    nodeType.value = ''
    activeCommunity.value = null
    pathResult.value = null
    clearGraphFocus()
  }
  camera.position.set(0, 0, viewMode.value === 'all' ? 880 : 640)
  cameraPanVelocity.set(0, 0)
  pressedKeys.clear()
  if (animateBack) {
    graphGroup.rotation.set(-0.16, 0.18, 0)
  } else {
    graphGroup.rotation.x = -0.16
    graphGroup.rotation.y = 0.18
    graphGroup.rotation.z = 0
  }
  if (animateBack !== false) void nextTick().then(renderGraph)
}

function setObjectOpacity(object: THREE.Object3D, opacity: number) {
  const material = (object as THREE.Mesh | THREE.Sprite).material
  if (Array.isArray(material)) {
    material.forEach((item) => {
      item.opacity = opacity
      item.transparent = true
    })
  } else if (material instanceof THREE.Material) {
    material.opacity = opacity
    material.transparent = true
  }
}

function objectOpacity(object: THREE.Object3D) {
  const material = (object as THREE.Mesh | THREE.Sprite).material
  if (Array.isArray(material)) return material[0]?.opacity ?? 1
  if (material instanceof THREE.Material) return material.opacity
  return 1
}

function animateGraphFocus(deltaSeconds: number) {
  if (!nodeMeshes.length) return
  const moveEase = 1 - Math.exp(-7.5 * deltaSeconds)
  const fadeEase = 1 - Math.exp(-9 * deltaSeconds)
  const scaleEase = 1 - Math.exp(-8 * deltaSeconds)
  let moved = false

  nodeMeshes.forEach((mesh) => {
    const rawNode = mesh.userData.raw as GraphNode
    const target = nodeTargetPositions.get(rawNode.id) || nodeHomePositions.get(rawNode.id)
    if (!target) return
    const before = mesh.position.clone()
    mesh.position.lerp(target, moveEase)
    if (before.distanceToSquared(mesh.position) > 0.0001) moved = true

    const focus = nodeFocusState.get(rawNode.id) ?? 1
    const isFocused = focusedNodeId === rawNode.id
    const targetOpacity = focusedNodeId ? (focus > 0.5 ? 1 : 0.16) : 1
    const currentOpacity = objectOpacity(mesh)
    setObjectOpacity(mesh, currentOpacity + (targetOpacity - currentOpacity) * fadeEase)

    const targetScale = isFocused ? 1.32 : focus > 0.5 ? 1.04 : 0.66
    const baseScale = mesh.userData.baseScale as THREE.Vector3
    if (baseScale) {
      const scale = baseScale.clone().multiplyScalar(targetScale)
      mesh.scale.lerp(scale, scaleEase)
    }

    nodeCompanions.get(rawNode.id)?.forEach((item) => {
      const offset = item.userData.offset as THREE.Vector3 | undefined
      item.position.copy(mesh.position).add(offset || new THREE.Vector3())

      const baseOpacity = item.userData.baseOpacity ?? 1
      const itemTargetOpacity = focusedNodeId ? baseOpacity * (focus > 0.5 ? 1 : 0.12) : baseOpacity
      const current = objectOpacity(item)
      setObjectOpacity(item, current + (itemTargetOpacity - current) * fadeEase)

      const baseItemScale = item.userData.baseScale as THREE.Vector3 | undefined
      if (baseItemScale) {
        item.scale.lerp(baseItemScale.clone().multiplyScalar(isFocused ? 1.14 : focus > 0.5 ? 1.02 : 0.74), scaleEase)
      }
    })
  })

  if (moved || focusedNodeId) {
    updateEdgeGeometry(false)
    updateHighlightEdgeGeometry()
  }
}

function animate() {
  if (!scene || !camera || !renderer) return
  const now = performance.now()
  const deltaSeconds = lastFrameTime ? Math.min((now - lastFrameTime) / 1000, 0.05) : 0
  lastFrameTime = now
  animationId = requestAnimationFrame(animate)
  updateKeyboardPan(deltaSeconds)
  animateGraphFocus(deltaSeconds)
  if (graphGroup && !isDragging && !draggedMesh) {
    graphGroup.rotation.y += 0.0007
    graphGroup.rotation.z = Math.sin(Date.now() * 0.00035) * 0.025
  }
  renderer.render(scene, camera)
}

function resizeScene() {
  const container = containerRef.value
  if (!container || !renderer || !camera) return
  const width = container.clientWidth
  const height = container.clientHeight
  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
}

function relationshipCount(id: string) {
  return raw.value.edges.filter((edge) => edge.source === id || edge.target === id).length
}

function communityWidth(count: number) {
  return `${Math.round((count / maxCommunityCount.value) * 100)}%`
}

async function toggleCommunity(index: number) {
  activeCommunity.value = activeCommunity.value === index ? null : index
  clearGraphFocus()
  await renderGraph()
}

function parseGraphJobId(id: string) {
  const match = id.match(/(\d+)$/)
  return match ? Number(match[1]) : Number.NaN
}

function adjacentNodes(id: string) {
  const adjacentIds = new Set<string>()
  raw.value.edges.forEach((edge) => {
    if (edge.source === id) adjacentIds.add(edge.target)
    if (edge.target === id) adjacentIds.add(edge.source)
  })
  return raw.value.nodes.filter((node) => adjacentIds.has(node.id)).slice(0, 12)
}

function pruneIsolatedNodes(nodes: GraphNode[], edges: GraphEdge[]) {
  const nodeIds = new Set(nodes.map((node) => node.id))
  const cleanEdges = edges.filter((edge) => nodeIds.has(edge.source) && nodeIds.has(edge.target))
  const connectedIds = new Set<string>()
  cleanEdges.forEach((edge) => {
    connectedIds.add(edge.source)
    connectedIds.add(edge.target)
  })
  return {
    nodes: nodes.filter((node) => connectedIds.has(node.id)),
    edges: cleanEdges.filter((edge) => connectedIds.has(edge.source) && connectedIds.has(edge.target))
  }
}

function isDarkMode() {
  return document.body.classList.contains('theme-dark')
}

async function handleTargetJobChange() {
  selected.value = raw.value.nodes.find((node) => node.id === targetJobId.value)
  await renderGraph()
}

async function findPath() {
  if (!pathFrom.value || !pathTo.value) return
  pathLoading.value = true
  try {
    pathResult.value = await api.graphPath(pathFrom.value, pathTo.value)
  } finally {
    pathLoading.value = false
  }
}

async function loadGraph() {
  loading.value = true
  graphError.value = false
  try {
    const [response, explore] = await Promise.all([
      api.skillGraph(),
      api.graphFull({ limit: 500 }).catch(() => null)
    ])
    const cleanGraph = pruneIsolatedNodes(
      Array.isArray(response?.nodes) ? response.nodes : [],
      Array.isArray(response?.edges) ? response.edges : []
    )
    raw.value = cleanGraph
    graphStats.value = explore?.stats ?? {
      nodeCount: cleanGraph.nodes.length,
      jobCount: cleanGraph.nodes.filter((node) => node.type === 'Job').length,
      skillCount: cleanGraph.nodes.filter((node) => node.type === 'Skill').length,
      edgeCount: cleanGraph.edges.length,
      communityCount: 0,
      avgDegree: cleanGraph.nodes.length ? ((cleanGraph.edges.length * 2) / cleanGraph.nodes.length).toFixed(2) : '0'
    }
    communities.value = Array.isArray(explore?.communities) ? explore.communities : []
    nodeCommunityMap.value = Array.isArray(explore?.nodes)
      ? explore.nodes.reduce((map: Record<string, number>, node: { id?: string; community?: number }) => {
        if (node.id && typeof node.community === 'number') map[node.id] = node.community
        return map
      }, {})
      : {}
    if (!targetJobId.value || !raw.value.nodes.some((node) => node.id === targetJobId.value)) {
      targetJobId.value = raw.value.nodes.find((node) => node.type === 'Job')?.id || ''
    }
    if (selected.value && !raw.value.nodes.some((node) => node.id === selected.value?.id)) selected.value = undefined
    if (pathFrom.value && !pathJobOptions.value.some((job) => job.value === pathFrom.value)) pathFrom.value = null
    if (pathTo.value && !pathJobOptions.value.some((job) => job.value === pathTo.value)) pathTo.value = null
    await renderGraph()
  } catch {
    graphError.value = true
    clearGraphGroup()
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  initScene()
  await loadGraph()
  window.addEventListener('keydown', handleKeyDown)
  window.addEventListener('keyup', handleKeyUp)
  window.addEventListener('blur', handleWindowBlur)
  if (containerRef.value) {
    resizeObserver = new ResizeObserver(resizeScene)
    resizeObserver.observe(containerRef.value)
  }
})

onBeforeUnmount(() => {
  if (renderer?.domElement) {
    renderer.domElement.removeEventListener('pointerdown', handlePointerDown)
    renderer.domElement.removeEventListener('pointermove', handlePointerMove)
    renderer.domElement.removeEventListener('pointerup', handlePointerUp)
    renderer.domElement.removeEventListener('pointerleave', handlePointerLeave)
    renderer.domElement.removeEventListener('wheel', handleWheel)
  }
  window.removeEventListener('keydown', handleKeyDown)
  window.removeEventListener('keyup', handleKeyUp)
  window.removeEventListener('blur', handleWindowBlur)
  resizeObserver?.disconnect()
  cancelAnimationFrame(animationId)
  clearGraphGroup()
  labelTextureCache.forEach((texture) => texture.dispose())
  glowTexture?.dispose()
  renderer?.dispose()
})
</script>

<style scoped>
.skill-graph-page {
  position: relative;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
}

:global(.node-search-option) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  width: 100%;
}

:global(.node-search-option span) {
  overflow: hidden;
  color: #16345f;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:global(.node-search-option small) {
  flex: 0 0 auto;
  color: #7b8faa;
  font-size: 11px;
}

.graph-overview {
  display: grid;
  grid-template-columns: repeat(6, minmax(120px, 1fr)) minmax(260px, 1.5fr);
  gap: 14px;
}

.graph-overview__item {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(107, 174, 255, 0.3);
  border-radius: 18px;
  padding: 16px 18px;
  background: rgba(255, 255, 255, 0.62);
  box-shadow: 0 14px 42px rgba(37, 99, 235, 0.08);
  backdrop-filter: blur(16px);
}

.graph-overview__item::after {
  position: absolute;
  right: -20px;
  top: -34px;
  width: 92px;
  height: 92px;
  content: "";
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0, 200, 245, 0.22), transparent 68%);
}

.graph-overview strong {
  display: block;
  color: #1768d1;
  font-size: 26px;
  font-weight: 950;
}

.graph-overview span {
  position: relative;
  color: #5d759a;
  font-size: 13px;
  font-weight: 800;
  line-height: 1.8;
}

.graph-overview__hint {
  display: flex;
  align-items: center;
}

.graph-panel,
.graph-detail-panel {
  overflow: hidden;
}

.graph-detail-panel {
  max-height: 842px;
  overflow-y: auto;
}

.graph-detail-panel::-webkit-scrollbar {
  width: 6px;
}

.graph-detail-panel::-webkit-scrollbar-thumb {
  border-radius: 999px;
  background: rgba(30, 123, 255, 0.22);
}

.graph-stage {
  position: relative;
  min-height: 740px;
}

.graph-box {
  position: relative;
  height: 740px;
  overflow: hidden;
  border: 1px solid rgba(92, 199, 255, 0.34);
  border-radius: 26px;
  background:
    radial-gradient(circle at 46% 48%, rgba(62, 132, 220, 0.22), transparent 30%),
    radial-gradient(circle at 72% 24%, rgba(0, 196, 245, 0.12), transparent 24%),
    radial-gradient(circle at 24% 78%, rgba(84, 112, 196, 0.14), transparent 28%),
    linear-gradient(145deg, #07152d 0%, #0b2244 50%, #0d2d55 100%);
  background-size: auto, auto, auto, auto;
  box-shadow:
    inset 0 0 100px rgba(2, 11, 28, 0.38),
    inset 0 0 70px rgba(0, 200, 245, 0.08),
    0 22px 70px rgba(10, 36, 82, 0.18);
}

.graph-box::before {
  position: absolute;
  z-index: 0;
  inset: -18%;
  content: "";
  pointer-events: none;
  background:
    conic-gradient(from 80deg, transparent 0 18%, rgba(0, 200, 245, 0.08), transparent 34% 100%);
  filter: blur(18px);
  opacity: 0.34;
  animation: nebulaSpin 42s linear infinite;
}

.graph-box::after {
  position: absolute;
  z-index: 1;
  inset: 0;
  content: "";
  pointer-events: none;
  background:
    radial-gradient(circle at 15% 18%, rgba(255, 255, 255, 0.72) 0 1px, transparent 2px),
    radial-gradient(circle at 34% 36%, rgba(136, 231, 255, 0.62) 0 1px, transparent 2px),
    radial-gradient(circle at 62% 22%, rgba(255, 255, 255, 0.58) 0 1px, transparent 2px),
    radial-gradient(circle at 78% 64%, rgba(116, 200, 255, 0.68) 0 1px, transparent 2px),
    radial-gradient(circle at 42% 82%, rgba(255, 255, 255, 0.5) 0 1px, transparent 2px);
  opacity: 0.28;
  animation: starTwinkle 5.6s ease-in-out infinite;
}

.graph-box :deep(canvas) {
  position: relative;
  z-index: 2;
  display: block;
  cursor: grab;
}

.graph-box :deep(canvas:active) {
  cursor: grabbing;
}

.graph-orbit {
  position: absolute;
  z-index: 1;
  left: 50%;
  top: 50%;
  pointer-events: none;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  opacity: 0.48;
}

.graph-orbit-a {
  width: 500px;
  height: 500px;
  border: 1px dashed rgba(0, 200, 245, 0.18);
  box-shadow: 0 0 30px rgba(0, 200, 245, 0.04);
  animation: graphOrbit 28s linear infinite;
}

.graph-orbit-b {
  width: 720px;
  height: 720px;
  border: 1px solid rgba(120, 186, 255, 0.08);
  box-shadow: inset 0 0 46px rgba(30, 123, 255, 0.04);
  animation: graphOrbit 42s linear reverse infinite;
}

.node-tooltip {
  position: absolute;
  z-index: 4;
  min-width: 130px;
  max-width: 220px;
  border: 1px solid rgba(105, 191, 255, 0.52);
  border-radius: 14px;
  padding: 10px 12px;
  background: rgba(7, 30, 68, 0.82);
  box-shadow: 0 16px 40px rgba(11, 43, 111, 0.22);
  color: #fff;
  pointer-events: none;
  backdrop-filter: blur(14px);
}

.node-tooltip b,
.node-tooltip span {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-tooltip span {
  margin-top: 4px;
  color: #9eeaff;
  font-size: 12px;
}

.graph-message {
  position: absolute;
  z-index: 6;
  inset: 0;
  display: grid;
  place-items: center;
  border-radius: 22px;
  background: rgba(248, 252, 255, 0.68);
  backdrop-filter: blur(12px);
}

.detail-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 20px;
  color: #15386d;
  font-weight: 950;
}

.detail-heading.compact {
  margin-bottom: 12px;
}

.detail-heading small {
  color: #00a4d6;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 1px;
}

.selected-node {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 18px;
  border: 1px solid rgba(107, 174, 255, 0.28);
  border-radius: 18px;
  padding: 14px;
  background: linear-gradient(135deg, rgba(230, 244, 255, 0.86), rgba(255, 255, 255, 0.72));
}

.selected-node__dot {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--node-color);
  box-shadow: 0 0 28px color-mix(in srgb, var(--node-color) 66%, transparent);
}

.selected-node h3 {
  margin: 0 0 8px;
  color: #102f60;
  font-size: 18px;
}

.detail-block {
  display: grid;
  gap: 8px;
  margin-top: 16px;
}

.detail-block span {
  color: #6580ab;
  font-size: 12px;
  font-weight: 900;
}

.detail-block p {
  margin: 0;
  color: #23436e;
  font-size: 14px;
  line-height: 1.8;
}

.detail-subsection {
  margin-top: 22px;
  border-top: 1px solid rgba(104, 158, 225, 0.18);
  padding-top: 18px;
}

.community-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.community-row {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(107, 174, 255, 0.22);
  border-radius: 14px;
  padding: 9px 10px;
  background: rgba(246, 251, 255, 0.58);
  color: #173b70;
  cursor: pointer;
  transition: all 0.2s ease;
}

.community-row:hover,
.community-row.active {
  border-color: rgba(0, 200, 245, 0.46);
  background: rgba(226, 246, 255, 0.78);
  box-shadow: 0 12px 30px rgba(30, 123, 255, 0.1);
  transform: translateY(-1px);
}

.community-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  opacity: 0.88;
  box-shadow: 0 0 8px rgba(112, 205, 224, 0.24);
}

.community-name,
.community-count {
  font-size: 13px;
  font-weight: 850;
}

.community-count {
  color: #52739f;
}

.community-bar {
  grid-column: 1 / -1;
  height: 4px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(190, 213, 242, 0.42);
}

.community-bar i {
  display: block;
  height: 100%;
  border-radius: inherit;
  opacity: 0.78;
  filter: saturate(0.78);
  box-shadow: 0 0 8px rgba(100, 190, 218, 0.2);
}

.path-select {
  width: 100%;
  margin-bottom: 10px;
}

.path-button {
  width: 100%;
}

.path-result {
  margin-top: 14px;
}

.path-chain {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 7px;
}

.path-node {
  border: 1px solid rgba(95, 159, 255, 0.28);
  border-radius: 999px;
  padding: 5px 10px;
  background: rgba(235, 243, 255, 0.88);
  color: #1d4f9a;
  font-size: 12px;
  font-weight: 850;
}

.path-node.skill,
.path-node.Skill {
  border-color: rgba(0, 200, 245, 0.32);
  background: rgba(224, 250, 255, 0.88);
  color: #007c9d;
}

.path-arrow {
  color: #00a4d6;
  font-weight: 950;
}

.path-shared {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
}

.path-shared span {
  width: 100%;
  color: #6580ab;
  font-size: 12px;
  font-weight: 900;
}

.neighbor-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.graph-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.graph-legend__item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(107, 174, 255, 0.24);
  border-radius: 999px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.54);
  color: #58749e;
  font-size: 12px;
  font-weight: 850;
  backdrop-filter: blur(12px);
}

.graph-legend__item i {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  box-shadow: 0 0 12px currentColor;
}

:global(body.theme-dark) .graph-overview__item {
  border-color: rgba(91, 145, 220, 0.4);
  background:
    radial-gradient(circle at 10% 0%, rgba(0, 200, 245, 0.12), transparent 36%),
    linear-gradient(145deg, rgba(22, 48, 98, 0.86), rgba(10, 28, 62, 0.78)),
    rgba(14, 34, 72, 0.78) !important;
  box-shadow:
    0 0 0 1px rgba(91, 145, 220, 0.14) inset,
    0 18px 54px rgba(0, 0, 0, 0.28) !important;
}

:global(body.theme-dark) .selected-node {
  border-color: rgba(91, 145, 220, 0.42);
  background:
    radial-gradient(circle at 8% 0%, rgba(0, 200, 245, 0.12), transparent 40%),
    linear-gradient(145deg, rgba(22, 48, 98, 0.88), rgba(10, 28, 62, 0.78)),
    rgba(14, 34, 72, 0.78) !important;
  box-shadow:
    0 0 0 1px rgba(91, 145, 220, 0.16) inset,
    0 18px 54px rgba(0, 0, 0, 0.28) !important;
}

:global(body.theme-dark) .community-row {
  border-color: rgba(91, 145, 220, 0.34);
  background:
    radial-gradient(circle at 100% 0%, rgba(89, 166, 255, 0.1), transparent 40%),
    linear-gradient(145deg, rgba(20, 44, 90, 0.82), rgba(10, 26, 58, 0.74)),
    rgba(12, 30, 66, 0.76) !important;
  color: #e8f2ff !important;
  box-shadow:
    0 0 0 1px rgba(91, 145, 220, 0.12) inset !important;
}

:global(body.theme-dark) .community-row:hover,
:global(body.theme-dark) .community-row.active {
  border-color: rgba(0, 214, 255, 0.56) !important;
  background:
    radial-gradient(circle at 0% 0%, rgba(0, 214, 255, 0.22), transparent 42%),
    linear-gradient(145deg, rgba(24, 72, 138, 0.9), rgba(14, 44, 92, 0.82)),
    rgba(18, 56, 112, 0.84) !important;
  box-shadow:
    0 0 0 1px rgba(0, 214, 255, 0.22) inset,
    0 14px 40px rgba(0, 120, 220, 0.22) !important;
}

:global(body.theme-dark) .path-node {
  border-color: rgba(91, 145, 220, 0.42) !important;
  background:
    radial-gradient(circle at 0% 0%, rgba(0, 200, 245, 0.12), transparent 40%),
    linear-gradient(145deg, rgba(22, 48, 98, 0.88), rgba(10, 28, 62, 0.8)),
    rgba(14, 34, 72, 0.8) !important;
  color: #d8e8ff !important;
}

:global(body.theme-dark) .path-node.skill,
:global(body.theme-dark) .path-node.Skill {
  border-color: rgba(0, 214, 255, 0.48) !important;
  background:
    radial-gradient(circle at 100% 0%, rgba(0, 214, 255, 0.2), transparent 40%),
    linear-gradient(145deg, rgba(12, 70, 118, 0.88), rgba(8, 40, 78, 0.8)),
    rgba(10, 50, 96, 0.8) !important;
  color: #bef3ff !important;
}

:global(body.theme-dark) .graph-legend__item {
  border-color: rgba(91, 145, 220, 0.36) !important;
  background:
    linear-gradient(145deg, rgba(20, 44, 90, 0.82), rgba(10, 26, 58, 0.72)),
    rgba(12, 30, 66, 0.74) !important;
  color: #9db3cf !important;
}

:global(body.theme-dark) .graph-box {
  box-shadow:
    inset 0 0 120px rgba(0, 200, 245, 0.12),
    inset 0 0 72px rgba(89, 166, 255, 0.08),
    0 22px 64px rgba(0, 0, 0, 0.32) !important;
}

:global(body.theme-dark) .graph-message {
  background:
    radial-gradient(circle at 10% 0%, rgba(0, 200, 245, 0.1), transparent 30%),
    linear-gradient(145deg, rgba(18, 38, 78, 0.88), rgba(8, 22, 48, 0.82)),
    rgba(12, 28, 58, 0.8) !important;
  backdrop-filter: blur(18px) !important;
}

@keyframes nebulaSpin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes starTwinkle {
  0%,
  100% {
    opacity: 0.42;
  }

  50% {
    opacity: 0.72;
  }
}

:global(body.theme-dark) .graph-overview strong {
  color: #7fc8ff !important;
  text-shadow: 0 0 18px rgba(89, 166, 255, 0.35);
}

:global(body.theme-dark) .detail-heading,
:global(body.theme-dark) .selected-node h3,
:global(body.theme-dark) .community-name {
  color: #e8f2ff;
}

:global(body.theme-dark) .graph-overview span,
:global(body.theme-dark) .detail-block span,
:global(body.theme-dark) .community-count,
:global(body.theme-dark) .path-shared span {
  color: #9db3cf;
}

:global(body.theme-dark) .detail-block p {
  color: #d8e8ff;
}

:global(body.theme-dark) .community-bar {
  background: rgba(70, 110, 170, 0.28) !important;
  box-shadow: inset 0 0 0 1px rgba(91, 145, 220, 0.18) !important;
}

:global(body.theme-dark) :deep(.path-shared .el-tag) {
  border-color: rgba(0, 214, 255, 0.36) !important;
  background:
    linear-gradient(145deg, rgba(12, 70, 118, 0.72), rgba(8, 40, 78, 0.66)),
    rgba(10, 50, 96, 0.64) !important;
  color: #bef3ff !important;
}

@keyframes graphOrbit {
  to {
    transform: translate(-50%, -50%) rotate(360deg);
  }
}

@media (max-width: 1280px) {
  .graph-overview {
    grid-template-columns: repeat(2, 1fr);
  }

  .graph-stage,
  .graph-box {
    min-height: 560px;
    height: 560px;
  }
}
</style>

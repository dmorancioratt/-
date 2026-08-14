<template>
  <div class="life-tree" aria-label="可交互的职业天赋树">
    <div ref="flowShell" class="life-tree__flow-shell">
      <VueFlow
        id="career-talent-tree"
        v-model:nodes="nodes"
        v-model:edges="edges"
        :min-zoom="currentLayout.minZoom"
        :max-zoom="1.4"
        :nodes-draggable="false"
        :nodes-connectable="false"
        :elements-selectable="false"
        :zoom-on-double-click="false"
        :pan-on-scroll="true"
        :prevent-scrolling="true"
        fit-view-on-init
        @node-click="handleNodeClick"
      >
        <template #node-talent="nodeProps">
          <TalentTreeNode v-bind="nodeProps" />
        </template>
        <template #edge-energy="edgeProps">
          <TalentTreeEdge v-bind="edgeProps" />
        </template>
      </VueFlow>

      <div class="life-tree__controls" aria-label="天赋树视图控制">
        <button type="button" title="放大" aria-label="放大" @click="zoomIn({ duration: 220 })"><el-icon><ZoomIn /></el-icon></button>
        <button type="button" title="缩小" aria-label="缩小" @click="zoomOut({ duration: 220 })"><el-icon><ZoomOut /></el-icon></button>
        <button type="button" title="显示完整天赋树" aria-label="显示完整天赋树" @click="resetView"><el-icon><FullScreen /></el-icon></button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'
import { FullScreen, ZoomIn, ZoomOut } from '@element-plus/icons-vue'
import { Position, VueFlow, useVueFlow, type Edge, type GraphNode, type Node } from '@vue-flow/core'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import TalentTreeEdge from './TalentTreeEdge.vue'
import TalentTreeNode from './TalentTreeNode.vue'
import type { EnergyEdgeData, LifeTreeItem, TalentBranch, TalentNodeData } from './talentTreeTypes'

export type { LifeTreeItem } from './talentTreeTypes'

const props = defineProps<{ items: LifeTreeItem[]; selected?: string; targetRole?: string }>()
const emit = defineEmits<{ select: [item: LifeTreeItem] }>()

const nodes = shallowRef<Node<TalentNodeData>[]>([])
const edges = shallowRef<Edge<EnergyEdgeData>[]>([])
const flowShell = ref<HTMLElement | null>(null)
const layoutMode = ref<'wide' | 'medium' | 'compact'>('wide')
const nodeIdBySkill = new Map<string, string>()
const { fitView, zoomIn, zoomOut, setNodes, setEdges } = useVueFlow('career-talent-tree')
let resizeObserver: ResizeObserver | null = null
let fitTimer: number | undefined

const branchConfig: Array<{ key: TalentBranch; label: string }> = [
  { key: 'professional', label: '专业技能' },
  { key: 'engineering', label: '工程实践' },
  { key: 'general', label: '通用能力' },
]

const layoutProfiles = {
  wide: { branchStep: 300, laneOffset: 76, tripleLaneStep: 162, columns: 2, branchY: 178, skillY: 330, rowGap: 116, minZoom: .45, fitMinZoom: .52, fitMaxZoom: .96 },
  medium: { branchStep: 250, laneOffset: 50, tripleLaneStep: 146, columns: 2, branchY: 168, skillY: 312, rowGap: 110, minZoom: .36, fitMinZoom: .42, fitMaxZoom: .9 },
  compact: { branchStep: 156, laneOffset: 0, tripleLaneStep: 0, columns: 1, branchY: 150, skillY: 278, rowGap: 96, minZoom: .3, fitMinZoom: .36, fitMaxZoom: .82 },
} as const

const currentLayout = computed(() => layoutProfiles[layoutMode.value])

function branchPositions(count: number) {
  const step = currentLayout.value.branchStep
  if (count <= 1) return [0]
  if (count === 2) return [-step / 2, step / 2]
  return [-step, 0, step]
}

function branchFor(item: LifeTreeItem): TalentBranch {
  if (/工程|部署|运维|Docker|Kubernetes|Linux|Git|CI\/CD/i.test(`${item.category} ${item.name}`)) return 'engineering'
  if (/通用|沟通|表达|协作|管理|需求|领导|创新|学习/i.test(`${item.category} ${item.name}`)) return 'general'
  return 'professional'
}

function statusLabel(status: LifeTreeItem['status']) {
  if (status === 'mastered') return '已激活'
  if (status === 'growing') return '升级中'
  return '待解锁'
}

function statusRank(status: LifeTreeItem['status']) {
  return status === 'mastered' ? 0 : status === 'growing' ? 1 : 2
}

function buildTree() {
  nodeIdBySkill.clear()
  const sourceItems = props.items.length
    ? props.items.slice(0, 18)
    : [{ name: '建立个人能力档案', score: 35, category: '通用能力', status: 'growing' as const }]
  const activated = sourceItems.filter((item) => item.status !== 'missing').length
  const activeBranches = branchConfig
    .map((branch) => ({ ...branch, items: sourceItems.filter((item) => branchFor(item) === branch.key) }))
    .filter((branch) => branch.items.length)
  const branchXs = branchPositions(activeBranches.length)
  const layout = currentLayout.value
  const nextNodes: Node<TalentNodeData>[] = [{
    id: 'career-core',
    type: 'talent',
    position: { x: -95, y: 0 },
    sourcePosition: Position.Bottom,
    targetPosition: Position.Top,
    data: {
      kind: 'core',
      label: props.targetRole && props.targetRole !== '尚未选择' ? props.targetRole : '目标岗位',
      subtitle: `${activated} / ${sourceItems.length} 个节点已激活`,
      progress: sourceItems.length ? activated / sourceItems.length * 100 : 0,
      status: activated ? 'growing' : 'missing',
      branch: 'professional',
    },
  }]
  const nextEdges: Edge<EnergyEdgeData>[] = []

  activeBranches.forEach((branch, branchIndex) => {
    const branchItems = branch.items
      .sort((a, b) => statusRank(a.status) - statusRank(b.status) || b.score - a.score)
    const branchX = branchXs[branchIndex] ?? 0
    const branchColumns = activeBranches.length === 1
      ? layoutMode.value === 'compact' ? 2 : 3
      : layout.columns
    const branchLaneOffset = layoutMode.value === 'compact' && branchColumns === 2 ? 76 : layout.laneOffset

    const branchId = `branch-${branch.key}`
    const branchStatus: LifeTreeItem['status'] = branchItems.every((item) => item.status === 'mastered') ? 'mastered' : 'growing'
    nextNodes.push({
      id: branchId,
      type: 'talent',
      position: { x: branchX - 62, y: layout.branchY },
      sourcePosition: Position.Bottom,
      targetPosition: Position.Top,
      data: {
        kind: 'branch',
        label: branch.label,
        subtitle: `${branchItems.filter((item) => item.status !== 'missing').length} / ${branchItems.length} 激活`,
        progress: branchItems.reduce((sum, item) => sum + item.score, 0) / branchItems.length,
        status: branchStatus,
        branch: branch.key,
      },
    })
    nextEdges.push({
      id: `edge-core-${branch.key}`,
      source: 'career-core',
      target: branchId,
      type: 'energy',
      selectable: false,
      data: { status: branchStatus },
    })

    branchItems.forEach((item, index) => {
      const lane = index % branchColumns
      const row = Math.floor(index / branchColumns)
      const laneX = branchColumns === 1
        ? 0
        : branchColumns === 3
          ? (lane - 1) * layout.tripleLaneStep
          : lane === 0 ? -branchLaneOffset : branchLaneOffset
      const nodeId = `skill-${branch.key}-${index}`
      const parentId = row === 0 ? branchId : `skill-${branch.key}-${index - branchColumns}`
      nodeIdBySkill.set(item.name, nodeId)
      nextNodes.push({
        id: nodeId,
        type: 'talent',
        position: { x: branchX + laneX - 74, y: layout.skillY + row * layout.rowGap },
        sourcePosition: Position.Bottom,
        targetPosition: Position.Top,
        data: {
          kind: 'skill',
          label: item.name,
          subtitle: `${statusLabel(item.status)} · ${Math.round(item.score)}%`,
          progress: item.score,
          status: item.status,
          branch: branch.key,
          selected: item.name === props.selected,
          item,
        },
      })
      nextEdges.push({
        id: `edge-${parentId}-${nodeId}`,
        source: parentId,
        target: nodeId,
        type: 'energy',
        selectable: false,
        data: { status: item.status },
      })
    })
  })

  nodes.value = nextNodes
  edges.value = nextEdges
  setNodes(nextNodes)
  setEdges(nextEdges)
  markSelectedPath(props.selected)
  scheduleFitView(350)
}

function scheduleFitView(duration = 320) {
  if (fitTimer) window.clearTimeout(fitTimer)
  nextTick(() => {
    fitTimer = window.setTimeout(() => {
      const layout = currentLayout.value
      fitView({ padding: layoutMode.value === 'compact' ? .12 : .08, minZoom: layout.fitMinZoom, maxZoom: layout.fitMaxZoom, duration })
    }, 60)
  })
}

function markSelectedPath(selected?: string) {
  const selectedId = selected ? nodeIdBySkill.get(selected) : undefined
  const activeNodes = new Set<string>()
  if (selectedId) {
    let current: string | undefined = selectedId
    while (current) {
      activeNodes.add(current)
      let parent: string | undefined
      for (const edge of edges.value) {
        if (edge.target === current) {
          parent = edge.source
          break
        }
      }
      current = parent
    }
  }
  const updatedNodes: Node<TalentNodeData>[] = []
  for (const node of nodes.value) {
    const data = node.data as TalentNodeData
    updatedNodes.push({ ...node, data: { ...data, selected: node.id === selectedId } })
  }
  nodes.value = updatedNodes

  const updatedEdges: Edge<EnergyEdgeData>[] = []
  for (const edge of edges.value) {
    const data = edge.data as EnergyEdgeData
    updatedEdges.push({
      ...edge,
      data: { ...data, active: activeNodes.has(edge.source) && activeNodes.has(edge.target) },
    })
  }
  edges.value = updatedEdges
}

function focusSelected(selected?: string) {
  markSelectedPath(selected)
  const nodeId = selected ? nodeIdBySkill.get(selected) : undefined
  if (!nodeId) return
  nextTick(() => fitView({ nodes: [nodeId], padding: 3, minZoom: .9, maxZoom: 1.12, duration: 560 }))
}

function handleNodeClick({ node }: { node: GraphNode<TalentNodeData> }) {
  if (node.data.item) emit('select', node.data.item)
}

function resetView() {
  scheduleFitView(420)
}

watch(
  () => `${props.targetRole}|${props.items.map((item) => `${item.name}:${item.score}:${item.status}`).join('|')}`,
  buildTree,
  { immediate: true },
)
watch(() => props.selected, focusSelected)

onMounted(() => {
  resizeObserver = new ResizeObserver(([entry]) => {
    const width = entry.contentRect.width
    const nextMode = width < 480 ? 'compact' : width < 760 ? 'medium' : 'wide'
    if (nextMode !== layoutMode.value) {
      layoutMode.value = nextMode
      buildTree()
      return
    }
    scheduleFitView(180)
  })
  if (flowShell.value) resizeObserver.observe(flowShell.value)
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  if (fitTimer) window.clearTimeout(fitTimer)
})
</script>

<style scoped>
.life-tree { position: relative; width: 100%; height: 100%; min-height: 560px; overflow: hidden; background: transparent; box-shadow: none; }
.life-tree__flow-shell { position: absolute; inset: 12px clamp(220px, 18vw, 278px) 42px; min-width: 0; overflow: hidden; }
.life-tree :deep(.vue-flow) { background: transparent; }
.life-tree :deep(.vue-flow__pane) { cursor: grab; }
.life-tree :deep(.vue-flow__pane.dragging) { cursor: grabbing; }
.life-tree :deep(.vue-flow__node) { border: 0; padding: 0; background: transparent; box-shadow: none; }
.life-tree :deep(.vue-flow__edge) { pointer-events: none; }
.life-tree :deep(.vue-flow__selectionpane) { cursor: grab; }
.life-tree__controls { position: absolute; bottom: 0; left: 50%; z-index: 5; display: flex; overflow: hidden; border: 1px solid rgba(78, 200, 255, .15); border-radius: 6px; background: rgba(8, 42, 92, 0.4); transform: translateX(-50%); backdrop-filter: blur(6px); }
.life-tree__controls button { display: grid; place-items: center; width: 34px; height: 32px; border: 0; border-right: 1px solid rgba(69, 197, 245, .15); color: #6eabc6; background: transparent; cursor: pointer; }
.life-tree__controls button:last-child { border-right: 0; }
.life-tree__controls button:hover { color: #71e9ff; background: rgba(31, 139, 191, .18); }
@media (max-width: 1320px) { .life-tree__flow-shell { inset-right: 240px; inset-left: 240px; } }
@media (max-width: 900px) { .life-tree__flow-shell { inset: 390px 10px 238px; min-width: 0; } }
@media (max-width: 720px) { .life-tree { min-height: 1080px; }.life-tree__flow-shell { inset: 382px 0 230px; } }
</style>

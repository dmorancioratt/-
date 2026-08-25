import { defineStore } from 'pinia'
import { markRaw } from 'vue'
import type { FlowNode, FlowEdge, NodeStatus, StageLog, DocumentInfo, TestRunResponse, WorkflowConfig } from '@/types/workflow'
import { buildDefaultEdges, buildDefaultNodes } from '@/utils/workflowTemplate'
import { api } from '@/api/http'

const DRAFT_KEY = 'workflow_draft_v2'

interface WorkflowState {
  configId: number | null
  configName: string
  nodes: FlowNode[]
  edges: FlowEdge[]
  selectedNodeId: string | null
  drawerOpen: boolean
  docs: DocumentInfo[]
  docsLoading: boolean
  runtime: {
    running: boolean
    stageIndex: number
    logs: StageLog[]
    lastResult: TestRunResponse | null
  }
  saving: boolean
  testDialogVisible: boolean
  testQuestion: string
}

export const useWorkflowStore = defineStore('workflow', {
  state: (): WorkflowState => ({
    configId: null,
    configName: '默认 RAG 流程',
    nodes: buildDefaultNodes(),
    edges: buildDefaultEdges(),
    selectedNodeId: null,
    drawerOpen: false,
    docs: [],
    docsLoading: false,
    runtime: {
      running: false,
      stageIndex: 0,
      logs: [],
      lastResult: null,
    },
    saving: false,
    testDialogVisible: false,
    testQuestion: '',
  }),

  getters: {
    selectedNode: (state) => state.nodes.find((n) => n.id === state.selectedNodeId) || null,
    totalDocs: (state) => state.docs.length,
    totalChunks: (state) => state.docs.reduce((acc, d) => acc + d.chunk_count, 0),
  },

  actions: {
    resetLayout() {
      this.nodes = buildDefaultNodes()
      this.edges = buildDefaultEdges()
      this.configId = null
      this.configName = '默认 RAG 流程'
      this.persistDraft()
    },

    openDrawer(nodeId: string) {
      this.selectedNodeId = nodeId
      this.drawerOpen = true
    },

    closeDrawer() {
      this.drawerOpen = false
    },

    setNodeStatus(nodeId: string, status: NodeStatus, output?: string) {
      const node = this.nodes.find((n) => n.id === nodeId)
      if (node) {
        node.data.status = status
        if (output !== undefined) node.data.output = output
      }
    },

    setNodeConfig(nodeId: string, patch: Record<string, any>) {
      const node = this.nodes.find((n) => n.id === nodeId)
      if (node) {
        node.data.config = { ...node.data.config, ...patch }
        this.persistDraft()
      }
    },

    updateNodePosition(nodeId: string, position: { x: number; y: number }) {
      const node = this.nodes.find((n) => n.id === nodeId)
      if (node) {
        node.position = position
        this.persistDraft()
      }
    },

    addEdge(source: string, target: string) {
      const exists = this.edges.some((e) => e.source === source && e.target === target)
      if (exists) return
      if (source === target) return
      this.edges.push({
        id: `edge-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
        source,
        target,
        animated: false,
      })
      this.persistDraft()
    },

    removeEdge(edgeId: string) {
      this.edges = this.edges.filter((e) => e.id !== edgeId)
      this.persistDraft()
    },

    deleteNode(nodeId: string) {
      this.nodes = this.nodes.filter((n) => n.id !== nodeId)
      this.edges = this.edges.filter((e) => e.source !== nodeId && e.target !== nodeId)
      if (this.selectedNodeId === nodeId) this.selectedNodeId = null
      this.persistDraft()
    },

    setNodes(nodes: FlowNode[], edges: FlowEdge[]) {
      this.nodes = nodes
      this.edges = edges
    },

    async fetchDocs() {
      this.docsLoading = true
      try {
        const list = await api.workflowDocsList()
        this.docs = Array.isArray(list) ? list : []
      } catch (e) {
        this.docs = []
      } finally {
        this.docsLoading = false
      }
    },

    async uploadDoc(file: File) {
      const doc = await api.workflowDocsUpload(file)
      await this.fetchDocs()
      return doc
    },

    async chunkDoc(docId: number, chunkSize = 500, chunkOverlap = 50) {
      const res = await api.workflowDocsChunk(docId, { chunk_size: chunkSize, chunk_overlap: chunkOverlap })
      await this.fetchDocs()
      return res
    },

    async deleteDoc(docId: number) {
      await api.workflowDocsDelete(docId)
      await this.fetchDocs()
    },

    async save(name: string): Promise<WorkflowConfig> {
      this.saving = true
      try {
        const payload = {
          name,
          is_default: true,
          graph_json: { nodes: this.nodes, edges: this.edges },
          node_settings: this.collectSettings(),
        }
        if (this.configId) {
          const cfg = await api.workflowConfigsUpdate(this.configId, payload)
          this.configId = cfg.id
          this.configName = cfg.name
          return cfg
        } else {
          const cfg = await api.workflowConfigsSave(payload)
          this.configId = cfg.id
          this.configName = cfg.name
          return cfg
        }
      } finally {
        this.saving = false
      }
    },

    async load(configId: number) {
      const cfg = await api.workflowConfigsGet(configId)
      this.configId = cfg.id
      this.configName = cfg.name
      const graph = (cfg.graph_json || {}) as { nodes?: FlowNode[]; edges?: FlowEdge[] }
      this.nodes = graph.nodes || buildDefaultNodes()
      this.edges = graph.edges || buildDefaultEdges()
    },

    async listConfigs() {
      return api.workflowConfigsList()
    },

    async testRun(question: string, topK = 5): Promise<TestRunResponse> {
      if (!this.configId) throw new Error('请先保存工作流配置')
      this.runtime.running = true
      this.runtime.logs = []
      this.runtime.lastResult = null
      // 先把所有节点重置为 idle
      this.nodes.forEach((n) => (n.data.status = 'idle'))

      const result = await api.workflowConfigTestRun(this.configId, { question, top_k: topK })
      // 模拟流转：依次把每个 stage 反映到对应节点
      const kindToStage = [
        ['问题解析', 'parser'],
        ['本地知识库', 'knowledge'],
        ['Top-K 检索', 'retrieve'],
        ['向量检索', 'vector'],
        ['大模型生成', 'llm'],
        ['幻觉检测', 'guard'],
        ['引用校验', 'citation'],
      ] as Array<[string, string]>
      for (const [stageLabel, kind] of kindToStage) {
        const node = this.nodes.find((n) => n.data.kind === kind)
        if (node) node.data.status = 'done'
        const log = result.stages_log?.find((s) => s.stage === stageLabel)
        if (node && log) node.data.output = log.output
      }
      this.runtime.logs = result.stages_log || []
      this.runtime.lastResult = result
      this.runtime.running = false
      return result
    },

    collectSettings(): Record<string, any> {
      const out: Record<string, any> = {}
      this.nodes.forEach((n) => {
        out[n.data.kind] = { ...n.data.config }
      })
      return out
    },

    persistDraft() {
      try {
        const draft = {
          configId: this.configId,
          configName: this.configName,
          nodes: this.nodes,
          edges: this.edges,
        }
        localStorage.setItem(DRAFT_KEY, JSON.stringify(draft))
      } catch {
        // localStorage 写入失败不阻塞 UI
      }
    },

    loadDraft() {
      try {
        const raw = localStorage.getItem(DRAFT_KEY)
        if (!raw) return
        const draft = JSON.parse(raw)
        if (draft.nodes && Array.isArray(draft.nodes)) {
          this.nodes = markRawArr(draft.nodes)
          this.edges = draft.edges || []
          this.configId = draft.configId || null
          this.configName = draft.configName || '默认 RAG 流程'
        }
      } catch {
        // 草稿损坏忽略
      }
    },

    openTestDialog(question = '') {
      this.testQuestion = question
      this.testDialogVisible = true
    },

    closeTestDialog() {
      this.testDialogVisible = false
    },
  },
})

function markRawArr<T>(arr: T[]): T[] {
  return arr.map((item) => (item as any).__v_skip ? item : markRaw(item))
}
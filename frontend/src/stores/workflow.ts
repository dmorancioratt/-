import { defineStore } from 'pinia'
import { markRaw } from 'vue'
import type { FlowNode, FlowEdge, NodeStatus, StageLog, DocumentInfo, TestRunResponse, WorkflowConfig, NodeKind } from '@/types/workflow'
import { buildDefaultEdges, buildDefaultNodes, NODE_KIND_META } from '@/utils/workflowTemplate'
import { api } from '@/api/http'

const DRAFT_KEY = 'workflow_draft_v5'

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
    progress: number
    logs: StageLog[]
    lastResult: TestRunResponse | null
    lastRunAt: string | null
  }
  saving: boolean
  lastSavedAt: string | null
  testDialogVisible: boolean
  testQuestion: string
}

export const useWorkflowStore = defineStore('workflow', {
  state: (): WorkflowState => ({
    configId: null,
    configName: '默认 RAG 流程',
    nodes: buildDefaultNodes(),
    edges: buildDefaultEdges(),
    selectedNodeId: 'node-input',
    drawerOpen: false,
    docs: [],
    docsLoading: false,
    runtime: {
      running: false,
      stageIndex: 0,
      progress: 0,
      logs: [],
      lastResult: null,
      lastRunAt: null,
    },
    saving: false,
    lastSavedAt: null,
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

    addNode(node: FlowNode) {
      this.nodes.push(node)
      this.persistDraft()
    },

    addNodeByKind(kind: NodeKind, position: { x: number; y: number }) {
      const meta = NODE_KIND_META[kind]
      const node: FlowNode = {
        id: `node-${kind}-${Date.now()}`,
        type: kind,
        position,
        data: {
          kind,
          label: meta.label,
          description: meta.description,
          status: 'idle',
          config: { ...meta.config },
        },
      }
      this.addNode(node)
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
          this.lastSavedAt = cfg.updated_at || new Date().toISOString()
          this.persistDraft()
          return cfg
        } else {
          let cfg: any
          try {
            cfg = await api.workflowConfigsSave(payload)
          } catch (e: any) {
            // 409：名称已存在 → 自动切换为更新同名配置，而不是报错
            if (e?.response?.status === 409) {
              const existing = ((await this.listConfigs()) || []).find((c: any) => c.name === name)
              if (!existing) throw e
              cfg = await api.workflowConfigsUpdate(existing.id, payload)
            } else {
              throw e
            }
          }
          this.configId = cfg.id
          this.configName = cfg.name
          this.lastSavedAt = cfg.updated_at || new Date().toISOString()
          this.persistDraft()
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
      this.lastSavedAt = cfg.updated_at || null
      const graph = (cfg.graph_json || {}) as { nodes?: FlowNode[]; edges?: FlowEdge[] }
      this.nodes = graph.nodes || buildDefaultNodes()
      this.edges = graph.edges || buildDefaultEdges()
    },

    async listConfigs() {
      return api.workflowConfigsList()
    },

    async ensureConfig() {
      // 页面加载时：若无关联配置，自动关联后端已有配置（优先默认），避免反复新建导致重名冲突
      if (this.configId) return
      try {
        const configs = (await this.listConfigs()) || []
        if (!configs.length) return
        const target = configs.find((c: any) => c.is_default) || configs[0]
        if (target?.id) {
          this.configId = target.id
          this.configName = target.name
        }
      } catch {
        // 关联失败不阻塞
      }
    },

    async testRun(question: string, topK = 5): Promise<TestRunResponse> {
      if (!this.configId) throw new Error('请先保存工作流配置')
      this.runtime.running = true
      this.runtime.logs = []
      this.runtime.lastResult = null
      // 先把所有节点重置为 idle
      this.nodes.forEach((n) => (n.data.status = 'idle'))

      try {
        const result = await api.workflowConfigTestRun(this.configId, { question, top_k: topK })
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
          const log = result.stages_log?.find((s: StageLog) => s.stage === stageLabel)
          if (node && log) node.data.output = log.output
        }
        this.runtime.logs = result.stages_log || []
        this.runtime.lastResult = result
        return result
      } finally {
        this.runtime.running = false
        this.runtime.lastRunAt = new Date().toISOString()
      }
    },

    async testRunStream(question: string, topK = 5): Promise<TestRunResponse | null> {
      if (!this.configId) throw new Error('请先保存工作流配置')
      this.runtime.running = true
      this.runtime.progress = 0
      this.runtime.stageIndex = 0
      this.runtime.logs = []
      this.runtime.lastResult = null
      this.nodes.forEach((n) => (n.data.status = 'idle'))

      const base = import.meta.env.VITE_API_BASE || ''
      const token = localStorage.getItem('auth_token')
      try {
        const res = await fetch(`${base}/api/workflow/configs/${this.configId}/test-stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({ question, top_k: topK }),
        })
        if (!res.ok || !res.body) throw new Error('运行失败，请稍后重试')

        const reader = res.body.getReader()
        const decoder = new TextDecoder()
        let buf = ''
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          buf += decoder.decode(value, { stream: true })
          let sep: number
          while ((sep = buf.indexOf('\n\n')) >= 0) {
            const raw = buf.slice(0, sep)
            buf = buf.slice(sep + 2)
            const line = raw.split('\n').find((l) => l.startsWith('data:'))
            if (!line) continue
            let payload: any
            try {
              payload = JSON.parse(line.slice(5).trim())
            } catch {
              continue
            }
            this.applyStreamEvent(payload)
          }
        }
        return this.runtime.lastResult
      } finally {
        this.runtime.running = false
        this.runtime.lastRunAt = new Date().toISOString()
      }
    },

    applyStreamEvent(payload: any) {
      if (payload.event === 'stage') {
        this.runtime.stageIndex = payload.index ?? 0
        this.runtime.progress = payload.progress ?? 0
        const existing = this.runtime.logs.find((l) => l.stage === payload.stage)
        if (existing) {
          existing.status = payload.status
          existing.output = payload.output
        } else {
          this.runtime.logs.push({ stage: payload.stage, status: payload.status, output: payload.output })
        }
        const kind = this.stageToKind(payload.stage)
        const node = this.nodes.find((n) => n.data.kind === kind)
        if (node) {
          const valid: NodeStatus[] = ['idle', 'running', 'done', 'error', 'warn']
          node.data.status = valid.includes(payload.status) ? (payload.status as NodeStatus) : 'idle'
          node.data.output = payload.output
        }
      } else if (payload.event === 'result') {
        this.runtime.logs = payload.stages_log || this.runtime.logs
        this.runtime.lastResult = {
          answer: payload.answer ?? null,
          evidence: payload.evidence || [],
          confidence: payload.confidence ?? 0,
          stages_log: payload.stages_log || [],
        }
        this.runtime.progress = 100
        this.runtime.running = false
      }
    },

    stageToKind(stage: string): string {
      const map: Record<string, string> = {
        '问题解析': 'parser',
        '本地知识库': 'knowledge',
        'Top-K 检索': 'retrieve',
        '向量检索': 'vector',
        '大模型生成': 'llm',
        '幻觉检测': 'guard',
        '引用校验': 'citation',
      }
      return map[stage] || ''
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

    exportJSON() {
      return {
        nodes: this.nodes,
        edges: this.edges,
        configName: this.configName,
        configId: this.configId,
      }
    },

    importJSON(payload: unknown) {
      if (!payload || typeof payload !== 'object') throw new Error('JSON 内容不是有效对象')
      const data = payload as Record<string, any>
      if (!Array.isArray(data.nodes) || !Array.isArray(data.edges)) {
        throw new Error('JSON 必须包含 nodes 和 edges 数组')
      }
      if (data.nodes.some((node: any) => !node?.id || !node?.data?.kind || !node?.position)) {
        throw new Error('节点数据缺少 id、kind 或 position')
      }
      this.nodes = markRawArr(data.nodes)
      this.edges = data.edges
      this.configId = null
      this.configName = typeof data.configName === 'string' && data.configName.trim()
        ? `${data.configName.trim()}（导入）`
        : '导入的 RAG 流程'
      this.persistDraft()
    },
  },
})

function markRawArr<T>(arr: T[]): T[] {
  return arr.map((item) => (item as any).__v_skip ? item : markRaw(item as object) as T)
}

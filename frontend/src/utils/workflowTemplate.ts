import type { FlowNode, FlowEdge, NodeKind, FlowNodeData } from '@/types/workflow'

const NODES_PER_ROW = 4
const X_STEP = 240
const Y_STEP = 160
const X_START = 80
const Y_START = 80

const KIND_LIST: NodeKind[] = [
  'input',
  'parser',
  'knowledge',
  'chunker',
  'embedding',
  'vector',
  'retrieve',
  'relevance',
  'llm',
  'guard',
  'citation',
  'output',
]

const KIND_META: Record<NodeKind, { label: string; description: string; config: Record<string, any> }> = {
  input: {
    label: '用户问题',
    description: '接收用户原始提问',
    config: { placeholder: '请输入你的问题...' },
  },
  parser: {
    label: '问题解析',
    description: '意图识别 / 实体抽取',
    config: { method: 'rule', timeout_ms: 200 },
  },
  knowledge: {
    label: '本地知识库',
    description: '用户上传的文档库',
    config: { docs: [] },
  },
  chunker: {
    label: '文档切片',
    description: '将文档切成 chunks',
    config: { chunk_size: 500, chunk_overlap: 50 },
  },
  embedding: {
    label: 'Embedding',
    description: '向量化',
    config: { model: 'bge-small-zh', dim: 512 },
  },
  vector: {
    label: '向量数据库',
    description: 'faiss 索引',
    config: { index_path: 'data/rag/user_docs.index', metric: 'cosine' },
  },
  retrieve: {
    label: 'Top-K 检索',
    description: '相似度召回',
    config: { top_k: 5 },
  },
  relevance: {
    label: '相关性判断',
    description: '过滤低质内容',
    config: { threshold: 0.75 },
  },
  llm: {
    label: '大模型生成',
    description: '基于上下文生成回答',
    config: { model: 'deepseek-v4-flash', temperature: 0.2, max_tokens: 1024 },
  },
  guard: {
    label: '幻觉检测',
    description: '事实一致性校验',
    config: { threshold: 0.72 },
  },
  citation: {
    label: '引用校验',
    description: '标注引用来源',
    config: { min_sources: 1 },
  },
  output: {
    label: '最终回答',
    description: '返回用户',
    config: {},
  },
}

export function buildDefaultNodes(): FlowNode[] {
  return KIND_LIST.map((kind, idx) => {
    const meta = KIND_META[kind]
    const row = Math.floor(idx / NODES_PER_ROW)
    const col = idx % NODES_PER_ROW
    const data: FlowNodeData = {
      kind,
      label: meta.label,
      description: meta.description,
      status: 'idle',
      config: { ...meta.config },
    }
    return {
      id: `node-${kind}`,
      type: `node-${kind}`,
      position: { x: X_START + col * X_STEP, y: Y_START + row * Y_STEP },
      data,
    }
  })
}

export function buildDefaultEdges(): FlowEdge[] {
  const edges: FlowEdge[] = []
  for (let i = 0; i < KIND_LIST.length - 1; i++) {
    edges.push({
      id: `edge-${i}`,
      source: `node-${KIND_LIST[i]}`,
      target: `node-${KIND_LIST[i + 1]}`,
      animated: false,
    })
  }
  return edges
}

export const NODE_KIND_META = KIND_META
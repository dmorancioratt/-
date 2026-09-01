export type NodeKind =
  | 'input'
  | 'parser'
  | 'knowledge'
  | 'chunker'
  | 'embedding'
  | 'vector'
  | 'retrieve'
  | 'relevance'
  | 'llm'
  | 'guard'
  | 'citation'
  | 'output'

export type NodeStatus = 'idle' | 'running' | 'done' | 'error' | 'warn'

export interface FlowNodeData {
  kind: NodeKind
  label: string
  description?: string
  status: NodeStatus
  output?: string
  config: Record<string, any>
}

export interface FlowNode {
  id: string
  type: string
  position: { x: number; y: number }
  data: FlowNodeData
}

export interface FlowEdge {
  id: string
  source: string
  target: string
  animated?: boolean
}

export interface WorkflowConfig {
  id?: number
  name: string
  is_default?: boolean
  graph_json: {
    nodes: FlowNode[]
    edges: FlowEdge[]
  }
  node_settings: Record<string, any>
}

export interface DocumentInfo {
  id: number
  filename: string
  file_type: string
  char_count: number
  chunk_count: number
  indexed: boolean
  created_at: string
}

export interface ChunkRequest {
  chunk_size?: number
  chunk_overlap?: number
}

export interface ChunkResponse {
  document_id: number
  chunk_count: number
  chunks_preview: string[]
}

export interface TestRunRequest {
  question: string
  top_k?: number
}

export interface TestRunResponse {
  answer: string | null
  evidence: Array<{
    chunk_id: number
    text: string
    score: number
    source_type: string
    ref_id: number
  }>
  confidence: number
  stages_log: Array<{
    stage: string
    status: string
    output: string
  }>
}

export interface StageLog {
  stage: string
  status: NodeStatus | string
  output: string
}

export interface RagSourceStatus {
  source_type: string
  status: string
  chunk_count: number
  started_at?: string
  completed_at?: string | null
  error_message?: string
}

export interface RagEngineStatus {
  embedder: {
    model_name: string
    dim: number
    is_fake: boolean
  }
  sources: RagSourceStatus[]
}
// ============================================================================
// API Request/Response Type Definitions
// Maps 1:1 to backend Pydantic schemas
// ============================================================================

// === Generic Response Wrapper ===
export interface ApiResponse<T = unknown> {
  status: number
  message: string
  data: T
}

// === Request Types ===

export interface SearchRequest {
  query: string
  top_k: number
  use_hybrid: boolean
}

export interface ChatRequest {
  query: string
  top_k: number
  conversation_id?: string | null
}

// === Response Data Types ===

export interface SearchResult {
  entry_id: string
  title: string
  page: number | null
  chunk_id: string
  content: string
  score: number
  retrieval_method: string
}

export interface SearchData {
  results: SearchResult[]
  total: number
  query: string
  retrieval_method: string
}

export interface CitedSource {
  entry_id: string
  title: string
  page: number | null
  excerpt: string
}

export type ConfidenceLevel = 'high' | 'medium' | 'low' | 'not_found'

export interface ChatData {
  answer: string
  sources: CitedSource[]
  confidence: ConfidenceLevel
  query: string
}

export interface HealthData {
  status: string
  milvus: string
}

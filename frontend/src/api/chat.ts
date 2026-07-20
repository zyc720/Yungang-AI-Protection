// POST /api/chat — Full RAG pipeline with LLM generation
import client from './client'
import type { ChatRequest, ChatData } from '@/types/api'

export function chatQuery(params: ChatRequest): Promise<ChatData> {
  return client.post('/api/chat', params) as Promise<ChatData>
}

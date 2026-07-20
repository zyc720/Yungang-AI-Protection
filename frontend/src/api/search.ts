// POST /api/search — Pure document retrieval
import client from './client'
import type { SearchRequest, SearchData } from '@/types/api'

export function searchDocuments(params: SearchRequest): Promise<SearchData> {
  return client.post('/api/search', params) as Promise<SearchData>
}

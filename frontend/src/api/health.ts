// GET /api/health — Backend health check
import client from './client'
import type { HealthData } from '@/types/api'

export function healthCheck(): Promise<HealthData> {
  return client.get('/api/health') as Promise<HealthData>
}

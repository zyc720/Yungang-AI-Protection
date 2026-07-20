// ============================================================================
// Axios Client — configured instance with interceptors
// ============================================================================

import axios from 'axios'
import type { AxiosInstance, AxiosResponse } from 'axios'
import type { ApiResponse } from '@/types/api'
import { ApiError } from './errors'

// In development, the Vite proxy handles /api -> backend.
// In production, same-origin deployment means /api works directly.
const client: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// --- Request Interceptor ---
client.interceptors.request.use(
  (config) => {
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.debug(`[API] ${config.method?.toUpperCase()} ${config.url}`)
    }
    return config
  },
  (error) => Promise.reject(error),
)

// --- Response Interceptor ---
client.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const body = response.data

    // The backend wraps everything in { status, message, data }
    // Status 200 = success, unwrap the data field.
    if (body && body.status === 200) {
      return body.data as unknown as AxiosResponse
    }

    // Non-200 status from backend
    throw new ApiError(
      body?.status || response.status,
      body?.message || 'Unknown error',
    )
  },
  (error) => {
    if (error instanceof ApiError) {
      throw error
    }

    // Network error, timeout, etc.
    if (error.code === 'ECONNABORTED') {
      throw new ApiError(0, '请求超时，请稍后重试')
    }
    if (!error.response) {
      throw new ApiError(0, '无法连接到服务器，请检查网络')
    }

    const status = error.response.status
    const data = error.response.data as ApiResponse | undefined
    throw new ApiError(
      status,
      data?.message || error.message || '服务器错误',
    )
  },
)

export default client

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { healthCheck } from '@/api/health'
import { HOT_ENTRIES } from '@/constants/hotEntries'
import type { HotEntry } from '@/types/dictionary'

/**
 * Global application state — lightweight, not tied to any single search session.
 */
export const useAppStore = defineStore('app', () => {
  const healthStatus = ref<'ok' | 'error' | 'loading'>('loading')
  const hotEntries = ref<HotEntry[]>([])

  /** Check backend connectivity on app mount. */
  async function checkHealth(): Promise<void> {
    healthStatus.value = 'loading'
    try {
      await healthCheck()
      healthStatus.value = 'ok'
    } catch {
      healthStatus.value = 'error'
    }
  }

  /** Load the curated hot entries (currently from constants). */
  function loadHotEntries(): void {
    hotEntries.value = HOT_ENTRIES
  }

  return {
    healthStatus,
    hotEntries,
    checkHealth,
    loadHotEntries,
  }
})

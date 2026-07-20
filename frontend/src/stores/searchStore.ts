import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { chatQuery as chatApi, searchDocuments as searchApi } from '@/api'
import type { ChatData, SearchData, ConfidenceLevel } from '@/types/api'
import type { DocumentViewEntry } from '@/types/dictionary'

/**
 * Central store for a single search session.
 *
 * Manages the complete lifecycle:
 *   search/chat request → loading → result display → document viewer
 */
export const useSearchStore = defineStore('search', () => {
  // --- Input State ---
  const query = ref('')
  const topK = ref(5)
  const useHybrid = ref(true)

  // --- Result State ---
  const isLoading = ref(false)
  const chatResult = ref<ChatData | null>(null)
  const searchResult = ref<SearchData | null>(null)
  const error = ref<string | null>(null)

  // --- Document Viewer State ---
  const selectedEntry = ref<DocumentViewEntry | null>(null)
  const isViewerOpen = ref(false)

  // --- Computed ---
  const confidence = computed<ConfidenceLevel | null>(() => {
    return chatResult.value?.confidence ?? null
  })

  const hasResults = computed<boolean>(() => {
    return chatResult.value !== null || searchResult.value !== null
  })

  // --- Actions ---

  /** Execute a full RAG chat query: retrieve + LLM generate. */
  async function doChat(q: string, k: number = 5): Promise<void> {
    query.value = q
    topK.value = k
    isLoading.value = true
    error.value = null
    chatResult.value = null
    searchResult.value = null

    try {
      const result = await chatApi({
        query: q,
        top_k: k,
      })
      chatResult.value = result
    } catch (e) {
      const msg = e instanceof Error ? e.message : '查询失败，请稍后重试'
      error.value = msg
    } finally {
      isLoading.value = false
    }
  }

  /** Execute a pure document search (no LLM). */
  async function doSearch(q: string, k: number = 5, hybrid: boolean = true): Promise<void> {
    query.value = q
    topK.value = k
    useHybrid.value = hybrid
    isLoading.value = true
    error.value = null
    searchResult.value = null

    try {
      const result = await searchApi({
        query: q,
        top_k: k,
        use_hybrid: hybrid,
      })
      searchResult.value = result
    } catch (e) {
      const msg = e instanceof Error ? e.message : '检索失败，请稍后重试'
      error.value = msg
    } finally {
      isLoading.value = false
    }
  }

  /** Open the document viewer for a specific entry. */
  function openViewer(entry: DocumentViewEntry): void {
    selectedEntry.value = entry
    isViewerOpen.value = true
  }

  /** Close the document viewer. */
  function closeViewer(): void {
    isViewerOpen.value = false
  }

  /** Clear all results and reset to initial state. */
  function clear(): void {
    query.value = ''
    chatResult.value = null
    searchResult.value = null
    error.value = null
    selectedEntry.value = null
    isViewerOpen.value = false
  }

  return {
    // State
    query,
    topK,
    useHybrid,
    isLoading,
    chatResult,
    searchResult,
    error,
    selectedEntry,
    isViewerOpen,
    // Computed
    confidence,
    hasResults,
    // Actions
    doChat,
    doSearch,
    openViewer,
    closeViewer,
    clear,
  }
})

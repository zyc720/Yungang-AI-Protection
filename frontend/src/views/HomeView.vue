<script setup lang="ts">
/**
 * HomeView — the single-page orchestrator for the Yungang e-Dictionary.
 *
 * Coordinates all sections: search bar, hot entries, AI answer display,
 * citation sources, and the document viewer drawer.
 */
import { ref, onMounted } from 'vue'
import { useSearchStore } from '@/stores/searchStore'
import { useAppStore } from '@/stores/appStore'
import type { DocumentViewEntry } from '@/types/dictionary'

import SearchBar from '@/components/SearchBar.vue'
import HotEntries from '@/components/HotEntries.vue'
import EmptyState from '@/components/EmptyState.vue'
import AnswerDisplay from '@/components/AnswerDisplay.vue'
import SourcesList from '@/components/SourcesList.vue'
import DocumentViewer from '@/components/DocumentViewer.vue'

const searchStore = useSearchStore()
const appStore = useAppStore()

// Ref for SourcesList component to call highlightSource()
const sourcesListRef = ref<InstanceType<typeof SourcesList> | null>(null)

// Local v-model for the search input
const searchInput = ref('')

const showEmpty = () => !searchStore.hasResults && !searchStore.isLoading

onMounted(() => {
  appStore.checkHealth()
  appStore.loadHotEntries()
})

/** Trigger a chat query when the user submits the search bar. */
async function handleSearch(query: string, topK: number, _useHybrid: boolean) {
  await searchStore.doChat(query, topK)
}

/** Populate search input when a hot entry is clicked, then search. */
async function handleHotEntrySelect(entryId: string) {
  searchInput.value = entryId
  await searchStore.doChat(entryId, 5)
}

/** Called when a citation badge is clicked in the answer text. */
function handleShowSource(title: string) {
  sourcesListRef.value?.highlightSource(title)
}

/** Open the document viewer for a cited source. */
function handleShowDocument(_entryId: string, title: string) {
  // Find the matching search result or use the chat sources to build an entry
  const results = searchStore.searchResult?.results ?? []
  const sources = searchStore.chatResult?.sources ?? []

  let entry: DocumentViewEntry | null = null

  // Try to find full content from search results
  const result = results.find(
    (r) => r.title === title,
  )
  if (result) {
    entry = {
      entry_id: result.entry_id,
      title: result.title,
      content: result.content,
      page: result.page,
      chunk_id: result.chunk_id,
    }
  } else {
    // Fallback: use the source excerpt from chat
    const source = sources.find(
      (s) => s.title === title,
    )
    if (source) {
      entry = {
        entry_id: source.entry_id,
        title: source.title,
        content: source.excerpt,
        page: source.page,
      }
    }
  }

  if (entry) {
    searchStore.openViewer(entry)
  }
}
</script>

<template>
  <div class="home">
    <main class="main-content">
      <!-- Section 1 & 2: Search Bar + Hot Entries -->
      <section class="search-section">
        <SearchBar
          v-model="searchInput"
          :loading="searchStore.isLoading"
          @search="handleSearch"
        />
        <HotEntries
          :entries="appStore.hotEntries"
          @select="handleHotEntrySelect"
        />
      </section>

      <!-- Error message -->
      <div v-if="searchStore.error" class="error-banner">
        <span class="error-icon">!</span>
        <span>{{ searchStore.error }}</span>
        <button class="error-dismiss" @click="searchStore.error = null">✕</button>
      </div>

      <!-- Section 3: AI Answer -->
      <section v-if="searchStore.chatResult" class="answer-section">
        <AnswerDisplay
          :text="searchStore.chatResult.answer"
          :confidence="searchStore.chatResult.confidence"
          @show-source="handleShowSource"
        />
      </section>

      <!-- Section 4: Cited Sources -->
      <section v-if="searchStore.chatResult?.sources?.length">
        <SourcesList
          ref="sourcesListRef"
          :sources="searchStore.chatResult.sources"
          @show-document="handleShowDocument"
        />
      </section>

      <!-- Loading skeleton -->
      <section v-if="searchStore.isLoading" class="loading-section">
        <div class="skeleton-block">
          <div class="skeleton-line skeleton-line--short"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line skeleton-line--medium"></div>
        </div>
      </section>

      <!-- Empty state: no search has been made -->
      <EmptyState v-if="showEmpty()" />
    </main>

    <!-- Section 5: Document Viewer (slide-out drawer) -->
    <DocumentViewer />
  </div>
</template>

<style scoped lang="scss">
.home {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  max-width: $max-content-width;
  width: 100%;
  margin: 0 auto;
  padding: $space-xl $space-lg $space-2xl;
}

.search-section {
  margin-bottom: $space-xl;
}

.answer-section {
  animation: fadeIn 0.4s ease;
}

.loading-section {
  margin-top: $space-xl;
}

// Skeleton loader
.skeleton-block {
  padding: $space-xl;
  background: $color-bg-card;
  border-radius: $radius-lg;
  border: 1px solid $color-border;
}

.skeleton-line {
  height: 16px;
  background: linear-gradient(90deg, $color-border 25%, $color-bg 50%, $color-border 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: $radius-sm;
  margin-bottom: $space-md;

  &--short { width: 40%; }
  &--medium { width: 70%; }
}

// Error banner
.error-banner {
  display: flex;
  align-items: center;
  gap: $space-sm;
  padding: $space-md $space-lg;
  background: rgba($color-accent, 0.08);
  border: 1px solid rgba($color-accent, 0.3);
  border-radius: $radius-md;
  color: $color-accent;
  font-size: $font-size-small;
  margin-bottom: $space-lg;
}

.error-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: $color-accent;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.error-dismiss {
  margin-left: auto;
  border: none;
  background: none;
  color: $color-accent;
  cursor: pointer;
  font-size: 14px;
  padding: 2px 6px;
  border-radius: $radius-sm;

  &:hover {
    background: rgba($color-accent, 0.1);
  }
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 640px) {
  .main-content {
    padding: $space-md $space-md $space-xl;
  }
}
</style>

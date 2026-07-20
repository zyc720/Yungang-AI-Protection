<script setup lang="ts">
/**
 * Horizontal scrollable list of cited sources.
 */
import { ref } from 'vue'
import type { CitedSource } from '@/types/api'
import SourceCard from './SourceCard.vue'

const props = defineProps<{
  sources: CitedSource[]
}>()

const emit = defineEmits<{
  showDocument: [entryId: string, title: string]
}>()

const highlightedIndex = ref<number | null>(null)

function highlightSource(title: string) {
  const { sources } = props
  const idx = sources.findIndex((s: CitedSource) => s.title === title)
  highlightedIndex.value = idx >= 0 ? idx : null
}

defineExpose({ highlightSource })
</script>

<template>
  <div v-if="sources.length > 0" class="sources-section">
    <h3 class="section-label">
      引用来源
      <span class="source-count">{{ sources.length }}</span>
    </h3>
    <div class="sources-scroll">
      <SourceCard
        v-for="(source, idx) in sources"
        :key="source.entry_id + '-' + idx"
        :source="source"
        :highlighted="highlightedIndex === idx"
        @click="emit('showDocument', source.entry_id, source.title)"
      />
    </div>
  </div>
</template>

<style scoped lang="scss">
.sources-section {
  margin-top: $space-lg;
}

.section-label {
  display: flex;
  align-items: center;
  gap: $space-sm;
  font-size: 14px;
  font-weight: 500;
  color: $color-text-muted;
  margin-bottom: $space-sm;
  letter-spacing: 1px;
}

.source-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  font-size: $font-size-caption;
  color: #fff;
  background: $color-accent;
  border-radius: 10px;
}

.sources-scroll {
  display: flex;
  gap: $space-md;
  overflow-x: auto;
  padding-bottom: $space-sm;

  // Hide scrollbar on hover-less interfaces but keep functionality
  &::-webkit-scrollbar {
    height: 4px;
  }

  &::-webkit-scrollbar-thumb {
    background: $color-border;
    border-radius: 2px;
  }
}
</style>

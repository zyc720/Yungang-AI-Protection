<script setup lang="ts">
/**
 * Curated hot entries — clickable chips for quick exploration.
 */
import type { HotEntry } from '@/types/dictionary'

defineProps<{
  entries: HotEntry[]
}>()

const emit = defineEmits<{
  select: [entryId: string]
}>()
</script>

<template>
  <div class="hot-entries" v-if="entries.length > 0">
    <h3 class="section-title">热门词条</h3>
    <div class="entries-grid">
      <button
        v-for="entry in entries"
        :key="entry.entry_id"
        class="entry-chip"
        @click="emit('select', entry.entry_id)"
      >
        <span class="chip-title">{{ entry.title }}</span>
        <span class="chip-category">{{ entry.category }}</span>
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.hot-entries {
  margin-top: $space-lg;
}

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: $color-text-muted;
  margin-bottom: $space-sm;
  letter-spacing: 1px;
}

.entries-grid {
  display: flex;
  flex-wrap: wrap;
  gap: $space-sm;
}

.entry-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border: 1px solid $color-border;
  border-radius: 20px;
  background: $color-bg;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: $font-ui;
  font-size: $font-size-small;

  &:hover {
    border-color: $color-accent;
    background: $color-accent-bg;
    color: $color-accent;
  }

  &:active {
    transform: scale(0.97);
  }
}

.chip-title {
  color: $color-text-heading;
  font-weight: 500;
}

.chip-category {
  font-size: $font-size-caption;
  color: $color-text-muted;
  padding: 1px 6px;
  background: $color-bg-card;
  border-radius: 10px;
}
</style>

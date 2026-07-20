<script setup lang="ts">
/**
 * Single citation source card.
 * Click to view the full dictionary entry in the document viewer.
 */
import type { CitedSource } from '@/types/api'

defineProps<{
  source: CitedSource
  highlighted: boolean
}>()

const emit = defineEmits<{
  click: [source: CitedSource]
}>()
</script>

<template>
  <div
    class="source-card"
    :class="{ highlighted }"
    @click="emit('click', source)"
  >
    <div class="source-header">
      <h4 class="source-title">{{ source.title }}</h4>
      <span v-if="source.page" class="source-page">第{{ source.page }}页</span>
    </div>
    <p class="source-excerpt">{{ source.excerpt || '（原文较长，点击查看完整内容）' }}</p>
    <div class="source-action">点击查看原文 →</div>
  </div>
</template>

<style scoped lang="scss">
.source-card {
  flex-shrink: 0;
  width: 240px;
  padding: $space-md;
  background: $color-bg;
  border: 1px solid $color-border;
  border-radius: $radius-md;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: $color-accent;
    box-shadow: $shadow-md;
  }

  &.highlighted {
    border-color: $color-accent;
    background: $color-accent-bg;
    box-shadow: $shadow-md;
  }
}

.source-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: $space-sm;
  margin-bottom: $space-sm;
}

.source-title {
  font-size: $font-size-small;
  font-weight: 600;
  color: $color-text-heading;
  margin: 0;
}

.source-page {
  font-size: $font-size-caption;
  color: $color-text-muted;
  white-space: nowrap;
  padding: 1px 6px;
  background: $color-bg-card;
  border-radius: 3px;
}

.source-excerpt {
  font-size: $font-size-small;
  color: $color-text-body;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: $space-sm;
}

.source-action {
  font-size: $font-size-caption;
  color: $color-accent;
  font-weight: 500;
}
</style>

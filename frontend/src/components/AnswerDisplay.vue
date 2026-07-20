<script setup lang="ts">
/**
 * Renders the AI-generated answer with inline citation highlighting.
 *
 * Parses 【来源：词条标题，页码 X】 markers and renders them as
 * clickable styled badges. Emits a showSource event when a citation
 * badge is clicked so the parent can scroll to the matching source.
 */
import { computed } from 'vue'
import type { ConfidenceLevel } from '@/types/api'
import { useCitationParser } from '@/composables/useCitationParser'
import { useConfidenceStyle } from '@/composables/useConfidenceStyle'

const props = defineProps<{
  text: string
  confidence: ConfidenceLevel
}>()

const emit = defineEmits<{
  showSource: [title: string]
}>()

const segments = computed(() => useCitationParser(props.text))
const conf = computed(() => useConfidenceStyle(props.confidence))
</script>

<template>
  <div class="answer-display" :class="conf.className">
    <div class="confidence-bar" :style="{ borderLeftColor: conf.color }">
      <span class="confidence-badge" :style="{ background: conf.color }">
        {{ conf.label }}
      </span>
    </div>
    <div class="answer-content">
      <template v-for="(seg, idx) in segments" :key="idx">
        <span v-if="seg.type === 'text'" class="text-segment">{{ seg.text }}</span>
        <button
          v-else
          class="citation-badge"
          @click="emit('showSource', seg.title!)"
          :title="`查看词条：${seg.title}`"
        >
          {{ seg.text }}
        </button>
      </template>
    </div>
  </div>
  <div v-if="confidence === 'not_found'" class="not-found-hint">
    知识库中未检索到相关信息。以上回答可能基于有限资料，建议尝试其他关键词。
  </div>
</template>

<style scoped lang="scss">
.answer-display {
  background: $color-bg-card;
  border-radius: $radius-lg;
  border: 1px solid $color-border;
  overflow: hidden;
}

.confidence-bar {
  display: flex;
  align-items: center;
  padding: $space-sm $space-md;
  border-left: 4px solid;
  background: rgba(255, 255, 255, 0.5);
}

.confidence-badge {
  font-size: $font-size-caption;
  color: #fff;
  padding: 2px 10px;
  border-radius: 10px;
  font-weight: 500;
}

.answer-content {
  padding: $space-lg;
  font-family: $font-body;
  font-size: $font-size-body;
  color: $color-text-body;
  line-height: 2;
  text-align: justify;
  word-break: break-word;
}

.text-segment {
  white-space: pre-wrap;
}

.citation-badge {
  display: inline;
  padding: 2px 8px;
  margin: 0 2px;
  background: $color-accent-bg;
  color: $color-accent;
  border: 1px solid rgba($color-accent, 0.2);
  border-radius: $radius-sm;
  font-size: $font-size-small;
  font-family: $font-ui;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;

  &:hover {
    background: rgba($color-accent, 0.15);
    border-color: $color-accent;
  }
}

.not-found-hint {
  margin-top: $space-sm;
  padding: $space-sm $space-md;
  font-size: $font-size-small;
  color: $color-text-muted;
  text-align: center;
  background: rgba($color-not-found, 0.3);
  border-radius: $radius-md;
}
</style>

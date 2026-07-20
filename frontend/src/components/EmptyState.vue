<script setup lang="ts">
/**
 * Welcoming empty state shown before the first search.
 * Uses a museum-display aesthetic, NOT a chatbot look.
 */
import { onMounted, ref } from 'vue'

const visible = ref(false)

onMounted(() => {
  // Delay to allow splash to animate in
  requestAnimationFrame(() => {
    visible.value = true
  })
})
</script>

<template>
  <div class="empty-state" :class="{ visible }">
    <div class="empty-ornament">⟩⟩⟩⟩ ⟨⟨⟨⟨</div>
    <h2 class="empty-title">探究云冈，从这里开始</h2>
    <p class="empty-desc">
      这是一个同云冈石窟知识相关的智能问答平台<br />
      输入您感兴趣的关键词或问题，系统将从知识库中检索相关信息并给出答案
    </p>
    <p class="empty-hint">
      试试搜索：<em>云冈石窟建于何时</em>、<em>昙曜五窟是哪几个窟</em>、<em>第20窟大佛</em>
    </p>
  </div>
</template>

<style scoped lang="scss">
.empty-state {
  text-align: center;
  padding: $space-2xl $space-lg;
  opacity: 0;
  transform: translateY(12px);
  transition: opacity 0.6s ease, transform 0.6s ease;

  &.visible {
    opacity: 1;
    transform: translateY(0);
  }
}

.empty-ornament {
  font-family: $font-body;
  font-size: 20px;
  color: $color-text-muted;
  letter-spacing: 4px;
  margin-bottom: $space-xl;
  user-select: none;
}

.empty-title {
  font-size: 22px;
  color: $color-text-heading;
  margin-bottom: $space-md;
  font-weight: 600;
}

.empty-desc {
  font-size: $font-size-body;
  color: $color-text-body;
  line-height: 1.8;
  max-width: 480px;
  margin: 0 auto $space-lg;
}

.empty-hint {
  font-size: $font-size-small;
  color: $color-text-muted;

  em {
    font-style: normal;
    color: $color-accent;
  }
}
</style>

<script setup lang="ts">
/**
 * Document viewer — a slide-out drawer showing the full text of a dictionary entry.
 * Used to browse original text from the knowledge base.
 */
import { computed } from 'vue'
import { useSearchStore } from '@/stores/searchStore'
import { Document } from '@element-plus/icons-vue'

const store = useSearchStore()

const entryTitle = computed(() => store.selectedEntry?.title ?? '')
const entryContent = computed(() => store.selectedEntry?.content ?? '')
const entryPage = computed(() => store.selectedEntry?.page)

function close() {
  store.closeViewer()
}
</script>

<template>
  <transition name="drawer">
    <div v-if="store.isViewerOpen" class="viewer-overlay" @click.self="close">
      <div class="viewer-drawer">
        <div class="viewer-header">
          <div class="viewer-header-left">
            <el-icon :size="18"><Document /></el-icon>
            <h3 class="viewer-title">《云冈石窟辞典》原文</h3>
          </div>
          <button class="viewer-close" @click="close" title="关闭">✕</button>
        </div>

        <div class="viewer-body">
          <div class="entry-metadata">
            <span class="entry-label">词条</span>
            <span class="entry-name">{{ entryTitle }}</span>
            <span v-if="entryPage" class="entry-page-badge">第{{ entryPage }}页</span>
          </div>
          <div class="entry-content">
            <p v-for="(para, idx) in entryContent.split('\n\n')" :key="idx" class="entry-paragraph">
              {{ para }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped lang="scss">
.viewer-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: rgba(61, 48, 32, 0.3);
  display: flex;
  justify-content: flex-end;
  backdrop-filter: blur(2px);
}

.viewer-drawer {
  width: 520px;
  max-width: 90vw;
  height: 100%;
  background: $color-bg;
  box-shadow: -4px 0 24px rgba(61, 48, 32, 0.15);
  display: flex;
  flex-direction: column;
}

.viewer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $space-md $space-lg;
  border-bottom: 1px solid $color-border;
  flex-shrink: 0;
}

.viewer-header-left {
  display: flex;
  align-items: center;
  gap: $space-sm;
  color: $color-text-muted;
}

.viewer-title {
  font-size: $font-size-small;
  font-weight: 600;
  color: $color-text-heading;
  margin: 0;
}

.viewer-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid $color-border;
  border-radius: $radius-md;
  background: $color-bg;
  color: $color-text-muted;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: $color-accent;
    color: $color-accent;
    background: $color-accent-bg;
  }
}

.viewer-body {
  flex: 1;
  overflow-y: auto;
  padding: $space-lg;
}

.entry-metadata {
  display: flex;
  align-items: center;
  gap: $space-sm;
  padding-bottom: $space-md;
  margin-bottom: $space-md;
  border-bottom: 2px solid $color-border;
}

.entry-label {
  font-size: $font-size-caption;
  color: $color-text-muted;
  padding: 2px 8px;
  background: $color-bg-card;
  border-radius: 3px;
}

.entry-name {
  font-family: $font-body;
  font-size: 18px;
  font-weight: 700;
  color: $color-text-heading;
}

.entry-page-badge {
  font-size: $font-size-caption;
  color: $color-text-muted;
  margin-left: auto;
}

.entry-content {
  font-family: $font-body;
  font-size: 15px;
  color: $color-text-body;
  line-height: 2;
}

.entry-paragraph {
  margin-bottom: $space-md;
  text-indent: 2em;
  text-align: justify;
}

// Drawer transitions
.drawer-enter-active,
.drawer-leave-active {
  transition: all 0.3s ease;

  .viewer-drawer {
    transition: transform 0.3s ease;
  }
}

.drawer-enter-from,
.drawer-leave-to {
  .viewer-drawer {
    transform: translateX(100%);
  }
  background: rgba(61, 48, 32, 0);
}

.drawer-enter-to,
.drawer-leave-from {
  .viewer-drawer {
    transform: translateX(0);
  }
  background: rgba(61, 48, 32, 0.3);
}
</style>

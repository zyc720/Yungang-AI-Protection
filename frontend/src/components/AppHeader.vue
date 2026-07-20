<script setup lang="ts">
/**
 * Application header with logo, title, page navigation, and backend health indicator.
 */
import { useRoute } from 'vue-router'

defineProps<{
  healthStatus: 'ok' | 'error' | 'loading'
}>()

const route = useRoute()

function isActive(path: string): boolean {
  return route.path === path
}
</script>

<template>
  <header class="app-header">
    <div class="header-inner">
      <div class="brand">
        <div class="title-group">
          <h1 class="app-title">云冈石窟智能问答平台</h1>
          <p class="app-subtitle">基于每个用户自己所选择的知识库</p>
        </div>
        <nav class="page-badges">
          <router-link
            to="/"
            class="page-badge"
            :class="{ active: isActive('/') }"
          >
            <img
              src="/ai.svg"
              alt="AI"
              class="page-badge-icon"
            />
            <span class="page-badge-text">AI chat</span>
          </router-link>
          <router-link
            to="/knowledge-base"
            class="page-badge"
            :class="{ active: isActive('/knowledge-base') }"
          >
            <img
              src="/graph.svg"
              alt="知识库"
              class="page-badge-icon"
            />
            <span class="page-badge-text">知识库</span>
          </router-link>
        </nav>
      </div>
      <div class="health-indicator" :class="`health-${healthStatus}`" :title="healthStatus === 'ok' ? '服务正常' : healthStatus === 'error' ? '服务异常' : '检测中...'">
          <span class="health-dot"></span>
          <span class="health-label">
            {{ healthStatus === 'ok' ? '服务正常' : healthStatus === 'error' ? '服务异常' : '检测中' }}
          </span>
      </div>
    </div>
  </header>
</template>

<style scoped lang="scss">
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  height: $header-height;
  background: $color-bg;
  border-bottom: 1px solid $color-border;
  backdrop-filter: blur(8px);
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: $max-content-width;
  margin: 0 auto;
  padding: 0 $space-lg;
  height: 100%;
}

.brand {
  display: flex;
  align-items: center;
  gap: $space-md;
}

.page-badges {
  display: flex;
  align-items: center;
  gap: 0;
}

.page-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px 4px 8px;
  border-radius: $radius-sm;
  white-space: nowrap;
  flex-shrink: 0;
  text-decoration: none;
  cursor: pointer;
  color: $color-text-muted;
  background: transparent;
  transition: color 0.2s ease, background 0.2s ease;

  &:hover {
    color: $color-accent;
    background: rgba($color-accent, 0.04);
  }

  &.active {
    color: $color-accent;
    background: $color-accent-bg;

    .page-badge-text {
      font-weight: 600;
    }
  }
}

.page-badge-icon {
  width: 18px;
  height: 18px;
  object-fit: contain;
  flex-shrink: 0;
}

.page-badge-text {
  font-size: $font-size-small;
  letter-spacing: 0.3px;
}

.title-group {
  display: flex;
  flex-direction: column;
}

.app-title {
  font-size: 18px;
  font-weight: 700;
  color: $color-text-heading;
  margin: 0;
  line-height: 1.3;
  letter-spacing: 0.5px;
}

.app-subtitle {
  font-size: $font-size-caption;
  color: $color-text-muted;
  margin: 0;
}

.health-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: $font-size-caption;
  color: $color-text-muted;
}

.health-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: $color-text-muted;
  transition: background 0.3s ease;

  .health-ok & { background: $color-confidence-high; }
  .health-error & { background: $color-accent; }
  .health-loading & { animation: pulse 1.5s infinite; background: $color-confidence-medium; }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

@media (max-width: 640px) {
  .app-subtitle { display: none; }
  .health-label { display: none; }
}
</style>

<script setup lang="ts">
/**
 * Application header with logo, title, and backend health indicator.
 */
defineProps<{
  healthStatus: 'ok' | 'error' | 'loading'
}>()
</script>

<template>
  <header class="app-header">
    <div class="header-inner">
      <div class="brand">
        <div class="logo-icon">
          <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="8" y="4" width="24" height="32" rx="4" stroke="currentColor" stroke-width="1.5" fill="none"/>
            <path d="M14 14 Q20 8 26 14" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round"/>
            <line x1="16" y1="20" x2="24" y2="20" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            <line x1="16" y1="25" x2="22" y2="25" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="title-group">
          <h1 class="app-title">云冈石窟智能电子辞典</h1>
          <p class="app-subtitle">基于《云冈石窟辞典》知识库</p>
        </div>
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

.logo-icon {
  width: 36px;
  height: 36px;
  color: $color-accent;
  flex-shrink: 0;
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

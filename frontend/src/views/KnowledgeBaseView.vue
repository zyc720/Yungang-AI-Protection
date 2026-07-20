<script setup lang="ts">
/**
 * KnowledgeBaseView — knowledge base management page (placeholder).
 *
 * Will host knowledge graph browsing, entry exploration, and document
 * management features in future versions.
 */
</script>

<template>
  <div class="knowledge-base">
    <header class="kb-header">
      <h1 class="kb-title">知识库</h1>
      <p class="kb-subtitle">知识库管理与浏览功能即将上线</p>
    </header>
    <main class="kb-content">
      <div class="kb-placeholder">
        <div class="empty-icon">
          <svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="16" y="8" width="48" height="64" rx="8" stroke="currentColor" stroke-width="1.5" fill="none"/>
            <rect x="22" y="18" width="36" height="4" rx="2" fill="currentColor" opacity="0.3"/>
            <rect x="22" y="28" width="28" height="4" rx="2" fill="currentColor" opacity="0.2"/>
            <rect x="22" y="38" width="32" height="4" rx="2" fill="currentColor" opacity="0.2"/>
            <rect x="22" y="48" width="24" height="4" rx="2" fill="currentColor" opacity="0.15"/>
          </svg>
        </div>
        <p class="empty-text">此页面将在后续版本中实现</p>
        <p class="empty-hint">敬请期待知识图谱浏览、词条探索与文档管理功能</p>
      </div>
    </main>
  </div>
</template>

<style scoped lang="scss">
.knowledge-base {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: $color-bg;
}

.kb-header {
  text-align: center;
  padding: $space-2xl $space-lg $space-xl;
  border-bottom: 1px solid $color-border;
}

.kb-title {
  font-size: $font-size-heading;
  font-weight: 700;
  color: $color-text-heading;
  margin: 0 0 $space-sm 0;
}

.kb-subtitle {
  font-size: $font-size-small;
  color: $color-text-muted;
  margin: 0;
}

.kb-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $space-xl $space-lg;
}

.kb-placeholder {
  text-align: center;
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto $space-lg;
  color: $color-text-muted;
  opacity: 0.5;
}

.empty-text {
  font-size: $font-size-body;
  color: $color-text-heading;
  margin: 0 0 $space-sm 0;
}

.empty-hint {
  font-size: $font-size-small;
  color: $color-text-muted;
  margin: 0;
}
</style>

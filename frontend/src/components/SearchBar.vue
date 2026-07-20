<script setup lang="ts">
/**
 * Main search bar with advanced options toggle.
 * Supports Enter-to-search and loading state.
 */
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'

const props = defineProps<{
  loading: boolean
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  search: [query: string, topK: number, useHybrid: boolean]
}>()

const showAdvanced = ref(false)
const topK = ref(5)
const useHybrid = ref(true)

function handleSearch() {
  const trimmed = props.modelValue.trim()
  if (!trimmed || props.loading) return
  emit('search', trimmed, topK.value, useHybrid.value)
}
</script>

<template>
  <div class="search-bar">
    <div class="search-input-row">
      <el-input
        :model-value="modelValue"
        @update:model-value="(v: string) => emit('update:modelValue', v)"
        placeholder="输入您想了解的云冈石窟相关问题..."
        size="large"
        :disabled="loading"
        clearable
        @keyup.enter="handleSearch"
        class="search-input"
      >
        <template #suffix>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            :disabled="!modelValue.trim()"
            @click="handleSearch"
            class="search-btn"
          >
            <el-icon v-if="!loading"><Search /></el-icon>
            <span>{{ loading ? '检索中...' : '搜索' }}</span>
          </el-button>
        </template>
      </el-input>
    </div>

    <div class="search-advanced-toggle" @click="showAdvanced = !showAdvanced">
      <span class="toggle-text">
        {{ showAdvanced ? '收起' : '高级' }}选项
      </span>
      <span class="toggle-icon" :class="{ open: showAdvanced }">▾</span>
    </div>

    <transition name="collapse">
      <div v-if="showAdvanced" class="search-advanced">
        <div class="option-row">
          <label class="option-label">检索数量 (TopK)</label>
          <el-slider
            v-model="topK"
            :min="1"
            :max="20"
            :step="1"
            show-input
            :show-input-controls="false"
            size="small"
            class="option-slider"
          />
        </div>
        <div class="option-row">
          <label class="option-label">混合检索 (BM25 + 向量)</label>
          <el-switch v-model="useHybrid" size="small" />
          <span class="option-hint">{{ useHybrid ? '更精准的混合检索' : '仅向量语义检索' }}</span>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped lang="scss">
.search-bar {
  width: 100%;
}

.search-input-row {
  display: flex;
  gap: 0;
}

.search-input {
  :deep(.el-input__wrapper) {
    border-radius: $radius-lg;
    box-shadow: $shadow-md;
    padding-right: 8px;
    border: 2px solid transparent;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;

    &:hover {
      box-shadow: $shadow-lg;
    }

    &.is-focus {
      border-color: $color-accent;
      box-shadow: $shadow-lg;
    }
  }

  :deep(.el-input__inner) {
    font-size: 16px;
    color: $color-text-heading;
    line-height: 1.6;

    &::placeholder {
      color: $color-text-muted;
    }
  }

  :deep(.el-input__suffix) {
    display: flex;
    align-items: center;
  }
}

.search-btn {
  margin-right: -4px;
  border-radius: $radius-md;
  font-weight: 500;
  white-space: nowrap;

  :deep(.el-icon) {
    margin-right: 4px;
  }
}

.search-advanced-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  margin-top: $space-sm;
  cursor: pointer;
  user-select: none;
  color: $color-text-muted;
  font-size: $font-size-caption;
  transition: color 0.2s;

  &:hover {
    color: $color-accent;
  }
}

.toggle-icon {
  transition: transform 0.2s ease;
  &.open { transform: rotate(180deg); }
}

.search-advanced {
  margin-top: $space-md;
  padding: $space-md $space-lg;
  background: $color-bg-card;
  border-radius: $radius-md;
  border: 1px solid $color-border;
}

.option-row {
  display: flex;
  align-items: center;
  gap: $space-md;
  margin-bottom: $space-sm;

  &:last-child {
    margin-bottom: 0;
  }
}

.option-label {
  font-size: $font-size-small;
  color: $color-text-body;
  white-space: nowrap;
  min-width: 140px;
}

.option-slider {
  flex: 1;
}

.option-hint {
  font-size: $font-size-caption;
  color: $color-text-muted;
}

// Transition
.collapse-enter-active,
.collapse-leave-active {
  transition: all 0.25s ease;
}

.collapse-enter-from,
.collapse-leave-to {
  opacity: 0;
  max-height: 0;
  margin-top: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.collapse-enter-to,
.collapse-leave-from {
  opacity: 1;
  max-height: 200px;
}
</style>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import { useAppStore } from '@/stores/appStore'

const appStore = useAppStore()
</script>

<template>
  <AppHeader :health-status="appStore.healthStatus" />
  <RouterView />
</template>

<style lang="scss">
@use '@/assets/styles/variables' as *;
@use '@/assets/styles/element-overrides.scss';
@use '@/assets/styles/global.scss';
</style>

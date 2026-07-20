import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: 'AI chat — 云冈石窟智能问答平台' },
  },
  {
    path: '/knowledge-base',
    name: 'knowledge-base',
    component: () => import('@/views/KnowledgeBaseView.vue'),
    meta: { title: '知识库 — 云冈石窟智能问答平台' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Set document title on route change
router.beforeEach((to) => {
  const title = to.meta.title as string | undefined
  document.title = title || '云冈石窟智能电子辞典'
})

export default router

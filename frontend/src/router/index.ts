import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: '云冈石窟智能电子辞典' },
  },
  // Future routes (v2+):
  // { path: '/browse', name: 'browse', component: ... },
  // { path: '/history', name: 'history', component: ... },
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

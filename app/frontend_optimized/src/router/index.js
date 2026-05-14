import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/views/Layout.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    meta: { title: '职业规划智能体' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫更新标题
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '职业规划智能体'
  next()
})

export default router

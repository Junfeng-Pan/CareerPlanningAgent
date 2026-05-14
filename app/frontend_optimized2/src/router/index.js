import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Chat',
    component: () => import('@/views/ChatView.vue'),
    meta: { title: '智能对话' }
  },
  {
    path: '/student-profile',
    name: 'StudentProfile',
    component: () => import('@/views/StudentProfileView.vue'),
    meta: { title: '学生画像' }
  },
  {
    path: '/job-profile',
    name: 'JobProfile',
    component: () => import('@/views/JobProfileView.vue'),
    meta: { title: '岗位画像' }
  },
  {
    path: '/match-result',
    name: 'MatchResult',
    component: () => import('@/views/MatchResultView.vue'),
    meta: { title: '人岗匹配' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - 职业规划智能体`
  }
  next()
})

export default router

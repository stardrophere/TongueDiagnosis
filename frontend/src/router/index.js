import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Check from '../views/Check.vue'
import LoginRegister from '@/views/LoginRegister.vue'
import { useAuthStore } from '@/stores/authStore'

const routes = [
  {
    path: '/home',
    name: 'home',
    component: Home,
    meta: {
      title: '首页',
    },
  },
  {
    path: '/login',
    name: 'login',
    component: LoginRegister,
    meta: {
      guestOnly: true,
      authMode: 'login',
      title: '登录',
    },
  },
  {
    path: '/register',
    name: 'register',
    component: LoginRegister,
    meta: {
      guestOnly: true,
      authMode: 'register',
      title: '注册',
    },
  },
  {
    path: '/check',
    name: 'check',
    component: Check,
    meta: {
      requireAuth: true,
      title: '智能诊断',
    },
  },
  {
    path: '/',
    redirect: '/home',
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

/**
 * 统一管理页面标题与登录态拦截。
 * 这样页面组件可以专注于业务，而不是重复写跳转判断。
 */
router.beforeEach(async (to) => {
  const authStore = useAuthStore()
  const hasToken = Boolean(authStore.token || localStorage.getItem('token'))

  document.title = to.meta?.title ? `AI 舌诊助手 - ${to.meta.title}` : 'AI 舌诊助手'

  if (to.meta?.requireAuth && !hasToken) {
    return {
      path: '/login',
      query: {
        redirect: to.fullPath,
      },
    }
  }

  if (to.meta?.guestOnly && hasToken) {
    return '/check'
  }

  return true
})

export default router

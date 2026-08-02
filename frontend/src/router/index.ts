import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/compare',
      name: 'compare',
      component: () => import('@/views/CompareView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/interview-simulator',
      name: 'interview-simulator',
      component: () => import('@/views/InterviewSimulatorView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/interview-results',
      name: 'interview-results',
      component: () => import('@/views/InterviewResultsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/free-trial',
      name: 'free-trial',
      component: () => import('@/views/FreeTrialView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/ProfileView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/auth/callback',
      name: 'auth-callback',
      component: () => import('@/views/AuthCallbackView.vue'),
      meta: { requiresAuth: false },
    },
  ],
})

async function waitForAuthReady() {
  const authStore = useAuthStore()
  if (!authStore.loading) return

  await new Promise<void>((resolve) => {
    const stop = authStore.$subscribe((_mutation, state) => {
      if (!state.loading) {
        stop()
        resolve()
      }
    })
    // Sécurité si loading est déjà false entre le check et le subscribe
    if (!authStore.loading) {
      stop()
      resolve()
    }
  })
}

router.beforeEach(async (to) => {
  const authStore = useAuthStore()
  await waitForAuthReady()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return '/login'
  }

  return true
})

export default router

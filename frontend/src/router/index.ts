import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/compare',
      name: 'compare',
      component: () => import('@/views/CompareView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/ProfileView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { requiresAuth: false }
    }
  ]
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Si l'authentification est en cours de chargement, attendre
  if (authStore.loading) {
    // Attendre que l'initialisation soit terminée
    await new Promise(resolve => {
      const unwatch = authStore.$subscribe(() => {
        if (!authStore.loading) {
          unwatch()
          resolve(true)
        }
      })
    })
  }
  
  // Rediriger les utilisateurs connectés vers /compare s'ils tentent d'accéder à la page d'accueil
  if (to.path === '/' && authStore.isAuthenticated) {
    next('/compare')
    return
  }
  
  // Rediriger les utilisateurs non connectés vers /login pour les routes protégées
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router 
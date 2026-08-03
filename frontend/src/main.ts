import { ViteSSG } from 'vite-ssg'
import { createPinia } from 'pinia'
import { createHead } from '@vueuse/head'
import App from './App.vue'
import { routes } from './router'
import { useAuthStore } from '@/stores/auth'
import {
  captureAnalyticsException,
  initAnalytics,
  isAnalyticsConfigured,
} from './lib/analytics'
import './style.css'

export const createApp = ViteSSG(
  App,
  {
    routes,
    scrollBehavior(to) {
      if (to.hash) {
        return { el: to.hash, behavior: 'smooth' }
      }
      return { top: 0 }
    },
  },
  ({ app, router, isClient }) => {
    const pinia = createPinia()
    const head = createHead()
    app.use(pinia)
    app.use(head)

    if (isClient) {
      initAnalytics()

      app.config.errorHandler = (error) => {
        if (isAnalyticsConfigured) {
          captureAnalyticsException(error)
        }
      }
    }

    router.beforeEach(async (to) => {
      // Pendant le SSG, ne pas bloquer sur l’auth client
      if (import.meta.env.SSR) {
        if (to.meta.requiresAuth) return '/login'
        return true
      }

      const authStore = useAuthStore()

      // Démarrer l’auth ici (pas seulement dans App.onMounted) : sinon
      // router.isReady() attend loading=false avant le mount → deadlock,
      // l’app ne s’hydrate jamais et la bannière cookies n’apparaît pas.
      if (authStore.loading) {
        await authStore.initializeAuth()
      }

      if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        return '/login'
      }

      return true
    })
  },
)

import { ViteSSG } from 'vite-ssg'
import { createPinia } from 'pinia'
import App from './App.vue'
import { routes } from './router'
import { createAppI18n, isLocale, type Locale } from './i18n'
import { hasEnglishVersion, localizePath } from './i18n/routing'
import { STORAGE_KEYS } from './lib/storageKeys'
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
    // Le head (@unhead/vue) est créé par vite-ssg : c'est lui qui est sérialisé au prerender
    const pinia = createPinia()
    app.use(pinia)
    const i18n = createAppI18n()
    app.use(i18n)

    if (isClient) {
      initAnalytics()

      app.config.errorHandler = (error) => {
        if (isAnalyticsConfigured) {
          captureAnalyticsException(error)
        }
      }
    }

    let initialNavigation = true

    router.beforeEach(async (to) => {
      const locale: Locale = to.meta.locale ?? 'fr'
      i18n.global.locale.value = locale

      // Pendant le SSG, ne pas bloquer sur l’auth client
      if (import.meta.env.SSR) {
        if (to.meta.requiresAuth) return localizePath('/login', locale)
        return true
      }

      // Première page : appliquer la langue mémorisée, sinon celle du navigateur
      if (initialNavigation) {
        initialNavigation = false
        const preferred = preferredLocale()
        if (preferred && preferred !== locale && hasEnglishVersion(to.path)) {
          return { path: localizePath(to.path, preferred), query: to.query, hash: to.hash, replace: true }
        }
      }

      const authStore = useAuthStore()

      // Démarrer l’auth ici (pas seulement dans App.onMounted) : sinon
      // router.isReady() attend loading=false avant le mount → deadlock,
      // l’app ne s’hydrate jamais et la bannière cookies n’apparaît pas.
      if (authStore.loading) {
        await authStore.initializeAuth()
      }

      if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        return localizePath('/login', locale)
      }

      return true
    })
  },
)

const BOT_UA = /bot|crawl|spider|slurp|facebookexternalhit|embedly|preview/i

/** Langue choisie (sélecteur) ou, au tout premier passage, langue du navigateur. Jamais pour les robots. */
function preferredLocale(): Locale | null {
  if (BOT_UA.test(navigator.userAgent)) return null
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.locale)
    if (isLocale(stored)) return stored
  } catch {
    return null
  }
  return navigator.language?.toLowerCase().startsWith('fr') ? null : 'en'
}

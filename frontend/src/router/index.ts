import type { RouteRecordRaw } from 'vue-router'
import type { Locale } from '@/i18n'

export const EN_PREFIX = '/en'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    noindex?: boolean
    /** Clé i18n `seo.<key>.title` / `seo.<key>.description` */
    seo?: string
    locale?: Locale
  }
}

type BaseRoute = RouteRecordRaw & {
  name: string
  /** false : la page n'existe qu'en français (contenu non encore traduit) */
  translated?: boolean
}

const baseRoutes: BaseRoute[] = [
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
    meta: { requiresAuth: true, seo: 'dashboard' },
  },
  {
    path: '/compare',
    name: 'compare',
    component: () => import('@/views/CompareView.vue'),
    meta: { requiresAuth: true, seo: 'compare' },
  },
  {
    path: '/interview-simulator',
    name: 'interview-simulator',
    component: () => import('@/views/InterviewSimulatorView.vue'),
    meta: { requiresAuth: true, seo: 'interviewSimulator' },
  },
  {
    path: '/interview-results',
    name: 'interview-results',
    component: () => import('@/views/InterviewResultsView.vue'),
    meta: { requiresAuth: true, seo: 'interviewResults' },
  },
  {
    path: '/cover-letter',
    name: 'cover-letter',
    component: () => import('@/views/CoverLetterView.vue'),
    meta: { requiresAuth: true, seo: 'coverLetter' },
  },
  {
    // Bookmarklet « Envoyer vers Talento » : installation et réception des offres (Indeed, LinkedIn…)
    path: '/import',
    name: 'import-offer',
    component: () => import('@/views/ImportOfferView.vue'),
    meta: { requiresAuth: true, seo: 'importOffer' },
  },
  {
    path: '/free-trial',
    name: 'free-trial',
    component: () => import('@/views/FreeTrialView.vue'),
    meta: { requiresAuth: false, seo: 'freeTrial' },
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { requiresAuth: true, seo: 'profile' },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false, seo: 'login' },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { requiresAuth: false, seo: 'register' },
  },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: () => import('@/views/ForgotPasswordView.vue'),
    meta: { requiresAuth: false, noindex: true, seo: 'forgotPassword' },
  },
  {
    path: '/reset-password',
    name: 'reset-password',
    component: () => import('@/views/ResetPasswordView.vue'),
    meta: { requiresAuth: false, noindex: true, seo: 'resetPassword' },
  },
  {
    path: '/verify-email',
    name: 'verify-email',
    component: () => import('@/views/VerifyEmailView.vue'),
    meta: { requiresAuth: false, noindex: true, seo: 'verifyEmail' },
  },
  {
    path: '/auth/callback',
    name: 'auth-callback',
    component: () => import('@/views/AuthCallbackView.vue'),
    meta: { requiresAuth: false, noindex: true },
  },
  {
    path: '/mentions-legales',
    name: 'mentions-legales',
    component: () => import('@/views/MentionsLegalesView.vue'),
    meta: { requiresAuth: false, seo: 'legalNotice' },
  },
  {
    path: '/cgv',
    name: 'cgv',
    component: () => import('@/views/CgvView.vue'),
    meta: { requiresAuth: false, seo: 'terms' },
  },
  {
    path: '/confidentialite',
    name: 'confidentialite',
    component: () => import('@/views/ConfidentialiteView.vue'),
    meta: { requiresAuth: false, seo: 'privacy' },
  },
]

/** Chemins (sans préfixe) disposant d'une version anglaise sous /en. */
export const englishPaths = new Set(
  baseRoutes.filter((route) => route.translated !== false).map((route) => route.path),
)

function withLocale(base: BaseRoute, locale: Locale): RouteRecordRaw {
  const route: Partial<BaseRoute> = { ...base }
  delete route.translated
  const english = locale === 'en'
  return {
    ...route,
    path: english ? (base.path === '/' ? EN_PREFIX : `${EN_PREFIX}${base.path}`) : base.path,
    name: english ? `en-${base.name}` : base.name,
    meta: { ...route.meta, locale },
  } as RouteRecordRaw
}

export const routes: RouteRecordRaw[] = [
  ...baseRoutes.map((route) => withLocale(route, 'fr')),
  ...baseRoutes.filter((route) => englishPaths.has(route.path)).map((route) => withLocale(route, 'en')),
]

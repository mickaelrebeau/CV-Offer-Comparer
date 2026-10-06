import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api, getApiBaseURL } from '@/lib/api'
import { clearAccessToken, getAccessToken, setAccessToken } from '@/lib/authToken'
import posthog from 'posthog-js'
import type { AuthResponse, AuthUser } from '@/types/auth'
import { t } from '@/i18n'
import { useApplicationContextStore } from './applicationContext'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<AuthUser | null>(null)
  // false pendant le SSG pour ne pas prerender l’overlay « session »
  const loading = ref(typeof window !== 'undefined')
  let initPromise: Promise<void> | null = null

  // Jeton présent mais /auth/me injoignable (hors ligne) : session conservée, revérifiée au retour du réseau
  const sessionUnverified = ref(false)
  // Ordre important : pas d'accès à localStorage pendant le SSG (user null → court-circuit)
  const isAuthenticated = computed(
    () => (!!user.value || sessionUnverified.value) && !!getAccessToken(),
  )
  const isPostHogConfigured = Boolean(
    import.meta.env.VITE_POSTHOG_PROJECT_TOKEN && import.meta.env.VITE_POSTHOG_HOST,
  )

  function identifyUser(authUser: AuthUser) {
    if (!isPostHogConfigured || typeof window === 'undefined') return

    posthog.identify(authUser.id, {
      email: authUser.email,
      ...(authUser.full_name ? { name: authUser.full_name } : {}),
    })
  }

  function resetPostHog() {
    if (isPostHogConfigured && typeof window !== 'undefined') {
      posthog.reset()
    }
  }

  // CV et offre en session : jamais laissés au prochain utilisateur du poste
  function clearApplicationContext() {
    if (typeof window !== 'undefined') useApplicationContextStore().clear()
  }

  async function fetchMe(): Promise<AuthUser | null> {
    const token = getAccessToken()
    if (!token) {
      user.value = null
      return null
    }
    try {
      const { data } = await api.get<AuthUser>('/auth/me')
      user.value = data
      sessionUnverified.value = false
      identifyUser(data)
      return data
    } catch (error: any) {
      if (!error?.response) {
        // Erreur réseau : ne pas déconnecter l'utilisateur pour une coupure
        sessionUnverified.value = true
        return null
      }
      // Réponse du serveur (401…) : session invalide
      clearAccessToken()
      user.value = null
      sessionUnverified.value = false
      clearApplicationContext()
      resetPostHog()
      return null
    }
  }

  async function initializeAuth() {
    if (initPromise) return initPromise

    initPromise = (async () => {
      loading.value = true
      try {
        await fetchMe()
      } finally {
        loading.value = false
        initPromise = null
      }
    })()

    return initPromise
  }

  function applyAuth(payload: AuthResponse) {
    if (user.value && user.value.id !== payload.user.id) {
      clearApplicationContext()
      resetPostHog()
    }

    setAccessToken(payload.access_token)
    user.value = payload.user
    identifyUser(payload.user)
  }

  async function signUp(email: string, password: string) {
    loading.value = true
    try {
      const { data } = await api.post<AuthResponse>('/auth/register', { email, password })
      applyAuth(data)
      return { data, error: null }
    } catch (error: any) {
      return {
        data: null,
        error: new Error(error.response?.data?.detail || t('auth.register.errors.generic')),
      }
    } finally {
      loading.value = false
    }
  }

  async function signIn(email: string, password: string) {
    loading.value = true
    try {
      const { data } = await api.post<AuthResponse>('/auth/login', { email, password })
      applyAuth(data)
      return { data, error: null }
    } catch (error: any) {
      return {
        data: null,
        error: new Error(error.response?.data?.detail || t('auth.login.invalidCredentials')),
      }
    } finally {
      loading.value = false
    }
  }

  async function signInWithGoogle() {
    const base = getApiBaseURL().replace(/\/api$/, '')
    window.location.href = `${base}/api/auth/google`
    return { data: null, error: null }
  }

  async function completeGoogleCallback(code: string) {
    // Ne pas toggler loading ici : ça détruisait la vue callback
    try {
      const { data } = await api.post<AuthResponse>('/auth/google/exchange', { code })
      applyAuth(data)
      return true
    } catch {
      return false
    }
  }

  async function verifyEmail(token: string) {
    try {
      const { data } = await api.post<AuthUser>('/auth/verify-email', { token })
      if (user.value?.id === data.id) user.value = data
      return { error: null }
    } catch (error: any) {
      return { error: new Error(error.response?.data?.detail || t('auth.verify.error')) }
    }
  }

  async function resendVerification() {
    try {
      const { data } = await api.post<{ message: string }>('/auth/resend-verification')
      return { message: data.message, error: null }
    } catch (error: any) {
      return { message: null, error: new Error(error.response?.data?.detail || t('auth.errors.sendFailed')) }
    }
  }

  async function requestPasswordReset(email: string) {
    try {
      const { data } = await api.post<{ message: string }>('/auth/forgot-password', { email })
      return { message: data.message, error: null }
    } catch (error: any) {
      return { message: null, error: new Error(error.response?.data?.detail || t('auth.errors.sendFailed')) }
    }
  }

  async function resetPassword(token: string, password: string) {
    try {
      const { data } = await api.post<AuthResponse>('/auth/reset-password', { token, password })
      applyAuth(data)
      return { error: null }
    } catch (error: any) {
      return { error: new Error(error.response?.data?.detail || t('auth.reset.error')) }
    }
  }

  async function signOut() {
    clearAccessToken()
    user.value = null
    sessionUnverified.value = false
    clearApplicationContext()
    resetPostHog()
    return { error: null }
  }

  async function getCurrentUser() {
    return fetchMe()
  }

  async function deleteAccount() {
    loading.value = true
    try {
      await api.delete('/auth/me')
      clearAccessToken()
      user.value = null
      clearApplicationContext()
      resetPostHog()
      return { error: null }
    } catch (error: any) {
      return {
        error: new Error(error.response?.data?.detail || t('auth.errors.deleteFailed')),
      }
    } finally {
      loading.value = false
    }
  }

  return {
    user,
    loading,
    isAuthenticated,
    sessionUnverified,
    signUp,
    signIn,
    signInWithGoogle,
    completeGoogleCallback,
    verifyEmail,
    resendVerification,
    requestPasswordReset,
    resetPassword,
    signOut,
    deleteAccount,
    getCurrentUser,
    initializeAuth,
  }
})

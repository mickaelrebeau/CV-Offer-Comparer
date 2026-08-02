import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api, getApiBaseURL } from '@/lib/api'
import { clearAccessToken, getAccessToken, setAccessToken } from '@/lib/authToken'
import type { AuthResponse, AuthUser } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<AuthUser | null>(null)
  const loading = ref(true)
  let initPromise: Promise<void> | null = null

  const isAuthenticated = computed(() => !!user.value && !!getAccessToken())

  async function fetchMe(): Promise<AuthUser | null> {
    const token = getAccessToken()
    if (!token) {
      user.value = null
      return null
    }
    try {
      const { data } = await api.get<AuthUser>('/auth/me')
      user.value = data
      return data
    } catch {
      clearAccessToken()
      user.value = null
      return null
    }
  }

  async function initializeAuth() {
    if (initPromise) return initPromise

    initPromise = (async () => {
      loading.value = true
      try {
        // Token déjà présent dans l'URL du callback Google
        if (typeof window !== 'undefined') {
          const path = window.location.pathname
          const params = new URLSearchParams(window.location.search)
          const urlToken = params.get('token')
          if (path === '/auth/callback' && urlToken) {
            setAccessToken(urlToken)
          }
        }
        await fetchMe()
      } finally {
        loading.value = false
        initPromise = null
      }
    })()

    return initPromise
  }

  function applyAuth(payload: AuthResponse) {
    setAccessToken(payload.access_token)
    user.value = payload.user
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
        error: new Error(error.response?.data?.detail || 'Erreur lors de la création du compte'),
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
        error: new Error(error.response?.data?.detail || 'Email ou mot de passe incorrect'),
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

  async function completeGoogleCallback(token: string) {
    setAccessToken(token)
    // Ne pas toggler loading ici : ça détruisait la vue callback
    const me = await fetchMe()
    return !!me
  }

  async function signOut() {
    clearAccessToken()
    user.value = null
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
      return { error: null }
    } catch (error: any) {
      return {
        error: new Error(error.response?.data?.detail || 'Erreur lors de la suppression'),
      }
    } finally {
      loading.value = false
    }
  }

  return {
    user,
    loading,
    isAuthenticated,
    signUp,
    signIn,
    signInWithGoogle,
    completeGoogleCallback,
    signOut,
    deleteAccount,
    getCurrentUser,
    initializeAuth,
  }
})

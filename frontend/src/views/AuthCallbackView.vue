<template>
  <div class="flex min-h-[50vh] items-center justify-center px-6">
    <div class="space-y-3 text-center font-mono">
      <Loader2 class="mx-auto h-8 w-8 animate-spin text-ink-soft" />
      <p class="text-caption uppercase text-ink-soft">Connexion en cours</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Loader2 } from 'lucide-vue-next'
import posthog from 'posthog-js'
import { useAuthStore } from '@/stores/auth'

const isPostHogConfigured = Boolean(
  import.meta.env.VITE_POSTHOG_PROJECT_TOKEN && import.meta.env.VITE_POSTHOG_HOST,
)

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const handled = ref(false)

onMounted(async () => {
  if (handled.value) return
  handled.value = true

  if (authStore.loading) {
    await authStore.initializeAuth()
  }

  if (authStore.isAuthenticated) {
    router.replace('/dashboard')
    return
  }

  const code = typeof route.query.code === 'string' ? route.query.code : null
  // Retire le code de l'URL (historique, referrer, analytics) avant tout appel réseau
  window.history.replaceState(window.history.state, '', route.path)
  if (!code) {
    router.replace('/login?error=google_oauth')
    return
  }

  const ok = await authStore.completeGoogleCallback(code)
  if (ok && isPostHogConfigured) {
    posthog.capture('account_signed_in', { sign_in_method: 'google' })
  }
  router.replace(ok ? '/dashboard' : '/login?error=google_oauth')
})
</script>

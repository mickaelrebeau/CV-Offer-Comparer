<template>
  <div class="flex min-h-[50vh] items-center justify-center px-6">
    <div class="space-y-3 text-center font-mono">
      <Loader2 class="mx-auto h-8 w-8 animate-spin text-ink-soft" aria-hidden="true" />
      <p class="text-caption uppercase text-ink-soft">{{ t('auth.callback.connecting') }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { Loader2 } from 'lucide-vue-next'
import posthog from 'posthog-js'
import { useLocale } from '@/i18n/useLocale'
import { useAuthStore } from '@/stores/auth'

const isPostHogConfigured = Boolean(
  import.meta.env.VITE_POSTHOG_PROJECT_TOKEN && import.meta.env.VITE_POSTHOG_HOST,
)

const { t } = useI18n()
const { replace } = useLocale()
const route = useRoute()
const authStore = useAuthStore()
const handled = ref(false)

onMounted(async () => {
  if (handled.value) return
  handled.value = true

  if (authStore.loading) {
    await authStore.initializeAuth()
  }

  if (authStore.isAuthenticated) {
    replace('/dashboard')
    return
  }

  const code = typeof route.query.code === 'string' ? route.query.code : null
  // Retire le code de l'URL (historique, referrer, analytics) avant tout appel réseau
  window.history.replaceState(window.history.state, '', route.path)
  if (!code) {
    replace('/login?error=google_oauth')
    return
  }

  const ok = await authStore.completeGoogleCallback(code)
  if (ok && isPostHogConfigured) {
    posthog.capture('account_signed_in', { sign_in_method: 'google' })
  }
  replace(ok ? '/dashboard' : '/login?error=google_oauth')
})
</script>

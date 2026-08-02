<template>
  <div class="min-h-[50vh] flex items-center justify-center px-6">
    <div class="text-center space-y-3">
      <Loader2 class="h-8 w-8 animate-spin mx-auto text-muted-foreground" />
      <p class="text-sm text-muted-foreground">Connexion en cours…</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Loader2 } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const handled = ref(false)

onMounted(async () => {
  if (handled.value) return
  handled.value = true

  // Attendre la fin de l'init globale (qui peut déjà avoir consommé le token URL)
  if (authStore.loading) {
    await authStore.initializeAuth()
  }

  if (authStore.isAuthenticated) {
    router.replace('/dashboard')
    return
  }

  const token = typeof route.query.token === 'string' ? route.query.token : null
  if (!token) {
    router.replace('/login?error=google_oauth')
    return
  }

  const ok = await authStore.completeGoogleCallback(token)
  router.replace(ok ? '/dashboard' : '/login?error=google_oauth')
})
</script>

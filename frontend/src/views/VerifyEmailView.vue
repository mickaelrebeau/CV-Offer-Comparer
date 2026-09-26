<template>
  <div class="page-shell">
    <div class="mx-auto max-w-md">
      <AppPageHeader label="Compte" title="Vérification de l’adresse e-mail" />

      <div class="panel p-6 sm:p-8 space-y-6">
        <div v-if="status === 'pending'" class="flex items-center justify-center gap-3 font-mono text-caption uppercase text-ink-soft">
          <Loader2 class="h-5 w-5 animate-spin" aria-hidden="true" />
          Vérification en cours
        </div>

        <div role="status" v-else-if="status === 'success'" class="rounded-lg border border-emerald-500/25 bg-emerald-500/5 p-3 font-mono text-micro text-emerald-700">
          Adresse e-mail confirmée. Vous pouvez lancer vos analyses.
        </div>

        <div role="alert" v-else class="rounded-lg border border-rose-500/25 bg-rose-500/5 p-3 font-mono text-micro text-rose-700">
          {{ error }}
        </div>

        <Button
          v-if="status !== 'pending'"
          type="button"
          variant="full"
          size="lg"
          @click="router.replace(authStore.isAuthenticated ? '/dashboard' : '/login')"
        >
          {{ authStore.isAuthenticated ? 'Aller au tableau de bord' : 'Se connecter' }}
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppPageHeader from '@/components/AppPageHeader.vue'
import { Button } from '@/components/ui/button'
import { Loader2 } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const status = ref<'pending' | 'success' | 'error'>('pending')
const error = ref('')

onMounted(async () => {
  const token = typeof route.query.token === 'string' ? route.query.token : ''
  // Retire le jeton de l'URL (historique, referrer, analytics)
  window.history.replaceState(window.history.state, '', route.path)

  if (!token) {
    error.value = 'Lien de vérification incomplet.'
    status.value = 'error'
    return
  }

  const { error: verifyError } = await authStore.verifyEmail(token)
  if (verifyError) {
    error.value = `${verifyError.message}. Connectez-vous pour recevoir un nouveau lien.`
    status.value = 'error'
  } else {
    status.value = 'success'
  }
})
</script>

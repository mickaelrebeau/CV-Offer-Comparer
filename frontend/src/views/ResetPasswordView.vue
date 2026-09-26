<template>
  <div class="page-shell">
    <div class="mx-auto max-w-md">
      <AppPageHeader
        label="Accès"
        title="Nouveau mot de passe"
        description="Choisissez un nouveau mot de passe d’au moins 8 caractères."
      />

      <div class="panel p-6 sm:p-8 space-y-6">
        <template v-if="token">
          <form @submit.prevent="handleSubmit" class="space-y-4">
            <div class="space-y-1.5">
              <label for="password" class="field-label">Nouveau mot de passe</label>
              <Input id="password" v-model="password" type="password" required placeholder="••••••••" :show-password-toggle="true" />
            </div>

            <div class="space-y-1.5">
              <label for="confirm-password" class="field-label">Confirmer le mot de passe</label>
              <Input id="confirm-password" v-model="confirmPassword" type="password" required placeholder="••••••••" :show-password-toggle="true" />
            </div>

            <div v-if="error" class="rounded-lg border border-rose-500/25 bg-rose-500/5 p-3 font-mono text-micro text-rose-700">
              {{ error }}
            </div>

            <Button type="submit" variant="full" size="lg" :disabled="loading">
              <Loader2 v-if="loading" class="mr-2 h-4 w-4 animate-spin" />
              Enregistrer le mot de passe
            </Button>
          </form>
        </template>

        <div v-else class="rounded-lg border border-rose-500/25 bg-rose-500/5 p-3 font-mono text-micro text-rose-700">
          Lien de réinitialisation incomplet. Demandez un nouveau lien.
        </div>

        <p class="text-center font-mono text-micro uppercase text-ink-soft">
          <router-link to="/forgot-password" class="text-ink hover:underline">Demander un nouveau lien</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppPageHeader from '@/components/AppPageHeader.vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Loader2 } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const token = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)

onMounted(() => {
  token.value = typeof route.query.token === 'string' ? route.query.token : ''
  // Retire le jeton de l'URL (historique, referrer, analytics)
  window.history.replaceState(window.history.state, '', route.path)
})

async function handleSubmit() {
  if (password.value.length < 8) {
    error.value = 'Le mot de passe doit contenir au moins 8 caractères'
    return
  }
  if (password.value !== confirmPassword.value) {
    error.value = 'Les mots de passe ne correspondent pas'
    return
  }

  loading.value = true
  error.value = ''

  const { error: resetError } = await authStore.resetPassword(token.value, password.value)
  if (resetError) {
    error.value = resetError.message
    loading.value = false
    return
  }

  router.replace('/dashboard')
}
</script>

<template>
  <div class="page-shell">
    <div class="mx-auto max-w-md">
      <AppPageHeader
        label="Accès"
        title="Connexion"
        description="Accédez à votre espace de comparaison et à vos historiques."
      />

      <div class="panel p-6 sm:p-8 space-y-6">
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div class="space-y-1.5">
            <label for="email" class="field-label">Adresse email</label>
            <Input id="email" v-model="email" type="email" required placeholder="nom@exemple.com" />
          </div>

          <div class="space-y-1.5">
            <label for="password" class="field-label">Mot de passe</label>
            <Input id="password" v-model="password" type="password" required placeholder="••••••••" :show-password-toggle="true" />
          </div>

          <div v-if="error" class="rounded-lg border border-rose-500/25 bg-rose-500/5 p-3 font-mono text-micro text-rose-700">
            {{ error }}
          </div>

          <Button type="submit" variant="full" size="lg" :disabled="loading">
            <Loader2 v-if="loading" class="mr-2 h-4 w-4 animate-spin" />
            Se connecter
          </Button>
        </form>

        <div class="relative">
          <div class="absolute inset-0 flex items-center"><span class="w-full border-t border-ink/10" /></div>
          <div class="relative flex justify-center font-mono text-micro uppercase">
            <span class="bg-paper px-2 text-ink-soft">Ou continuer avec</span>
          </div>
        </div>

        <Button type="button" variant="full-outline" size="lg" :disabled="loading" @click="handleGoogleLogin">
          <svg v-if="!loading" class="mr-2 h-4 w-4 shrink-0" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
          </svg>
          <Loader2 v-if="loading" class="mr-2 h-4 w-4 animate-spin" />
          Continuer avec Google
        </Button>

        <p class="text-center font-mono text-micro uppercase text-ink-soft">
          Pas encore de compte ?
          <router-link to="/register" class="text-ink hover:underline">Créer un compte</router-link>
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

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

onMounted(() => {
  if (route.query.error === 'google_oauth') {
    const reason = typeof route.query.reason === 'string' ? route.query.reason : ''
    const hints: Record<string, string> = {
      no_code: 'Google n’a pas renvoyé de code. Vérifie les URI de redirection dans la console Google.',
      exchange_failed: 'Échange du code Google échoué. Vérifie GOOGLE_CLIENT_SECRET et l’URI localhost dans Google Cloud.',
      server_error: 'Erreur serveur pendant l’auth Google. Regarde les logs uvicorn.',
    }
    error.value =
      hints[reason] ||
      'Connexion Google impossible. Réessayez ou utilisez email / mot de passe.'
  }
})

async function handleLogin() {
  loading.value = true
  error.value = ''

  const { error: loginError } = await authStore.signIn(email.value, password.value)

  if (loginError) {
    error.value = 'Email ou mot de passe incorrect'
  } else {
    router.push('/dashboard')
  }

  loading.value = false
}

async function handleGoogleLogin() {
  loading.value = true
  error.value = ''

  const { error: googleError } = await authStore.signInWithGoogle()

  if (googleError) {
    error.value = 'Erreur lors de la connexion avec Google'
    loading.value = false
  }
}
</script>

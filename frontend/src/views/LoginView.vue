<template>
  <div class="max-w-md mx-auto mt-12">
    <Card>
      <CardHeader>
        <CardTitle>Connexion</CardTitle>
        <CardDescription>
          Connectez-vous pour accéder au comparateur
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label for="email" class="block text-sm font-medium mb-2">
              Email
            </label>
            <Input id="email" v-model="email" type="email" required placeholder="votre@email.com" />
          </div>

          <div>
            <label for="password" class="block text-sm font-medium mb-2">
              Mot de passe
            </label>
            <Input id="password" v-model="password" type="password" required placeholder="Votre mot de passe"
              :show-password-toggle="true" />
          </div>

          <div v-if="error" class="text-destructive text-sm">
            {{ error }}
          </div>

          <div class="mt-10" />

          <Button type="submit" variant="full" size="lg" :disabled="loading">
            <Loader2 v-if="loading" class="mr-2 h-4 w-4 animate-spin" />
            Se connecter
          </Button>
        </form>

        <div class="relative my-6">
          <div class="absolute inset-0 flex items-center">
            <span class="w-full border-t" />
          </div>
          <div class="relative flex justify-center text-xs uppercase">
            <span class="bg-background px-2 text-muted-foreground">
              Ou
            </span>
          </div>
        </div>

        <Button type="button" variant="full" size="lg"
          :disabled="loading" @click="handleGoogleLogin">
          <svg v-if="!loading" class="mr-2 h-4 w-4" viewBox="0 0 24 24">
            <path fill="currentColor"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
            <path fill="currentColor"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
            <path fill="currentColor"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
            <path fill="currentColor"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
          </svg>
          <Loader2 v-if="loading" class="mr-2 h-4 w-4 animate-spin" />
          Continuer avec Google
        </Button>

        <div class="mt-6 text-center">
          <p class="text-sm text-muted-foreground">
            Pas encore de compte ?
            <router-link to="/register" class="text-primary hover:underline">
              Créer un compte
            </router-link>
          </p>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Loader2 } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

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
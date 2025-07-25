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

          <Button type="submit" variant="default" size="lg" :disabled="loading"
            class="py-2 px-4 w-full bg-primary hover:bg-primary/90 text-white rounded-md">
            <Loader2 v-if="loading" class="mr-2 h-4 w-4 animate-spin" />
            Se connecter
          </Button>
        </form>

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
    router.push('/compare')
  }
  
  loading.value = false
}
</script> 
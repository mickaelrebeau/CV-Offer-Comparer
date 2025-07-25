<template>
  <div class="max-w-md mx-auto mt-12">
    <Card>
      <CardHeader>
        <CardTitle>Créer un compte</CardTitle>
        <CardDescription>
          Inscrivez-vous pour accéder au comparateur
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form @submit.prevent="handleRegister" class="space-y-4">
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
            <Input id="password" v-model="password" type="password" required minlength="6"
              placeholder="Au moins 6 caractères" :show-password-toggle="true" />
          </div>

          <div>
            <label for="confirmPassword" class="block text-sm font-medium mb-2">
              Confirmer le mot de passe
            </label>
            <Input id="confirmPassword" v-model="confirmPassword" type="password" required
              placeholder="Confirmez votre mot de passe" :show-password-toggle="true" />
          </div>

          <div v-if="error" class="text-destructive text-sm">
            {{ error }}
          </div>

          <div v-if="success" class="text-match text-sm">
            {{ success }}
          </div>

          <div class="mt-10"/>

          <Button type="submit" variant="default" size="lg" :disabled="loading"
            class="py-2 px-4 w-full bg-primary hover:bg-primary/90 text-white rounded-md">
            <Loader2 v-if="loading" class="mr-2 h-4 w-4 animate-spin" />
            Créer un compte
          </Button>
        </form>

        <div class="mt-6 text-center">
          <p class="text-sm text-muted-foreground">
            Déjà un compte ?
            <router-link to="/login" class="text-primary hover:underline">
              Se connecter
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
const confirmPassword = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)

async function handleRegister() {
  if (password.value !== confirmPassword.value) {
    error.value = 'Les mots de passe ne correspondent pas'
    return
  }

  if (password.value.length < 6) {
    error.value = 'Le mot de passe doit contenir au moins 6 caractères'
    return
  }

  loading.value = true
  error.value = ''
  success.value = ''

  const { error: registerError } = await authStore.signUp(email.value, password.value)
  
  if (registerError) {
    error.value = 'Erreur lors de la création du compte'
  } else {
    success.value = 'Compte créé avec succès ! Vérifiez votre email pour confirmer votre compte.'
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  }
  
  loading.value = false
}
</script> 
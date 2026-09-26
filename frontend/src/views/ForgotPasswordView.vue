<template>
  <div class="page-shell">
    <div class="mx-auto max-w-md">
      <AppPageHeader
        label="Accès"
        title="Mot de passe oublié"
        description="Indiquez votre adresse : nous vous envoyons un lien pour choisir un nouveau mot de passe."
      />

      <div class="panel p-6 sm:p-8 space-y-6">
        <div v-if="sent" class="rounded-lg border border-emerald-500/25 bg-emerald-500/5 p-3 font-mono text-micro text-emerald-700">
          {{ sent }}
        </div>

        <form v-else @submit.prevent="handleSubmit" class="space-y-4">
          <div class="space-y-1.5">
            <label for="email" class="field-label">Adresse email</label>
            <Input id="email" v-model="email" type="email" required placeholder="nom@exemple.com" />
          </div>

          <div v-if="error" class="rounded-lg border border-rose-500/25 bg-rose-500/5 p-3 font-mono text-micro text-rose-700">
            {{ error }}
          </div>

          <Button type="submit" variant="full" size="lg" :disabled="loading">
            <Loader2 v-if="loading" class="mr-2 h-4 w-4 animate-spin" />
            Envoyer le lien
          </Button>
        </form>

        <p class="text-center font-mono text-micro uppercase text-ink-soft">
          <router-link to="/login" class="text-ink hover:underline">Retour à la connexion</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppPageHeader from '@/components/AppPageHeader.vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Loader2 } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const email = ref('')
const error = ref('')
const sent = ref('')
const loading = ref(false)

async function handleSubmit() {
  loading.value = true
  error.value = ''

  const { message, error: requestError } = await authStore.requestPasswordReset(email.value)
  if (requestError) {
    error.value = requestError.message
  } else {
    sent.value = message || 'Si un compte existe pour cette adresse, un e-mail vient d’être envoyé.'
  }

  loading.value = false
}
</script>

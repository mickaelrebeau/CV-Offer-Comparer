<template>
  <div
    v-if="visible"
    class="border-b border-amber-500/25 bg-amber-500/5 px-5 py-2.5 font-mono text-micro text-amber-800 sm:px-8 lg:px-16"
    role="status"
  >
    <div class="mx-auto flex max-w-[100rem] flex-wrap items-center justify-between gap-2">
      <p>
        Confirmez votre adresse e-mail ({{ authStore.user?.email }}) pour lancer des analyses et des simulations d’entretien.
      </p>
      <div class="flex items-center gap-3">
        <span v-if="feedback">{{ feedback }}</span>
        <button
          v-else
          type="button"
          class="uppercase underline-offset-2 hover:underline disabled:opacity-50"
          :disabled="sending"
          @click="resend"
        >
          {{ sending ? 'Envoi…' : 'Renvoyer le lien' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const sending = ref(false)
const feedback = ref('')

const visible = computed(() => authStore.isAuthenticated && authStore.user?.email_verified === false)

async function resend() {
  sending.value = true
  const { message, error } = await authStore.resendVerification()
  feedback.value = error ? error.message : message || 'E-mail envoyé'
  sending.value = false
}
</script>

<template>
  <div
    v-if="visible"
    class="fixed inset-x-0 bottom-0 z-[90] px-4 pb-4 sm:px-6 sm:pb-6"
    role="dialog"
    aria-modal="false"
    aria-labelledby="cookie-consent-title"
    aria-describedby="cookie-consent-desc"
  >
    <div class="mx-auto flex max-w-3xl flex-col gap-4 rounded-xl border border-ink/15 bg-paper p-5 shadow-[0_20px_50px_-24px_rgba(35,35,35,0.45)] sm:flex-row sm:items-end sm:justify-between sm:p-6">
      <div class="min-w-0 space-y-2">
        <p id="cookie-consent-title" class="font-mono text-micro uppercase text-ink">
          Cookies &amp; mesure d’usage
        </p>
        <p id="cookie-consent-desc" class="max-w-[52ch] text-sm leading-relaxed text-ink-soft">
          Nous utilisons PostHog (UE) pour comprendre l’usage du produit et diagnostiquer les erreurs.
          Acceptez pour activer les cookies / stockage local ; refusez pour un suivi anonymisé sans cookies.
          Détails dans la
          <RouterLink to="/confidentialite" class="text-ink underline underline-offset-2">politique de confidentialité</RouterLink>.
        </p>
      </div>
      <div class="flex shrink-0 flex-col gap-2 sm:flex-row">
        <button type="button" class="btn-secondary !h-10 !px-4 !text-micro" @click="decline">
          Refuser
        </button>
        <button type="button" class="btn-primary !h-10 !px-4 !text-micro" @click="accept">
          Accepter
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import {
  acceptAnalytics,
  declineAnalytics,
  getConsentStatus,
  isAnalyticsConfigured,
} from '@/lib/analytics'

const visible = ref(false)

onMounted(() => {
  if (!isAnalyticsConfigured) return
  // Afficher dès qu’aucun choix explicite n’a été fait (pending).
  // 'unavailable' ne devrait plus arriver après init dans main.ts.
  const status = getConsentStatus()
  visible.value = status === 'pending' || status === 'unavailable'
})

function accept() {
  acceptAnalytics()
  visible.value = false
}

function decline() {
  declineAnalytics()
  visible.value = false
}
</script>

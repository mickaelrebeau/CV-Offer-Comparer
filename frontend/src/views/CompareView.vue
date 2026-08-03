<template>
  <div class="page-shell">
    <AppPageHeader
      label="Comparateur"
      title="CV ↔ Offre d'emploi"
      description="Évaluez l'adéquation sémantique exacte entre votre profil et la fiche de poste."
    />
    <div
      v-if="historyLoading"
      class="panel mb-6 p-4 font-mono text-micro uppercase text-ink-soft"
    >
      Chargement de l'historique…
    </div>
    <ComparisonView />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppPageHeader from '@/components/AppPageHeader.vue'
import ComparisonView from '@/components/ComparisonView.vue'
import { useCompareStore } from '@/stores/compare'

const route = useRoute()
const router = useRouter()
const compareStore = useCompareStore()
const historyLoading = ref(false)

onMounted(async () => {
  const historyId = typeof route.query.history === 'string' ? route.query.history : null
  if (!historyId) return

  historyLoading.value = true
  try {
    await compareStore.loadFromHistory(historyId)
    router.replace({ path: '/compare', query: {} })
  } catch {
    // L'erreur est déjà exposée par le store
  } finally {
    historyLoading.value = false
  }
})
</script>

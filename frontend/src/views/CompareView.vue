<template>
  <div class="page-shell">
    <AppPageHeader
      :label="t('compare.label')"
      :title="t('compare.title')"
      :description="t('compare.description')"
    />
    <AppStatus v-if="historyLoading" class="mb-6" kind="loading" :message="t('compare.historyLoading')" />
    <AppStatus
      v-else-if="historyError"
      class="mb-6"
      kind="error"
      :message="historyError"
      :action-label="t('common.retry')"
      @action="pendingHistoryId && loadHistory(pendingHistoryId)"
    />
    <ApplicationContextBanner
      edit-target="compare-offer"
      :proposal="compareStore.historyContext"
      @adopt="compareStore.adoptHistoryContext"
      @dismiss="compareStore.dismissHistoryContext"
    />
    <ComparisonView />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import AppPageHeader from '@/components/AppPageHeader.vue'
import AppStatus from '@/components/AppStatus.vue'
import ApplicationContextBanner from '@/components/ApplicationContextBanner.vue'
import ComparisonView from '@/components/ComparisonView.vue'
import { useLocale } from '@/i18n/useLocale'
import { isOnline } from '@/lib/pwa'
import { useApplicationContextStore } from '@/stores/applicationContext'
import { useCompareStore } from '@/stores/compare'

const { t } = useI18n()
const { replace } = useLocale()
const route = useRoute()
const compareStore = useCompareStore()
const context = useApplicationContextStore()
const historyLoading = ref(false)
const pendingHistoryId = ref<string | null>(null)
const historyError = ref('')

// Réanalyse demandée depuis l'historique (/compare?history=…&rescore=1)
const rescoreRequested = ref(false)

// Deep link /compare?history=… : l'id est gardé tant que le chargement échoue (hors ligne)
async function loadHistory(historyId: string) {
  historyLoading.value = true
  historyError.value = ''
  try {
    await compareStore.loadFromHistory(historyId)
    if (rescoreRequested.value) compareStore.startRescore()
    rescoreRequested.value = false
    pendingHistoryId.value = null
    replace({ path: '/compare', query: {} })
  } catch {
    // Affichée ici (avec relance) plutôt que sous le formulaire ; nouvel essai au retour du réseau
    historyError.value = compareStore.error || t('comparison.errors.loadHistory')
    compareStore.error = null
    pendingHistoryId.value = historyId
  } finally {
    historyLoading.value = false
  }
}

onMounted(() => {
  context.trackReuse('compare')
  const historyId = typeof route.query.history === 'string' ? route.query.history : null
  rescoreRequested.value = route.query.rescore === '1'
  if (historyId) loadHistory(historyId)
})

watch(isOnline, (online) => {
  if (online && pendingHistoryId.value) loadHistory(pendingHistoryId.value)
})
</script>

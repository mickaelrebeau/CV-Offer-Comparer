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
    <ComparisonView />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import AppPageHeader from '@/components/AppPageHeader.vue'
import AppStatus from '@/components/AppStatus.vue'
import ComparisonView from '@/components/ComparisonView.vue'
import { useLocale } from '@/i18n/useLocale'
import { isOnline } from '@/lib/pwa'
import { useCompareStore } from '@/stores/compare'

const { t } = useI18n()
const { replace } = useLocale()
const route = useRoute()
const compareStore = useCompareStore()
const historyLoading = ref(false)
const pendingHistoryId = ref<string | null>(null)
const historyError = ref('')

// Deep link /compare?history=… : l'id est gardé tant que le chargement échoue (hors ligne)
async function loadHistory(historyId: string) {
  historyLoading.value = true
  historyError.value = ''
  try {
    await compareStore.loadFromHistory(historyId)
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
  const historyId = typeof route.query.history === 'string' ? route.query.history : null
  if (historyId) loadHistory(historyId)
})

watch(isOnline, (online) => {
  if (online && pendingHistoryId.value) loadHistory(pendingHistoryId.value)
})
</script>

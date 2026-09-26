<template>
  <div class="page-shell">
    <AppPageHeader
      :label="t('compare.label')"
      :title="t('compare.title')"
      :description="t('compare.description')"
    />
    <div
      v-if="historyLoading"
      class="panel mb-6 p-4 font-mono text-micro uppercase text-ink-soft"
    >
      {{ t('compare.historyLoading') }}
    </div>
    <ComparisonView />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import AppPageHeader from '@/components/AppPageHeader.vue'
import ComparisonView from '@/components/ComparisonView.vue'
import { useLocale } from '@/i18n/useLocale'
import { useCompareStore } from '@/stores/compare'

const { t } = useI18n()
const { replace } = useLocale()
const route = useRoute()
const compareStore = useCompareStore()
const historyLoading = ref(false)

onMounted(async () => {
  const historyId = typeof route.query.history === 'string' ? route.query.history : null
  if (!historyId) return

  historyLoading.value = true
  try {
    await compareStore.loadFromHistory(historyId)
    replace({ path: '/compare', query: {} })
  } catch {
    // L'erreur est déjà exposée par le store
  } finally {
    historyLoading.value = false
  }
})
</script>

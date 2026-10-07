<template>
  <div class="page-shell">
    <AppPageHeader
      :label="t('applications.label')"
      :title="detailId ? t('applications.detailHeading') : t('applications.title')"
      :description="t('applications.description')"
    />
    <!-- Fiche (?id=…) ou tableau des candidatures -->
    <ApplicationDetail v-if="detailId" :id="detailId" />
    <ApplicationsBoard v-else @created="(id) => push(`/applications?id=${id}`)" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import AppPageHeader from '@/components/AppPageHeader.vue'
import ApplicationDetail from '@/components/applications/ApplicationDetail.vue'
import ApplicationsBoard from '@/components/applications/ApplicationsBoard.vue'
import { useLocale } from '@/i18n/useLocale'
import { isOnline } from '@/lib/pwa'
import { useApplicationsStore } from '@/stores/applications'

const { t } = useI18n()
const { push } = useLocale()
const route = useRoute()
const store = useApplicationsStore()

const detailId = computed(() => (typeof route.query.id === 'string' ? route.query.id : null))

// Retour à la liste : statuts et compteurs à jour
watch(detailId, (id) => {
  if (!id) store.fetch()
})

onMounted(() => {
  if (!detailId.value) store.fetch()
})

watch(isOnline, (online) => {
  if (online && store.error) store.fetch()
})
</script>

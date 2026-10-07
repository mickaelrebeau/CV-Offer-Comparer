<template>
  <!-- Rendu uniquement à l'impression ; placé sous <body> pour que le reste de l'application soit masqué -->
  <Teleport to="body">
    <article class="print-report" :lang="locale">
      <header class="print-report-header">
        <p class="print-report-brand">Talento</p>
        <h1 class="print-report-title">{{ title }}</h1>
        <p class="print-report-date">{{ t('report.generatedOn', { date: formatDate(meta.date, { dateStyle: 'long' }) }) }}</p>
      </header>

      <section v-if="meta.offerText.trim() || meta.offerUrl" class="print-report-section">
        <h2>{{ t('report.offer') }}</h2>
        <p v-if="meta.offerUrl" class="print-report-source">
          {{ t('report.source') }} <span class="print-report-url">{{ meta.offerUrl }}</span>
        </p>
        <p v-if="meta.offerText.trim()" class="print-report-excerpt">{{ offerExcerpt(meta.offerText) }}</p>
      </section>

      <slot />
    </article>
  </Teleport>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useLocale } from '@/i18n/useLocale'
import { offerExcerpt, type ReportMeta } from '@/lib/report'

defineProps<{ title: string; meta: ReportMeta }>()

const { t } = useI18n()
const { locale, formatDate } = useLocale()
</script>

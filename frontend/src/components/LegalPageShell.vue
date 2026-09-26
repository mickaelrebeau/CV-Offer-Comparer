<template>
  <div class="page-shell">
    <AppPageHeader :label="label" :title="title" :description="description" />
    <article class="panel prose-legal mx-auto max-w-3xl space-y-8 p-6 sm:p-10">
      <p class="font-mono text-micro uppercase text-ink-soft">
        {{ t('legal.updatedAt', { date: formatDate(updatedAt, { dateStyle: 'long' }) }) }}
      </p>
      <p
        v-if="locale !== 'fr'"
        role="note"
        class="rounded-lg border border-amber-500/25 bg-amber-500/5 p-4 text-sm text-amber-800"
      >
        {{ t('legal.frenchPrevails') }}
        <RouterLink :to="frenchPath" lang="fr" class="font-medium underline underline-offset-2">{{ t('legal.viewFrench') }}</RouterLink>
      </p>
      <slot />
    </article>
    <nav class="mx-auto mt-10 flex max-w-3xl flex-wrap gap-4 font-mono text-micro uppercase text-ink-soft">
      <RouterLink :to="localePath('/mentions-legales')" class="hover:text-ink">{{ t('legal.legalNotice') }}</RouterLink>
      <RouterLink :to="localePath('/cgv')" class="hover:text-ink">{{ t('legal.terms') }}</RouterLink>
      <RouterLink :to="localePath('/confidentialite')" class="hover:text-ink">{{ t('legal.privacy') }}</RouterLink>
      <RouterLink :to="localePath('/')" class="hover:text-ink">{{ t('legal.home') }}</RouterLink>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import AppPageHeader from '@/components/AppPageHeader.vue'
import { localizePath } from '@/i18n/routing'
import { useLocale } from '@/i18n/useLocale'

const { t } = useI18n()
const { locale, localePath, formatDate } = useLocale()
const route = useRoute()
const frenchPath = computed(() => localizePath(route.path, 'fr'))

defineProps<{
  label: string
  title: string
  description: string
  /** Date ISO (AAAA-MM-JJ), formatée selon la langue */
  updatedAt: string
}>()
</script>

<style scoped>
.prose-legal :deep(h2) {
  margin-top: 1.75rem;
  font-size: clamp(1.25rem, 2vw, 1.5rem);
  font-weight: 500;
  letter-spacing: -0.015em;
}
.prose-legal :deep(h3) {
  margin-top: 1.25rem;
  font-size: 1rem;
  font-weight: 500;
}
.prose-legal :deep(p),
.prose-legal :deep(li) {
  color: #5e5c57;
  line-height: 1.65;
  font-size: 1.05rem;
}
.prose-legal :deep(ul) {
  list-style: disc;
  padding-left: 1.25rem;
  display: grid;
  gap: 0.4rem;
}
.prose-legal :deep(a) {
  color: #232323;
  text-decoration: underline;
  text-underline-offset: 3px;
}
.prose-legal :deep(strong) {
  color: #232323;
  font-weight: 500;
}
</style>

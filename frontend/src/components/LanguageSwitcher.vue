<template>
  <div role="group" :aria-label="t('language.label')" class="flex items-center gap-1 font-mono text-micro uppercase">
    <button
      v-for="option in LOCALES"
      :key="option"
      type="button"
      :lang="option"
      :aria-pressed="option === locale"
      :aria-label="t(`language.switchTo.${option}`)"
      :title="isAvailable(option) ? undefined : t('language.unavailable')"
      :disabled="!isAvailable(option)"
      class="rounded px-1.5 py-0.5 transition-colors disabled:cursor-not-allowed disabled:opacity-40"
      :class="option === locale ? 'bg-ink text-paper' : 'text-ink-soft hover:text-ink'"
      @click="switchTo(option)"
    >
      {{ option }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { LOCALES, DEFAULT_LOCALE, type Locale } from '@/i18n'
import { hasEnglishVersion, localizePath } from '@/i18n/routing'
import { useLocale } from '@/i18n/useLocale'
import { STORAGE_KEYS } from '@/lib/storageKeys'

const { t } = useI18n()
const { locale } = useLocale()
const route = useRoute()
const router = useRouter()

const isAvailable = (option: Locale) => option === DEFAULT_LOCALE || hasEnglishVersion(route.path)

function switchTo(option: Locale) {
  if (option === locale.value || !isAvailable(option)) return
  try {
    localStorage.setItem(STORAGE_KEYS.locale, option)
  } catch {
    // Préférence non mémorisée (stockage indisponible) : la bascule fonctionne quand même
  }
  router.push({ path: localizePath(route.path, option), query: route.query, hash: route.hash })
}
</script>

import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, type RouteLocationRaw } from 'vue-router'
import { LOCALE_TAGS, isLocale, DEFAULT_LOCALE, type Locale } from '@/i18n'
import { localizePath, localizeRoute } from '@/i18n/routing'

/** Langue active + helpers de navigation et de formatage localisés. */
export function useLocale() {
  const { locale: i18nLocale } = useI18n()
  const router = useRouter()

  const locale = computed<Locale>(() => (isLocale(i18nLocale.value) ? i18nLocale.value : DEFAULT_LOCALE))
  const intlTag = computed(() => LOCALE_TAGS[locale.value].intl)

  return {
    locale,
    localePath: (path: string) => localizePath(path, locale.value),
    push: (to: RouteLocationRaw) => router.push(localizeRoute(to, locale.value)),
    replace: (to: RouteLocationRaw) => router.replace(localizeRoute(to, locale.value)),
    formatDate: (value: string | null | undefined, options: Intl.DateTimeFormatOptions = { dateStyle: 'medium', timeStyle: 'short' }) =>
      value ? new Intl.DateTimeFormat(intlTag.value, options).format(new Date(value)) : '—',
    formatNumber: (value: number, options?: Intl.NumberFormatOptions) =>
      Number.isFinite(value) ? new Intl.NumberFormat(intlTag.value, options).format(value) : '—',
    formatPercent: (ratio: number) =>
      new Intl.NumberFormat(intlTag.value, { style: 'percent', maximumFractionDigits: 0 }).format(ratio),
  }
}

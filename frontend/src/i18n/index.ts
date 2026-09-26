import { createI18n, type I18n } from 'vue-i18n'
import en from '@/locales/en.json'
import fr from '@/locales/fr.json'

export const LOCALES = ['fr', 'en'] as const
export type Locale = (typeof LOCALES)[number]
export const DEFAULT_LOCALE: Locale = 'fr'

/** Balises BCP 47 pour Intl, og:locale et hreflang. */
export const LOCALE_TAGS: Record<Locale, { intl: string; og: string }> = {
  fr: { intl: 'fr-FR', og: 'fr_FR' },
  en: { intl: 'en-GB', og: 'en_GB' },
}

export function isLocale(value: unknown): value is Locale {
  return typeof value === 'string' && (LOCALES as readonly string[]).includes(value)
}

type AppI18n = I18n<{ fr: typeof fr; en: typeof en }, object, object, Locale, false>

// Instance du navigateur, pour les stores et lib/api (hors composants).
// Côté SSR, chaque page a sa propre instance (vite-ssg rend les pages en parallèle).
let clientI18n: AppI18n | null = null

export function createAppI18n(locale: Locale = DEFAULT_LOCALE): AppI18n {
  const i18n = createI18n({
    legacy: false,
    locale,
    fallbackLocale: DEFAULT_LOCALE,
    messages: { fr, en },
  }) as AppI18n
  if (!import.meta.env.SSR) clientI18n = i18n
  return i18n
}

export function currentLocale(): Locale {
  const locale = clientI18n?.global.locale.value
  return isLocale(locale) ? locale : DEFAULT_LOCALE
}

/** Traduction hors composant (stores, lib/api) : côté client uniquement. */
export function t(key: string, params: Record<string, unknown> = {}): string {
  return clientI18n ? clientI18n.global.t(key, params) : key
}

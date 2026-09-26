import type { RouteLocationRaw } from 'vue-router'
import { DEFAULT_LOCALE, type Locale } from '@/i18n'
import { EN_PREFIX, englishPaths } from '@/router'

/** Chemin sans préfixe de langue : /en/login → /login, /en → /. */
export function stripLocale(path: string): string {
  if (path === EN_PREFIX) return '/'
  return path.startsWith(`${EN_PREFIX}/`) ? path.slice(EN_PREFIX.length) : path
}

export function localeOfPath(path: string): Locale {
  return stripLocale(path) === path ? DEFAULT_LOCALE : 'en'
}

/** La page existe-t-elle en anglais ? (pages non traduites : restent en français) */
export function hasEnglishVersion(path: string): boolean {
  return englishPaths.has(stripLocale(path))
}

/**
 * Chemin dans la langue demandée, query et hash conservés.
 * Une page sans version anglaise garde son URL française.
 */
export function localizePath(target: string, locale: Locale): string {
  const match = target.match(/^([^?#]*)(.*)$/)
  const path = match?.[1] || '/'
  const suffix = match?.[2] || ''
  const base = stripLocale(path)
  if (locale === DEFAULT_LOCALE || !englishPaths.has(base)) return `${base}${suffix}`
  return `${base === '/' ? EN_PREFIX : `${EN_PREFIX}${base}`}${suffix}`
}

export function localizeRoute(to: RouteLocationRaw, locale: Locale): RouteLocationRaw {
  if (typeof to === 'string') return localizePath(to, locale)
  if ('path' in to && typeof to.path === 'string') return { ...to, path: localizePath(to.path, locale) }
  return to
}

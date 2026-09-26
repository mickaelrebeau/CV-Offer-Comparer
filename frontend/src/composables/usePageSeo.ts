import { computed, type MaybeRefOrGetter, toValue } from 'vue'
import { useHead } from '@unhead/vue'
import { useI18n } from 'vue-i18n'
import { DEFAULT_LOCALE, LOCALE_TAGS, isLocale } from '@/i18n'
import { hasEnglishVersion, localizePath } from '@/i18n/routing'
import {
  SITE_DESCRIPTION,
  SITE_NAME,
  SITE_URL,
  absoluteUrl,
} from '@/lib/site'

export type PageSeoInput = {
  title?: string
  description?: string
  path?: string
  image?: string
  noindex?: boolean
  type?: 'website' | 'article'
  jsonLd?: Record<string, unknown> | Record<string, unknown>[]
}

export function usePageSeo(input: MaybeRefOrGetter<PageSeoInput>) {
  const { t, locale: i18nLocale } = useI18n()

  useHead(
    computed(() => {
      const seo = toValue(input)
      const locale = isLocale(i18nLocale.value) ? i18nLocale.value : DEFAULT_LOCALE
      const title = seo.title
        ? `${seo.title} · ${SITE_NAME}`
        : `${SITE_NAME} — ${t('seo.default.tagline')}`
      const description = seo.description || t('seo.default.description')
      const path = seo.path || '/'
      const url = absoluteUrl(path)
      const image = seo.image || absoluteUrl('/og.png')
      const robots = seo.noindex ? 'noindex, nofollow' : 'index, follow'
      const jsonLd = seo.jsonLd
        ? Array.isArray(seo.jsonLd)
          ? seo.jsonLd
          : [seo.jsonLd]
        : []

      // hreflang : seulement si la page existe dans les deux langues (x-default = français)
      const alternates = hasEnglishVersion(path)
        ? [
            { key: 'hreflang-fr', rel: 'alternate', hreflang: 'fr', href: absoluteUrl(localizePath(path, 'fr')) },
            { key: 'hreflang-en', rel: 'alternate', hreflang: 'en', href: absoluteUrl(localizePath(path, 'en')) },
            { key: 'hreflang-x-default', rel: 'alternate', hreflang: 'x-default', href: absoluteUrl(localizePath(path, 'fr')) },
          ]
        : []
      const otherLocale = locale === 'fr' ? 'en' : 'fr'

      return {
        title,
        htmlAttrs: { lang: locale },
        meta: [
          { name: 'description', content: description },
          { name: 'robots', content: robots },
          { name: 'author', content: 'Mickael Rébeau' },
          { name: 'theme-color', content: '#F1EEE7' },
          { property: 'og:type', content: seo.type || 'website' },
          { property: 'og:site_name', content: SITE_NAME },
          { property: 'og:locale', content: LOCALE_TAGS[locale].og },
          ...(alternates.length
            ? [{ property: 'og:locale:alternate', content: LOCALE_TAGS[otherLocale].og }]
            : []),
          { property: 'og:title', content: title },
          { property: 'og:description', content: description },
          { property: 'og:url', content: url },
          { property: 'og:image', content: image },
          { name: 'twitter:card', content: 'summary_large_image' },
          { name: 'twitter:title', content: title },
          { name: 'twitter:description', content: description },
          { name: 'twitter:image', content: image },
        ],
        link: [{ key: 'canonical', rel: 'canonical', href: url }, ...alternates],
        script: jsonLd.map((schema) => ({
          // Clé stable : unhead remplace ou retire ces scripts (shell SPA servi avec le head de l'accueil)
          key: `ld-${schema['@type']}`,
          type: 'application/ld+json',
          innerHTML: JSON.stringify(schema),
        })),
      }
    }),
  )
}

export function buildWebSiteJsonLd() {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: SITE_NAME,
    url: SITE_URL,
    description: SITE_DESCRIPTION,
    inLanguage: 'fr-FR',
    publisher: {
      '@type': 'Person',
      name: 'Mickael Rébeau',
      url: 'https://github.com/mickaelrebeau',
    },
  }
}

export function buildSoftwareJsonLd() {
  return {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    name: SITE_NAME,
    applicationCategory: 'BusinessApplication',
    operatingSystem: 'Web',
    url: SITE_URL,
    description: SITE_DESCRIPTION,
    offers: {
      '@type': 'Offer',
      price: '0',
      priceCurrency: 'EUR',
    },
    license: 'https://opensource.org/licenses/MIT',
    author: {
      '@type': 'Person',
      name: 'Mickael Rébeau',
      url: 'https://github.com/mickaelrebeau',
    },
  }
}

export function buildFaqJsonLd(items: { question: string; answer: string }[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: items.map((item) => ({
      '@type': 'Question',
      name: item.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: item.answer,
      },
    })),
  }
}

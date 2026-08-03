import { computed, type MaybeRefOrGetter, toValue } from 'vue'
import { useHead } from '@vueuse/head'
import {
  SITE_DESCRIPTION,
  SITE_NAME,
  SITE_TAGLINE,
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
  useHead(
    computed(() => {
      const seo = toValue(input)
      const title = seo.title
        ? `${seo.title} · ${SITE_NAME}`
        : `${SITE_NAME} — ${SITE_TAGLINE}`
      const description = seo.description || SITE_DESCRIPTION
      const path = seo.path || '/'
      const url = absoluteUrl(path)
      const image = seo.image || absoluteUrl('/og.png')
      const robots = seo.noindex ? 'noindex, nofollow' : 'index, follow'
      const jsonLd = seo.jsonLd
        ? Array.isArray(seo.jsonLd)
          ? seo.jsonLd
          : [seo.jsonLd]
        : []

      return {
        title,
        htmlAttrs: { lang: 'fr' },
        meta: [
          { name: 'description', content: description },
          { name: 'robots', content: robots },
          { name: 'author', content: 'Mickael Rébeau' },
          { name: 'theme-color', content: '#F1EEE7' },
          { property: 'og:type', content: seo.type || 'website' },
          { property: 'og:site_name', content: SITE_NAME },
          { property: 'og:locale', content: 'fr_FR' },
          { property: 'og:title', content: title },
          { property: 'og:description', content: description },
          { property: 'og:url', content: url },
          { property: 'og:image', content: image },
          { name: 'twitter:card', content: 'summary_large_image' },
          { name: 'twitter:title', content: title },
          { name: 'twitter:description', content: description },
          { name: 'twitter:image', content: image },
        ],
        link: [
          { rel: 'canonical', href: url },
          { rel: 'alternate', hreflang: 'fr', href: url },
        ],
        script: jsonLd.map((schema) => ({
          type: 'application/ld+json',
          children: JSON.stringify(schema),
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

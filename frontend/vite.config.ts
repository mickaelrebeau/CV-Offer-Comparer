import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { copyFileSync, writeFileSync } from 'fs'
import { resolve } from 'path'
import { prerenderRoutes } from './prerender-routes'

const SITE_URL = 'https://cv-compare.up.railway.app'
// changefreq / priorité par page (chemin sans préfixe de langue)
const SITEMAP_META: Record<string, [string, string]> = {
  '/': ['weekly', '1.0'],
  '/free-trial': ['monthly', '0.8'],
  '/register': ['yearly', '0.5'],
  '/login': ['yearly', '0.4'],
  '/confidentialite': ['yearly', '0.4'],
  '/mentions-legales': ['yearly', '0.3'],
  '/cgv': ['yearly', '0.3'],
}

/** Sitemap des pages prégénérées, avec alternates hreflang quand les deux langues existent. */
function buildSitemap(paths: string[]): string {
  const url = (path: string) => `${SITE_URL}${path === '/' ? '' : path}`
  const frenchOf = (path: string) => (path === '/en' ? '/' : path.replace(/^\/en(?=\/)/, ''))
  const englishOf = (path: string) => (path === '/' ? '/en' : `/en${path}`)
  const entries = paths.map((path) => {
    const french = frenchOf(path)
    const [changefreq, priority] = SITEMAP_META[french] ?? ['monthly', '0.5']
    const bilingual = paths.includes(french) && paths.includes(englishOf(french))
    const alternates = bilingual
      ? [
          `    <xhtml:link rel="alternate" hreflang="fr" href="${url(french)}"/>`,
          `    <xhtml:link rel="alternate" hreflang="en" href="${url(englishOf(french))}"/>`,
          `    <xhtml:link rel="alternate" hreflang="x-default" href="${url(french)}"/>`,
        ]
      : []
    return [
      '  <url>',
      `    <loc>${url(path)}</loc>`,
      ...alternates,
      `    <changefreq>${changefreq}</changefreq>`,
      `    <priority>${priority}</priority>`,
      '  </url>',
    ].join('\n')
  })
  return [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ...entries,
    '</urlset>',
    '',
  ].join('\n')
}

const dist = (file: string) => resolve(__dirname, 'dist', file)

// Routes du routeur non prégénérées (espace connecté, liens e-mail…) : servies par un shell SPA
// vierge, pour ne pas hériter du head de l'accueil (canonical, JSON-LD…)
const SPA_SHELL = '_spa.html'
let spaRoutes: string[] = []

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  ssgOptions: {
    script: 'async',
    formatting: 'minify',
    // Fichiers plats (login.html) : `serve` les associe à /login via cleanUrls
    dirStyle: 'flat',
    beastiesOptions: false,
    includedRoutes(paths) {
      spaRoutes = paths.filter((path) => !prerenderRoutes.includes(path) && !path.includes(':'))
      // Appelé avant le rendu : dist/index.html est encore le template client non rendu
      copyFileSync(dist('index.html'), dist(SPA_SHELL))
      return prerenderRoutes
    },
    // `serve -s` réécrivait toutes les URL vers index.html (page d'accueil), même quand
    // une page prégénérée existait : seules les routes SPA sont réécrites désormais
    onFinished() {
      const config = {
        cleanUrls: true,
        rewrites: spaRoutes.map((source) => ({ source, destination: `/${SPA_SHELL}` })),
      }
      writeFileSync(dist('serve.json'), JSON.stringify(config, null, 2))
      writeFileSync(dist('sitemap.xml'), buildSitemap(prerenderRoutes))
    },
  },
})

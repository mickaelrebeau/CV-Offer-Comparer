import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { createHash } from 'crypto'
import { copyFileSync, readFileSync, readdirSync, statSync, writeFileSync } from 'fs'
import { join, relative, resolve } from 'path'
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

/** Fichiers du build à précacher par le service worker (URL propres pour les pages HTML). */
function precacheEntries(): { url: string; file: string }[] {
  const root = resolve(__dirname, 'dist')
  const entries: { url: string; file: string }[] = []
  const walk = (dir: string) => {
    for (const name of readdirSync(dir)) {
      const file = join(dir, name)
      if (statSync(file).isDirectory()) {
        walk(file)
        continue
      }
      const path = `/${relative(root, file).split('\\').join('/')}`
      if (path.endsWith('.html')) {
        // /index.html → /, /login.html → /login, /en.html → /en, /_spa.html → /_spa
        entries.push({ url: path === '/index.html' ? '/' : path.replace(/\.html$/, ''), file })
      } else if (
        path.startsWith('/assets/') ||
        path.startsWith('/icons/') ||
        path === '/manifest.webmanifest' ||
        path === '/logo.png'
      ) {
        entries.push({ url: path, file })
      }
    }
  }
  walk(root)
  return entries.sort((a, b) => a.url.localeCompare(b.url))
}

/** dist/sw.js : modèle pwa/sw.template.js + liste de précache + version (empreinte du contenu). */
function buildServiceWorker(): string {
  const entries = precacheEntries()
  const hash = createHash('sha256')
  for (const { url, file } of entries) hash.update(url).update(readFileSync(file))
  const template = readFileSync(resolve(__dirname, 'pwa/sw.template.js'), 'utf-8')
  return template
    .replace('__VERSION__', hash.digest('hex').slice(0, 12))
    .replace('__PRECACHE_URLS__', JSON.stringify(entries.map((entry) => entry.url)))
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
      // En dernier : le précache doit inclure toutes les pages rendues
      writeFileSync(dist('sw.js'), buildServiceWorker())
    },
  },
})

/* Service worker Talento — généré au build (vite.config.ts → onFinished), ne pas éditer dist/sw.js.
 *
 * - Pages : réseau d'abord ; hors ligne, page en cache puis shell SPA (/_spa)
 * - Assets versionnés (/assets/*), icônes, manifeste : cache d'abord (précache)
 * - Google Fonts : stale-while-revalidate
 * - Jamais mis en cache : API, vidéos, documents utilisateur, requêtes non GET
 */
const VERSION = '__VERSION__'
const PRECACHE = `talento-precache-${VERSION}`
const FONTS_CACHE = 'talento-fonts-v1'
const PRECACHE_URLS = __PRECACHE_URLS__
const SPA_SHELL = '/_spa'
const FONT_ORIGINS = ['https://fonts.googleapis.com', 'https://fonts.gstatic.com']

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches
      .open(PRECACHE)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting()),
  )
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys
            .filter((key) => key.startsWith('talento-precache-') && key !== PRECACHE)
            .map((key) => caches.delete(key)),
        ),
      )
      .then(() => self.clients.claim()),
  )
})

self.addEventListener('fetch', (event) => {
  const request = event.request
  if (request.method !== 'GET') return
  const url = new URL(request.url)

  if (FONT_ORIGINS.includes(url.origin)) {
    event.respondWith(staleWhileRevalidate(request, FONTS_CACHE))
    return
  }
  // Autres origines (API backend, analytics…) : jamais interceptées
  if (url.origin !== self.location.origin) return
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/videos/')) return

  if (request.mode === 'navigate') {
    event.respondWith(networkFirstPage(request, url))
    return
  }
  if (url.pathname.startsWith('/assets/') || PRECACHE_URLS.includes(url.pathname)) {
    event.respondWith(cacheFirst(request))
  }
})

async function networkFirstPage(request, url) {
  try {
    return await fetch(request)
  } catch (error) {
    const cache = await caches.open(PRECACHE)
    const path = url.pathname.length > 1 ? url.pathname.replace(/\/$/, '') : '/'
    // Page prégénérée si disponible, sinon shell SPA (deep links : /compare?history=…)
    return (await cache.match(path)) || (await cache.match(SPA_SHELL)) || Response.error()
  }
}

async function cacheFirst(request) {
  const cached = await caches.match(request)
  if (cached) return cached
  const response = await fetch(request)
  if (response.ok) {
    const cache = await caches.open(PRECACHE)
    cache.put(request, response.clone())
  }
  return response
}

async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName)
  const cached = await cache.match(request)
  const network = fetch(request)
    .then((response) => {
      if (response.ok || response.type === 'opaque') cache.put(request, response.clone())
      return response
    })
    .catch(() => cached)
  return cached || network
}

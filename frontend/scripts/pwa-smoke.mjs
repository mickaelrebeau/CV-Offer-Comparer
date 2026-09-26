// Smoke test PWA sur le build servi comme en production (`serve dist`) :
// manifeste installable, service worker actif, navigation hors ligne, pas d'API en cache.
import { chromium } from 'playwright'

const BASE_URL = process.env.PWA_BASE_URL || 'http://127.0.0.1:4173'
const errors = []
const check = (label, condition, detail = '') => {
  console.log(`${condition ? '✓' : '✗'} ${label}${detail ? ` — ${detail}` : ''}`)
  if (!condition) errors.push(label)
}

// Manifeste et icônes
const manifestResponse = await fetch(`${BASE_URL}/manifest.webmanifest`)
const manifest = await manifestResponse.json()
check('manifeste servi en JSON', manifestResponse.ok && /json/.test(manifestResponse.headers.get('content-type') || ''))
check(
  'manifeste installable',
  manifest.name && manifest.short_name && manifest.start_url && ['standalone', 'minimal-ui'].includes(manifest.display),
)
const iconKeys = manifest.icons.map((icon) => `${icon.sizes}/${icon.purpose}`)
check(
  'icônes 192/512 (any + maskable)',
  ['192x192/any', '512x512/any', '192x192/maskable', '512x512/maskable'].every((key) => iconKeys.includes(key)),
)
for (const icon of manifest.icons) {
  check(`icône ${icon.src}`, (await fetch(`${BASE_URL}${icon.src}`)).ok)
}

// Service worker et hors ligne
const browser = await chromium.launch()
const context = await browser.newContext({ locale: 'fr-FR' })
let offline = false
// API simulée (et coupée hors ligne comme un vrai réseau)
await context.route('**/api/**', (route) =>
  offline ? route.abort('internetdisconnected') : route.fulfill({ status: 401, body: '{}' }),
)
const page = await context.newPage()
await page.goto(BASE_URL, { waitUntil: 'networkidle' })
await page.evaluate(() => navigator.serviceWorker.ready)
await page.reload({ waitUntil: 'networkidle' })
check('service worker contrôlant la page', await page.evaluate(() => Boolean(navigator.serviceWorker.controller)))

const cachedPaths = await page.evaluate(async () => {
  const paths = []
  for (const key of await caches.keys()) {
    for (const request of await (await caches.open(key)).keys()) paths.push(new URL(request.url).pathname)
  }
  return paths
})
check('pages et shell SPA précachés', ['/', '/login', '/en', '/_spa'].every((path) => cachedPaths.includes(path)))
check('aucune réponse API ni vidéo en cache', !cachedPaths.some((path) => /^\/(api|videos)\//.test(path)))

offline = true
await context.setOffline(true)
for (const path of ['/', '/en/login', '/dashboard']) {
  const response = await page.goto(`${BASE_URL}${path}`, { waitUntil: 'domcontentloaded' }).catch(() => null)
  check(`hors ligne : ${path}`, Boolean(response) && (await page.locator('#app').innerHTML()).length > 0)
}
await browser.close()

if (errors.length) {
  console.error(`\n${errors.length} vérification(s) PWA en échec`)
  process.exit(1)
}

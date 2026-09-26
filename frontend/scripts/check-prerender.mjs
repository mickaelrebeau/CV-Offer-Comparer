// Vérifie le head des pages prégénérées (dist/) et la config `serve` : garde-fou contre #33.
import { existsSync, readFileSync, readdirSync, statSync } from 'fs'
import { join, relative, resolve } from 'path'

const DIST = resolve(import.meta.dirname, '../dist')
const SITE_URL = 'https://cv-compare.up.railway.app'
const errors = []
const check = (ok, message) => ok || errors.push(message)
const read = (file) => readFileSync(resolve(DIST, file), 'utf-8')
const matchAll = (html, regex) => [...html.matchAll(regex)].map((m) => m[1])

function* htmlFiles(dir) {
  for (const entry of readdirSync(dir)) {
    const path = join(dir, entry)
    if (statSync(path).isDirectory()) yield* htmlFiles(path)
    else if (entry.endsWith('.html') && !entry.startsWith('_')) yield relative(DIST, path)
  }
}

const pages = [...htmlFiles(DIST)]
const titles = new Map()
const toPath = (file) => (file === 'index.html' ? '' : `/${file.replace(/\.html$/, '')}`)
const fileOf = (path) => (path === '' ? 'index.html' : `${path.slice(1)}.html`)

for (const file of pages) {
  const html = read(file)
  const path = toPath(file)
  const locale = path === '/en' || path.startsWith('/en/') ? 'en' : 'fr'
  const canonical = matchAll(html, /<link[^>]*rel="canonical"[^>]*href="([^"]*)"/g)
  const title = matchAll(html, /<title>([^<]*)<\/title>/g)

  check(new RegExp(`<html[^>]*lang="${locale}"`).test(html), `${file} : <html lang="${locale}"> manquant`)

  // hreflang croisés quand les deux versions sont prégénérées
  const frPath = locale === 'en' ? path.replace(/^\/en/, '') : path
  const enPath = frPath === '' ? '/en' : `/en${frPath}`
  if (pages.includes(fileOf(frPath)) && pages.includes(fileOf(enPath))) {
    const alternates = Object.fromEntries(
      [...html.matchAll(/<link[^>]*hreflang="([^"]*)"[^>]*href="([^"]*)"/g)].map((m) => [m[1], m[2]]),
    )
    check(alternates.fr === `${SITE_URL}${frPath}`, `${file} : hreflang fr ${alternates.fr}`)
    check(alternates.en === `${SITE_URL}${enPath}`, `${file} : hreflang en ${alternates.en}`)
    check(alternates['x-default'] === `${SITE_URL}${frPath}`, `${file} : hreflang x-default ${alternates['x-default']}`)
  }
  check(canonical.length === 1 && canonical[0] === `${SITE_URL}${path}`, `${file} : canonical ${JSON.stringify(canonical)} ≠ ${SITE_URL}${path}`)
  check(title.length === 1, `${file} : ${title.length} <title>`)
  check(matchAll(html, /<meta[^>]*name="description"/g).length === 1, `${file} : meta description absente ou dupliquée`)
  for (const json of matchAll(html, /<script type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/g)) {
    try { JSON.parse(json) } catch { errors.push(`${file} : JSON-LD invalide`) }
  }
  if (titles.has(title[0])) errors.push(`${file} : même <title> que ${titles.get(title[0])}`)
  titles.set(title[0], file)
}

check(existsSync(resolve(DIST, '_spa.html')), '_spa.html manquant')
check(!/rel="canonical"/.test(read('_spa.html')), '_spa.html ne doit pas porter de canonical')
const serve = JSON.parse(read('serve.json'))
for (const { source, destination } of serve.rewrites) {
  check(destination === '/_spa.html', `serve.json : ${source} → ${destination}`)
  check(!pages.includes(fileOf(source)), `serve.json : ${source} est prégénérée mais réécrite`)
}

console.log(`${pages.length} pages prégénérées, ${serve.rewrites.length} routes SPA`)
if (errors.length) {
  console.error(errors.map((e) => `✗ ${e}`).join('\n'))
  process.exit(1)
}
console.log('✓ head et config serve OK')

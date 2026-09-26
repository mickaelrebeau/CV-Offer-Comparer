// Vérifie le head des pages prégénérées (dist/) et la config `serve` : garde-fou contre #33.
import { existsSync, readFileSync, readdirSync } from 'fs'
import { resolve } from 'path'

const DIST = resolve(import.meta.dirname, '../dist')
const SITE_URL = 'https://cv-compare.up.railway.app'
const errors = []
const check = (ok, message) => ok || errors.push(message)
const read = (file) => readFileSync(resolve(DIST, file), 'utf-8')
const matchAll = (html, regex) => [...html.matchAll(regex)].map((m) => m[1])

const pages = readdirSync(DIST).filter((f) => f.endsWith('.html') && !f.startsWith('_'))
const titles = new Map()

for (const file of pages) {
  const html = read(file)
  const path = file === 'index.html' ? '' : `/${file.replace(/\.html$/, '')}`
  const canonical = matchAll(html, /<link[^>]*rel="canonical"[^>]*href="([^"]*)"/g)
  const title = matchAll(html, /<title>([^<]*)<\/title>/g)

  check(/<html[^>]*lang="fr"/.test(html), `${file} : <html lang="fr"> manquant`)
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
  check(!pages.includes(`${source.slice(1)}.html`), `serve.json : ${source} est prégénérée mais réécrite`)
}

console.log(`${pages.length} pages prégénérées, ${serve.rewrites.length} routes SPA`)
if (errors.length) {
  console.error(errors.map((e) => `✗ ${e}`).join('\n'))
  process.exit(1)
}
console.log('✓ head et config serve OK')

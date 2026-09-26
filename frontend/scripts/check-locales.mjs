// Cohérence des catalogues i18n : mêmes clés, mêmes paramètres, syntaxe vue-i18n sûre,
// et toutes les clés statiques utilisées dans le code existent.
import { readFileSync, readdirSync, statSync } from 'fs'
import { join, resolve } from 'path'

const ROOT = resolve(import.meta.dirname, '..')
const LOCALES = ['fr', 'en']
const catalogs = Object.fromEntries(
  LOCALES.map((locale) => [locale, JSON.parse(readFileSync(join(ROOT, 'src/locales', `${locale}.json`), 'utf-8'))]),
)
const errors = []

function flatten(node, prefix = '', out = new Map()) {
  if (Array.isArray(node)) node.forEach((value, i) => flatten(value, `${prefix}.${i}`, out))
  else if (node && typeof node === 'object') {
    for (const [key, value] of Object.entries(node)) flatten(value, prefix ? `${prefix}.${key}` : key, out)
  } else out.set(prefix, String(node))
  return out
}

const flat = Object.fromEntries(LOCALES.map((locale) => [locale, flatten(catalogs[locale])]))
const params = (message) => [...message.matchAll(/\{(\w+)\}/g)].map((m) => m[1]).sort().join(',')
// Hors littéraux {'…'}, « @ » (message lié) et « | » (pluriel) sont interprétés par vue-i18n
const unsafe = (message) => /[@|]/.test(message.replace(/\{'[^']*'\}/g, ''))

for (const [key, fr] of flat.fr) {
  const en = flat.en.get(key)
  if (en === undefined) errors.push(`en : clé manquante « ${key} »`)
  else if (params(fr) !== params(en)) errors.push(`« ${key} » : paramètres fr {${params(fr)}} ≠ en {${params(en)}}`)
}
for (const key of flat.en.keys()) if (!flat.fr.has(key)) errors.push(`fr : clé manquante « ${key} »`)
for (const locale of LOCALES) {
  for (const [key, message] of flat[locale]) if (unsafe(message)) errors.push(`${locale} « ${key} » : @ ou | à échapper ({'@'})`)
}

// Clés utilisées dans le code : t('a.b'), tm('a.b'), keypath="a.b"
const exists = (key) => [...flat.fr.keys()].some((k) => k === key || k.startsWith(`${key}.`))
function* sources(dir) {
  for (const entry of readdirSync(dir)) {
    const path = join(dir, entry)
    if (statSync(path).isDirectory()) yield* sources(path)
    else if (/\.(vue|ts)$/.test(entry)) yield path
  }
}
let used = 0
for (const file of sources(join(ROOT, 'src'))) {
  const code = readFileSync(file, 'utf-8')
  for (const [, key] of code.matchAll(/\b(?:t|tm|te)\(\s*['"]([\w.-]+)['"]/g)) {
    used++
    if (!exists(key)) errors.push(`${file.slice(ROOT.length + 1)} : clé inconnue « ${key} »`)
  }
  for (const [, key] of code.matchAll(/keypath="([\w.-]+)"/g)) {
    used++
    if (!exists(key)) errors.push(`${file.slice(ROOT.length + 1)} : clé inconnue « ${key} »`)
  }
}

console.log(`${flat.fr.size} messages par langue, ${used} usages statiques vérifiés`)
if (errors.length) {
  console.error(errors.map((e) => `✗ ${e}`).join('\n'))
  process.exit(1)
}
console.log('✓ catalogues fr/en cohérents')

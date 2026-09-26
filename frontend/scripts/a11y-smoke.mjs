// Audit axe-core (WCAG 2.1 A/AA) des pages publiques servies par `vite preview`.
// Échoue sur toute violation « serious » ou « critical ».
import AxeBuilder from '@axe-core/playwright'
import { chromium } from 'playwright'

const BASE_URL = process.env.A11Y_BASE_URL || 'http://localhost:4173'
const ROUTES = [
  '/',
  '/free-trial',
  '/login',
  '/register',
  '/forgot-password',
  '/reset-password',
  '/mentions-legales',
  '/cgv',
  '/confidentialite',
]
const BLOCKING = new Set(['serious', 'critical'])

const browser = await chromium.launch()
// Animations d'apparition coupées : axe mesure le contraste de l'état final
const context = await browser.newContext({ reducedMotion: 'reduce' })
let failures = 0

for (const route of ROUTES) {
  const page = await context.newPage()
  await page.goto(`${BASE_URL}${route}`, { waitUntil: 'networkidle' })
  const { violations } = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze()
  const blocking = violations.filter((v) => BLOCKING.has(v.impact))

  console.log(`${blocking.length ? '✗' : '✓'} ${route} (${violations.length} violation(s), ${blocking.length} bloquante(s))`)
  for (const v of violations) {
    console.log(`   [${v.impact}] ${v.id} — ${v.help} (${v.nodes.length} élément(s))`)
    for (const node of v.nodes.slice(0, 3)) console.log(`      ${node.target.join(' ')}`)
  }
  failures += blocking.length
  await page.close()
}

await browser.close()
if (failures) {
  console.error(`\n${failures} violation(s) bloquante(s)`)
  process.exit(1)
}

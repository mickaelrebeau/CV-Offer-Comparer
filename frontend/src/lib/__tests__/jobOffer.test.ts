import { describe, expect, it } from 'vitest'
import { composeOfferText, offerDomain, safeHttpUrl } from '@/lib/jobOffer'

describe('composeOfferText', () => {
  it('place poste, entreprise et lieu en tête de la description', () => {
    expect(
      composeOfferText({ title: 'Data Analyst', company: 'ACME', location: 'Lyon', text: 'Missions…' }),
    ).toBe('Data Analyst\nACME · Lyon\n\nMissions…')
  })

  it('ignore les champs vides', () => {
    expect(composeOfferText({ title: '', company: 'ACME', location: ' ', text: ' Missions ' })).toBe('ACME\n\nMissions')
    expect(composeOfferText({ title: '', company: '', location: '', text: 'Missions' })).toBe('Missions')
  })
})

describe('offerDomain', () => {
  it('renvoie le domaine sans www (seule donnée envoyée à PostHog)', () => {
    expect(offerDomain('https://www.welcometothejungle.com/fr/companies/x/jobs/y?ref=1')).toBe('welcometothejungle.com')
    expect(offerDomain('https://jobs.lever.co/acme/123')).toBe('jobs.lever.co')
  })

  it('tolère une valeur invalide', () => {
    expect(offerDomain('pas une url')).toBe('')
    expect(offerDomain(null)).toBe('')
  })
})

describe('safeHttpUrl', () => {
  it('accepte uniquement http(s)', () => {
    expect(safeHttpUrl('https://jobs.example.com/a')).toBe('https://jobs.example.com/a')
    expect(safeHttpUrl('javascript:alert(1)')).toBeNull()
    expect(safeHttpUrl('data:text/html,x')).toBeNull()
    expect(safeHttpUrl('')).toBeNull()
  })
})

import { afterEach, vi } from 'vitest'
import {
  BOOKMARKLET_HASH_KEY,
  bookmarkletSource,
  browserAssistedSite,
  decodeOfferPayload,
  encodeOfferPayload,
} from '@/lib/jobOffer'

describe('browserAssistedSite', () => {
  it('reconnaît les sites qui bloquent l’import serveur', () => {
    expect(browserAssistedSite('https://fr.indeed.com/viewjob?jk=abc')).toBe('Indeed')
    expect(browserAssistedSite('www.linkedin.com/jobs/view/1')).toBe('LinkedIn')
    expect(browserAssistedSite('https://www.welcometothejungle.com/fr/companies/x/jobs/y')).toBe('Welcome to the Jungle')
  })

  it('laisse passer les sites importables côté serveur', () => {
    expect(browserAssistedSite('https://www.hellowork.com/fr-fr/emplois/1.html')).toBeNull()
    expect(browserAssistedSite('https://welovedevs.com/app/fr/job/dev-qonto')).toBeNull()
    expect(browserAssistedSite('https://notindeed.example.com/')).toBeNull()
    expect(browserAssistedSite('')).toBeNull()
  })
})

describe('payload du bookmarklet', () => {
  it('fait l’aller-retour en UTF-8', () => {
    const payload = { u: 'https://fr.indeed.com/viewjob?jk=1', t: 'Développeur·se — Île-de-France', j: ['{"a":"é"}'], x: '✓' }
    const encoded = encodeOfferPayload(payload)
    expect(encoded).not.toMatch(/[+/=]/)
    expect(decodeOfferPayload(encoded)).toEqual(payload)
  })

  it('rejette un contenu illisible et filtre les types', () => {
    expect(decodeOfferPayload('%%%')).toBeNull()
    expect(decodeOfferPayload(encodeOfferPayload({ u: 1, t: null, j: ['ok', 2], x: {} } as any))).toEqual({
      u: '',
      t: '',
      j: ['ok'],
      x: '',
    })
  })
})

describe('bookmarklet', () => {
  const IMPORT_URL = 'https://talento.example/import'

  /** Exécute le favori sur la page courante (jsdom) et renvoie l'offre envoyée à Talento. */
  function runBookmarklet() {
    const open = vi.spyOn(window, 'open').mockImplementation(() => null)
    const source = bookmarkletSource(IMPORT_URL)
    expect(source.startsWith('javascript:')).toBe(true)
    new Function(decodeURIComponent(source.slice('javascript:'.length)))()
    const target = String(open.mock.calls[0][0])
    expect(target.startsWith(`${IMPORT_URL}#${BOOKMARKLET_HASH_KEY}=`)).toBe(true)
    return decodeOfferPayload(target.split(`#${BOOKMARKLET_HASH_KEY}=`)[1])
  }

  afterEach(() => {
    vi.restoreAllMocks()
    document.head.innerHTML = ''
    document.body.innerHTML = ''
  })

  it('envoie le JSON-LD JobPosting de la page', () => {
    document.head.innerHTML = `
      <script type="application/ld+json">{"@type":"BreadcrumbList"}</script>
      <script type="application/ld+json">{"@type":"JobPosting","title":"Développeur H/F"}</script>`
    document.title = 'Développeur H/F - Paris - Indeed.com'
    const payload = runBookmarklet()
    expect(payload?.j).toEqual(['{"@type":"JobPosting","title":"Développeur H/F"}'])
    expect(payload?.x).toBe('')
    expect(payload?.t).toBe('Développeur H/F - Paris - Indeed.com')
  })

  it('sans JSON-LD : titre et zone de description connue (Indeed)', () => {
    document.body.innerHTML = `
      <nav>Accueil Avis sur les entreprises</nav>
      <h1>Développeur Full Stack H/F</h1>
      <div id="jobDescriptionText">Rejoignez l’équipe produit.</div>
      <footer>Signaler l’offre</footer>`
    const payload = runBookmarklet()
    expect(payload?.j).toEqual([])
    expect(payload?.x).toContain('Développeur Full Stack H/F')
    expect(payload?.x).toContain('Rejoignez l’équipe produit.')
    expect(payload?.x).not.toContain('Signaler')
  })
})

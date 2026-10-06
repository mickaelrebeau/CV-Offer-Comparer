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
    const payload = {
      u: 'https://fr.indeed.com/viewjob?jk=1',
      t: 'Développeur·se — Île-de-France',
      j: ['{"a":"é"}'],
      x: '✓',
      f: { ti: 'Développeur·se', co: 'Café & Co', lo: 'Île-de-France', de: '✓' },
    }
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
      f: null,
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

  const originalLocation = window.location

  afterEach(() => {
    // Certains tests simulent une page Indeed / LinkedIn
    Object.defineProperty(window, 'location', { value: originalLocation, configurable: true })
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

  it('Indeed, page de recherche : offre du panneau affiché, pas le JSON-LD de la liste', () => {
    Object.defineProperty(window, 'location', { value: new URL('https://fr.indeed.com/emplois?q=developpeur&l=Paris&vjk=1a2b3c4d5e6f7a8b'), configurable: true })
    document.head.innerHTML = `<script type="application/ld+json">{"@type":"ItemList","itemListElement":[{"@type":"JobPosting","title":"Autre offre"}]}</script>`
    document.body.innerHTML = `
      <h1>Emplois : developpeur - Paris</h1>
      <ul><li><h2 class="jobTitle">Autre offre</h2></li></ul>
      <div id="jobsearch-ViewjobPaneWrapper">
        <h2 data-testid="jobsearch-JobInfoHeader-title"><span>Développeur Full Stack H/F</span><span> - job post</span></h2>
        <div data-testid="inlineHeader-companyName"><a>Doctolib</a></div>
        <div data-testid="inlineHeader-companyLocation">Paris (75)</div>
        <div id="jobDescriptionText">Rejoignez l’équipe produit.</div>
      </div>`
    const payload = runBookmarklet()
    expect(payload?.u).toBe('https://fr.indeed.com/viewjob?jk=1a2b3c4d5e6f7a8b')
    expect(payload?.f).toEqual({ ti: 'Développeur Full Stack H/F', co: 'Doctolib', lo: 'Paris (75)', de: 'Rejoignez l’équipe produit.' })
    expect(payload?.x).toBe('')
  })

  it('LinkedIn, liste de recherche : offre affichée et URL /jobs/view/<id>/', () => {
    Object.defineProperty(window, 'location', { value: new URL('https://www.linkedin.com/jobs/search/?currentJobId=4012345678&keywords=dev'), configurable: true })
    document.body.innerHTML = `
      <h1>Développeur – 2 000 résultats</h1>
      <div class="job-details-jobs-unified-top-card__job-title"><h1>Data Engineer</h1></div>
      <div class="job-details-jobs-unified-top-card__company-name"><a>Qonto</a></div>
      <div class="job-details-jobs-unified-top-card__primary-description-container">Paris, Île-de-France, France · il y a 2 jours · 87 candidats</div>
      <div class="jobs-description__content">Vous construirez nos pipelines de données.</div>`
    const payload = runBookmarklet()
    expect(payload?.u).toBe('https://www.linkedin.com/jobs/view/4012345678/')
    expect(payload?.f).toEqual({ ti: 'Data Engineer', co: 'Qonto', lo: 'Paris, Île-de-France, France', de: 'Vous construirez nos pipelines de données.' })
  })

  it('Indeed sans sélecteur reconnu : texte de la page, sans champs partiels', () => {
    Object.defineProperty(window, 'location', { value: new URL('https://fr.indeed.com/?vjk=0011aabbccddeeff'), configurable: true })
    document.body.innerHTML = `
      <h1>Emplois</h1>
      <div class="css-x1"><h2 class="css-y2">Alternance Développeur (F/H)</h2><div>ISCOD</div></div>
      <div class="css-z3"><h2>Description du poste</h2><div>Missions : développer en Angular.</div></div>`
    const payload = runBookmarklet()
    expect(payload?.u).toBe('https://fr.indeed.com/viewjob?jk=0011aabbccddeeff')
    expect(payload?.f).toBeNull()
    expect(payload?.x).toContain('Description du poste')
    expect(payload?.x).toContain('Missions : développer en Angular.')
  })

  it('Indeed : offre affichée dans une iframe du même site', () => {
    Object.defineProperty(window, 'location', { value: new URL('https://fr.indeed.com/emplois?q=dev&vjk=99'), configurable: true })
    document.body.innerHTML = '<iframe id="vjs-container-iframe"></iframe>'
    const frame = (document.getElementById('vjs-container-iframe') as HTMLIFrameElement).contentDocument!
    frame.body.innerHTML = `
      <h1 class="jobsearch-JobInfoHeader-title">Data Analyst</h1>
      <div data-testid="inlineHeader-companyName">ACME</div>
      <div data-testid="inlineHeader-companyLocation">Lyon (69)</div>
      <div id="jobDescriptionText">Tableaux de bord et SQL.</div>`
    const payload = runBookmarklet()
    expect(payload?.f).toEqual({ ti: 'Data Analyst', co: 'ACME', lo: 'Lyon (69)', de: 'Tableaux de bord et SQL.' })
  })

  it('une sélection de l’utilisateur prime sur la lecture automatique', () => {
    Object.defineProperty(window, 'location', { value: new URL('https://fr.indeed.com/viewjob?jk=abc'), configurable: true })
    document.body.innerHTML = `<div id="jobDescriptionText">Description complète</div><p id="sel">Texte choisi</p>`
    const range = document.createRange()
    range.selectNodeContents(document.getElementById('sel')!)
    window.getSelection()!.addRange(range)
    const payload = runBookmarklet()
    window.getSelection()!.removeAllRanges()
    expect(payload?.f).toBeNull()
    expect(payload?.x).toBe('Texte choisi')
  })

  it('autre site sans JSON-LD : titre et zone de description connue', () => {
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

/** Offre importée depuis une URL : champs éditables avant analyse. */
export interface OfferDraft {
  title: string
  company: string
  location: string
  text: string
}

/** Texte d'offre envoyé aux modules : en-tête (poste, entreprise, lieu) puis description. */
export function composeOfferText(draft: OfferDraft): string {
  const title = draft.title.trim()
  const meta = [draft.company.trim(), draft.location.trim()].filter(Boolean).join(' · ')
  const header = [title, meta].filter(Boolean).join('\n')
  const body = draft.text.trim()
  return [header, body].filter(Boolean).join('\n\n')
}

/** Domaine affiché (et seul envoyé à PostHog) : « jobs.lever.co », sans « www. ». */
export function offerDomain(url: string | null | undefined): string {
  if (!url) return ''
  try {
    return new URL(url).hostname.replace(/^www\./, '')
  } catch {
    return ''
  }
}

/** Lien affichable : http(s) uniquement (jamais javascript:…). */
export function safeHttpUrl(url: string | null | undefined): string | null {
  if (!url) return null
  try {
    const parsed = new URL(url)
    return parsed.protocol === 'http:' || parsed.protocol === 'https:' ? parsed.href : null
  } catch {
    return null
  }
}

// --- Sites qui bloquent l'import serveur : lecture dans le navigateur de l'utilisateur ---------

const BROWSER_ASSISTED_SITES: [RegExp, string][] = [
  [/(^|\.)indeed\.[a-z.]+$/, 'Indeed'],
  [/(^|\.)linkedin\.[a-z.]+$/, 'LinkedIn'],
  [/(^|\.)welcometothejungle\.[a-z.]+$/, 'Welcome to the Jungle'],
  [/(^|\.)glassdoor\.[a-z.]+$/, 'Glassdoor'],
  [/(^|\.)monster\.[a-z.]+$/, 'Monster'],
]

/** Nom du site si l'offre doit être lue depuis le navigateur (bookmarklet ou copier-coller), sinon null. */
export function browserAssistedSite(url: string | null | undefined): string | null {
  if (!url) return null
  let host = ''
  try {
    host = new URL(/^https?:\/\//i.test(url) ? url : `https://${url}`).hostname.toLowerCase()
  } catch {
    return null
  }
  return BROWSER_ASSISTED_SITES.find(([pattern]) => pattern.test(host))?.[1] ?? null
}

/** Offre envoyée par le bookmarklet (fragment d'URL, jamais transmis au serveur web). */
export interface BookmarkletPayload {
  /** URL de l'offre */
  u: string
  /** titre de l'onglet */
  t: string
  /** balises JSON-LD contenant un JobPosting */
  j: string[]
  /** texte de l'offre (zone de description connue, sélection ou page) quand il n'y a pas de JSON-LD */
  x: string
  /** champs lus dans le panneau de l'offre affichée (Indeed, LinkedIn) : poste, entreprise, lieu, description */
  f?: { ti: string; co: string; lo: string; de: string } | null
}

export const BOOKMARKLET_HASH_KEY = 'offer'

/** JSON → base64url (UTF-8), même encodage que le bookmarklet. */
export function encodeOfferPayload(payload: BookmarkletPayload): string {
  const bytes = new TextEncoder().encode(JSON.stringify(payload))
  let binary = ''
  bytes.forEach((byte) => (binary += String.fromCharCode(byte)))
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}

export function decodeOfferPayload(encoded: string): BookmarkletPayload | null {
  try {
    const base64 = encoded.replace(/-/g, '+').replace(/_/g, '/')
    const binary = atob(base64 + '='.repeat((4 - (base64.length % 4)) % 4))
    const data = JSON.parse(new TextDecoder().decode(Uint8Array.from(binary, (c) => c.charCodeAt(0))))
    if (!data || typeof data !== 'object') return null
    const text = (value: unknown) => (typeof value === 'string' ? value : '')
    const f = data.f && typeof data.f === 'object' ? data.f : null
    return {
      u: text(data.u),
      t: text(data.t),
      j: Array.isArray(data.j) ? data.j.filter((item: unknown) => typeof item === 'string').slice(0, 10) : [],
      x: text(data.x),
      f: f ? { ti: text(f.ti), co: text(f.co), lo: text(f.lo), de: text(f.de) } : null,
    }
  } catch {
    return null
  }
}

/**
 * Sélecteurs du panneau de l'offre affichée sur les sites qui bloquent les serveurs. Sur leurs pages
 * de recherche, le JSON-LD, le premier <h1> et l'URL décrivent la liste, pas l'offre ouverte.
 * Plusieurs sélecteurs par champ : leurs interfaces changent régulièrement.
 */
export const SITE_SELECTORS = {
  indeed: {
    title: ['[data-testid="jobsearch-JobInfoHeader-title"]', 'h1.jobsearch-JobInfoHeader-title', '.jobsearch-JobInfoHeader-title'],
    company: ['[data-testid="inlineHeader-companyName"]', '[data-company-name="true"]', '.jobsearch-CompanyInfoContainer a', '.jobsearch-InlineCompanyRating div'],
    location: ['[data-testid="inlineHeader-companyLocation"]', '[data-testid="job-location"]', '[data-testid="jobsearch-JobInfoHeader-companyLocation"]', '.jobsearch-JobInfoHeader-subtitle > div:last-child'],
    description: ['#jobDescriptionText', '.jobsearch-jobDescriptionText', '[data-testid="jobsearch-JobComponent-description"]'],
  },
  linkedin: {
    title: ['.job-details-jobs-unified-top-card__job-title', '.jobs-unified-top-card__job-title', '.top-card-layout__title', '.topcard__title'],
    company: ['.job-details-jobs-unified-top-card__company-name', '.jobs-unified-top-card__company-name', '.topcard__org-name-link', '.top-card-layout__second-subline a'],
    location: ['.job-details-jobs-unified-top-card__primary-description-container', '.job-details-jobs-unified-top-card__bullet', '.jobs-unified-top-card__bullet', '.topcard__flavor--bullet'],
    description: ['.jobs-description__content', '#job-details', '.jobs-box__html-content', '.show-more-less-html__markup', '.description__text'],
  },
} as const

/**
 * Code du favori « Envoyer vers Talento ». Exécuté sur la page de l'offre, dans le navigateur
 * de l'utilisateur, il ouvre `importUrl#offer=…` (aucune donnée envoyée ailleurs) avec :
 * - Indeed / LinkedIn : les champs du panneau de l'offre affichée et son URL propre
 *   (`viewjob?jk=…`, `/jobs/view/<id>/`), y compris depuis une page de recherche ;
 * - les balises JSON-LD JobPosting de la page ;
 * - un texte de secours : sélection de l'utilisateur, zone de description connue ou page.
 */
export function bookmarkletSource(importUrl: string): string {
  const code = `(()=>{
const S=${JSON.stringify(SITE_SELECTORS)};
const v=e=>e?(e.innerText||e.textContent||'').replace(/[ \\t]+/g,' ').trim():'';
const q=l=>{for(const k of l){const e=document.querySelector(k);if(v(e))return e}return null};
const H=location.hostname,P=new URLSearchParams(location.search);
let u=location.href,f=null,site=null;
if(/(^|\\.)indeed\\./.test(H)){site=S.indeed;const id=P.get('vjk')||P.get('jk');if(id)u=location.origin+'/viewjob?jk='+encodeURIComponent(id)}
else if(/(^|\\.)linkedin\\./.test(H)){site=S.linkedin;const id=P.get('currentJobId')||(location.pathname.match(/\\/jobs\\/view\\/(\\d+)/)||[])[1];if(id)u='https://www.linkedin.com/jobs/view/'+id+'/'}
if(site){f={ti:v(q(site.title)).replace(/\\s*[-–]\\s*(job post|offre d'emploi)\\s*$/i,''),co:v(q(site.company)),lo:v(q(site.location)).split(/\\s+·\\s+/)[0],de:v(q(site.description))}}
const s=String(getSelection()||'').trim();
if(s)f=null;
const j=s?[]:[...document.querySelectorAll('script[type="application/ld+json"]')].map(e=>e.textContent||'').filter(t=>/JobPosting/.test(t)).slice(0,5);
const z=q(['#jobDescriptionText','.jobs-description__content','.show-more-less-html__markup','[data-testid="job-section-description"]']);
const x=s||(j.length||(f&&f.de)?'':[v(document.querySelector('h1')),v(z||document.body)].join('\\n\\n')).slice(0,150000);
const b=new TextEncoder().encode(JSON.stringify({u:u,t:document.title,j:j,x:x,f:f}));
let r='';b.forEach(c=>r+=String.fromCharCode(c));
window.open(${JSON.stringify(importUrl)}+'#${BOOKMARKLET_HASH_KEY}='+btoa(r).replace(/\\+/g,'-').replace(/\\//g,'_').replace(/=+$/,''),'_blank');
})()`
  return `javascript:${encodeURIComponent(code.replace(/\n/g, ''))}`
}

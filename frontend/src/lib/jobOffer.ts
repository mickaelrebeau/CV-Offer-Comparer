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
    return {
      u: typeof data.u === 'string' ? data.u : '',
      t: typeof data.t === 'string' ? data.t : '',
      j: Array.isArray(data.j) ? data.j.filter((item: unknown) => typeof item === 'string').slice(0, 10) : [],
      x: typeof data.x === 'string' ? data.x : '',
    }
  } catch {
    return null
  }
}

/**
 * Code du favori « Envoyer vers Talento ». Exécuté sur la page de l'offre, dans le navigateur
 * de l'utilisateur : lit le JSON-LD JobPosting (sinon la description, la sélection ou la page)
 * et ouvre `importUrl#offer=…`. Aucune donnée n'est envoyée ailleurs.
 */
export function bookmarkletSource(importUrl: string): string {
  const code = `(()=>{
const j=[...document.querySelectorAll('script[type="application/ld+json"]')].map(e=>e.textContent||'').filter(t=>/JobPosting/.test(t)).slice(0,5);
const z=document.querySelector('#jobDescriptionText,.jobs-description__content,.show-more-less-html__markup,[data-testid="job-section-description"]');
const s=String(getSelection()||'').trim();
const h=document.querySelector('h1');
const v=e=>e?(e.innerText||e.textContent||''):'';
const x=j.length?'':[v(h),s||v(z||document.body)].join('\\n\\n').slice(0,150000);
const b=new TextEncoder().encode(JSON.stringify({u:location.href,t:document.title,j:j,x:x}));
let r='';b.forEach(c=>r+=String.fromCharCode(c));
window.open(${JSON.stringify(importUrl)}+'#${BOOKMARKLET_HASH_KEY}='+btoa(r).replace(/\\+/g,'-').replace(/\\//g,'_').replace(/=+$/,''),'_blank');
})()`
  return `javascript:${encodeURIComponent(code.replace(/\n/g, ''))}`
}

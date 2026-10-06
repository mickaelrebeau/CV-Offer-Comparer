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

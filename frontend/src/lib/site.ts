/** URL canonique de production (Railway). */
export const SITE_URL = 'https://cv-compare.up.railway.app'

export const SITE_NAME = 'Talento'

export const SITE_TAGLINE = 'Analyse ATS CV ↔ offre & préparation d’entretien'

export const SITE_DESCRIPTION =
  'Talento compare votre CV à une offre d’emploi avec Gemini : correspondances, lacunes, reformulations ATS et simulateur d’entretien. Open source, essai gratuit.'

export const CONTACT_EMAIL = 'rebeau.mickael@gmail.com'

export const GITHUB_URL = 'https://github.com/mickaelrebeau/CV-Offer-Comparer'

export const LEGAL_PUBLISHER = {
  name: 'Mickael Rébeau',
  email: CONTACT_EMAIL,
  github: 'https://github.com/mickaelrebeau',
}

export function absoluteUrl(path = '/') {
  const normalized = path.startsWith('/') ? path : `/${path}`
  return `${SITE_URL}${normalized === '/' ? '' : normalized}`
}

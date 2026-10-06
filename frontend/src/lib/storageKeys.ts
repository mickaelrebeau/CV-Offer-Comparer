/**
 * Clés localStorage Talento.
 * Les anciennes clés (nom « CV-Offer-Comparer ») sont migrées à la première lecture
 * pour ne pas déconnecter les utilisateurs ni réinitialiser l'essai gratuit.
 */
export const STORAGE_KEYS = {
  accessToken: 'talento_access_token',
  freeAnalysisUsed: 'talento_free_analysis_used',
  locale: 'talento_locale',
  // sessionStorage : CV + offre partagés entre les modules (jamais en localStorage, poste partagé possible)
  applicationContext: 'talento_application_context',
} as const

const LEGACY_KEYS: Record<string, string> = {
  [STORAGE_KEYS.accessToken]: 'cv_offer_access_token',
  [STORAGE_KEYS.freeAnalysisUsed]: 'cv-offer-compare-free-analysis-used',
}

export function readStorage(key: string): string | null {
  const value = localStorage.getItem(key)
  if (value !== null) return value

  const legacyKey = LEGACY_KEYS[key]
  const legacyValue = legacyKey ? localStorage.getItem(legacyKey) : null
  if (legacyValue !== null) {
    localStorage.setItem(key, legacyValue)
    localStorage.removeItem(legacyKey)
  }
  return legacyValue
}

export function removeStorage(key: string): void {
  localStorage.removeItem(key)
  const legacyKey = LEGACY_KEYS[key]
  if (legacyKey) localStorage.removeItem(legacyKey)
}

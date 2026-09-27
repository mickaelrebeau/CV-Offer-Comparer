/** Codes d'erreur IA renvoyés par l'API (voir backend `app/services/llm/errors.py`). */

/** Stack plateforme saturée ou indisponible : proposer une clé personnelle (BYOK). */
export const PLATFORM_LLM_ERRORS = new Set(['llm.platform_quota_exceeded', 'llm.platform_unavailable'])

/** Problème sur la clé personnelle active : proposer d'en activer une autre ou de revenir à Talento. */
export const USER_LLM_ERRORS = new Set([
  'llm.invalid_user_api_key',
  'llm.user_provider_quota_exceeded',
  'llm.provider_unavailable',
  'llm.provider_rejected',
  'llm.provider_refused',
  'llm.credential_unreadable',
])

/** Ancre de la section providers dans le profil. */
export const LLM_PROVIDERS_PATH = '/profile#llm-providers'

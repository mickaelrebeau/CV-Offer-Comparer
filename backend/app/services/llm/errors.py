"""Erreurs LLM normalisées, communes à tous les providers.

Chaque erreur porte un code stable (traduit par `app.i18n`) qui distingue la stack
plateforme (Gemini + GOOGLE_API_KEY) d'une clé personnelle (BYOK) : le client s'en
sert pour proposer d'ajouter une clé, d'en activer une autre ou de réessayer.
"""

from app.i18n import ApiError

PLATFORM = "platform"
USER = "user"

# code -> statut HTTP (jamais 401 : le front déconnecterait l'utilisateur)
STATUS = {
    "llm.platform_quota_exceeded": 503,
    "llm.platform_unavailable": 503,
    "llm.invalid_user_api_key": 400,
    "llm.user_provider_quota_exceeded": 429,
    "llm.provider_unavailable": 502,
    "llm.provider_rejected": 400,
    "llm.provider_refused": 422,
    "llm.credential_unreadable": 409,
}


class LLMError(ApiError):
    """Échec d'un appel LLM, déjà classé (quota, clé invalide, indisponibilité…)."""

    def __init__(self, code: str):
        super().__init__(STATUS[code], code)


def classify(status: int | None, owner: str, message: str = "") -> LLMError:
    """Traduit une réponse d'erreur provider en erreur normalisée.

    `status` None = timeout / erreur réseau. `message` sert uniquement à repérer les
    clés invalides ou crédits épuisés que certains providers signalent en 400.
    """
    text = (message or "").lower()
    user = owner == USER
    if status is None or status >= 500:
        return LLMError("llm.provider_unavailable" if user else "llm.platform_unavailable")
    if status in (401, 403) or (status == 400 and ("api key" in text or "api_key" in text)):
        return LLMError("llm.invalid_user_api_key" if user else "llm.platform_unavailable")
    # 402 : solde insuffisant (DeepSeek…) ; 400 « credit balance » : Anthropic
    if status in (402, 429) or "credit balance" in text or "insufficient" in text or "quota" in text:
        return LLMError("llm.user_provider_quota_exceeded" if user else "llm.platform_quota_exceeded")
    return LLMError("llm.provider_rejected" if user else "llm.platform_unavailable")

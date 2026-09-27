"""Chiffrement au repos des clés API utilisateur (Fernet : AES-128-CBC + HMAC-SHA256).

LLM_ENCRYPTION_KEYS contient une ou plusieurs clés Fernet séparées par des virgules :
la première chiffre, toutes déchiffrent. Rotation : ajouter la nouvelle clé en tête,
lancer `python -m app.scripts.rotate_llm_keys`, puis retirer l'ancienne.
"""

from cryptography.fernet import Fernet, InvalidToken, MultiFernet

from app.config import settings
from app.i18n import ApiError
from app.services.llm.errors import LLMError


def _keys() -> list[str]:
    return [key.strip() for key in settings.LLM_ENCRYPTION_KEYS.split(",") if key.strip()]


def byok_enabled() -> bool:
    return bool(_keys())


def _fernet() -> MultiFernet:
    keys = _keys()
    if not keys:
        raise ApiError(503, "llm.byok_disabled")
    return MultiFernet([Fernet(key.encode()) for key in keys])


def encrypt(secret: str) -> str:
    return _fernet().encrypt(secret.encode()).decode()


def decrypt(token: str) -> str:
    try:
        return _fernet().decrypt(token.encode()).decode()
    except InvalidToken as exc:
        # Clé de chiffrement retirée ou modifiée : l'utilisateur doit réenregistrer sa clé API
        raise LLMError("llm.credential_unreadable") from exc


def rotate(token: str) -> str:
    """Rechiffre avec la clé principale (première de la liste)."""
    return _fernet().rotate(token.encode()).decode()


def key_hint(api_key: str) -> str:
    """Indice affichable : préfixe court + 4 derniers caractères, jamais la clé."""
    if len(api_key) < 12:
        return f"••••{api_key[-2:]}"
    return f"{api_key[:3]}••••{api_key[-4:]}"

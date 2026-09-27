"""Validation des base_url saisies par les utilisateurs (anti-SSRF).

Le serveur appelle l'URL fournie : sans contrôle, un utilisateur pourrait viser le réseau
interne (métadonnées cloud, Redis, PostgreSQL…). Règles : HTTPS, pas d'identifiants dans
l'URL, et l'hôte doit résoudre uniquement vers des IP publiques. La vérification est refaite
avant chaque appel (DNS qui change entre l'enregistrement et l'usage).
"""

import ipaddress
import socket
from urllib.parse import urlsplit

from app.config import settings
from app.i18n import ApiError

MAX_URL_LENGTH = 300
BLOCKED_SUFFIXES = (".localhost", ".local", ".internal", ".lan", ".home.arpa")


def private_urls_allowed() -> bool:
    return settings.LLM_ALLOW_PRIVATE_BASE_URLS and settings.ENVIRONMENT.lower() != "production"


def _resolve(host: str) -> list[str]:
    return list({info[4][0] for info in socket.getaddrinfo(host, None)})


def _invalid() -> ApiError:
    return ApiError(400, "llm.invalid_base_url")


def validate_base_url(url: str) -> str:
    """Renvoie l'URL normalisée (sans / final) ou lève llm.invalid_base_url."""
    url = (url or "").strip()
    if not url or len(url) > MAX_URL_LENGTH:
        raise _invalid()
    try:
        parts = urlsplit(url)
        host = (parts.hostname or "").lower()
        parts.port  # noqa: B018 — lève ValueError si le port est invalide
    except ValueError as exc:
        raise _invalid() from exc

    allow_private = private_urls_allowed()
    allowed_schemes = ("https", "http") if allow_private else ("https",)
    if parts.scheme not in allowed_schemes or not host:
        raise _invalid()
    if parts.username or parts.password or parts.query or parts.fragment:
        raise _invalid()

    if not allow_private:
        if host == "localhost" or host.endswith(BLOCKED_SUFFIXES):
            raise _invalid()
        try:
            addresses = _resolve(host)
        except OSError as exc:
            raise _invalid() from exc
        for address in addresses:
            ip = ipaddress.ip_address(address.split("%")[0])
            if not ip.is_global or ip.is_multicast:
                raise _invalid()

    return url.rstrip("/")

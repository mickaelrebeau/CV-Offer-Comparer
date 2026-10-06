"""Import d'offre : sites bloquants, cache Redis par URL, récupération, extraction, nettoyage IA."""

from __future__ import annotations

import hashlib
import json
import re
import time
from typing import Any
from urllib.parse import urlsplit

from app.i18n import ApiError
from app.services.ai_service import AIService
from app.services.job_offers.extract import (
    MAX_TEXT_CHARS,
    MIN_TEXT_CHARS,
    ExtractedOffer,
    extract_offer,
    from_workable,
    workable_api_url,
)
from app.services.job_offers.fetch import fetch_html, fetch_json, validate_url
from app.services.redis_service import redis_service

CACHE_TTL_SECONDS = 15 * 60
CACHE_PREFIX = "job_offer:"
# Sites qui exigent une connexion ou bloquent les robots : inutile de les appeler
BLOCKED_SITES = re.compile(r"(^|\.)(linkedin|indeed|glassdoor|monster)\.[a-z.]+$")

_memory_cache: dict[str, tuple[float, dict[str, Any]]] = {}


def _cache_key(url: str) -> str:
    return CACHE_PREFIX + hashlib.sha256(url.encode()).hexdigest()


def _cache_get(key: str) -> dict[str, Any] | None:
    if redis_service.redis_available:
        try:
            raw = redis_service.redis_client.get(key)
            return json.loads(raw) if raw else None
        except Exception:
            return None
    expires, value = _memory_cache.get(key, (0.0, None))
    return value if expires > time.monotonic() else None


def _cache_set(key: str, value: dict[str, Any]) -> None:
    if redis_service.redis_available:
        try:
            redis_service.redis_client.setex(key, CACHE_TTL_SECONDS, json.dumps(value))
        except Exception:
            pass
        return
    now = time.monotonic()
    for stale in [k for k, (expires, _) in _memory_cache.items() if expires <= now]:
        del _memory_cache[stale]
    _memory_cache[key] = (now + CACHE_TTL_SECONDS, value)


def safe_offer_url(value: str | None) -> str | None:
    """URL source à conserver dans l'historique : http(s) uniquement (jamais javascript:…), sinon None."""
    value = (value or "").strip()
    if not value or len(value) > 2048:
        return None
    try:
        parts = urlsplit(value)
    except ValueError:
        return None
    if parts.scheme not in ("http", "https") or not parts.hostname:
        return None
    return value


def clear_cache() -> None:
    _memory_cache.clear()


def is_blocked_site(url: str) -> bool:
    host = (urlsplit(url).hostname or "").lower().rstrip(".")
    return bool(BLOCKED_SITES.search(host))


def import_offer(url: str) -> dict[str, Any]:
    """{title, company, location, text, method, source_url} ou ApiError job_offer.*"""
    raw = (url or "").strip()
    # Collé sans schéma (« www.site.fr/offre ») : https par défaut
    if raw and "://" not in raw:
        raw = f"https://{raw}"
    if is_blocked_site(raw):
        raise ApiError(422, "job_offer.site_blocked")
    source_url = validate_url(raw)

    key = _cache_key(source_url)
    cached = _cache_get(key)
    if cached:
        return {**cached, "cached": True}

    # Redirection vers un site bloquant (raccourcisseur, lien de partage…) refusée avant la requête
    page = fetch_html(source_url, is_blocked=is_blocked_site)
    offer = extract_offer(page.html, page.url) or _from_ats_api(page.url)
    if offer is None:
        raise ApiError(422, "job_offer.no_content")

    result = {**offer.to_dict(), "source_url": source_url}
    _cache_set(key, result)
    return {**result, "cached": False}


def _from_ats_api(url: str) -> ExtractedOffer | None:
    """Page sans offre lisible (rendue en JavaScript) : API publique de l'ATS quand elle est connue."""
    api_url = workable_api_url(url)
    if not api_url:
        return None
    try:
        payload = json.loads(fetch_json(api_url).html)
    except (ApiError, ValueError):
        return None
    account = urlsplit(url).path.strip("/").split("/")[0]
    return from_workable(payload, account) if isinstance(payload, dict) else None


CLEANUP_PROMPT = """Tu reçois le texte brut d'une page d'offre d'emploi, extrait automatiquement.
Renvoie uniquement ce JSON :
{{"title": "intitulé du poste", "company": "entreprise", "location": "lieu", "text": "offre nettoyée"}}

Règles :
- "text" : uniquement l'offre (missions, profil, compétences, conditions, avantages), dans la langue
  d'origine, sans rien inventer ni résumer ; retire menus, bandeaux cookies, liens de partage,
  « offres similaires », mentions légales. Garde les listes à puces (« • ») et les paragraphes.
- Champ inconnu : chaîne vide.

Titre détecté : {title}
Entreprise détectée : {company}
Lieu détecté : {location}

Texte :
{text}
"""


def clean_with_ai(ai: AIService, offer: dict[str, Any]) -> dict[str, Any]:
    """Nettoyage LLM (provider actif de l'utilisateur ou plateforme). Garde l'extraction si la réponse est vide."""
    prompt = CLEANUP_PROMPT.format(
        title=offer.get("title", ""),
        company=offer.get("company", ""),
        location=offer.get("location", ""),
        text=str(offer.get("text", ""))[:20_000],
    )
    data = ai.llm.generate_json(prompt, temperature=0)
    if not isinstance(data, dict):
        return offer
    text = str(data.get("text") or "").strip()
    if len(text) < MIN_TEXT_CHARS:
        return offer
    return {
        **offer,
        "title": str(data.get("title") or offer.get("title") or "").strip(),
        "company": str(data.get("company") or offer.get("company") or "").strip(),
        "location": str(data.get("location") or offer.get("location") or "").strip(),
        "text": text[:MAX_TEXT_CHARS],
        "method": "ai",
    }

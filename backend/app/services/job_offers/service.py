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
    job_posting_from_blocks,
    parse_json_ld,
    from_workable,
    workable_api_url,
)
from app.services.job_offers.fetch import fetch_html, fetch_json, validate_url
from app.services.redis_service import redis_service

CACHE_TTL_SECONDS = 15 * 60
CACHE_PREFIX = "job_offer:"
# Sites qui exigent une connexion ou bloquent les robots : inutile de les appeler
# (Welcome to the Jungle : 503 / délais dépassés pour les robots, vérifié le 6 octobre 2026)
BLOCKED_SITES = re.compile(r"(^|\.)(linkedin|indeed|glassdoor|monster|welcometothejungle)\.[a-z.]+$")

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


# Contenu lu dans le navigateur de l'utilisateur (bookmarklet, copier-coller) : limites d'entrée
MAX_JSON_LD_CHARS = 500_000
MAX_PASTED_CHARS = 200_000
MAX_TITLE_CHARS = 300


def _page_title(title: str) -> str:
    """Titre d'onglet sans le nom du site (« Développeur H/F - Paris - Indeed.com » → « Développeur H/F - Paris »)."""
    title = re.sub(r"\s+", " ", title or "").strip()[:MAX_TITLE_CHARS]
    return re.sub(r"\s*[-|–·]\s*(Indeed(\.\w+)*|LinkedIn|Welcome to the Jungle)\s*$", "", title, flags=re.I)


def _clean_pasted_text(text: str) -> str:
    lines = [re.sub(r"[ \t\u00a0]+", " ", line).strip() for line in (text or "").splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def parse_offer(
    *,
    url: str | None,
    title: str = "",
    json_ld: list[str] | None = None,
    text: str = "",
) -> dict[str, Any]:
    """Offre lue dans le navigateur (sites qui bloquent l'import serveur). Rien n'est téléchargé.

    `json_ld` : balises JSON-LD de la page (bookmarklet) ; `text` : texte de l'offre ou de la page.
    """
    raws = [raw for raw in (json_ld or []) if isinstance(raw, str)]
    if sum(len(raw) for raw in raws) > MAX_JSON_LD_CHARS or len(text or "") > MAX_PASTED_CHARS:
        raise ApiError(413, "job_offer.too_large")

    source_url = safe_offer_url(url)
    offer = job_posting_from_blocks(parse_json_ld(raws)) if raws else None
    if offer is None:
        cleaned = _clean_pasted_text(text)
        if len(cleaned) < MIN_TEXT_CHARS:
            raise ApiError(422, "job_offer.paste_too_short", min_chars=MIN_TEXT_CHARS)
        offer = ExtractedOffer(title=_page_title(title), company="", location="", text=cleaned[:MAX_TEXT_CHARS], method="paste")
    return {**offer.to_dict(), "source_url": source_url}


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

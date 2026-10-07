"""Optimiseur de CV : 1 appel LLM, validation stricte des propositions, puis streaming une par une."""

from __future__ import annotations

import asyncio
import json
import re
from collections.abc import AsyncIterator, Callable
from typing import Any

from app.i18n import DEFAULT_LOCALE, t
from app.services.ai_service import AIService, ai_service
from app.services.llm.errors import LLMError

MAX_SUGGESTIONS = 10
# Une reformulation reste de la taille d'une puce ou d'un court paragraphe
MAX_PROPOSED_CHARS = 800
NUMBER_PATTERN = re.compile(r"\d+(?:[.,]\d+)?")

# Renvoie l'id de l'historique enregistré (None si non persisté)
PersistCallback = Callable[[dict[str, Any]], str | None]


class NoSuggestionError(Exception):
    """Aucune proposition exploitable après validation."""


def _sse(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _text(value: Any, limit: int) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]


def _numbers(text: str) -> set[str]:
    return {number.replace(",", ".") for number in NUMBER_PATTERN.findall(text)}


def locate_in_cv(excerpt: str, cv_text: str) -> str | None:
    """Extrait tel qu'il figure dans le CV (espaces et retours à la ligne d'origine), ou None s'il n'y est pas."""
    excerpt = (excerpt or "").strip()
    if not excerpt:
        return None
    if excerpt in cv_text:
        return excerpt
    # Le modèle normalise souvent les espaces : on tolère toute suite d'espaces entre les mots
    words = excerpt.split()
    match = re.search(r"\s+".join(re.escape(word) for word in words), cv_text)
    return match.group(0) if match else None


def validate_optimization(raw: Any, cv_text: str) -> dict[str, Any]:
    """Garde-fous sur la sortie du LLM.

    - `original` doit être un extrait réel du CV (sinon la proposition ne peut pas être appliquée,
      et le modèle a probablement paraphrasé ou inventé) ;
    - `proposed` ne doit introduire aucun chiffre absent du CV (années, pourcentages, volumes…) ;
    - extraits distincts, propositions non vides et différentes de l'original, nombre plafonné.
    """
    if not isinstance(raw, dict):
        raise NoSuggestionError("réponse non structurée")
    items = raw.get("suggestions")
    if not isinstance(items, list):
        raise NoSuggestionError("suggestions absentes")

    cv_numbers = _numbers(cv_text)
    suggestions: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        original = locate_in_cv(str(item.get("original") or ""), cv_text)
        proposed = str(item.get("proposed") or "").strip()
        if not original or not proposed or original in seen:
            continue
        if " ".join(proposed.split()) == " ".join(original.split()) or len(proposed) > MAX_PROPOSED_CHARS:
            continue
        if not _numbers(proposed) <= cv_numbers:
            continue
        seen.add(original)
        suggestions.append(
            {
                "id": f"s{len(suggestions) + 1}",
                "section": _text(item.get("section"), 80),
                "original": original,
                "proposed": proposed,
                "requirement": _text(item.get("requirement"), 300),
                "rationale": _text(item.get("rationale"), 500),
            }
        )
        if len(suggestions) == MAX_SUGGESTIONS:
            break

    if not suggestions:
        raise NoSuggestionError("aucune proposition valide")
    return {"summary": _text(raw.get("summary"), 500), "suggestions": suggestions}


async def stream_cv_optimization(
    cv_text: str,
    job_text: str,
    *,
    gaps: list[dict[str, str]],
    locale: str = DEFAULT_LOCALE,
    on_result: PersistCallback | None = None,
    ai: AIService | None = None,
) -> AsyncIterator[str]:
    """
    Flux SSE :
    1) statuts pendant l'appel LLM unique
    2) propositions validées diffusées une à une
    3) résultat complet (+ id d'historique) puis complete
    """
    try:
        yield _sse({"type": "status", "message": t("cv_optimizer.start", locale)})
        yield _sse({"type": "status", "message": t("cv_optimizer.gemini", locale)})
        yield _sse({"type": "progress", "value": 12, "current": 0, "total": 1})

        raw = await asyncio.to_thread((ai or ai_service).optimize_cv, cv_text, job_text, gaps)
        result = validate_optimization(raw, cv_text)

        optimization_id = None
        if on_result is not None:
            try:
                optimization_id = on_result(result)
            except Exception as persist_exc:
                print(f"Erreur persistance optimisation de CV: {persist_exc!r}")

        suggestions = result["suggestions"]
        total = len(suggestions)
        yield _sse({"type": "status", "message": t("cv_optimizer.streaming", locale, total=total)})
        for index, suggestion in enumerate(suggestions):
            progress = 40 + ((index + 1) / total) * 55
            yield _sse({"type": "progress", "value": progress, "current": index + 1, "total": total})
            yield _sse({"type": "suggestion", "suggestion": suggestion})
            await asyncio.sleep(0.06)

        yield _sse({"type": "progress", "value": 100, "current": total, "total": total})
        yield _sse({"type": "result", "summary": result["summary"], "id": optimization_id})
        yield _sse({"type": "complete"})

    except LLMError as exc:
        yield _sse({"type": "error", "message": t(exc.code, locale), "code": exc.code})
    except NoSuggestionError as exc:
        print(f"Optimisation de CV sans proposition valide: {exc}")
        yield _sse({"type": "error", "message": t("cv_optimizer.no_suggestions", locale), "code": "cv_optimizer.no_suggestions"})
    except Exception as exc:
        print(f"Erreur stream_cv_optimization: {exc!r}")
        yield _sse({"type": "error", "message": t("cv_optimizer.failed", locale), "code": "cv_optimizer.failed"})

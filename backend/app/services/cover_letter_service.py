"""Lettre de motivation : 1 appel Gemini puis streaming progressif des paragraphes."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator, Callable
from typing import Any

from app.i18n import DEFAULT_LOCALE, t
from app.services.ai_service import ai_service

TONES = ("professional", "warm", "confident", "formal")
LENGTHS = ("short", "standard", "detailed")
LANGUAGES = ("auto", "fr", "en")

# Renvoie l'id de l'historique enregistré (None si non persisté)
PersistCallback = Callable[[dict[str, Any]], str | None]


def _sse(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def letter_sections(letter: dict[str, Any]) -> list[dict[str, str]]:
    """Sections dans l'ordre de lecture, diffusées une à une."""
    sections = [{"key": "subject", "text": letter.get("subject") or ""}]
    sections += [{"key": key, "text": letter.get(key) or ""} for key in ("greeting", "opening")]
    sections += [{"key": "body", "text": paragraph} for paragraph in letter.get("body") or []]
    sections += [{"key": key, "text": letter.get(key) or ""} for key in ("closing", "signoff", "signature")]
    return [section for section in sections if section["text"]]


async def stream_cover_letter(
    cv_text: str,
    job_text: str,
    *,
    tone: str,
    length: str,
    language: str,
    locale: str = DEFAULT_LOCALE,
    on_result: PersistCallback | None = None,
) -> AsyncIterator[str]:
    """
    Flux SSE :
    1) statuts pendant l'appel LLM unique
    2) sections de la lettre diffusées une à une
    3) lettre complète (+ id d'historique) puis complete
    """
    try:
        yield _sse({"type": "status", "message": t("cover_letter.start", locale)})
        yield _sse({"type": "status", "message": t("cover_letter.gemini", locale)})
        yield _sse({"type": "progress", "value": 12, "current": 0, "total": 1})

        letter = await asyncio.to_thread(
            ai_service.generate_cover_letter,
            cv_text,
            job_text,
            tone=tone,
            length=length,
            language=language,
        )

        letter_id = None
        if on_result is not None:
            try:
                letter_id = on_result(letter)
            except Exception as persist_exc:
                print(f"Erreur persistance lettre de motivation: {persist_exc!r}")

        sections = letter_sections(letter)
        total = len(sections)
        yield _sse({"type": "status", "message": t("cover_letter.writing", locale)})
        yield _sse({"type": "progress", "value": 40, "current": 0, "total": total})

        for index, section in enumerate(sections):
            progress = 40 + ((index + 1) / max(total, 1)) * 55
            yield _sse({"type": "progress", "value": progress, "current": index + 1, "total": total})
            yield _sse({"type": "section", "section": section})
            await asyncio.sleep(0.08)

        yield _sse({"type": "progress", "value": 100, "current": total, "total": total})
        yield _sse({"type": "letter", "letter": letter, "id": letter_id})
        yield _sse({"type": "complete"})

    except Exception as exc:
        print(f"Erreur stream_cover_letter: {exc!r}")
        yield _sse({"type": "error", "message": t("cover_letter.failed", locale)})

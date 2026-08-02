"""Comparaison CV ↔ offre : 1 appel Gemini puis streaming progressif des items."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any

from app.services.ai_service import ai_service


def _sse(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


async def stream_comparison(
    offer_text: str,
    cv_text: str,
    *,
    intro_message: str = "Début de l'analyse…",
) -> AsyncIterator[str]:
    """
    Flux SSE optimisé :
    1) statuts pendant l'appel LLM unique
    2) items diffusés un par un pour une UI progressive
    3) summary + complete
    """
    try:
        yield _sse({"type": "status", "message": intro_message})
        yield _sse(
            {
                "type": "status",
                "message": "Analyse ATS par Gemini (extraction + matching)…",
            }
        )
        yield _sse({"type": "progress", "value": 12, "current": 0, "total": 1})

        result = await asyncio.to_thread(
            ai_service.compare_offer_and_cv,
            offer_text,
            cv_text,
        )

        items = result["items"]
        summary = result["summary"]
        total = len(items)

        yield _sse(
            {
                "type": "status",
                "message": f"{total} exigences analysées — diffusion des résultats…",
            }
        )
        yield _sse({"type": "progress", "value": 35, "current": 0, "total": total})

        for index, item in enumerate(items):
            # Progress 35% → 95% pendant la diffusion
            progress = 35 + ((index + 1) / max(total, 1)) * 60
            yield _sse(
                {
                    "type": "progress",
                    "value": progress,
                    "current": index + 1,
                    "total": total,
                }
            )
            yield _sse({"type": "item", "item": item})
            # Petite pause pour l'animation front (sans ralentir trop)
            await asyncio.sleep(0.04)

        yield _sse({"type": "progress", "value": 100, "current": total, "total": total})
        yield _sse({"type": "summary", "summary": summary})
        yield _sse({"type": "complete"})

    except Exception as exc:
        print(f"Erreur stream_comparison: {exc}")
        yield _sse({"type": "error", "message": str(exc)})


class ComparisonService:
    """Compatibilité avec les imports existants."""

    def __init__(self) -> None:
        self.ai_service = ai_service

    async def compare_cv_offer_stream(self, offer_text: str, cv_text: str, job_category: str = None):
        # Conservé pour compat éventuelle — préférer stream_comparison
        return ai_service.compare_offer_and_cv(offer_text, cv_text)

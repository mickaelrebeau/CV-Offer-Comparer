"""Évolution entre deux analyses de la même offre : score avant → après, items améliorés ou en régression."""

import re
import unicodedata
from difflib import SequenceMatcher
from typing import Any

from app.models.comparison_record import ComparisonRecord

# Rang d'un statut : une hausse est une amélioration, une baisse une régression
STATUS_RANK = {"missing": 0, "unclear": 1, "match": 2}
# Deux analyses du même texte d'offre reformulent parfois un critère : appariement approché au-delà de ce seuil
FUZZY_THRESHOLD = 0.8


def _normalize(text: Any) -> str:
    text = unicodedata.normalize("NFKD", str(text or "")).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _status(item: dict[str, Any]) -> str:
    status = item.get("status")
    return status if status in STATUS_RANK else "unclear"


def _key(item: dict[str, Any]) -> tuple[str, str]:
    return _normalize(item.get("category")), _normalize(item.get("offerText"))


def pair_items(
    before: list[dict[str, Any]], after: list[dict[str, Any]]
) -> tuple[list[tuple[dict, dict]], list[dict], list[dict]]:
    """Apparie les items par catégorie + texte d'offre (exact, puis approché dans la même catégorie).

    Renvoie (paires, items disparus, items nouveaux).
    """
    pairs: list[tuple[dict, dict]] = []
    remaining = list(after)

    unmatched_before = []
    for old in before:
        match = next((new for new in remaining if _key(new) == _key(old)), None)
        if match is None:
            unmatched_before.append(old)
        else:
            pairs.append((old, match))
            remaining.remove(match)

    removed = []
    for old in unmatched_before:
        category, text = _key(old)
        candidates = [
            (SequenceMatcher(None, text, _key(new)[1]).ratio(), new)
            for new in remaining
            if _key(new)[0] == category
        ]
        score, best = max(candidates, key=lambda candidate: candidate[0], default=(0.0, None))
        if best is not None and score >= FUZZY_THRESHOLD:
            pairs.append((old, best))
            remaining.remove(best)
        else:
            removed.append(old)

    return pairs, removed, remaining


def _side(record: ComparisonRecord) -> dict[str, Any]:
    return {
        "id": str(record.id),
        "match_percentage": record.match_percentage,
        "matches": record.matches,
        "missing": record.missing,
        "unclear": record.unclear,
        "total_items": record.total_items,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }


def _change(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    return {
        "category": new.get("category") or old.get("category"),
        "offerText": new.get("offerText") or old.get("offerText"),
        "before": _status(old),
        "after": _status(new),
        "cvText": new.get("cvText"),
    }


def diff_comparisons(before: ComparisonRecord, after: ComparisonRecord) -> dict[str, Any]:
    pairs, removed, added = pair_items(list(before.items or []), list(after.items or []))
    improved, regressed, unchanged = [], [], 0
    for old, new in pairs:
        delta = STATUS_RANK[_status(new)] - STATUS_RANK[_status(old)]
        if delta > 0:
            improved.append(_change(old, new))
        elif delta < 0:
            regressed.append(_change(old, new))
        else:
            unchanged += 1

    return {
        "before": _side(before),
        "after": _side(after),
        "score_delta": after.match_percentage - before.match_percentage,
        "same_offer": _normalize(before.offer_text) == _normalize(after.offer_text),
        "improved": improved,
        "regressed": regressed,
        "unchanged": unchanged,
        "added": [{"category": item.get("category"), "offerText": item.get("offerText"), "status": _status(item)} for item in added],
        "removed": [{"category": item.get("category"), "offerText": item.get("offerText"), "status": _status(item)} for item in removed],
    }

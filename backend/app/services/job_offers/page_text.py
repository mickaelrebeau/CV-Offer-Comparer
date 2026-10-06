"""Offre Indeed extraite du texte visible de la page (copier-coller, ou bouton « Envoyer vers Talento »
quand les sélecteurs CSS ne correspondent plus).

Les classes d'Indeed changent souvent, pas ses libellés : le panneau de l'offre affichée suit
toujours « titre, entreprise, (note), lieu, contrat, Postuler… », puis « Description du poste »,
la description, et « Signaler l'offre ». La liste des offres recommandées qui précède est ignorée.
"""

from __future__ import annotations

import re

from app.services.job_offers.extract import MAX_TEXT_CHARS, MIN_TEXT_CHARS, ExtractedOffer


def _line(pattern: str) -> re.Pattern[str]:
    return re.compile(rf"^\s*(?:{pattern})\s*$", re.IGNORECASE)


APPLY = _line(
    r"postuler maintenant|postuler sur le site de l[’']entreprise|postuler|apply now|apply on company site"
)
DESCRIPTION_START = _line(
    r"description (?:complète )?du poste|full job description|job description|descripción (?:completa )?del empleo"
)
DESCRIPTION_END = _line(
    r"signaler l[’']offre|report job|hiring lab|guide carrières|career guide|© \d{4} indeed"
)
LIST_END = _line(r"afficher plus d[’']emplois|show more jobs|voir plus d[’']offres")
# Lignes d'en-tête sans information : séparateurs, note de l'entreprise, badges
HEADER_NOISE = _line(
    r"·|•|-|\d(?:[.,]\d)?|\d(?:[.,]\d)? (?:sur|out of) 5(?: étoiles| stars)?|nouveau|new|annonce|sponsored"
    r"|candidature simplifiée|easily apply|répond généralement.*|typically responds.*"
)
CONTRACT = re.compile(
    r"\b(cdi|cdd|int[ée]rim|stage|alternance|apprentissage|freelance|ind[ée]pendant|temps plein|temps partiel"
    r"|full[- ]time|part[- ]time|contract|temporary|internship|permanent)\b",
    re.IGNORECASE,
)
HEADER_MAX_LINES = 10


def _lines(text: str) -> list[str]:
    return [re.sub(r"[ \t ]+", " ", line).strip() for line in (text or "").splitlines()]


def _last_index(lines: list[str], pattern: re.Pattern[str], before: int) -> int | None:
    return next((i for i in range(before - 1, -1, -1) if pattern.match(lines[i])), None)


def from_indeed_text(text: str) -> ExtractedOffer | None:
    lines = _lines(text)
    start = next((i for i, line in enumerate(lines) if DESCRIPTION_START.match(line)), None)
    if start is None:
        return None
    end = next((i for i in range(start + 1, len(lines)) if DESCRIPTION_END.match(lines[i])), len(lines))
    description = re.sub(r"\n{3,}", "\n\n", "\n".join(lines[start + 1 : end])).strip()
    if len(description) < MIN_TEXT_CHARS:
        return None

    title = company = location = ""
    apply = _last_index(lines, APPLY, before=start)
    if apply is not None:
        # En-tête : du dernier repère de fin de liste (ou au plus HEADER_MAX_LINES lignes) jusqu'à « Postuler »
        list_end = _last_index(lines, LIST_END, before=apply)
        first = max(list_end + 1 if list_end is not None else 0, apply - HEADER_MAX_LINES)
        header = [line for line in lines[first:apply] if line and not HEADER_NOISE.match(line)]
        if header:
            title = header[0]
        if len(header) > 1:
            company = header[1]
        location = next((line for line in header[2:] if not CONTRACT.search(line)), "")

    return ExtractedOffer(
        title=title[:300],
        company=company[:300],
        location=location[:300],
        text=description[:MAX_TEXT_CHARS],
        method="page",
    )

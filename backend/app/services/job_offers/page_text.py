"""Offre extraite du texte visible d'une page Indeed ou LinkedIn (copier-coller, ou bouton
« Envoyer vers Talento » quand les sélecteurs CSS ne correspondent plus).

Leurs classes CSS changent souvent (LinkedIn les génère), pas leurs libellés. On repère le panneau
de l'offre affichée grâce à eux et on ignore la liste de résultats, les menus et les encarts.
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


# --- LinkedIn -------------------------------------------------------------------------------------
# Panneau de l'offre : « entreprise », « titre », « lieu · il y a 2 semaines · 90 candidats »,
# (« Hybride », « Temps plein », « Postuler »…), puis « À propos de l'offre d'emploi », la
# description, et « … plus » / l'encart Premium / « À propos de l'entreprise ».

LINKEDIN_DESCRIPTION_START = _line(r"à propos de l[’']offre d[’']emploi|about the job|à propos du poste")
LINKEDIN_DESCRIPTION_END = _line(
    r"… ?plus|\.\.\. ?plus|… ?more|\.\.\. ?more|afficher moins|voir moins|show less|see less"
    r"|à propos de l[’']entreprise|about the company|des recherches d[’']emploi plus rapides avec premium"
    r"|job search faster with premium|.*millions d[’']autres membres utilisent premium.*"
)
# « Lille, Hauts-de-France, France · il y a 2 semaines · 90 personnes ont cliqué sur Postuler »
LINKEDIN_META = re.compile(
    r"^(?P<location>[^·]+?)\s+·\s+.*\b(il y a|republiée|reposted|ago|candidat|applicant|clicked apply|postuler)\b",
    re.IGNORECASE,
)
WORKPLACE = _line(r"hybride|sur site|à distance|télétravail|hybrid|on-site|remote")
LINKEDIN_META_WINDOW = 15


def from_linkedin_text(text: str) -> ExtractedOffer | None:
    lines = _lines(text)
    start = next((i for i, line in enumerate(lines) if LINKEDIN_DESCRIPTION_START.match(line)), None)
    if start is None:
        return None
    end = next((i for i in range(start + 1, len(lines)) if LINKEDIN_DESCRIPTION_END.match(lines[i])), len(lines))
    description = re.sub(r"\n{3,}", "\n\n", "\n".join(lines[start + 1 : end])).strip()
    if len(description) < MIN_TEXT_CHARS:
        return None

    title = company = location = ""
    # Dernière ligne « lieu · date · candidats » avant la description : en-tête de l'offre affichée
    meta = next(
        (i for i in range(start - 1, -1, -1) if LINKEDIN_META.match(lines[i])),
        None,
    )
    if meta is not None:
        location = LINKEDIN_META.match(lines[meta])["location"].strip()
        above = [line for line in lines[max(0, meta - 6) : meta] if line]
        if above:
            title = above[-1]
        if len(above) > 1:
            company = above[-2]
        workplace = next(
            (line for line in lines[meta + 1 : meta + LINKEDIN_META_WINDOW] if WORKPLACE.match(line)), None
        )
        if workplace and workplace.lower() not in location.lower():
            location = f"{location} ({workplace})"

    return ExtractedOffer(
        title=title[:300],
        company=company[:300],
        location=location[:300],
        text=description[:MAX_TEXT_CHARS],
        method="page",
    )


def from_page_text(text: str, host: str = "") -> ExtractedOffer | None:
    """Extracteur du site du lien d'abord, puis l'autre (lien d'un site, texte copié d'un autre)."""
    if re.search(r"(^|\.)linkedin\.", host):
        return from_linkedin_text(text) or from_indeed_text(text)
    return from_indeed_text(text) or from_linkedin_text(text)

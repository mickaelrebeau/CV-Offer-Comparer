"""Extraction d'une offre d'emploi depuis le HTML d'une page.

Ordre de priorité :
1. données structurées JSON-LD `schema.org/JobPosting` (Welcome to the Jungle, APEC, Lever,
   Greenhouse, Workable, la plupart des sites carrières : elles servent au référencement Google) ;
2. contenu principal de la page (trafilatura), sans menus, bandeaux cookies ni « offres similaires ».
"""

from __future__ import annotations

import html as html_lib
import json
import re
from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urlsplit

import lxml.etree
import lxml.html
import trafilatura

MAX_TEXT_CHARS = 50_000
MIN_TEXT_CHARS = 200


@dataclass
class ExtractedOffer:
    title: str
    company: str
    location: str
    text: str
    method: str  # "json-ld" | "api" | "html" | "page" | "paste" | "ai"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", html_lib.unescape(str(value or ""))).strip()


def html_to_text(fragment: str) -> str:
    """Description HTML (JSON-LD) → texte lisible : paragraphes et puces conservés."""
    fragment = html_lib.unescape(fragment or "")
    if "<" not in fragment:
        return fragment.strip()
    root = lxml.html.fragment_fromstring(fragment, create_parent="div")
    for br in root.iter("br"):
        br.tail = "\n" + (br.tail or "")
    for element in root.iter("p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "tr"):
        element.tail = "\n\n" + (element.tail or "")
    for item in root.iter("li"):
        item.text = "• " + (item.text or "")
        item.tail = "\n" + (item.tail or "")
    text = root.text_content()
    lines = [re.sub(r"[ \t ]+", " ", line).strip() for line in text.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


# --- JSON-LD -----------------------------------------------------------------------------


def parse_json_ld(raws: list[str]) -> list[Any]:
    """Blocs JSON-LD lisibles parmi les textes donnés (balises <script> de la page)."""
    blocks = []
    for raw in raws:
        raw = (raw or "").strip()
        if not raw:
            continue
        try:
            blocks.append(json.loads(raw))
        except json.JSONDecodeError:
            # Certains sites laissent des retours à la ligne bruts dans les chaînes
            try:
                blocks.append(json.loads(re.sub(r"[\r\n\t]+", " ", raw)))
            except json.JSONDecodeError:
                continue
    return blocks


def _json_ld_blocks(document: lxml.html.HtmlElement) -> list[Any]:
    return parse_json_ld([script.text or "" for script in document.xpath('//script[@type="application/ld+json"]')])


def _iter_nodes(node: Any):
    if isinstance(node, list):
        for item in node:
            yield from _iter_nodes(item)
    elif isinstance(node, dict):
        yield node
        for key in ("@graph", "mainEntity", "itemListElement"):
            if key in node:
                yield from _iter_nodes(node[key])


def _is_job_posting(node: dict) -> bool:
    types = node.get("@type")
    types = types if isinstance(types, list) else [types]
    return any(str(t).split("/")[-1] == "JobPosting" for t in types)


def _name(value: Any) -> str:
    if isinstance(value, list):
        value = value[0] if value else ""
    if isinstance(value, dict):
        return _clean(value.get("name"))
    return _clean(value)


def _location(value: Any) -> str:
    places = value if isinstance(value, list) else [value]
    names = []
    for place in places:
        if not isinstance(place, dict):
            if place:
                names.append(_clean(place))
            continue
        address = place.get("address", place)
        if isinstance(address, dict):
            parts = [address.get("addressLocality"), address.get("addressRegion"), address.get("addressCountry")]
            parts = [_name(part) for part in parts if part]
            label = ", ".join(dict.fromkeys(part for part in parts if part))
        else:
            label = _clean(address)
        if label and label not in names:
            names.append(label)
    return " / ".join(names)


def from_json_ld(document: lxml.html.HtmlElement) -> ExtractedOffer | None:
    headings = document.xpath("//h1")
    title_hint = _clean(headings[0].text_content()) if headings else ""
    return job_posting_from_blocks(_json_ld_blocks(document), title_hint=title_hint)


def _comparable(value: str) -> str:
    return re.sub(r"[^\w]+", " ", (value or "").lower()).strip()


def _same_title(a: str, b: str) -> bool:
    a, b = _comparable(a), _comparable(b)
    return bool(a and b) and (a in b or b in a)


def _posting_offer(node: dict) -> ExtractedOffer | None:
    text = html_to_text(str(node.get("description") or ""))
    if len(text) < MIN_TEXT_CHARS:
        return None
    location = _location(node.get("jobLocation"))
    if not location and str(node.get("jobLocationType", "")).upper() == "TELECOMMUTE":
        location = "Remote"
    return ExtractedOffer(
        title=_clean(node.get("title")),
        company=_name(node.get("hiringOrganization")),
        location=location,
        text=text[:MAX_TEXT_CHARS],
        method="json-ld",
    )


def job_posting_from_blocks(blocks: list[Any], title_hint: str = "") -> ExtractedOffer | None:
    """Offre `JobPosting` de la page parmi des blocs JSON-LD déjà décodés.

    Une seule offre : retenue. Plusieurs (liste de résultats, « offres similaires ») : seule celle
    dont le titre correspond à l'offre affichée (`title_hint`) est retenue, sinon aucune — prendre
    la première afficherait l'offre d'un autre employeur.
    """
    offers = [
        offer
        for block in blocks
        for node in _iter_nodes(block)
        if _is_job_posting(node) and (offer := _posting_offer(node)) is not None
    ]
    if len(offers) == 1:
        return offers[0]
    return next((offer for offer in offers if _same_title(offer.title, title_hint)), None)


# --- Contenu principal (fallback) ------------------------------------------------------------


def _meta(document: lxml.html.HtmlElement, *names: str) -> str:
    for name in names:
        values = document.xpath(f'//meta[@property="{name}" or @name="{name}"]/@content')
        if values and values[0].strip():
            return _clean(values[0])
    return ""


def from_main_content(page_html: str, document: lxml.html.HtmlElement, url: str) -> ExtractedOffer | None:
    text = trafilatura.extract(
        page_html,
        url=url,
        include_comments=False,
        include_tables=True,
        include_links=False,
        favor_precision=True,
        # Pas de deduplicate : son cache est global au processus et viderait un 2e import de la même page
    )
    if not text or len(text.strip()) < MIN_TEXT_CHARS:
        return None
    titles = document.xpath("//title/text()")
    title = _meta(document, "og:title", "twitter:title") or (_clean(titles[0]) if titles else "")
    return ExtractedOffer(
        title=title,
        company=_meta(document, "og:site_name"),
        location="",
        text=text.strip()[:MAX_TEXT_CHARS],
        method="html",
    )


def extract_offer(page_html: str, url: str) -> ExtractedOffer | None:
    """Offre extraite, ou None si la page ne contient pas de texte exploitable (page rendue en JS…)."""
    try:
        document = lxml.html.document_fromstring(page_html)
    except (lxml.etree.ParserError, ValueError):
        return None
    return from_json_ld(document) or from_main_content(page_html, document, url)


# --- Adaptateurs d'ATS (pages rendues en JavaScript, sans JSON-LD) -------------------------------

WORKABLE_JOB = re.compile(r"^/(?P<account>[\w-]+)/j/(?P<shortcode>[A-Z0-9]+)/?$")


def workable_api_url(url: str) -> str | None:
    """apply.workable.com/<compte>/j/<code> → URL de l'API publique de l'offre."""
    parts = urlsplit(url)
    if (parts.hostname or "").lower() != "apply.workable.com":
        return None
    match = WORKABLE_JOB.match(parts.path)
    if not match:
        return None
    return f"https://apply.workable.com/api/v2/accounts/{match['account']}/jobs/{match['shortcode']}"


def from_workable(payload: dict[str, Any], account: str) -> ExtractedOffer | None:
    sections = [payload.get(key) for key in ("description", "requirements", "benefits")]
    text = "\n\n".join(html_to_text(str(section)) for section in sections if section)
    if len(text) < MIN_TEXT_CHARS:
        return None
    location = payload.get("location") or {}
    if isinstance(location, dict):
        parts = [location.get("city"), location.get("region"), location.get("country")]
        location = ", ".join(dict.fromkeys(_clean(part) for part in parts if part))
    if not location and payload.get("remote"):
        location = "Remote"
    return ExtractedOffer(
        title=_clean(payload.get("title")),
        company=account,
        location=_clean(location),
        text=text[:MAX_TEXT_CHARS],
        method="api",
    )

"""Import d'offre depuis une URL : extraction (JSON-LD, contenu principal) et protection SSRF."""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from uuid import UUID

import httpx
import pytest
from sqlalchemy import select

from app.i18n import ApiError
from app.models.comparison_record import ComparisonRecord
from app.services.job_offers import fetch, service
from app.services.job_offers.fetch import PublicOnlyBackend
from app.services.job_offers.service import safe_offer_url
from tests.test_comparison_stream_persist import FAKE_RESULT

PUBLIC_IP = "93.184.216.34"
DESCRIPTION = (
    "<p>Nous recherchons un·e <strong>développeur·se front-end Vue.js</strong> pour rejoindre notre équipe produit.</p>"
    "<h3>Missions</h3><ul><li>Développer les nouvelles fonctionnalités en Vue 3 et TypeScript</li>"
    "<li>Concevoir des composants accessibles et testés</li><li>Participer aux revues de code</li></ul>"
    "<h3>Profil</h3><p>3 ans d'expérience minimum, maîtrise de Pinia et Vite.<br>Anglais professionnel.</p>"
)


def job_posting_page(**overrides) -> str:
    posting = {
        "@context": "https://schema.org",
        "@type": "JobPosting",
        "title": "Développeur Front-end Vue.js (H/F)",
        "description": DESCRIPTION,
        "hiringOrganization": {"@type": "Organization", "name": "Talento &amp; Co"},
        "jobLocation": {
            "@type": "Place",
            "address": {"addressLocality": "Paris", "addressRegion": "Île-de-France", "addressCountry": "FR"},
        },
        **overrides,
    }
    graph = {"@context": "https://schema.org", "@graph": [{"@type": "WebSite", "name": "Jobs"}, posting]}
    return f"""<html><head><title>Offre</title>
<script type="application/ld+json">{json.dumps(graph)}</script></head>
<body><nav>Accueil · Offres · Connexion</nav><div id="app"></div></body></html>"""


ARTICLE_PAGE = """<html><head>
<title>Data Analyst - Carrières ACME</title>
<meta property="og:title" content="Data Analyst (CDI) — Lyon">
<meta property="og:site_name" content="ACME Carrières">
</head><body>
<nav><a href="/">Accueil</a> <a href="/offres">Toutes nos offres</a> <a href="/login">Connexion</a></nav>
<div class="cookie-banner">Nous utilisons des cookies pour améliorer votre expérience. Accepter / Refuser</div>
<main><article>
<h1>Data Analyst (CDI)</h1>
<p>Rattaché·e à la direction financière, vous construisez les tableaux de bord de pilotage de l'activité
et accompagnez les équipes métiers dans l'analyse de leurs données au quotidien.</p>
<h2>Vos missions</h2>
<p>Modéliser les données de ventes dans l'entrepôt, automatiser les rapports hebdomadaires,
et animer des ateliers de formation SQL pour les équipes opérationnelles de toutes les régions.</p>
<h2>Votre profil</h2>
<p>Diplômé·e d'une école d'ingénieur ou équivalent, vous maîtrisez SQL, Python et un outil de visualisation
comme Power BI ou Looker. Vous savez vulgariser des résultats complexes auprès de non-spécialistes.</p>
</article></main>
<aside><h3>Offres similaires</h3><ul><li>Data Engineer</li><li>Contrôleur de gestion</li></ul></aside>
<footer>Mentions légales · Plan du site</footer>
</body></html>"""


@pytest.fixture
def web(monkeypatch):
    """Faux Internet : `pages[url] = (statut, en-têtes, corps)` ; `dns[host] = [IP…]` (public par défaut)."""
    state = SimpleNamespace(pages={}, dns={}, calls=[], fail=None)

    def resolve(host, port):
        return state.dns.get(host, [PUBLIC_IP])

    def handler(request: httpx.Request) -> httpx.Response:
        state.calls.append(str(request.url))
        if state.fail:
            raise state.fail
        status, headers, body = state.pages.get(str(request.url), (404, {"content-type": "text/html"}, "Not found"))
        return httpx.Response(status, headers=headers, content=body.encode() if isinstance(body, str) else body)

    monkeypatch.setattr(fetch, "_resolve", resolve)
    monkeypatch.setattr(fetch, "http_transport", httpx.MockTransport(handler))
    service.clear_cache()
    yield state
    service.clear_cache()


def html(body: str, status: int = 200, **headers) -> tuple:
    return status, {"content-type": "text/html; charset=utf-8", **headers}, body


def _import(client, headers, url, **extra):
    return client.post("/api/job-offers/import", headers=headers, json={"url": url, **extra})


# --- Extraction ---------------------------------------------------------------------


def test_json_ld_job_posting(client, auth_headers, web):
    web.pages["https://jobs.example.com/offre/42"] = html(job_posting_page())
    response = _import(client, auth_headers, "https://jobs.example.com/offre/42")

    assert response.status_code == 200, response.text
    offer = response.json()
    assert offer["method"] == "json-ld"
    assert offer["title"] == "Développeur Front-end Vue.js (H/F)"
    assert offer["company"] == "Talento & Co"
    assert offer["location"] == "Paris, Île-de-France, FR"
    assert offer["source_url"] == "https://jobs.example.com/offre/42"
    assert "• Développer les nouvelles fonctionnalités en Vue 3 et TypeScript" in offer["text"]
    assert "Anglais professionnel." in offer["text"]
    assert "<" not in offer["text"]
    # Menus de la page ignorés
    assert "Connexion" not in offer["text"]


def test_json_ld_variants(client, auth_headers, web):
    page = job_posting_page(
        **{
            "@type": ["JobPosting"],
            "hiringOrganization": "Startup",
            "jobLocation": [
                {"address": {"addressLocality": "Nantes", "addressCountry": {"name": "France"}}},
                {"address": {"addressLocality": "Rennes", "addressCountry": "France"}},
            ],
        }
    )
    web.pages["https://jobs.example.com/a"] = html(page)
    offer = _import(client, auth_headers, "https://jobs.example.com/a").json()
    assert offer["company"] == "Startup"
    assert offer["location"] == "Nantes, France / Rennes, France"


def test_remote_job_location(client, auth_headers, web):
    page = job_posting_page(jobLocation=None, jobLocationType="TELECOMMUTE")
    web.pages["https://jobs.example.com/remote"] = html(page)
    assert _import(client, auth_headers, "https://jobs.example.com/remote").json()["location"] == "Remote"


def test_main_content_fallback(client, auth_headers, web):
    web.pages["https://careers.acme.test/data-analyst"] = html(ARTICLE_PAGE)
    response = _import(client, auth_headers, "https://careers.acme.test/data-analyst")

    assert response.status_code == 200, response.text
    offer = response.json()
    assert offer["method"] == "html"
    assert offer["title"] == "Data Analyst (CDI) — Lyon"
    assert offer["company"] == "ACME Carrières"
    assert "Modéliser les données de ventes" in offer["text"]
    for noise in ("cookies", "Offres similaires", "Mentions légales", "Toutes nos offres"):
        assert noise not in offer["text"]


def test_page_without_offer(client, auth_headers, web):
    web.pages["https://spa.example.com/job/1"] = html('<html><body><div id="root"></div><script src="/app.js"></script></body></html>')
    response = _import(client, auth_headers, "https://spa.example.com/job/1")
    assert response.status_code == 422
    assert response.json()["code"] == "job_offer.no_content"


def test_url_without_scheme_defaults_to_https(client, auth_headers, web):
    web.pages["https://jobs.example.com/offre/42"] = html(job_posting_page())
    response = _import(client, auth_headers, "jobs.example.com/offre/42")
    assert response.status_code == 200
    assert response.json()["source_url"] == "https://jobs.example.com/offre/42"


def test_latin1_page_without_charset(client, auth_headers, web):
    body = job_posting_page().encode("cp1252", errors="replace")
    web.pages["https://old.example.com/offre"] = (200, {"content-type": "text/html"}, body)
    offer = _import(client, auth_headers, "https://old.example.com/offre").json()
    assert offer["location"] == "Paris, Île-de-France, FR"


def test_workable_page_uses_public_api(client, auth_headers, web):
    """Page Workable rendue en JavaScript : l'offre est lue via l'API publique de l'ATS."""
    web.pages["https://apply.workable.com/j/ABC123"] = (302, {"location": "/acme/j/ABC123/"}, "")
    web.pages["https://apply.workable.com/acme/j/ABC123/"] = html('<html><body><div id="app"></div></body></html>')
    web.pages["https://apply.workable.com/api/v2/accounts/acme/jobs/ABC123"] = (
        200,
        {"content-type": "application/json"},
        json.dumps(
            {
                "title": "Machine Learning Engineer",
                "location": {"city": "Paris", "region": "Île-de-France", "country": "France"},
                "description": DESCRIPTION,
                "requirements": "<ul><li>Python</li><li>PyTorch</li></ul>",
                "benefits": "<p>Télétravail partiel</p>",
            }
        ),
    )
    offer = _import(client, auth_headers, "https://apply.workable.com/j/ABC123").json()
    assert offer["method"] == "api"
    assert offer["title"] == "Machine Learning Engineer"
    assert offer["company"] == "acme"
    assert offer["location"] == "Paris, Île-de-France, France"
    assert "• PyTorch" in offer["text"]
    assert "Télétravail partiel" in offer["text"]


# --- Protection SSRF -------------------------------------------------------------------


@pytest.mark.parametrize(
    "url,code",
    [
        ("http://127.0.0.1/admin", "job_offer.forbidden_url"),
        ("http://169.254.169.254/latest/meta-data/", "job_offer.forbidden_url"),
        ("http://10.0.0.5/", "job_offer.forbidden_url"),
        ("http://192.168.1.1/", "job_offer.forbidden_url"),
        ("http://[::1]/", "job_offer.forbidden_url"),
        ("http://[::ffff:127.0.0.1]/", "job_offer.forbidden_url"),
        ("http://0.0.0.0/", "job_offer.forbidden_url"),
        ("http://localhost/", "job_offer.forbidden_url"),
        ("http://redis.internal/", "job_offer.forbidden_url"),
        ("http://jobs.example.com:6379/", "job_offer.forbidden_url"),
        ("https://user:secret@jobs.example.com/", "job_offer.forbidden_url"),
        ("ftp://jobs.example.com/offre", "job_offer.invalid_url"),
        ("file:///etc/passwd", "job_offer.invalid_url"),
        ("javascript:alert(1)", "job_offer.invalid_url"),
        ("", "job_offer.invalid_url"),
    ],
)
def test_forbidden_urls(client, auth_headers, web, url, code):
    response = _import(client, auth_headers, url)
    assert response.status_code == 400, (url, response.text)
    assert response.json()["code"] == code
    assert web.calls == []


def test_hostname_resolving_to_private_ip(client, auth_headers, web):
    web.dns["evil.example.com"] = [PUBLIC_IP, "10.0.0.7"]
    response = _import(client, auth_headers, "https://evil.example.com/job")
    assert response.json()["code"] == "job_offer.forbidden_url"
    assert web.calls == []


@pytest.mark.parametrize(
    "location",
    ["http://169.254.169.254/latest/meta-data/", "http://127.0.0.1:80/", "http://intranet.local/"],
)
def test_redirect_to_private_address_is_refused(client, auth_headers, web, location):
    web.pages["https://short.example.com/x"] = (302, {"location": location}, "")
    response = _import(client, auth_headers, "https://short.example.com/x")
    assert response.status_code == 400
    assert response.json()["code"] == "job_offer.forbidden_url"
    assert web.calls == ["https://short.example.com/x"]


def test_redirect_to_host_resolving_privately(client, auth_headers, web):
    web.dns["rebind.example.com"] = ["127.0.0.1"]
    web.pages["https://short.example.com/y"] = (301, {"location": "https://rebind.example.com/"}, "")
    assert _import(client, auth_headers, "https://short.example.com/y").json()["code"] == "job_offer.forbidden_url"


def test_redirects_are_followed_and_capped(client, auth_headers, web):
    web.pages["https://short.example.com/ok"] = (301, {"location": "/offre/42"}, "")
    web.pages["https://short.example.com/offre/42"] = html(job_posting_page())
    assert _import(client, auth_headers, "https://short.example.com/ok").status_code == 200

    for i in range(fetch.MAX_REDIRECTS + 1):
        web.pages[f"https://loop.example.com/{i}"] = (302, {"location": f"/{i + 1}"}, "")
    response = _import(client, auth_headers, "https://loop.example.com/0")
    assert response.json()["code"] == "job_offer.too_many_redirects"
    assert len([c for c in web.calls if "loop" in c]) == fetch.MAX_REDIRECTS + 1


def test_connection_checks_ip_again(monkeypatch):
    """DNS rebinding : l'hôte validé résout ensuite vers une IP interne au moment de la connexion."""
    monkeypatch.setattr(fetch, "_resolve", lambda host, port: ["169.254.169.254"])
    with pytest.raises(ApiError) as error:
        PublicOnlyBackend().connect_tcp("jobs.example.com", 443, timeout=1)
    assert error.value.code == "job_offer.forbidden_url"


def test_real_transport_uses_public_only_backend(monkeypatch):
    monkeypatch.setattr(fetch, "http_transport", None)
    monkeypatch.setattr(fetch, "_resolve", lambda host, port: ["127.0.0.1"])
    # validate_url passe (IP publique), puis la connexion réelle est refusée par le backend
    monkeypatch.setattr(fetch, "validate_url", lambda url: url)
    with pytest.raises(ApiError) as error:
        fetch.fetch_html("http://jobs.example.com/")
    assert error.value.code == "job_offer.forbidden_url"


# --- Réponses du site ------------------------------------------------------------------------


def test_timeout(client, auth_headers, web):
    web.fail = httpx.ReadTimeout("trop lent")
    response = _import(client, auth_headers, "https://slow.example.com/job")
    assert response.status_code == 504
    assert response.json()["code"] == "job_offer.timeout"


def test_network_error(client, auth_headers, web):
    web.fail = httpx.ConnectError("refusé")
    assert _import(client, auth_headers, "https://down.example.com/job").json()["code"] == "job_offer.unreachable"


def test_non_html_content(client, auth_headers, web):
    web.pages["https://jobs.example.com/offre.pdf"] = (200, {"content-type": "application/pdf"}, b"%PDF-1.4")
    response = _import(client, auth_headers, "https://jobs.example.com/offre.pdf")
    assert response.status_code == 415
    assert response.json()["code"] == "job_offer.not_html"


def test_response_too_large(client, auth_headers, web, monkeypatch):
    monkeypatch.setattr(fetch, "MAX_RESPONSE_BYTES", 1000)
    web.pages["https://jobs.example.com/big"] = html("x" * 2000)
    assert _import(client, auth_headers, "https://jobs.example.com/big").json()["code"] == "job_offer.too_large"
    web.pages["https://jobs.example.com/declared"] = html("x", **{"content-length": "999999"})
    assert _import(client, auth_headers, "https://jobs.example.com/declared").json()["code"] == "job_offer.too_large"


def test_not_found(client, auth_headers, web):
    response = _import(client, auth_headers, "https://jobs.example.com/removed")
    assert response.status_code == 404
    assert response.json()["code"] == "job_offer.not_found"


@pytest.mark.parametrize(
    "url",
    ["https://www.linkedin.com/jobs/view/123", "https://fr.indeed.com/viewjob?jk=abc", "https://www.glassdoor.fr/job"],
)
def test_known_blocking_sites(client, auth_headers, web, url):
    response = _import(client, auth_headers, url)
    assert response.status_code == 422
    assert response.json()["code"] == "job_offer.site_blocked"
    assert web.calls == []


@pytest.mark.parametrize("status", [403, 429, 999])
def test_site_refusing_robots(client, auth_headers, web, status):
    web.pages["https://protected.example.com/job"] = html("Access denied", status=status)
    assert _import(client, auth_headers, "https://protected.example.com/job").json()["code"] == "job_offer.site_blocked"


def test_redirect_to_blocking_site(client, auth_headers, web):
    web.pages["https://lnkd.example.com/abc"] = (302, {"location": "https://www.linkedin.com/jobs/view/1"}, "")
    assert _import(client, auth_headers, "https://lnkd.example.com/abc").json()["code"] == "job_offer.site_blocked"
    assert web.calls == ["https://lnkd.example.com/abc"]


def test_error_messages_are_translated(client, auth_headers, web):
    response = client.post(
        "/api/job-offers/import",
        headers={**auth_headers, "Accept-Language": "en"},
        json={"url": "https://www.linkedin.com/jobs/view/1"},
    )
    assert response.json()["detail"].startswith("This site blocks automatic import")


# --- Cache, authentification, nettoyage IA ------------------------------------------------------


def test_result_is_cached_by_url(client, auth_headers, web):
    web.pages["https://jobs.example.com/offre/42"] = html(job_posting_page())
    first = _import(client, auth_headers, "https://jobs.example.com/offre/42").json()
    second = _import(client, auth_headers, "https://jobs.example.com/offre/42#postuler").json()
    assert first["cached"] is False
    assert second["cached"] is True
    assert second["title"] == first["title"]
    assert len(web.calls) == 1


def test_requires_auth(client, web):
    assert client.post("/api/job-offers/import", json={"url": "https://jobs.example.com/"}).status_code in (401, 403)


def test_ai_cleanup_requires_verified_email(client, unverified_user, web):
    headers = {"Authorization": f"Bearer {unverified_user['token']}"}
    web.pages["https://careers.acme.test/data-analyst"] = html(ARTICLE_PAGE)
    # Import simple autorisé, nettoyage IA réservé aux comptes vérifiés
    assert _import(client, headers, "https://careers.acme.test/data-analyst").status_code == 200
    response = _import(client, headers, "https://careers.acme.test/data-analyst", ai_cleanup=True)
    assert response.status_code == 403
    assert response.json()["code"] == "auth.email_not_verified"


def test_ai_cleanup(client, auth_headers, web):
    web.pages["https://careers.acme.test/data-analyst"] = html(ARTICLE_PAGE)
    cleaned = {
        "title": "Data Analyst",
        "company": "ACME",
        "location": "Lyon",
        "text": "Missions : construire les tableaux de bord de pilotage. " * 6,
    }
    prompts = []
    llm = SimpleNamespace(generate_json=lambda prompt, temperature: prompts.append(prompt) or cleaned)
    with patch("app.routers.job_offers.ai_for_user", return_value=SimpleNamespace(llm=llm)):
        offer = _import(client, auth_headers, "https://careers.acme.test/data-analyst", ai_cleanup=True).json()
    assert offer["method"] == "ai"
    assert offer["company"] == "ACME"
    assert offer["source_url"] == "https://careers.acme.test/data-analyst"
    assert "Modéliser les données de ventes" in prompts[0]


def test_ai_cleanup_keeps_extraction_when_answer_is_empty(client, auth_headers, web):
    web.pages["https://careers.acme.test/data-analyst"] = html(ARTICLE_PAGE)
    llm = SimpleNamespace(generate_json=lambda prompt, temperature: {"text": ""})
    with patch("app.routers.job_offers.ai_for_user", return_value=SimpleNamespace(llm=llm)):
        offer = _import(client, auth_headers, "https://careers.acme.test/data-analyst", ai_cleanup=True).json()
    assert offer["method"] == "html"


# --- URL de l'offre dans l'historique ------------------------------------------------------------


@pytest.mark.parametrize(
    "value,expected",
    [
        ("https://jobs.example.com/offre/42?ref=talento", "https://jobs.example.com/offre/42?ref=talento"),
        ("http://jobs.example.com/a", "http://jobs.example.com/a"),
        ("javascript:alert(document.cookie)", None),
        ("data:text/html,<script>", None),
        ("  ", None),
        (None, None),
        ("https://" + "a" * 2050, None),
    ],
)
def test_safe_offer_url(value, expected):
    assert safe_offer_url(value) == expected


def test_comparison_history_keeps_offer_url(client, auth_headers, db_session, registered_user):
    with patch("app.services.comparison_service.ai_service.compare_offer_and_cv", return_value=FAKE_RESULT):
        with client.stream(
            "POST",
            "/api/compare-stream",
            headers={**auth_headers, "Accept": "text/event-stream"},
            json={"offer_text": "Offre", "cv_text": "CV", "offer_url": "https://jobs.example.com/offre/42"},
        ) as response:
            "".join(response.iter_text())

    db_session.expire_all()
    record = db_session.scalars(
        select(ComparisonRecord).where(ComparisonRecord.user_id == UUID(registered_user["user"]["id"]))
    ).one()
    assert record.offer_url == "https://jobs.example.com/offre/42"
    listing = client.get("/api/comparisons", headers=auth_headers).json()
    assert listing["items"][0]["offer_url"] == "https://jobs.example.com/offre/42"


# --- Contenu lu dans le navigateur (bookmarklet, copier-coller) ------------------------------------

INDEED_PAGE_TEXT = """Passer au contenu principal
Accueil  Avis sur les entreprises  Estimation de salaire
Développeur Full Stack H/F
Doctolib
Paris (75)
CDI
Description du poste
Rejoignez l'équipe produit pour construire les outils de prise de rendez-vous utilisés par des millions de patients.
Vous travaillerez en Ruby on Rails et React, avec un fort accent sur la qualité et les tests automatisés.
Profil recherché : 3 ans d'expérience, goût du produit, autonomie.
Signaler l'offre"""


def _parse(client, headers, **body):
    return client.post("/api/job-offers/parse", headers=headers, json=body)


def test_parse_json_ld_from_bookmarklet(client, auth_headers, web):
    posting = json.loads(job_posting_page().split('application/ld+json">')[1].split("</script>")[0])
    response = _parse(
        client,
        auth_headers,
        url="https://fr.indeed.com/viewjob?jk=abc123",
        title="Développeur Front-end - Paris - Indeed.com",
        json_ld=["{pas du json", json.dumps({"@type": "BreadcrumbList"}), json.dumps(posting)],
    )
    assert response.status_code == 200, response.text
    offer = response.json()
    assert offer["method"] == "json-ld"
    assert offer["company"] == "Talento & Co"
    assert offer["source_url"] == "https://fr.indeed.com/viewjob?jk=abc123"
    # Aucune requête vers le site (Indeed bloque les serveurs)
    assert web.calls == []


def test_parse_pasted_page_text(client, auth_headers, web):
    offer = _parse(
        client,
        auth_headers,
        url="https://www.linkedin.com/jobs/view/42",
        title="Développeur Full Stack H/F - Doctolib | LinkedIn",
        text=INDEED_PAGE_TEXT,
    ).json()
    # Libellé « Description du poste » repéré : seule la description est gardée ; titre de l'onglet
    assert offer["method"] == "page"
    assert offer["title"] == "Développeur Full Stack H/F - Doctolib"
    assert "Passer au contenu principal" not in offer["text"]
    assert "Ruby on Rails et React" in offer["text"]
    assert offer["source_url"] == "https://www.linkedin.com/jobs/view/42"
    assert web.calls == []


def test_parse_falls_back_to_text_when_json_ld_has_no_posting(client, auth_headers):
    offer = _parse(client, auth_headers, json_ld=[json.dumps({"@type": "Organization"})], text=INDEED_PAGE_TEXT).json()
    assert offer["method"] == "paste"
    assert offer["source_url"] is None


def test_parse_rejects_short_text_and_oversized_input(client, auth_headers):
    short = _parse(client, auth_headers, text="Développeur H/F")
    assert short.status_code == 422
    assert short.json()["code"] == "job_offer.paste_too_short"

    big = _parse(client, auth_headers, text="x" * 200_001)
    assert big.status_code == 413
    assert _parse(client, auth_headers, json_ld=["x" * 500_001]).status_code == 413


def test_parse_never_keeps_unsafe_source_url(client, auth_headers):
    offer = _parse(client, auth_headers, url="javascript:alert(1)", text=INDEED_PAGE_TEXT).json()
    assert offer["source_url"] is None


def test_parse_with_ai_cleanup(client, auth_headers, unverified_user):
    unverified = {"Authorization": f"Bearer {unverified_user['token']}"}
    assert _parse(client, unverified, text=INDEED_PAGE_TEXT, ai_cleanup=True).status_code == 403

    cleaned = {"title": "Développeur Full Stack", "company": "Doctolib", "location": "Paris", "text": "Missions : " * 30}
    llm = SimpleNamespace(generate_json=lambda prompt, temperature: cleaned)
    with patch("app.routers.job_offers.ai_for_user", return_value=SimpleNamespace(llm=llm)):
        offer = _parse(client, auth_headers, text=INDEED_PAGE_TEXT, ai_cleanup=True).json()
    assert offer["method"] == "ai"
    assert offer["company"] == "Doctolib"


def test_parse_requires_auth(client):
    assert client.post("/api/job-offers/parse", json={"text": INDEED_PAGE_TEXT}).status_code in (401, 403)


def test_welcome_to_the_jungle_goes_through_the_browser(client, auth_headers, web):
    url = "https://www.welcometothejungle.com/fr/companies/acme/jobs/dev_paris"
    assert _import(client, auth_headers, url).json()["code"] == "job_offer.site_blocked"
    assert web.calls == []


def _posting(title: str, company: str) -> dict:
    return {
        "@type": "JobPosting",
        "title": title,
        "hiringOrganization": {"name": company},
        "description": f"<p>{title} chez {company}. " + "Missions détaillées et profil recherché. " * 8 + "</p>",
    }


def test_parse_prefers_fields_of_displayed_offer(client, auth_headers):
    """Page de recherche Indeed : le JSON-LD décrit la liste, les champs décrivent l'offre ouverte."""
    listing = {"@type": "ItemList", "itemListElement": [_posting("Autre offre", "Autre employeur")]}
    offer = _parse(
        client,
        auth_headers,
        url="https://fr.indeed.com/viewjob?jk=1a2b3c4d5e6f7a8b",
        title="Emplois : développeur - Paris | Indeed",
        json_ld=[json.dumps(listing)],
        fields={
            "title": "Développeur Full Stack H/F",
            "company": "Doctolib",
            "location": "Paris (75)",
            "description": INDEED_PAGE_TEXT,
        },
    ).json()
    assert offer["method"] == "page"
    assert (offer["title"], offer["company"], offer["location"]) == ("Développeur Full Stack H/F", "Doctolib", "Paris (75)")
    assert "Autre employeur" not in offer["text"]


def test_parse_ignores_incomplete_fields(client, auth_headers):
    """Sélecteurs périmés (description vide) : repli sur le JSON-LD de l'offre affichée."""
    posting = _posting("Data Engineer", "Qonto")
    offer = _parse(
        client,
        auth_headers,
        json_ld=[json.dumps(posting)],
        fields={"title": "Data Engineer", "company": "", "location": "", "description": ""},
    ).json()
    assert offer["method"] == "json-ld"
    assert offer["company"] == "Qonto"


def test_several_postings_pick_the_displayed_one(client, auth_headers):
    blocks = [json.dumps({"@graph": [_posting("Autre offre", "Autre employeur"), _posting("Data Engineer", "Qonto")]})]
    offer = _parse(client, auth_headers, title="Data Engineer - Qonto | LinkedIn", json_ld=blocks, text=INDEED_PAGE_TEXT).json()
    assert offer["company"] == "Qonto"


def test_several_postings_without_match_are_not_trusted(client, auth_headers):
    """Plusieurs offres sans correspondance : jamais la première par défaut (mauvais employeur)."""
    blocks = [json.dumps([_posting("Offre A", "Employeur A"), _posting("Offre B", "Employeur B")])]
    offer = _parse(client, auth_headers, title="Titre sans rapport", json_ld=blocks, text=INDEED_PAGE_TEXT).json()
    assert offer["method"] == "paste"
    assert "Employeur A" not in offer["text"]


def test_server_import_uses_h1_to_pick_posting(client, auth_headers, web):
    blocks = json.dumps([_posting("Offre similaire", "Autre employeur"), _posting("Développeur Vue.js", "Talento")])
    page = f'<html><head><script type="application/ld+json">{blocks}</script></head><body><h1>Développeur Vue.js</h1></body></html>'
    web.pages["https://jobs.example.com/vue"] = html(page)
    assert _import(client, auth_headers, "https://jobs.example.com/vue").json()["company"] == "Talento"


# --- Indeed : texte visible de la page (exemple réel, page d'accueil « Emplois recommandés ») ------

INDEED_HOME = (Path(__file__).parent / "fixtures" / "indeed_accueil_fr.txt").read_text(encoding="utf-8")


def _assert_iscod_offer(offer):
    assert offer["method"] == "page"
    assert offer["title"] == "Alternance Développeur Fullstack .NET & Angular (F/H)"
    assert offer["company"] == "ISCOD"
    assert offer["location"] == "51100 Reims"
    assert offer["text"].startswith("Description :")
    assert "Piloter l’architecture technique" in offer["text"]
    assert offer["text"].endswith("Poste à pourvoir dès que possible !")
    # Ni la liste des offres recommandées, ni l'en-tête, ni le pied de page d'Indeed
    for noise in ("Capfinances", "Verisure", "Bienvenue", "Avis sur les entreprises", "Signaler l'offre", "© 2026 Indeed"):
        assert noise not in offer["text"]


def test_indeed_bookmarklet_page_text(client, auth_headers, web):
    """Bouton sur la page d'accueil Indeed : aucun sélecteur reconnu, texte de toute la page envoyé."""
    offer = _parse(
        client,
        auth_headers,
        url="https://fr.indeed.com/viewjob?jk=0011aabbccddeeff",
        title="Emplois, Travail | Indeed.com",
        text=INDEED_HOME,
        fields=None,
    ).json()
    _assert_iscod_offer(offer)
    assert offer["source_url"] == "https://fr.indeed.com/viewjob?jk=0011aabbccddeeff"
    assert web.calls == []


def test_indeed_copy_paste_of_whole_page(client, auth_headers):
    """Copier-coller guidé (Ctrl+A, Ctrl+C) de la même page."""
    _assert_iscod_offer(_parse(client, auth_headers, url="https://fr.indeed.com/?vjk=0011aabbccddeeff", text=INDEED_HOME).json())


def test_indeed_text_beats_unrelated_json_ld(client, auth_headers):
    other = json.dumps(_posting("Commercial terrain", "Verisure SAS"))
    offer = _parse(client, auth_headers, url="https://fr.indeed.com/viewjob?jk=1", json_ld=[other], text=INDEED_HOME).json()
    assert offer["company"] == "ISCOD"


def test_indeed_english_labels(client, auth_headers):
    page = "\n".join(
        [
            "Recommended jobs", "Other job", "Other company", "Show more jobs",
            "Senior Data Engineer", "Acme Corp", "·", "4.1", "London", "Full-time", "Apply now",
            "Job details", "£70,000 - £80,000 a year", "Full job description",
            "We are looking for a senior data engineer to build our streaming platform. " * 4,
            "Report job", "Hiring Lab",
        ]
    )
    offer = _parse(client, auth_headers, url="https://uk.indeed.com/viewjob?jk=2", text=page).json()
    assert (offer["title"], offer["company"], offer["location"]) == ("Senior Data Engineer", "Acme Corp", "London")
    assert "Report job" not in offer["text"]

"""Récupération d'une page web fournie par l'utilisateur, protégée contre le SSRF.

Le serveur télécharge une URL arbitraire : sans contrôle, un utilisateur pourrait viser le réseau
interne (métadonnées cloud 169.254.169.254, Redis, PostgreSQL…). Règles :
- http(s) uniquement, ports 80/443, pas d'identifiants dans l'URL ;
- l'hôte doit résoudre uniquement vers des IP publiques. Le contrôle est refait **à la connexion**
  (backend réseau httpcore) : un DNS qui change entre la vérification et la connexion (rebinding)
  ne peut pas contourner la règle ;
- redirections suivies à la main (chacune revalidée), au plus MAX_REDIRECTS ;
- délai, taille maximale (après décompression) et Content-Type HTML imposés ;
- aucun proxy de l'environnement (il contournerait les contrôles).
"""

from __future__ import annotations

import ipaddress
import socket
from collections.abc import Callable
from dataclasses import dataclass
from urllib.parse import urljoin, urlsplit

import httpcore
import httpx

from app.i18n import ApiError

MAX_URL_LENGTH = 2048
MAX_REDIRECTS = 5
MAX_RESPONSE_BYTES = 3 * 1024 * 1024
TIMEOUT = httpx.Timeout(10.0, connect=5.0)
ALLOWED_PORTS = (80, 443)
HTML_CONTENT_TYPES = ("text/html", "application/xhtml+xml")
JSON_CONTENT_TYPES = ("application/json",)
BLOCKED_SUFFIXES = (".localhost", ".local", ".internal", ".lan", ".home.arpa", ".onion")
USER_AGENT = "Mozilla/5.0 (compatible; TalentoBot/1.0; +https://cv-compare.up.railway.app)"
# Codes renvoyés par les sites qui refusent les robots (999 : LinkedIn)
BLOCKING_STATUSES = (401, 403, 429, 451, 999)

# Transport HTTP injectable (tests : httpx.MockTransport)
http_transport: httpx.BaseTransport | None = None


@dataclass
class FetchedPage:
    url: str
    html: str  # corps décodé (HTML, ou JSON pour fetch_json)


def _resolve(host: str, port: int) -> list[str]:
    return list({info[4][0] for info in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)})


def _is_public(address: str) -> bool:
    ip = ipaddress.ip_address(address.split("%")[0])
    # IPv4 encapsulée (::ffff:127.0.0.1) : contrôle sur l'adresse IPv4
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped
    return ip.is_global and not ip.is_multicast


def public_addresses(host: str, port: int) -> list[str]:
    """IP publiques de l'hôte ; lève job_offer.forbidden_url si une seule IP est interne."""
    literal = host.strip("[]")
    try:
        ipaddress.ip_address(literal.split("%")[0])
    except ValueError:
        pass
    else:
        # Adresse IP saisie directement : contrôlée telle quelle, sans résolution DNS
        if not _is_public(literal):
            raise ApiError(400, "job_offer.forbidden_url")
        return [literal]
    try:
        addresses = _resolve(host, port)
    except OSError as exc:
        raise ApiError(400, "job_offer.unreachable") from exc
    if not addresses or not all(_is_public(address) for address in addresses):
        raise ApiError(400, "job_offer.forbidden_url")
    return addresses


def validate_url(url: str) -> str:
    """URL normalisée (sans fragment) ou ApiError ; vérifie aussi la résolution DNS."""
    url = (url or "").strip()
    if not url or len(url) > MAX_URL_LENGTH:
        raise ApiError(400, "job_offer.invalid_url")
    try:
        parts = urlsplit(url)
        host = (parts.hostname or "").lower().rstrip(".")
        port = parts.port or (443 if parts.scheme == "https" else 80)
    except ValueError as exc:
        raise ApiError(400, "job_offer.invalid_url") from exc
    if parts.scheme not in ("http", "https") or not host:
        raise ApiError(400, "job_offer.invalid_url")
    if parts.username or parts.password or port not in ALLOWED_PORTS:
        raise ApiError(400, "job_offer.forbidden_url")
    if host == "localhost" or host.endswith(BLOCKED_SUFFIXES):
        raise ApiError(400, "job_offer.forbidden_url")
    public_addresses(host, port)
    return parts._replace(fragment="").geturl()


class PublicOnlyBackend(httpcore.SyncBackend):
    """Backend réseau : se connecte uniquement à une IP publique vérifiée juste avant la connexion.

    TLS (SNI, certificat) reste vérifié sur le nom d'hôte : httpcore le prend dans l'URL, pas
    dans l'adresse de connexion.
    """

    def connect_tcp(self, host, port, timeout=None, local_address=None, socket_options=None):
        address = public_addresses(host, port)[0]
        return super().connect_tcp(
            address, port, timeout=timeout, local_address=local_address, socket_options=socket_options
        )


def _transport() -> httpx.BaseTransport:
    if http_transport is not None:
        return http_transport
    transport = httpx.HTTPTransport(retries=0)
    # Pas d'option publique pour le backend réseau : on remplace celui du pool de connexions
    transport._pool._network_backend = PublicOnlyBackend()  # noqa: SLF001
    return transport


def fetch_html(url: str, is_blocked: Callable[[str], bool] | None = None) -> FetchedPage:
    """Télécharge une page HTML publique. Erreurs traduites (ApiError job_offer.*).

    `is_blocked` : sites refusés d'office, vérifié avant chaque requête (redirections comprises).
    """
    return _fetch(url, HTML_CONTENT_TYPES, "text/html,application/xhtml+xml;q=0.9,*/*;q=0.1", is_blocked)


def fetch_json(url: str) -> FetchedPage:
    """API publique d'un ATS (mêmes protections que fetch_html)."""
    return _fetch(url, JSON_CONTENT_TYPES, "application/json", None)


def _fetch(
    url: str,
    content_types: tuple[str, ...],
    accept: str,
    is_blocked: Callable[[str], bool] | None,
) -> FetchedPage:

    def checked(target: str) -> str:
        target = validate_url(target)
        if is_blocked and is_blocked(target):
            raise ApiError(422, "job_offer.site_blocked")
        return target

    current = checked(url)
    headers = {"User-Agent": USER_AGENT, "Accept": accept}
    with httpx.Client(transport=_transport(), timeout=TIMEOUT, trust_env=False, follow_redirects=False) as client:
        for _ in range(MAX_REDIRECTS + 1):
            try:
                with client.stream("GET", current, headers=headers) as response:
                    if response.is_redirect:
                        location = response.headers.get("location")
                        if not location:
                            raise ApiError(502, "job_offer.unreachable")
                        current = checked(urljoin(current, location))
                        continue
                    return FetchedPage(url=current, html=_read_body(response, content_types))
            except httpx.TimeoutException as exc:
                raise ApiError(504, "job_offer.timeout") from exc
            except httpx.TransportError as exc:
                raise ApiError(502, "job_offer.unreachable") from exc
    raise ApiError(502, "job_offer.too_many_redirects")


def _read_body(response: httpx.Response, content_types: tuple[str, ...]) -> str:
    if response.status_code in BLOCKING_STATUSES:
        raise ApiError(422, "job_offer.site_blocked")
    if response.status_code == 404 or response.status_code == 410:
        raise ApiError(404, "job_offer.not_found")
    if response.status_code >= 400:
        raise ApiError(502, "job_offer.unreachable")

    content_type = response.headers.get("content-type", "").split(";")[0].strip().lower()
    if content_type not in content_types:
        raise ApiError(415, "job_offer.not_html")
    declared = response.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > MAX_RESPONSE_BYTES:
        raise ApiError(413, "job_offer.too_large")

    body = bytearray()
    for chunk in response.iter_bytes():
        body.extend(chunk)
        if len(body) > MAX_RESPONSE_BYTES:
            raise ApiError(413, "job_offer.too_large")
    return _decode(bytes(body), response.charset_encoding)


def _decode(body: bytes, charset: str | None) -> str:
    """Charset annoncé par le serveur, sinon UTF-8, sinon Windows-1252 (vieux sites carrières)."""
    if charset:
        try:
            return body.decode(charset, errors="replace")
        except LookupError:
            pass
    try:
        return body.decode("utf-8")
    except UnicodeDecodeError:
        return body.decode("cp1252", errors="replace")

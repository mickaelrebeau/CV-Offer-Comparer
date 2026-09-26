from dataclasses import dataclass
from html import escape

import httpx

from app.config import settings
from app.i18n import DEFAULT_LOCALE

RESEND_API_URL = "https://api.resend.com/emails"


@dataclass
class Email:
    to: str
    subject: str
    text: str
    html: str


def send_email(email: Email) -> None:
    """Envoie un e-mail via le provider configuré. Ne lève jamais : un échec est journalisé."""
    provider = settings.EMAIL_PROVIDER.lower()
    try:
        if provider == "resend":
            _send_resend(email)
        else:
            if settings.ENVIRONMENT.lower() == "production":
                print("[Email] ⚠️ EMAIL_PROVIDER=console en production : aucun e-mail envoyé")
            print(f"[Email] À: {email.to} | {email.subject}\n{email.text}")
    except Exception as e:
        print(f"[Email] Échec d'envoi à {email.to} ({provider}): {e!r}")


def _send_resend(email: Email) -> None:
    if not settings.RESEND_API_KEY:
        raise RuntimeError("RESEND_API_KEY manquant")
    response = httpx.post(
        RESEND_API_URL,
        headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
        json={
            "from": settings.EMAIL_FROM,
            "to": [email.to],
            "subject": email.subject,
            "text": email.text,
            "html": email.html,
        },
        timeout=10,
    )
    response.raise_for_status()


def _action_email(to: str, subject: str, intro: str, cta: str, url: str, outro: str, copy_link: str) -> Email:
    text = f"{intro}\n\n{cta}\n{url}\n\n{outro}\n\n— Talento"
    html = f"""<div style="font-family:system-ui,sans-serif;max-width:480px;margin:auto;color:#111">
  <p>{escape(intro)}</p>
  <p><a href="{escape(url)}" style="display:inline-block;padding:12px 20px;background:#111;color:#fff;
     text-decoration:none;border-radius:8px">{escape(cta)}</a></p>
  <p style="font-size:13px;color:#555">{escape(copy_link)} {escape(url)}</p>
  <p style="font-size:13px;color:#555">{escape(outro)}</p>
  <p>— Talento</p>
</div>"""
    return Email(to=to, subject=subject, text=text, html=html)


COPY_LINK = {"fr": "Ou copiez ce lien :", "en": "Or copy this link:"}

EMAIL_TEXTS = {
    "verification": {
        "fr": {
            "subject": "Confirmez votre adresse e-mail — Talento",
            "intro": "Bienvenue sur Talento ! Confirmez votre adresse e-mail pour lancer vos analyses.",
            "cta": "Confirmer mon adresse",
            "outro": "Ce lien expire dans {hours} h. Si vous n'avez pas créé de compte, ignorez cet e-mail.",
        },
        "en": {
            "subject": "Confirm your email address — Talento",
            "intro": "Welcome to Talento! Confirm your email address to start your analyses.",
            "cta": "Confirm my address",
            "outro": "This link expires in {hours} h. If you did not create an account, ignore this email.",
        },
    },
    "password_reset": {
        "fr": {
            "subject": "Réinitialisation de votre mot de passe — Talento",
            "intro": "Vous avez demandé à réinitialiser votre mot de passe Talento.",
            "cta": "Choisir un nouveau mot de passe",
            "outro": "Ce lien expire dans {minutes} min et ne fonctionne qu'une fois. "
            "Si vous n'êtes pas à l'origine de cette demande, ignorez cet e-mail.",
        },
        "en": {
            "subject": "Reset your password — Talento",
            "intro": "You asked to reset your Talento password.",
            "cta": "Choose a new password",
            "outro": "This link expires in {minutes} min and works only once. "
            "If you did not make this request, ignore this email.",
        },
    },
}


def _localized_email(kind: str, to: str, url: str, locale: str, **params) -> Email:
    texts = EMAIL_TEXTS[kind].get(locale, EMAIL_TEXTS[kind][DEFAULT_LOCALE])
    copy_link = COPY_LINK.get(locale, COPY_LINK[DEFAULT_LOCALE])
    outro = texts["outro"].format(**params)
    return _action_email(to, texts["subject"], texts["intro"], texts["cta"], url, outro, copy_link)


def verification_email(to: str, url: str, locale: str = DEFAULT_LOCALE) -> Email:
    return _localized_email("verification", to, url, locale, hours=settings.EMAIL_VERIFICATION_TTL_HOURS)


def password_reset_email(to: str, url: str, locale: str = DEFAULT_LOCALE) -> Email:
    return _localized_email("password_reset", to, url, locale, minutes=settings.PASSWORD_RESET_TTL_MINUTES)

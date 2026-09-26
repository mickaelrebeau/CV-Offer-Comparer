from dataclasses import dataclass
from html import escape

import httpx

from app.config import settings

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


def _action_email(to: str, subject: str, intro: str, cta: str, url: str, outro: str) -> Email:
    text = f"{intro}\n\n{cta} : {url}\n\n{outro}\n\n— Talento"
    html = f"""<div style="font-family:system-ui,sans-serif;max-width:480px;margin:auto;color:#111">
  <p>{escape(intro)}</p>
  <p><a href="{escape(url)}" style="display:inline-block;padding:12px 20px;background:#111;color:#fff;
     text-decoration:none;border-radius:8px">{escape(cta)}</a></p>
  <p style="font-size:13px;color:#555">Ou copiez ce lien : {escape(url)}</p>
  <p style="font-size:13px;color:#555">{escape(outro)}</p>
  <p>— Talento</p>
</div>"""
    return Email(to=to, subject=subject, text=text, html=html)


def verification_email(to: str, url: str) -> Email:
    hours = settings.EMAIL_VERIFICATION_TTL_HOURS
    return _action_email(
        to,
        "Confirmez votre adresse e-mail — Talento",
        "Bienvenue sur Talento ! Confirmez votre adresse e-mail pour lancer vos analyses.",
        "Confirmer mon adresse",
        url,
        f"Ce lien expire dans {hours} h. Si vous n'avez pas créé de compte, ignorez cet e-mail.",
    )


def password_reset_email(to: str, url: str) -> Email:
    minutes = settings.PASSWORD_RESET_TTL_MINUTES
    return _action_email(
        to,
        "Réinitialisation de votre mot de passe — Talento",
        "Vous avez demandé à réinitialiser votre mot de passe Talento.",
        "Choisir un nouveau mot de passe",
        url,
        f"Ce lien expire dans {minutes} min et ne fonctionne qu'une fois. "
        "Si vous n'êtes pas à l'origine de cette demande, ignorez cet e-mail.",
    )

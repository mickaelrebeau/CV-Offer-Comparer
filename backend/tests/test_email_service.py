import httpx

from app.config import settings
from app.services import email_service
from app.services.email_service import password_reset_email, send_email


def test_resend_provider_posts_email(monkeypatch):
    calls = []

    def fake_post(url, **kwargs):
        calls.append((url, kwargs))
        return httpx.Response(200, request=httpx.Request("POST", url))

    monkeypatch.setattr(settings, "EMAIL_PROVIDER", "resend")
    monkeypatch.setattr(settings, "RESEND_API_KEY", "re_test")
    monkeypatch.setattr(settings, "EMAIL_FROM", "Talento <no-reply@example.com>")
    monkeypatch.setattr(email_service.httpx, "post", fake_post)

    send_email(password_reset_email("user@example.com", "https://front/reset-password?token=abc"))

    url, kwargs = calls[0]
    assert url == email_service.RESEND_API_URL
    assert kwargs["headers"]["Authorization"] == "Bearer re_test"
    assert kwargs["json"]["to"] == ["user@example.com"]
    assert kwargs["json"]["from"] == "Talento <no-reply@example.com>"
    assert "token=abc" in kwargs["json"]["html"]


def test_send_email_never_raises(monkeypatch, capsys):
    def failing_post(url, **kwargs):
        raise httpx.ConnectError("down")

    monkeypatch.setattr(settings, "EMAIL_PROVIDER", "resend")
    monkeypatch.setattr(settings, "RESEND_API_KEY", "re_test")
    monkeypatch.setattr(email_service.httpx, "post", failing_post)

    send_email(password_reset_email("user@example.com", "https://front/x"))
    assert "Échec d'envoi" in capsys.readouterr().out


def test_console_provider_prints_link(monkeypatch, capsys):
    monkeypatch.setattr(settings, "EMAIL_PROVIDER", "console")
    send_email(password_reset_email("user@example.com", "https://front/reset-password?token=abc"))
    assert "token=abc" in capsys.readouterr().out

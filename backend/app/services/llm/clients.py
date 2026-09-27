"""Clients LLM derrière une interface commune : `generate_json(prompt, temperature)`.

- GeminiClient : SDK google-genai (plateforme, ou clé Gemini de l'utilisateur)
- AnthropicClient : SDK anthropic
- OpenAICompatibleClient : API REST chat completions (OpenAI, DeepSeek, Qwen, Kimi, endpoint libre)

Les erreurs sont converties en LLMError (codes stables). La clé n'est jamais journalisée :
les logs ne contiennent que le provider, le statut HTTP et le code normalisé.
"""

from __future__ import annotations

import json
from typing import Any

import anthropic
import httpx
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from app.config import settings
from app.services.llm.errors import PLATFORM, USER, LLMError, classify
from app.services.llm.urls import validate_base_url

# Transport HTTP injectable (tests : httpx.MockTransport)
http_transport: httpx.BaseTransport | None = None


def parse_json(text: str) -> Any:
    """JSON de la réponse, y compris enveloppé dans du texte ou un bloc ```json."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start_obj, end_obj = text.find("{"), text.rfind("}")
        start_arr, end_arr = text.find("["), text.rfind("]")
        if start_obj != -1 and end_obj > start_obj and (start_arr == -1 or start_obj < start_arr):
            return json.loads(text[start_obj : end_obj + 1])
        if start_arr != -1 and end_arr > start_arr:
            return json.loads(text[start_arr : end_arr + 1])
        raise


def _log_failure(provider: str, owner: str, status: int | None, error: LLMError) -> None:
    print(f"[LLM] échec {provider} ({owner}) statut={status or 'réseau'} -> {error.code}")


class LLMClient:
    provider = "unknown"

    def __init__(self, *, model: str, owner: str) -> None:
        self.model = model
        self.owner = owner

    def generate_json(self, prompt: str, *, temperature: float = 0.2) -> Any:
        text = self._generate_text(prompt, temperature=temperature).strip()
        if not text:
            raise RuntimeError(f"Réponse {self.provider} vide")
        return parse_json(text)

    def _generate_text(self, prompt: str, *, temperature: float) -> str:  # pragma: no cover
        raise NotImplementedError

    def _fail(self, status: int | None, message: str = "") -> LLMError:
        error = classify(status, self.owner, message)
        _log_failure(self.provider, self.owner, status, error)
        return error


class GeminiClient(LLMClient):
    provider = "gemini"

    def __init__(self, *, api_key: str, model: str, owner: str) -> None:
        super().__init__(model=model, owner=owner)
        self._api_key = api_key
        self._client: genai.Client | None = None

    def _sdk(self) -> genai.Client:
        if self._client is None:
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    def _generate_text(self, prompt: str, *, temperature: float) -> str:
        try:
            response = self._sdk().models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    response_mime_type="application/json",
                ),
            )
        except genai_errors.APIError as exc:
            raise self._fail(exc.code, f"{exc.status} {exc.message}") from exc
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            raise self._fail(None) from exc
        return response.text or ""


class AnthropicClient(LLMClient):
    provider = "anthropic"

    def __init__(self, *, api_key: str, model: str, base_url: str | None, custom_base_url: bool) -> None:
        super().__init__(model=model, owner=USER)
        self._api_key = api_key
        self._base_url = base_url
        self._custom_base_url = custom_base_url

    def _sdk(self) -> anthropic.Anthropic:
        base_url = validate_base_url(self._base_url) if self._custom_base_url else self._base_url
        return anthropic.Anthropic(
            api_key=self._api_key,
            base_url=base_url,
            timeout=settings.LLM_REQUEST_TIMEOUT_SECONDS,
            max_retries=1,
        )

    def _generate_text(self, prompt: str, *, temperature: float) -> str:
        # Pas de temperature : refusée par les modèles Claude récents
        try:
            message = self._sdk().messages.create(
                model=self.model,
                max_tokens=16000,
                messages=[{"role": "user", "content": prompt}],
            )
        except anthropic.APIStatusError as exc:
            raise self._fail(exc.status_code, str(getattr(exc, "message", ""))) from exc
        except anthropic.APIConnectionError as exc:  # inclut les timeouts
            raise self._fail(None) from exc

        if message.stop_reason == "refusal":
            _log_failure(self.provider, self.owner, 200, LLMError("llm.provider_refused"))
            raise LLMError("llm.provider_refused")
        # Seuls les blocs texte portent la réponse (les blocs thinking sont ignorés)
        return "".join(block.text for block in message.content if block.type == "text")


class OpenAICompatibleClient(LLMClient):
    """POST {base_url}/chat/completions, format OpenAI."""

    def __init__(
        self,
        *,
        provider: str,
        api_key: str,
        model: str,
        base_url: str,
        custom_base_url: bool,
        json_mode: bool,
    ) -> None:
        super().__init__(model=model, owner=USER)
        self.provider = provider
        self._api_key = api_key
        self._base_url = base_url
        self._custom_base_url = custom_base_url
        self._json_mode = json_mode

    def _post(self, payload: dict[str, Any]) -> httpx.Response:
        base_url = validate_base_url(self._base_url) if self._custom_base_url else self._base_url
        with httpx.Client(
            timeout=settings.LLM_REQUEST_TIMEOUT_SECONDS,
            follow_redirects=False,  # pas de redirection vers une cible non validée
            transport=http_transport,
        ) as client:
            return client.post(
                f"{base_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json=payload,
            )

    def _generate_text(self, prompt: str, *, temperature: float) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        if self._json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            response = self._post(payload)
            # Certains modèles refusent temperature (raisonnement) ou response_format :
            # une seconde tentative sans le paramètre incriminé
            if response.status_code == 400:
                body = response.text.lower()
                dropped = [key for key in ("temperature", "response_format") if key in payload and key in body]
                if dropped:
                    response = self._post({k: v for k, v in payload.items() if k not in dropped})
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            raise self._fail(None) from exc

        if response.status_code >= 400:
            raise self._fail(response.status_code, _error_message(response))

        try:
            return response.json()["choices"][0]["message"]["content"] or ""
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise self._fail(502) from exc


def _error_message(response: httpx.Response) -> str:
    try:
        error = response.json().get("error")
    except ValueError:
        return ""
    if isinstance(error, dict):
        return f"{error.get('code') or ''} {error.get('type') or ''} {error.get('message') or ''}"
    return str(error or "")


def platform_client() -> GeminiClient:
    return GeminiClient(api_key=settings.GOOGLE_API_KEY, model=settings.GEMINI_MODEL, owner=PLATFORM)

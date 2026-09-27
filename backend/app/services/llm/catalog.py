"""Providers LLM supportés en BYOK.

`kind` choisit le client : SDK Gemini, SDK Anthropic, ou API REST OpenAI (chat completions)
pour OpenAI et tous les providers compatibles (DeepSeek, Qwen, Kimi, endpoint libre).
Les modèles sont des suggestions : l'utilisateur peut saisir n'importe quel identifiant.
"""

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class Provider:
    id: str
    label: str
    kind: str  # gemini | anthropic | openai
    default_model: str
    models: list[str] = field(default_factory=list)
    default_base_url: str | None = None
    # base_url libre : obligatoire pour openai_compatible, optionnelle (proxy) sinon
    base_url_required: bool = False
    base_url_editable: bool = True
    # response_format {"type": "json_object"} supporté
    json_mode: bool = True
    key_console_url: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


PROVIDERS: dict[str, Provider] = {
    p.id: p
    for p in (
        Provider(
            id="gemini",
            label="Google Gemini",
            kind="gemini",
            default_model="gemini-flash-latest",
            models=["gemini-flash-latest", "gemini-2.5-flash", "gemini-2.5-pro"],
            base_url_editable=False,
            key_console_url="https://aistudio.google.com/apikey",
        ),
        Provider(
            id="openai",
            label="OpenAI",
            kind="openai",
            default_model="gpt-4.1-mini",
            models=["gpt-4.1-mini", "gpt-4.1", "gpt-4o-mini", "gpt-5-mini"],
            default_base_url="https://api.openai.com/v1",
            key_console_url="https://platform.openai.com/api-keys",
        ),
        Provider(
            id="anthropic",
            label="Anthropic (Claude)",
            kind="anthropic",
            default_model="claude-opus-5",
            models=["claude-opus-5", "claude-sonnet-5", "claude-haiku-4-5"],
            default_base_url="https://api.anthropic.com",
            key_console_url="https://platform.claude.com/settings/keys",
        ),
        Provider(
            id="deepseek",
            label="DeepSeek",
            kind="openai",
            default_model="deepseek-chat",
            models=["deepseek-chat", "deepseek-reasoner"],
            default_base_url="https://api.deepseek.com/v1",
            key_console_url="https://platform.deepseek.com/api_keys",
        ),
        Provider(
            id="qwen",
            label="Qwen (Alibaba Cloud DashScope)",
            kind="openai",
            default_model="qwen-plus",
            models=["qwen-plus", "qwen-max", "qwen-turbo"],
            default_base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
            key_console_url="https://www.alibabacloud.com/help/en/model-studio/get-api-key",
        ),
        Provider(
            id="kimi",
            label="Kimi (Moonshot AI)",
            kind="openai",
            default_model="kimi-latest",
            models=["kimi-latest", "kimi-k2-turbo-preview", "moonshot-v1-32k"],
            default_base_url="https://api.moonshot.ai/v1",
            key_console_url="https://platform.moonshot.ai/console/api-keys",
        ),
        Provider(
            id="openai_compatible",
            label="Endpoint compatible OpenAI",
            kind="openai",
            default_model="",
            base_url_required=True,
            # Tous les serveurs compatibles ne gèrent pas response_format : JSON demandé par le prompt
            json_mode=False,
        ),
    )
}


def get_provider(provider_id: str) -> Provider | None:
    return PROVIDERS.get(provider_id)

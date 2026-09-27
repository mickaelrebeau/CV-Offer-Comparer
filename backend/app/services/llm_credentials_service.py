"""Configurations LLM personnelles (BYOK) : résolution du provider actif et gestion des clés."""

from __future__ import annotations

import re
import uuid

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.i18n import ApiError
from app.models.llm_credential import UserLLMCredential
from app.models.user import User
from app.services.ai_service import AIService, ai_service
from app.services.llm import crypto
from app.services.llm.catalog import Provider, get_provider
from app.services.llm.clients import AnthropicClient, GeminiClient, LLMClient, OpenAICompatibleClient
from app.services.llm.errors import USER
from app.services.llm.urls import validate_base_url

MAX_API_KEY_LENGTH = 512
MODEL_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,127}$")
VERIFY_PROMPT = 'Réponds uniquement avec ce JSON : {"ok": true}'


def build_client(provider: Provider, *, api_key: str, model: str, base_url: str | None) -> LLMClient:
    """Client LLM de l'utilisateur. `base_url` : URL personnalisée (revalidée à chaque appel)."""
    custom = bool(base_url)
    if provider.kind == "gemini":
        return GeminiClient(api_key=api_key, model=model, owner=USER)
    if provider.kind == "anthropic":
        return AnthropicClient(
            api_key=api_key,
            model=model,
            base_url=base_url or provider.default_base_url,
            custom_base_url=custom,
        )
    return OpenAICompatibleClient(
        provider=provider.id,
        api_key=api_key,
        model=model,
        base_url=base_url or provider.default_base_url or "",
        custom_base_url=custom,
        json_mode=provider.json_mode,
    )


def active_credential(db: Session, user: User) -> UserLLMCredential | None:
    return db.scalar(
        select(UserLLMCredential).where(
            UserLLMCredential.user_id == user.id, UserLLMCredential.is_active.is_(True)
        )
    )


def ai_for_user(db: Session, user: User) -> AIService:
    """Service IA de l'utilisateur : son provider actif (BYOK), sinon la stack plateforme."""
    credential = active_credential(db, user)
    provider = get_provider(credential.provider) if credential else None
    if credential is None or provider is None:
        return ai_service
    if not crypto.byok_enabled():
        # Chiffrement désactivé côté serveur : la clé est inutilisable, repli sur la plateforme
        print("[LLM] BYOK désactivé (LLM_ENCRYPTION_KEYS vide) : repli sur la plateforme")
        return ai_service
    api_key = crypto.decrypt(credential.encrypted_api_key)
    return AIService(build_client(provider, api_key=api_key, model=credential.model, base_url=credential.base_url))


# --- Gestion des credentials ---------------------------------------------------


def list_credentials(db: Session, user: User) -> list[UserLLMCredential]:
    return list(
        db.scalars(
            select(UserLLMCredential)
            .where(UserLLMCredential.user_id == user.id)
            .order_by(UserLLMCredential.created_at)
        )
    )


def get_credential(db: Session, user: User, credential_id: uuid.UUID) -> UserLLMCredential:
    credential = db.get(UserLLMCredential, credential_id)
    if not credential or credential.user_id != user.id:
        raise ApiError(404, "llm.credential_not_found")
    return credential


def _deactivate_all(db: Session, user: User) -> None:
    db.execute(
        update(UserLLMCredential)
        .where(UserLLMCredential.user_id == user.id, UserLLMCredential.is_active.is_(True))
        .values(is_active=False)
    )
    # Avant toute activation : l'index unique partiel n'admet qu'une ligne active
    db.flush()


def activate(db: Session, user: User, credential: UserLLMCredential) -> UserLLMCredential:
    _deactivate_all(db, user)
    credential.is_active = True
    db.commit()
    db.refresh(credential)
    return credential


def deactivate_all(db: Session, user: User) -> None:
    _deactivate_all(db, user)
    db.commit()


def delete(db: Session, user: User, credential: UserLLMCredential) -> None:
    # Suppression physique : le chiffré disparaît de la base
    db.delete(credential)
    db.commit()


def upsert(
    db: Session,
    user: User,
    *,
    provider_id: str,
    api_key: str | None,
    model: str,
    base_url: str | None,
    activate_now: bool,
    verify: bool,
) -> UserLLMCredential:
    """Crée ou remplace la configuration d'un provider. `api_key` vide = conserver la clé existante."""
    if not crypto.byok_enabled():
        raise ApiError(503, "llm.byok_disabled")
    provider = get_provider(provider_id)
    if provider is None:
        raise ApiError(400, "llm.unsupported_provider")

    model = (model or "").strip() or provider.default_model
    if not MODEL_PATTERN.match(model):
        raise ApiError(400, "llm.invalid_model")

    base_url = (base_url or "").strip() or None
    if base_url and not provider.base_url_editable:
        raise ApiError(400, "llm.invalid_base_url")
    if provider.base_url_required and not base_url:
        raise ApiError(400, "llm.base_url_required")
    if base_url:
        base_url = validate_base_url(base_url)

    existing = db.scalar(
        select(UserLLMCredential).where(
            UserLLMCredential.user_id == user.id, UserLLMCredential.provider == provider.id
        )
    )
    api_key = (api_key or "").strip()
    if api_key and (len(api_key) > MAX_API_KEY_LENGTH or any(c.isspace() for c in api_key)):
        raise ApiError(400, "llm.invalid_api_key_format")
    if not api_key and existing is None:
        raise ApiError(400, "llm.api_key_required")
    plain_key = api_key or crypto.decrypt(existing.encrypted_api_key)

    if verify:
        # Appel minimal : clé, modèle et endpoint doivent répondre (erreurs LLMError propagées)
        build_client(provider, api_key=plain_key, model=model, base_url=base_url).generate_json(
            VERIFY_PROMPT, temperature=0
        )

    credential = existing or UserLLMCredential(user_id=user.id, provider=provider.id)
    if api_key:
        credential.encrypted_api_key = crypto.encrypt(api_key)
        credential.key_hint = crypto.key_hint(api_key)
    credential.model = model
    credential.base_url = base_url
    if existing is None:
        db.add(credential)

    # Première configuration : activée d'office
    if activate_now or active_credential(db, user) is None:
        _deactivate_all(db, user)
        credential.is_active = True
    db.commit()
    db.refresh(credential)
    return credential

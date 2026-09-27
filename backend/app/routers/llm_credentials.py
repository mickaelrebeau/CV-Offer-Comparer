from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.services import llm_credentials_service as service
from app.services.auth_service import get_current_user
from app.services.llm.catalog import PROVIDERS
from app.services.llm.crypto import byok_enabled
from app.services.rate_limit_service import rate_limit

router = APIRouter(prefix="/profile", tags=["llm-credentials"])


class CredentialIn(BaseModel):
    # Champs permissifs, validés dans le service : une erreur 422 FastAPI renvoie la valeur
    # reçue dans sa réponse (jamais la clé, toujours acceptée comme chaîne)
    provider: str = ""
    api_key: str | None = None
    model: str = ""
    base_url: str | None = None
    activate: bool = True
    verify: bool = True


def _listing(db: Session, user: User) -> dict:
    items = service.list_credentials(db, user)
    active = next((item for item in items if item.is_active), None)
    return {"items": [item.to_dict() for item in items], "active_id": str(active.id) if active else None}


@router.get("/llm-providers")
def list_providers(_: User = Depends(get_current_user)):
    """Catalogue des providers supportés et modèles suggérés."""
    return {"byok_enabled": byok_enabled(), "providers": [p.to_dict() for p in PROVIDERS.values()]}


@router.get("/llm-credentials")
def list_credentials(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Configurations enregistrées, sans les clés (indice masqué uniquement)."""
    return _listing(db, user)


@router.put(
    "/llm-credentials",
    dependencies=[Depends(rate_limit("llm_credentials", "DAILY_QUOTA_LLM_CREDENTIALS"))],
)
def upsert_credential(
    body: CredentialIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    credential = service.upsert(
        db,
        user,
        provider_id=body.provider,
        api_key=body.api_key,
        model=body.model,
        base_url=body.base_url,
        activate_now=body.activate,
        verify=body.verify,
    )
    return credential.to_dict()


@router.post("/llm-credentials/deactivate")
def deactivate_credentials(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Revenir à la stack plateforme (aucune configuration active)."""
    service.deactivate_all(db, user)
    return _listing(db, user)


@router.post("/llm-credentials/{credential_id}/activate")
def activate_credential(
    credential_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service.activate(db, user, service.get_credential(db, user, credential_id))
    return _listing(db, user)


@router.delete("/llm-credentials/{credential_id}")
def delete_credential(
    credential_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service.delete(db, user, service.get_credential(db, user, credential_id))
    return _listing(db, user)

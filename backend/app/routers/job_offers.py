from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.i18n import ApiError
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.job_offers import service
from app.services.llm_credentials_service import ai_for_user
from app.services.rate_limit_service import rate_limit

router = APIRouter(prefix="/job-offers", tags=["job-offers"])


class ImportIn(BaseModel):
    url: str = ""
    # Nettoyage par le LLM (provider actif de l'utilisateur) : appel IA, compte vérifié requis
    ai_cleanup: bool = False


@router.post(
    "/import",
    dependencies=[Depends(rate_limit("job_offer_import", "DAILY_QUOTA_JOB_OFFER_IMPORT"))],
)
def import_job_offer(body: ImportIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Offre extraite d'une URL publique : {title, company, location, text, source_url, method}."""
    if body.ai_cleanup and not user.email_verified:
        raise ApiError(403, "auth.email_not_verified")
    offer = service.import_offer(body.url)
    if body.ai_cleanup:
        offer = service.clean_with_ai(ai_for_user(db, user), offer)
    return offer

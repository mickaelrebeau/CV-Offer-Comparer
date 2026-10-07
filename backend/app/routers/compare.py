import json
import asyncio

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import require_debug_endpoints
from app.i18n import request_locale
from app.models.comparison import ComparisonRequest
from app.models.comparison_record import ComparisonRecord
from app.services.job_offers.service import safe_offer_url
from app.models.user import User
from app.routers.comparisons import owned_comparison
from app.services.auth_service import AuthService, require_verified_user
from app.services.comparison_service import stream_comparison
from app.services.llm_credentials_service import ai_for_user
from app.services.rate_limit_service import rate_limit

router = APIRouter()
security = HTTPBearer()
auth_service = AuthService()


def _sse_headers() -> dict[str, str]:
    return {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "*",
    }


@router.get("/test-stream", dependencies=[Depends(require_debug_endpoints)], include_in_schema=False)
async def test_stream():
    async def generate_test():
        try:
            for i in range(10):
                yield f"data: {json.dumps({'type': 'status', 'message': f'Test message {i + 1}/10'})}\n\n"
                yield f"data: {json.dumps({'type': 'progress', 'value': (i + 1) * 10, 'current': i + 1, 'total': 10})}\n\n"
                await asyncio.sleep(0.5)
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        generate_test(),
        media_type="text/event-stream",
        headers=_sse_headers(),
    )


@router.post(
    "/compare-stream",
    dependencies=[Depends(require_verified_user), Depends(rate_limit("compare", "DAILY_QUOTA_COMPARE"))],
)
async def compare_cv_offer_stream(
    request: ComparisonRequest,
    user: User = Depends(auth_service.verify_token),
    db: Session = Depends(get_db),
    locale: str = Depends(request_locale),
):
    """Compare CV ↔ offre via un seul appel LLM (provider BYOK actif, sinon Gemini plateforme)."""
    offer_text, offer_url = request.offer_text, safe_offer_url(request.offer_url)
    parent_id = None
    if request.parent_comparison_id is not None:
        # Réanalyse : même offre que la version précédente, quel que soit le texte envoyé
        parent = owned_comparison(db, user, request.parent_comparison_id)
        offer_text, offer_url, parent_id = parent.offer_text, parent.offer_url, parent.id

    ai = ai_for_user(db, user)

    def persist(items, summary) -> str:
        record = ComparisonRecord.from_analysis(
            user_id=user.id,
            offer_text=offer_text,
            cv_text=request.cv_text,
            offer_url=offer_url,
            parent_comparison_id=parent_id,
            items=items,
            summary=summary,
        )
        db.add(record)
        db.commit()
        return str(record.id)

    return StreamingResponse(
        stream_comparison(
            offer_text,
            request.cv_text,
            locale=locale,
            on_result=persist,
            ai=ai,
        ),
        media_type="text/event-stream",
        headers=_sse_headers(),
    )

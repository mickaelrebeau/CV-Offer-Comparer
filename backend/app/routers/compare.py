import json
import asyncio

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer

from app.models.comparison import ComparisonRequest
from app.services.auth_service import AuthService
from app.services.comparison_service import stream_comparison

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


@router.get("/test-stream")
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


@router.post("/compare-stream")
async def compare_cv_offer_stream(
    request: ComparisonRequest,
    user=Depends(auth_service.verify_token),
):
    """Compare CV ↔ offre via un seul appel Gemini, puis stream SSE des items."""
    return StreamingResponse(
        stream_comparison(
            request.offer_text,
            request.cv_text,
            intro_message="Début de l'analyse…",
        ),
        media_type="text/event-stream",
        headers=_sse_headers(),
    )

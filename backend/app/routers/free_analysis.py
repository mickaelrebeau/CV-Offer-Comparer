import hashlib
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse

from app.dependencies import require_debug_endpoints
from app.models.comparison import ComparisonRequest
from app.models.upload import PDFUploadResponse
from app.services.comparison_service import stream_comparison
from app.services.rate_limit_service import get_client_ip, ip_rate_limit
from app.services.redis_service import redis_service
from app.services.upload_service import UploadService

router = APIRouter()
upload_service = UploadService()


def get_client_identifier(request: Request) -> str:
    client_ip = get_client_ip(request)
    user_agent = request.headers.get("user-agent", "")
    identifier = f"{client_ip}:{user_agent}"
    return hashlib.md5(identifier.encode()).hexdigest()


def check_free_analysis_limit(client_id: str) -> bool:
    return redis_service.check_free_analysis_available(client_id)


def mark_free_analysis_used(client_id: str):
    redis_service.mark_free_analysis_used(client_id)


@router.post("/free-compare-stream", dependencies=[Depends(ip_rate_limit("free_compare"))])
async def free_compare_cv_offer_stream(
    request: ComparisonRequest,
    http_request: Request,
):
    """Essai gratuit — même pipeline Gemini optimisé que /compare-stream."""
    client_id = get_client_identifier(http_request)

    if not check_free_analysis_limit(client_id):
        raise HTTPException(
            status_code=429,
            detail="Vous avez déjà utilisé votre analyse gratuite. Veuillez créer un compte pour continuer.",
        )

    mark_free_analysis_used(client_id)

    return StreamingResponse(
        stream_comparison(
            request.offer_text,
            request.cv_text,
            intro_message="Début de l'analyse gratuite…",
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*",
        },
    )


@router.get("/free-analysis-status")
async def get_free_analysis_status(http_request: Request):
    client_id = get_client_identifier(http_request)
    can_use_free = check_free_analysis_limit(client_id)

    analysis_info = None
    if not can_use_free:
        analysis_info = redis_service.get_free_analysis_info(client_id)

    return {
        "can_use_free_analysis": can_use_free,
        "client_id": client_id,
        "message": (
            "Vous pouvez faire une analyse gratuite"
            if can_use_free
            else "Vous avez déjà utilisé votre analyse gratuite"
        ),
        "analysis_info": analysis_info,
    }


@router.post("/reset-free-analysis", dependencies=[Depends(require_debug_endpoints)], include_in_schema=False)
async def reset_free_analysis(http_request: Request):
    client_id = get_client_identifier(http_request)
    success = redis_service.reset_free_analysis(client_id)
    return {
        "message": "Analyse gratuite réinitialisée" if success else "Erreur lors de la réinitialisation",
        "client_id": client_id,
        "success": success,
    }


@router.get("/free-analysis-stats", dependencies=[Depends(require_debug_endpoints)], include_in_schema=False)
async def get_free_analysis_stats():
    stats = redis_service.get_stats()
    redis_health = redis_service.health_check()
    return {
        "stats": stats,
        "redis_health": redis_health,
        "timestamp": datetime.now().isoformat(),
    }


@router.post(
    "/free-upload-cv",
    response_model=PDFUploadResponse,
    dependencies=[Depends(ip_rate_limit("free_upload"))],
)
async def free_upload_cv_pdf(
    http_request: Request,
    file: UploadFile = File(...),
):
    return await upload_service.pdf_upload_response(file)

from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/health")
async def health_check():
    """Point de terminaison de santé"""
    return {
        "status": "healthy", 
        "message": "Comparateur CV ↔ Offre d'emploi",
        "features": {
            "sse": True,
            "streaming": True,
            "timeout": os.getenv("SSE_TIMEOUT", "300")
        }
    }

@router.get("/health/sse")
async def sse_health_check():
    """Point de terminaison de santé spécifique aux SSE"""
    return {
        "status": "healthy",
        "sse_support": True,
        "timeout_seconds": int(os.getenv("SSE_TIMEOUT", "300")),
        "max_concurrent": int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
    } 
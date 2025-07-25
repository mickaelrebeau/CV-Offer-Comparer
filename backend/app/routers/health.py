from fastapi import APIRouter
import os
from app.services.redis_service import redis_service

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

@router.get("/health/redis")
async def redis_health_check():
    """Point de terminaison de santé pour Redis"""
    redis_health = redis_service.health_check()
    stats = redis_service.get_stats()
    
    return {
        "status": "healthy" if redis_health else "unhealthy",
        "redis_connected": redis_health,
        "stats": stats,
        "service": "free_analysis_tracking"
    } 
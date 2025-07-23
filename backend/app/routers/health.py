from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Point de terminaison de santé"""
    return {"status": "healthy", "message": "Comparateur CV ↔ Offre d'emploi"} 
from fastapi import HTTPException

from app.config import settings


def require_debug_endpoints() -> None:
    """Masque les endpoints de debug (404) hors dev avec ENABLE_DEBUG_ENDPOINTS=true."""
    if not settings.debug_endpoints_enabled:
        raise HTTPException(status_code=404, detail="Not Found")

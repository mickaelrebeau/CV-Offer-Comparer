from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db import init_db
from app.i18n import ApiError, negotiate_locale, t
from app.routers import (
    auth,
    compare,
    comparisons,
    cover_letters,
    cv_optimizer,
    free_analysis,
    health,
    interview,
    interviews,
    job_offers,
    llm_credentials,
    saved_cvs,
    upload,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Talento API",
    version="1.0.0",
    description=(
        "API de Talento : analyse ATS d'un CV face à une offre d'emploi, simulateur d'entretien "
        "et générateur de lettre de motivation."
    ),
    lifespan=lifespan,
)


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    """Erreur traduite selon Accept-Language, avec un code stable pour le client."""
    locale = negotiate_locale(request.headers.get("accept-language"))
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": t(exc.code, locale, **exc.params), "code": exc.code},
        headers=exc.headers,
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(compare.router, prefix="/api", tags=["compare"])
app.include_router(comparisons.router, prefix="/api", tags=["comparisons"])
app.include_router(free_analysis.router, prefix="/api", tags=["free-analysis"])
app.include_router(interview.router, prefix="/api", tags=["interview"])
app.include_router(interviews.router, prefix="/api", tags=["interviews"])
app.include_router(cover_letters.router, prefix="/api", tags=["cover-letters"])
app.include_router(cv_optimizer.router, prefix="/api", tags=["cv-optimizer"])
app.include_router(llm_credentials.router, prefix="/api", tags=["llm-credentials"])
app.include_router(saved_cvs.router, prefix="/api", tags=["saved-cvs"])
app.include_router(job_offers.router, prefix="/api", tags=["job-offers"])

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.config import settings
from app.routers import compare, upload, health

app = FastAPI(
    title="Comparateur CV ↔ Offre d'emploi",
    version="1.0.0",
    description="API pour comparer intelligemment un CV avec une offre d'emploi"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de compression pour optimiser les performances
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Inclure les routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(compare.router, prefix="/api", tags=["compare"]) 
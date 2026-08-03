from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.config import settings
from app.db import init_db
from app.routers import auth, compare, comparisons, free_analysis, health, interview, interviews, upload


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Comparateur CV ↔ Offre d'emploi",
    version="1.0.0",
    description="API pour comparer intelligemment un CV avec une offre d'emploi",
    lifespan=lifespan,
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

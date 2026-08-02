from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict
from pydantic import field_validator
from typing import Annotated, List, Union


class Settings(BaseSettings):
    # Google Gemini (IA)
    GOOGLE_API_KEY: str
    GEMINI_MODEL: str = "gemini-flash-latest"

    # Google OAuth (connexion utilisateurs)
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"

    # URL du frontend (redirection après OAuth)
    FRONTEND_URL: str = "http://localhost:3000"

    # CORS — peut être surchargé via ALLOWED_ORIGINS (CSV) dans l'environnement Railway
    ALLOWED_ORIGINS: Annotated[List[str], NoDecode] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://frontend-production-5bcc.up.railway.app",
        "https://cv-compare.up.railway.app",
        "https://cv-offer-comparer-mike-dreeman.vercel.app",
    ]

    # Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # JWT
    SECRET_KEY: str = "your_secret_key_here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 jours

    # Production settings
    ENVIRONMENT: str = "development"

    # Redis (Railway / local)
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    # PostgreSQL Railway
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, value: Union[str, List[str]]) -> List[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()

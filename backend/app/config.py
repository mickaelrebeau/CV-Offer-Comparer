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
        "https://cv-compare.up.railway.app",
    ]

    # Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # JWT
    SECRET_KEY: str = "your_secret_key_here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 jours

    # E-mails transactionnels (vérification, reset). "console" = liens affichés dans les logs (dev)
    EMAIL_PROVIDER: str = "console"  # console | resend
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "Talento <no-reply@talento.app>"
    EMAIL_VERIFICATION_TTL_HOURS: int = 48
    PASSWORD_RESET_TTL_MINUTES: int = 60

    # Production settings
    ENVIRONMENT: str = "development"
    # Endpoints de debug (test-stream, reset free-trial, stats…) : jamais exposés en production
    ENABLE_DEBUG_ENDPOINTS: bool = False

    # Rate limiting (0 = illimité). Fenêtre glissante d'une minute + quota journalier UTC par utilisateur
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_USER_PER_MINUTE: int = 10
    RATE_LIMIT_IP_PER_MINUTE: int = 30
    DAILY_QUOTA_COMPARE: int = 50
    DAILY_QUOTA_INTERVIEW_GENERATE: int = 30
    DAILY_QUOTA_INTERVIEW_ANALYZE: int = 30
    DAILY_QUOTA_UPLOAD: int = 100
    # Header contenant l'IP réelle du client derrière le proxy (Railway : X-Real-IP). Vide = IP de la socket
    CLIENT_IP_HEADER: str = "X-Real-IP"

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

    @property
    def debug_endpoints_enabled(self) -> bool:
        return self.ENABLE_DEBUG_ENDPOINTS and self.ENVIRONMENT.lower() != "production"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, value: Union[str, List[str]]) -> List[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()

import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    
    # Google Gemini
    GOOGLE_API_KEY: str
    
    # CORS - Support pour les environnements de production
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://localhost:5173",
        "https://cv-offer-comparer-mike-dreeman.vercel.app",  # Frontend Vercel
        "https://cv-offer-comparer.onrender.com", # Backend Render
    ]
    
    # Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # JWT (si nécessaire pour l'authentification)
    SECRET_KEY: str = "your_secret_key_here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Production settings
    ENVIRONMENT: str = "development"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    
    class Config:
        env_file = ".env"
        # Permettre les champs supplémentaires dans le fichier .env
        extra = "ignore"

settings = Settings() 
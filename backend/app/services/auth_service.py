from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from app.config import settings

class AuthService:
    def __init__(self):
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        self.security = HTTPBearer()
    
    async def verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """Vérifie le token d'authentification"""
        try:
            # Vérifier le token avec Supabase
            user = self.supabase.auth.get_user(credentials.credentials)
            return user
        except Exception:
            raise HTTPException(status_code=401, detail="Token invalide") 
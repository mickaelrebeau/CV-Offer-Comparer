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
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """Récupère l'utilisateur actuel à partir du token"""
        try:
            # Vérifier le token avec Supabase
            user_response = self.supabase.auth.get_user(credentials.credentials)
            if user_response.user:
                return {
                    "id": user_response.user.id,
                    "email": user_response.user.email,
                    "role": "user"  # Par défaut
                }
            else:
                raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
        except Exception as e:
            raise HTTPException(status_code=401, detail="Token invalide")

# Instance globale du service d'authentification
auth_service = AuthService()

# Fonction de dépendance pour récupérer l'utilisateur actuel
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    return await auth_service.get_current_user(credentials) 
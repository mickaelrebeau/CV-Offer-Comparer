from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode
from uuid import UUID

import bcrypt
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.user import User

security = HTTPBearer()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(user_id: str, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": user_id, "email": email, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
        ) from exc


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def get_user_by_id(db: Session, user_id: str | UUID) -> User | None:
    try:
        uid = UUID(str(user_id))
    except ValueError:
        return None
    return db.get(User, uid)


def register_user(db: Session, email: str, password: str) -> User:
    email = email.lower().strip()
    if get_user_by_email(db, email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte existe déjà avec cet email",
        )
    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = get_user_by_email(db, email.lower().strip())
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )
    return user


def google_authorize_url(state: str | None = None) -> str:
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth non configuré (GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET)",
        )
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
        "prompt": "select_account",
    }
    if state:
        params["state"] = state
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


async def exchange_google_code(code: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=20) as client:
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            headers={"Accept": "application/json"},
        )
        if token_response.status_code != 200:
            err_body = token_response.text
            print(
                f"[OAuth] token exchange failed ({token_response.status_code}): {err_body} "
                f"| redirect_uri={settings.GOOGLE_REDIRECT_URI}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Échec de l'échange du code Google: {err_body}",
            )
        tokens = token_response.json()
        access_token = tokens.get("access_token")
        id_token = tokens.get("id_token")

        # Profil via userinfo (prioritaire)
        if access_token:
            userinfo_response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if userinfo_response.status_code == 200:
                return userinfo_response.json()
            print(f"[OAuth] userinfo failed: {userinfo_response.text}")

        # Fallback : décoder l'id_token via tokeninfo
        if id_token:
            info = await verify_google_id_token(id_token)
            return info

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token Google manquant",
        )



async def verify_google_id_token(id_token: str) -> dict[str, Any]:
    """Vérifie un ID token GIS via le endpoint tokeninfo Google."""
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": id_token},
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="ID token Google invalide",
            )
        data = response.json()
        audience = data.get("aud")
        if settings.GOOGLE_CLIENT_ID and audience != settings.GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Audience Google invalide",
            )
        if data.get("email_verified") not in (True, "true"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email Google non vérifié",
            )
        return data


def upsert_google_user(db: Session, profile: dict[str, Any]) -> User:
    email = (profile.get("email") or "").lower().strip()
    google_id = profile.get("sub") or profile.get("id")
    if not email or not google_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profil Google incomplet",
        )

    user = db.scalar(select(User).where(User.google_id == str(google_id)))
    if not user:
        user = get_user_by_email(db, email)

    if user:
        user.google_id = str(google_id)
        user.full_name = profile.get("name") or user.full_name
        user.avatar_url = profile.get("picture") or user.avatar_url
        if not user.email:
            user.email = email
    else:
        user = User(
            email=email,
            google_id=str(google_id),
            full_name=profile.get("name"),
            avatar_url=profile.get("picture"),
        )
        db.add(user)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token invalide")
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
    return user


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Alias pour les routes protégées existantes."""
    return await get_current_user(credentials=credentials, db=db)


class AuthService:
    """Compatibilité avec les Depends(auth_service.verify_token) existants."""

    verify_token = staticmethod(verify_token)
    get_current_user = staticmethod(get_current_user)


auth_service = AuthService()

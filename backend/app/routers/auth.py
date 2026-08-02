from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    GoogleTokenRequest,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    delete_user,
    exchange_google_code,
    get_current_user,
    google_authorize_url,
    register_user,
    upsert_google_user,
    verify_google_id_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _auth_payload(user: User) -> AuthResponse:
    return AuthResponse(
        access_token=create_access_token(str(user.id), user.email),
        user=UserResponse(**user.to_public_dict()),
    )


@router.post("/register", response_model=AuthResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(db, payload.email, payload.password)
    return _auth_payload(user)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)
    return _auth_payload(user)


@router.get("/google")
def google_login():
    """Démarre le flux OAuth Google (redirection)."""
    return RedirectResponse(google_authorize_url(), status_code=302)


@router.get("/google/callback")
async def google_callback(
    code: str | None = Query(default=None),
    error: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    frontend = settings.FRONTEND_URL.rstrip("/")
    if error or not code:
        print(f"[OAuth] callback without code: error={error}")
        return RedirectResponse(
            f"{frontend}/login?error=google_oauth&reason=no_code",
            status_code=302,
        )

    try:
        profile = await exchange_google_code(code)
        user = upsert_google_user(db, profile)
        token = create_access_token(str(user.id), user.email)
        query = urlencode({"token": token})
        redirect_to = f"{frontend}/auth/callback?{query}"
        print(f"[OAuth] success for {user.email} → {frontend}/auth/callback")
        return RedirectResponse(redirect_to, status_code=302)
    except HTTPException as exc:
        print(f"[OAuth] HTTPException: {exc.detail}")
        return RedirectResponse(
            f"{frontend}/login?error=google_oauth&reason=exchange_failed",
            status_code=302,
        )
    except Exception as exc:
        print(f"[OAuth] unexpected error: {exc!r}")
        return RedirectResponse(
            f"{frontend}/login?error=google_oauth&reason=server_error",
            status_code=302,
        )



@router.post("/google/token", response_model=AuthResponse)
async def google_token_login(
    payload: GoogleTokenRequest,
    db: Session = Depends(get_db),
):
    """Alternative : ID token Google Identity Services."""
    profile = await verify_google_id_token(payload.id_token)
    user = upsert_google_user(db, profile)
    return _auth_payload(user)


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return UserResponse(**user.to_public_dict())


@router.delete("/me")
def delete_me(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delete_user(db, user)
    return {"success": True, "message": "Compte supprimé"}

from urllib.parse import urlencode

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    GoogleCodeExchangeRequest,
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
    get_user_by_id,
    google_authorize_url,
    register_user,
    upsert_google_user,
    verify_google_id_token,
)
from app.services.oauth_service import (
    OAUTH_STATE_COOKIE,
    OAUTH_STATE_MAX_AGE,
    generate_state,
    is_valid_state,
    oauth_code_store,
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


def _state_cookie_kwargs() -> dict:
    # Cookie posé et relu sur le domaine du backend (redirections top-level → SameSite=Lax suffit)
    return {
        "path": "/api/auth/google",
        "httponly": True,
        "secure": settings.GOOGLE_REDIRECT_URI.startswith("https://"),
        "samesite": "lax",
    }


def _login_error_redirect(reason: str) -> RedirectResponse:
    frontend = settings.FRONTEND_URL.rstrip("/")
    response = RedirectResponse(
        f"{frontend}/login?error=google_oauth&reason={reason}",
        status_code=302,
    )
    response.delete_cookie(OAUTH_STATE_COOKIE, **_state_cookie_kwargs())
    return response


@router.get("/google")
def google_login():
    """Démarre le flux OAuth Google (redirection) avec un state anti-CSRF."""
    state = generate_state()
    response = RedirectResponse(google_authorize_url(state), status_code=302)
    response.set_cookie(
        OAUTH_STATE_COOKIE,
        state,
        max_age=OAUTH_STATE_MAX_AGE,
        **_state_cookie_kwargs(),
    )
    return response


@router.get("/google/callback")
async def google_callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    oauth_state: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    if error or not code:
        print(f"[OAuth] callback without code: error={error}")
        return _login_error_redirect("no_code")

    if not is_valid_state(oauth_state, state):
        print("[OAuth] invalid state")
        return _login_error_redirect("invalid_state")

    try:
        profile = await exchange_google_code(code)
        user = upsert_google_user(db, profile)
    except HTTPException as exc:
        print(f"[OAuth] HTTPException: {exc.detail}")
        return _login_error_redirect("exchange_failed")
    except Exception as exc:
        print(f"[OAuth] unexpected error: {exc!r}")
        return _login_error_redirect("server_error")

    # Code à usage unique : le JWT ne transite jamais dans l'URL
    frontend = settings.FRONTEND_URL.rstrip("/")
    query = urlencode({"code": oauth_code_store.issue(str(user.id))})
    print(f"[OAuth] success for {user.email} → {frontend}/auth/callback")
    response = RedirectResponse(f"{frontend}/auth/callback?{query}", status_code=302)
    response.delete_cookie(OAUTH_STATE_COOKIE, **_state_cookie_kwargs())
    return response


@router.post("/google/exchange", response_model=AuthResponse)
def google_code_exchange(
    payload: GoogleCodeExchangeRequest,
    db: Session = Depends(get_db),
):
    """Échange le code à usage unique du callback contre un JWT."""
    user_id = oauth_code_store.consume(payload.code)
    user = get_user_by_id(db, user_id) if user_id else None
    if not user:
        raise HTTPException(status_code=400, detail="Code de connexion invalide ou expiré")
    return _auth_payload(user)


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

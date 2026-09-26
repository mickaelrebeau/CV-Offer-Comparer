from urllib.parse import urlencode

from fastapi import APIRouter, BackgroundTasks, Cookie, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.i18n import ApiError, request_locale, t
from app.models.auth_token import PURPOSE_RESET_PASSWORD, PURPOSE_VERIFY_EMAIL
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    GoogleCodeExchangeRequest,
    GoogleTokenRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    UserResponse,
    VerifyEmailRequest,
)
from app.services.account_service import (
    build_password_reset_email,
    build_verification_email,
    consume_token,
    mark_email_verified,
    reset_password,
)
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    delete_user,
    exchange_google_code,
    get_current_user,
    get_user_by_email,
    get_user_by_id,
    google_authorize_url,
    register_user,
    upsert_google_user,
    verify_google_id_token,
)
from app.services.email_service import send_email
from app.services.oauth_service import (
    OAUTH_STATE_COOKIE,
    OAUTH_STATE_MAX_AGE,
    generate_state,
    is_valid_state,
    oauth_code_store,
)
from app.services.rate_limit_service import ip_rate_limit

router = APIRouter(prefix="/auth", tags=["auth"])


def _auth_payload(user: User) -> AuthResponse:
    return AuthResponse(
        access_token=create_access_token(str(user.id), user.email),
        user=UserResponse(**user.to_public_dict()),
    )


@router.post("/register", response_model=AuthResponse)
def register(
    payload: RegisterRequest,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    locale: str = Depends(request_locale),
):
    user = register_user(db, payload.email, payload.password)
    background.add_task(send_email, build_verification_email(db, user, locale))
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


@router.post("/forgot-password", dependencies=[Depends(ip_rate_limit("forgot_password"))])
def forgot_password(
    payload: ForgotPasswordRequest,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    locale: str = Depends(request_locale),
):
    """Réponse identique que le compte existe ou non (pas d'énumération d'adresses)."""
    user = get_user_by_email(db, payload.email)
    if user:
        background.add_task(send_email, build_password_reset_email(db, user, locale))
    return {"success": True, "message": t("auth.forgot_password_sent", locale)}


@router.post("/reset-password", response_model=AuthResponse)
def reset_password_route(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = consume_token(db, payload.token, PURPOSE_RESET_PASSWORD)
    if not user:
        raise ApiError(400, "auth.invalid_reset_link")
    return _auth_payload(reset_password(db, user, payload.password))


@router.post("/verify-email", response_model=UserResponse)
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)):
    user = consume_token(db, payload.token, PURPOSE_VERIFY_EMAIL)
    if not user:
        raise ApiError(400, "auth.invalid_verification_link")
    return UserResponse(**mark_email_verified(db, user).to_public_dict())


@router.post("/resend-verification", dependencies=[Depends(ip_rate_limit("resend_verification"))])
def resend_verification(
    background: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    locale: str = Depends(request_locale),
):
    if user.email_verified:
        return {"success": True, "message": t("auth.already_verified", locale)}
    background.add_task(send_email, build_verification_email(db, user, locale))
    return {"success": True, "message": t("auth.verification_sent", locale)}


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
        raise ApiError(400, "auth.invalid_login_code")
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
    locale: str = Depends(request_locale),
):
    delete_user(db, user)
    return {"success": True, "message": t("auth.account_deleted", locale)}

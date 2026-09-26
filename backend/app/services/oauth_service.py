import secrets
import threading
import time

from app.services.redis_service import redis_service

OAUTH_STATE_COOKIE = "oauth_state"
OAUTH_STATE_MAX_AGE = 10 * 60  # 10 min pour finir le consentement Google
OAUTH_CODE_TTL = 60  # le front échange le code immédiatement


def generate_state() -> str:
    return secrets.token_urlsafe(32)


def is_valid_state(expected: str | None, received: str | None) -> bool:
    if not expected or not received:
        return False
    return secrets.compare_digest(expected, received)


class OAuthCodeStore:
    """Codes à usage unique échangés contre un JWT (Redis, sinon mémoire)."""

    def __init__(self) -> None:
        self._memory: dict[str, tuple[str, float]] = {}
        self._lock = threading.Lock()

    @staticmethod
    def _key(code: str) -> str:
        return f"oauth_code:{code}"

    def issue(self, user_id: str) -> str:
        code = secrets.token_urlsafe(32)
        if redis_service.redis_available:
            try:
                redis_service.redis_client.setex(self._key(code), OAUTH_CODE_TTL, user_id)
                return code
            except Exception as e:
                print(f"[OAuth] Redis indisponible, code stocké en mémoire: {e}")
        with self._lock:
            self._purge_expired()
            self._memory[code] = (user_id, time.monotonic() + OAUTH_CODE_TTL)
        return code

    def consume(self, code: str) -> str | None:
        if redis_service.redis_available:
            try:
                pipe = redis_service.redis_client.pipeline()
                pipe.get(self._key(code))
                pipe.delete(self._key(code))
                user_id, _ = pipe.execute()
                if user_id:
                    return user_id
            except Exception as e:
                print(f"[OAuth] Redis indisponible, lecture du code en mémoire: {e}")
        with self._lock:
            entry = self._memory.pop(code, None)
        if not entry or entry[1] < time.monotonic():
            return None
        return entry[0]

    def _purge_expired(self) -> None:
        now = time.monotonic()
        for code in [c for c, (_, exp) in self._memory.items() if exp < now]:
            del self._memory[code]


oauth_code_store = OAuthCodeStore()

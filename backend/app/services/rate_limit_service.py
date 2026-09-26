import math
import threading
import time
import uuid
from collections import deque
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request

from app.config import settings
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.redis_service import redis_service

MINUTE = 60


def get_client_ip(request: Request) -> str:
    """IP du client : header posé par le proxy (X-Real-IP sur Railway), sinon socket."""
    header = settings.CLIENT_IP_HEADER
    if header:
        value = request.headers.get(header, "").split(",")[0].strip()
        if value:
            return value
    return request.client.host if request.client else "unknown"


def _seconds_until_utc_midnight(now: datetime) -> int:
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return max(1, math.ceil((tomorrow - now).total_seconds()))


class RateLimiter:
    """Fenêtre glissante (sorted set Redis) + quota journalier UTC (compteur Redis).

    Retombe sur un stockage mémoire si Redis est indisponible.
    """

    def __init__(self) -> None:
        self._windows: dict[str, deque[float]] = {}
        self._counters: dict[str, tuple[int, float]] = {}
        self._lock = threading.Lock()

    def reset(self) -> None:
        with self._lock:
            self._windows.clear()
            self._counters.clear()

    # --- Fenêtre glissante -------------------------------------------------

    def hit_window(self, key: str, limit: int, window: int) -> int | None:
        """Enregistre un appel ; renvoie le Retry-After (s) si la limite est atteinte."""
        if limit <= 0:
            return None
        if redis_service.redis_available:
            try:
                return self._hit_window_redis(key, limit, window)
            except Exception as e:
                print(f"[RateLimit] Redis indisponible, fallback mémoire: {e}")
        return self._hit_window_memory(key, limit, window)

    def _hit_window_redis(self, key: str, limit: int, window: int) -> int | None:
        client = redis_service.redis_client
        now = time.time()
        pipe = client.pipeline()
        pipe.zremrangebyscore(key, 0, now - window)
        pipe.zcard(key)
        pipe.zrange(key, 0, 0, withscores=True)
        _, count, oldest = pipe.execute()
        if count >= limit:
            oldest_ts = oldest[0][1] if oldest else now
            return max(1, math.ceil(oldest_ts + window - now))
        pipe = client.pipeline()
        pipe.zadd(key, {f"{now}:{uuid.uuid4().hex}": now})
        pipe.expire(key, window)
        pipe.execute()
        return None

    def _hit_window_memory(self, key: str, limit: int, window: int) -> int | None:
        now = time.monotonic()
        with self._lock:
            hits = self._windows.setdefault(key, deque())
            while hits and hits[0] <= now - window:
                hits.popleft()
            if len(hits) >= limit:
                return max(1, math.ceil(hits[0] + window - now))
            hits.append(now)
        return None

    # --- Quota journalier --------------------------------------------------

    def hit_daily(self, key: str, quota: int) -> int | None:
        """Incrémente le quota du jour (UTC) ; renvoie le Retry-After (s) s'il est dépassé."""
        if quota <= 0:
            return None
        now = datetime.now(timezone.utc)
        ttl = _seconds_until_utc_midnight(now)
        day_key = f"{key}:{now:%Y-%m-%d}"
        count = None
        if redis_service.redis_available:
            try:
                pipe = redis_service.redis_client.pipeline()
                pipe.incr(day_key)
                pipe.expire(day_key, ttl + MINUTE)
                count, _ = pipe.execute()
            except Exception as e:
                print(f"[RateLimit] Redis indisponible, fallback mémoire: {e}")
        if count is None:
            with self._lock:
                value, expires = self._counters.get(day_key, (0, 0.0))
                if expires < time.monotonic():
                    value = 0
                count = value + 1
                self._counters[day_key] = (count, time.monotonic() + ttl)
        return ttl if count > quota else None


rate_limiter = RateLimiter()


def _too_many(message: str, retry_after: int) -> HTTPException:
    return HTTPException(
        status_code=429,
        detail=message,
        headers={"Retry-After": str(retry_after)},
    )


def _check_ip_window(action: str, request: Request) -> None:
    ip = get_client_ip(request)
    retry = rate_limiter.hit_window(f"rl:{action}:ip:{ip}", settings.RATE_LIMIT_IP_PER_MINUTE, MINUTE)
    if retry:
        raise _too_many("Trop de requêtes depuis cette adresse IP. Réessayez dans un instant.", retry)


def rate_limit(action: str, daily_quota_setting: str):
    """Dépendance : limite par minute (user + IP) et quota journalier par user."""

    def dependency(request: Request, user: User = Depends(get_current_user)) -> None:
        if not settings.RATE_LIMIT_ENABLED:
            return
        retry = rate_limiter.hit_window(
            f"rl:{action}:user:{user.id}", settings.RATE_LIMIT_USER_PER_MINUTE, MINUTE
        )
        if retry:
            raise _too_many("Trop de requêtes. Réessayez dans un instant.", retry)
        _check_ip_window(action, request)
        retry = rate_limiter.hit_daily(f"quota:{action}:user:{user.id}", getattr(settings, daily_quota_setting))
        if retry:
            raise _too_many("Quota journalier atteint. Réessayez demain.", retry)

    return dependency


def ip_rate_limit(action: str):
    """Dépendance pour les routes anonymes (essai gratuit) : limite par minute et par IP."""

    def dependency(request: Request) -> None:
        if settings.RATE_LIMIT_ENABLED:
            _check_ip_window(action, request)

    return dependency

"""In-memory sliding-window rate limiter.

Protects a hosted PedroIA backend from runaway usage (and runaway bills).
Keyed by API key when present, otherwise by client IP. For a single instance
this is enough; for multiple instances, back it with Redis (see note below).
"""
from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock
from typing import Deque, Dict

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings

# Paths that are never rate-limited.
_EXEMPT_PREFIXES = ("/docs", "/openapi.json", "/redoc", "/")
_EXEMPT_EXACT = {"/api/v1/health"}


class SlidingWindowLimiter:
    def __init__(self) -> None:
        self._minute: Dict[str, Deque[float]] = defaultdict(deque)
        self._day: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def _trim(self, dq: Deque[float], window: float, now: float) -> None:
        cutoff = now - window
        while dq and dq[0] < cutoff:
            dq.popleft()

    def check(self, key: str, per_minute: int, per_day: int) -> tuple[bool, str]:
        now = time.time()
        with self._lock:
            m, dd = self._minute[key], self._day[key]
            self._trim(m, 60, now)
            self._trim(dd, 86400, now)
            if len(m) >= per_minute:
                return False, "Limite por minuto excedido. Tente novamente em instantes."
            if len(dd) >= per_day:
                return False, "Limite diário excedido."
            m.append(now)
            dd.append(now)
            return True, ""


_limiter = SlidingWindowLimiter()


def _client_key(request: Request) -> str:
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return "key:" + auth[7:].strip()[:64]
    # Respect a proxy's forwarded IP when present (Render/Fly set this).
    fwd = request.headers.get("x-forwarded-for", "")
    ip = fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "unknown")
    return "ip:" + ip


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        path = request.url.path
        if not settings.rate_limit_enabled or path in _EXEMPT_EXACT or path == "/":
            return await call_next(request)
        if any(path.startswith(p) and p != "/" for p in _EXEMPT_PREFIXES):
            return await call_next(request)

        allowed, message = _limiter.check(
            _client_key(request), settings.rate_limit_per_minute, settings.rate_limit_per_day
        )
        if not allowed:
            return JSONResponse(status_code=429, content={"detail": message})
        return await call_next(request)

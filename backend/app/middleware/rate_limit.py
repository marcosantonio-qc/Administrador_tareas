from __future__ import annotations
import time
from typing import Dict, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 200, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._buckets: Dict[Tuple[str, str], Tuple[int, float]] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        key = (client_ip, request.url.path)
        now = time.time()

        count, reset = self._buckets.get(key, (0, now + self.window_seconds))
        if now > reset:
            count, reset = 0, now + self.window_seconds
        count += 1
        self._buckets[key] = (count, reset)

        if count > self.max_requests:
            retry_after = int(reset - now)
            return JSONResponse({"detail": "Too Many Requests"}, status_code=429, headers={"Retry-After": str(retry_after)})

        response: Response = await call_next(request)
        remaining = max(0, self.max_requests - count)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(reset))
        return response

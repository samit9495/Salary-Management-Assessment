"""Request-scoped logging context.

Each inbound HTTP request is assigned an ``X-Request-ID`` (echoed if the
client supplied one, freshly generated otherwise). The id is exposed via
:data:`app.core.logging.request_id_var` so any log emitted while the
request is in flight carries the same correlation id, returned as a
response header so the client can grep server logs.

A single structured INFO line per request records method, path, status,
and duration. The health check (``GET /``) drops to DEBUG so the
production access log is not dominated by Fly's keep-alive probes.
"""
from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import request_id_var

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Set ``request_id_var``, emit access log, attach response header."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        token = request_id_var.set(request_id)
        started = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            duration_ms = (time.perf_counter() - started) * 1000.0
            request_id_var.reset(token)

        response.headers[REQUEST_ID_HEADER] = request_id

        is_health_check = request.method == "GET" and request.url.path == "/"
        log = logger.debug if is_health_check else logger.info
        log(
            "http_request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 3),
                "request_id": request_id,
            },
        )
        return response

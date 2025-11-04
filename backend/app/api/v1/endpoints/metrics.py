"""Prometheus metrics endpoint and middleware."""

from __future__ import annotations

import time
from typing import Awaitable, Callable

from fastapi import APIRouter
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, REGISTRY, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

router = APIRouter()

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)
REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to record Prometheus metrics for each HTTP request."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)

        route = request.scope.get("route")
        path_template = getattr(route, "path", request.url.path)

        # Skip recording metrics for the metrics endpoint itself to avoid recursion
        if path_template != "/metrics":
            REQUEST_COUNT.labels(
                method=request.method,
                path=path_template,
                status_code=response.status_code,
            ).inc()

            elapsed = time.perf_counter() - start_time
            REQUEST_LATENCY.labels(
                method=request.method,
                path=path_template,
            ).observe(elapsed)

        return response


@router.get("", include_in_schema=False)
def metrics_endpoint() -> Response:
    """Expose Prometheus metrics at the "/metrics" path."""

    metrics_data = generate_latest(REGISTRY)
    return Response(metrics_data, media_type=CONTENT_TYPE_LATEST)
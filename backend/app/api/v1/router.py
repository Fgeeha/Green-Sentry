from fastapi import APIRouter
from app.api.v1.endpoints import diagnosis, health, users, analytics, history, metrics

api_router = APIRouter()

api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

api_router.include_router(
    diagnosis.router,
    prefix="/diagnosis",
    tags=["diagnosis"]
)

api_router.include_router(
    history.router,
    prefix="/history",
    tags=["history"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"]
)

api_router.include_router(
    metrics.router,
    prefix="/metrics",
    tags=["metrics"]
)

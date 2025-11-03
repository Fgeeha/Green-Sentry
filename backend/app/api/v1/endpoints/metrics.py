from fastapi import APIRouter

router = APIRouter()

@router.get("/metrics")
async def metrics():
    """Expose a lightweight readiness/metrics endpoint for Prometheus."""
    return {"status": "ok"}
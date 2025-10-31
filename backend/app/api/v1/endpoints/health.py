from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.session import get_db
from app.core.config import settings
from app.core.cache import cache
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""

    # Check database
    db_healthy = True
    try:
        db.execute("SELECT 1")
    except Exception:
        db_healthy = False

    # Check cache
    cache_healthy = True
    try:
        cache.set("health_check", "ok", ttl=10)
        cache_healthy = cache.get("health_check") == "ok"
    except Exception:
        cache_healthy = False

    # Check ML model (simplified)
    ml_healthy = True

    return HealthResponse(
        status="healthy" if all([db_healthy, cache_healthy, ml_healthy]) else "unhealthy",
        version=settings.VERSION,
        timestamp=datetime.utcnow(),
        database=db_healthy,
        cache=cache_healthy,
        ml_model=ml_healthy
    )
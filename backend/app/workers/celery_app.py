from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "plant_disease",
    broker=settings.CELERY_CONFIG["broker_url"],
    backend=settings.CELERY_CONFIG["result_backend"]
)

celery_app.conf.update(settings.CELERY_CONFIG)


@celery_app.task(name="process_diagnosis_async")
def process_diagnosis_async(
        user_id: int,
        image_path: str,
        context: dict
):
    """Async diagnosis processing"""
    from app.db.session import SessionLocal
    from app.services.diagnosis_service import diagnosis_service

    db = SessionLocal()
    try:
        result = diagnosis_service.diagnose(
            db=db,
            user_id=user_id,
            image_path=image_path,
            **context
        )
        return result
    finally:
        db.close()
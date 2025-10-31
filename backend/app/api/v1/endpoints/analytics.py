from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.database.user import User
from app.models.database.diagnosis import Diagnosis

router = APIRouter()


@router.get("/statistics")
def get_statistics(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get analytics statistics"""

    # Total diagnoses
    total_diagnoses = db.query(Diagnosis).count()

    # User's diagnoses
    user_diagnoses = db.query(Diagnosis).filter(
        Diagnosis.user_id == current_user.id
    ).count()

    # Average confidence
    avg_confidence = db.query(
        func.avg(Diagnosis.confidence)
    ).scalar() or 0

    # Most common diseases
    most_common = db.query(
        Diagnosis.disease_name,
        func.count(Diagnosis.id).label('count')
    ).group_by(
        Diagnosis.disease_name
    ).order_by(
        func.count(Diagnosis.id).desc()
    ).limit(5).all()

    # Average processing time
    avg_processing_time = db.query(
        func.avg(Diagnosis.processing_time)
    ).scalar() or 0

    return {
        "total_diagnoses": total_diagnoses,
        "user_diagnoses": user_diagnoses,
        "avg_confidence": float(avg_confidence),
        "avg_processing_time": float(avg_processing_time),
        "most_common_diseases": [
            {"disease": disease, "count": count}
            for disease, count in most_common
        ]
    }
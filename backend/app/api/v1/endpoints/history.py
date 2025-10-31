from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.database.user import User
from app.repositories.diagnosis import diagnosis_repository
from app.schemas.diagnosis import DiagnosisResponse
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[DiagnosisResponse])
def get_diagnosis_history(
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get diagnosis history for current user"""
    diagnoses = diagnosis_repository.get_by_user(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )

    total = diagnosis_repository.count_by_user(db, user_id=current_user.id)

    return PaginatedResponse(
        items=diagnoses,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total
    )


@router.get("/{diagnosis_id}", response_model=DiagnosisResponse)
def get_diagnosis_by_id(
        diagnosis_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get specific diagnosis"""
    diagnosis = diagnosis_repository.get(db, id=diagnosis_id)

    if not diagnosis:
        raise HTTPException(status_code=404, detail="Diagnosis not found")

    if diagnosis.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return diagnosis
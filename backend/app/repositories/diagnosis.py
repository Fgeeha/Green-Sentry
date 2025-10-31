from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.database.diagnosis import Diagnosis
from app.schemas.diagnosis import DiagnosisCreate, DiagnosisUpdate
from app.repositories.base import BaseRepository


class DiagnosisRepository(BaseRepository[Diagnosis, DiagnosisCreate, DiagnosisUpdate]):
    """Repository for diagnosis operations"""

    def get_by_user(
            self,
            db: Session,
            user_id: int,
            skip: int = 0,
            limit: int = 100
    ) -> List[Diagnosis]:
        """Get all diagnoses for a user"""
        return (
            db.query(Diagnosis)
            .filter(Diagnosis.user_id == user_id)
            .order_by(desc(Diagnosis.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_disease(
            self,
            db: Session,
            disease_name: str,
            skip: int = 0,
            limit: int = 100
    ) -> List[Diagnosis]:
        """Get diagnoses by disease name"""
        return (
            db.query(Diagnosis)
            .filter(Diagnosis.disease_name == disease_name)
            .order_by(desc(Diagnosis.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_high_confidence(
            self,
            db: Session,
            threshold: float = 0.9,
            limit: int = 100
    ) -> List[Diagnosis]:
        """Get high confidence diagnoses"""
        return (
            db.query(Diagnosis)
            .filter(Diagnosis.confidence >= threshold)
            .order_by(desc(Diagnosis.confidence))
            .limit(limit)
            .all()
        )

    def get_recent(
            self,
            db: Session,
            limit: int = 10
    ) -> List[Diagnosis]:
        """Get recent diagnoses"""
        return (
            db.query(Diagnosis)
            .order_by(desc(Diagnosis.created_at))
            .limit(limit)
            .all()
        )

    def get_by_image_hash(
            self,
            db: Session,
            image_hash: str
    ) -> Optional[Diagnosis]:
        """Get diagnosis by image hash (для дедупликации)"""
        return (
            db.query(Diagnosis)
            .filter(Diagnosis.image_hash == image_hash)
            .order_by(desc(Diagnosis.created_at))
            .first()
        )


diagnosis_repository = DiagnosisRepository(Diagnosis)
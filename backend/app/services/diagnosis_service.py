from typing import Dict, Optional
from sqlalchemy.orm import Session
import time
import hashlib
from pathlib import Path

from app.models.ml.cv_model import PlantDiseaseClassifier
from app.models.ml.reasoning_agent import DiseaseReasoningAgent
from app.utils.image_processor import ImageProcessor
from app.repositories.diagnosis import diagnosis_repository
from app.models.database.diagnosis import Diagnosis
from app.core.config import settings
from app.core.cache import cache, cached
from app.core.exceptions import ImageProcessingException, ModelInferenceException


class DiagnosisService:
    """Service for plant disease diagnosis"""

    def __init__(self):
        self.cv_model = PlantDiseaseClassifier()
        self.reasoning_agent = DiseaseReasoningAgent()
        self.image_processor = ImageProcessor()

    def process_image(self, image_path: str) -> str:
        """Calculate image hash for deduplication"""
        with open(image_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    @cached(ttl=3600, prefix="diagnosis")
    def diagnose(
            self,
            db: Session,
            user_id: int,
            image_path: str,
            region: Optional[str] = None,
            climate: Optional[str] = None,
            plant_age: Optional[int] = None,
            additional_context: Optional[str] = None,
            use_reasoning: bool = True
    ) -> Dict:
        """Perform complete diagnosis"""

        start_time = time.time()

        try:
            # Calculate image hash
            image_hash = self.process_image(image_path)

            # Check for duplicate diagnosis
            if settings.DIAGNOSIS_CACHE_ENABLED:
                cached_diagnosis = diagnosis_repository.get_by_image_hash(
                    db, image_hash
                )
                if cached_diagnosis:
                    return {
                        "cached": True,
                        "diagnosis": cached_diagnosis
                    }

            # Load and preprocess image
            image = self.image_processor.load_and_preprocess(image_path)

            # CV Model prediction
            cv_result = self.cv_model.predict(image)

            # Reasoning analysis
            reasoning_result = None
            if use_reasoning:
                reasoning_result = self.reasoning_agent.analyze_disease(
                    cv_result=cv_result,
                    region=region or settings.DEFAULT_REGION,
                    climate=climate or settings.DEFAULT_CLIMATE,
                    plant_age=plant_age,
                    additional_context=additional_context
                )

            processing_time = time.time() - start_time

            # Save to database
            diagnosis = Diagnosis(
                user_id=user_id,
                image_path=image_path,
                image_hash=image_hash,
                predicted_class=cv_result["predicted_class"],
                disease_name=cv_result["disease_name"],
                confidence=cv_result["confidence"],
                cv_results=cv_result,
                region=region,
                climate=climate,
                plant_age=plant_age,
                additional_context=additional_context,
                reasoning_enabled=use_reasoning,
                reasoning_results=reasoning_result if reasoning_result else None,
                processing_time=processing_time,
                pipeline_version="v1.0-reasoning"
            )

            db.add(diagnosis)
            db.commit()
            db.refresh(diagnosis)

            return {
                "cached": False,
                "diagnosis": diagnosis,
                "processing_time": processing_time
            }

        except Exception as e:
            raise ModelInferenceException(str(e))


diagnosis_service = DiagnosisService()

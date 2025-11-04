from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Top3Prediction(BaseModel):
    class_name: str = Field(..., alias="class")
    name_ru: str
    confidence: float

class CVResult(BaseModel):
    predicted_class: str
    disease_name: str
    confidence: float
    top3_predictions: List[Top3Prediction]

class ImageAnalysis(BaseModel):
    is_plant: bool
    green_pixel_ratio: float
    green_threshold: float
    mean_saturation: float
    mean_value: float

class ReasoningAnalysis(BaseModel):
    diagnosis_confirmation: Optional[str] = None
    disease_stage: Optional[str] = None
    causes: Optional[List[str]] = None
    risk_factors: Optional[List[str]] = None
    spread_forecast: Optional[str] = None
    treatment_plan: Optional[str] = None
    prevention: Optional[str] = None
    regional_recommendations: Optional[str] = None
    timeline: Optional[str] = None
    success_probability: Optional[str] = None
    raw_response: Optional[str] = None
    parsed: bool = True

class DiagnosisResponse(BaseModel):
    pipeline_version: str
    cv_result: Optional[CVResult] = None
    reasoning_analysis: Optional[Dict[str, Any]] = None
    report: str
    image_analysis: Optional[ImageAnalysis] = None

class DiagnosisRequest(BaseModel):
    region: Optional[str] = None
    climate: Optional[str] = None
    plant_age: Optional[int] = None
    additional_context: Optional[str] = None
    use_reasoning: bool = True
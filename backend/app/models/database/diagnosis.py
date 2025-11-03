from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Image info
    image_path = Column(String, nullable=False)
    image_hash = Column(String, index=True)

    # CV Results
    predicted_class = Column(String, nullable=False)
    disease_name = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    cv_results = Column(JSON)  # Top predictions, probabilities

    # Context
    region = Column(String)
    climate = Column(String)
    plant_age = Column(Integer)
    additional_context = Column(Text)

    # Reasoning Results
    reasoning_enabled = Column(Boolean, default=True)
    reasoning_results = Column(JSON)  # Full reasoning analysis

    # Metadata
    processing_time = Column(Float)  # seconds
    pipeline_version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="diagnoses")
    feedback = relationship("Feedback", back_populates="diagnosis", uselist=False)

    def __repr__(self):
        return f"<Diagnosis {self.id}: {self.disease_name}>"
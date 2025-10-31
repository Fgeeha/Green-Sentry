from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base


class FeedbackType(str, enum.Enum):
    ACCURATE = "accurate"
    INACCURATE = "inaccurate"
    PARTIAL = "partial"


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    diagnosis_id = Column(Integer, ForeignKey("diagnoses.id"), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    feedback_type = Column(Enum(FeedbackType), nullable=False)
    rating = Column(Integer)  # 1-5
    comment = Column(Text)
    correct_disease = Column(String)  # If diagnosis was wrong

    is_reviewed = Column(Boolean, default=False)
    reviewed_at = Column(DateTime)
    reviewer_notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    diagnosis = relationship("Diagnosis", back_populates="feedback")
    user = relationship("User", back_populates="feedbacks")

    def __repr__(self):
        return f""

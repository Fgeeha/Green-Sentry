from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models here for Alembic
from app.models.database.user import User  # noqa
from app.models.database.diagnosis import Diagnosis  # noqa
from app.models.database.feedback import Feedback  # noqa
import factory
from factory.alchemy import SQLAlchemyModelFactory
from app.models.database.user import User, UserRole
from app.models.database.diagnosis import Diagnosis
from app.core.security import get_password_hash


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    email = factory.Faker("email")
    username = factory.Faker("user_name")
    hashed_password = factory.LazyFunction(lambda: get_password_hash("testpass123"))
    full_name = factory.Faker("name")
    role = UserRole.USER
    is_active = True
    is_verified = True


class DiagnosisFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Diagnosis
        sqlalchemy_session_persistence = "commit"

    user_id = factory.SelfAttribute("user.id")
    user = factory.SubFactory(UserFactory)
    image_path = factory.Faker("file_path", extension="jpg")
    predicted_class = "powdery_mildew_tomato"
    disease_name = "Мучнистая роса томатов"
    confidence = factory.Faker("pyfloat", left_digits=0, right_digits=2, positive=True, max_value=1)
    cv_results = factory.LazyFunction(lambda: {})
    reasoning_enabled = True
    reasoning_results = factory.LazyFunction(lambda: {})
    processing_time = factory.Faker("pyfloat", left_digits=1, right_digits=2, positive=True)
    pipeline_version = "v1.0-reasoning"
from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Base exception for API"""
    def __init__(self, detail: str):
        super().__init__(status_code=self.status_code, detail=detail)


class NotFoundException(BaseAPIException):
    status_code = status.HTTP_404_NOT_FOUND


class BadRequestException(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST


class UnauthorizedException(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED


class ForbiddenException(BaseAPIException):
    status_code = status.HTTP_403_FORBIDDEN


class ConflictException(BaseAPIException):
    status_code = status.HTTP_409_CONFLICT


class ValidationException(BaseAPIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class InternalServerException(BaseAPIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


# Specific exceptions
class DiagnosisNotFoundException(NotFoundException):
    def __init__(self, diagnosis_id: int):
        super().__init__(f"Diagnosis with id {diagnosis_id} not found")


class UserNotFoundException(NotFoundException):
    def __init__(self, user_id: int):
        super().__init__(f"User with id {user_id} not found")


class InvalidCredentialsException(UnauthorizedException):
    def __init__(self):
        super().__init__("Invalid credentials")


class InvalidTokenException(UnauthorizedException):
    def __init__(self):
        super().__init__("Invalid or expired token")


class ImageProcessingException(BadRequestException):
    def __init__(self, detail: str):
        super().__init__(f"Image processing error: {detail}")


class ModelInferenceException(InternalServerException):
    def __init__(self, detail: str):
        super().__init__(f"Model inference error: {detail}")


class ReasoningException(InternalServerException):
    def __init__(self, detail: str):
        super().__init__(f"Reasoning error: {detail}")
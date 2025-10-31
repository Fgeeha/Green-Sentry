from pydantic import BaseModel
from typing import Optional, Generic, TypeVar, List
from datetime import datetime

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = 0
    limit: int = 100


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response"""
    items: List[T]
    total: int
    skip: int
    limit: int
    has_more: bool


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime
    database: bool
    cache: bool
    ml_model: bool
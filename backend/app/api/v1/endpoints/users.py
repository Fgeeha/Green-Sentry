from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_current_user, get_current_admin_user
from app.db.session import get_db
from app.models.database.user import User
from app.repositories.user import user_repository
from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.core.security import get_password_hash

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
        current_user: User = Depends(get_current_user)
):
    """Get current user info"""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user(
        user_update: UserUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Update current user"""
    return user_repository.update(db, db_obj=current_user, obj_in=user_update)


@router.get("/", response_model=List[UserResponse])
def get_users(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_admin_user)
):
    """Get all users (admin only)"""
    return user_repository.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
        user_in: UserCreate,
        db: Session = Depends(get_db)
):
    """Create new user"""
    # Check if user exists
    if user_repository.get_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )

    if user_repository.get_by_username(db, username=user_in.username):
        raise HTTPException(
            status_code=400,
            detail="User with this username already exists"
        )

    return user_repository.create(db, obj_in=user_in)
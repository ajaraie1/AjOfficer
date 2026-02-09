from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.auth.models import UserModel
from app.auth.schemas import UserCreate
from app.auth.jwt import get_password_hash, verify_password


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[UserModel]:
    """Get a user by email."""
    result = await db.execute(select(UserModel).where(UserModel.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[UserModel]:
    """Get a user by ID."""
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_data: UserCreate) -> UserModel:
    """Create a new user."""
    # Check if user exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = UserModel(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password)
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[UserModel]:
    """Authenticate a user by email and password."""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

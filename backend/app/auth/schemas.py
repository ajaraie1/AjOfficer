from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class User(UserBase):
    """User response schema."""
    id: str
    created_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT Token response schema."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    user_id: Optional[str] = None
    email: Optional[str] = None

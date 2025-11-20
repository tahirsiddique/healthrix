"""
User Schemas
============

Pydantic schemas for user-related API operations.
"""

from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field
from ..models.user import UserRole


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    department: Optional[str] = Field(None, max_length=100)
    role: UserRole = UserRole.EMPLOYEE


class UserCreate(UserBase):
    """Schema for creating a new user."""
    emp_id: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=8)
    hire_date: Optional[date] = None


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    department: Optional[str] = Field(None, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    """Schema for user responses."""
    emp_id: str
    is_active: bool
    hire_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for token payload."""
    sub: Optional[str] = None
    exp: Optional[int] = None

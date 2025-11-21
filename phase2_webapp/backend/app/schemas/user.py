"""
User Schemas
============

Pydantic schemas for user-related API operations.
"""

from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field, validator
from ..models.user import UserRole


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    department: Optional[str] = Field(None, max_length=100)
    department_id: Optional[int] = None
    role: UserRole = UserRole.EMPLOYEE


class UserCreate(UserBase):
    """Schema for creating a new user."""
    emp_id: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    hire_date: Optional[date] = None
    is_active: bool = True

    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    department: Optional[str] = Field(None, max_length=100)
    department_id: Optional[int] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    hire_date: Optional[date] = None


class UserResponse(UserBase):
    """Schema for user responses."""
    emp_id: str
    is_active: bool
    hire_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for paginated user list response."""
    users: List[UserResponse]
    total: int
    skip: int
    limit: int


class PasswordChange(BaseModel):
    """Schema for password change."""
    old_password: Optional[str] = Field(None, description="Required when changing own password")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")

    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v


class UserActivation(BaseModel):
    """Schema for user activation/deactivation."""
    is_active: bool


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

"""
Department Schemas
==================

Pydantic schemas for department-related API operations.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class DepartmentBase(BaseModel):
    """Base department schema with common fields."""
    dept_code: str = Field(..., min_length=1, max_length=20, description="Unique department code")
    dept_name: str = Field(..., min_length=1, max_length=255, description="Department name")
    description: Optional[str] = Field(None, max_length=500)


class DepartmentCreate(DepartmentBase):
    """Schema for creating a new department."""
    manager_emp_id: Optional[str] = Field(None, description="Employee ID of department head")
    is_active: bool = True


class DepartmentUpdate(BaseModel):
    """Schema for updating department information."""
    dept_code: Optional[str] = Field(None, min_length=1, max_length=20)
    dept_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    manager_emp_id: Optional[str] = None
    is_active: Optional[bool] = None


class DepartmentResponse(DepartmentBase):
    """Schema for department responses."""
    id: int
    manager_emp_id: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DepartmentWithManagerResponse(DepartmentResponse):
    """Schema for department response with manager details."""
    manager_name: Optional[str] = None
    employee_count: Optional[int] = 0


class DepartmentListResponse(BaseModel):
    """Schema for paginated department list response."""
    departments: List[DepartmentWithManagerResponse]
    total: int
    skip: int
    limit: int

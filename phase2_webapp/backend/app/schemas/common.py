"""
Common Schemas
==============

Pydantic schemas for task standards, activities, metrics, and performance.
"""

from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, Field


# ============================================================================
# Task Standard Schemas
# ============================================================================

class TaskStandardBase(BaseModel):
    """Base task standard schema."""
    task_name: str = Field(..., min_length=1, max_length=255)
    ec_category: str = Field(..., pattern="^EC-[1-5]$")
    base_score: int = Field(..., gt=0)
    target_daily: int = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=500)


class TaskStandardCreate(TaskStandardBase):
    """Schema for creating a task standard."""
    task_id: str = Field(..., min_length=1, max_length=50)


class TaskStandardUpdate(BaseModel):
    """Schema for updating a task standard."""
    task_name: Optional[str] = Field(None, min_length=1, max_length=255)
    ec_category: Optional[str] = Field(None, pattern="^EC-[1-5]$")
    base_score: Optional[int] = Field(None, gt=0)
    target_daily: Optional[int] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=500)


class TaskStandardResponse(TaskStandardBase):
    """Schema for task standard responses."""
    task_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Activity Schemas
# ============================================================================

class ActivityBase(BaseModel):
    """Base activity schema."""
    date: date
    task_id: str
    count: int = Field(1, gt=0)
    patient_id: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    notes: Optional[str] = None


class ActivityCreate(ActivityBase):
    """Schema for creating an activity."""
    emp_id: Optional[str] = None  # Will be set from token if not provided


class ActivityUpdate(BaseModel):
    """Schema for updating an activity."""
    date: Optional[date] = None
    task_id: Optional[str] = None
    count: Optional[int] = Field(None, gt=0)
    patient_id: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    notes: Optional[str] = None


class ActivityResponse(ActivityBase):
    """Schema for activity responses."""
    activity_id: str
    emp_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Daily Metric Schemas
# ============================================================================

class DailyMetricBase(BaseModel):
    """Base daily metric schema."""
    date: date
    idle_hours: float = Field(0.0, ge=0, le=24)
    conduct_flag: int = Field(0, ge=0, le=1)
    conduct_notes: Optional[str] = None
    supervisor: Optional[str] = None


class DailyMetricCreate(DailyMetricBase):
    """Schema for creating a daily metric."""
    emp_id: str


class DailyMetricUpdate(BaseModel):
    """Schema for updating a daily metric."""
    idle_hours: Optional[float] = Field(None, ge=0, le=24)
    conduct_flag: Optional[int] = Field(None, ge=0, le=1)
    conduct_notes: Optional[str] = None
    supervisor: Optional[str] = None


class DailyMetricResponse(DailyMetricBase):
    """Schema for daily metric responses."""
    metric_id: str
    emp_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Performance Score Schemas
# ============================================================================

class PerformanceScoreResponse(BaseModel):
    """Schema for performance score responses."""
    score_id: str
    date: date
    emp_id: str
    total_task_points: float
    productivity_percent: float
    weighted_prod_score: float
    behavior_score_raw: float
    weighted_behavior_score: float
    final_performance_percent: float
    task_count: int
    idle_hours: float
    conduct_flag: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PerformanceCalculationRequest(BaseModel):
    """Schema for performance calculation request."""
    date: date
    emp_id: Optional[str] = None  # If None, calculate for all employees


class PerformanceTrendResponse(BaseModel):
    """Schema for performance trend response."""
    emp_id: str
    employee_name: str
    start_date: date
    end_date: date
    scores: list[PerformanceScoreResponse]
    avg_performance: float
    trend: str  # "improving", "declining", "stable"

"""
API Schemas
===========

Pydantic schemas for request validation and response serialization.
"""

from .user import UserCreate, UserUpdate, UserResponse, UserLogin, Token
from .task_standard import TaskStandardCreate, TaskStandardUpdate, TaskStandardResponse
from .activity import ActivityCreate, ActivityUpdate, ActivityResponse
from .daily_metric import DailyMetricCreate, DailyMetricUpdate, DailyMetricResponse
from .performance import PerformanceScoreResponse, PerformanceCalculationRequest

__all__ = [
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "Token",
    # Task Standard schemas
    "TaskStandardCreate",
    "TaskStandardUpdate",
    "TaskStandardResponse",
    # Activity schemas
    "ActivityCreate",
    "ActivityUpdate",
    "ActivityResponse",
    # Daily Metric schemas
    "DailyMetricCreate",
    "DailyMetricUpdate",
    "DailyMetricResponse",
    # Performance schemas
    "PerformanceScoreResponse",
    "PerformanceCalculationRequest",
]

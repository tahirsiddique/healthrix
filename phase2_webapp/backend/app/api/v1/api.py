"""
API Router
==========

Main API router that includes all endpoint routers.
"""

from fastapi import APIRouter

from .endpoints import auth, users, departments, activities, performance

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["user-management"])
api_router.include_router(departments.router, prefix="/departments", tags=["department-management"])
api_router.include_router(activities.router, prefix="/activities", tags=["activities"])
api_router.include_router(performance.router, prefix="/performance", tags=["performance"])

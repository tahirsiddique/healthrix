"""
API Router
==========

Main API router that includes all endpoint routers.
"""

from fastapi import APIRouter

from .endpoints import auth, activities, performance

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(activities.router, prefix="/activities", tags=["activities"])
api_router.include_router(performance.router, prefix="/performance", tags=["performance"])

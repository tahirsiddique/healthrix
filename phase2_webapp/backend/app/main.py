"""
Main FastAPI Application
=========================

Entry point for the Healthrix Productivity System API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings
from .api.v1.api import api_router
from .db.session import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    **Healthrix Productivity System API**

    A comprehensive performance tracking and analytics system for healthcare operations.

    ## Features

    * **Activity Tracking**: Log daily tasks and completions
    * **Performance Calculation**: Automated 90% Productivity + 10% Behavior scoring
    * **Analytics**: Trends, leaderboards, and team statistics
    * **Role-Based Access**: Employee, Supervisor, and Admin roles
    * **RESTful API**: Full CRUD operations with authentication

    ## Authentication

    All endpoints except registration and login require authentication.
    Use the `/api/v1/auth/login` endpoint to obtain an access token.

    Include the token in the Authorization header:
    ```
    Authorization: Bearer <your_access_token>
    ```

    ## Performance Formula

    **Final Performance = (Productivity × 0.90) + (Behavior × 0.10)**

    - **Productivity**: (Total Points / 400) × 100
    - **Behavior**: 100 - (Idle Hours × 10) - (Conduct Flag × 50)
    """,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "api": settings.API_V1_PREFIX,
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )

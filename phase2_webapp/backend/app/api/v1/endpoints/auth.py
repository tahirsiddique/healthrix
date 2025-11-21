"""
Authentication Endpoints
========================

Login, registration, and token management.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ....db.session import get_db
from ....core import security
from ....core.config import settings
from ....models.user import User
from ....schemas.user import UserCreate, UserResponse, Token, UserLogin

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Creates a new employee account with hashed password.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    existing_emp = db.query(User).filter(User.emp_id == user_in.emp_id).first()
    if existing_emp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID already exists"
        )

    # Create new user
    hashed_password = security.get_password_hash(user_in.password)
    user = User(
        emp_id=user_in.emp_id,
        email=user_in.email,
        hashed_password=hashed_password,
        name=user_in.name,
        department=user_in.department,
        role=user_in.role,
        hire_date=user_in.hire_date,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login.

    Get an access token for future requests.
    """
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    access_token = security.create_access_token(
        data={"sub": user.email}
    )
    refresh_token = security.create_refresh_token(
        data={"sub": user.email}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(security.get_current_active_user)
):
    """
    Get current user information.

    Returns the authenticated user's profile.
    """
    return current_user

"""
User Management API Endpoints
==============================

Complete CRUD operations for user management with role-based access control.
"""

from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ....db.session import get_db
from ....models import User, UserRole, Department
from ....schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserListResponse,
    PasswordChange, UserActivation
)
from ....core import security
from ....core.permissions import PermissionChecker, Permission
from ....core.security import get_password_hash


router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    Create a new user.

    **Required Permissions:**
    - USER_CREATE

    **Additional Rules:**
    - ADMIN cannot create SUPER_ADMIN users
    - HR can only create EMPLOYEE and DEPARTMENT_HEAD users
    """
    # Check permission
    PermissionChecker.require_permission(current_user.role, Permission.USER_CREATE)

    # Check if manager can create user with this role
    if not PermissionChecker.can_manage_user_role(current_user.role, user_data.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You cannot create users with role: {user_data.role.value}"
        )

    # Check if emp_id already exists
    existing_user = db.query(User).filter(User.emp_id == user_data.emp_id).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee ID {user_data.emp_id} already exists"
        )

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {user_data.email} already exists"
        )

    # Verify department exists if provided
    if user_data.department_id:
        dept = db.query(Department).filter(Department.id == user_data.department_id).first()
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department with ID {user_data.department_id} not found"
            )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        emp_id=user_data.emp_id,
        email=user_data.email,
        hashed_password=hashed_password,
        name=user_data.name,
        department=user_data.department,
        department_id=user_data.department_id,
        role=user_data.role,
        is_active=user_data.is_active,
        hire_date=user_data.hire_date,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/", response_model=UserListResponse)
def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    department_id: Optional[int] = Query(None, description="Filter by department"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by name, email, or emp_id"),
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    List users with filtering and pagination.

    **Permissions:**
    - SUPER_ADMIN/ADMIN/HR: Can view all users
    - DEPARTMENT_HEAD: Can view users in their department
    - EMPLOYEE: Can only view own profile (redirected to /me endpoint)
    """
    # Build base query
    query = db.query(User)

    # Apply role-based filtering
    if current_user.role == UserRole.EMPLOYEE:
        # Employees can only view themselves
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employees can only view their own profile. Use /users/me endpoint."
        )
    elif current_user.role == UserRole.DEPARTMENT_HEAD:
        # Department heads can only view their department
        if not current_user.department_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department head must be assigned to a department"
            )
        query = query.filter(User.department_id == current_user.department_id)

    # Apply filters
    if role:
        query = query.filter(User.role == role)
    if department_id:
        query = query.filter(User.department_id == department_id)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                User.name.ilike(search_pattern),
                User.email.ilike(search_pattern),
                User.emp_id.ilike(search_pattern)
            )
        )

    # Get total count
    total = query.count()

    # Apply pagination
    users = query.offset(skip).limit(limit).all()

    return {
        "users": users,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(security.get_current_user)):
    """
    Get current user's profile.

    **Permissions:** Any authenticated user
    """
    return current_user


@router.get("/{emp_id}", response_model=UserResponse)
def get_user(
    emp_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    Get user by employee ID.

    **Permissions:**
    - User can view own profile
    - SUPER_ADMIN/ADMIN/HR can view any user
    - DEPARTMENT_HEAD can view users in their department
    """
    user = db.query(User).filter(User.emp_id == emp_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with employee ID {emp_id} not found"
        )

    # Check if current user can access this user's data
    if not PermissionChecker.can_access_user_data(
        viewer_role=current_user.role,
        viewer_emp_id=current_user.emp_id,
        viewer_dept_id=current_user.department_id,
        target_emp_id=user.emp_id,
        target_dept_id=user.department_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this user"
        )

    return user


@router.put("/{emp_id}", response_model=UserResponse)
def update_user(
    emp_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    Update user information.

    **Required Permissions:**
    - USER_UPDATE

    **Additional Rules:**
    - Cannot change own role
    - Role changes require USER_CHANGE_ROLE permission
    - ADMIN cannot promote users to SUPER_ADMIN
    """
    # Check permission
    PermissionChecker.require_permission(current_user.role, Permission.USER_UPDATE)

    # Get user to update
    user = db.query(User).filter(User.emp_id == emp_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with employee ID {emp_id} not found"
        )

    # Check if user can access this user's data
    if not PermissionChecker.can_access_user_data(
        viewer_role=current_user.role,
        viewer_emp_id=current_user.emp_id,
        viewer_dept_id=current_user.department_id,
        target_emp_id=user.emp_id,
        target_dept_id=user.department_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this user"
        )

    # Handle role change
    if user_data.role is not None and user_data.role != user.role:
        # Cannot change own role
        if user.emp_id == current_user.emp_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot change your own role"
            )

        # Check if manager can assign this role
        if not PermissionChecker.can_manage_user_role(current_user.role, user_data.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You cannot assign role: {user_data.role.value}"
            )

    # Check email uniqueness if being changed
    if user_data.email and user_data.email != user.email:
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email {user_data.email} already exists"
            )

    # Verify department exists if being changed
    if user_data.department_id and user_data.department_id != user.department_id:
        dept = db.query(Department).filter(Department.id == user_data.department_id).first()
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department with ID {user_data.department_id} not found"
            )

    # Update fields
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    return user


@router.post("/{emp_id}/change-password", response_model=dict)
def change_user_password(
    emp_id: str,
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    Change user password.

    **Permissions:**
    - User can change own password (with old password verification)
    - SUPER_ADMIN/ADMIN can change any user's password (no old password required)
    """
    user = db.query(User).filter(User.emp_id == emp_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with employee ID {emp_id} not found"
        )

    # If changing own password, verify old password
    if user.emp_id == current_user.emp_id:
        if not password_data.old_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Old password is required to change your own password"
            )
        if not security.verify_password(password_data.old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect old password"
            )
    else:
        # Changing another user's password requires admin permissions
        PermissionChecker.require_any_permission(
            current_user.role,
            [Permission.USER_UPDATE]
        )

    # Update password
    user.hashed_password = get_password_hash(password_data.new_password)
    user.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Password changed successfully"}


@router.post("/{emp_id}/activate", response_model=UserResponse)
def activate_user(
    emp_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    Activate a user account.

    **Required Permissions:** USER_ACTIVATE
    """
    PermissionChecker.require_permission(current_user.role, Permission.USER_ACTIVATE)

    user = db.query(User).filter(User.emp_id == emp_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with employee ID {emp_id} not found"
        )

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already active"
        )

    user.is_active = True
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    return user


@router.post("/{emp_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    emp_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    Deactivate a user account.

    **Required Permissions:** USER_DEACTIVATE

    **Rules:**
    - Cannot deactivate own account
    - Cannot deactivate super admin accounts (unless you are a super admin)
    """
    PermissionChecker.require_permission(current_user.role, Permission.USER_DEACTIVATE)

    user = db.query(User).filter(User.emp_id == emp_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with employee ID {emp_id} not found"
        )

    # Cannot deactivate own account
    if user.emp_id == current_user.emp_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot deactivate your own account"
        )

    # Only super admin can deactivate other super admins
    if user.role == UserRole.SUPER_ADMIN and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can deactivate other super admin accounts"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already inactive"
        )

    user.is_active = False
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    return user


@router.delete("/{emp_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    emp_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    Delete a user permanently.

    **Required Permissions:** USER_DELETE

    **Rules:**
    - Cannot delete own account
    - Cannot delete super admin accounts (unless you are a super admin)
    - This will cascade delete all associated data (activities, metrics, performance scores)
    """
    PermissionChecker.require_permission(current_user.role, Permission.USER_DELETE)

    user = db.query(User).filter(User.emp_id == emp_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with employee ID {emp_id} not found"
        )

    # Cannot delete own account
    if user.emp_id == current_user.emp_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot delete your own account"
        )

    # Only super admin can delete other super admins
    if user.role == UserRole.SUPER_ADMIN and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can delete other super admin accounts"
        )

    db.delete(user)
    db.commit()

    return None

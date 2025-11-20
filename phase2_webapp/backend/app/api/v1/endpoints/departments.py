"""
Department Management API Endpoints
====================================

CRUD operations for department management with role-based access control.
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from ....db.session import get_db
from ....models import Department, User, UserRole
from ....schemas.department import (
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    DepartmentWithManagerResponse, DepartmentListResponse
)
from ....core import security
from ....core.permissions import PermissionChecker, Permission


router = APIRouter()


@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    dept_data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    Create a new department.

    **Required Permissions:** DEPT_CREATE
    """
    PermissionChecker.require_permission(current_user.role, Permission.DEPT_CREATE)

    # Check if dept_code already exists
    existing = db.query(Department).filter(Department.dept_code == dept_data.dept_code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department code {dept_data.dept_code} already exists"
        )

    # Verify manager exists if provided
    if dept_data.manager_emp_id:
        manager = db.query(User).filter(User.emp_id == dept_data.manager_emp_id).first()
        if not manager:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Manager with employee ID {dept_data.manager_emp_id} not found"
            )

    # Create new department
    new_dept = Department(
        dept_code=dept_data.dept_code,
        dept_name=dept_data.dept_name,
        description=dept_data.description,
        manager_emp_id=dept_data.manager_emp_id,
        is_active=dept_data.is_active,
    )

    db.add(new_dept)
    db.commit()
    db.refresh(new_dept)

    return new_dept


@router.get("/", response_model=DepartmentListResponse)
def list_departments(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by code, name, or description"),
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    List departments with filtering and pagination.

    **Required Permissions:** DEPT_READ
    """
    PermissionChecker.require_permission(current_user.role, Permission.DEPT_READ)

    # Build base query
    query = db.query(Department)

    # Apply filters
    if is_active is not None:
        query = query.filter(Department.is_active == is_active)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Department.dept_code.ilike(search_pattern),
                Department.dept_name.ilike(search_pattern),
                Department.description.ilike(search_pattern)
            )
        )

    # Get total count
    total = query.count()

    # Apply pagination
    departments = query.offset(skip).limit(limit).all()

    # Enrich with manager info and employee count
    dept_list = []
    for dept in departments:
        dept_dict = {
            "id": dept.id,
            "dept_code": dept.dept_code,
            "dept_name": dept.dept_name,
            "description": dept.description,
            "manager_emp_id": dept.manager_emp_id,
            "is_active": dept.is_active,
            "created_at": dept.created_at,
            "updated_at": dept.updated_at,
            "manager_name": dept.manager.name if dept.manager else None,
            "employee_count": db.query(func.count(User.emp_id))\
                .filter(User.department_id == dept.id).scalar()
        }
        dept_list.append(DepartmentWithManagerResponse(**dept_dict))

    return {
        "departments": dept_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{dept_id}", response_model=DepartmentWithManagerResponse)
def get_department(
    dept_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    Get department by ID.

    **Required Permissions:** DEPT_READ
    """
    PermissionChecker.require_permission(current_user.role, Permission.DEPT_READ)

    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID {dept_id} not found"
        )

    # Build response with manager info
    dept_dict = {
        "id": dept.id,
        "dept_code": dept.dept_code,
        "dept_name": dept.dept_name,
        "description": dept.description,
        "manager_emp_id": dept.manager_emp_id,
        "is_active": dept.is_active,
        "created_at": dept.created_at,
        "updated_at": dept.updated_at,
        "manager_name": dept.manager.name if dept.manager else None,
        "employee_count": db.query(func.count(User.emp_id))\
            .filter(User.department_id == dept.id).scalar()
    }

    return DepartmentWithManagerResponse(**dept_dict)


@router.put("/{dept_id}", response_model=DepartmentResponse)
def update_department(
    dept_id: int,
    dept_data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    Update department information.

    **Required Permissions:** DEPT_UPDATE
    """
    PermissionChecker.require_permission(current_user.role, Permission.DEPT_UPDATE)

    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID {dept_id} not found"
        )

    # Check dept_code uniqueness if being changed
    if dept_data.dept_code and dept_data.dept_code != dept.dept_code:
        existing = db.query(Department).filter(
            Department.dept_code == dept_data.dept_code
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Department code {dept_data.dept_code} already exists"
            )

    # Verify manager exists if being changed
    if dept_data.manager_emp_id:
        manager = db.query(User).filter(User.emp_id == dept_data.manager_emp_id).first()
        if not manager:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Manager with employee ID {dept_data.manager_emp_id} not found"
            )

    # Update fields
    update_data = dept_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dept, field, value)

    dept.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(dept)

    return dept


@router.post("/{dept_id}/assign-manager", response_model=DepartmentResponse)
def assign_department_manager(
    dept_id: int,
    manager_emp_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    Assign a manager to a department.

    **Required Permissions:** DEPT_ASSIGN_MANAGER

    **Additional Actions:**
    - Automatically updates the user's role to DEPARTMENT_HEAD if not already higher
    """
    PermissionChecker.require_permission(current_user.role, Permission.DEPT_ASSIGN_MANAGER)

    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID {dept_id} not found"
        )

    manager = db.query(User).filter(User.emp_id == manager_emp_id).first()
    if not manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with employee ID {manager_emp_id} not found"
        )

    # Assign manager
    dept.manager_emp_id = manager_emp_id
    dept.updated_at = datetime.utcnow()

    # Promote user to department head if they're currently an employee
    if manager.role == UserRole.EMPLOYEE:
        manager.role = UserRole.DEPARTMENT_HEAD
        manager.updated_at = datetime.utcnow()

    # Assign user to this department if not already assigned
    if not manager.department_id:
        manager.department_id = dept_id

    db.commit()
    db.refresh(dept)

    return dept


@router.delete("/{dept_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    dept_id: int,
    force: bool = Query(False, description="Force delete even if department has employees"),
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_user)
):
    """
    Delete a department.

    **Required Permissions:** DEPT_DELETE

    **Rules:**
    - Cannot delete department with active employees unless force=true
    - Force delete will unassign all employees from the department
    """
    PermissionChecker.require_permission(current_user.role, Permission.DEPT_DELETE)

    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID {dept_id} not found"
        )

    # Check for employees
    employee_count = db.query(func.count(User.emp_id))\
        .filter(User.department_id == dept_id).scalar()

    if employee_count > 0 and not force:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department has {employee_count} employees. Use force=true to delete anyway."
        )

    # Unassign all employees if force delete
    if force and employee_count > 0:
        db.query(User).filter(User.department_id == dept_id)\
            .update({"department_id": None}, synchronize_session=False)

    db.delete(dept)
    db.commit()

    return None

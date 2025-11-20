"""
Activity Endpoints
==================

CRUD operations for employee activities.
"""

from typing import List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import uuid

from ....db.session import get_db
from ....core import security
from ....models.user import User
from ....models.activity import Activity
from ....schemas.common import ActivityCreate, ActivityUpdate, ActivityResponse

router = APIRouter()


@router.post("/", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    activity_in: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_active_user)
):
    """
    Create a new activity.

    Employees can only create activities for themselves.
    Supervisors can create for any employee.
    """
    # If emp_id not provided, use current user's ID
    emp_id = activity_in.emp_id or current_user.emp_id

    # Check permissions
    if current_user.role == "employee" and emp_id != current_user.emp_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employees can only log their own activities"
        )

    # Create activity
    activity = Activity(
        activity_id=str(uuid.uuid4()),
        emp_id=emp_id,
        date=activity_in.date,
        task_id=activity_in.task_id,
        count=activity_in.count,
        patient_id=activity_in.patient_id,
        duration_minutes=activity_in.duration_minutes,
        notes=activity_in.notes,
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)

    return activity


@router.get("/", response_model=List[ActivityResponse])
def list_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    emp_id: str = None,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_active_user)
):
    """
    List activities with optional filters.

    Employees can only see their own activities.
    Supervisors can see all activities.
    """
    query = db.query(Activity)

    # Apply role-based filtering
    if current_user.role == "employee":
        query = query.filter(Activity.emp_id == current_user.emp_id)
    elif emp_id:
        query = query.filter(Activity.emp_id == emp_id)

    # Apply date filters
    if start_date:
        query = query.filter(Activity.date >= start_date)
    if end_date:
        query = query.filter(Activity.date <= end_date)

    activities = query.order_by(Activity.date.desc()).offset(skip).limit(limit).all()

    return activities


@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(
    activity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_active_user)
):
    """Get a specific activity by ID."""
    activity = db.query(Activity).filter(Activity.activity_id == activity_id).first()

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )

    # Check permissions
    if current_user.role == "employee" and activity.emp_id != current_user.emp_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this activity"
        )

    return activity


@router.put("/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: str,
    activity_in: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_active_user)
):
    """Update an activity."""
    activity = db.query(Activity).filter(Activity.activity_id == activity_id).first()

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )

    # Check permissions
    if current_user.role == "employee" and activity.emp_id != current_user.emp_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this activity"
        )

    # Update fields
    update_data = activity_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(activity, field, value)

    db.commit()
    db.refresh(activity)

    return activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    activity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_active_user)
):
    """Delete an activity."""
    activity = db.query(Activity).filter(Activity.activity_id == activity_id).first()

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )

    # Check permissions
    if current_user.role == "employee" and activity.emp_id != current_user.emp_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this activity"
        )

    db.delete(activity)
    db.commit()

    return None

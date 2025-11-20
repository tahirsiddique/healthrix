"""
Performance Endpoints
=====================

Performance calculation, viewing, and analytics.
"""

from typing import List
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ....db.session import get_db
from ....core import security
from ....models.user import User
from ....models.performance_score import PerformanceScore
from ....schemas.common import (
    PerformanceScoreResponse,
    PerformanceCalculationRequest,
)
from ....services.performance_calculator import PerformanceCalculatorService

router = APIRouter()


@router.post("/calculate", response_model=List[PerformanceScoreResponse])
def calculate_performance(
    request: PerformanceCalculationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_supervisor)
):
    """
    Calculate performance scores.

    Only supervisors and admins can trigger calculations.
    If emp_id is provided, calculates for that employee only.
    Otherwise, calculates for all employees with activities on the specified date.
    """
    calculator = PerformanceCalculatorService(db)

    if request.emp_id:
        # Calculate for specific employee
        score = calculator.calculate_for_employee(request.emp_id, request.date)
        if not score:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No activities found for employee {request.emp_id} on {request.date}"
            )
        return [score]
    else:
        # Calculate for all employees
        scores = calculator.calculate_for_all_employees(request.date)
        if not scores:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No activities found for any employee on {request.date}"
            )
        return scores


@router.get("/scores", response_model=List[PerformanceScoreResponse])
def list_performance_scores(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    emp_id: str = None,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_active_user)
):
    """
    List performance scores with optional filters.

    Employees can only see their own scores.
    Supervisors can see all scores.
    """
    query = db.query(PerformanceScore)

    # Apply role-based filtering
    if current_user.role == "employee":
        query = query.filter(PerformanceScore.emp_id == current_user.emp_id)
    elif emp_id:
        query = query.filter(PerformanceScore.emp_id == emp_id)

    # Apply date filters
    if start_date:
        query = query.filter(PerformanceScore.date >= start_date)
    if end_date:
        query = query.filter(PerformanceScore.date <= end_date)

    scores = query.order_by(PerformanceScore.date.desc()).offset(skip).limit(limit).all()

    return scores


@router.get("/trend/{emp_id}", response_model=List[PerformanceScoreResponse])
def get_performance_trend(
    emp_id: str,
    start_date: date = Query(..., description="Start date for trend"),
    end_date: date = Query(..., description="End date for trend"),
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_active_user)
):
    """
    Get performance trend for an employee over a date range.

    Employees can only view their own trend.
    Supervisors can view any employee's trend.
    """
    # Check permissions
    if current_user.role == "employee" and emp_id != current_user.emp_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this employee's trend"
        )

    calculator = PerformanceCalculatorService(db)
    scores = calculator.get_employee_trend(emp_id, start_date, end_date)

    if not scores:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No performance data found for employee {emp_id} in the specified date range"
        )

    return scores


@router.get("/leaderboard", response_model=List[PerformanceScoreResponse])
def get_leaderboard(
    target_date: date = Query(None, description="Date for leaderboard (default: yesterday)"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_supervisor)
):
    """
    Get top performers leaderboard for a specific date.

    Only supervisors and admins can access the leaderboard.
    Defaults to yesterday's performance if no date provided.
    """
    if not target_date:
        target_date = date.today() - timedelta(days=1)

    calculator = PerformanceCalculatorService(db)
    scores = calculator.get_team_leaderboard(target_date, limit)

    if not scores:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No performance data found for {target_date}"
        )

    return scores


@router.get("/statistics")
def get_statistics(
    target_date: date = Query(None, description="Date for statistics (default: yesterday)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_supervisor)
):
    """
    Get aggregate performance statistics for a specific date.

    Only supervisors and admins can access statistics.
    Returns team-wide metrics: averages, top/bottom performers, etc.
    """
    if not target_date:
        target_date = date.today() - timedelta(days=1)

    calculator = PerformanceCalculatorService(db)
    stats = calculator.get_statistics(target_date)

    return stats


@router.get("/my-latest", response_model=PerformanceScoreResponse)
def get_my_latest_score(
    db: Session = Depends(get_db),
    current_user: User = Depends(security.get_current_active_user)
):
    """
    Get the latest performance score for the current user.

    Returns the most recent performance score.
    """
    score = (
        db.query(PerformanceScore)
        .filter(PerformanceScore.emp_id == current_user.emp_id)
        .order_by(PerformanceScore.date.desc())
        .first()
    )

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No performance scores found. Activities need to be logged first."
        )

    return score

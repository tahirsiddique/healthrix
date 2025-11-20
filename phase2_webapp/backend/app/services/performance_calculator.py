"""
Performance Calculator Service
===============================

Business logic for calculating employee performance scores.
Integrates with the healthrix_automation engine.
"""

from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid

from ..models import User, Activity, DailyMetric, PerformanceScore, TaskStandard
from ..core.config import settings


class PerformanceCalculatorService:
    """
    Service for calculating employee performance scores.

    Implements the 90% Productivity + 10% Behavior formula.
    """

    def __init__(self, db: Session):
        """Initialize the calculator service."""
        self.db = db
        self.daily_target = settings.DAILY_TARGET_POINTS
        self.productivity_weight = settings.PRODUCTIVITY_WEIGHT
        self.behavior_weight = settings.BEHAVIOR_WEIGHT
        self.idle_penalty = settings.IDLE_PENALTY_PER_HOUR
        self.conduct_penalty = settings.CONDUCT_PENALTY

    def calculate_for_employee(self, emp_id: str, target_date: date) -> Optional[PerformanceScore]:
        """
        Calculate performance score for a single employee on a specific date.

        Args:
            emp_id: Employee ID
            target_date: Date to calculate performance for

        Returns:
            PerformanceScore object or None if no activities found
        """
        # Get employee
        employee = self.db.query(User).filter(User.emp_id == emp_id).first()
        if not employee:
            return None

        # Get activities for this date
        activities = (
            self.db.query(Activity)
            .filter(Activity.emp_id == emp_id, Activity.date == target_date)
            .all()
        )

        if not activities:
            return None

        # Calculate total task points
        total_points = 0.0
        task_count = len(activities)

        for activity in activities:
            task_standard = (
                self.db.query(TaskStandard)
                .filter(TaskStandard.task_id == activity.task_id)
                .first()
            )
            if task_standard:
                total_points += activity.count * task_standard.base_score

        # Get daily metrics (default to 0 if not found)
        metric = (
            self.db.query(DailyMetric)
            .filter(DailyMetric.emp_id == emp_id, DailyMetric.date == target_date)
            .first()
        )

        idle_hours = metric.idle_hours if metric else 0.0
        conduct_flag = metric.conduct_flag if metric else 0

        # Calculate productivity score (90% weight)
        productivity_percent = (total_points / self.daily_target) * 100
        weighted_prod_score = productivity_percent * self.productivity_weight

        # Calculate behavior score (10% weight)
        behavior_score_raw = 100.0
        behavior_score_raw -= idle_hours * self.idle_penalty
        behavior_score_raw -= conduct_flag * self.conduct_penalty
        behavior_score_raw = max(behavior_score_raw, 0)  # Floor at 0

        weighted_behavior_score = behavior_score_raw * self.behavior_weight

        # Final performance
        final_performance = weighted_prod_score + weighted_behavior_score

        # Generate score ID
        score_id = f"SCR_{emp_id}_{target_date.strftime('%Y%m%d')}"

        # Check if score already exists
        existing_score = (
            self.db.query(PerformanceScore)
            .filter(PerformanceScore.score_id == score_id)
            .first()
        )

        if existing_score:
            # Update existing score
            existing_score.total_task_points = total_points
            existing_score.productivity_percent = productivity_percent
            existing_score.weighted_prod_score = weighted_prod_score
            existing_score.behavior_score_raw = behavior_score_raw
            existing_score.weighted_behavior_score = weighted_behavior_score
            existing_score.final_performance_percent = final_performance
            existing_score.task_count = task_count
            existing_score.idle_hours = idle_hours
            existing_score.conduct_flag = conduct_flag
            score = existing_score
        else:
            # Create new score
            score = PerformanceScore(
                score_id=score_id,
                date=target_date,
                emp_id=emp_id,
                total_task_points=total_points,
                productivity_percent=productivity_percent,
                weighted_prod_score=weighted_prod_score,
                behavior_score_raw=behavior_score_raw,
                weighted_behavior_score=weighted_behavior_score,
                final_performance_percent=final_performance,
                task_count=task_count,
                idle_hours=idle_hours,
                conduct_flag=conduct_flag,
            )
            self.db.add(score)

        self.db.commit()
        self.db.refresh(score)

        return score

    def calculate_for_all_employees(self, target_date: date) -> List[PerformanceScore]:
        """
        Calculate performance scores for all employees on a specific date.

        Args:
            target_date: Date to calculate performance for

        Returns:
            List of PerformanceScore objects
        """
        # Get all employees who have activities on this date
        emp_ids = (
            self.db.query(Activity.emp_id)
            .filter(Activity.date == target_date)
            .distinct()
            .all()
        )

        scores = []
        for (emp_id,) in emp_ids:
            score = self.calculate_for_employee(emp_id, target_date)
            if score:
                scores.append(score)

        return scores

    def get_employee_trend(
        self, emp_id: str, start_date: date, end_date: date
    ) -> List[PerformanceScore]:
        """
        Get performance trend for an employee over a date range.

        Args:
            emp_id: Employee ID
            start_date: Start date
            end_date: End date

        Returns:
            List of PerformanceScore objects ordered by date
        """
        scores = (
            self.db.query(PerformanceScore)
            .filter(
                PerformanceScore.emp_id == emp_id,
                PerformanceScore.date >= start_date,
                PerformanceScore.date <= end_date,
            )
            .order_by(PerformanceScore.date)
            .all()
        )

        return scores

    def get_team_leaderboard(
        self, target_date: date, limit: int = 10
    ) -> List[PerformanceScore]:
        """
        Get top performers for a specific date.

        Args:
            target_date: Date to get leaderboard for
            limit: Number of top performers to return

        Returns:
            List of PerformanceScore objects ordered by performance DESC
        """
        scores = (
            self.db.query(PerformanceScore)
            .filter(PerformanceScore.date == target_date)
            .order_by(PerformanceScore.final_performance_percent.desc())
            .limit(limit)
            .all()
        )

        return scores

    def get_statistics(self, target_date: date) -> dict:
        """
        Calculate aggregate statistics for a specific date.

        Args:
            target_date: Date to calculate statistics for

        Returns:
            Dictionary with statistics
        """
        scores = (
            self.db.query(PerformanceScore)
            .filter(PerformanceScore.date == target_date)
            .all()
        )

        if not scores:
            return {
                "date": target_date,
                "count": 0,
                "avg_performance": 0,
                "avg_productivity": 0,
                "avg_behavior": 0,
                "top_performer": None,
                "needs_improvement": None,
            }

        performances = [s.final_performance_percent for s in scores]
        productivities = [s.weighted_prod_score for s in scores]
        behaviors = [s.weighted_behavior_score for s in scores]

        # Get top and bottom performers
        sorted_scores = sorted(scores, key=lambda x: x.final_performance_percent, reverse=True)

        return {
            "date": target_date,
            "count": len(scores),
            "avg_performance": sum(performances) / len(performances),
            "avg_productivity": sum(productivities) / len(productivities),
            "avg_behavior": sum(behaviors) / len(behaviors),
            "max_performance": max(performances),
            "min_performance": min(performances),
            "top_performer": {
                "emp_id": sorted_scores[0].emp_id,
                "performance": sorted_scores[0].final_performance_percent,
            },
            "needs_improvement": {
                "emp_id": sorted_scores[-1].emp_id,
                "performance": sorted_scores[-1].final_performance_percent,
            },
        }

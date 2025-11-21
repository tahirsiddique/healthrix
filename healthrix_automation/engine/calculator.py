"""
Performance Calculation Engine
===============================

Core logic for calculating employee performance scores.
Implements the 90% Productivity + 10% Behavior evaluation model.

Based on Sources 5 & 6 from the original Excel system.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import pandas as pd

from ..models.standards import StandardsDatabase
from ..models.activity import ActivityLog, ActivityEntry


@dataclass
class PerformanceScore:
    """
    Represents the complete performance evaluation for an employee.

    Attributes:
        emp_id: Employee ID
        name: Employee name
        date: Evaluation date
        total_task_points: Raw points earned from task completion
        productivity_percentage: Productivity as percentage of target
        weighted_prod_score: Productivity score with 90% weight applied
        behavior_score_raw: Raw behavior score (0-100)
        weighted_behavior_score: Behavior score with 10% weight applied
        final_performance: Combined final performance percentage
        task_breakdown: Dictionary of task counts
        idle_hours: Total idle hours
        conduct_flag: Whether conduct issues were flagged
    """
    emp_id: str
    name: str
    date: str
    total_task_points: float
    productivity_percentage: float
    weighted_prod_score: float
    behavior_score_raw: float
    weighted_behavior_score: float
    final_performance: float
    task_breakdown: Dict[str, int]
    idle_hours: float
    conduct_flag: int

    def to_dict(self) -> dict:
        """Convert the performance score to a dictionary."""
        return {
            "Emp_ID": self.emp_id,
            "Name": self.name,
            "Date": self.date,
            "Total_Task_Points": self.total_task_points,
            "Productivity_%": round(self.productivity_percentage, 2),
            "Weighted_Prod_Score": round(self.weighted_prod_score, 2),
            "Behavior_Score_Raw": round(self.behavior_score_raw, 2),
            "Weighted_Behavior_Score": round(self.weighted_behavior_score, 2),
            "Final_Performance_%": round(self.final_performance, 2),
            "Idle_Hours": self.idle_hours,
            "Conduct_Flag": self.conduct_flag,
        }


class PerformanceCalculator:
    """
    Calculates employee performance scores based on productivity and behavior.

    The calculation follows this formula:
    - Productivity Score (90% weight): Based on task completion vs. target
    - Behavior Score (10% weight): Based on idle time and conduct
    - Final Performance = Weighted_Prod_Score + Weighted_Behavior_Score
    """

    # Configuration constants
    PRODUCTIVITY_WEIGHT = 0.90  # 90% weight for productivity
    BEHAVIOR_WEIGHT = 0.10      # 10% weight for behavior
    DEFAULT_DAILY_TARGET = 400   # Default target points per day
    IDLE_PENALTY_PER_HOUR = 10   # Points deducted per idle hour
    CONDUCT_PENALTY = 50         # Points deducted for conduct flag

    def __init__(self, standards_db: StandardsDatabase,
                 daily_target_points: Optional[int] = None):
        """
        Initialize the performance calculator.

        Args:
            standards_db: StandardsDatabase instance for task scoring
            daily_target_points: Target points for 100% productivity (default 400)
        """
        self.standards_db = standards_db
        self.daily_target = daily_target_points or self.DEFAULT_DAILY_TARGET

    def calculate_task_points(self, activities: List[ActivityEntry]) -> tuple[float, Dict[str, int]]:
        """
        Calculate total points earned from tasks.

        Args:
            activities: List of activity entries

        Returns:
            Tuple of (total_points, task_breakdown_dict)
        """
        total_points = 0.0
        task_breakdown = {}

        for activity in activities:
            points = self.standards_db.get_score(activity.task_name, activity.count)
            total_points += points

            # Track task counts
            if activity.task_name in task_breakdown:
                task_breakdown[activity.task_name] += activity.count
            else:
                task_breakdown[activity.task_name] = activity.count

        return total_points, task_breakdown

    def calculate_productivity_score(self, total_points: float) -> tuple[float, float]:
        """
        Calculate productivity score with 90% weight.

        Formula:
        - Productivity % = (Total Points / Daily Target) * 100
        - Weighted Score = Productivity % * 0.90

        Args:
            total_points: Total points earned from tasks

        Returns:
            Tuple of (productivity_percentage, weighted_score)
        """
        productivity_pct = (total_points / self.daily_target) * 100
        weighted_score = productivity_pct * self.PRODUCTIVITY_WEIGHT

        return productivity_pct, weighted_score

    def calculate_behavior_score(self, idle_hours: float, conduct_flag: int) -> tuple[float, float]:
        """
        Calculate behavior score with 10% weight.

        Formula:
        - Base Score = 100
        - Deduct: idle_hours * IDLE_PENALTY_PER_HOUR
        - Deduct: conduct_flag * CONDUCT_PENALTY
        - Floor at 0
        - Weighted Score = Base Score * 0.10

        Args:
            idle_hours: Hours of idle time
            conduct_flag: 0 (Good) or 1 (Issue flagged)

        Returns:
            Tuple of (raw_behavior_score, weighted_score)
        """
        base_score = 100.0

        # Apply penalties
        base_score -= (idle_hours * self.IDLE_PENALTY_PER_HOUR)
        base_score -= (conduct_flag * self.CONDUCT_PENALTY)

        # Floor at 0
        base_score = max(base_score, 0)

        # Apply 10% weight
        weighted_score = base_score * self.BEHAVIOR_WEIGHT

        return base_score, weighted_score

    def calculate_employee_performance(self, emp_id: str, target_date: str,
                                      activity_log: ActivityLog) -> Optional[PerformanceScore]:
        """
        Calculate complete performance score for an employee on a specific date.

        Args:
            emp_id: Employee ID
            target_date: Date to evaluate (YYYY-MM-DD)
            activity_log: ActivityLog instance with employee activities

        Returns:
            PerformanceScore object or None if no activities found
        """
        # Get activities for this employee on this date
        activities = [
            a for a in activity_log.activities
            if a.emp_id == emp_id and a.date == target_date
        ]

        if not activities:
            return None

        # Get employee name
        employee = activity_log.employees.get(emp_id)
        emp_name = employee.name if employee else "Unknown"

        # Calculate task points
        total_points, task_breakdown = self.calculate_task_points(activities)

        # Calculate productivity score
        prod_pct, weighted_prod = self.calculate_productivity_score(total_points)

        # Get behavior metrics (use max values as they're daily metrics)
        idle_hours = max(a.idle_hours for a in activities)
        conduct_flag = max(a.conduct_flag for a in activities)

        # Calculate behavior score
        behavior_raw, weighted_behavior = self.calculate_behavior_score(
            idle_hours, conduct_flag
        )

        # Calculate final performance
        final_performance = weighted_prod + weighted_behavior

        return PerformanceScore(
            emp_id=emp_id,
            name=emp_name,
            date=target_date,
            total_task_points=total_points,
            productivity_percentage=prod_pct,
            weighted_prod_score=weighted_prod,
            behavior_score_raw=behavior_raw,
            weighted_behavior_score=weighted_behavior,
            final_performance=final_performance,
            task_breakdown=task_breakdown,
            idle_hours=idle_hours,
            conduct_flag=conduct_flag,
        )

    def calculate_all_employees(self, target_date: str,
                               activity_log: ActivityLog) -> List[PerformanceScore]:
        """
        Calculate performance scores for all employees on a specific date.

        Args:
            target_date: Date to evaluate (YYYY-MM-DD)
            activity_log: ActivityLog instance

        Returns:
            List of PerformanceScore objects
        """
        # Get unique employee IDs for this date
        emp_ids = set(
            a.emp_id for a in activity_log.activities
            if a.date == target_date
        )

        scores = []
        for emp_id in emp_ids:
            score = self.calculate_employee_performance(emp_id, target_date, activity_log)
            if score:
                scores.append(score)

        # Sort by final performance (descending)
        scores.sort(key=lambda x: x.final_performance, reverse=True)

        return scores

    def calculate_date_range(self, start_date: str, end_date: str,
                            activity_log: ActivityLog) -> Dict[str, List[PerformanceScore]]:
        """
        Calculate performance scores for all employees across a date range.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            activity_log: ActivityLog instance

        Returns:
            Dictionary mapping dates to lists of PerformanceScore objects
        """
        # Get unique dates in range
        dates = set(
            a.date for a in activity_log.activities
            if start_date <= a.date <= end_date
        )

        results = {}
        for date in sorted(dates):
            results[date] = self.calculate_all_employees(date, activity_log)

        return results

    def get_employee_trend(self, emp_id: str, start_date: str, end_date: str,
                          activity_log: ActivityLog) -> pd.DataFrame:
        """
        Get performance trend for an employee over time.

        Args:
            emp_id: Employee ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            activity_log: ActivityLog instance

        Returns:
            DataFrame with daily performance metrics
        """
        dates = set(
            a.date for a in activity_log.activities
            if a.emp_id == emp_id and start_date <= a.date <= end_date
        )

        trend_data = []
        for date in sorted(dates):
            score = self.calculate_employee_performance(emp_id, date, activity_log)
            if score:
                trend_data.append(score.to_dict())

        return pd.DataFrame(trend_data)

    def set_daily_target(self, new_target: int):
        """
        Update the daily target points.

        Args:
            new_target: New target points value
        """
        if new_target <= 0:
            raise ValueError("Daily target must be positive")
        self.daily_target = new_target

    def get_productivity_statistics(self, scores: List[PerformanceScore]) -> dict:
        """
        Calculate aggregate statistics for a list of performance scores.

        Args:
            scores: List of PerformanceScore objects

        Returns:
            Dictionary with statistics
        """
        if not scores:
            return {
                "count": 0,
                "avg_performance": 0,
                "avg_productivity": 0,
                "avg_behavior": 0,
                "top_performer": None,
                "needs_improvement": None,
            }

        performances = [s.final_performance for s in scores]
        productivities = [s.weighted_prod_score for s in scores]
        behaviors = [s.weighted_behavior_score for s in scores]

        return {
            "count": len(scores),
            "avg_performance": sum(performances) / len(performances),
            "avg_productivity": sum(productivities) / len(productivities),
            "avg_behavior": sum(behaviors) / len(behaviors),
            "top_performer": scores[0].name if scores else None,
            "needs_improvement": scores[-1].name if scores else None,
        }

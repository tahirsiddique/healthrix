"""
Activity Log Data Model
========================

Manages employee activity tracking and logging.
Replaces the wide-format "Productivity Pattern" Excel sheet with normalized data.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional
import pandas as pd


@dataclass
class Employee:
    """
    Represents an employee in the system.

    Attributes:
        emp_id: Unique employee identifier
        name: Employee full name
        department: Department name (optional)
        role: Job role/title (optional)
    """
    emp_id: str
    name: str
    department: Optional[str] = None
    role: Optional[str] = None


@dataclass
class ActivityEntry:
    """
    Represents a single activity entry for an employee.

    Attributes:
        date: Date of activity
        emp_id: Employee ID
        patient_id: Patient identifier (optional)
        task_name: Name of the task performed
        count: Number of times task was completed (default 1)
        duration_minutes: Time spent on task in minutes (optional)
        idle_hours: Idle time during the day in hours (default 0)
        conduct_flag: Behavioral flag (0=Good, 1=Issue, default 0)
        notes: Additional notes (optional)
    """
    date: str  # Format: YYYY-MM-DD
    emp_id: str
    task_name: str
    count: int = 1
    patient_id: Optional[str] = None
    duration_minutes: Optional[int] = None
    idle_hours: float = 0.0
    conduct_flag: int = 0
    notes: Optional[str] = None

    def __post_init__(self):
        """Validate the activity entry after initialization."""
        # Validate date format
        try:
            datetime.strptime(self.date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format: {self.date}. Expected YYYY-MM-DD")

        # Validate count
        if self.count < 0:
            raise ValueError("Count cannot be negative")

        # Validate conduct flag
        if self.conduct_flag not in [0, 1]:
            raise ValueError("Conduct flag must be 0 (Good) or 1 (Issue)")

        # Validate idle hours
        if self.idle_hours < 0:
            raise ValueError("Idle hours cannot be negative")


class ActivityLog:
    """
    Manages the collection of activity entries for all employees.

    This class provides methods to add, retrieve, and analyze employee activities.
    Based on Source 9 from the original Excel system.
    """

    def __init__(self):
        """Initialize an empty activity log."""
        self.activities: List[ActivityEntry] = []
        self.employees: dict[str, Employee] = {}

    def add_employee(self, employee: Employee):
        """
        Add an employee to the system.

        Args:
            employee: Employee object to add
        """
        self.employees[employee.emp_id] = employee

    def add_activity(self, activity: ActivityEntry):
        """
        Add a single activity entry to the log.

        Args:
            activity: ActivityEntry object to add
        """
        self.activities.append(activity)

    def add_activities_bulk(self, activities: List[ActivityEntry]):
        """
        Add multiple activity entries at once.

        Args:
            activities: List of ActivityEntry objects
        """
        self.activities.extend(activities)

    def get_employee_activities(self, emp_id: str,
                                start_date: Optional[str] = None,
                                end_date: Optional[str] = None) -> List[ActivityEntry]:
        """
        Retrieve all activities for a specific employee, optionally filtered by date range.

        Args:
            emp_id: Employee ID
            start_date: Start date (YYYY-MM-DD), optional
            end_date: End date (YYYY-MM-DD), optional

        Returns:
            List of ActivityEntry objects
        """
        filtered = [a for a in self.activities if a.emp_id == emp_id]

        if start_date:
            filtered = [a for a in filtered if a.date >= start_date]
        if end_date:
            filtered = [a for a in filtered if a.date <= end_date]

        return filtered

    def get_activities_by_date(self, target_date: str) -> List[ActivityEntry]:
        """
        Retrieve all activities for a specific date.

        Args:
            target_date: Date in YYYY-MM-DD format

        Returns:
            List of ActivityEntry objects for that date
        """
        return [a for a in self.activities if a.date == target_date]

    def get_activities_by_task(self, task_name: str) -> List[ActivityEntry]:
        """
        Retrieve all activities for a specific task type.

        Args:
            task_name: Name of the task

        Returns:
            List of ActivityEntry objects for that task
        """
        return [a for a in self.activities if a.task_name == task_name]

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert the activity log to a pandas DataFrame.

        Returns:
            DataFrame with all activity entries
        """
        if not self.activities:
            return pd.DataFrame()

        data = []
        for activity in self.activities:
            emp_name = self.employees.get(activity.emp_id, Employee(activity.emp_id, "Unknown")).name

            data.append({
                "Date": activity.date,
                "Emp_ID": activity.emp_id,
                "Name": emp_name,
                "Task": activity.task_name,
                "Count": activity.count,
                "Patient_ID": activity.patient_id,
                "Duration_Minutes": activity.duration_minutes,
                "Idle_Hours": activity.idle_hours,
                "Conduct_Flag": activity.conduct_flag,
                "Notes": activity.notes,
            })

        return pd.DataFrame(data)

    def get_employee_summary(self, emp_id: str, target_date: str) -> dict:
        """
        Get a summary of an employee's activities for a specific date.

        Args:
            emp_id: Employee ID
            target_date: Date in YYYY-MM-DD format

        Returns:
            Dictionary with summary statistics
        """
        activities = [
            a for a in self.activities
            if a.emp_id == emp_id and a.date == target_date
        ]

        if not activities:
            return {
                "emp_id": emp_id,
                "date": target_date,
                "total_tasks": 0,
                "total_count": 0,
                "idle_hours": 0,
                "conduct_issues": 0,
            }

        return {
            "emp_id": emp_id,
            "date": target_date,
            "total_tasks": len(set(a.task_name for a in activities)),
            "total_count": sum(a.count for a in activities),
            "idle_hours": max(a.idle_hours for a in activities),  # Take max as it's a daily metric
            "conduct_issues": max(a.conduct_flag for a in activities),
        }

    @classmethod
    def from_csv(cls, csv_path: str, employees_csv: Optional[str] = None):
        """
        Load activity log from a CSV file.

        CSV Format:
        Date,Emp_ID,Name,Task,Count,Patient_ID,Duration_Minutes,Idle_Hours,Conduct_Flag,Notes

        Args:
            csv_path: Path to the activities CSV file
            employees_csv: Optional path to employees CSV file

        Returns:
            ActivityLog instance
        """
        log = cls()

        # Load employees if provided
        if employees_csv:
            emp_df = pd.read_csv(employees_csv)
            for _, row in emp_df.iterrows():
                employee = Employee(
                    emp_id=row['Emp_ID'],
                    name=row['Name'],
                    department=row.get('Department'),
                    role=row.get('Role'),
                )
                log.add_employee(employee)

        # Load activities
        df = pd.read_csv(csv_path)

        for _, row in df.iterrows():
            # Add employee if not already present
            if row['Emp_ID'] not in log.employees:
                log.add_employee(Employee(emp_id=row['Emp_ID'], name=row['Name']))

            activity = ActivityEntry(
                date=row['Date'],
                emp_id=row['Emp_ID'],
                task_name=row['Task'],
                count=int(row.get('Count', 1)),
                patient_id=row.get('Patient_ID'),
                duration_minutes=int(row['Duration_Minutes']) if pd.notna(row.get('Duration_Minutes')) else None,
                idle_hours=float(row.get('Idle_Hours', 0)),
                conduct_flag=int(row.get('Conduct_Flag', 0)),
                notes=row.get('Notes'),
            )
            log.add_activity(activity)

        return log

    def export_to_csv(self, output_path: str):
        """
        Export the activity log to a CSV file.

        Args:
            output_path: Path where the CSV should be saved
        """
        df = self.to_dataframe()
        df.to_csv(output_path, index=False)

    def clear(self):
        """Clear all activities from the log."""
        self.activities.clear()

    def get_date_range(self) -> tuple[Optional[str], Optional[str]]:
        """
        Get the date range of activities in the log.

        Returns:
            Tuple of (earliest_date, latest_date) or (None, None) if empty
        """
        if not self.activities:
            return None, None

        dates = [a.date for a in self.activities]
        return min(dates), max(dates)

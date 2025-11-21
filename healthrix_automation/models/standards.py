"""
Standards Database Module
=========================

Defines the master standards table for task scoring and categorization.
This replaces the manual lookup from the "Standard.csv" Excel sheet.
"""

from dataclasses import dataclass
from typing import Dict, Optional
import pandas as pd


@dataclass
class TaskStandard:
    """
    Represents a single task standard with scoring information.

    Attributes:
        task_name: Name of the task (e.g., "Authorization Created")
        ec_category: Effort Category (e.g., "EC-1", "EC-2")
        base_score: Points awarded per task completion
        target_daily: Recommended daily target count
        weight: Weight factor for productivity calculation (default 0.90)
    """
    task_name: str
    ec_category: str
    base_score: int
    target_daily: int
    weight: float = 0.90

    def calculate_points(self, count: int) -> float:
        """Calculate total points for a given count of this task."""
        return count * self.base_score


class StandardsDatabase:
    """
    Master standards database for all task types.

    This class manages the lookup table that assigns scores to tasks instantly.
    Based on Sources 10 & 11 from the original Excel system.
    """

    # Default standards configuration
    DEFAULT_STANDARDS = {
        "Authorization Created": {
            "ec_category": "EC-1",
            "base_score": 45,
            "target_daily": 10,
        },
        "Authorization Status/FU": {
            "ec_category": "EC-1",
            "base_score": 25,
            "target_daily": 15,
        },
        "Appeal": {
            "ec_category": "EC-1",
            "base_score": 10,
            "target_daily": 5,
        },
        "Eligibility Check": {
            "ec_category": "EC-2",
            "base_score": 20,
            "target_daily": 25,
        },
        "Medication Refill": {
            "ec_category": "EC-2",
            "base_score": 20,
            "target_daily": 30,
        },
        "Pharmacy Call": {
            "ec_category": "EC-2",
            "base_score": 10,
            "target_daily": 10,
        },
        "Document Upload": {
            "ec_category": "EC-5",
            "base_score": 10,
            "target_daily": 2,
        },
        "Patient Outreach": {
            "ec_category": "EC-3",
            "base_score": 15,
            "target_daily": 20,
        },
        "Insurance Verification": {
            "ec_category": "EC-2",
            "base_score": 25,
            "target_daily": 15,
        },
        "Claims Processing": {
            "ec_category": "EC-4",
            "base_score": 30,
            "target_daily": 12,
        },
    }

    def __init__(self, custom_standards: Optional[Dict] = None):
        """
        Initialize the standards database.

        Args:
            custom_standards: Optional dictionary to override default standards
        """
        self.standards: Dict[str, TaskStandard] = {}

        # Load defaults
        standards_config = custom_standards or self.DEFAULT_STANDARDS

        for task_name, config in standards_config.items():
            self.standards[task_name] = TaskStandard(
                task_name=task_name,
                ec_category=config["ec_category"],
                base_score=config["base_score"],
                target_daily=config["target_daily"],
            )

    def get_task_standard(self, task_name: str) -> Optional[TaskStandard]:
        """
        Retrieve the standard for a specific task.

        Args:
            task_name: Name of the task

        Returns:
            TaskStandard object or None if not found
        """
        return self.standards.get(task_name)

    def get_score(self, task_name: str, count: int = 1) -> float:
        """
        Calculate the score for a task given its count.

        Args:
            task_name: Name of the task
            count: Number of times the task was completed

        Returns:
            Total points earned (0 if task not found)
        """
        standard = self.get_task_standard(task_name)
        if standard:
            return standard.calculate_points(count)
        return 0.0

    def list_all_tasks(self) -> list:
        """Return a list of all available task names."""
        return list(self.standards.keys())

    def get_ec_category_tasks(self, ec_category: str) -> list:
        """
        Get all tasks belonging to a specific EC category.

        Args:
            ec_category: The EC category (e.g., "EC-1")

        Returns:
            List of task names in that category
        """
        return [
            task_name
            for task_name, standard in self.standards.items()
            if standard.ec_category == ec_category
        ]

    def to_dataframe(self) -> pd.DataFrame:
        """
        Export the standards database as a pandas DataFrame.

        Returns:
            DataFrame with columns: Task_Name, EC_Category, Base_Score, Target_Daily
        """
        data = []
        for task_name, standard in self.standards.items():
            data.append({
                "Task_Name": task_name,
                "EC_Category": standard.ec_category,
                "Base_Score": standard.base_score,
                "Target_Daily": standard.target_daily,
            })

        return pd.DataFrame(data)

    def add_custom_task(self, task_name: str, ec_category: str,
                       base_score: int, target_daily: int):
        """
        Add a new custom task standard to the database.

        Args:
            task_name: Name of the new task
            ec_category: Effort Category
            base_score: Points per completion
            target_daily: Recommended daily target
        """
        self.standards[task_name] = TaskStandard(
            task_name=task_name,
            ec_category=ec_category,
            base_score=base_score,
            target_daily=target_daily,
        )

    @classmethod
    def from_csv(cls, csv_path: str):
        """
        Load standards from a CSV file.

        CSV Format:
        Task_Name,EC_Category,Base_Score,Target_Daily

        Args:
            csv_path: Path to the CSV file

        Returns:
            StandardsDatabase instance
        """
        df = pd.read_csv(csv_path)

        custom_standards = {}
        for _, row in df.iterrows():
            custom_standards[row['Task_Name']] = {
                'ec_category': row['EC_Category'],
                'base_score': int(row['Base_Score']),
                'target_daily': int(row['Target_Daily']),
            }

        return cls(custom_standards=custom_standards)

    def export_to_csv(self, output_path: str):
        """
        Export the standards database to a CSV file.

        Args:
            output_path: Path where the CSV should be saved
        """
        df = self.to_dataframe()
        df.to_csv(output_path, index=False)

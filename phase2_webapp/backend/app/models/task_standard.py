"""
Task Standard Model
===================

Represents task scoring standards and targets.
"""

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from ..db.session import Base


class TaskStandard(Base):
    """
    Task Standard model for scoring configuration.

    Attributes:
        task_id: Unique task identifier (primary key)
        task_name: Task name
        ec_category: Effort Category (EC-1, EC-2, etc.)
        base_score: Points awarded per task completion
        target_daily: Recommended daily target count
        description: Task description
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """

    __tablename__ = "task_standards"

    task_id = Column(String(50), primary_key=True, index=True)
    task_name = Column(String(255), unique=True, nullable=False, index=True)
    ec_category = Column(String(10), nullable=False)
    base_score = Column(Integer, nullable=False)
    target_daily = Column(Integer, nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    activities = relationship("Activity", back_populates="task_standard")

    def __repr__(self):
        return f"<TaskStandard {self.task_id}: {self.task_name} ({self.base_score} pts)>"

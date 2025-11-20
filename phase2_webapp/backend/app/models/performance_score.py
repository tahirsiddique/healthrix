"""
Performance Score Model
=======================

Represents calculated performance scores for employees.
"""

from sqlalchemy import Column, String, Float, Integer, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from ..db.session import Base


class PerformanceScore(Base):
    """
    Performance Score model for calculated performance metrics.

    Attributes:
        score_id: Unique score identifier (primary key)
        date: Date of performance calculation
        emp_id: Employee ID (foreign key to users)
        total_task_points: Total points earned from tasks
        productivity_percent: Productivity as percentage
        weighted_prod_score: Productivity score with 90% weight
        behavior_score_raw: Raw behavior score (0-100)
        weighted_behavior_score: Behavior score with 10% weight
        final_performance_percent: Final combined performance score
        task_count: Number of activities logged
        idle_hours: Total idle hours for the day
        conduct_flag: Conduct flag for the day
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """

    __tablename__ = "performance_scores"

    score_id = Column(String(50), primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    emp_id = Column(String(50), ForeignKey("users.emp_id"), nullable=False, index=True)
    total_task_points = Column(Float, nullable=False)
    productivity_percent = Column(Float, nullable=False)
    weighted_prod_score = Column(Float, nullable=False)
    behavior_score_raw = Column(Float, nullable=False)
    weighted_behavior_score = Column(Float, nullable=False)
    final_performance_percent = Column(Float, nullable=False)
    task_count = Column(Integer, nullable=False)
    idle_hours = Column(Float, nullable=False)
    conduct_flag = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="performance_scores")

    def __repr__(self):
        return f"<PerformanceScore {self.score_id}: {self.emp_id} - {self.final_performance_percent:.2f}%>"

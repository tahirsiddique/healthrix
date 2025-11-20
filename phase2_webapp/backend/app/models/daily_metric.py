"""
Daily Metric Model
==================

Represents daily behavioral metrics for employees.
"""

from sqlalchemy import Column, String, Integer, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from ..db.session import Base


class DailyMetric(Base):
    """
    Daily Metric model for behavioral tracking.

    Attributes:
        metric_id: Unique metric identifier (primary key)
        date: Date of metric
        emp_id: Employee ID (foreign key to users)
        idle_hours: Hours of idle time (decimal)
        conduct_flag: Conduct issue flag (0=Good, 1=Issue)
        conduct_notes: Notes about conduct issue
        supervisor: Supervisor who recorded metric
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """

    __tablename__ = "daily_metrics"

    metric_id = Column(String(50), primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    emp_id = Column(String(50), ForeignKey("users.emp_id"), nullable=False, index=True)
    idle_hours = Column(Float, default=0.0, nullable=False)
    conduct_flag = Column(Integer, default=0, nullable=False)
    conduct_notes = Column(Text)
    supervisor = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="daily_metrics")

    def __repr__(self):
        return f"<DailyMetric {self.metric_id}: {self.emp_id} on {self.date}>"

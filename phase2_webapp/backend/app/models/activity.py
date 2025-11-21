"""
Activity Model
==============

Represents employee activities and task completions.
"""

from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from ..db.session import Base


class Activity(Base):
    """
    Activity model for logging employee tasks.

    Attributes:
        activity_id: Unique activity identifier (primary key)
        date: Date when activity was performed
        emp_id: Employee ID (foreign key to users)
        task_id: Task ID (foreign key to task_standards)
        count: Number of times task was completed
        patient_id: Patient identifier (optional)
        duration_minutes: Time spent on task in minutes (optional)
        notes: Additional notes (optional)
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """

    __tablename__ = "activities"

    activity_id = Column(String(50), primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    emp_id = Column(String(50), ForeignKey("users.emp_id"), nullable=False, index=True)
    task_id = Column(String(50), ForeignKey("task_standards.task_id"), nullable=False)
    count = Column(Integer, default=1, nullable=False)
    patient_id = Column(String(50))
    duration_minutes = Column(Integer)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="activities")
    task_standard = relationship("TaskStandard", back_populates="activities")

    def __repr__(self):
        return f"<Activity {self.activity_id}: {self.emp_id} - {self.task_id} (×{self.count})>"

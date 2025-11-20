"""
User Model
==========

Represents employees, supervisors, and administrators.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..db.session import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    EMPLOYEE = "employee"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"


class User(Base):
    """
    User model representing employees, supervisors, and admins.

    Attributes:
        emp_id: Unique employee ID (primary key)
        email: User email address (unique)
        hashed_password: Bcrypt hashed password
        name: Full name
        department: Department name
        role: User role (employee, supervisor, admin)
        is_active: Whether user account is active
        hire_date: Date when employee was hired
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """

    __tablename__ = "users"

    emp_id = Column(String(50), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    department = Column(String(100))
    role = Column(SQLEnum(UserRole), default=UserRole.EMPLOYEE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    hire_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")
    daily_metrics = relationship("DailyMetric", back_populates="user", cascade="all, delete-orphan")
    performance_scores = relationship("PerformanceScore", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.emp_id}: {self.name} ({self.role})>"

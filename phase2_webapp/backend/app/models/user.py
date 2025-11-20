"""
User Model
==========

Represents employees, supervisors, and administrators.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..db.session import Base


class UserRole(str, enum.Enum):
    """
    User role enumeration with hierarchical permissions.

    Hierarchy (highest to lowest):
    - SUPER_ADMIN: Full system access, can manage all users and settings
    - ADMIN: Can manage most operations, create users (except super admins)
    - HR: Can manage employees, view all performance data, generate reports
    - DEPARTMENT_HEAD: Can manage department employees, view department performance
    - EMPLOYEE: Can view own data, submit activities
    """
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    HR = "hr"
    DEPARTMENT_HEAD = "department_head"
    EMPLOYEE = "employee"

    # Legacy roles (kept for backward compatibility)
    SUPERVISOR = "department_head"  # Alias for department_head


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
    department = Column(String(100))  # Legacy field, kept for backward compatibility
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"))
    role = Column(SQLEnum(UserRole), default=UserRole.EMPLOYEE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    hire_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    department_obj = relationship("Department", foreign_keys=[department_id], back_populates="employees")
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")
    daily_metrics = relationship("DailyMetric", back_populates="user", cascade="all, delete-orphan")
    performance_scores = relationship("PerformanceScore", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.emp_id}: {self.name} ({self.role})>"

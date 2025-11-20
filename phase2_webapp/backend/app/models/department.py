"""
Department Model
================

Represents organizational departments with hierarchical management.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from ..db.session import Base


class Department(Base):
    """
    Department model for organizational structure.

    Attributes:
        id: Auto-incrementing primary key
        dept_code: Unique department code (e.g., "IT", "HR", "SALES")
        dept_name: Department name
        description: Department description
        manager_emp_id: Employee ID of department head
        is_active: Whether department is active
        created_at: Timestamp when department was created
        updated_at: Timestamp when department was last updated
    """

    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dept_code = Column(String(20), unique=True, index=True, nullable=False)
    dept_name = Column(String(255), nullable=False)
    description = Column(String(500))
    manager_emp_id = Column(String(50), ForeignKey("users.emp_id", ondelete="SET NULL"))
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    manager = relationship("User", foreign_keys=[manager_emp_id], backref="managed_departments")
    employees = relationship("User", foreign_keys="User.department_id", back_populates="department_obj")

    def __repr__(self):
        return f"<Department {self.dept_code}: {self.dept_name}>"

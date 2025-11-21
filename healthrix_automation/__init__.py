"""
Healthrix Productivity System - Automation Engine POC
=====================================================

A comprehensive automation system for tracking and evaluating employee productivity
based on task completion and behavioral metrics.

Key Components:
- Standards Database: Task scoring and categorization
- Activity Tracking: Employee task logging
- Performance Engine: 90% Productivity + 10% Behavior calculation
- Reporting: Automated performance reports
"""

__version__ = "1.0.0"
__author__ = "Healthrix Automation Team"

from .models.standards import StandardsDatabase
from .models.activity import ActivityLog, Employee
from .engine.calculator import PerformanceCalculator
from .engine.reporter import PerformanceReporter

__all__ = [
    'StandardsDatabase',
    'ActivityLog',
    'Employee',
    'PerformanceCalculator',
    'PerformanceReporter',
]

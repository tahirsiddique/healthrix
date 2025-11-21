"""
Helper Utilities
================

Common utility functions for the Healthrix system.
"""

from datetime import datetime, timedelta
from typing import List


def validate_date(date_string: str) -> bool:
    """
    Validate that a string is in YYYY-MM-DD format.

    Args:
        date_string: Date string to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def generate_date_range(start_date: str, end_date: str) -> List[str]:
    """
    Generate a list of dates between start and end (inclusive).

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        List of date strings
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    date_list = []
    current = start

    while current <= end:
        date_list.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return date_list


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format a percentage value for display.

    Args:
        value: Percentage value
        decimals: Number of decimal places

    Returns:
        Formatted string
    """
    return f"{value:.{decimals}f}%"

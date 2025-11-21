#!/usr/bin/env python3
"""
Healthrix Automation Engine - Demo Script
==========================================

This script demonstrates the complete automation POC for the Healthrix
Productivity System. It showcases:

1. Loading standards and activity data
2. Calculating performance scores (90% Productivity + 10% Behavior)
3. Generating various reports
4. Exporting results to CSV/Excel

Usage:
    python scripts/demo.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from healthrix_automation.models.standards import StandardsDatabase
from healthrix_automation.models.activity import ActivityLog
from healthrix_automation.engine.calculator import PerformanceCalculator
from healthrix_automation.engine.reporter import PerformanceReporter


def main():
    """Main demo function."""

    print("\n" + "=" * 80)
    print("HEALTHRIX PRODUCTIVITY SYSTEM - AUTOMATION ENGINE POC")
    print("=" * 80)

    # ========================================================================
    # STEP 1: Initialize the Standards Database
    # ========================================================================
    print("\n[1] Initializing Standards Database...")

    standards_db = StandardsDatabase()

    print(f"    ✓ Loaded {len(standards_db.list_all_tasks())} task standards")
    print("\n    Sample Standards:")
    for task in list(standards_db.list_all_tasks())[:5]:
        standard = standards_db.get_task_standard(task)
        print(f"      • {task}: {standard.base_score} points (Target: {standard.target_daily}/day)")

    # ========================================================================
    # STEP 2: Load Activity Data
    # ========================================================================
    print("\n[2] Loading Employee Activity Data...")

    # Check if sample data exists
    activities_path = "data/sample_activities.csv"
    employees_path = "data/sample_employees.csv"

    if not os.path.exists(activities_path):
        print(f"    ✗ ERROR: {activities_path} not found!")
        print("    Please run this script from the project root directory.")
        return

    activity_log = ActivityLog.from_csv(activities_path, employees_path)

    print(f"    ✓ Loaded {len(activity_log.employees)} employees")
    print(f"    ✓ Loaded {len(activity_log.activities)} activity entries")

    date_range = activity_log.get_date_range()
    print(f"    ✓ Date range: {date_range[0]} to {date_range[1]}")

    # ========================================================================
    # STEP 3: Calculate Performance Scores
    # ========================================================================
    print("\n[3] Calculating Performance Scores...")

    calculator = PerformanceCalculator(standards_db, daily_target_points=400)

    # Calculate for first date in the dataset
    target_date = date_range[0]
    print(f"    Analyzing performance for: {target_date}")

    scores = calculator.calculate_all_employees(target_date, activity_log)

    print(f"    ✓ Calculated scores for {len(scores)} employees")

    # ========================================================================
    # STEP 4: Generate Summary Report
    # ========================================================================
    print("\n[4] Generating Performance Reports...")

    reporter = PerformanceReporter()

    # Summary Report
    summary_report = reporter.generate_summary_report(
        scores,
        title=f"HEALTHRIX AUTOMATED PERFORMANCE REPORT - {target_date}"
    )
    print(summary_report)

    # Statistics Report
    print("\n" + "-" * 80)
    stats_report = reporter.generate_statistics_report(scores)
    print(stats_report)

    # Alert Report
    print("-" * 80)
    alert_report = reporter.generate_alert_report(scores)
    print(alert_report)

    # ========================================================================
    # STEP 5: Detailed Employee Report (Top Performer)
    # ========================================================================
    print("\n[5] Detailed Report - Top Performer...")

    if scores:
        top_performer = scores[0]
        detailed_report = reporter.generate_detailed_report(top_performer)
        print(detailed_report)

    # ========================================================================
    # STEP 6: Multi-Date Analysis
    # ========================================================================
    print("\n[6] Multi-Date Performance Analysis...")

    if date_range[0] != date_range[1]:
        all_scores = calculator.calculate_date_range(
            date_range[0], date_range[1], activity_log
        )

        comparison_report = reporter.generate_comparison_report(all_scores)
        print(comparison_report)

    # ========================================================================
    # STEP 7: Export Results
    # ========================================================================
    print("\n[7] Exporting Results...")

    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    # Export to CSV
    csv_path = output_dir / f"performance_report_{target_date}.csv"
    reporter.export_to_csv(scores, str(csv_path))
    print(f"    ✓ CSV report saved to: {csv_path}")

    # Export to Excel (if openpyxl is available)
    try:
        excel_path = output_dir / f"performance_report_{target_date}.xlsx"
        reporter.export_to_excel(scores, str(excel_path), include_statistics=True)
        print(f"    ✓ Excel report saved to: {excel_path}")
    except ImportError:
        print("    ℹ Excel export requires 'openpyxl' package (optional)")

    # Export standards to CSV
    standards_csv = output_dir / "standards_database.csv"
    standards_db.export_to_csv(str(standards_csv))
    print(f"    ✓ Standards database saved to: {standards_csv}")

    # ========================================================================
    # STEP 8: Employee Trend Analysis
    # ========================================================================
    if len(activity_log.employees) > 0 and date_range[0] != date_range[1]:
        print("\n[8] Employee Trend Analysis...")

        # Get trend for first employee
        first_emp_id = list(activity_log.employees.keys())[0]
        emp_name = activity_log.employees[first_emp_id].name

        trend_df = calculator.get_employee_trend(
            first_emp_id,
            date_range[0],
            date_range[1],
            activity_log
        )

        if not trend_df.empty:
            print(f"    Performance Trend for {emp_name}:")
            print(trend_df[['Date', 'Total_Task_Points', 'Final_Performance_%']].to_string(index=False))

            trend_csv = output_dir / f"trend_{first_emp_id}.csv"
            trend_df.to_csv(trend_csv, index=False)
            print(f"    ✓ Trend data saved to: {trend_csv}")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("POC DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\nKey Highlights:")
    print(f"  • Automated scoring for {len(activity_log.employees)} employees")
    print(f"  • Processed {len(activity_log.activities)} activity entries")
    print(f"  • 90% Productivity + 10% Behavior formula applied")
    print(f"  • Reports generated and exported to 'output/' directory")
    print("\nNext Steps:")
    print("  1. Review the generated reports in the 'output/' directory")
    print("  2. Customize standards in models/standards.py")
    print("  3. Deploy as web app (Streamlit/Django) or integrate with AppSheet")
    print("  4. Set up automated daily report generation")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()

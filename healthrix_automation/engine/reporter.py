"""
Performance Reporting Module
=============================

Generates formatted performance reports in various formats.
"""

from typing import List, Optional
import pandas as pd
from datetime import datetime
from tabulate import tabulate

from .calculator import PerformanceScore


class PerformanceReporter:
    """
    Generates performance reports in multiple formats.

    Supports:
    - Console output (markdown tables)
    - CSV export
    - Excel export
    - Summary statistics
    - Detailed breakdowns
    """

    def __init__(self):
        """Initialize the reporter."""
        pass

    def generate_summary_report(self, scores: List[PerformanceScore],
                                title: Optional[str] = None) -> str:
        """
        Generate a summary performance report as a formatted table.

        Args:
            scores: List of PerformanceScore objects
            title: Optional report title

        Returns:
            Formatted string report
        """
        if not scores:
            return "No performance data available."

        # Build header
        report_lines = []
        if title:
            report_lines.append(f"\n{'=' * 80}")
            report_lines.append(f"{title:^80}")
            report_lines.append(f"{'=' * 80}\n")

        # Build data table
        table_data = []
        for score in scores:
            table_data.append([
                score.name,
                f"{score.total_task_points:.0f}",
                f"{score.weighted_prod_score:.2f}",
                f"{score.weighted_behavior_score:.2f}",
                f"{score.final_performance:.2f}",
            ])

        headers = [
            "Name",
            "Total Points",
            "Prod Score (Max 90)",
            "Behavior Score (Max 10)",
            "FINAL %"
        ]

        report_lines.append(tabulate(table_data, headers=headers, tablefmt="pipe"))

        return "\n".join(report_lines)

    def generate_detailed_report(self, score: PerformanceScore) -> str:
        """
        Generate a detailed report for a single employee.

        Args:
            score: PerformanceScore object

        Returns:
            Formatted detailed report string
        """
        report_lines = [
            f"\n{'=' * 80}",
            f"DETAILED PERFORMANCE REPORT",
            f"{'=' * 80}",
            f"",
            f"Employee: {score.name} ({score.emp_id})",
            f"Date: {score.date}",
            f"",
            f"--- PRODUCTIVITY METRICS ---",
            f"Total Task Points Earned: {score.total_task_points:.0f}",
            f"Productivity Percentage: {score.productivity_percentage:.2f}%",
            f"Weighted Productivity Score (90%): {score.weighted_prod_score:.2f}",
            f"",
            f"--- BEHAVIOR METRICS ---",
            f"Idle Hours: {score.idle_hours:.1f}",
            f"Conduct Flag: {'YES - Issue Reported' if score.conduct_flag else 'NO - Good Standing'}",
            f"Raw Behavior Score: {score.behavior_score_raw:.2f}",
            f"Weighted Behavior Score (10%): {score.weighted_behavior_score:.2f}",
            f"",
            f"--- TASK BREAKDOWN ---",
        ]

        # Add task breakdown
        for task_name, count in sorted(score.task_breakdown.items()):
            report_lines.append(f"  • {task_name}: {count}")

        report_lines.extend([
            f"",
            f"{'=' * 80}",
            f"FINAL PERFORMANCE SCORE: {score.final_performance:.2f}%",
            f"{'=' * 80}",
            f"",
        ])

        return "\n".join(report_lines)

    def generate_statistics_report(self, scores: List[PerformanceScore]) -> str:
        """
        Generate aggregate statistics report.

        Args:
            scores: List of PerformanceScore objects

        Returns:
            Formatted statistics report
        """
        if not scores:
            return "No data available for statistics."

        performances = [s.final_performance for s in scores]
        productivities = [s.weighted_prod_score for s in scores]
        behaviors = [s.weighted_behavior_score for s in scores]

        report_lines = [
            f"\n{'=' * 80}",
            f"TEAM PERFORMANCE STATISTICS",
            f"{'=' * 80}",
            f"",
            f"Total Employees: {len(scores)}",
            f"",
            f"--- PERFORMANCE SCORES ---",
            f"Average: {sum(performances) / len(performances):.2f}%",
            f"Highest: {max(performances):.2f}% ({scores[0].name})",
            f"Lowest: {min(performances):.2f}% ({scores[-1].name})",
            f"",
            f"--- PRODUCTIVITY SCORES ---",
            f"Average: {sum(productivities) / len(productivities):.2f}",
            f"Highest: {max(productivities):.2f}",
            f"Lowest: {min(productivities):.2f}",
            f"",
            f"--- BEHAVIOR SCORES ---",
            f"Average: {sum(behaviors) / len(behaviors):.2f}",
            f"Highest: {max(behaviors):.2f}",
            f"Lowest: {min(behaviors):.2f}",
            f"",
            f"--- PERFORMANCE DISTRIBUTION ---",
        ]

        # Performance distribution
        excellent = len([s for s in scores if s.final_performance >= 90])
        good = len([s for s in scores if 70 <= s.final_performance < 90])
        needs_improvement = len([s for s in scores if s.final_performance < 70])

        report_lines.extend([
            f"Excellent (≥90%): {excellent} ({excellent/len(scores)*100:.1f}%)",
            f"Good (70-89%): {good} ({good/len(scores)*100:.1f}%)",
            f"Needs Improvement (<70%): {needs_improvement} ({needs_improvement/len(scores)*100:.1f}%)",
            f"",
            f"{'=' * 80}",
            f"",
        ])

        return "\n".join(report_lines)

    def export_to_dataframe(self, scores: List[PerformanceScore]) -> pd.DataFrame:
        """
        Convert performance scores to a pandas DataFrame.

        Args:
            scores: List of PerformanceScore objects

        Returns:
            DataFrame with all performance data
        """
        if not scores:
            return pd.DataFrame()

        data = [score.to_dict() for score in scores]
        return pd.DataFrame(data)

    def export_to_csv(self, scores: List[PerformanceScore], output_path: str):
        """
        Export performance scores to a CSV file.

        Args:
            scores: List of PerformanceScore objects
            output_path: Path to save the CSV file
        """
        df = self.export_to_dataframe(scores)
        df.to_csv(output_path, index=False)

    def export_to_excel(self, scores: List[PerformanceScore], output_path: str,
                       include_statistics: bool = True):
        """
        Export performance scores to an Excel file with multiple sheets.

        Args:
            scores: List of PerformanceScore objects
            output_path: Path to save the Excel file
            include_statistics: Whether to include a statistics sheet
        """
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Main performance data
            df = self.export_to_dataframe(scores)
            df.to_excel(writer, sheet_name='Performance Scores', index=False)

            # Statistics sheet
            if include_statistics and scores:
                stats_data = self._calculate_statistics_data(scores)
                stats_df = pd.DataFrame(stats_data)
                stats_df.to_excel(writer, sheet_name='Statistics', index=False)

    def _calculate_statistics_data(self, scores: List[PerformanceScore]) -> dict:
        """
        Calculate statistics data for export.

        Args:
            scores: List of PerformanceScore objects

        Returns:
            Dictionary with statistics
        """
        performances = [s.final_performance for s in scores]
        productivities = [s.weighted_prod_score for s in scores]
        behaviors = [s.weighted_behavior_score for s in scores]

        return {
            "Metric": [
                "Total Employees",
                "Avg Performance",
                "Max Performance",
                "Min Performance",
                "Avg Productivity",
                "Avg Behavior",
            ],
            "Value": [
                len(scores),
                f"{sum(performances) / len(performances):.2f}",
                f"{max(performances):.2f}",
                f"{min(performances):.2f}",
                f"{sum(productivities) / len(productivities):.2f}",
                f"{sum(behaviors) / len(behaviors):.2f}",
            ]
        }

    def generate_comparison_report(self, scores_dict: dict) -> str:
        """
        Generate a comparison report across multiple dates.

        Args:
            scores_dict: Dictionary mapping dates to lists of PerformanceScore objects

        Returns:
            Formatted comparison report
        """
        if not scores_dict:
            return "No data available for comparison."

        report_lines = [
            f"\n{'=' * 80}",
            f"PERFORMANCE COMPARISON REPORT",
            f"{'=' * 80}",
            f"",
        ]

        for date, scores in sorted(scores_dict.items()):
            if not scores:
                continue

            avg_performance = sum(s.final_performance for s in scores) / len(scores)

            report_lines.extend([
                f"Date: {date}",
                f"  Employees: {len(scores)}",
                f"  Average Performance: {avg_performance:.2f}%",
                f"  Top Performer: {scores[0].name} ({scores[0].final_performance:.2f}%)",
                f"",
            ])

        report_lines.append(f"{'=' * 80}\n")

        return "\n".join(report_lines)

    def generate_alert_report(self, scores: List[PerformanceScore],
                             performance_threshold: float = 70.0,
                             behavior_threshold: float = 5.0) -> str:
        """
        Generate an alert report for employees who need attention.

        Args:
            scores: List of PerformanceScore objects
            performance_threshold: Performance % below which to flag
            behavior_threshold: Behavior score below which to flag

        Returns:
            Formatted alert report
        """
        alerts = []

        for score in scores:
            issues = []

            if score.final_performance < performance_threshold:
                issues.append(f"Low performance: {score.final_performance:.2f}%")

            if score.weighted_behavior_score < behavior_threshold:
                issues.append(f"Behavior issues (score: {score.weighted_behavior_score:.2f})")

            if score.idle_hours > 2.0:
                issues.append(f"High idle time: {score.idle_hours:.1f} hours")

            if score.conduct_flag:
                issues.append("Conduct flag raised")

            if issues:
                alerts.append({
                    "employee": score.name,
                    "emp_id": score.emp_id,
                    "date": score.date,
                    "issues": issues,
                })

        if not alerts:
            return "\nNo alerts - All employees meeting standards.\n"

        report_lines = [
            f"\n{'=' * 80}",
            f"PERFORMANCE ALERTS",
            f"{'=' * 80}",
            f"",
        ]

        for alert in alerts:
            report_lines.append(f"Employee: {alert['employee']} ({alert['emp_id']})")
            report_lines.append(f"Date: {alert['date']}")
            report_lines.append(f"Issues:")
            for issue in alert['issues']:
                report_lines.append(f"  • {issue}")
            report_lines.append("")

        report_lines.append(f"Total Alerts: {len(alerts)}")
        report_lines.append(f"{'=' * 80}\n")

        return "\n".join(report_lines)

# Healthrix Productivity System - Automation Engine POC

## Overview

This is a comprehensive **Proof of Concept (POC)** for automating the **Healthrix Productivity System**. It transforms complex Excel-based productivity tracking into a structured, Python-based automation engine that can be deployed as a web application or integrated with platforms like AppSheet.

### Key Features

- **Automated Performance Scoring**: 90% Productivity + 10% Behavior evaluation model
- **Standards Database**: Master lookup table for task scoring and categorization
- **Activity Tracking**: Normalized employee activity logging system
- **Multi-Format Reporting**: Console, CSV, Excel outputs with statistics and alerts
- **Flexible Architecture**: Easily extensible for web deployment

## Problem Statement

The current manual process relies on complex Excel sheets with:
- Merged headers and wide-format data
- Manual score calculations
- Time-consuming report generation
- Difficulty scaling across teams

This POC eliminates these pain points through automation.

## Solution Architecture

### 1. Data Models

#### Standards Database (`models/standards.py`)
- Master table for task scoring
- EC (Effort Category) classification
- Base scores and daily targets
- Configurable and extensible

#### Activity Log (`models/activity.py`)
- Normalized activity entries
- Employee tracking
- Date-based filtering
- Behavioral metrics (idle time, conduct flags)

### 2. Calculation Engine

#### Performance Calculator (`engine/calculator.py`)
Implements the core evaluation formula:

**Productivity Score (90% weight)**
```
Productivity % = (Total Points Earned / Daily Target) × 100
Weighted Score = Productivity % × 0.90
```

**Behavior Score (10% weight)**
```
Base Score = 100
- Deduct: Idle Hours × 10 points
- Deduct: Conduct Flag × 50 points
Weighted Score = Base Score × 0.10
```

**Final Performance**
```
Final % = Weighted Productivity + Weighted Behavior
```

### 3. Reporting System (`engine/reporter.py`)

Multiple report types:
- **Summary Report**: Team overview with rankings
- **Detailed Report**: Individual employee breakdown
- **Statistics Report**: Aggregate metrics
- **Alert Report**: Flags for employees needing attention
- **Comparison Report**: Multi-date analysis
- **Trend Analysis**: Performance over time

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd healthrix

# Install dependencies
pip install -r requirements.txt
```

### Running the Demo

```bash
# Run the comprehensive demo
python scripts/demo.py

# Or run the simple example (matches original POC)
python scripts/simple_example.py
```

### Output

The demo generates:
- Console reports with formatted tables
- CSV exports in `output/` directory
- Excel reports with multiple sheets
- Performance trends and statistics

## Usage Examples

### Basic Usage

```python
from healthrix_automation import (
    StandardsDatabase,
    ActivityLog,
    PerformanceCalculator,
    PerformanceReporter
)

# 1. Initialize standards
standards = StandardsDatabase()

# 2. Load activity data
activity_log = ActivityLog.from_csv('data/sample_activities.csv')

# 3. Calculate performance
calculator = PerformanceCalculator(standards, daily_target_points=400)
scores = calculator.calculate_all_employees('2025-11-03', activity_log)

# 4. Generate report
reporter = PerformanceReporter()
print(reporter.generate_summary_report(scores))
```

### Adding Custom Tasks

```python
standards = StandardsDatabase()

# Add a new task type
standards.add_custom_task(
    task_name="Prior Authorization Review",
    ec_category="EC-1",
    base_score=50,
    target_daily=8
)
```

### Creating Activity Entries

```python
from healthrix_automation.models.activity import ActivityEntry, ActivityLog

log = ActivityLog()

# Add an activity
activity = ActivityEntry(
    date="2025-11-20",
    emp_id="EMP001",
    task_name="Authorization Created",
    count=10,
    idle_hours=0.5,
    conduct_flag=0
)

log.add_activity(activity)
```

### Exporting Reports

```python
reporter = PerformanceReporter()

# Export to CSV
reporter.export_to_csv(scores, 'output/report.csv')

# Export to Excel with statistics
reporter.export_to_excel(scores, 'output/report.xlsx', include_statistics=True)
```

## Project Structure

```
healthrix/
├── healthrix_automation/          # Main package
│   ├── __init__.py
│   ├── models/                    # Data models
│   │   ├── __init__.py
│   │   ├── standards.py          # Task standards database
│   │   └── activity.py           # Activity log and employee models
│   ├── engine/                    # Calculation engine
│   │   ├── __init__.py
│   │   ├── calculator.py         # Performance calculations
│   │   └── reporter.py           # Report generation
│   └── utils/                     # Utilities
│       ├── __init__.py
│       └── helpers.py            # Helper functions
├── data/                          # Sample data
│   ├── sample_employees.csv
│   └── sample_activities.csv
├── scripts/                       # Demo scripts
│   ├── demo.py                   # Comprehensive demo
│   └── simple_example.py         # Simple POC example
├── tests/                         # Unit tests
├── output/                        # Generated reports (created at runtime)
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Deployment Options

### Phase 1: Google Sheets + AppSheet (Fastest)

1. **Database**: Create Google Sheets with tabs:
   - `Activity_Log`
   - `Standards_Ref`
   - `Employee_List`

2. **Interface**: Connect AppSheet
   - Form View for activity logging
   - Virtual Columns for calculations
   - Dashboard View for reports

3. **Automation**: Use AppSheet formulas or integrate this Python engine via Google Apps Script

### Phase 2: Web Application (Scalable)

**Option A: Streamlit (Rapid Prototyping)**
```python
# streamlit_app.py
import streamlit as st
from healthrix_automation import *

st.title("Healthrix Performance Dashboard")
# ... build interface
```

**Option B: Django/FastAPI (Production)**
- RESTful API for activity logging
- PostgreSQL database
- React/Vue.js frontend
- Scheduled jobs for daily calculations

### Phase 3: Enterprise Integration

- Single Sign-On (SSO)
- Role-based access control
- Multi-tenant support
- Advanced analytics and ML predictions

## Sample Output

```
================================================================================
         HEALTHRIX AUTOMATED PERFORMANCE REPORT - 2025-11-03
================================================================================

| Name              | Total Points | Prod Score (Max 90) | Behavior Score (Max 10) | FINAL %  |
|-------------------|--------------|---------------------|-------------------------|----------|
| Emily Chen        | 650          | 146.25              | 10.00                   | 156.25   |
| Waqas Anwar       | 450          | 101.25              | 9.00                    | 110.25   |
| M. Zeeshan        | 380          | 85.50               | 9.50                    | 95.00    |
| Sarah Johnson     | 270          | 60.75               | 8.00                    | 68.75    |
| Ahmed Hassan      | 100          | 22.50               | 2.50                    | 25.00    |
```

## Configuration

### Adjusting Daily Targets

```python
calculator = PerformanceCalculator(
    standards_db,
    daily_target_points=500  # Adjust based on your requirements
)
```

### Modifying Penalties

Edit constants in `engine/calculator.py`:

```python
IDLE_PENALTY_PER_HOUR = 10   # Points deducted per idle hour
CONDUCT_PENALTY = 50         # Points deducted for conduct flag
```

### Custom Weights

```python
PRODUCTIVITY_WEIGHT = 0.90  # 90% weight
BEHAVIOR_WEIGHT = 0.10      # 10% weight
```

## Testing

```bash
# Run tests (when implemented)
pytest tests/

# Run with coverage
pytest --cov=healthrix_automation tests/
```

## Next Steps

1. **Validation**: Test with real production data
2. **Customization**: Adjust standards, targets, and penalties
3. **Web Interface**: Deploy as Streamlit app or Django application
4. **Integration**: Connect to existing HR/payroll systems
5. **Automation**: Set up scheduled daily report generation
6. **Analytics**: Add trend analysis and predictive modeling

## Technical Requirements

- Python 3.8+
- pandas >= 2.0.0
- numpy >= 1.24.0
- tabulate >= 0.9.0
- openpyxl >= 3.1.0 (optional, for Excel export)

## License

Proprietary - Healthrix Automation System

## Support

For questions or issues, contact the development team.

---

**Built with ❤️ for Healthrix Operations Team**

# AppSheet Formulas & Virtual Columns

## Overview

This document contains all the formulas and virtual column definitions needed for the Healthrix Productivity System in AppSheet.

---

## Table: Employee_List

### Virtual Columns

#### 1. Related Activities (Virtual Column)
**Column Name:** `Related_Activities`
**Type:** List of Activity_Log (Ref)
**Formula:**
```
REF_ROWS("Activity_Log", "Emp_ID")
```
**Purpose:** Shows all activities logged by this employee

#### 2. Related Metrics (Virtual Column)
**Column Name:** `Related_Metrics`
**Type:** List of Daily_Metrics (Ref)
**Formula:**
```
REF_ROWS("Daily_Metrics", "Emp_ID")
```
**Purpose:** Shows all daily metrics for this employee

#### 3. Related Scores (Virtual Column)
**Column Name:** `Related_Scores`
**Type:** List of Performance_Scores (Ref)
**Formula:**
```
REF_ROWS("Performance_Scores", "Emp_ID")
```
**Purpose:** Shows all performance scores for this employee

#### 4. Latest Performance
**Column Name:** `Latest_Performance`
**Type:** Number (Decimal)
**Formula:**
```
INDEX(
  SORT(
    SELECT(Performance_Scores[Final_Performance_Percent], [Emp_ID] = [_THISROW].[Emp_ID]),
    Performance_Scores[Date],
    TRUE
  ),
  1
)
```
**Purpose:** Shows most recent performance score

---

## Table: Standards_Ref

### Virtual Columns

#### 1. Related Activities
**Column Name:** `Related_Activities`
**Type:** List of Activity_Log (Ref)
**Formula:**
```
REF_ROWS("Activity_Log", "Task_Name")
```
**Purpose:** Shows all activities using this task

#### 2. Total Usage Count
**Column Name:** `Total_Usage_Count`
**Type:** Number
**Formula:**
```
SUM(
  SELECT(Activity_Log[Count], [Task_Name] = [_THISROW].[Task_Name])
)
```
**Purpose:** Total times this task has been logged

---

## Table: Activity_Log

### App Formulas (Auto-calculated columns)

#### 1. Employee_Name (Auto-fill from Emp_ID)
**Column:** `Employee_Name`
**Type:** Text
**Formula:**
```
[Emp_ID].[Name]
```
**Show:** No
**Editable:** No
**Purpose:** Automatically fills employee name from selected Emp_ID

#### 2. Task_Score (Points earned for this activity)
**Column Name:** `Task_Score`
**Type:** Virtual Column - Number
**Formula:**
```
[Count] *
LOOKUP(
  [Task_Name],
  "Standards_Ref",
  "Task_Name",
  "Base_Score"
)
```
**Purpose:** Calculates points: count × base_score from Standards_Ref

#### 3. EC_Category (Task category)
**Column Name:** `EC_Category`
**Type:** Virtual Column - Text
**Formula:**
```
LOOKUP([Task_Name], "Standards_Ref", "Task_Name", "EC_Category")
```
**Purpose:** Shows the EC category of the selected task

### Initial Values

#### Activity_ID
**Formula:**
```
UNIQUEID()
```

#### Date
**Formula:**
```
TODAY()
```

#### Count
**Formula:**
```
1
```

---

## Table: Daily_Metrics

### App Formulas

#### 1. Employee_Name (Auto-fill)
**Column:** `Employee_Name`
**Type:** Text
**Formula:**
```
[Emp_ID].[Name]
```
**Show:** No
**Editable:** No

### Initial Values

#### Metric_ID
**Formula:**
```
UNIQUEID()
```

#### Date
**Formula:**
```
TODAY()
```

#### Idle_Hours
**Formula:**
```
0
```

#### Conduct_Flag
**Formula:**
```
0
```

---

## Table: Performance_Scores

### Virtual Columns (Calculated Daily)

**NOTE:** These can be calculated via AppSheet virtual columns OR via Google Apps Script automation. For real-time calculation, use virtual columns. For scheduled daily batch calculation, use Apps Script (see APPS_SCRIPT_INTEGRATION.gs).

#### Option A: AppSheet Virtual Columns (Real-Time Calculation)

Create a **Workflow** or **Bot** that runs daily to create Performance_Scores entries.

#### 1. Total_Task_Points
**Column Name:** `Total_Task_Points`
**Type:** Virtual Column - Number
**Formula:**
```
SUM(
  SELECT(Activity_Log[Task_Score],
    AND(
      [Emp_ID] = [_THISROW].[Emp_ID],
      [Date] = [_THISROW].[Date]
    )
  )
)
```
**Purpose:** Sum of all task points for this employee on this date

#### 2. Task_Count
**Column Name:** `Task_Count`
**Type:** Virtual Column - Number
**Formula:**
```
COUNT(
  SELECT(Activity_Log[Activity_ID],
    AND(
      [Emp_ID] = [_THISROW].[Emp_ID],
      [Date] = [_THISROW].[Date]
    )
  )
)
```
**Purpose:** Number of activities logged

#### 3. Idle_Hours
**Column Name:** `Idle_Hours`
**Type:** Virtual Column - Number
**Formula:**
```
MAX(
  SELECT(Daily_Metrics[Idle_Hours],
    AND(
      [Emp_ID] = [_THISROW].[Emp_ID],
      [Date] = [_THISROW].[Date]
    )
  )
)
```
**Purpose:** Gets idle hours from Daily_Metrics (using MAX in case of multiple entries)

**Alternative - with default value:**
```
IF(
  ISBLANK(
    MAX(SELECT(Daily_Metrics[Idle_Hours],
      AND([Emp_ID] = [_THISROW].[Emp_ID], [Date] = [_THISROW].[Date])
    ))
  ),
  0,
  MAX(SELECT(Daily_Metrics[Idle_Hours],
    AND([Emp_ID] = [_THISROW].[Emp_ID], [Date] = [_THISROW].[Date])
  ))
)
```

#### 4. Conduct_Flag
**Column Name:** `Conduct_Flag`
**Type:** Virtual Column - Number
**Formula:**
```
MAX(
  SELECT(Daily_Metrics[Conduct_Flag],
    AND(
      [Emp_ID] = [_THISROW].[Emp_ID],
      [Date] = [_THISROW].[Date]
    )
  )
)
```
**Alternative with default:**
```
IF(
  ISBLANK(
    MAX(SELECT(Daily_Metrics[Conduct_Flag],
      AND([Emp_ID] = [_THISROW].[Emp_ID], [Date] = [_THISROW].[Date])
    ))
  ),
  0,
  MAX(SELECT(Daily_Metrics[Conduct_Flag],
    AND([Emp_ID] = [_THISROW].[Emp_ID], [Date] = [_THISROW].[Date])
  ))
)
```

#### 5. Productivity_Percent
**Column Name:** `Productivity_Percent`
**Type:** Virtual Column - Decimal
**Formula:**
```
([Total_Task_Points] / 400) * 100
```
**Purpose:** Productivity as percentage of 400-point daily target

**Note:** Change 400 to your actual daily target

#### 6. Weighted_Prod_Score
**Column Name:** `Weighted_Prod_Score`
**Type:** Virtual Column - Decimal
**Formula:**
```
[Productivity_Percent] * 0.90
```
**Purpose:** Productivity score with 90% weight

#### 7. Behavior_Score_Raw
**Column Name:** `Behavior_Score_Raw`
**Type:** Virtual Column - Decimal
**Formula:**
```
MAX(
  100 - ([Idle_Hours] * 10) - ([Conduct_Flag] * 50),
  0
)
```
**Purpose:**
- Start with 100
- Deduct 10 points per idle hour
- Deduct 50 points for conduct flag
- Floor at 0

#### 8. Weighted_Behavior_Score
**Column Name:** `Weighted_Behavior_Score`
**Type:** Virtual Column - Decimal
**Formula:**
```
[Behavior_Score_Raw] * 0.10
```
**Purpose:** Behavior score with 10% weight

#### 9. Final_Performance_Percent
**Column Name:** `Final_Performance_Percent`
**Type:** Virtual Column - Decimal
**Formula:**
```
[Weighted_Prod_Score] + [Weighted_Behavior_Score]
```
**Purpose:** **FINAL PERFORMANCE SCORE** = Productivity (90%) + Behavior (10%)

#### 10. Performance_Rating
**Column Name:** `Performance_Rating`
**Type:** Virtual Column - Text
**Formula:**
```
IF(
  [Final_Performance_Percent] >= 90,
  "Excellent",
  IF(
    [Final_Performance_Percent] >= 70,
    "Good",
    IF(
      [Final_Performance_Percent] >= 50,
      "Needs Improvement",
      "Critical"
    )
  )
)
```
**Purpose:** Categorizes performance into ratings

#### 11. Employee_Name (Auto-fill)
**Column:** `Employee_Name`
**Type:** Text
**Formula:**
```
[Emp_ID].[Name]
```

---

## Workflow: Daily Performance Calculation

### Option B: Automated Bot/Workflow

Create a **Bot** with the following configuration:

**Name:** Daily Performance Calculator
**Event:** Data Change → Daily_Metrics (Any Update/Add)
**Condition:**
```
TRUE
```

**Process:**
1. **Step 1:** Find or create Performance_Scores row for this Emp_ID + Date
2. **Step 2:** Execute action "Calculate Performance"

**Action: Calculate Performance**
- Type: Data: execute an action on a set of rows
- Referenced Table: Performance_Scores
- Referenced Rows:
```
SELECT(Performance_Scores[Score_ID],
  AND([Emp_ID] = [_THISROW].[Emp_ID], [Date] = [_THISROW].[Date])
)
```
- Action: Add a new row if not exists / Update if exists

---

## Report Views

### View 1: Employee Daily Summary

**Type:** Dashboard
**For:** Activity_Log table
**Filter:** `[Emp_ID] = USEREMAIL()`
**Group By:** Date
**Summary:**
```
SUM([Task_Score])
```

### View 2: Team Performance Leaderboard

**Type:** Table/Deck
**For:** Performance_Scores table
**Filter:** `[Date] = TODAY()`
**Sort By:** `Final_Performance_Percent` DESC
**Show Columns:**
- Employee_Name
- Final_Performance_Percent
- Performance_Rating
- Total_Task_Points

### View 3: Performance Trend (Chart)

**Type:** Chart (Line)
**For:** Performance_Scores table
**Filter:**
```
AND(
  [Emp_ID] = USEREMAIL(),
  [Date] >= (TODAY() - 30)
)
```
**X-Axis:** Date
**Y-Axis:** Final_Performance_Percent
**Series:** Employee_Name

---

## Actions

### Action 1: Quick Log Activity

**Name:** Quick Log
**Type:** Form
**Behavior:**
- Default Emp_ID to current user: `USEREMAIL()`
- Default Date to `TODAY()`
- Show only: Task_Name, Count, Patient_ID (optional)

### Action 2: Submit Daily Metrics (Supervisor)

**Name:** Submit Metrics
**Type:** Form
**For:** Daily_Metrics table
**Only available if:** `ROLE() = "Supervisor"`

---

## Validation Rules

### Activity_Log

**Count Must Be Positive:**
```
[Count] > 0
```
Error Message: "Count must be greater than 0"

**Date Cannot Be Future:**
```
[Date] <= TODAY()
```
Error Message: "Cannot log activities for future dates"

### Daily_Metrics

**Idle Hours Range:**
```
AND([Idle_Hours] >= 0, [Idle_Hours] <= 8)
```
Error Message: "Idle hours must be between 0 and 8"

**Conduct Flag Values:**
```
OR([Conduct_Flag] = 0, [Conduct_Flag] = 1)
```
Error Message: "Conduct flag must be 0 (Good) or 1 (Issue)"

---

## Formatting Expressions

### Color Coding for Performance

**Background Color for Final_Performance_Percent:**
```
IFS(
  [Final_Performance_Percent] >= 90, "#4CAF50",  // Green - Excellent
  [Final_Performance_Percent] >= 70, "#2196F3",  // Blue - Good
  [Final_Performance_Percent] >= 50, "#FF9800",  // Orange - Needs Improvement
  TRUE, "#F44336"                                 // Red - Critical
)
```

### Icon for Conduct Flag

**Icon Expression for Conduct_Flag (in Daily_Metrics):**
```
IF([Conduct_Flag] = 1, "warning", "check_circle")
```

**Icon Color:**
```
IF([Conduct_Flag] = 1, "#F44336", "#4CAF50")
```

---

## Sample Calculations (Manual Verification)

### Example Data:
- Employee: M. Zeeshan (EMP001)
- Date: 2025-11-20
- Activities:
  - Authorization Created × 8 = 8 × 45 = 360 points
  - Appeal × 2 = 2 × 10 = 20 points
  - **Total: 380 points**
- Idle Hours: 0.5
- Conduct Flag: 0

### Calculation:
1. **Total_Task_Points:** 380
2. **Productivity_%:** (380 / 400) × 100 = 95%
3. **Weighted_Prod_Score:** 95 × 0.90 = 85.5
4. **Behavior_Score_Raw:** 100 - (0.5 × 10) - (0 × 50) = 95
5. **Weighted_Behavior_Score:** 95 × 0.10 = 9.5
6. **Final_Performance_%:** 85.5 + 9.5 = **95.0%**

---

## Troubleshooting

### Issue: Virtual columns not calculating

**Solution:**
1. Verify column types are correct (especially Ref types)
2. Check that table names match exactly (case-sensitive)
3. Re-sync the app data
4. Check for circular references

### Issue: Performance scores not appearing

**Solution:**
1. Ensure Daily_Metrics exists for that employee/date
2. Verify Activity_Log has entries for that date
3. Check that virtual column formulas reference correct table names
4. Manually test formulas in AppSheet expression editor

### Issue: "Cannot find matching row" errors

**Solution:**
1. Verify Emp_ID in Activity_Log matches Employee_List exactly
2. Check Task_Name matches Standards_Ref exactly (case-sensitive)
3. Ensure foreign key relationships are configured correctly

---

## Performance Optimization

For large datasets (>10,000 rows), consider:

1. Use **Apps Script** instead of virtual columns for complex calculations
2. Implement **incremental refresh** for Performance_Scores
3. Archive old data (>90 days) to separate sheet
4. Use **SELECT()** with specific conditions instead of full table scans
5. Schedule Bot to run during off-peak hours

---

## References

- AppSheet Expression Reference: https://help.appsheet.com/en/articles/961489
- AppSheet Virtual Columns: https://help.appsheet.com/en/articles/961547
- AppSheet Workflows: https://help.appsheet.com/en/collections/2002191

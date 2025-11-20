# Phase 1: AppSheet Deployment Guide

## Complete Implementation Roadmap

This guide provides step-by-step instructions to deploy the Healthrix Productivity System using Google Sheets and AppSheet.

**Estimated Time:** 2-4 hours
**Technical Level:** Beginner to Intermediate
**Cost:** Free (using free tiers of Google Sheets and AppSheet)

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Part 1: Google Sheets Setup (30 minutes)](#part-1-google-sheets-setup)
3. [Part 2: Google Apps Script Installation (20 minutes)](#part-2-google-apps-script-installation)
4. [Part 3: AppSheet App Creation (60 minutes)](#part-3-appsheet-app-creation)
5. [Part 4: User Testing (30 minutes)](#part-4-user-testing)
6. [Part 5: Team Deployment (30 minutes)](#part-5-team-deployment)
7. [Troubleshooting](#troubleshooting)
8. [Next Steps](#next-steps)

---

## Prerequisites

### Required Accounts:
- [ ] Google Account (Gmail)
- [ ] AppSheet Account (sign up at appsheet.com - free tier available)

### Required Access:
- [ ] Permission to create Google Sheets
- [ ] Permission to share documents with your team

### Recommended:
- [ ] Basic familiarity with Google Sheets
- [ ] List of employees with their email addresses
- [ ] Current task standards and scoring criteria

---

## Part 1: Google Sheets Setup

### Step 1.1: Create the Spreadsheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Click **"Blank"** to create a new spreadsheet
3. Name it: **"Healthrix Productivity System"**
4. Save and note the URL

### Step 1.2: Import Templates

You have two options:

#### Option A: Manual Import from CSV

1. Download all CSV files from `appsheet_deployment/sheets_templates/`
2. For each CSV file:
   - Create a new sheet (click **+** at bottom)
   - Name it according to the CSV filename (without numbers and extension)
   - File → Import → Upload → Select CSV
   - Import location: "Replace current sheet"
   - Click "Import data"

**Sheet Names (must match exactly):**
- Employee_List
- Standards_Ref
- Activity_Log
- Daily_Metrics
- Performance_Scores

#### Option B: Manual Creation

Follow the detailed column specifications in `appsheet_config/APPSHEET_SETUP.md`

### Step 1.3: Format the Sheets

#### Employee_List Sheet

**Columns:**
```
A: Emp_ID (Text)
B: Name (Text)
C: Department (Text)
D: Role (Text)
E: Email (Email format)
F: Hire_Date (Date format)
G: Status (Text - "Active", "Inactive", etc.)
```

**Formatting:**
1. Select row 1 → Bold + Freeze row
2. Select column E → Format → Number → Plain text (or Email if available)
3. Select column F → Format → Number → Date
4. Select column G → Data → Data validation → List: Active, Inactive, On Leave

**Sample Data:**
Add your employees or use the sample data from the CSV template.

#### Standards_Ref Sheet

**Columns:**
```
A: Task_ID (Text)
B: Task_Name (Text)
C: EC_Category (Text)
D: Base_Score (Number)
E: Target_Daily (Number)
F: Description (Text)
```

**Formatting:**
1. Row 1: Bold + Freeze
2. Columns D-E: Format → Number → Number (0 decimals)
3. Column C: Data validation → List: EC-1, EC-2, EC-3, EC-4, EC-5

**Populate with your task standards** (see template for examples)

#### Activity_Log Sheet

**Columns:**
```
A: Activity_ID (Text - will be auto-generated)
B: Date (Date)
C: Emp_ID (Text - references Employee_List)
D: Employee_Name (Text - auto-filled)
E: Task_Name (Text - references Standards_Ref)
F: Count (Number)
G: Patient_ID (Text - optional)
H: Duration_Minutes (Number - optional)
I: Notes (Text - optional)
```

**Formatting:**
1. Row 1: Bold + Freeze
2. Column B: Format → Date
3. Columns F, H: Format → Number

**Leave data rows empty** - will be populated by users

#### Daily_Metrics Sheet

**Columns:**
```
A: Metric_ID (Text - auto-generated)
B: Date (Date)
C: Emp_ID (Text)
D: Employee_Name (Text - auto-filled)
E: Idle_Hours (Number - decimal)
F: Conduct_Flag (Number - 0 or 1)
G: Conduct_Notes (Text)
H: Supervisor (Text)
```

**Formatting:**
1. Row 1: Bold + Freeze
2. Column B: Format → Date
3. Column E: Format → Number (1 decimal place)
4. Column F: Data validation → List: 0, 1

#### Performance_Scores Sheet

**Columns:**
```
A: Score_ID (Text)
B: Date (Date)
C: Emp_ID (Text)
D: Employee_Name (Text)
E: Total_Task_Points (Number)
F: Productivity_Percent (Number)
G: Weighted_Prod_Score (Number)
H: Behavior_Score_Raw (Number)
I: Weighted_Behavior_Score (Number)
J: Final_Performance_Percent (Number)
K: Task_Count (Number)
L: Idle_Hours (Number)
M: Conduct_Flag (Number)
```

**Formatting:**
1. Row 1: Bold + Freeze
2. All number columns: Format → Number (2 decimal places)

**Leave empty** - will be populated by automation

### Step 1.4: Set Permissions

1. Click **"Share"** button (top right)
2. Add your team members:
   - **Employees**: "Editor" access
   - **Supervisors**: "Editor" access
   - **Managers**: "Editor" or "Owner" access
3. Or set to "Anyone in [YourOrganization] with the link can edit"

---

## Part 2: Google Apps Script Installation

### Step 2.1: Open Script Editor

1. In your Google Sheet, click **Extensions → Apps Script**
2. Delete any default code in the editor
3. Name the project: **"Healthrix Automation"**

### Step 2.2: Add the Script

1. Copy the entire contents of `apps_script/PerformanceCalculator.gs`
2. Paste into the Apps Script editor
3. Click **Save** (Ctrl+S or Cmd+S)

### Step 2.3: Test the Script

1. In the function dropdown, select **"onOpen"**
2. Click **Run**
3. You'll be prompted to authorize:
   - Click "Review Permissions"
   - Select your Google account
   - Click "Advanced" → "Go to Healthrix Automation (unsafe)"
   - Click "Allow"

### Step 2.4: Verify Menu Added

1. Return to your Google Sheet
2. Refresh the page (F5)
3. You should see a new menu: **"Healthrix"**

### Step 2.5: Setup Automation

1. In Google Sheet, click **Healthrix → Setup Automation**
2. Authorize again if prompted
3. Confirm the daily trigger is created
4. You should see: "Performance scores will now be calculated automatically every day at 1:00 AM"

### Step 2.6: Test Manual Calculation

1. Add a test entry to Activity_Log sheet:
   - Activity_ID: TEST001
   - Date: Today's date
   - Emp_ID: EMP001 (or any employee ID you have)
   - Task_Name: Authorization Created (or any task from Standards_Ref)
   - Count: 5

2. Add a test entry to Daily_Metrics sheet:
   - Metric_ID: MET001
   - Date: Today's date
   - Emp_ID: EMP001 (same as above)
   - Idle_Hours: 0.5
   - Conduct_Flag: 0

3. Click **Healthrix → Calculate Today's Performance**

4. Check the Performance_Scores sheet - you should see a new row with calculated scores!

**Expected Result:**
- Total_Task_Points: 225 (5 × 45)
- Productivity_Percent: ~56.25% (225/400)
- Final_Performance_Percent: ~51.12%

If you see this, **automation is working!** ✅

---

## Part 3: AppSheet App Creation

### Step 3.1: Create the App

1. Go to [AppSheet.com](https://www.appsheet.com)
2. Sign in with your Google account
3. Click **"Create"** → **"App"** → **"Start with your own data"**
4. Choose **"Google Sheets"**
5. Find and select your "Healthrix Productivity System" spreadsheet
6. Click **"Create app"**
7. Name your app: **"Healthrix Productivity Tracker"**

AppSheet will automatically detect your tables!

### Step 3.2: Configure Data Structure

Click **"Data"** in the left sidebar:

1. Verify all 5 tables are listed:
   - Employee_List
   - Standards_Ref
   - Activity_Log
   - Daily_Metrics
   - Performance_Scores

2. For **Employee_List**:
   - Click the table name
   - Set "Key" (Primary Key): **Emp_ID**
   - Set "Label": **Name**

3. For **Standards_Ref**:
   - Key: **Task_ID**
   - Label: **Task_Name**

4. For **Activity_Log**:
   - Key: **Activity_ID**
   - Label: Leave as default or set to: `[Employee_Name]`

5. For **Daily_Metrics**:
   - Key: **Metric_ID**
   - Label: `[Employee_Name]`

6. For **Performance_Scores**:
   - Key: **Score_ID**
   - Label: `[Employee_Name]`

### Step 3.3: Configure Column Types

Click **"Data" → "Columns"**

#### Activity_Log Table:

Find and edit these columns:

**Activity_ID:**
- Type: Text
- Initial Value: `UNIQUEID()`
- Show?: No (hidden from users)

**Date:**
- Type: Date
- Initial Value: `TODAY()`

**Emp_ID:**
- Type: Ref
- Source table: **Employee_List**
- Show column: **Name**

**Employee_Name:**
- Type: Formula
- Formula: `[Emp_ID].[Name]`
- Show?: No
- Editable?: No

**Task_Name:**
- Type: Enum
- Values: From **Standards_Ref[Task_Name]**
- Allow other values: No

**Count:**
- Type: Number
- Initial Value: `1`

**Patient_ID:**
- Type: Text
- Required?: No

**Duration_Minutes:**
- Type: Number
- Required?: No

**Notes:**
- Type: LongText
- Required?: No

#### Daily_Metrics Table:

**Metric_ID:**
- Type: Text
- Initial Value: `UNIQUEID()`
- Show?: No

**Date:**
- Type: Date
- Initial Value: `TODAY()`

**Emp_ID:**
- Type: Ref
- Source: Employee_List

**Employee_Name:**
- Type: Formula
- Formula: `[Emp_ID].[Name]`
- Show?: No
- Editable?: No

**Idle_Hours:**
- Type: Decimal
- Initial Value: `0`

**Conduct_Flag:**
- Type: Enum
- Values: `0, 1`
- Base type: Number

### Step 3.4: Add Virtual Columns (Optional)

If you want **real-time** calculation in AppSheet (vs. nightly batch via Apps Script):

See `appsheet_config/APPSHEET_FORMULAS.md` for detailed virtual column formulas.

**Recommended:** Use Apps Script for calculations (better performance with large datasets)

### Step 3.5: Configure Views

Click **"UX"** in left sidebar:

#### Primary Views to Create:

1. **Home Dashboard**
   - Type: Dashboard
   - Add cards showing:
     - Today's activities count
     - Current performance score
     - Team leaderboard

2. **Log Activity** (Form View)
   - Table: Activity_Log
   - Form Mode: Add only
   - Show columns: Date, Emp_ID, Task_Name, Count, Patient_ID, Notes
   - Position: Primary Navigation

3. **My Activities** (Table View)
   - Table: Activity_Log
   - Filter: `[Emp_ID] = USEREMAIL()`
   - Show user's own activities only

4. **My Performance** (Detail View)
   - Table: Performance_Scores
   - Filter: `[Emp_ID] = USEREMAIL()`
   - Shows latest scores

5. **Team Performance** (Table/Chart View)
   - Table: Performance_Scores
   - Filter: `[Date] = TODAY() - 1` (yesterday's scores)
   - Sort: Final_Performance_Percent DESC
   - Only visible to supervisors

6. **Daily Metrics Entry** (Form View)
   - Table: Daily_Metrics
   - Only visible to supervisors

### Step 3.6: Set Up Security

Click **"Settings"** → **"Security"**:

1. **Require sign-in**: Enable
2. **Authentication provider**: Google
3. **Email whitelist**: Add your team's email domain

**Row-Level Security:**

Go to **Data** → **Tables** → Select table → **Security Filter**:

**Activity_Log:**
- ADDS: `TRUE`
- UPDATES: `[Emp_ID] = USEREMAIL()`
- DELETES: `FALSE`
- READS: `[Emp_ID] = USEREMAIL()`

**Performance_Scores:**
- READS: `[Emp_ID] = USEREMAIL()`
- All others: `FALSE` (read-only)

### Step 3.7: Customize Branding

Click **"Settings" → "Brand"**:

1. Upload your logo
2. Set primary color (brand color)
3. Set app icon

### Step 3.8: Test the App

1. Click **"Preview"** icon (top right - looks like a phone)
2. Test logging an activity
3. Test viewing performance scores
4. Test on mobile device (use QR code or install link)

---

## Part 4: User Testing

### Step 4.1: Create Test Accounts

1. Add 2-3 test employees to Employee_List
2. Use real email addresses you can access

### Step 4.2: Test Scenarios

**Scenario 1: Employee Logs Activity**
1. Open app as employee
2. Click "Log Activity"
3. Select task and enter count
4. Submit

**Scenario 2: Supervisor Records Metrics**
1. Open app as supervisor
2. Navigate to Daily Metrics
3. Enter idle hours and conduct flag
4. Submit

**Scenario 3: Performance Calculation**
1. Wait for nightly automation OR
2. Run manually: Healthrix → Calculate Today's Performance
3. Verify scores appear in Performance_Scores sheet
4. Check that they display in AppSheet

### Step 4.3: Validation Checklist

- [ ] Employees can log activities
- [ ] Employee names auto-fill
- [ ] Task dropdowns work
- [ ] Supervisors can log metrics
- [ ] Performance scores calculate correctly
- [ ] Users see only their own data
- [ ] Managers see all data
- [ ] Mobile app works
- [ ] Notifications work (if configured)

---

## Part 5: Team Deployment

### Step 5.1: Prepare Documentation

1. Create a 1-page Quick Start Guide for employees:
   - How to log activities
   - When to log (daily? real-time?)
   - How to view their performance

2. Create a Supervisor Guide:
   - How to log daily metrics
   - When to log (end of day)
   - How to view team performance

### Step 5.2: Training Session

Conduct a 30-minute training:

1. **Demo (10 min):** Show how to log activities
2. **Practice (15 min):** Have everyone log a test activity
3. **Q&A (5 min):** Answer questions

### Step 5.3: Phased Rollout

**Week 1: Pilot Group**
- Deploy to 5-10 employees
- Monitor daily usage
- Collect feedback

**Week 2: Adjust**
- Fix any issues
- Adjust task standards if needed
- Refine workflows

**Week 3: Full Deployment**
- Roll out to entire team
- Send announcement email
- Provide support channel

### Step 5.4: Support Plan

1. **Designate a champion:** 1-2 people who know the system well
2. **Create FAQ:** Common questions and answers
3. **Support channel:** Email, Slack, or Teams channel for questions
4. **Weekly check-ins:** First month, check usage and issues

---

## Troubleshooting

### Issue: AppSheet not seeing Google Sheet

**Solution:**
1. Verify sheet is shared with your Google account
2. In AppSheet, click Data → Re-sync
3. Check that sheet names match exactly (case-sensitive)

### Issue: Auto-calculations not working

**Solution:**
1. Verify Apps Script trigger is set up (Extensions → Apps Script → Triggers)
2. Check script logs for errors (Apps Script → View → Logs)
3. Run manual calculation to test

### Issue: Users can't sign in

**Solution:**
1. Verify email is in Employee_List
2. Check AppSheet security settings allow their domain
3. Ensure they're using correct Google account

### Issue: Performance scores don't match expected

**Solution:**
1. Verify daily target (CONFIG.DAILY_TARGET_POINTS in Apps Script)
2. Check task base scores in Standards_Ref
3. Verify idle hours and conduct flags are correct
4. Run calculation manually and check logs

### Issue: Dropdown lists not populating

**Solution:**
1. Verify reference tables (Employee_List, Standards_Ref) have data
2. Check column types in AppSheet (should be Ref or Enum)
3. Re-sync app data

---

## Next Steps

### Immediate (Week 1):
- [ ] Monitor daily usage
- [ ] Collect user feedback
- [ ] Fix any bugs

### Short Term (Month 1):
- [ ] Add custom reports
- [ ] Configure email notifications
- [ ] Set up dashboard for managers
- [ ] Archive old data

### Long Term (Months 2-3):
- [ ] Analyze performance trends
- [ ] Adjust task standards based on data
- [ ] Add predictive analytics
- [ ] Consider migration to Phase 2 (Web App)

---

## Additional Resources

- **AppSheet Setup Guide:** `appsheet_config/APPSHEET_SETUP.md`
- **Formula Reference:** `appsheet_config/APPSHEET_FORMULAS.md`
- **Apps Script Code:** `apps_script/PerformanceCalculator.gs`
- **Python Engine (for reference):** `../healthrix_automation/`

---

## Support

For technical issues:
1. Check the Troubleshooting section above
2. Review AppSheet documentation: https://help.appsheet.com
3. Contact your implementation team

---

**Congratulations!** 🎉

You've successfully deployed the Healthrix Productivity System on AppSheet!

Your team can now:
- ✅ Log activities in real-time
- ✅ Track performance automatically
- ✅ View insights on mobile and desktop
- ✅ Make data-driven decisions

---

**Next:** Consider Phase 2 deployment for advanced features like:
- Custom web interface
- Advanced analytics
- Integration with payroll systems
- Predictive performance modeling

# AppSheet Setup Guide for Healthrix Productivity System

## Overview

This guide walks you through setting up the Healthrix Productivity System in AppSheet with Google Sheets as the backend database.

## Prerequisites

1. Google Account with Google Sheets access
2. AppSheet account (free tier works fine)
3. The CSV templates from `sheets_templates/` folder

---

## Part 1: Google Sheets Setup

### Step 1: Create a New Google Spreadsheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Name it: **"Healthrix Productivity System"**

### Step 2: Import the Templates

Create the following sheets (tabs) in this order:

#### Sheet 1: Employee_List

1. Create a new sheet named **"Employee_List"**
2. Import `1_Employee_List.csv` or manually create with these columns:
   - `Emp_ID` (Text) - Primary Key
   - `Name` (Text)
   - `Department` (Text)
   - `Role` (Text)
   - `Email` (Email)
   - `Hire_Date` (Date)
   - `Status` (Text) - Active/Inactive

**Formatting:**
- Set row 1 as header (bold, freeze row)
- Format `Hire_Date` column as Date
- Add data validation for `Status`: Active, Inactive, On Leave

#### Sheet 2: Standards_Ref

1. Create a new sheet named **"Standards_Ref"**
2. Import `2_Standards_Ref.csv` or create with columns:
   - `Task_ID` (Text) - Primary Key
   - `Task_Name` (Text)
   - `EC_Category` (Text)
   - `Base_Score` (Number)
   - `Target_Daily` (Number)
   - `Description` (Text)

**Formatting:**
- Set row 1 as header (bold, freeze row)
- Format `Base_Score` and `Target_Daily` as Number (no decimals)
- Add data validation for `EC_Category`: EC-1, EC-2, EC-3, EC-4, EC-5

#### Sheet 3: Activity_Log

1. Create a new sheet named **"Activity_Log"**
2. Import `3_Activity_Log.csv` or create with columns:
   - `Activity_ID` (Text) - Primary Key (auto-generated in AppSheet)
   - `Date` (Date)
   - `Emp_ID` (Text) - Foreign Key to Employee_List
   - `Employee_Name` (Text) - Auto-filled
   - `Task_Name` (Text) - From Standards_Ref
   - `Count` (Number)
   - `Patient_ID` (Text) - Optional
   - `Duration_Minutes` (Number) - Optional
   - `Notes` (Text) - Optional

**Formatting:**
- Set row 1 as header (bold, freeze row)
- Format `Date` column as Date (default to TODAY)
- Format `Count` and `Duration_Minutes` as Number

#### Sheet 4: Daily_Metrics

1. Create a new sheet named **"Daily_Metrics"**
2. Import `4_Daily_Metrics.csv` or create with columns:
   - `Metric_ID` (Text) - Primary Key
   - `Date` (Date)
   - `Emp_ID` (Text) - Foreign Key
   - `Employee_Name` (Text)
   - `Idle_Hours` (Number) - Decimal allowed
   - `Conduct_Flag` (Number) - 0 or 1
   - `Conduct_Notes` (Text)
   - `Supervisor` (Text)

**Formatting:**
- Set row 1 as header (bold, freeze row)
- Format `Date` as Date
- Format `Idle_Hours` as Number (1 decimal place)
- Add data validation for `Conduct_Flag`: 0, 1

#### Sheet 5: Performance_Scores

1. Create a new sheet named **"Performance_Scores"**
2. Import `5_Performance_Scores.csv` or create with columns:
   - `Score_ID` (Text) - Primary Key
   - `Date` (Date)
   - `Emp_ID` (Text)
   - `Employee_Name` (Text)
   - `Total_Task_Points` (Number)
   - `Productivity_Percent` (Number)
   - `Weighted_Prod_Score` (Number)
   - `Behavior_Score_Raw` (Number)
   - `Weighted_Behavior_Score` (Number)
   - `Final_Performance_Percent` (Number)
   - `Task_Count` (Number)
   - `Idle_Hours` (Number)
   - `Conduct_Flag` (Number)

**Formatting:**
- Set row 1 as header (bold, freeze row)
- Format all number columns with 2 decimal places
- This sheet will be populated by AppSheet or Apps Script

### Step 3: Set Up Named Ranges (Optional but Recommended)

1. Select the `Task_Name` column in Standards_Ref (excluding header)
2. Data → Named ranges → Create named range: "TaskNames"
3. Select the `Emp_ID` column in Employee_List (excluding header)
4. Create named range: "EmployeeIDs"

### Step 4: Share the Spreadsheet

1. Click "Share" button
2. Get the shareable link
3. Set to "Anyone with the link can view" (or restrict to your organization)

---

## Part 2: AppSheet App Creation

### Step 1: Create New App

1. Go to [AppSheet](https://www.appsheet.com)
2. Click **"Create"** → **"App"** → **"Start with your own data"**
3. Choose **"Google Sheets"** as data source
4. Select your "Healthrix Productivity System" spreadsheet
5. Name your app: **"Healthrix Productivity Tracker"**

### Step 2: Configure Data Tables

AppSheet will automatically detect your sheets. Verify:

1. **Employee_List**
   - Primary Key: `Emp_ID`
   - Label: `Name`

2. **Standards_Ref**
   - Primary Key: `Task_ID`
   - Label: `Task_Name`

3. **Activity_Log**
   - Primary Key: `Activity_ID` (set to Initial Value: `UNIQUEID()`)
   - Label: `[Date] & " - " & [Employee_Name] & " - " & [Task_Name]`

4. **Daily_Metrics**
   - Primary Key: `Metric_ID` (set to Initial Value: `UNIQUEID()`)
   - Label: `[Date] & " - " & [Employee_Name]`

5. **Performance_Scores**
   - Primary Key: `Score_ID` (set to Initial Value: `UNIQUEID()`)
   - Label: `[Date] & " - " & [Employee_Name]`

### Step 3: Set Up Column Types

Go to **Data** → **Columns** and configure:

#### Activity_Log Table:
- `Activity_ID`: Type = **Text**, Initial Value = `UNIQUEID()`
- `Date`: Type = **Date**, Initial Value = `TODAY()`
- `Emp_ID`: Type = **Ref** → References **Employee_List**
- `Employee_Name`: Type = **Text**, App Formula = `[Emp_ID].[Name]`, Show = No, Editable = No
- `Task_Name`: Type = **Enum**, Base Type = **Ref** → References **Standards_Ref** (Task_Name column)
- `Count`: Type = **Number**, Initial Value = `1`
- `Patient_ID`: Type = **Text**, Optional = Yes
- `Duration_Minutes`: Type = **Number**, Optional = Yes
- `Notes`: Type = **LongText**, Optional = Yes

#### Daily_Metrics Table:
- `Metric_ID`: Type = **Text**, Initial Value = `UNIQUEID()`
- `Date`: Type = **Date**, Initial Value = `TODAY()`
- `Emp_ID`: Type = **Ref** → References **Employee_List**
- `Employee_Name`: Type = **Text**, App Formula = `[Emp_ID].[Name]`, Editable = No
- `Idle_Hours`: Type = **Decimal**, Initial Value = `0`
- `Conduct_Flag`: Type = **Enum**, Values = `0, 1`, Base Type = **Number**
- `Conduct_Notes`: Type = **LongText**, Optional = Yes
- `Supervisor`: Type = **Text**

### Step 4: Configure Views

#### Primary Navigation:
1. **Home** - Dashboard view
2. **Log Activity** - Form view for Activity_Log
3. **Daily Metrics** - Form view for Daily_Metrics (supervisor only)
4. **Performance** - Table/Chart view for Performance_Scores
5. **My Performance** - Filtered view for current user

---

## Part 3: AppSheet Formulas & Virtual Columns

See the file `APPSHEET_FORMULAS.md` for all virtual column definitions and expressions.

---

## Part 4: User Roles & Security

### Step 1: Enable User Authentication

1. Go to **Settings** → **Security**
2. Enable **Require user sign-in**
3. Choose authentication provider (Google recommended)

### Step 2: Create User Roles

Create two roles:

**Role 1: Employee**
- Can add/edit own Activity_Log entries
- Can view own Performance_Scores
- Cannot access Daily_Metrics
- Cannot edit other employees' data

**Role 2: Supervisor**
- Can view all Activity_Log entries
- Can add/edit Daily_Metrics for all employees
- Can view all Performance_Scores
- Can generate reports

### Step 3: Set Up Row-Level Security

#### Activity_Log:
- **ADDS**: `TRUE`
- **UPDATES**: `[Emp_ID] = USEREMAIL()` (employees can only edit their own)
- **DELETES**: `[Emp_ID] = USEREMAIL() AND ROLE() = "Supervisor"`
- **READS**: `[Emp_ID] = USEREMAIL() OR ROLE() = "Supervisor"`

#### Daily_Metrics:
- **All Operations**: `ROLE() = "Supervisor"`

#### Performance_Scores:
- **READS**: `[Emp_ID] = USEREMAIL() OR ROLE() = "Supervisor"`
- **All other operations**: `FALSE` (read-only, populated by automation)

---

## Part 5: Testing

### Test Checklist:

- [ ] Employees can log activities via form
- [ ] Employee name auto-fills from Emp_ID
- [ ] Task dropdown shows all tasks from Standards_Ref
- [ ] Date defaults to today
- [ ] Supervisors can log daily metrics
- [ ] Virtual columns calculate correctly
- [ ] Performance scores are generated
- [ ] Users can only see their own data (unless supervisor)
- [ ] Reports display correctly

---

## Next Steps

1. Review `APPSHEET_FORMULAS.md` for virtual column setup
2. Review `APPS_SCRIPT_INTEGRATION.gs` for automated score calculation
3. Deploy the app to your team
4. Train users on data entry
5. Schedule daily performance calculation

---

## Support

For issues, refer to:
- AppSheet Documentation: https://help.appsheet.com
- Google Sheets Help: https://support.google.com/docs
- Project README: `../README.md`

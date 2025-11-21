#!/usr/bin/env python3
"""
Simple Example - Matching the Original POC
===========================================

This script replicates the exact example from the POC description.
It's a simplified, standalone version to show the core concept.
"""

import pandas as pd

# --- STEP 1: DEFINE STANDARDS (Derived from Source 10 & 11) ---
standards_db = {
    "Authorization Created": {"EC": "EC-1", "Score": 45, "Weight": 0.90},
    "Authorization Status":  {"EC": "EC-1", "Score": 25, "Weight": 0.90},
    "Appeal":                {"EC": "EC-1", "Score": 10, "Weight": 0.90},
    "Eligibility Check":     {"EC": "EC-2", "Score": 20, "Weight": 0.90},
    "Medication Refill":     {"EC": "EC-2", "Score": 20, "Weight": 0.90},
    "Pharmacy Call":         {"EC": "EC-2", "Score": 10, "Weight": 0.90},
    "Document Upload":       {"EC": "EC-5", "Score": 10, "Weight": 0.90}
}

# --- STEP 2: SIMULATE INPUT DATA (Derived from Source 8 & 9) ---
data = [
    {"Date": "2025-11-03", "Emp_ID": "EMP001", "Name": "M. Zeeshan", "Task": "Authorization Created", "Count": 8, "Idle_Hours": 0.5, "Conduct_Flag": 0},
    {"Date": "2025-11-03", "Emp_ID": "EMP001", "Name": "M. Zeeshan", "Task": "Appeal", "Count": 2, "Idle_Hours": 0.5, "Conduct_Flag": 0},
    {"Date": "2025-11-03", "Emp_ID": "EMP002", "Name": "Waqas Anwar", "Task": "Eligibility Check", "Count": 20, "Idle_Hours": 1.0, "Conduct_Flag": 0},
    {"Date": "2025-11-03", "Emp_ID": "EMP002", "Name": "Waqas Anwar", "Task": "Document Upload", "Count": 5, "Idle_Hours": 1.0, "Conduct_Flag": 0},
    {"Date": "2025-11-03", "Emp_ID": "EMP003", "Name": "Bad Behavior Guy", "Task": "Pharmacy Call", "Count": 5, "Idle_Hours": 2.5, "Conduct_Flag": 1},
]

df_activity = pd.DataFrame(data)

# --- STEP 3: CALCULATE PRODUCTIVITY SCORE (The 90% Portion) ---
def calculate_task_score(row):
    task_meta = standards_db.get(row['Task'], {"Score": 0})
    return row['Count'] * task_meta['Score']

df_activity['Total_Task_Points'] = df_activity.apply(calculate_task_score, axis=1)

# Aggregate by Employee
df_performance = df_activity.groupby(['Emp_ID', 'Name']).agg({
    'Total_Task_Points': 'sum',
    'Idle_Hours': 'mean',   # Averaging daily logs for this POC
    'Conduct_Flag': 'max'   # If flagged once, it registers
}).reset_index()

# --- STEP 4: NORMALIZE SCORES (Logic from Source 5) ---
DAILY_TARGET_POINTS = 400

# Calculate Productivity % (Weighted at 90%)
df_performance['Prod_Percentage_Raw'] = (df_performance['Total_Task_Points'] / DAILY_TARGET_POINTS) * 100
df_performance['Weighted_Prod_Score'] = df_performance['Prod_Percentage_Raw'] * 0.90

# --- STEP 5: CALCULATE BEHAVIOR SCORE (The 10% Portion) ---
def calc_behavior(row):
    base_score = 100

    # Penalty: -10 points per idle hour
    base_score -= (row['Idle_Hours'] * 10)

    # Penalty: -50 points for Conduct Flag
    base_score -= (row['Conduct_Flag'] * 50)

    # Floor at 0
    base_score = max(base_score, 0)

    # Apply 10% Weightage
    return base_score * 0.10

df_performance['Weighted_Behavior_Score'] = df_performance.apply(calc_behavior, axis=1)

# --- STEP 6: FINAL EVALUATION ---
df_performance['FINAL_PERFORMANCE_%'] = df_performance['Weighted_Prod_Score'] + df_performance['Weighted_Behavior_Score']

# Formatting for display
display_cols = ['Name', 'Total_Task_Points', 'Weighted_Prod_Score', 'Weighted_Behavior_Score', 'FINAL_PERFORMANCE_%']
print("\n--- HEALTHRIX AUTOMATED PERFORMANCE REPORT ---\n")
print(df_performance[display_cols].round(2).to_markdown(index=False))
print()

/**
 * Healthrix Productivity System - Google Apps Script Integration
 * ==============================================================
 *
 * This script automates performance score calculation in Google Sheets.
 * It implements the 90% Productivity + 10% Behavior formula.
 *
 * INSTALLATION:
 * 1. Open your Google Sheet
 * 2. Extensions → Apps Script
 * 3. Delete any existing code
 * 4. Paste this entire file
 * 5. Save and name the project "Healthrix Automation"
 * 6. Run "setupTriggers" function once to schedule daily calculations
 * 7. Authorize the script when prompted
 *
 * CONFIGURATION:
 * - Modify DAILY_TARGET_POINTS if needed (default: 400)
 * - Modify IDLE_PENALTY and CONDUCT_PENALTY if needed
 * - Schedule in setupTriggers() function
 */

// ============================================================================
// CONFIGURATION CONSTANTS
// ============================================================================

const CONFIG = {
  // Sheet names (must match your Google Sheet tabs exactly)
  SHEETS: {
    EMPLOYEE_LIST: 'Employee_List',
    STANDARDS_REF: 'Standards_Ref',
    ACTIVITY_LOG: 'Activity_Log',
    DAILY_METRICS: 'Daily_Metrics',
    PERFORMANCE_SCORES: 'Performance_Scores'
  },

  // Calculation parameters
  DAILY_TARGET_POINTS: 400,
  PRODUCTIVITY_WEIGHT: 0.90,  // 90%
  BEHAVIOR_WEIGHT: 0.10,      // 10%
  IDLE_PENALTY_PER_HOUR: 10,
  CONDUCT_PENALTY: 50
};

// ============================================================================
// MAIN FUNCTIONS
// ============================================================================

/**
 * Calculate performance scores for all employees for a specific date
 * Default: Yesterday (since today's data may be incomplete)
 *
 * Usage: Run manually or via trigger
 */
function calculateDailyPerformance() {
  try {
    Logger.log('=== Starting Daily Performance Calculation ===');

    // Calculate for yesterday by default
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const targetDate = Utilities.formatDate(yesterday, Session.getScriptTimeZone(), 'yyyy-MM-dd');

    Logger.log('Calculating performance for date: ' + targetDate);

    const result = calculatePerformanceForDate(targetDate);

    Logger.log('=== Calculation Complete ===');
    Logger.log('Employees processed: ' + result.employeesProcessed);
    Logger.log('Scores updated: ' + result.scoresUpdated);

    return result;

  } catch (error) {
    Logger.log('ERROR in calculateDailyPerformance: ' + error.toString());
    sendErrorNotification('Daily Performance Calculation Failed', error);
    throw error;
  }
}

/**
 * Calculate performance for a specific date
 *
 * @param {string} dateString - Date in YYYY-MM-DD format
 * @return {object} Result summary
 */
function calculatePerformanceForDate(dateString) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  // Get all sheets
  const employeeSheet = ss.getSheetByName(CONFIG.SHEETS.EMPLOYEE_LIST);
  const standardsSheet = ss.getSheetByName(CONFIG.SHEETS.STANDARDS_REF);
  const activitySheet = ss.getSheetByName(CONFIG.SHEETS.ACTIVITY_LOG);
  const metricsSheet = ss.getSheetByName(CONFIG.SHEETS.DAILY_METRICS);
  const scoresSheet = ss.getSheetByName(CONFIG.SHEETS.PERFORMANCE_SCORES);

  // Verify all sheets exist
  if (!employeeSheet || !standardsSheet || !activitySheet || !metricsSheet || !scoresSheet) {
    throw new Error('One or more required sheets not found. Check sheet names in CONFIG.');
  }

  // Load data
  const employees = loadEmployees(employeeSheet);
  const standards = loadStandards(standardsSheet);
  const activities = loadActivities(activitySheet, dateString);
  const metrics = loadDailyMetrics(metricsSheet, dateString);

  Logger.log('Loaded: ' + employees.length + ' employees, ' + activities.length + ' activities');

  // Calculate performance for each employee who has activities on this date
  const scores = [];
  const employeesWithActivities = [...new Set(activities.map(a => a.empId))];

  for (const empId of employeesWithActivities) {
    const score = calculateEmployeeScore(
      empId,
      dateString,
      employees,
      standards,
      activities,
      metrics
    );

    if (score) {
      scores.push(score);
    }
  }

  // Write scores to sheet
  const scoresUpdated = writePerformanceScores(scoresSheet, scores, dateString);

  return {
    date: dateString,
    employeesProcessed: employeesWithActivities.length,
    scoresUpdated: scoresUpdated,
    scores: scores
  };
}

// ============================================================================
// DATA LOADING FUNCTIONS
// ============================================================================

/**
 * Load employee data from Employee_List sheet
 */
function loadEmployees(sheet) {
  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  const employees = [];

  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    if (row[0]) { // Has Emp_ID
      employees.push({
        empId: row[0].toString(),
        name: row[1],
        department: row[2],
        role: row[3]
      });
    }
  }

  return employees;
}

/**
 * Load task standards from Standards_Ref sheet
 */
function loadStandards(sheet) {
  const data = sheet.getDataRange().getValues();
  const standards = {};

  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const taskName = row[1]; // Task_Name column

    if (taskName) {
      standards[taskName] = {
        taskId: row[0],
        taskName: taskName,
        ecCategory: row[2],
        baseScore: Number(row[3]),
        targetDaily: Number(row[4])
      };
    }
  }

  return standards;
}

/**
 * Load activities for a specific date
 */
function loadActivities(sheet, dateString) {
  const data = sheet.getDataRange().getValues();
  const activities = [];

  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const activityDate = row[1]; // Date column

    // Convert date to string for comparison
    const activityDateStr = Utilities.formatDate(
      new Date(activityDate),
      Session.getScriptTimeZone(),
      'yyyy-MM-dd'
    );

    if (activityDateStr === dateString && row[2]) { // Has Emp_ID
      activities.push({
        activityId: row[0],
        date: activityDateStr,
        empId: row[2].toString(),
        taskName: row[4],
        count: Number(row[5]) || 1,
        patientId: row[6],
        durationMinutes: Number(row[7]) || 0
      });
    }
  }

  return activities;
}

/**
 * Load daily metrics for a specific date
 */
function loadDailyMetrics(sheet, dateString) {
  const data = sheet.getDataRange().getValues();
  const metrics = {};

  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const metricDate = row[1]; // Date column

    const metricDateStr = Utilities.formatDate(
      new Date(metricDate),
      Session.getScriptTimeZone(),
      'yyyy-MM-dd'
    );

    if (metricDateStr === dateString && row[2]) { // Has Emp_ID
      const empId = row[2].toString();
      metrics[empId] = {
        idleHours: Number(row[4]) || 0,
        conductFlag: Number(row[5]) || 0,
        conductNotes: row[6] || ''
      };
    }
  }

  return metrics;
}

// ============================================================================
// CALCULATION FUNCTIONS
// ============================================================================

/**
 * Calculate performance score for a single employee
 */
function calculateEmployeeScore(empId, dateString, employees, standards, activities, metrics) {
  // Find employee
  const employee = employees.find(e => e.empId === empId);
  if (!employee) {
    Logger.log('WARNING: Employee not found: ' + empId);
    return null;
  }

  // Get employee's activities for this date
  const empActivities = activities.filter(a => a.empId === empId);

  if (empActivities.length === 0) {
    return null;
  }

  // Calculate total task points
  let totalPoints = 0;
  const taskBreakdown = {};

  for (const activity of empActivities) {
    const standard = standards[activity.taskName];
    if (standard) {
      const points = activity.count * standard.baseScore;
      totalPoints += points;

      if (taskBreakdown[activity.taskName]) {
        taskBreakdown[activity.taskName] += activity.count;
      } else {
        taskBreakdown[activity.taskName] = activity.count;
      }
    } else {
      Logger.log('WARNING: No standard found for task: ' + activity.taskName);
    }
  }

  // Get metrics (default to 0 idle hours, 0 conduct flag if not found)
  const empMetrics = metrics[empId] || { idleHours: 0, conductFlag: 0 };

  // Calculate productivity score (90% weight)
  const productivityPercent = (totalPoints / CONFIG.DAILY_TARGET_POINTS) * 100;
  const weightedProdScore = productivityPercent * CONFIG.PRODUCTIVITY_WEIGHT;

  // Calculate behavior score (10% weight)
  let behaviorScoreRaw = 100;
  behaviorScoreRaw -= (empMetrics.idleHours * CONFIG.IDLE_PENALTY_PER_HOUR);
  behaviorScoreRaw -= (empMetrics.conductFlag * CONFIG.CONDUCT_PENALTY);
  behaviorScoreRaw = Math.max(behaviorScoreRaw, 0); // Floor at 0

  const weightedBehaviorScore = behaviorScoreRaw * CONFIG.BEHAVIOR_WEIGHT;

  // Final performance
  const finalPerformance = weightedProdScore + weightedBehaviorScore;

  return {
    scoreId: generateScoreId(empId, dateString),
    date: dateString,
    empId: empId,
    employeeName: employee.name,
    totalTaskPoints: totalPoints,
    productivityPercent: productivityPercent,
    weightedProdScore: weightedProdScore,
    behaviorScoreRaw: behaviorScoreRaw,
    weightedBehaviorScore: weightedBehaviorScore,
    finalPerformancePercent: finalPerformance,
    taskCount: empActivities.length,
    idleHours: empMetrics.idleHours,
    conductFlag: empMetrics.conductFlag
  };
}

/**
 * Generate a unique Score_ID
 */
function generateScoreId(empId, dateString) {
  return 'SCR_' + empId + '_' + dateString.replace(/-/g, '');
}

// ============================================================================
// DATA WRITING FUNCTIONS
// ============================================================================

/**
 * Write performance scores to the Performance_Scores sheet
 * Updates existing rows or appends new ones
 */
function writePerformanceScores(sheet, scores, dateString) {
  if (scores.length === 0) {
    Logger.log('No scores to write');
    return 0;
  }

  // Get existing data
  const existingData = sheet.getDataRange().getValues();
  const headers = existingData[0];

  // Find column indices
  const colIndices = {
    scoreId: 0,
    date: 1,
    empId: 2,
    employeeName: 3,
    totalTaskPoints: 4,
    productivityPercent: 5,
    weightedProdScore: 6,
    behaviorScoreRaw: 7,
    weightedBehaviorScore: 8,
    finalPerformancePercent: 9,
    taskCount: 10,
    idleHours: 11,
    conductFlag: 12
  };

  // Create a map of existing scores by scoreId
  const existingScores = {};
  for (let i = 1; i < existingData.length; i++) {
    const scoreId = existingData[i][colIndices.scoreId];
    if (scoreId) {
      existingScores[scoreId] = i + 1; // Row number (1-indexed)
    }
  }

  let updatedCount = 0;

  for (const score of scores) {
    const rowData = [
      score.scoreId,
      score.date,
      score.empId,
      score.employeeName,
      round2(score.totalTaskPoints),
      round2(score.productivityPercent),
      round2(score.weightedProdScore),
      round2(score.behaviorScoreRaw),
      round2(score.weightedBehaviorScore),
      round2(score.finalPerformancePercent),
      score.taskCount,
      round2(score.idleHours),
      score.conductFlag
    ];

    if (existingScores[score.scoreId]) {
      // Update existing row
      const rowNum = existingScores[score.scoreId];
      sheet.getRange(rowNum, 1, 1, rowData.length).setValues([rowData]);
      Logger.log('Updated score for ' + score.employeeName + ': ' + round2(score.finalPerformancePercent) + '%');
    } else {
      // Append new row
      sheet.appendRow(rowData);
      Logger.log('Added score for ' + score.employeeName + ': ' + round2(score.finalPerformancePercent) + '%');
    }

    updatedCount++;
  }

  return updatedCount;
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Round to 2 decimal places
 */
function round2(num) {
  return Math.round(num * 100) / 100;
}

/**
 * Send error notification email (optional)
 */
function sendErrorNotification(subject, error) {
  try {
    const userEmail = Session.getActiveUser().getEmail();
    if (userEmail) {
      MailApp.sendEmail({
        to: userEmail,
        subject: 'Healthrix Automation Error: ' + subject,
        body: 'An error occurred during automated performance calculation:\n\n' +
              error.toString() + '\n\n' +
              'Stack trace:\n' + error.stack
      });
    }
  } catch (e) {
    Logger.log('Could not send error notification: ' + e.toString());
  }
}

// ============================================================================
// TRIGGER SETUP
// ============================================================================

/**
 * Set up automatic triggers for daily calculation
 *
 * RUN THIS FUNCTION ONCE to enable automation:
 * 1. Select "setupTriggers" from function dropdown
 * 2. Click Run
 * 3. Authorize when prompted
 */
function setupTriggers() {
  // Remove any existing triggers first
  removeTriggers();

  // Create a daily trigger at 1:00 AM
  ScriptApp.newTrigger('calculateDailyPerformance')
    .timeBased()
    .atHour(1)
    .everyDays(1)
    .create();

  Logger.log('Trigger created: Daily performance calculation at 1:00 AM');

  SpreadsheetApp.getUi().alert(
    'Automation Enabled',
    'Performance scores will now be calculated automatically every day at 1:00 AM.\n\n' +
    'You can also run calculations manually using the "Healthrix" menu.',
    SpreadsheetApp.getUi().ButtonSet.OK
  );
}

/**
 * Remove all existing triggers
 */
function removeTriggers() {
  const triggers = ScriptApp.getProjectTriggers();
  for (const trigger of triggers) {
    ScriptApp.deleteTrigger(trigger);
  }
  Logger.log('Removed ' + triggers.length + ' existing trigger(s)');
}

// ============================================================================
// CUSTOM MENU
// ============================================================================

/**
 * Add custom menu to spreadsheet
 * This runs automatically when the spreadsheet is opened
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('Healthrix')
    .addItem('Calculate Today\'s Performance', 'calculateTodayPerformance')
    .addItem('Calculate Yesterday\'s Performance', 'calculateDailyPerformance')
    .addItem('Recalculate Date Range...', 'showDateRangeDialog')
    .addSeparator()
    .addItem('Setup Automation', 'setupTriggers')
    .addItem('Remove Automation', 'removeTriggers')
    .addSeparator()
    .addItem('View Documentation', 'showDocumentation')
    .addToUi();
}

/**
 * Calculate performance for today
 */
function calculateTodayPerformance() {
  const today = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd');
  Logger.log('Calculating performance for today: ' + today);

  const result = calculatePerformanceForDate(today);

  SpreadsheetApp.getUi().alert(
    'Calculation Complete',
    'Processed ' + result.employeesProcessed + ' employees for ' + today + '\n' +
    'Updated ' + result.scoresUpdated + ' performance scores.',
    SpreadsheetApp.getUi().ButtonSet.OK
  );
}

/**
 * Show dialog for date range calculation
 */
function showDateRangeDialog() {
  const ui = SpreadsheetApp.getUi();

  const startDateResponse = ui.prompt(
    'Calculate Date Range',
    'Enter start date (YYYY-MM-DD):',
    ui.ButtonSet.OK_CANCEL
  );

  if (startDateResponse.getSelectedButton() !== ui.Button.OK) {
    return;
  }

  const endDateResponse = ui.prompt(
    'Calculate Date Range',
    'Enter end date (YYYY-MM-DD):',
    ui.ButtonSet.OK_CANCEL
  );

  if (endDateResponse.getSelectedButton() !== ui.Button.OK) {
    return;
  }

  const startDate = startDateResponse.getResponseText();
  const endDate = endDateResponse.getResponseText();

  ui.alert('Processing...', 'Calculating performance for date range. This may take a moment.', ui.ButtonSet.OK);

  const result = calculateDateRange(startDate, endDate);

  ui.alert(
    'Calculation Complete',
    'Processed ' + result.datesProcessed + ' dates\n' +
    'Total scores updated: ' + result.totalScoresUpdated,
    ui.ButtonSet.OK
  );
}

/**
 * Calculate performance for a date range
 */
function calculateDateRange(startDateStr, endDateStr) {
  const startDate = new Date(startDateStr);
  const endDate = new Date(endDateStr);

  let currentDate = new Date(startDate);
  let datesProcessed = 0;
  let totalScoresUpdated = 0;

  while (currentDate <= endDate) {
    const dateStr = Utilities.formatDate(currentDate, Session.getScriptTimeZone(), 'yyyy-MM-dd');
    Logger.log('Processing date: ' + dateStr);

    const result = calculatePerformanceForDate(dateStr);
    datesProcessed++;
    totalScoresUpdated += result.scoresUpdated;

    currentDate.setDate(currentDate.getDate() + 1);
  }

  return {
    datesProcessed: datesProcessed,
    totalScoresUpdated: totalScoresUpdated
  };
}

/**
 * Show documentation
 */
function showDocumentation() {
  const ui = SpreadsheetApp.getUi();
  const html = HtmlService.createHtmlOutput(
    '<h2>Healthrix Performance System</h2>' +
    '<p>This automation calculates employee performance scores based on:</p>' +
    '<ul>' +
    '<li><strong>90% Productivity</strong>: Task completion vs. daily target</li>' +
    '<li><strong>10% Behavior</strong>: Idle time and conduct penalties</li>' +
    '</ul>' +
    '<h3>Usage:</h3>' +
    '<ol>' +
    '<li>Employees log activities in the Activity_Log sheet</li>' +
    '<li>Supervisors record metrics in the Daily_Metrics sheet</li>' +
    '<li>Performance is calculated automatically each night at 1:00 AM</li>' +
    '<li>View results in the Performance_Scores sheet</li>' +
    '</ol>' +
    '<p>For full documentation, see the repository README.</p>'
  ).setWidth(500).setHeight(400);

  ui.showModalDialog(html, 'Healthrix Documentation');
}

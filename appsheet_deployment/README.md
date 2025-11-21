# AppSheet Deployment Package

## Overview

This directory contains everything needed to deploy the Healthrix Productivity System using **Google Sheets** and **AppSheet** (Phase 1).

This is the **fastest, lowest-cost deployment option** - perfect for getting started quickly without custom development.

---

## What's Included

### 📁 Directory Structure

```
appsheet_deployment/
├── README.md                           # This file
├── PHASE1_DEPLOYMENT_GUIDE.md         # Complete step-by-step guide
├── QUICK_REFERENCE.md                 # User quick reference card
│
├── sheets_templates/                   # Google Sheets import templates
│   ├── 1_Employee_List.csv
│   ├── 2_Standards_Ref.csv
│   ├── 3_Activity_Log.csv
│   ├── 4_Daily_Metrics.csv
│   └── 5_Performance_Scores.csv
│
├── appsheet_config/                    # AppSheet configuration
│   ├── APPSHEET_SETUP.md              # Detailed setup instructions
│   └── APPSHEET_FORMULAS.md           # Virtual columns & formulas
│
├── apps_script/                        # Google Apps Script automation
│   └── PerformanceCalculator.gs       # Automated calculation script
│
└── documentation/                      # Additional docs
    └── (supplementary materials)
```

---

## Quick Start

### Option 1: Full Deployment (Recommended)

Follow the complete guide: **[PHASE1_DEPLOYMENT_GUIDE.md](PHASE1_DEPLOYMENT_GUIDE.md)**

**Time:** 2-4 hours
**Result:** Fully functional app with automation

### Option 2: Google Sheets Only (Fastest)

If you just want to start with Google Sheets without AppSheet:

1. Create a new Google Sheet
2. Import the 5 CSV templates from `sheets_templates/`
3. Install the Apps Script from `apps_script/PerformanceCalculator.gs`
4. Use the built-in menu: "Healthrix" for manual calculations

**Time:** 30 minutes
**Result:** Automated Google Sheets system (no mobile app)

### Option 3: AppSheet Only (No Automation)

If you want the mobile app but not automated calculations:

1. Set up Google Sheets (as above)
2. Follow **APPSHEET_SETUP.md** to create the app
3. Use AppSheet virtual columns for real-time calculation (see APPSHEET_FORMULAS.md)

**Time:** 1-2 hours
**Result:** Mobile app with real-time calculations (slower with large datasets)

---

## Prerequisites

### Required:
- Google Account (free)
- AppSheet Account (free tier available)
- Access to Google Sheets

### Recommended:
- List of employees with email addresses
- Current task standards and scoring criteria
- Admin access to share documents

---

## Deployment Steps

### 1. Google Sheets Setup

**Goal:** Create the database

**Steps:**
1. Create new Google Spreadsheet
2. Import CSV templates OR create sheets manually
3. Add your employees to Employee_List
4. Configure task standards in Standards_Ref
5. Set permissions

**Guide:** See `appsheet_config/APPSHEET_SETUP.md` Part 1

**Time:** 30 minutes

### 2. Apps Script Installation

**Goal:** Enable automated performance calculation

**Steps:**
1. Open Apps Script editor (Extensions → Apps Script)
2. Copy/paste code from `apps_script/PerformanceCalculator.gs`
3. Save and authorize
4. Run "setupTriggers" to enable daily automation

**Guide:** See `PHASE1_DEPLOYMENT_GUIDE.md` Part 2

**Time:** 20 minutes

### 3. AppSheet App Creation

**Goal:** Build mobile/web interface

**Steps:**
1. Create new app in AppSheet
2. Connect to your Google Sheet
3. Configure data types and relationships
4. Set up views (forms, dashboards, reports)
5. Configure security

**Guide:** See `appsheet_config/APPSHEET_SETUP.md`

**Time:** 60-90 minutes

### 4. Testing & Deployment

**Goal:** Verify and roll out to team

**Steps:**
1. Test with sample data
2. Train pilot users
3. Collect feedback
4. Roll out to full team

**Guide:** See `PHASE1_DEPLOYMENT_GUIDE.md` Parts 4-5

**Time:** 1-2 weeks (including pilot)

---

## Key Features

### What You Get:

✅ **Mobile App** - Log activities on phones/tablets
✅ **Real-time Data** - See performance instantly
✅ **Automated Scoring** - Calculations run nightly
✅ **Dashboards** - Visual performance tracking
✅ **Role-Based Security** - Employees see only their data
✅ **Team Leaderboards** - See top performers
✅ **Trend Analysis** - Track performance over time
✅ **Zero Infrastructure** - No servers to manage
✅ **Free/Low Cost** - Uses free tiers

### What's Calculated:

- **Productivity Score** (90%): Tasks completed vs. daily target
- **Behavior Score** (10%): Penalties for idle time & conduct
- **Final Performance**: Combined score (0-100%+)
- **Performance Ratings**: Excellent, Good, Needs Improvement, Critical

---

## Configuration

### Adjusting Settings

**Daily Target Points:**
- Default: 400 points = 100% productivity
- Change in: `apps_script/PerformanceCalculator.gs` → `CONFIG.DAILY_TARGET_POINTS`

**Behavior Penalties:**
- Idle time: 10 points per hour (default)
- Conduct flag: 50 points (default)
- Change in: `apps_script/PerformanceCalculator.gs` → `CONFIG`

**Task Standards:**
- Edit in Google Sheet: Standards_Ref tab
- Changes take effect immediately

**Weights:**
- Productivity: 90% (default)
- Behavior: 10% (default)
- Change in: `apps_script/PerformanceCalculator.gs` → `CONFIG`

---

## User Roles

### Employee Role

**Can:**
- Log their own activities
- View their own performance scores
- See their performance trend

**Cannot:**
- View other employees' data
- Edit daily metrics
- Access admin functions

### Supervisor Role

**Can:**
- Everything employees can do
- Log daily metrics (idle time, conduct)
- View all employees' activities
- View team performance dashboard
- Generate reports

**Cannot:**
- Edit performance scores (auto-calculated)
- Change task standards (must edit Google Sheet)

### Admin Role

**Can:**
- Everything supervisors can do
- Edit task standards
- Manage employee list
- Configure automation
- Access all data

---

## Maintenance

### Daily:
- ✅ Automated (no action required)
- Performance scores calculate at 1:00 AM automatically

### Weekly:
- Review team performance trends
- Check for any anomalies
- Address low performers

### Monthly:
- Review and adjust task standards if needed
- Archive old data (optional)
- Update employee list (new hires, departures)

### Quarterly:
- Analyze performance trends
- Adjust daily targets based on data
- Collect user feedback for improvements

---

## Troubleshooting

### Common Issues:

**Scores not calculating?**
→ Check Apps Script trigger is enabled (Extensions → Apps Script → Triggers)

**Can't sign in to app?**
→ Verify email is in Employee_List sheet

**Dropdown lists empty?**
→ Check Standards_Ref and Employee_List have data

**Scores seem wrong?**
→ Verify task base scores and daily target (400)

For more: See **PHASE1_DEPLOYMENT_GUIDE.md** Troubleshooting section

---

## Support & Resources

### Documentation:
- **Main Guide:** `PHASE1_DEPLOYMENT_GUIDE.md`
- **Setup Details:** `appsheet_config/APPSHEET_SETUP.md`
- **Formulas:** `appsheet_config/APPSHEET_FORMULAS.md`
- **User Guide:** `QUICK_REFERENCE.md`

### External Resources:
- AppSheet Help: https://help.appsheet.com
- Google Sheets Help: https://support.google.com/docs
- Apps Script Docs: https://developers.google.com/apps-script

### Community:
- AppSheet Community: https://community.appsheet.com
- Google Sheets Reddit: r/googlesheets

---

## Cost Estimate

### Free Tier (for small teams <10 users):
- Google Sheets: **Free**
- Apps Script: **Free**
- AppSheet: **Free** (up to 10 users)
- **Total: $0/month**

### Paid Tier (for larger teams):
- Google Workspace: **$6-18/user/month** (if not already using)
- AppSheet: **$5-10/user/month**
- **Total: ~$11-28/user/month**

### ROI:
- Saves ~2 hours/week on manual tracking per manager
- Cost per manager: ~$50-100/month (at 2 hours @ $25-50/hr)
- **ROI: 2-5x within first month**

---

## Migration Path

### Phase 1 → Phase 2 (Web App)

When you're ready to scale, migrate to a custom web application:

**Benefits of Phase 2:**
- Full customization
- Better performance with large datasets (1000+ users)
- Advanced analytics & ML predictions
- Integration with payroll/HR systems
- Custom branding

**Migration:**
1. Export data from Google Sheets
2. Import into PostgreSQL database
3. Deploy Python backend (FastAPI/Django)
4. Build React/Vue.js frontend
5. Transition users gradually

**Timeline:** 4-8 weeks
**Cost:** $5,000-$20,000 (one-time development)

---

## Success Metrics

Track these to measure success:

### Adoption:
- [ ] % of employees logging daily
- [ ] % of supervisors logging metrics
- [ ] Daily active users

### Quality:
- [ ] Data accuracy (spot checks)
- [ ] Time to log activities (<2 min)
- [ ] User satisfaction score

### Impact:
- [ ] Time saved on manual tracking
- [ ] Improved performance visibility
- [ ] Better employee recognition
- [ ] Data-driven decision making

---

## Next Steps

1. **Read the deployment guide:** `PHASE1_DEPLOYMENT_GUIDE.md`
2. **Set up Google Sheets:** Import templates
3. **Install automation:** Add Apps Script
4. **Create AppSheet app:** Follow setup guide
5. **Train users:** Share Quick Reference
6. **Deploy to team:** Start with pilot group
7. **Monitor & iterate:** Collect feedback and improve

---

## Questions?

Review the **PHASE1_DEPLOYMENT_GUIDE.md** for detailed answers and troubleshooting.

---

**Ready to get started?**

👉 Open **[PHASE1_DEPLOYMENT_GUIDE.md](PHASE1_DEPLOYMENT_GUIDE.md)** and follow Step 1!

Good luck with your deployment! 🚀

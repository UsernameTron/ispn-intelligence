# Genesys Cloud CX Reporting Quick Start Guide

## Weekly Scorecard Data Collection Checklist

### Before You Begin
- [ ] Confirm the reporting week (Sunday–Saturday or Monday–Sunday)
- [ ] Verify you have access to all 4 export locations
- [ ] Ensure timezone consistency (Central Time)

### Step 1: Interactions Export

**Location:** Performance → Workspace → Interactions → Export

**Filters:**
- Media Type: Voice
- Direction: Inbound, Outbound (select both)
- Date Range: [Your scorecard week]

**Required Fields:**
```
✓ Conversation ID    ✓ Total Queue
✓ Date               ✓ Total Alert
✓ Direction          ✓ Total Handle
✓ Media Type         ✓ Total Talk
✓ Queue              ✓ Total ACW
✓ Users - Interacted ✓ Total Hold
✓ Abandoned          ✓ Transfers
✓ Disconnect Type
✓ Flow-Out Type
✓ Wrap-up
✓ Transferred
✓ Non-ACD
✓ First Queue
```

**Save as:** `Interactions_Export_[YYYY-MM-DD].csv`

---

### Step 2: Agent Status Duration Details

**Location:** Performance → Workspace → Contact Center → Agent Status → Export

**Export Type:** Select "Agent Status Duration Details"

**Filters:**
- Date Range: [Same week as Interactions]

**Required Fields:**
```
✓ Agent Name         ✓ Training
✓ Agent Id           ✓ Break
✓ Email              ✓ Meal
✓ Department         ✓ Meeting
✓ Division Name      ✓ Away
✓ Logged In          ✓ System Away
✓ On Queue           ✓ Interacting
✓ Off Queue          ✓ Idle
✓ On Queue %         ✓ Occupancy
```

**Save as:** `Agent_Status_[YYYY-MM-DD].csv`

---

### Step 3: WFM Historical Adherence

**Location:** WFM → Historical Adherence → Export

**Filters:**
- Date Range: [Same week as Interactions]
- Management Unit: Permanent Schedules MU

**Required Fields:**
```
✓ Agent                         ✓ Scheduled Minutes
✓ Management Unit               ✓ Actual Time
✓ Adherence (%)                 ✓ Scheduled On Queue
✓ Conformance (%)               ✓ Work Time On Queue
✓ Exceptions                    ✓ Scheduled (Adherence)
✓ Exceptions Duration Minutes
✓ Exceptions Duration (Adherence)
✓ Net Impact
```

**Save as:** `Adherence_[YYYY-MM-DD].csv`

---

### Step 4: Agent Performance

**Location:** Performance → Workspace → Agents Performance → Export

**Filters:**
- Date Range: [Same week as Interactions]
- Media Type: Voice

**Required Fields:**
```
✓ Agent Name         ✓ Avg Handle
✓ Agent Id           ✓ Avg Talk
✓ Department         ✓ Avg Hold
✓ Email              ✓ Avg ACW
✓ Handle             ✓ ASA
✓ Total Handle       ✓ Outbound
✓ Total Talk         ✓ Transferred
✓ Total Hold         ✓ Alert - No Answer
✓ Total ACW
✓ Total Alert
```

**Save as:** `Agent_Performance_[YYYY-MM-DD].csv`

---

## Quick Calculations

### AHT Calculation
```
Filter Interactions to:
- Direction = "Inbound"
- Abandoned = "NO"
- Total Handle >= 20000

AHT (minutes) = AVERAGE(Total Handle) / 60000
```

### Callback Count
```
Filter Interactions to:
- Media Type = "callback"

Callback Count = COUNT(*)
```

### Shrinkage Percentage
```
From Agent Status (filter Department = "Tech Center"):

Training Hours = SUM(Training) / 3600000
Total Hours = SUM(Logged In) / 3600000
On Queue Hours = SUM(On Queue) / 3600000

Hours Worked (excl training) = Total Hours - Training Hours
Shrinkage Hours = Hours Worked (excl training) - On Queue Hours
Shrinkage % = Shrinkage Hours / Hours Worked (excl training)
```

### Utilization Percentage
```
Inbound Hours = (from Interactions calculation)
Hours Worked (excl training) = (from Agent Status calculation)

Utilization % = Inbound Hours / Hours Worked (excl training)
```

---

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| AHT too high | Including short calls | Apply Total Handle >= 20000 filter |
| Callbacks = 0 | Wrong filter | Use Media Type = "callback" |
| Utilization very low | Date range mismatch | Align all export date ranges |
| Missing agents | Department filter | Filter Department = "Tech Center" |
| Wrong units | Time conversion error | Interactions/Status = ms, Adherence = minutes |

---

## Scorecard Row Quick Reference

| Row | Metric | Export | Key Filter |
|-----|--------|--------|------------|
| 19 | AHT | Interactions | Inbound, Handled, ≥20s |
| 22 | Inbound Count | Interactions | Inbound, Handled, ≥20s |
| 23 | AWT | Interactions | All Inbound |
| 24-27 | Answer Thresholds | Interactions | Total Alert ≤ threshold |
| 28 | Abandoned | Interactions | Queue ≥ 60s |
| 29 | Outbound Count | Interactions | Direction=Outbound, voice |
| 31 | Callbacks | Interactions | Media Type=callback |
| 59 | Training Hours | Agent Status | Tech Center |
| 60 | Hours Worked | Agent Status | Tech Center |
| 62 | On-Queue Hours | Agent Status | Tech Center |
| 64 | Shrinkage % | Derived | — |
| 66 | Utilization | Derived | — |
| 67 | Occupancy | Derived | — |

---

## Excel Formulas for Scorecard

### If importing raw exports to Excel:

**AHT (assuming data in columns with headers):**
```excel
=AVERAGEIFS(TotalHandle,Direction,"Inbound",Abandoned,"NO",TotalHandle,">=20000")/60000
```

**Inbound Count:**
```excel
=COUNTIFS(Direction,"Inbound",Abandoned,"NO",TotalHandle,">=20000")
```

**AWT:**
```excel
=AVERAGEIF(Direction,"Inbound",TotalQueue)/1000
```

**Callback Count:**
```excel
=COUNTIF(MediaType,"callback")
```

**Tech Center Hours Worked:**
```excel
=SUMIF(Department,"Tech Center",LoggedIn)/3600000
```

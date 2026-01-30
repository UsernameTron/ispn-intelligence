# ISPN Calculation Methodology
**Source:** ISPN Network Services Tech Center Scorecard Standards

Standardized KPI calculations for consistent reporting across ISPN Tech Center operations.

---

## Core Principle

**All metrics use the same formulas regardless of reporting period:**
- Weekly reports
- Monthly reports
- Quarterly reports
- Ad-hoc analysis

**Consistency ensures:**
- Apples-to-apples comparisons
- Trend analysis validity
- Stakeholder confidence in data

---

## Call Metrics

### Average Handle Time (AHT)

**Formula:**
```
AHT = Total Handle Time ÷ Number of Handled Calls
```

**Filters:**
```
Include only:
- Direction = Inbound
- Abandoned = No
- Handle Time >= 20 seconds
```

**Output:** Minutes

**ISPN Target:** <10.7 minutes

**Notes:**
- 20-second threshold excludes test calls and disconnects
- Inbound only (excludes outbound campaigns, callbacks counted separately)
- Handle time includes: Talk + Hold + ACW

**Data source:** Genesys Interactions Export

---

### Average Wait Time (AWT)

**Formula:**
```
AWT = Total Queue Time ÷ Number of Inbound Calls
```

**Filters:**
```
Include:
- All inbound calls (both answered AND abandoned)
```

**Output:** Seconds

**ISPN Target:** <90 seconds

**Notes:**
- More comprehensive than ASA (includes abandons)
- Reflects true customer wait experience
- Queue time = moment call enters queue until answered or abandoned

**Data source:** Genesys Interactions Export

---

### Inbound Call Count

**Formula:**
```
Count of calls where:
- Direction = Inbound
- Abandoned = No
- Handle Time >= 20 seconds
```

**Output:** Integer count

**Notes:**
- Answered and handled calls only
- Excludes abandoned calls (tracked separately)
- Excludes <20 second calls (wrong numbers, disconnects)

**Data source:** Genesys Interactions Export

---

### Callback Count

**Formula:**
```
Count of calls where:
- Media Type = callback
```

**Output:** Integer count

**Notes:**
- Callbacks requested by customers (not abandoned calls)
- Callbacks later delivered to agents as outbound calls
- Track to ensure callback completion

**Data source:** Genesys Interactions Export

---

### Outbound Call Count

**Formula:**
```
Count of calls where:
- Direction = Outbound
- Media Type = voice
```

**Output:** Integer count

**Notes:**
- Agent-initiated calls
- Includes callback deliveries to customers
- Excludes automated dialers (if any)

**Data source:** Genesys Interactions Export

---

### Abandoned Call Count

**Formula:**
```
Count of calls where:
- Direction = Inbound
- Abandoned = Yes
- Queue Time >= 60 seconds
```

**Output:** Integer count

**ISPN Standard:** 60-second threshold

**Notes:**
- Excludes short abandons (<60 seconds)
- Short abandons typically wrong numbers or accidental dials
- 60-second threshold aligns with customer patience expectations

**Derived metric:**
```
Abandon Rate = (Abandoned Call Count ÷ (Inbound Call Count + Abandoned Call Count)) × 100
```

**ISPN Target:** <5%

**Data source:** Genesys Interactions Export

---

### Service Level (Calls Answered Within Threshold)

**Formula:**
```
Count of handled calls where:
- Alert Time <= threshold (30/60/90/120 seconds)
```

**Service Level % calculation:**
```
SL% = (Answered Within Threshold ÷ Total Answered Calls) × 100
```

**Threshold:** Varies by queue
- Standard: 80% in 60 seconds
- Premium: 80% in 30 seconds
- Overflow: 70% in 120 seconds

**Notes:**
- ISPN excludes abandoned calls from denominator
- ISPN excludes short abandons (<60 sec) from SL calculation
- Alert Time = queue wait time until agent picked up

**Data source:** Genesys Interactions Export

---

## Workforce Metrics

**CRITICAL:** All workforce metrics filter to `Department = Tech Center`

This ensures only ISPN Network Services Tech Center agents are included in calculations.

---

### On-Queue Hours

**Formula:**
```
Sum of On Queue time for all Tech Center agents
```

**Filters:**
```
Where:
- Department = Tech Center
```

**Output:** Hours (decimal)

**Notes:**
- On Queue = agent logged in and available to take ACD calls
- Includes both idle time and interacting time
- Denominator for Occupancy calculation

**Data source:** Genesys Agent Status Duration Details

---

### Training Hours

**Formula:**
```
Sum of Training time for all Tech Center agents
```

**Filters:**
```
Where:
- Department = Tech Center
- Status = Training
```

**Output:** Hours (decimal)

**Notes:**
- Formal training activities
- Excluded from Utilization and Shrinkage calculations
- Tracked separately to measure investment in development

**Data source:** Genesys Agent Status Duration Details

---

### Shrinkage %

**Formula:**
```
Shrinkage = ((Logged In - Training - On Queue) ÷ (Logged In - Training)) × 100
```

**Expanded:**
```
Shrinkage = (Break + Meal + Meeting + Other Non-Productive) ÷ (Logged In - Training) × 100
```

**Filters:**
```
Where:
- Department = Tech Center
```

**Output:** Percentage

**ISPN Target:** ≤20%

**Interpretation:**
- Shrinkage = time paid but not available for productive work
- Includes: breaks, meals, meetings, system issues, unplanned unavailability
- Does NOT include training (tracked separately)

**Typical shrinkage components:**
- Breaks/Meals: 10-12%
- Meetings: 3-5%
- System issues: 2-3%
- Other: 1-2%

**Notes:**
- High shrinkage (>25%) indicates scheduling inefficiency or excessive non-productive time
- Low shrinkage (<15%) may indicate burnout risk (insufficient breaks)

**Data source:** Genesys Agent Status Duration Details

---

### Utilization %

**Formula:**
```
Utilization = (Inbound Call Hours ÷ (Logged In - Training)) × 100
```

**Filters:**
```
Where:
- Department = Tech Center
```

**Output:** Percentage

**ISPN Target:** >55%

**Interpretation:**
- Utilization = percentage of paid time spent on primary work (inbound calls)
- Higher = more time on core activity
- Lower = more time on support activities (outbound, projects, idle)

**Calculation steps:**
1. Calculate total inbound call hours (sum of handle times for inbound calls)
2. Calculate total logged-in hours minus training hours
3. Divide and multiply by 100

**Notes:**
- Does NOT count outbound calls (tracked separately)
- Does NOT count callbacks (tracked separately)
- Only inbound ACD calls in numerator

**Data source:** 
- Numerator: Genesys Interactions Export (inbound handle times)
- Denominator: Genesys Agent Status Duration Details (logged in, training)

---

### Occupancy %

**Formula:**
```
Occupancy = ((Inbound + Outbound + Callback Hours) ÷ On-Queue Hours) × 100
```

**Filters:**
```
Where:
- Department = Tech Center
```

**Output:** Percentage

**ISPN Target:** >75%

**Interpretation:**
- Occupancy = percentage of on-queue time actively handling interactions
- Higher = agents busy most of the time
- Lower = agents idle frequently

**Calculation steps:**
1. Sum handle hours for:
   - Inbound calls
   - Outbound calls
   - Callbacks
2. Divide by on-queue hours
3. Multiply by 100

**Notes:**
- Denominator = on-queue time only (not total logged-in time)
- Includes all interaction types (inbound, outbound, callback)
- Industry best practice: 75-85%

**Data sources:**
- Numerator: Genesys Interactions Export (all handle times)
- Denominator: Genesys Agent Status Duration Details (on-queue time)

---

## Data Sources Reference

| Metric | Genesys Export |
|--------|----------------|
| AHT, AWT, Call Counts, Callbacks, Abandoned | Interactions Export |
| On-Queue Hours, Training, Logged In | Agent Status Duration Details |
| Schedule Adherence | WFM Historical Adherence |

---

## Key Filters Summary

### What We Count

| Category | Filter Applied |
|----------|----------------|
| Handled inbound calls | Direction = Inbound, Abandoned = No, Handle >= 20 sec |
| Callbacks | Media Type = callback |
| Outbound calls | Direction = Outbound, Media Type = voice |
| Long abandons | Direction = Inbound, Abandoned = Yes, Queue >= 60 sec |
| Tech Center agents | Department = Tech Center |

---

## Calculation Examples

### Example 1: Daily AHT Calculation

**Data:**
- 500 inbound calls handled
- Total handle time: 5,350 minutes

**Filters applied:**
- Direction = Inbound ✓
- Abandoned = No ✓
- Handle time >= 20 seconds ✓

**Calculation:**
```
AHT = 5,350 minutes ÷ 500 calls
AHT = 10.7 minutes
```

**Result:** Exactly at target (10.7 minutes)

---

### Example 2: Weekly Shrinkage Calculation

**Data (for week):**
- Total logged-in time: 2,000 hours
- Training time: 100 hours
- On-queue time: 1,400 hours

**Calculation:**
```
Shrinkage = ((2,000 - 100 - 1,400) ÷ (2,000 - 100)) × 100
Shrinkage = (500 ÷ 1,900) × 100
Shrinkage = 26.3%
```

**Result:** Above target (target ≤20%), indicates excessive non-productive time

**Root cause analysis needed:**
- Check break/meal durations
- Review meeting schedules
- Investigate unplanned unavailability

---

### Example 3: Monthly Occupancy Calculation

**Data (for month):**
- Inbound call hours: 3,200
- Outbound call hours: 400
- Callback hours: 150
- Total on-queue hours: 4,500

**Calculation:**
```
Occupancy = ((3,200 + 400 + 150) ÷ 4,500) × 100
Occupancy = (3,750 ÷ 4,500) × 100
Occupancy = 83.3%
```

**Result:** Within healthy range (target >75%)

---

## Metric Relationships

### Key Relationships:
```
Logged In Time = On-Queue Time + Off-Queue Time + Training

Off-Queue Time = Breaks + Meals + Meetings + Other Non-Productive

Shrinkage = Off-Queue Time ÷ (Logged In - Training)

Utilization = Inbound Call Hours ÷ (Logged In - Training)

Occupancy = All Call Hours ÷ On-Queue Hours

Occupancy > Utilization (always, because denominator smaller)
```

---

## Data Quality Checks

### Before Reporting, Validate:

1. **Call count reconciliation:**
   ```
   Total Offered ≈ Inbound Count + Abandoned Count + Callback Count
   ```
   (Small variance acceptable due to test calls, errors)

2. **Time reconciliation:**
   ```
   Logged In = On-Queue + Off-Queue + Training
   ```
   (Should balance exactly)

3. **Handle time validation:**
   ```
   Average Handle Time within expected range (5-20 minutes typical)
   ```
   (Outliers indicate data errors)

4. **Department filter applied:**
   ```
   All workforce metrics filtered to Department = Tech Center
   ```
   (Critical - ensures only ISPN agents counted)

5. **Date range consistency:**
   ```
   All exports use same start/end dates
   ```
   (Mismatched dates = invalid comparisons)

---

## Common Data Issues

### Issue 1: AHT Spike
**Symptom:** AHT suddenly jumps from 10 min to 25 min

**Diagnosis:**
1. Check if filter applied (Handle >= 20 seconds)
2. Look for data errors (negative times, missing values)
3. Check if test calls included

**Common cause:** Filter not applied, test calls with 300+ min handle times included

---

### Issue 2: Shrinkage >100%
**Symptom:** Shrinkage calculates to 150%

**Diagnosis:**
1. Check denominator (Logged In - Training)
2. Verify Training time isn't larger than Logged In time

**Common cause:** Data export issue, incorrect department filter

---

### Issue 3: Occupancy >100%
**Symptom:** Occupancy calculates to 110%

**Diagnosis:**
1. Check if numerator (call hours) includes activities not in on-queue time
2. Verify on-queue time includes all interacting time

**Common cause:** ACW done off-queue but counted in handle time

---

## Reporting Standards

### Weekly Tech Center Scorecard

**Required metrics:**
- Inbound Call Count
- Average Handle Time (AHT)
- Average Wait Time (AWT)
- Abandon Count / Abandon Rate
- Service Level %
- Occupancy %
- Utilization %
- Shrinkage %

**Format:** Excel scorecard with trend arrows

**Distribution:** Monday morning (prior week performance)

**Recipients:** Tech Center leadership, WFM team, Operations VP

---

### Monthly Leadership Team (LT) Scorecard

**Required metrics:**
- All weekly metrics (aggregated)
- Month-over-month trends
- YTD comparisons
- Partner-specific breakdowns

**Format:** Excel workbook (TC_ONLY_ISPN_iGLASS_LT_Scorecard)

**Distribution:** First business day of month

**Recipients:** ISPN senior leadership

---

### Daily Performance Report (DPR)

**Required metrics:**
- Call volumes (inbound, outbound, abandoned)
- AHT, AWT
- Service level by queue
- Staffing levels

**Format:** Excel workbook with 25+ months of historical data

**Distribution:** Daily (prior day performance)

**Recipients:** Operations managers, supervisors

---

## Best Practices

### 1. Consistent Date Ranges
Always use the same start/end dates across all exports for a given report period.

**Example (weekly report for week of Jan 4-10):**
- Interactions export: Jan 4 00:00:00 to Jan 10 23:59:59
- Agent Status export: Jan 4 00:00:00 to Jan 10 23:59:59
- WFM Adherence: Jan 4 to Jan 10

### 2. Filter Validation
Always verify filters before calculating:
```sql
-- Pseudo-code check
if handle_time < 20 seconds:
    exclude from AHT calculation

if department != "Tech Center":
    exclude from workforce metrics

if queue_time < 60 seconds AND abandoned:
    exclude from abandon count
```

### 3. Trend Analysis
Don't evaluate single period in isolation:
- Compare to prior week/month
- Compare to same period last year
- Calculate moving averages (4-week, 13-week)

### 4. Segment Analysis
Break down by meaningful dimensions:
- By queue (Gateway Fiber, Quantum Fiber, etc.)
- By time of day (peak hours vs. off-peak)
- By day of week (Monday spike vs. Friday drop)
- By agent tenure (new hires vs. tenured)

### 5. Document Assumptions
Always note:
- Threshold values used (60-second abandon, 20-second handle)
- Filters applied
- Data source and export date
- Any data quality issues encountered

---

## Version History

**Version 1.0 (Current)**
- Established standardized calculations
- Defined all filters and thresholds
- Documented data sources

**Key decisions:**
- Abandon threshold: 60 seconds (industry standard)
- Handle time minimum: 20 seconds (excludes disconnects)
- Department filter mandatory for workforce metrics

**Approved by:** ISPN Operations VP, WFM Director

---

## Reference

**Source:** ISPN Network Services Internal Documentation
- Tech Center Scorecard Methodology
- WFM Calculation Standards
- Genesys Reporting Standards

**Contact:**
- WFM Team for calculation questions
- Analytics Team for data quality issues
- Operations Team for target adjustments

---
name: genesys-cloud-cx-reporting
description: Complete guide for extracting and analyzing ISPN Tech Center performance data from Genesys Cloud CX. Use when building Genesys exports, calculating contact center KPIs (AHT, AWT, FCR, Utilization, Occupancy, Shrinkage), validating scorecard data, configuring scheduled reports, or troubleshooting metric discrepancies. Triggers on "Genesys export", "Interactions report", "Agent Status", "WFM adherence", "contact center metrics", "AHT calculation", "service level", "callback tracking", "shrinkage analysis", "workforce metrics".
---

# Genesys Cloud CX Reporting Specification for ISPN Tech Center

This skill provides complete, validated export configurations and KPI calculation logic for the ISPN Network Services Tech Center performance scorecard. All field names, filter values, and formulas have been validated against live Genesys Cloud CX exports.

## Quick Reference: The 4 Required Exports

| # | Export Name | Navigation Path | Primary Use |
|---|-------------|-----------------|-------------|
| 1 | **Interactions Export** | Performance → Workspace → Interactions | Call volumes, AHT, AWT, answer thresholds, abandons, callbacks |
| 2 | **Agent Status Duration Details** | Performance → Workspace → Contact Center → Agent Status | Hours worked, on-queue hours, shrinkage, training |
| 3 | **WFM Historical Adherence** | WFM → Historical Adherence | Schedule adherence, conformance, exceptions |
| 4 | **Agent Performance** | Performance → Workspace → Agents Performance | AHT validation, agent-level metrics |

---

## Export 1: Interactions Export

### Purpose
Primary dataset for all call and callback metrics. Provides interaction-level detail for calculating service levels, handle times, wait times, and abandonment rates.

### Navigation Path
```
Performance → Workspace → Interactions → Export (CSV)
```

### Required Filters

| Filter | Value | Notes |
|--------|-------|-------|
| Media Type | Voice | Callbacks have separate Media Type = "callback" |
| Direction | Inbound, Outbound | Select both; callbacks show as "Inbound/Outbound" |
| Date Range | Weekly (match scorecard week) | Use Sunday–Saturday or Monday–Sunday per org standard |
| Queues | All (filter downstream) | Or select specific TC queues |

### Required Fields (Exact Column Names)

#### From "Interactions" Section
| Field | Column Name in Export | Purpose |
|-------|----------------------|---------|
| Conversation ID | `Conversation ID` | Unique identifier, deduplication |
| Date | `Date` | Week bucketing, trend analysis |
| Direction | `Direction` | Inbound vs Outbound classification |
| Media Type | `Media Type` | Voice vs Callback identification |
| Queue | `Queue` | Queue-level filtering and reporting |
| First Queue | `First Queue` | Original queue (for transfers) |
| Agent | `Users - Interacted` | Agent attribution |
| Abandoned | `Abandoned` | YES/NO indicator |
| Disconnect Type | `Disconnect Type` | External/Agent/System |
| Flow-Out Type | `Flow-Out Type` | callback/voicemail/ivr/acd |
| Wrap-up | `Wrap-up` | Wrap-up code applied |
| Transferred | `Transferred` | YES/NO indicator |
| Non-ACD | `Non-ACD` | YES/NO - exclude from queue metrics |

#### From "Metrics" Section
| Field | Column Name in Export | Unit | Purpose |
|-------|----------------------|------|---------|
| Queue Wait Time | `Total Queue` | Milliseconds | AWT calculation |
| Time to Answer | `Total Alert` | Milliseconds | Answer threshold buckets |
| Handle Time | `Total Handle` | Milliseconds | AHT, call hours |
| Talk Time | `Total Talk` | Milliseconds | AHT decomposition |
| ACW Time | `Total ACW` | Milliseconds | After-call work tracking |
| Hold Time | `Total Hold` | Milliseconds | AHT decomposition |
| Transfer Count | `Transfers` | Count | Transfer tracking |

### Field Value Reference (Validated from Live Data)

#### Direction Values
| Value | Count (Sample) | Use |
|-------|----------------|-----|
| `Inbound` | 15,315 | Primary inbound calls |
| `Outbound` | 2,264 | Agent-initiated outbound |
| `Inbound/Outbound` | 2,222 | Callbacks (both legs) |

#### Media Type Values
| Value | Count (Sample) | Use |
|-------|----------------|-----|
| `voice` | 18,888 | Standard voice calls |
| `callback` | 871 | Callback interactions |
| `message` | 42 | Messaging (exclude from voice metrics) |

#### Abandoned Values
| Value | Meaning |
|-------|---------|
| `YES` | Call abandoned before agent answer |
| `NO` | Call handled by agent |

#### Disconnect Type Values
| Value | Count (Sample) | Meaning |
|-------|----------------|---------|
| `External` | 10,936 | Customer disconnected |
| `Agent` | 8,182 | Agent disconnected |
| `System` | 636 | System disconnected |

#### Wrap-up Values
| Value | Count (Sample) | Significance |
|-------|----------------|--------------|
| `ININ-WRAP-UP-TIMEOUT` | 15,383 | Agent timed out (15-second ACW limit) |
| `Default Wrap-up Code` | 193 | Manual wrap-up selection |

**CRITICAL FINDING:** 97.9% of interactions show `Total ACW` = exactly 15,000ms (15 seconds) due to the `ININ-WRAP-UP-TIMEOUT` wrap-up code. This confirms the system enforces a 15-second ACW timeout. The workbook's 15-second ACW assumption is accurate but reflects system configuration, not actual wrap-up work time.

#### Non-ACD Values
| Value | Count (Sample) | Treatment |
|-------|----------------|-----------|
| `NO` | 14,319 | Include in queue metrics |
| `YES` | 5,482 | **Exclude** from queue metrics (direct calls, internal) |

### Callback Identification

**VALIDATED METHOD:** Use `Media Type = "callback"` to identify callbacks natively.

| Identification Method | Filter Logic | Reliability |
|----------------------|--------------|-------------|
| **Primary (Use This)** | `Media Type = "callback"` | ✅ High - Native Genesys field |
| Secondary | `Direction = "Inbound/Outbound"` | Medium - Includes some voice |
| Tertiary | `Flow-Out Type CONTAINS "callback"` | Medium - Only catches flow-outs |

Callback interactions always show:
- `Media Type` = "callback"
- `Direction` = "Inbound/Outbound"
- `Disconnect Type` = "Agent" (typically)

---

## Export 2: Agent Status Duration Details

### Purpose
Provides agent-level time allocation data for calculating hours worked, on-queue hours, shrinkage, and training time.

### Navigation Path
```
Performance → Workspace → Contact Center → Agent Status → Export
```

**IMPORTANT:** Select "Agent Status Duration Details" (not "Agent Log In - Log Out Details" or "Agent Status Timeline Details")

### Export Type Selection

| Option | What It Provides | Use Case |
|--------|------------------|----------|
| Agent Log In - Log Out Details | Individual login/logout timestamps | Attendance tracking |
| Agent Status Timeline Details | Chronological status changes | Audit trails |
| **Agent Status Duration Details** ✅ | **Aggregated time per status** | **Scorecard KPIs** |

### Required Filters

| Filter | Value | Notes |
|--------|-------|-------|
| Date Range | Match Interactions export | Weekly for scorecard |
| Users | L1-L3 Tech population | Or export all, filter by Department |
| Timezone | Central Time | Must match other exports |

### Required Fields (Exact Column Names)

| Field | Column Name in Export | Unit | Purpose |
|-------|----------------------|------|---------|
| Agent ID | `Agent Id` | String | Unique identifier |
| Agent Name | `Agent Name` | String | Display name |
| Email | `Email` | String | Backup identifier |
| Department | `Department` | String | Population filtering |
| Division | `Division Name` | String | Org structure |
| Interval Start | `Interval Start` | Datetime | Export date range |
| Interval End | `Interval End` | Datetime | Export date range |
| Logged In | `Logged In` | Milliseconds | Total hours worked |
| On Queue | `On Queue` | Milliseconds | On-queue hours |
| Off Queue | `Off Queue` | Milliseconds | Off-queue hours |
| Training | `Training` | Milliseconds | Training hours |
| Break | `Break` | Milliseconds | Shrinkage component |
| Meal | `Meal` | Milliseconds | Shrinkage component |
| Meeting | `Meeting` | Milliseconds | Shrinkage component |
| Away | `Away` | Milliseconds | Shrinkage component |
| System Away | `System Away` | Milliseconds | System-initiated away |
| Interacting | `Interacting` | Milliseconds | Active interaction time |
| Idle | `Idle` | Milliseconds | Available but not interacting |
| Not Responding | `Not Responding` | Milliseconds | Missed alerts |
| Occupancy | `Occupancy` | Decimal (0.00-1.00) | Pre-calculated occupancy |
| On Queue % | `On Queue %` | Decimal | Percentage on queue |
| Idle % | `Idle %` | Decimal | Percentage idle |
| Interacting % | `Interacting %` | Decimal | Percentage interacting |

### Department Filtering

Filter to `Department = "Tech Center"` for L1-L3 Tech metrics.

| Department | Agent Count (Sample) | Include in Metrics |
|------------|---------------------|-------------------|
| Tech Center | 146 | ✅ Yes |
| Engineering | 9 | ❌ No |
| Administration | 3 | ❌ No |
| QC | 2 | ❌ No |
| Other | Various | ❌ No |

### Time Unit Conversion

All duration fields are in **milliseconds**. Convert to hours:
```
Hours = Milliseconds / 3,600,000
```

Example: `Logged In` = 618,710,100 ms = 171.86 hours

---

## Export 3: WFM Historical Adherence

### Purpose
Provides schedule adherence, conformance, and exception data for workforce management analysis.

### Navigation Path
```
WFM → Historical Adherence → Export (CSV)
```

### Required Filters

| Filter | Value | Notes |
|--------|-------|-------|
| Date Range | Match other exports | Weekly for scorecard |
| Management Unit | Permanent Schedules MU | Or your Tech Center MU |

### Required Fields (Exact Column Names)

| Field | Column Name in Export | Unit | Purpose |
|-------|----------------------|------|---------|
| Agent | `Agent` | String | Agent name |
| Management Unit | `Management Unit` | String | WFM grouping |
| Adherence | `Adherence (%)` | Percentage string | Schedule adherence |
| Conformance | `Conformance (%)` | Percentage string | Work time alignment |
| Exceptions | `Exceptions` | Count | Schedule deviation events |
| Exception Duration | `Exceptions Duration Minutes` | Minutes | Total exception time |
| Exception Duration (Adherence) | `Exceptions Duration (Adherence)` | Minutes | Exceptions affecting adherence |
| Net Impact | `Net Impact` | String | Positive/Negative/Neutral |
| Scheduled | `Scheduled Minutes` | Minutes | Total scheduled time |
| Actual Time | `Actual Time` | Minutes | Total actual time |
| Scheduled On Queue | `Scheduled On Queue` | Minutes | Scheduled queue time |
| Work Time On Queue | `Work Time On Queue` | Minutes | Actual queue time |
| Scheduled (Adherence) | `Scheduled (Adherence)` | Minutes | Scheduled time for adherence calc |

### Time Unit Note

**IMPORTANT:** Unlike other exports, WFM data is in **minutes**, not milliseconds.

### Data Quality Notes

| Condition | Count (Sample) | Handling |
|-----------|----------------|----------|
| Valid Adherence | 146 | Normal calculation |
| "Infinity%" Conformance | 3 | Exclude - no scheduled time |
| Negative Net Impact | 138 | Worked less than scheduled |
| Positive Net Impact | 6 | Worked more than scheduled |

---

## Export 4: Agent Performance

### Purpose
Supplemental validation data for AHT decomposition and agent-level handle time verification.

### Navigation Path
```
Performance → Workspace → Agents Performance → Export (CSV)
```

### Required Filters

| Filter | Value | Notes |
|--------|-------|-------|
| Date Range | Match other exports | Weekly for scorecard |
| Media Type | Voice | Scope to telephony |

### Required Fields (Exact Column Names)

| Field | Column Name in Export | Unit | Purpose |
|-------|----------------------|------|---------|
| Agent ID | `Agent Id` | String | Unique identifier |
| Agent Name | `Agent Name` | String | Display name |
| Department | `Department` | String | Population filtering |
| Handle Count | `Handle` | Count | Handled interactions |
| Total Handle | `Total Handle` | Milliseconds | Total handle time |
| Total Talk | `Total Talk` | Milliseconds | Total talk time |
| Total Hold | `Total Hold` | Milliseconds | Total hold time |
| Total ACW | `Total ACW` | Milliseconds | Total after-call work |
| Total Alert | `Total Alert` | Milliseconds | Total alert time |
| Total Dialing | `Total Dialing` | Milliseconds | Outbound dial time |
| Total Contacting | `Total Contacting` | Milliseconds | Contacting time |
| Avg Handle | `Avg Handle` | Milliseconds | Average handle time |
| Avg Talk | `Avg Talk` | Milliseconds | Average talk time |
| Avg Hold | `Avg Hold` | Milliseconds | Average hold time |
| Avg ACW | `Avg ACW` | Milliseconds | Average ACW time |
| ASA | `ASA` | Milliseconds | Average speed of answer |
| Outbound | `Outbound` | Count | Outbound call count |
| Transferred | `Transferred` | Count | Transfer count |
| Alert - No Answer | `Alert - No Answer` | Count | Missed alerts |

---

## KPI Calculation Logic

### Scorecard Row Mapping

| Row | KPI Name | Target | Source Export | Filter Logic | Formula |
|-----|----------|--------|---------------|--------------|---------|
| 19 | Genesys Inbound Call AHT | < 10.7 min | Interactions | Direction=Inbound AND Abandoned=NO AND Total Handle≥20000 | `AVG(Total Handle) / 60000` |
| 20 | Genesys Inbound Call Minutes | — | Interactions | Same as Row 19 | `SUM(Total Handle) / 60000` |
| 21 | Genesys Inbound Call Hours | — | Derived | — | `Row20 / 60` |
| 22 | Genesys Inbound Call Count | — | Interactions | Same as Row 19 | `COUNT(*)` |
| 23 | Genesys AWT (Seconds) | < 90 sec | Interactions | Direction=Inbound (all offered) | `AVG(Total Queue) / 1000` |
| 24 | Calls Answered ≤30 Seconds | — | Interactions | Row 19 filter AND Total Alert≤30000 | `COUNT(*)` |
| 25 | Calls Answered ≤60 Seconds | — | Interactions | Row 19 filter AND Total Alert≤60000 | `COUNT(*)` |
| 26 | Calls Answered ≤90 Seconds | — | Interactions | Row 19 filter AND Total Alert≤90000 | `COUNT(*)` |
| 27 | Calls Answered ≤120 Seconds | — | Interactions | Row 19 filter AND Total Alert≤120000 | `COUNT(*)` |
| 28 | Abandoned Call Count (>60s) | — | Interactions | Direction=Inbound AND Abandoned=YES AND Total Queue≥60000 | `COUNT(*)` |
| 29 | Genesys Outbound Call Count | — | Interactions | Direction=Outbound AND Media Type=voice | `COUNT(*)` |
| 30 | Genesys Outbound Call Hours | — | Interactions | Same as Row 29 | `SUM(Total Handle) / 3600000` |
| 31 | Genesys Callback Call Count | — | Interactions | Media Type=callback | `COUNT(*)` |
| 32 | Genesys Callback Call Hours | — | Interactions | Same as Row 31 | `SUM(Total Handle) / 3600000` |
| 44 | Total Inbound Call ACW Hours | — | Interactions | Row 19 filter | `SUM(Total ACW) / 3600000` |
| 59 | Training Hours | — | Agent Status | Department=Tech Center | `SUM(Training) / 3600000` |
| 60 | Total Hours Worked (L1-L3) | — | Agent Status | Department=Tech Center | `SUM(Logged In) / 3600000` |
| 61 | Hours Worked (excl. training) | — | Derived | — | `Row60 - Row59` |
| 62 | On-Queue Hours (L1-L3) | — | Agent Status | Department=Tech Center | `SUM(On Queue) / 3600000` |
| 63 | Hours Unavailable (Shrinkage) | — | Derived | — | `Row61 - Row62` |
| 64 | % Shrinkage | ≤ 20% | Derived | — | `Row63 / Row61` |
| 66 | L1-L3 Tech Utilization | > 55% | Derived | — | `Row21 / Row61` |
| 67 | L1-L3 Occupancy % | > 75% | Derived | — | `(Row21 + Row30 + Row32) / Row62` |

### Detailed Filter Logic

#### Inbound Handled Calls (≥20 seconds)
```python
filter = (
    (Direction == "Inbound") AND
    (Abandoned == "NO") AND
    (Total Handle >= 20000) AND
    (Non-ACD == "NO")  # Optional: exclude non-ACD
)
```

#### Abandoned Calls (≥60 seconds)
```python
filter = (
    (Direction == "Inbound") AND
    (Abandoned == "YES") AND
    (Total Queue >= 60000)
)
```

#### Callbacks
```python
filter = (Media Type == "callback")
```

#### Outbound (excluding callbacks)
```python
filter = (
    (Direction == "Outbound") AND
    (Media Type == "voice")
)
```

#### Tech Center Agents
```python
filter = (Department == "Tech Center")
```

### Unit Conversion Reference

| Source | Unit | To Hours | To Minutes | To Seconds |
|--------|------|----------|------------|------------|
| Interactions | Milliseconds | ÷ 3,600,000 | ÷ 60,000 | ÷ 1,000 |
| Agent Status | Milliseconds | ÷ 3,600,000 | ÷ 60,000 | ÷ 1,000 |
| Agent Performance | Milliseconds | ÷ 3,600,000 | ÷ 60,000 | ÷ 1,000 |
| WFM Adherence | Minutes | ÷ 60 | (native) | × 60 |

---

## Validated Sample Calculations

Based on live export data (Dec 29, 2025 – Jan 5, 2026):

### From Interactions Export
| Metric | Value | Filter Applied |
|--------|-------|----------------|
| Inbound Handled (≥20s) | 11,404 | Direction=Inbound, Abandoned=NO, Handle≥20000 |
| Callbacks | 871 | Media Type=callback |
| Outbound Voice | 2,264 | Direction=Outbound, Media Type=voice |
| Abandoned (≥60s) | 380 | Direction=Inbound, Abandoned=YES, Queue≥60000 |
| **Calculated AHT** | **9.90 minutes** | — |
| **Calculated AWT** | **46.90 seconds** | — |
| Answered ≤30s | 11,276 | Alert ≤ 30000 |
| Answered ≤60s | 11,349 | Alert ≤ 60000 |
| Answered ≤90s | 11,371 | Alert ≤ 90000 |
| Answered ≤120s | 11,381 | Alert ≤ 120000 |

### From Agent Status Export (Tech Center)
| Metric | Value |
|--------|-------|
| Total Logged In Hours | 26,920.31 |
| On Queue Hours | 17,772.19 |
| Training Hours | 242.86 |
| Break Hours | 1,413.81 |
| Meal Hours | 2,393.16 |
| Meeting Hours | 827.64 |

### From WFM Adherence Export
| Metric | Value |
|--------|-------|
| Agent Count | 146 |
| Mean Adherence | 80.95% |
| Mean Conformance | 81.39% |
| Total Exceptions | 4,034 |
| Total Exception Hours | 1,214.22 |

---

## Critical Configuration Notes

### ACW Timeout Configuration
The Genesys system is configured with a **15-second ACW timeout** (ININ-WRAP-UP-TIMEOUT). This means:
- 97.9% of interactions show `Total ACW` = 15,000ms
- Agents who don't manually select a wrap-up code timeout after 15 seconds
- The workbook's 15-second ACW assumption is accurate but represents forced timeout, not actual work

### Date Range Alignment
**CRITICAL:** All 4 exports must use the same date range for accurate cross-calculation. Mismatched date ranges will cause:
- Utilization percentages to be incorrect
- Occupancy percentages to be incorrect
- Shrinkage calculations to be skewed

### Non-ACD Exclusion
Interactions with `Non-ACD = "YES"` (blank queue) should generally be excluded from queue-based metrics. These represent:
- Direct agent calls
- Internal transfers
- Non-queue interactions

### Queue Filtering
For partner-specific reporting, filter by `Queue` field. Sample queues:
- Fastwyre (909 calls)
- Lightcurve (766 calls)
- Gateway Fiber (760 calls)
- CNSNext (670 calls)
- BTC Broadband (562 calls)

---

## Troubleshooting Guide

### Common Issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| AHT higher than expected | Including short calls < 20s | Apply `Total Handle >= 20000` filter |
| Callback count = 0 | Wrong filter | Use `Media Type = "callback"` not wrap-up code |
| Utilization extremely low | Date range mismatch | Align all export date ranges |
| Missing agents | Department filter | Check `Department = "Tech Center"` |
| Shrinkage > 50% | Including non-productive time | Verify status taxonomy mapping |

### Validation Checks

1. **Handle Count Validation:** Agent Performance `Handle` count should approximate Interactions `COUNT(Direction=Inbound, Abandoned=NO)`

2. **Hours Validation:** Agent Status `Logged In` total should exceed Interactions total handle time

3. **Adherence Validation:** WFM agent count should match Agent Status Tech Center count

---

## Automation Recommendations

### Scheduled Exports
Configure weekly scheduled exports for each of the 4 reports:
1. Set consistent date range (e.g., previous Sunday–Saturday)
2. Use static download links for automation
3. Schedule exports to run Monday morning for previous week

### Data Pipeline Integration
For automated scorecard population:
```
Genesys Scheduled Export → S3/SharePoint → ETL Process → Database → BI Dashboard
```

### API Alternative
For real-time metrics, consider Genesys Cloud Analytics API:
- `/api/v2/analytics/conversations/details/query`
- `/api/v2/analytics/users/details/query`
- `/api/v2/workforcemanagement/managementunits/{muId}/adherence`

---

## Appendix: Complete Field Reference

### Interactions Export - All Available Fields

#### Evaluations Section
- Evaluated Agent, Evaluation Assignee, Evaluation Created, Evaluation Critical Score, Evaluation Score, Evaluation Status, Evaluator

#### External Contact Section
- External Contact, External Organization

#### Flows Section
- All Flow Disconnect, Customer Disconnect, Customer Short Disconnect, Failed outcomes, Flow, Flow Disconnect, Flow Exit, Incomplete outcomes, Outcome Attempts, Outcome failure, Outcome success, Successful outcomes, System Error Disconnect

#### Interactions Section
- Abandoned, Abandoned in Queue, Agent Assist, ANI, Authenticated, Barged-In, Blind Transferred, Cleared by Customer, Co-browse, Coached, Consult Transferred, Consulted, Conversation Duration, Conversation ID, Conversation Initiator, Customer Participation, Date, Delivery Status, Delivery Status Details, Direction, Disconnect Type, Division, DNIS, Email BCC, Email CC, Emails Sent, End Date, Error Code, External Tag, Fax, First Queue, Flagged, Flow-Out Type, From, Has Media, Inbound Audio, Inbound Media, Initial Direction, Last Wrap-Up, Media, Media Type, Message Type, Monitored, MOS, Non-ACD, Outbound Audio, Outbound Media, Parked, Provider, Push Notifications, Queue, Recording, Remote, Screen Recorded, Session DNIS, SIP Call ID, Social Classification, Subject, To, Transferred, Users, Users - Alerted, Users - Interacted, Users - Not Responding, Voicemail, Wrap-up, Wrap-up Notes

#### Journey Section
- Has Customer Journey Data, Proactive

#### Metrics Section
- Active Park, Active Total Callback, Agentless Emails, Alert Segments, Avg Agent Response, Avg Customer Response, Blind Transfers, Callback - Time to First Connect, Callback - Time to First Dial, Consult Transfers, Consults, Contacting Segments, Dialing Segments, Error Count, Hold Segments, Inbound Messages, Inbound SMS/MMS Segments, IVR Segments, Message Turns, Messages, Not Responding, Outbound Messages, Outbound SMS/MMS Segments, Queue Segments, Talk Segments, Time to Abandon, Total ACW, Total Alert, Total Barge-In, Total Coaching, Total Contacting, Total Dialing, Total First Engagement, Total First Response, Total Handle, Total Hold, Total IVR, Total Monitor, Total Park, Total Queue, Total Talk, Total Voicemail, Transfers, User Segments, Wrap-Up Segments

#### Outbound Section
- Campaign Caller Name, Campaign Start, Time to Agent, Time to Flow

#### Routing Section
- Agent Bullseye Ring, Bullseye Ring, Direct Routing, Group Ring, Languages, Manual Agents Assigned, Manual Assigner, Predictive Agent Selected, Preferred Agents, Preferred Agents Requested, Preferred Rule, Routing Requested, Routing Rule, Routing Used, Skills, Skills - Active, Skills - Removed

#### Surveys Section
- Has Survey Data, Promoter Score, Survey Form, Survey Score, Survey Status, Survey Type, Surveys

### Agent Status Duration Details - All Available Fields
Adherence, Adherence: Duration, Agent, Available, Away, Break, Busy, Communicating, Department, Division, Duration, Duration 2, Duration 3, Email, ID, Idle, Idle %, Interacting, Interacting %, Interactions, Log in, Log out, Logged In, Meal, Media Types, Meeting, Not Responding, Not Responding %, Occupancy, Off Queue, Off Queue %, On Queue, On Queue %, Presence, Primary Phone, Routing Status, Scheduled Activity, Secondary Status, Skills, Station, Status, System Away, Time in Routing Status, Time in Status, Title, Total ACD, Training

### WFM Historical Adherence - All Available Fields
Management Unit, Adherence (%), Conformance (%), Exceptions, Exceptions Duration, Exceptions Duration (Adherence), Net Impact, Scheduled, Actual Time, Scheduled On Queue, Work Time On Queue, Scheduled (Adherence)

### Agent Performance - All Available Fields

#### Performance Section
Active Callback, ACW, Adherence, Adherence: Duration, Agent, Alert, Alert - No Answer, Answer, ASA, Avg Active Callback, Avg ACW, Avg Hold, Avg Talk, Avg ACW Handled, Avg Contacting, Avg Dialing, Avg Handle, Avg Hold Handled, Avg Monitor, Avg Park, Blind Transfer, Blind Transfer %, Consult, Consult Transfer, Consult Transfer %, Contacting, Department, Dialing, Division, Duration, Duration 2, Duration 3, Email, Error, Group, Handle, Hold, ID, Interactions, Location, Max Active Callback, Max ACW, Max Alert, Max Alert - No Answer, Max Answer, Max Contacting, Max Dialing, Max Handle, Max Hold, Max Monitor, Max Park, Max Talk, Media Types, Min Active Callback, Min ACW, Min Alert, Min Alert - No Answer, Min Answer, Min Contacting, Min Dialing, Min Handle, Min Hold, Min Monitor, Min Park, Min Talk, Monitor, Outbound, Outbound Audio, Park, Presence, Primary Phone, Reports To, Role, Routing Status, Scheduled Activity, Secondary Status, Skills, Station, Status, Talk, Time in Routing Status, Time in Status, Title, Total Active Callback, Total ACW, Total Hold, Total Talk, Total Alert, Total Alert - No Answer, Total Contacting, Total Dialing, Total Handle, Total Monitor, Total Park, Transfer, Transfer %

#### Routing Section
Bullseye Requested, Bullseye Requested %, Bullseye Used, Bullseye Used %, Conditional Requested, Conditional Requested %, Conditional Used, Conditional Used %, Direct Requested, Direct Requested %, Direct Used, Direct Used %, Last Requested, Last Requested %, Last Used, Last Used %, Manual Used, Manual Used %, Predictive Requested, Predictive Requested %, Predictive Used, Predictive Used %, Preferred Requested, Preferred Requested %, Preferred Used, Preferred Used %, Standard Requested, Standard Requested %, Standard Used, Standard Used %

#### Speech and Text Analytics Section
Average Sentiment Score, Avg Sentiment, Negative Sentiment Instances, Positive Sentiment Instances, Sentiment Instances

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-06 | Pete/Claude | Initial specification from live export validation |

---

*This specification was validated against live Genesys Cloud CX exports from ISPN Network Services Tech Center. All field names, filter values, and calculations have been verified with actual data.*

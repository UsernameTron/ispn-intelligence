# ISPN Data Standardization Architecture

## The Problem: Metric Drift Between Genesys and ISPN

Genesys Cloud CX exports include pre-calculated percentages that **do not match ISPN's canonical formulas**. This causes significant metric drift:

| Metric | ISPN Formula | Genesys Calculation | Typical Drift |
|--------|--------------|---------------------|---------------|
| **Shrinkage** | (Hours Worked - On-Queue) / Hours Worked | Category breakdown summed | **22+ pp** |
| **Occupancy** | Call Hours / On-Queue Hours | Interacting / On-Queue | **5-10 pp** |
| **Utilization** | Inbound Hours / (Hours - Training) | Not calculated | N/A |
| **AHT** | (Genesys + Wave Min) / Total Calls | Genesys-only average | Variable |
| **ACW** | Fixed 15 sec × Call Count | Actual measured ACW | Variable |

## The Solution: Single Source of Truth

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ISPN DATA STANDARDIZATION FLOW                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  GENESYS EXPORTS          ISPN CALCULATION ENGINE           BOARD REPORTS  │
│  (Raw Data Only)          (Canonical Formulas)              (Final Output) │
│                                                                             │
│  ┌─────────────┐          ┌─────────────────────┐          ┌─────────────┐ │
│  │ Interactions │ ──────► │  GenesysRawData     │          │  Monthly    │ │
│  │   Export     │         │  - call counts      │          │  Scorecard  │ │
│  │              │         │  - milliseconds     │          │             │ │
│  │ EXTRACT:     │         │  - NO percentages   │          │  9 KPIs     │ │
│  │ • Counts     │         └─────────┬───────────┘          │  Summary    │ │
│  │ • Times (ms) │                   │                      │             │ │
│  │ • Flags      │                   ▼                      │  Board      │ │
│  └─────────────┘          ┌─────────────────────┐          │  Deck       │ │
│                           │  ISPNCalculation    │          └──────▲──────┘ │
│  ┌─────────────┐          │  Engine             │                 │        │
│  │ Agent Status │ ──────► │                     │ ────────────────┘        │
│  │   Export     │         │  APPLIES:           │                          │
│  │              │         │  • Charlie's        │                          │
│  │ EXTRACT:     │         │    formulas         │                          │
│  │ • Logged In  │         │  • FY25 standards   │                          │
│  │ • On Queue   │         │  • Fixed ACW (15s)  │                          │
│  │ • Status ms  │         └─────────────────────┘                          │
│  └─────────────┘                                                           │
│                                                                             │
│  ┌─────────────┐          ┌─────────────────────┐                          │
│  │  Helpdesk   │ ──────► │  NON-GENESYS DATA   │                          │
│  │  (Tickets)   │         │  - Escalations      │                          │
│  └─────────────┘          │  - Call Tickets     │                          │
│                           │  - Training Hours   │                          │
│  ┌─────────────┐          │    (manual input)   │                          │
│  │  QA System  │ ──────► │  - Quality Scores   │                          │
│  │  (Scores)    │         └─────────────────────┘                          │
│  └─────────────┘                                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## ISPN Canonical Formulas (Charlie's LT Scorecard)

### 1. First Call Resolution (FCR) %
```
FCR = 1 - (Escalations / Call Tickets)
```
- Source: Helpdesk system (NOT Genesys)
- Target: > 70%

### 2. Escalation %
```
Escalation = Escalations / Call Tickets
```
- Source: Helpdesk system
- Target: < 30%

### 3. Average Handle Time (AHT) - Minutes
```
AHT = Total Call Minutes / Total Inbound Call Count
    = (Genesys Minutes + Wave Minutes) / (Genesys Calls + Wave Calls)
```
- Source: Interactions export (raw minutes/counts)
- Target: < 10.7 minutes

### 4. Average Wait Time (AWT) - Seconds
```
AWT = (Genesys Calls/Total × Genesys AWT) + (Wave Calls/Total × Wave AWT)
```
- Weighted average across platforms
- Source: Interactions export (queue times)
- Target: < 90 seconds

### 5. % Shrinkage of Total Hours Worked ⚠️ CRITICAL
```
Shrinkage = (Total Hours Worked - On-Queue Hours) / Total Hours Worked
          = Hours Unavailable / Total Hours Worked
```
- **DO NOT USE** Genesys "shrinkage" columns
- Source: Agent Status export → Logged In, On Queue columns
- Target: < 30%

### 6. L1-L3 Tech Utilization % (FY25+ Formula)
```
Utilization = Total Inbound Call Hours (incl. ACW) / (Total Hours Worked - Training Hours)
```
- **Requires manual training hours input**
- ACW calculated as: (15 sec / 3600) × Call Count
- Target: > 55%

### 7. L1-L3 Occupancy %
```
Occupancy = Total Call Hours (Inbound + Outbound) / On-Queue Hours
```
- **DO NOT USE** Genesys "Occupancy" column (different calculation)
- Target: ~65%

### 8. ACW Hours (Fixed Assumption)
```
ACW Hours = (15 seconds / 3600) × Total Inbound Call Count
```
- ISPN uses **fixed 15 seconds per call**
- Genesys actual ACW may vary (includes 15000ms timeouts)

## Implementation Files

| File | Purpose |
|------|---------|
| `scripts/utils/ispn_calculations.py` | Canonical calculation engine |
| `scripts/utils/parsers.py` | Raw data extraction (counts/ms only) |
| `scripts/utils/validators.py` | Threshold-based validation |
| `scripts/ingest.py` | Pipeline orchestration |

## Usage Example

```python
from ispn_calculations import ISPNCalculationEngine, GenesysRawData

# Load raw data (extracted from Genesys exports)
raw = GenesysRawData(
    inbound_call_count=50403,
    inbound_total_handle_ms=538180 * 60000,  # Convert to ms
    total_logged_in_ms=19869.67 * 3600000,   # Convert to ms
    total_on_queue_ms=14113.82 * 3600000,
    call_tickets=57743,  # From Helpdesk
    escalations=17770,   # From Helpdesk
    training_hours=0,    # Manual input
)

# Calculate using ISPN formulas
engine = ISPNCalculationEngine()
metrics = engine.calculate_all(raw)

# Results use ONLY canonical formulas
print(f"FCR: {metrics.fcr_pct:.1%}")           # 69.2%
print(f"Shrinkage: {metrics.shrinkage_pct:.1%}")  # 29.0% (NOT 51.7%)
print(f"Utilization: {metrics.utilization_pct:.1%}")  # 46.2%
```

## Key Differences from Previous Parser

| Previous Parser | New Standardized Approach |
|----------------|--------------------------|
| Used Genesys "Shrinkage" breakdown | Calculates: (Logged In - On Queue) / Logged In |
| Used Genesys "Occupancy" column | Calculates: Call Hours / On Queue Hours |
| Used actual ACW from Genesys | Fixed 15 seconds per call |
| Genesys-only AHT | Weighted average including Wave |
| No Utilization calculation | Full FY25 formula with training deduction |

## Validation Checklist

Before any board report, verify:
- [ ] All metrics calculated via `ISPNCalculationEngine`
- [ ] No Genesys pre-calculated percentages used
- [ ] Training hours manually input (for Utilization)
- [ ] Helpdesk data included (for FCR/Escalation)
- [ ] Quality scores included (for Quality metric)

## Contact

Pete Connor - Director, Technical Center Operations

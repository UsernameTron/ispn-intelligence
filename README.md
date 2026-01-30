# ISPN Workforce Intelligence

Local analytics platform for ISPN Tech Center operations. Processes Genesys Cloud exports, generates board reports, and supports ad-hoc analysis via Claude Desktop with 17 integrated skills.

## Architecture

```
Genesys Cloud Exports → data/raw/ → Python Ingest → Parsed JSON → Board Reports
                                                          ↓
                                     Claude Desktop + 17 Skills (Ad-hoc Analysis)
```

## Quick Start

### 1. Setup
```bash
git clone https://github.com/UsernameTron/ispn-intelligence.git
cd ispn-intelligence
pip install -r requirements.txt
```

### 2. Ingest Data
```bash
# Drop Genesys exports in data/raw/
cp ~/Downloads/*Interactions*.csv data/raw/

# Run ingestion (processes all files)
python scripts/ingest.py

# Or process single file
python scripts/ingest.py path/to/file.csv
```

### 3. Generate Reports
```bash
# Weekly report
python scripts/board_report.py --period weekly --week 2025-W04

# Monthly report
python scripts/board_report.py --period monthly --month 2025-01
```

### 4. Ad-hoc Analysis
Drop files into Claude Desktop and ask questions. Skills auto-route based on file patterns.

---

## Genesys Export Types

### Performance Exports (from Genesys Cloud)

| Export | Location | Columns | Purpose |
|--------|----------|---------|---------|
| **Interactions** | Performance → Workspace → Interactions | 25 cols | Call-level detail: handle time, wait time, abandons |
| **Agent Performance** | Performance → Workspace → Agents Performance | 32 cols | Agent AHT, talk, hold, ACW by period |
| **Agent Status** | Performance → Contact Center → Agent Status | 24 cols | Shrinkage breakdown, occupancy, idle time |
| **Skills Performance** | Analytics → Queue Activity → Skills | 24 cols | Queue SLA, answer rate, abandon rate |

### WFM Exports (from Genesys WFM)

| Export | Location | Columns | Purpose |
|--------|----------|---------|---------|
| **Historical Adherence** | WFM → Historical Adherence | 13 cols | Schedule adherence %, conformance % |
| **Scheduled/Required** | WFM → Scheduled vs Required | 11 cols | 15-min interval staffing gaps |
| **Activities** | WFM → Activities | 9 cols | Agent activity codes (On Queue, Meal, Break) |
| **Agent Schedules** | WFM → Agents | 11 cols | Skills, queues, planning groups |

### Time Value Reference

| Export | Time Format | Unit |
|--------|-------------|------|
| Interactions | Milliseconds | Total Queue, Total Handle, Total Talk, etc. |
| Agent Performance | Milliseconds | Avg Handle, Total Handle, ASA, etc. |
| Agent Status | Milliseconds | Logged In, On Queue, Break, etc. |
| Historical Adherence | **Minutes** | Scheduled Minutes, Work Time On Queue |
| Agent Status % fields | Decimal | 0.72 = 72% |
| Adherence % fields | String | "80.2%" with % sign |

---

## File Pattern Routing

| Pattern | Parser | Skill Route |
|---------|--------|-------------|
| `*Interactions*.csv` | `parse_interactions()` | ispn-dpr-analysis |
| `*Agent_Performance*.csv` | `parse_agent_performance()` | ispn-agent-coaching |
| `*Agent_Status*.csv` | `parse_agent_status()` | ispn-intraday-staffing |
| `*Skills_Performance*.csv` | `parse_skills_performance()` | genesys-queue-performance-analysis |
| `*Adherence*.csv` | `parse_historical_adherence()` | ispn-schedule-optimization |
| `ScheduledAndRequired*.csv` | `parse_wfm_scheduled()` | ispn-capacity-planning |
| `Activities*.csv` | `parse_wfm_activities()` | ispn-schedule-optimization |
| `Agents_Permanent*.csv` | `parse_agent_schedules()` | genesys-skills-routing |
| `DPR*.xlsx` | `parse_dpr()` | ispn-dpr-analysis |
| `WCS*.xlsx` | `parse_wcs()` | ispn-wcs-analysis |
| `*Scorecard*.xlsx` | `parse_scorecard()` | ispn-scorecard-analysis |

---

## Directory Structure

```
ispn-intelligence/
├── data/
│   ├── raw/                    # ⛔ Gitignored - Genesys exports with PII
│   │   └── archive/            # Processed files moved here
│   ├── parsed/
│   │   ├── genesys/
│   │   │   ├── interactions/   # Parsed interaction JSONs
│   │   │   ├── agent_performance/
│   │   │   ├── agent_status/
│   │   │   ├── skills_performance/
│   │   │   └── adherence/
│   │   ├── wfm/
│   │   │   ├── scheduled_required/
│   │   │   ├── activities/
│   │   │   └── agent_schedules/
│   │   ├── scorecard/
│   │   ├── dpr/
│   │   └── wcs/
│   └── metrics/
│       ├── kpi_history.json    # Time-series metrics
│       └── targets.json        # Threshold definitions
├── reports/
│   ├── board/                  # Monthly board reports
│   ├── weekly/                 # Weekly summaries
│   └── adhoc/                  # One-off analyses
├── scripts/
│   ├── ingest.py              # Main ingestion pipeline
│   ├── board_report.py        # Report generator
│   └── utils/
│       ├── parsers.py         # File parsers (validated against actual exports)
│       ├── validators.py      # Data validators with thresholds
│       └── thresholds.py      # KPI threshold definitions
├── templates/
│   └── board_narrative.md     # Report template
└── skills/                     # Claude skill reference (empty - skills in ~/Library/)
```

---

## KPI Targets & Thresholds

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| AHT | < 10.7 min | 11.5 min | 12.0 min |
| AWT | < 90 sec | 120 sec | 180 sec |
| FCR | > 70% | 65% | 60% |
| Escalation | < 30% | 35% | 40% |
| Abandon Rate | < 5% | 8% | 10% |
| Answer Rate | > 90% | 85% | 80% |
| Utilization | 55-65% | 50-70% | <50 / >70% |
| Shrinkage | < 30% | 35% | 40% |
| Adherence | > 90% | 85% | 80% |
| Occupancy | 75-85% | 70-90% | <70 / >90% |
| Quality | > 88 | 85 | 82 |

---

## ROI Benchmarks

| Improvement | Annual Value | Calculation |
|-------------|--------------|-------------|
| AHT -1 min | $186K | Volume × AvgWage × 60min savings |
| FCR +5pp | $501K | Repeat call reduction × handle cost |
| Utilization +5pp | $332K | FTE equivalent savings |

---

## ISPN Workforce Intelligence Suite (17 Skills)

### Layer 0: Platform (Genesys Raw Data)
- `genesys-cloud-cx-reporting` - Export specifications, field mappings
- `genesys-qa-analytics` - QA evaluation processing
- `genesys-skills-routing` - Skills-based routing configuration

### Layer 1: Parsers (Structured Data)
- `ispn-dpr-analysis` - Daily Performance Reports
- `ispn-wcs-analysis` - Weekly Call Statistics
- `ispn-scorecard-analysis` - Monthly Scorecard KPIs

### Layer 2: Diagnostics (Root Cause)
- `genesys-queue-performance-analysis` - Queue diagnostics
- `ispn-agent-coaching` - Individual performance analysis
- `ispn-training-gap` - QA failure patterns
- `ispn-sentiment-analysis` - Speech analytics

### Layer 3: Decisions (Actions)
- `workforce-optimization-persona` - Staffing decisions
- `ispn-capacity-planning` - FTE modeling
- `ispn-intraday-staffing` - Real-time VTO/OT
- `ispn-schedule-optimization` - Forecast validation
- `ispn-partner-sla` - Partner SLA monitoring
- `ispn-cost-analytics` - ROI calculations
- `ispn-attrition-risk` - Retention interventions

---

## ISPN Calculation Standards

| Standard | Value | Source |
|----------|-------|--------|
| ACW Timeout | 15 seconds | ININ-WRAP-UP-TIMEOUT |
| Abandon Threshold | ≥ 60 seconds | Only count abandons after 60s in queue |
| AHT Min Filter | ≥ 20 seconds | Exclude short handles from metrics |
| Non-ACD Exclusion | YES | Filter out Non-ACD = YES for queue metrics |

---

## Compensation Reference (for ROI)

| Level | Hourly | Annual | Turnover Cost |
|-------|--------|--------|---------------|
| L1 Tech | $18.11 | $37,669 | $11,301 |
| L2 Tech | $23.29 | $48,443 | $14,533 |
| L3 Tech | $28.46 | $59,197 | $17,759 |
| **Total Payroll** | | **$6.64M** | 187 employees |

---

## Capacity Formula

```
Required_FTE = (Monthly_Volume × AHT_Hours) / (173.2 × Utilization × (1 - Shrinkage))
```

Default values: Utilization = 0.60, Shrinkage = 0.28

---

*Part of ISPN Workforce Intelligence Suite | Updated Jan 2026*

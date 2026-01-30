# ISPN Workforce Intelligence

Local analytics platform for ISPN Tech Center operations. Processes Genesys exports, generates board reports, and supports ad-hoc analysis via Claude Desktop.

## Architecture

```
Genesys Export → ~/ispn-intelligence/data/raw/ → Python Ingest → Parsed JSON → Board Reports
                                                                            ↓
                                                          Claude Desktop + 12 Skills (Ad-hoc)
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
cp ~/Downloads/LT_Scorecard_Jan2025.xlsx data/raw/

# Run ingestion
python scripts/ingest.py
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

## File Patterns

| Pattern | Routed To | Data |
|---------|-----------|------|
| `DPR*.xlsx` | dpr-analysis | Daily performance, systemic flags |
| `WCS*.xlsx` | wcs-analysis | Weekly stats, partner SLAs, agent rankings |
| `*Scorecard*.xlsx` | scorecard-analysis | Monthly KPIs, capacity data |
| `Interactions*.csv` | dpr-analysis | Call-level detail |
| `Agent_Performance*.csv` | agent-coaching | Individual metrics |
| `reviewreport*.csv` | training-gap | QA scores, failures |

## Directory Structure

```
ispn-intelligence/
├── data/
│   ├── raw/           # ⛔ Gitignored - Genesys exports with PII
│   ├── parsed/        # ✅ Committed - Aggregated JSON metrics
│   └── metrics/       # ✅ Committed - Time-series for trending
├── reports/
│   ├── board/         # Monthly board reports
│   ├── weekly/        # Weekly summaries
│   └── adhoc/         # One-off analyses
├── scripts/           # Python automation
├── templates/         # Report templates
└── skills/            # Claude skill reference
```

## KPI Targets

| Metric | Target | Yellow | Red |
|--------|--------|--------|-----|
| AHT | < 10.7 min | 10.7-11.5 | > 11.5 |
| AWT | < 90 sec | 90-180 | > 180 |
| FCR | > 70% | 65-70% | < 65% |
| Escalation | < 30% | 30-35% | > 35% |
| Utilization | 55-65% | 45-55/65-70 | <45/>70 |
| Quality | > 88 | 85-88 | < 85 |
| Abandon | < 5% | 5-8% | > 8% |
| Shrinkage | < 30% | 30-35% | > 35% |

## ROI Benchmarks

| Improvement | Annual Value |
|-------------|--------------|
| AHT -1 min | $186K |
| FCR +5pp | $501K |
| Utilization +5pp | $332K |

---
*Part of ISPN Workforce Intelligence Suite*

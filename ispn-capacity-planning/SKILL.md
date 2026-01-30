---
name: ispn-capacity-planning
description: |
  FTE modeling, Erlang C, headcount justification, shrinkage management.
  TRIGGERS: "do we need to hire", "capacity", "FTE", "Erlang", "shrinkage"
  Part of ISPN Workforce Intelligence Suite
---

# ISPN Capacity Planning

## MASTER FORMULA

```
Required_FTE = (Volume × AHT_hrs) / (173.2 × Util × (1 - Shrinkage))

Where:
  Work_Hours_Per_Month = 173.2 hours
  Target_Util = 0.55 to 0.65
  Shrinkage = 0.25 to 0.30
```

## SEASONAL FACTORS

| Month | Factor | Month | Factor |
|-------|--------|-------|--------|
| Jan | 1.05 | Jul | 0.95 |
| Feb | 1.02 | Aug | 0.97 |
| Mar | 1.00 | Sep | 1.00 |
| Apr | 0.98 | Oct | 1.03 |
| May | 0.97 | Nov | 1.08 |
| Jun | 0.95 | Dec | 1.10 |

## ERLANG C MODEL

```python
def erlang_c(calls_per_hour, aht_minutes, agents, target_sla_seconds=120):
    traffic = (calls_per_hour * aht_minutes) / 60  # Erlangs
    rho = traffic / agents  # Occupancy
    prob_wait = erlang_c_formula(traffic, agents)
    asa = (prob_wait * aht_minutes * 60) / (agents * (1 - rho))
    return {"traffic": traffic, "occupancy": rho, "asa": asa}
```

## SHRINKAGE TAXONOMY

```
Total Shrinkage (Target: < 30%)
├── Planned Shrinkage (~20%)
│   ├── Training (5-8%)
│   ├── Meetings (3-5%)
│   ├── Breaks (5-7%)
│   └── Meals (in schedule)
│
└── Unplanned Shrinkage (<10%)
    ├── Unscheduled Absences
    ├── System Downtime
    ├── Late Arrivals
    └── Early Departures
```

### Shrinkage Thresholds

| KPI | Target | Warning | Critical |
|-----|--------|---------|----------|
| Total Shrinkage | < 30% | 30-35% | > 35% |
| Planned Shrinkage | ~20% | > 22% | > 25% |
| Unplanned Shrinkage | < 10% | 10-15% | > 15% |
| Training % | 5-8% | > 10% | > 15% |
| Meeting % | 3-5% | > 7% | > 10% |
| System Away % | < 2% | 2-5% | > 5% |

### Shrinkage Analysis Tree

```
Total Shrinkage High?
├── Planned High?
│   ├── Training excessive → Review calendar
│   ├── Meetings excessive → Audit, consolidate
│   └── Breaks → Schedule compliance check
│
└── Unplanned High?
    ├── Absences → Attendance management
    ├── System Away → Technical investigation
    └── Aux Time → Agent behavior audit
```

## FINANCIAL PARAMETERS

| Component | Monthly | Annual |
|-----------|---------|--------|
| Fully Loaded FTE (L1) | $3,139 | $37,669 |
| Fully Loaded FTE (L2) | $4,037 | $48,443 |
| Fully Loaded FTE (Blended) | $5,658 | $67,900 |

## HANDOFFS

**Receives from:**
- ispn-scorecard-analysis: Volume, AHT, current headcount
- ispn-cost-analytics: Financial constraints
- ispn-intraday-staffing: Pattern data for forecast adjustment
- ispn-schedule-optimization: Coverage analysis

**Sends to:**
- ispn-cost-analytics: FTE scenarios for financial modeling
- ispn-skill-orchestrator: Capacity recommendations

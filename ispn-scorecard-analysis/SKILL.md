---
name: ispn-scorecard-analysis
description: |
  Monthly LT Scorecard analysis for KPIs and capacity planning.
  TRIGGERS: *Scorecard*.xlsx, "monthly KPIs", "scorecard"
  Part of ISPN Workforce Intelligence Suite
---

# ISPN Scorecard Analysis

## FILE IDENTIFICATION

### Primary: *Scorecard*.xlsx, LT_Scorecard*.xlsx
- Sheet: "ISPN_Scorecard-Monthly_INPUT"
- FY columns: FY24 (BC-BN), FY25 (BO-BZ), FY26 (CA-CL)
- Monthly structure: Each column = one month

## 9 CORE KPIs

| KPI | Row | Target | Internal Threshold |
|-----|-----|--------|-------------------|
| Calls Offered | 52 | Forecast ±10% | Variance flag if >15% |
| AHT | 58 | < 10.7 min | GREEN < 10.7, YELLOW 10.7-11.5, RED > 11.5 |
| AWT | 59 | < 90 sec | GREEN < 90, YELLOW 90-180, RED > 180 |
| FCR | 60 | > 70% | GREEN > 70%, YELLOW 65-70%, RED < 65% |
| Escalation | 61 | < 30% | GREEN < 30%, YELLOW 30-35%, RED > 35% |
| Utilization | 62 | 55-65% | RED if < 45% or > 70% |
| Shrinkage | 63 | < 30% | Flag if > 32% |
| Quality Score | 64 | > 88 | GREEN > 88, YELLOW 85-88, RED < 85 |
| Headcount | 65 | Budget | Variance tracking |

## DATA QUALITY ALERTS

⚠️ **Row 58 (AHT):** Formula issues in FY20-FY23 columns. Always validate AHT manually for historical analysis.

```python
def validate_scorecard(df):
    alerts = []
    if row_58_fy20_fy23:
        alerts.append("AHT formula suspect - validate manually")
    if missing_months:
        alerts.append(f"Missing data: {missing_months}")
    return alerts
```

## CAPACITY CALCULATION

```
Required_FTE = (Volume × AHT_hrs) / (173.2 × 0.60 × 0.72)

Where:
- 173.2 = Avg work hours/month
- 0.60 = Target utilization
- 0.72 = (1 - 0.28 shrinkage)

Gap = Required_FTE - Current_Headcount
```

## TREND OUTPUTS

```python
scorecard_trend = {
    "period": "FY25",
    "months_analyzed": 6,
    "kpi_trends": {
        "aht": {"direction": "increasing", "rate": "+0.3min/month"},
        "fcr": {"direction": "stable", "rate": "±1%"},
        "utilization": {"direction": "decreasing", "rate": "-2pp/month"}
    },
    "flags": ["utilization_below_target_3_consecutive"]
}
```

## HANDOFFS

**Sends to:**
- ispn-capacity-planning: Volume, AHT, current headcount for FTE modeling
- ispn-cost-analytics: Utilization trend for efficiency ROI
- ispn-skill-orchestrator: Monthly KPI summary

**Receives from:**
- ispn-skill-orchestrator: File routing, query routing
- ispn-dpr-analysis: Daily data for monthly validation

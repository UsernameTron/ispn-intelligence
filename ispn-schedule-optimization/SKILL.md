---
name: ispn-schedule-optimization
description: |
  Weekly schedule optimization and forecast validation.
  TRIGGERS: "schedule optimization", "forecast accuracy", "shift optimization", "coverage analysis"
  Part of ISPN Workforce Intelligence Suite
---

# ISPN Schedule Optimization

## TRIGGERS

```yaml
weekly_review_triggers:
  - End of week performance review (Sunday)
  - Forecast accuracy < 85%
  - SLA missed 3+ days
  - Utilization outside 50-65% band for 3+ days

mid_week_adjustment_triggers:
  - Forecast variance > 15% by Wednesday
  - Unplanned absence rate > 10%
```

## WEEKLY OPTIMIZATION CHECKLIST

### 1. Forecast Accuracy Assessment
```python
def assess_forecast():
    mae = mean(abs(actual - forecast))
    mape = mean(abs(actual - forecast) / actual) * 100
    bias = mean(forecast - actual)  # + = over, - = under
    return {"MAE": mae, "MAPE": mape, "bias": bias}
```

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| MAPE | < 10% | 10-15% | > 15% |
| Bias | ±5% | ±10% | > ±10% |

### 2. Coverage Analysis
- Map understaffed intervals (AWT > 120s)
- Map overstaffed intervals (Util < 50%)
- Calculate optimal shift distribution

### 3. Schedule Adjustments
- Shift start time optimization
- Break/lunch stagger patterns
- Flex schedule activation

### 4. Capacity Buffer Setting
- Review shrinkage actuals
- Adjust buffer for unplanned absence
- Set OT/VTO thresholds

## FORMULAS

```
Forecast_Accuracy = 1 - ABS(Actual - Forecast) / Actual
Optimal_Headcount = (Forecasted_Calls × AHT) / (Available_Hours × Target_Util)
Schedule_Coverage_Index = Scheduled_Hours / Required_Hours (by interval)
```

## HANDOFFS

**Receives from:**
- ispn-scorecard-analysis: Volume forecasts
- ispn-intraday-staffing: Intraday pattern data

**Sends to:**
- ispn-capacity-planning: Forecast adjustment recommendations

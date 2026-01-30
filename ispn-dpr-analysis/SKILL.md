---
name: ispn-dpr-analysis
description: |
  Analyzes ISPN Daily Performance Reports. Extracts systemic context flags that
  ispn-agent-coaching requires before individual analysis.
  TRIGGERS: DPR*.xlsx, Interactions*.csv, "daily performance", "today's numbers"
  Part of ISPN Workforce Intelligence Suite
---

# ISPN DPR Analysis

## FILE IDENTIFICATION

### Primary: DPR*.xlsx
- Sheet names: Month abbreviations (OCT23, NOV23, etc.)
- Key columns: Total Calls, Avg Handle Time, FCR %, Outage Tickets

### Secondary: Interactions*.csv
- Call-level detail from Genesys Cloud
- Columns: InteractionID, StartTime, Duration, QueueTime, HandleTime, DispositionCode

## SYSTEMIC FLAGS (Required by ispn-agent-coaching)

```python
systemic_flags = {
    "outage_day": outage_tickets > 50,
    "volume_spike": total_calls > (trailing_4wk_avg * 1.20),
    "high_abandon": abandon_rate > 0.10,
    "staffing_gap": techs_on_queue < (techs_scheduled * 0.75),
    "routing_issue": (calls_in_queue > 10) and (agents_available > 5)
}
```

## INTERNAL PERFORMANCE THRESHOLDS

| Metric | GREEN | YELLOW | RED |
|--------|-------|--------|-----|
| AHT | < 10.7 min | 10.7-11.5 | > 11.5 |
| AWT | < 90 sec | 90-180 | > 180 |
| FCR | > 70% | 65-70% | < 65% |
| Abandon | < 5% | 5-8% | > 8% |

## AHT DECOMPOSITION

### Component Thresholds

| Component | Target | Warning | Critical |
|-----------|--------|---------|----------|
| Talk Time | ~8.5 min | > 9.5 min | > 10.5 min |
| Hold Time | ~1.9 min | > 2.5 min | > 3.0 min |
| ACW Time | 15 sec | N/A | N/A |

### Root Cause by Component

**High Talk Time:**
- Call control challenges
- Troubleshooting inefficiency
- Lack of product knowledge
- Documentation during call

**High Hold Time:**
- Tool navigation slow
- Knowledge base search
- Waiting for systems
- Escalation consultation

### AHT Drill-Down Dimensions

```python
# Decompose by component
aht_components = {'Talk': X, 'Hold': Y, 'ACW': Z}

# By Day of Week
aht_by_dow = df.groupby('day_of_week')['aht'].mean()

# By Hour of Day  
aht_by_hour = df.groupby('hour')['aht'].mean()

# By Agent (outlier detection)
aht_by_agent = df.groupby('agent')['aht'].mean().sort_values(ascending=False)

# By Partner/Queue
aht_by_queue = df.groupby('queue')['aht'].mean()

# By Call Type/Wrap-up
aht_by_type = df.groupby('wrap_up')['aht'].mean()
```

## TREND ANALYSIS OUTPUTS

```python
trend_output = {
    "metric": "AHT",
    "current_value": 11.2,
    "baseline_value": 10.4,
    "change_start_date": "2024-01-15",
    "component_breakdown": {"talk": 9.1, "hold": 2.0, "acw": 0.1},
    "correlation_factors": ["outage_spike", "new_hire_class"],
    "recommendation": "Route to ispn-training-gap for QA analysis"
}
```

## HANDOFFS

**Sends to:**
- ispn-agent-coaching: systemic_flags (REQUIRED)
- ispn-training-gap: FCR trend, escalation breakdown
- ispn-cost-analytics: AHT trend for ROI
- ispn-capacity-planning: Volume actuals vs forecast
- ispn-sentiment-analysis: Interaction data with sentiment

**Receives from:**
- ispn-skill-orchestrator: File routing, query routing
- ispn-wcs-analysis: Weekly aggregates for validation

## ISPN CALCULATION STANDARDS

- Abandon: Only count ≥ 60 sec queue time
- AHT: Exclude < 20 sec handle (likely misroutes)
- Occupancy: Exclude training/meeting aux codes

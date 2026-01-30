---
name: ispn-attrition-risk
description: |
  Flight risk scoring and retention interventions.
  TRIGGERS: "flight risk", "retention", "attrition"
  Part of ISPN Workforce Intelligence Suite
---

# ISPN Attrition Risk

## RISK INDICATORS

| Indicator | Weight | Source |
|-----------|--------|--------|
| Tenure < 6 months | +15 | HRIS |
| Performance declining 3+ months | +20 | ispn-agent-coaching |
| Attendance exceptions increasing | +15 | UKG/Attendance data |
| No promotion in 2+ years | +15 | HRIS |
| Quality score declining | +10 | ispn-training-gap |
| Schedule adherence dropping | +10 | ispn-agent-coaching |
| Passed over for advancement | +15 | Manager input |

## RISK TIERS

| Score | Tier | Action | Owner |
|-------|------|--------|-------|
| < 30 | Low | Standard engagement | Supervisor |
| 30-50 | Medium | Proactive check-in | Supervisor |
| 50-70 | High | Retention conversation | Manager + HR |
| > 70 | Critical | Immediate intervention | Director + HR |

## RISK CALCULATION

```python
def calculate_flight_risk(agent, sources):
    score = 0
    factors = []
    
    # Tenure risk
    if agent.tenure_months < 6:
        score += 15
        factors.append("new_hire_vulnerability")
    
    # Performance trend (from ispn-agent-coaching)
    if sources.coaching.performance_trend == "declining" and sources.coaching.decline_months >= 3:
        score += 20
        factors.append("performance_decline")
    
    # Attendance trend (from UKG)
    if sources.attendance.exception_trend == "increasing":
        score += 15
        factors.append("attendance_degrading")
    
    # Career progression
    if agent.years_since_promotion >= 2:
        score += 15
        factors.append("career_stagnation")
    
    # Quality trend (from ispn-training-gap)
    if sources.training.quality_trend == "declining":
        score += 10
        factors.append("quality_decline")
    
    return {
        "score": score,
        "tier": get_tier(score),
        "factors": factors,
        "recommendation": get_recommendation(score, factors)
    }
```

## DATA SOURCES (REQUIRED)

| Source | Data Needed | Skill |
|--------|-------------|-------|
| Performance trend | 3-month composite scores | ispn-agent-coaching |
| Quality trend | QA score trajectory | ispn-training-gap |
| Attendance | Exception frequency | ispn-agent-coaching |
| Tenure | Months employed | HRIS/direct |
| Promotion history | Last advancement date | HRIS/direct |

## TURNOVER COSTS

| Level | Turnover Cost | Components |
|-------|---------------|------------|
| L1 | $11,328 | Recruiting $3K + Training $5K + Productivity loss $3.3K |
| L2 | $14,500 | Recruiting $4K + Training $6K + Productivity loss $4.5K |
| L3 | $18,000 | Recruiting $5K + Training $7K + Productivity loss $6K |

## HANDOFFS

**Receives from:**
- ispn-agent-coaching: Performance trends, attendance data, before separation decisions
- ispn-training-gap: Quality score trends
- ispn-skill-orchestrator: Query routing

**Sends to:**
- ispn-agent-coaching: Flight risk flag before separation recommendations
- ispn-cost-analytics: Turnover cost projections

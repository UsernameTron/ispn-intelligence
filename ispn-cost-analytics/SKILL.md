---
name: ispn-cost-analytics
description: |
  Financial analysis: cost per contact, ROI, turnover impact.
  TRIGGERS: "cost per contact", "ROI", "turnover cost"
  Part of ISPN Workforce Intelligence Suite
---

# ISPN Cost Analytics

## COMPENSATION DATA

| Level | Loaded Rate | Annual | Turnover Cost |
|-------|-------------|--------|---------------|
| L1 | $18.11/hr | $37,669 | $11,328 |
| L2 | $23.29/hr | $48,443 | $14,500 |
| L3 | $28.46/hr | $59,197 | $18,000 |

**Blended Rate:** $21.19/hr
**Total Payroll:** $6.64M (187 employees)

## ROI BENCHMARKS

| Improvement | Annual Value | Calculation Basis |
|-------------|--------------|-------------------|
| AHT -1 min | $186K | 526K calls × $21.19/60 |
| FCR +5pp | $501K | Repeat call reduction |
| Utilization +5pp | $332K | Labor efficiency |

## COST OF UNDOCUMENTED DECISIONS
**$1.17M-$1.75M annually**

| Category | Range | Driver |
|----------|-------|--------|
| Delayed Staffing | $312K-$468K | Overtime, abandon, SLA |
| Inconsistent Quality | $195K-$293K | Rework, repeat calls |
| Partner Escalations | $156K-$234K | Remediation effort |
| Reactive Management | $507K-$755K | Crisis response vs prevention |

## FORMULAS

```python
# Cost per contact
cost_per_contact = total_labor_cost / handled_contacts

# AHT ROI
aht_roi = minutes_saved × ($21.19 / 60) × annual_call_volume

# Turnover cost
turnover_cost = recruiting + training + productivity_loss
# L1: $11,328 = $3,000 + $5,000 + $3,328

# Utilization ROI
util_roi = (util_improvement × total_payroll) / current_util
```

## HANDOFFS

**Receives from:**
- ispn-dpr-analysis: AHT trend for efficiency ROI
- ispn-scorecard-analysis: Utilization data for labor efficiency
- ispn-agent-coaching: Separation candidates for turnover cost
- ispn-capacity-planning: Headcount scenarios for financial modeling

**Sends to:**
- ispn-skill-orchestrator: ROI summaries for business cases
- ispn-capacity-planning: Financial constraints for FTE modeling

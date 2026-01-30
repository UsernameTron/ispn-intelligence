---
name: ispn-wcs-analysis
description: |
  Analyzes ISPN Weekly Call Statistics. Primary source for partner SLAs and agent rankings.
  TRIGGERS: WCS*.xlsx, "weekly stats", "partner SLA", "agent rankings"
  Part of ISPN Workforce Intelligence Suite
---

# ISPN WCS Analysis

## FILE IDENTIFICATION

### Primary: WCS*.xlsx or MMDDYY-MMDDYY.xlsx
- Sheet "CD data 2": 168-row hourly breakdown (24hrs × 7days)
- Partner summary tabs: One per partner with aggregated metrics
- Agent performance tabs: Individual rankings

### Validation Check
```python
def validate_wcs(df):
    assert len(cd_data_2) == 168, "Hourly data incomplete"
    assert all(partners_have_data), "Missing partner tabs"
    return True
```

## PARTNER SLA THRESHOLDS (CONTRACTUAL)

| Metric | Target | Warning | Breach |
|--------|--------|---------|--------|
| AWT | ≤ 120s | > 100s | > 120s |
| Answer < 60s | ≥ 70% | < 75% | < 70% |
| Escalation | < 10% | > 8% | > 10% |
| Abandon | ≤ 10% | > 8% | > 10% |

⚠️ These are **contractual** thresholds. Internal performance thresholds differ (see orchestrator).

## PARTNER STATUS CALCULATION

```python
def calculate_partner_status(partner):
    status = "GREEN"
    systemic_flag = None
    
    if partner.awt > 100 or partner.escalation > 0.08:
        status = "YELLOW"
    if partner.awt > 120 or partner.escalation > 0.10:
        status = "RED"
    if partner.escalation > 0.40:
        systemic_flag = f"partner_issue:{partner.name}"
    
    return {
        "status": status,
        "systemic_flag": systemic_flag,
        "metrics": {
            "awt": partner.awt,
            "escalation": partner.escalation,
            "abandon": partner.abandon,
            "fcr": partner.fcr
        }
    }
```

## AGENT RANKING OUTPUTS

```python
agent_ranking = {
    "top_10": [...],  # For recognition
    "bottom_15": [...],  # For coaching review (requires systemic check)
    "peer_comparison": {...}  # Team averages for context
}
```

## HANDOFFS

**Sends to:**
- ispn-partner-sla: Partner RED status triggers remediation workflow
- ispn-skill-orchestrator: partner_issue systemic flag
- ispn-agent-coaching: Agent rankings for peer comparison, bottom performers
- ispn-dpr-analysis: Weekly aggregates for daily validation

**Receives from:**
- ispn-skill-orchestrator: File routing, query routing
- ispn-dpr-analysis: Daily data for weekly rollup validation

## PARTNER-SPECIFIC NOTES

| Partner | AWT Target | Esc Target | Notes |
|---------|------------|------------|-------|
| Gateway Fiber | ≤ 90s | < 8% | Premium SLA |
| Allo | ≤ 120s | < 10% | Standard |
| Default | ≤ 120s | < 10% | Standard |

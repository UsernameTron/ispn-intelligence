---
name: ispn-partner-sla
description: |
  Partner SLA monitoring and remediation.
  TRIGGERS: "partner SLA", "breach", partner complaints
  Part of ISPN Workforce Intelligence Suite
---

# ISPN Partner SLA

## SLA THRESHOLDS (CONTRACTUAL)

| Metric | Target | Warning | Breach |
|--------|--------|---------|--------|
| AWT | ≤ 120s | > 100s | > 120s |
| Answer < 60s | ≥ 70% | < 75% | < 70% |
| Escalation | < 10% | > 8% | > 10% |
| Abandon | ≤ 10% | > 8% | > 10% |

⚠️ **Note:** These are **contractual** thresholds that trigger remediation. Internal performance thresholds for agent coaching are different (see ispn-agent-coaching).

## PARTNER-SPECIFIC SLAs

| Partner | AWT | Esc | Abandon | Notes |
|---------|-----|-----|---------|-------|
| Gateway Fiber | ≤ 90s | < 8% | < 8% | Premium SLA |
| Allo | ≤ 120s | < 10% | < 10% | Standard |
| Default | ≤ 120s | < 10% | < 10% | Standard |

## STATUS CALCULATION

```python
def partner_status(metrics):
    if metrics.awt > 120 or metrics.esc > 0.10 or metrics.abandon > 0.10:
        return "RED"
    if metrics.awt > 100 or metrics.esc > 0.08 or metrics.abandon > 0.08:
        return "YELLOW"
    return "GREEN"
```

## REMEDIATION PROTOCOL

| Level | Trigger | Action | Owner | Timeline |
|-------|---------|--------|-------|----------|
| Yellow | Warning threshold | Monitor + daily review | Supervisor | Same day |
| Orange | Near breach | Dedicated staffing surge | Ops Manager | 4 hours |
| Red | Breach | Surge + exec notification | Director | Immediate |

## ESCALATION PATH

```
Yellow (>100s AWT) → Supervisor monitors
    ↓ (persists 2+ days)
Orange → Ops Manager assigns dedicated staff
    ↓ (still breaching)
Red (>120s AWT) → Director + exec notification + surge
```

## HANDOFFS

**Receives from:**
- ispn-wcs-analysis: Partner RED status triggers this skill
- ispn-skill-orchestrator: Query routing for "partner SLA"

**Sends to:**
- ispn-skill-orchestrator: Remediation status updates
- ispn-capacity-planning: Surge staffing requests

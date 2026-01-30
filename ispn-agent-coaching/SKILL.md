---
name: ispn-agent-coaching
description: |
  Individual agent performance analysis. REQUIRES systemic context from ispn-dpr-analysis.
  Enforces "When NOT to Blame the Technician" protocol.
  TRIGGERS: Agent_Performance*.csv, Attendance*.csv, "who needs coaching", "bottom performers", "PIP"
  Part of ISPN Workforce Intelligence Suite
---

# ISPN Agent Coaching

## ⚠️ PREREQUISITE CHECK (MANDATORY)

Before ANY individual analysis:
1. Check systemic_flags from ispn-dpr-analysis
2. If no data: "Need DPR/WCS to verify systemic factors first"
3. If any flag TRUE: Document as mitigating factor
4. If all CLEAR: Proceed to individual analysis

```python
def systemic_check():
    flags = get_from_dpr_analysis()
    if flags is None:
        return "BLOCKED: Need DPR/WCS data first"
    
    mitigating = [k for k, v in flags.items() if v]
    if mitigating:
        return f"PROCEED WITH CONTEXT: {mitigating}"
    return "PROCEED: No systemic factors"
```

## FILE IDENTIFICATION

### Primary: Agent_Performance*.csv
- Columns: AgentID, Name, Team, AHT, FCR, Escalation, Quality, Calls
- Period: Usually weekly or monthly aggregate

### Secondary: Attendance*.csv, UKG*.xlsx
- Columns: AgentID, Date, ScheduledStart, ActualStart, ExceptionType, Hours
- Use for: Adherence calculation, attendance patterns

### Tertiary: Interactions*.csv (from DPR routing)
- Use for: Sentiment scores, call-level detail for coaching examples

## COMPOSITE SCORING

| Dimension | Weight | Source |
|-----------|--------|--------|
| Quality (QA) | 25% | QA reports |
| AHT | 15% | Agent_Performance |
| Availability | 15% | UKG/Attendance |
| Escalation Rate | 15% | Agent_Performance |
| Attendance | 15% | UKG/Attendance |
| Productivity | 15% | Calls handled |

```python
def calculate_composite(agent):
    scores = {
        "quality": normalize(agent.qa_score, 0, 100),
        "aht": normalize_inverse(agent.aht, 8, 15),  # Lower is better
        "availability": normalize(agent.availability, 0, 100),
        "escalation": normalize_inverse(agent.esc_rate, 0, 50),
        "attendance": normalize(agent.adherence, 0, 100),
        "productivity": normalize(agent.calls, min_calls, max_calls)
    }
    weights = [0.25, 0.15, 0.15, 0.15, 0.15, 0.15]
    return sum(s * w for s, w in zip(scores.values(), weights))
```

## INTERVENTION MATRIX

| Condition | Action | Owner |
|-----------|--------|-------|
| Gap < 20% from peers | Coaching conversation | Supervisor |
| Gap 20-40% sustained 2+ months | Formal PIP | Supervisor + HR |
| Bottom 15 + 3+ source validation | Separation consideration | Director + HR |
| QA = 0 (integrity failure) | Immediate HR escalation | Director |

## MULTI-SOURCE VALIDATION

**Never recommend separation without 3+ sources confirming:**
1. Performance metrics (composite score)
2. QA evaluations (quality trend)
3. Attendance records (reliability)
4. Peer/supervisor feedback (optional but valuable)
5. Systemic factor clearance (MANDATORY)

## INTERNAL PERFORMANCE THRESHOLDS

| Metric | GREEN | YELLOW | RED |
|--------|-------|--------|-----|
| AHT | < 10.7 min | 10.7-11.5 | > 11.5 |
| FCR | > 70% | 65-70% | < 65% |
| Escalation | < 30% | 30-35% | > 35% |
| Quality | > 88 | 85-88 | < 85 |
| Adherence | > 90% | 85-90% | < 85% |

## HANDOFFS

**Receives from:**
- ispn-dpr-analysis: systemic_flags (REQUIRED)
- ispn-wcs-analysis: Agent rankings, peer comparison data
- ispn-skill-orchestrator: File routing, query routing

**Sends to:**
- ispn-training-gap: Bottom performers for skill gap analysis
- ispn-attrition-risk: Check flight risk before separation decisions
- ispn-cost-analytics: Turnover cost if separation likely

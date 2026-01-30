# Partner SLA Tracker

## Partner SLA Dashboard

### Current Status Overview

| Partner | Status | AWT | Ans <60s | Esc Rate | Abandon | Priority |
|---------|--------|-----|----------|----------|---------|----------|
| [Partner 1] | 🟢🟡🔴 | [X]s | [X]% | [X]% | [X]% | [1-5] |
| [Partner 2] | 🟢🟡🔴 | [X]s | [X]% | [X]% | [X]% | [1-5] |
| ... | | | | | | |

### RAG Status Definitions

| Status | Meaning | Condition |
|--------|---------|-----------|
| 🟢 Green | On Track | All metrics within SLA |
| 🟡 Yellow | At Risk | Any metric within 10% of threshold |
| 🔴 Red | Breach | Any metric exceeding threshold |

---

## Standard SLA Thresholds

### Default Partner SLA

| Metric | Target | Warning (Yellow) | Breach (Red) |
|--------|--------|------------------|--------------|
| AWT (Average Wait Time) | ≤ 120s | > 100s | > 120s |
| % Answered < 60s | ≥ 70% | < 75% | < 70% |
| Escalation Rate | ≤ 10% | > 8% | > 10% |
| Abandon Rate | ≤ 10% | > 8% | > 10% |
| Bumpahead Minutes | Per contract | N/A | Below minimum |

### Premium Partner SLA (if applicable)

| Metric | Target | Warning | Breach |
|--------|--------|---------|--------|
| AWT | ≤ 60s | > 45s | > 60s |
| % Answered < 30s | ≥ 80% | < 85% | < 80% |
| Escalation Rate | ≤ 5% | > 4% | > 5% |
| Abandon Rate | ≤ 5% | > 4% | > 5% |

---

## Partner-Specific Tracking

### Partner Profile Template

```
PARTNER: [Name]
CONTRACT ID: [ID]
TIER: [Standard/Premium/Custom]
EFFECTIVE DATE: [Date]
REVIEW DATE: [Date]

SLA TERMS:
├── AWT: ≤ [X] seconds
├── % Answered < 60s: ≥ [X]%
├── Escalation Rate: ≤ [X]%
├── Abandon Rate: ≤ [X]%
├── Bumpahead: [X] minutes priority
└── Penalty: $[X] per breach / [X]% credit

CURRENT PERFORMANCE:
├── AWT: [X]s (Target: [X]s) [🟢🟡🔴]
├── % Answered < 60s: [X]% (Target: [X]%) [🟢🟡🔴]
├── Escalation Rate: [X]% (Target: [X]%) [🟢🟡🔴]
└── Abandon Rate: [X]% (Target: [X]%) [🟢🟡🔴]

TREND: [Improving/Stable/Declining]
RISK LEVEL: [Low/Medium/High/Critical]
```

---

## Breach Response Protocol

### Level 1: At Risk (Yellow)

**Trigger:** Any metric within 10% of threshold

**Actions:**
1. Increase monitoring frequency (hourly → 30 min)
2. Document trend and contributing factors
3. Prepare remediation options
4. Notify WFM for staffing review

**Owner:** Supervisor  
**Timeline:** Same day assessment

### Level 2: Breach Imminent (Orange)

**Trigger:** Any metric within 5% of threshold OR multiple yellows

**Actions:**
1. Activate dedicated partner queue staffing
2. Increase bumpahead priority (if contractually allowed)
3. Brief operations leadership
4. Prepare partner communication draft

**Owner:** Operations Manager  
**Timeline:** 2-hour response window

### Level 3: Active Breach (Red)

**Trigger:** Any metric exceeds threshold

**Actions:**
1. Immediate staffing surge (all available resources)
2. Activate all remediation levers
3. Executive notification
4. Partner notification within 4 hours
5. Begin root cause analysis
6. Schedule RCA review within 48 hours

**Owner:** Director  
**Timeline:** Immediate response

---

## Remediation Toolkit

### Staffing Levers

| Action | Impact | Speed | Cost |
|--------|--------|-------|------|
| Add partner-dedicated agents | High | Immediate | Reallocation |
| Extend shifts (OT) | Medium | Same day | 1.5× labor |
| Cancel VTO | Medium | Immediate | None |
| Recall on-call | High | 1-2 hours | OT rate |
| Cross-train general agents | Medium | 1-2 weeks | Training time |

### Routing Levers

| Action | Impact | Speed | Risk |
|--------|--------|-------|------|
| Increase bumpahead | High | Immediate | Other queues degrade |
| Dedicated queue hours | High | Same day | Scheduling complexity |
| Skills-based routing | Medium | 1-3 days | Configuration |
| Overflow handling | Medium | Immediate | Quality risk |

### Process Levers

| Action | Impact | Speed | Effort |
|--------|--------|-------|--------|
| Partner-specific job aids | Medium | 1-2 days | Content creation |
| Escalation path review | Medium | 1 week | Process design |
| Knowledge base update | Medium | 1-2 days | Documentation |
| Training refresher | High | 1-2 weeks | Time off-queue |

---

## Weekly SLA Review Template

### Week of: [Date Range]

#### Executive Summary

```
OVERALL STATUS: [X] of [Y] partners GREEN ([Z]%)

BREACHES THIS WEEK: [X]
AT-RISK PARTNERS: [X]

TOP CONCERNS:
1. [Partner A] - [Metric] at [X]%, trending [direction]
2. [Partner B] - [Metric] breach on [date]

ACTIONS TAKEN:
1. [Action] - [Result]
2. [Action] - [Result]
```

#### Partner Performance Matrix

| Partner | Mon | Tue | Wed | Thu | Fri | Sat | Sun | Weekly |
|---------|-----|-----|-----|-----|-----|-----|-----|--------|
| Partner A | 🟢 | 🟢 | 🟡 | 🔴 | 🟡 | 🟢 | 🟢 | 🟡 |
| Partner B | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 | 🟢 |
| ... | | | | | | | | |

#### Detailed Partner Analysis

**[Partner Name] - [Status]**

| Metric | Target | Actual | Variance | Trend |
|--------|--------|--------|----------|-------|
| AWT | ≤ 120s | [X]s | [+/-X]s | ↑↓→ |
| % < 60s | ≥ 70% | [X]% | [+/-X]% | ↑↓→ |
| Esc Rate | ≤ 10% | [X]% | [+/-X]% | ↑↓→ |
| Abandon | ≤ 10% | [X]% | [+/-X]% | ↑↓→ |

**Root Cause:** [If breach/at-risk]  
**Action Plan:** [Remediation steps]  
**Owner:** [Name]  
**Target Resolution:** [Date]

---

## Monthly Partner Business Review

### Agenda Template

1. **Performance Summary** (10 min)
   - SLA compliance rate
   - Trend analysis
   - Breach summary

2. **Root Cause Analysis** (15 min)
   - Contributing factors
   - Remediation effectiveness
   - Systemic issues

3. **Forecast & Capacity** (10 min)
   - Volume outlook
   - Staffing alignment
   - Known events

4. **Improvement Initiatives** (10 min)
   - Training programs
   - Process changes
   - Technology updates

5. **Contract Review** (5 min)
   - Term status
   - Modification requests
   - Penalty/credit status

---

## SLA Calculation Formulas

### AWT (Average Wait Time)

```python
AWT = SUM(Queue_Time_Answered) / COUNT(Answered_Calls)

# Filter: Partner queue only, direction = Inbound, Abandoned = NO
# Unit: Seconds (convert from milliseconds if needed)
```

### % Answered < 60 Seconds

```python
Pct_Under_60 = COUNT(Queue_Time < 60000 AND Answered) / COUNT(Answered) × 100

# Filter: Partner queue only, direction = Inbound
# Threshold in milliseconds (60000 = 60 seconds)
```

### Escalation Rate

```python
Esc_Rate = COUNT(Escalated_Tickets) / COUNT(Total_Partner_Tickets) × 100

# Source: HelpDesk data filtered by partner
```

### Abandon Rate

```python
Abandon_Rate = COUNT(Abandoned_Calls) / COUNT(Offered_Calls) × 100

# Filter: Partner queue only
# Exclude short abandons (< 20 seconds) if contractually specified
```

### Compliance Score (Aggregate)

```python
def calculate_compliance_score(metrics, thresholds):
    """
    Weighted compliance across all SLA metrics
    """
    weights = {'AWT': 0.30, 'Ans_60': 0.30, 'Esc_Rate': 0.20, 'Abandon': 0.20}
    
    score = 0
    for metric, weight in weights.items():
        if metrics[metric] meets thresholds[metric]:
            score += weight * 100
        else:
            # Partial credit for near-miss
            variance = (metrics[metric] - thresholds[metric]) / thresholds[metric]
            partial = max(0, (1 - abs(variance)) * weight * 100)
            score += partial
    
    return score

# Score >= 95: Green
# Score 85-94: Yellow  
# Score < 85: Red
```

---

## Partner Communication Templates

### Proactive Status Update (Green)

```
Subject: [Partner] Weekly SLA Summary - All Metrics Green

Hi [Contact],

This week's performance summary for [Partner]:

✓ AWT: [X]s (Target: ≤120s)
✓ Answered <60s: [X]% (Target: ≥70%)
✓ Escalation Rate: [X]% (Target: ≤10%)
✓ Abandon Rate: [X]% (Target: ≤10%)

All SLA metrics on track. Let me know if you have questions.

Best,
[Name]
```

### Breach Notification

```
Subject: [URGENT] [Partner] SLA Breach Notification - [Date]

Hi [Contact],

I'm writing to notify you of an SLA breach that occurred on [date]:

BREACH DETAILS:
- Metric: [Metric Name]
- Target: [X]
- Actual: [X]
- Duration: [X hours/day]

ROOT CAUSE:
[Brief explanation]

IMMEDIATE ACTIONS TAKEN:
1. [Action]
2. [Action]

REMEDIATION PLAN:
[Description with timeline]

I'll provide an updated status within 24 hours. Please reach out with any questions.

Regards,
[Name]
```

### Monthly Business Review Summary

```
Subject: [Partner] Monthly SLA Review - [Month Year]

Hi [Contact],

Please find attached the monthly SLA review for [Partner].

HIGHLIGHTS:
- Overall Compliance: [X]%
- Breaches: [X] ([X] resolved, [X] open)
- Trend: [Improving/Stable/Declining]

KEY ACTIONS:
1. [Completed action + result]
2. [Planned action + timeline]

Next review scheduled for [Date]. Please confirm attendance.

Best regards,
[Name]
```

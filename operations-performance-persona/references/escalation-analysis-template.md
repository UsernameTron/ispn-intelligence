# Escalation Analysis Template

## FCR/Escalation Dashboard

```
═══════════════════════════════════════════════════════════════════
                FCR & ESCALATION ANALYSIS REPORT
═══════════════════════════════════════════════════════════════════

PERIOD: [Start Date] to [End Date]
GENERATED: [Date/Time]

═══════════════════════════════════════════════════════════════════
```

---

## Executive Summary

### Key Metrics

| Metric | Current | Prior Period | Target | Status | Trend |
|--------|---------|--------------|--------|--------|-------|
| **FCR %** | [X]% | [X]% | > 70% | 🟢🟡🔴 | [↑↓→] |
| **Escalation Rate** | [X]% | [X]% | < 30% | 🟢🟡🔴 | [↑↓→] |
| **Re-escalation Rate** | [X]% | [X]% | < 5% | 🟢🟡🔴 | [↑↓→] |
| Total Tickets | [X,XXX] | [X,XXX] | N/A | - | [↑↓→] |
| Total Escalations | [XXX] | [XXX] | N/A | - | [↑↓→] |

---

## Section 1: Escalation Category Analysis

### Top Escalation Categories

| Rank | Category | Volume | % of Total | Rate | Trend |
|------|----------|--------|------------|------|-------|
| 1 | [Category] | [XXX] | [X]% | [X]% | [↑↓→] |
| 2 | [Category] | [XXX] | [X]% | [X]% | [↑↓→] |
| 3 | [Category] | [XXX] | [X]% | [X]% | [↑↓→] |
| 4 | [Category] | [XXX] | [X]% | [X]% | [↑↓→] |
| 5 | [Category] | [XXX] | [X]% | [X]% | [↑↓→] |

### Category Deep Dive Template

```
CATEGORY: [Name]
VOLUME: [XXX] escalations ([X]% of total)
ESCALATION RATE: [X]% (vs [X]% team average)

ROOT CAUSE BREAKDOWN:
├── [Sub-cause 1]: [X]% - [Action needed]
├── [Sub-cause 2]: [X]% - [Action needed]
└── [Sub-cause 3]: [X]% - [Action needed]

L1 RESOLUTION POTENTIAL:
├── Could have been resolved at L1: [X]%
├── Required L2 expertise: [X]%
└── System limitation: [X]%
```

---

## Section 2: Agent Performance Analysis

### Agent Escalation Distribution

| Agent | Tickets | Escalations | Rate | vs Team | Status |
|-------|---------|-------------|------|---------|--------|
| [Agent 1] | [XXX] | [XX] | [X]% | [+/-X]% | 🟢🟡🔴 |
| [Agent 2] | [XXX] | [XX] | [X]% | [+/-X]% | 🟢🟡🔴 |
| [Agent 3] | [XXX] | [XX] | [X]% | [+/-X]% | 🟢🟡🔴 |
| Team Average | [X,XXX] | [XXX] | [X]% | - | - |

### High Escalation Agent Profile

```
AGENT: [Name]
ESCALATION RATE: [X]% (Team: [X]%, Variance: +[X]%)

TOP ESCALATION CATEGORIES:
├── [Category 1]: [X] escalations ([X]%)
├── [Category 2]: [X] escalations ([X]%)
└── [Category 3]: [X] escalations ([X]%)

ROOT CAUSE ASSESSMENT:
[ ] Knowledge gap - specific topics
[ ] Authority awareness - doesn't know empowerment
[ ] Risk aversion - escalates unnecessarily
[ ] Process confusion - unclear criteria
[ ] Tenure related - new hire curve

COACHING RECOMMENDATION:
[Specific action]
```

---

## Section 3: Partner Analysis

### Escalation by Partner

| Partner | Tickets | Escalations | Rate | SLA Target | Status |
|---------|---------|-------------|------|------------|--------|
| [Partner 1] | [XXX] | [XX] | [X]% | < [X]% | 🟢🟡🔴 |
| [Partner 2] | [XXX] | [XX] | [X]% | < [X]% | 🟢🟡🔴 |
| [Partner 3] | [XXX] | [XX] | [X]% | < [X]% | 🟢🟡🔴 |
| General Queue | [XXX] | [XX] | [X]% | N/A | - |

---

## Section 4: Root Cause Summary

### Root Cause Distribution

| Root Cause Type | % of Escalations | Actionable? | Owner |
|-----------------|------------------|-------------|-------|
| **Knowledge Gap** | [X]% | Yes | Training |
| **Authority Gap** | [X]% | Yes | Policy |
| **Process Gap** | [X]% | Yes | Operations |
| **Tool Gap** | [X]% | Yes | IT/Systems |
| **Complexity** | [X]% | Partial | Product |
| **Customer Preference** | [X]% | No | - |

### Preventable Escalation Analysis

```
TOTAL ESCALATIONS: [XXX]

PREVENTABLE (L1 could have resolved):
├── With training: [XX] ([X]%)
├── With empowerment: [XX] ([X]%)
├── With better tools: [XX] ([X]%)
└── TOTAL PREVENTABLE: [XX] ([X]%)

REQUIRED (L2 expertise needed):
├── Technical complexity: [XX] ([X]%)
├── System access required: [XX] ([X]%)
└── TOTAL REQUIRED: [XX] ([X]%)
```

---

## Section 5: Improvement Recommendations

### Immediate Actions (This Week)

| Priority | Action | Owner | Timeline | Expected Impact |
|----------|--------|-------|----------|-----------------|
| 1 | [Action] | [Name] | [Date] | -[X]% escalations |
| 2 | [Action] | [Name] | [Date] | -[X]% escalations |

### Short-Term Actions (30 Days)

| Priority | Action | Owner | Timeline | Expected Impact |
|----------|--------|-------|----------|-----------------|
| 1 | [Action] | [Name] | [Date] | -[X]% escalations |
| 2 | [Action] | [Name] | [Date] | -[X]% escalations |

---

## Calculation Reference

### FCR Calculation

```python
FCR_Percent = (1 - (Escalations / Total_Call_Tickets)) × 100
```

### Escalation Rate

```python
Escalation_Rate = (Total_Escalations / Total_Call_Tickets) × 100
```

### Re-Escalation Rate

```python
Re_Escalation_Rate = (Tickets_Escalated_Multiple_Times / Total_Escalated) × 100
```

### Agent Escalation Index

```python
Agent_Esc_Index = Agent_Escalation_Rate / Team_Escalation_Rate
# Index > 1.2 = Coaching trigger
```

---

## Escalation Decision Tree

```
SHOULD THIS BE ESCALATED?

1. Is this within L1 empowerment?
   ├── YES → Resolve at L1
   └── NO → Continue to step 2

2. Is the issue documented in KB?
   ├── YES → Follow documented resolution
   │         └── Still unresolved? → Escalate with notes
   └── NO → Continue to step 3

3. Has troubleshooting been exhausted?
   ├── YES → Escalate with troubleshooting summary
   └── NO → Complete troubleshooting first

4. Is this a known L2-only issue?
   ├── YES → Escalate immediately
   └── NO → Attempt L1 resolution

ESCALATION REQUIREMENTS:
├── Document all troubleshooting completed
├── Include customer account details
├── Specify issue category accurately
└── Note any time sensitivity
```

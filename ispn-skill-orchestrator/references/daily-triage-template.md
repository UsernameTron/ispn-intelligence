# Daily Performance Triage Template

## Daily Operations Dashboard

```
═══════════════════════════════════════════════════════════════════
                    DAILY PERFORMANCE TRIAGE
═══════════════════════════════════════════════════════════════════

DATE: [Date]                            DAY: [Day of Week]
SHIFT: [Morning/Afternoon/Evening]      ANALYST: [Name]

═══════════════════════════════════════════════════════════════════
```

---

## Morning Triage (Start of Day)

### Prior Day Summary

| Metric | Yesterday | Target | Status | Notes |
|--------|-----------|--------|--------|-------|
| AHT | [X:XX] | < 10:42 | 🟢🟡🔴 | |
| AWT | [X] sec | < 90s | 🟢🟡🔴 | |
| Abandoned | [XXX] | < 200 | 🟢🟡🔴 | |
| FCR | [X]% | > 70% | 🟢🟡🔴 | |
| Outage Tickets | [XXX] | < 100 | 🟢🟡🔴 | |
| Adherence | [X]% | > 90% | 🟢🟡🔴 | |
| CSAT | [X]% | > 90% | 🟢🟡🔴 | |

### Context Check

```
OPERATIONAL CONTEXT:
├── Active Outage: [ ] Yes  [X] No
│   └── If yes: [Outage description]
├── System Issues: [ ] Yes  [X] No
│   └── If yes: [Issue description]
├── Staffing Anomalies: [ ] Yes  [X] No
│   └── If yes: [Variance from plan]
├── Known Events: [ ] Yes  [X] No
│   └── If yes: [Event description]
└── Weekend/Holiday: [ ] Yes  [X] No
```

### Red Metric Investigation

```
RED METRIC: [Metric Name]
VALUE: [X] (Target: [Y], Variance: [+/-Z])

WHEN DID IT GO RED?
[Time/interval]

WHAT'S DRIVING IT?
[Root cause analysis]

IMMEDIATE ACTION NEEDED?
[ ] Yes - Action: [Description]
[ ] No - Monitor only
```

---

## Mid-Day Check (12:00-14:00)

### Current Day Status

| Metric | MTD Today | Forecast | Status | Trend |
|--------|-----------|----------|--------|-------|
| Calls Offered | [X,XXX] | [X,XXX] | 🟢🟡🔴 | [↑↓→] |
| Calls Handled | [X,XXX] | [X,XXX] | 🟢🟡🔴 | [↑↓→] |
| AHT | [X:XX] | < 10:42 | 🟢🟡🔴 | [↑↓→] |
| AWT | [X] sec | < 90s | 🟢🟡🔴 | [↑↓→] |
| Abandoned | [XXX] | < 200 | 🟢🟡🔴 | [↑↓→] |
| Service Level | [X]% | > 80% | 🟢🟡🔴 | [↑↓→] |

### Staffing Position

| Time Block | Scheduled | Actual | Variance | Action |
|------------|-----------|--------|----------|--------|
| 06:00-10:00 | [XX] | [XX] | [+/-X] | |
| 10:00-14:00 | [XX] | [XX] | [+/-X] | |
| 14:00-18:00 | [XX] | [XX] | [+/-X] | |
| 18:00-22:00 | [XX] | [XX] | [+/-X] | |

### Adjustments Made

| Time | Issue | Action Taken | Result |
|------|-------|--------------|--------|
| [HH:MM] | [Issue] | [Action] | [Outcome] |
| [HH:MM] | [Issue] | [Action] | [Outcome] |

---

## End of Day Triage

### Daily Performance Summary

| Metric | Today | Yesterday | WoW | Target | Status |
|--------|-------|-----------|-----|--------|--------|
| AHT | [X:XX] | [X:XX] | [+/-] | < 10:42 | 🟢🟡🔴 |
| AWT | [X]s | [X]s | [+/-] | < 90s | 🟢🟡🔴 |
| Abandoned | [XXX] | [XXX] | [+/-] | < 200 | 🟢🟡🔴 |
| FCR | [X]% | [X]% | [+/-] | > 70% | 🟢🟡🔴 |
| Escalations | [XXX] | [XXX] | [+/-] | < 30% | 🟢🟡🔴 |
| Adherence | [X]% | [X]% | [+/-] | > 90% | 🟢🟡🔴 |
| Quality | [X] | [X] | [+/-] | > 88 | 🟢🟡🔴 |
| CSAT | [X]% | [X]% | [+/-] | > 90% | 🟢🟡🔴 |

### Highlights & Concerns

```
TODAY'S HIGHLIGHTS:
├── [Positive outcome 1]
├── [Positive outcome 2]
└── [Positive outcome 3]

TODAY'S CONCERNS:
├── [Concern 1] - [Action/Owner]
├── [Concern 2] - [Action/Owner]
└── [Concern 3] - [Action/Owner]

TOMORROW'S WATCH ITEMS:
├── [Item 1]
├── [Item 2]
└── [Item 3]
```

---

## RAG Status Actions

### When Metric Goes RED

| Metric | Red Trigger | Immediate Action |
|--------|-------------|------------------|
| AHT > 11.5 | Sustained 2+ hours | Floor support, AHT audit, SME deployment |
| AWT > 180s | Sustained 30+ min | Break/meeting delays, OT activation |
| Abandoned > 300 | Daily total | Callback activation, all-hands |
| FCR < 65% | Daily rate | L2 support expansion, root cause |
| Adherence < 85% | Team average | Real-time coaching, accountability |
| Outage > 150 | Daily tickets | Outage protocol, messaging updates |

### When Multiple Metrics RED

```
SYSTEMIC ISSUE PROTOCOL:
1. Identify common root cause
2. Escalate to leadership
3. Activate crisis response if needed
4. Document timeline and actions
5. Post-event review within 48 hours
```

---

## Partner Status Check

| Partner | AWT | Esc Rate | Status | Action Needed |
|---------|-----|----------|--------|---------------|
| [Partner 1] | [X]s | [X]% | 🟢🟡🔴 | |
| [Partner 2] | [X]s | [X]% | 🟢🟡🔴 | |
| [Partner 3] | [X]s | [X]% | 🟢🟡🔴 | |

---

## Agent Performance Flags

### Coaching Triggers Today

| Agent | Metric | Value | Threshold | Action |
|-------|--------|-------|-----------|--------|
| [Name] | AHT | [X:XX] | > 12:00 | Coaching |
| [Name] | FCR | [X]% | < 60% | Review |
| [Name] | Adherence | [X]% | < 80% | Check-in |

### Top Performers Today

| Agent | Highlight Metric | Value | Recognition |
|-------|------------------|-------|-------------|
| [Name] | [Metric] | [Value] | [Note] |
| [Name] | [Metric] | [Value] | [Note] |

---

## Handoff Notes

### For Next Shift / Tomorrow

```
ACTIVE ISSUES:
├── [Issue 1]: [Status, next steps]
├── [Issue 2]: [Status, next steps]
└── [Issue 3]: [Status, next steps]

PENDING ACTIONS:
├── [Action 1]: [Owner, due time]
├── [Action 2]: [Owner, due time]
└── [Action 3]: [Owner, due time]

WATCH ITEMS:
├── [Item 1]: [What to monitor]
├── [Item 2]: [What to monitor]
└── [Item 3]: [What to monitor]

ESCALATIONS:
├── [Escalation 1]: [Status]
└── [Escalation 2]: [Status]
```

---

## Weekly Pattern Recognition

### Day-of-Week Performance

| Day | Avg AHT | Avg AWT | Avg Abandoned | Pattern |
|-----|---------|---------|---------------|---------|
| Mon | [X:XX] | [X]s | [XXX] | [High/Normal/Low] |
| Tue | [X:XX] | [X]s | [XXX] | [High/Normal/Low] |
| Wed | [X:XX] | [X]s | [XXX] | [High/Normal/Low] |
| Thu | [X:XX] | [X]s | [XXX] | [High/Normal/Low] |
| Fri | [X:XX] | [X]s | [XXX] | [High/Normal/Low] |
| Sat | [X:XX] | [X]s | [XXX] | [High/Normal/Low] |
| Sun | [X:XX] | [X]s | [XXX] | [High/Normal/Low] |

### Hour-of-Day Patterns

```
PEAK HOURS (highest volume/longest wait):
├── [Hour 1]: [Pattern description]
├── [Hour 2]: [Pattern description]
└── [Hour 3]: [Pattern description]

CHALLENGING HOURS (worst metrics):
├── [Hour 1]: [Which metrics, why]
├── [Hour 2]: [Which metrics, why]
└── [Hour 3]: [Which metrics, why]

OPTIMIZATION OPPORTUNITIES:
├── [Opportunity 1]
├── [Opportunity 2]
└── [Opportunity 3]
```

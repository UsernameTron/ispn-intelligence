---
name: ispn-intraday-staffing
description: |
  Real-time staffing decisions: overstaffed/understaffed assessment, VTO/OT actions.
  TRIGGERS: "overstaffed", "understaffed", "VTO", "OT", "intraday", "real-time staffing"
  Part of ISPN Workforce Intelligence Suite
---

# ISPN Intraday Staffing

## OVERSTAFFED ASSESSMENT

### Triggers
```yaml
primary_triggers:
  - AWT < 30 seconds sustained 30+ minutes
  - Occupancy < 65% sustained 30+ minutes
  - Calls-in-queue = 0 for 15+ minutes
  - Utilization < 50% for current interval
```

### Scoring Logic
```python
def assess_overstaffing():
    score = 0
    if current_awt < 30: score += 3
    if current_occupancy < 0.65: score += 3
    if calls_in_queue == 0: score += 2
    if interval_utilization < 0.50: score += 3
    if forecast_variance < -0.15: score += 2
    
    if score >= 8: return "CRITICAL_OVERSTAFFED"
    elif score >= 5: return "OVERSTAFFED"
    else: return "WITHIN_TOLERANCE"
```

### Actions by Severity

| Score | Status | Action |
|-------|--------|--------|
| ≥ 8 | Critical | Mandatory early release (lowest seniority first) |
| ≥ 5 | Overstaffed | Offer VTO, reassign to projects, cancel scheduled OT |
| < 5 | Tolerance | Monitor, no action |

### Formulas
```
Overstaffing_Magnitude = (Current_Staff - Required_Staff) / Required_Staff × 100
VTO_Hours_Available = (Actual_Staff - Required_Staff) × Remaining_Shift_Hours
```

---

## UNDERSTAFFED ASSESSMENT

### Triggers
```yaml
primary_triggers:
  - AWT > 180 seconds sustained 15+ minutes
  - Occupancy > 90% sustained 30+ minutes
  - Abandon rate > 5% for current interval
  - Calls-in-queue > 20 sustained 10+ minutes

critical_triggers:
  - AWT > 300 seconds (5 minutes)
  - Abandon rate > 10%
  - Outage declared
```

### Scoring Logic
```python
def assess_understaffing():
    if current_awt > 300 or abandon_rate > 0.10:
        return "CRITICAL", calculate_staff_gap()
    elif current_awt > 180 or abandon_rate > 0.05:
        return "WARNING", calculate_staff_gap()
    elif occupancy > 0.90 and queue_depth > 20:
        return "WARNING", calculate_staff_gap()
    return "NORMAL", 0

def calculate_staff_gap():
    calls_per_hour = current_offered_rate * 60
    required = (calls_per_hour * target_aht) / (60 * target_occupancy)
    return max(0, required - current_available)
```

### Actions by Severity

| Severity | Action | Implementation |
|----------|--------|----------------|
| WARNING | Recall breaks | Page agents on break to return early |
| WARNING | Activate on-call | Contact on-call agents immediately |
| WARNING | Request OT | Open voluntary OT |
| CRITICAL | Mandatory OT | Extend current shifts 2+ hours |
| CRITICAL | All-hands | Cancel non-critical off-queue activities |
| CRITICAL | Callback activation | Enable callback in IVR |

### Formulas
```
Staff_Gap = Required_Agents - Available_Agents
Required_Agents = (Calls_In_Queue + (Arrival_Rate × Target_Wait)) × AHT / (Target_Occupancy × 60)
Recovery_Time = Calls_In_Queue × AHT / Available_Agents
```

---

## HANDOFFS

**Receives from:**
- ispn-skill-orchestrator: Query routing
- ispn-dpr-analysis: Current interval metrics
- Genesys real-time data: Queue depth, agent states

**Sends to:**
- ispn-cost-analytics: OT/VTO cost impact
- ispn-capacity-planning: Forecast variance patterns

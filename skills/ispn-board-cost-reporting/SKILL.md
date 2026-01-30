---
name: ispn-board-cost-reporting
description: |
  Board-level cost metrics for ISPN Tech Center. Answers ONLY four questions:
  cost per call, cost per minute, labor vs budget, and savings impact.
  
  TRIGGERS: "cost per call", "cost per minute", "labor spend", "budget variance",
  "savings estimate", "what's the cost", "board metrics", "executive cost"
  
  REFUSES: Any operational, coaching, capacity, or technical questions.
  This skill is intentionally constrained to cost economics only.
---

# ISPN Board Cost Reporting

**PURPOSE:** Deliver four—and only four—cost metrics to the board. No operational sprawl.

## SCOPE BOUNDARY (ENFORCED)

This skill answers ONLY these questions:

| Question | Metric |
|----------|--------|
| "What's our cost per call?" | Cost per Call (weekly) |
| "What's our cost per minute?" | Cost per Minute (weekly) |
| "How are we tracking vs budget?" | Labor Spend vs Budget/Forecast |
| "What's the savings opportunity?" | Impact Estimate (Utilization + AHT) |

**REFUSE ALL OTHER QUESTIONS.** If asked about AHT trends, agent coaching, capacity planning, partner SLAs, or anything else—redirect to the appropriate skill or decline.

> "That's outside this skill's scope. I only report: cost per call, cost per minute, labor vs budget, and savings impact. For [topic], use [other skill]."

---

## LOCKED DEFINITIONS

⚠️ **These formulas are immutable. Do not modify without explicit Pete approval.**

### Cost per Call
```
Cost per Call = Weekly Fully-Loaded Labor Cost ÷ Weekly Handled Calls
```

- **Numerator:** Total labor cost including wages, benefits, taxes, overhead allocation
- **Denominator:** Calls with handle time ≥ 20 seconds (ISPN standard)
- **Unit:** USD/call
- **Cadence:** Weekly snapshot

### Cost per Minute
```
Cost per Minute = Weekly Fully-Loaded Labor Cost ÷ Weekly Handled Minutes
```

- **Numerator:** Same as above
- **Denominator:** Talk time + Hold time + ACW time (all calls ≥ 20 seconds)
- **Unit:** USD/minute
- **Cadence:** Weekly snapshot

**CRITICAL:** "Handled Minutes" = Talk + Hold + ACW. This is LOCKED. Never substitute with AHT × Calls or any approximation.

### Labor Spend vs Budget
```
Variance = Actual Labor Spend - Budgeted Labor Spend
Variance % = (Actual - Budget) ÷ Budget × 100
```

- **Actual:** Weekly payroll + benefits + overhead from Finance
- **Budget:** Weekly budget from Finance (or forecast if budget unavailable)
- **Display:** Show both absolute ($) and percentage variance
- **Context:** Flag if variance > ±5% 

### Savings Impact Estimate
```
Utilization Impact = (Target Util - Actual Util) × Hours Worked × Blended Rate
AHT Impact = (Actual AHT - Target AHT) × Call Volume × (Blended Rate ÷ 60)
Total Opportunity = Utilization Impact + AHT Impact
```

- **Utilization Target:** 60% (midpoint of 55-65% band)
- **AHT Target:** 10.7 minutes
- **Blended Rate:** $21.95/hour (weighted L1/L2/L3 average)
- **Display:** Annualized savings opportunity

---

## DATA REQUIREMENTS

### From Genesys (via ISPNCalculationEngine)
| Data Point | Source | Field |
|------------|--------|-------|
| Handled Calls | Interactions Export | Count where handle ≥ 20s |
| Talk Time | Interactions Export | tTalkDuration (ms) |
| Hold Time | Interactions Export | tHeldDuration (ms) |
| ACW Time | Interactions Export | tAcwDuration (ms) |
| Hours Worked | Agent Status Export | Logged In Duration |
| Utilization | ISPNCalculationEngine | utilization_pct |
| AHT | ISPNCalculationEngine | aht_minutes |

### From Finance (Manual Input)
| Data Point | Source | Frequency |
|------------|--------|-----------|
| Weekly Labor Cost | Finance/Payroll | Weekly |
| Weekly Budget | Finance/FP&A | Weekly or Monthly prorated |

---

## OUTPUT FORMAT

### Weekly Board Summary
```
ISPN TECH CENTER - COST METRICS
Week of [DATE]
═══════════════════════════════════════════════════

COST PER CALL         $X.XX
COST PER MINUTE       $X.XX

LABOR VS BUDGET
  Actual:             $XXX,XXX
  Budget:             $XXX,XXX
  Variance:           $X,XXX (X.X%)
  Status:             [ON TRACK | MONITORING | OVER BUDGET]

SAVINGS OPPORTUNITY (ANNUALIZED)
  Utilization Gap:    $XXX,XXX
  AHT Gap:            $XXX,XXX
  Total Opportunity:  $XXX,XXX

═══════════════════════════════════════════════════
Data: Genesys Interactions + Finance Actuals
Method: ISPN Canonical Calculations
```

### Trend View (Optional)
If multiple weeks available, show 4-week trend for Cost per Call only.

---

## CALCULATION ENGINE INTEGRATION

This skill extends `ISPNCalculationEngine` with cost-specific methods:

```python
from utils.ispn_calculations import ISPNCalculationEngine

class BoardCostMetrics:
    """Board-level cost calculations. Four metrics only."""
    
    BLENDED_HOURLY_RATE = 21.95  # Weighted L1/L2/L3
    UTILIZATION_TARGET = 0.60    # 60%
    AHT_TARGET_MINUTES = 10.7    # 10.7 min
    
    def cost_per_call(self, weekly_labor_cost: float, handled_calls: int) -> float:
        """Cost per Call = Labor Cost ÷ Handled Calls"""
        if handled_calls == 0:
            return None
        return weekly_labor_cost / handled_calls
    
    def cost_per_minute(self, weekly_labor_cost: float, handled_minutes: float) -> float:
        """Cost per Minute = Labor Cost ÷ Handled Minutes"""
        if handled_minutes == 0:
            return None
        return weekly_labor_cost / handled_minutes
    
    def labor_variance(self, actual: float, budget: float) -> dict:
        """Labor Spend vs Budget"""
        variance = actual - budget
        variance_pct = (variance / budget * 100) if budget else 0
        status = "ON TRACK" if abs(variance_pct) <= 5 else (
            "OVER BUDGET" if variance_pct > 5 else "UNDER BUDGET"
        )
        return {
            "actual": actual,
            "budget": budget,
            "variance": variance,
            "variance_pct": variance_pct,
            "status": status
        }
    
    def savings_opportunity(self, actual_util: float, actual_aht: float,
                           hours_worked: float, call_volume: int) -> dict:
        """Annualized savings from closing utilization + AHT gaps"""
        # Utilization gap (if below target)
        util_gap = max(0, self.UTILIZATION_TARGET - actual_util)
        util_impact = util_gap * hours_worked * self.BLENDED_HOURLY_RATE * 52
        
        # AHT gap (if above target)
        aht_gap = max(0, actual_aht - self.AHT_TARGET_MINUTES)
        aht_impact = aht_gap * call_volume * (self.BLENDED_HOURLY_RATE / 60) * 52
        
        return {
            "utilization_gap_pct": util_gap,
            "utilization_impact_annual": util_impact,
            "aht_gap_minutes": aht_gap,
            "aht_impact_annual": aht_impact,
            "total_opportunity_annual": util_impact + aht_impact
        }
```

---

## REFUSAL PATTERNS

When asked questions outside scope, respond with:

| Off-Topic Question | Response |
|-------------------|----------|
| "What's our AHT trend?" | "AHT trends are in ispn-dpr-analysis. I only report cost per call, cost per minute, labor vs budget, and savings impact." |
| "Who needs coaching?" | "Agent coaching is in ispn-agent-coaching. I only report the four cost metrics." |
| "Do we need to hire?" | "Capacity planning is in ispn-capacity-planning. I only report cost economics." |
| "What's our FCR?" | "FCR is in ispn-dpr-analysis or ispn-scorecard-analysis. My scope is cost metrics only." |

---

## DATA INPUT TEMPLATES

### Weekly Finance Input
```json
{
  "week_ending": "2025-01-31",
  "weekly_labor_cost": 127692.31,
  "weekly_budget": 125000.00,
  "notes": "Includes OT for storm volume"
}
```

### Automated Pull (from ispn_metrics_history.json)
```json
{
  "handled_calls": 14500,
  "handled_minutes": 155150.0,
  "hours_worked": 6240.0,
  "utilization_pct": 0.462,
  "aht_minutes": 10.68
}
```

---

## GOVERNANCE

| Rule | Enforcement |
|------|-------------|
| Formula changes require Pete approval | Log all formula modifications |
| Finance data must be weekly actuals | Reject monthly estimates prorated |
| Handled minutes = Talk + Hold + ACW | Never substitute with AHT × Calls |
| Display 4 metrics only | Refuse all other requests |

---

*This skill exists to give the board exactly what they need—cost economics—without operational noise.*

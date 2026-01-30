# Capacity Model Template

## Monthly Capacity Planning Worksheet

### 1. Volume Forecast

| Month | Historical Volume | Growth Adjustment | Seasonal Factor | Forecast |
|-------|------------------|-------------------|-----------------|----------|
| M1 | [12mo avg] | × [1 + growth%] | × [seasonal] | = [forecast] |
| M2 | | | | |
| M3 | | | | |

**Growth Rate Calculation:**
```
YoY_Growth = (Current_Year_Volume - Prior_Year_Volume) / Prior_Year_Volume
MoM_Growth = (Current_Month - Prior_Month) / Prior_Month
Blended_Growth = (YoY_Growth × 0.6) + (MoM_Growth × 0.4)
```

**Seasonal Factors (ISPN Baseline):**
| Month | Factor | Notes |
|-------|--------|-------|
| January | 1.05 | Post-holiday catch-up |
| February | 0.95 | Shortest month |
| March | 1.00 | Baseline |
| April | 1.00 | Baseline |
| May | 0.98 | Memorial Day |
| June | 0.97 | Summer slowdown begins |
| July | 0.95 | Peak summer |
| August | 0.97 | Back-to-school ramp |
| September | 1.02 | Fall uptick |
| October | 1.03 | Q4 ramp |
| November | 1.08 | Peak pre-holiday |
| December | 1.10 | Holiday peak |

---

### 2. Handle Time Projection

| Component | Current | 3mo Trend | Projected | Notes |
|-----------|---------|-----------|-----------|-------|
| Talk Time | [X] min | [trend] | [proj] | |
| Hold Time | [X] min | [trend] | [proj] | |
| ACW Time | 15 sec | N/A | 15 sec | System-enforced |
| **Total AHT** | [X] min | | [proj] | |

**AHT Adjustment Factors:**
- New hire impact: +0.5-1.0 min during ramp (8 weeks)
- Process change: ±0.3-0.5 min
- System change: ±0.2-0.5 min
- Training initiative: -0.2-0.5 min (lagged 4-6 weeks)

---

### 3. Capacity Requirement Calculation

**Master Formula:**
```
Required_FTE = (Monthly_Volume × AHT_Hours) / (Work_Hours × Target_Util × (1 - Shrinkage))
```

**Standard Parameters:**
| Parameter | Value | Source |
|-----------|-------|--------|
| Work_Hours_Per_Month | 173.2 | 40 hrs × 4.33 weeks |
| Target_Utilization | 0.60 | 55-65% optimal range |
| Shrinkage | 0.28 | Historical average |

**Calculation Worksheet:**

| Input | Value | Calculation |
|-------|-------|-------------|
| Monthly Volume | [X] calls | From forecast |
| AHT (hours) | [X] / 60 | Convert minutes to hours |
| Work Hours | 173.2 | Standard |
| Target Utilization | 0.60 | Adjust if needed |
| Shrinkage Factor | 0.72 | 1 - 0.28 |
| **Raw FTE** | | Volume × AHT ÷ (173.2 × 0.60 × 0.72) |

---

### 4. Attrition Buffer

**Formula:**
```
Attrition_Buffer_FTE = Monthly_Turnover_Rate × Required_FTE × (Ramp_Weeks / 4)
```

| Input | Value |
|-------|-------|
| Monthly Turnover Rate | [X]% |
| Required FTE (from above) | [X] |
| Average Ramp Weeks | 8 |
| **Buffer FTE** | = Turnover × FTE × 2 |

---

### 5. Capacity Gap Analysis

| Category | Count |
|----------|-------|
| Current Headcount | [X] |
| - Planned Terminations | [X] |
| - Pipeline Attrition (expected) | [X] |
| + Confirmed Hires | [X] |
| + Pipeline Candidates | [X] |
| **= Net Available FTE** | [X] |
| Required FTE (with buffer) | [X] |
| **= Gap (+/-)** | [X] |

---

### 6. Scenario Modeling

| Scenario | Volume Δ | AHT Δ | Required FTE | Gap |
|----------|----------|-------|--------------|-----|
| Base Case | 0% | 0% | [X] | [X] |
| Conservative | -10% | -5% | [X] | [X] |
| Aggressive | +15% | +5% | [X] | [X] |
| Partner Growth | +20% | 0% | [X] | [X] |

---

### 7. Financial Impact

**Cost Per FTE (Fully Loaded):**
| Component | Monthly | Annual |
|-----------|---------|--------|
| Base Salary | $3,500 | $42,000 |
| Benefits (30%) | $1,050 | $12,600 |
| Overhead (15%) | $525 | $6,300 |
| Training (first 8 weeks) | $583 | $7,000 |
| **Total Fully Loaded** | $5,658 | $67,900 |

**Gap Cost Analysis:**
```
If Gap = +5 FTE needed:
  Annual Investment = 5 × $67,900 = $339,500
  Monthly Burn = 5 × $5,658 = $28,290

If Gap = -3 FTE excess:
  Potential Savings = 3 × $67,900 = $203,700/year
  Natural Attrition Timeline = 3 / (Headcount × Turnover%) months
```

---

### 8. Recommendation Framework

| Gap Size | Timeframe | Recommended Action |
|----------|-----------|-------------------|
| +1-2 FTE | Immediate | OT bridge, accelerate pipeline |
| +3-5 FTE | 30-45 days | Expedited hiring class |
| +6-10 FTE | 60-90 days | Major hiring initiative |
| +10+ FTE | 90+ days | Strategic staffing plan, temp staff bridge |
| -1-2 FTE | Ongoing | Natural attrition, expanded VTO |
| -3-5 FTE | 30-60 days | Hiring freeze, targeted VTO |
| -5+ FTE | 60-90 days | Reduction planning required |

---

## Quick Calculation Reference

**FTE from Call Volume:**
```python
def calculate_fte(monthly_volume, aht_minutes, utilization=0.60, shrinkage=0.28):
    aht_hours = aht_minutes / 60
    work_hours = 173.2
    effective_factor = utilization * (1 - shrinkage)
    return (monthly_volume * aht_hours) / (work_hours * effective_factor)

# Example: 50,000 calls, 10.7 min AHT
# FTE = (50000 × 0.178) / (173.2 × 0.60 × 0.72) = 119 FTE
```

**Calls Per FTE Per Month:**
```
Calls_Per_FTE = Work_Hours × Utilization × (1 - Shrinkage) × 60 / AHT_Minutes
             = 173.2 × 0.60 × 0.72 × 60 / 10.7
             = 420 calls/FTE/month
```

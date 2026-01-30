---
name: genesys-queue-performance-analysis
description: Comprehensive analysis of Genesys Cloud queue performance metrics including service level diagnostics, routing efficiency, skill mismatch detection, abandon pattern analysis, and queue-to-queue comparisons. Diagnoses why queues underperform and identifies root causes (staffing, routing, skill gaps). Triggers on "analyze queue performance", "queue metrics", "why is service level low", "queue comparison", "routing issues", "skill mismatch", "abandon analysis".
version: 1.0.0
---

# Genesys Queue Performance Analysis

Analyze Genesys Cloud CX queue performance, diagnose routing issues, and identify root causes of service level problems.

## When to Use This Skill

**Trigger phrases:**
- "Analyze queue performance for [queue name]"
- "Why is [queue] service level low?"
- "Compare queues [A] and [B]"
- "Which queue is underperforming?"
- "Diagnose routing issues in [queue]"
- "Why are calls waiting despite idle agents?"
- "Analyze abandon patterns"
- "Queue efficiency report"

**Use this skill when:**
- Service level targets are missed
- Abandon rates are elevated
- Average wait time is high despite adequate staffing
- Calls wait in queue while agents are idle (skill mismatch)
- Queue performance varies significantly by time of day
- Comparing multiple queues to identify best/worst performers
- Investigating routing configuration issues

---

## Core Queue Metrics Explained

### 1. **Offered Calls**
**Definition:** Number of interactions routed into the queue
- Every incoming call counts when it enters the queue
- Includes calls that are answered, abandoned, or flow out (callbacks)
- Key formula: `Offered = Answered + Abandoned + Flow-outs`

**Analysis:**
- If Offered > (Answered + Abandoned), the difference = flow-outs (callbacks, transfers to other queues)
- High offered volume without corresponding staffing = service level problem
- Compare offered vs. forecast to detect volume spikes

### 2. **Answered Calls**
**Definition:** Interactions actually connected to an agent
- Counts at the moment agent picks up
- Does NOT include abandoned calls or callbacks requested

**Analysis:**
- Answer Rate = (Answered ÷ Offered) × 100
- Target: typically 90%+ for well-staffed queues
- If Answer Rate < 85%, investigate abandon rate and staffing

### 3. **Abandoned Calls**
**Definition:** Interactions where customer disconnected before reaching agent
- Only counts if customer hangs up (not callbacks)
- Short abandons (<60 sec) may be excluded depending on SLA settings

**ISPN Standard:** Count as abandoned only if Queue Time >= 60 seconds

**Analysis:**
- Abandon Rate = (Abandoned ÷ Offered) × 100
- Target: <5% for most operations
- High abandons = understaffing, long wait times, or poor IVR experience
- Check **average abandon time** to see when customers give up

**Common patterns:**
- Many abandons at 120-180 sec = customers lose patience
- Many abandons at 5-10 sec = wrong number, accidental dials
- Abandons spike during peak hours = insufficient staffing

### 4. **Average Wait Time (AWT)**
**Definition:** Average time interactions spend in queue waiting for answer
- Includes ALL interactions (answered AND abandoned)
- Measured from queue entry to agent answer (or abandon/flow-out)

**ISPN Standard:** AWT in seconds, target <90 seconds

**Analysis:**
- AWT reflects overall queue delay experience
- High AWT = customers wait longer (correlates with abandons and low CSAT)
- Compare to Average Speed of Answer (ASA)

### 5. **Average Speed of Answer (ASA)**
**Definition:** Average wait time for ANSWERED calls only
- Excludes abandoned and flow-out calls
- Only measures queue time until agent picks up

**Analysis:**
- ASA is typically LOWER than AWT (because long-wait abandons aren't included)
- If ASA is low but abandons are high, many people hung up early (not captured in ASA)
- **Always analyze ASA + Abandon Rate together**

**Example:**
- ASA = 15 seconds (looks good!)
- But Abandon Rate = 20% (terrible!)
- Interpretation: Only fast-answered calls count in ASA; many others abandoned after 2+ minutes

### 6. **Service Level (SL)**
**Definition:** Percentage of calls answered within threshold time
- Common thresholds: 80/30 (80% in 30 sec), 80/60, 80/90, 80/120
- Genesys allows configuring what counts in denominator (abandons, flow-outs)

**ISPN Standards:**
- Threshold varies by queue (typically 30-120 seconds)
- Target: 80%+ within threshold

**Analysis:**
- If SL is below target, check:
  1. Are enough agents staffed?
  2. Is AHT longer than expected?
  3. Are agents On Queue (check adherence)?
  4. Are skills properly assigned (skill mismatch)?

**SLA Configuration Impact:**
- Including abandons in SLA lowers SL% (abandoned calls count as "not answered in threshold")
- Excluding flow-outs (callbacks) removes them from denominator
- ISPN default: Exclude short abandons (<60 sec) from SLA calculation

### 7. **Average Handle Time (AHT)**
**Definition:** Total time to process an interaction
- Formula: `AHT = Talk Time + Hold Time + After-Call Work (ACW)`
- For outbound: Also includes dialing/ringing time

**ISPN Standard:** AHT in minutes, target <10.7 minutes (varies by queue/skill)

**Analysis:**
- High AHT reduces agent capacity (fewer calls per hour)
- Compare actual AHT to forecast; if higher, may need more agents to maintain SL
- Break down into components:
  - High Talk Time = complex calls or agent needs training
  - High Hold Time = knowledge gaps, system issues
  - High ACW = process inefficiency or data entry burden

### 8. **Occupancy**
**Definition:** Percentage of on-queue time spent actively handling interactions
- Formula: `Occupancy = (Interacting Time ÷ On-Queue Time) × 100`
- "Interacting" = talk + hold + ACW

**ISPN Standard:** Target >75%

**Analysis:**
- Low occupancy (<60%) = agents idle frequently, possibly overstaffed
- High occupancy (>90%) = agents back-to-back with no breathing room, burnout risk
- Target sweet spot: 75-85% for sustainable performance

---

## Queue Performance Diagnostics Framework

### Scenario 1: Service Level Below Target

**Symptoms:**
- SL% < 80% (or queue target)
- Increasing trend of missed SL

**Diagnostic Steps:**

1. **Check Offered Volume**
   - Is volume higher than forecast?
   - Run: Compare actual offered calls vs. WFM forecast by interval

2. **Check Staffing Levels**
   - Are enough agents on queue?
   - Run: Compare actual agents on queue vs. scheduled
   - Check adherence: Are scheduled agents actually on queue?

3. **Check AHT**
   - Is AHT higher than expected?
   - If AHT increased, same staffing handles fewer calls
   - Cross-reference with HelpDesk categories (are complex calls spiking?)

4. **Check Skill Matching**
   - Are calls waiting despite idle agents?
   - This indicates skill mismatch (agents don't have required skills)
   - Use Skills Performance view to see if certain skill groups have long waits

5. **Check Interval Performance**
   - Is SL missed only at certain hours?
   - Peak hour understaffing vs. all-day problem
   - Use intraday monitoring to spot patterns

**Root Causes & Solutions:**

| Root Cause | Evidence | Solution |
|------------|----------|----------|
| Volume spike | Offered >> Forecast | Adjust forecast, add contingency staff |
| Understaffing | Agents on queue < Required | Schedule more agents, authorize OT |
| Poor adherence | Scheduled agents not on queue | Coach agents, improve schedule compliance |
| High AHT | AHT increased from baseline | Training, process improvement, knowledge base |
| Skill mismatch | Calls waiting + agents idle | Assign skills to agents, adjust routing logic |
| Routing config issue | Bullseye not expanding, wrong eval method | Review queue routing settings |

---

### Scenario 2: High Abandon Rate

**Symptoms:**
- Abandon Rate > 5%
- Customers hanging up before reaching agents

**Diagnostic Steps:**

1. **Analyze Abandon Time Distribution**
   - Use Genesys "Abandon Intervals" report
   - When are customers abandoning? (30s, 60s, 120s, 180s+?)

2. **Compare AWT vs. Customer Patience**
   - If average abandon time = 90 sec, but AWT = 120 sec, customers abandon before typical answer
   - Indicates wait times exceed patience threshold

3. **Check Service Level by Interval**
   - Are abandons concentrated in specific hours?
   - Morning rush, lunch, afternoon spikes?

4. **Review Callback Availability**
   - Are callbacks offered?
   - Callback usage reduces abandons (customers opt for callback instead of hanging up)

5. **Evaluate IVR Experience**
   - Are many abandons happening in first 10 seconds?
   - Could indicate IVR issues (confusing menu, long messages)

**Root Causes & Solutions:**

| Root Cause | Evidence | Solution |
|------------|----------|----------|
| Long wait times | AWT > 90 sec, ASA > 60 sec | Increase staffing, improve AHT |
| Peak hour staffing gap | Abandons spike 10-11am | Adjust schedules to cover peak |
| No callback option | Flow-outs = 0 | Implement callback routing |
| IVR friction | Many short abandons (<20 sec) | Simplify IVR, reduce menu depth |
| Wrong expectations | Abandons at 30-60 sec | Set IVR expectations ("2 min wait"), offer callback |

---

### Scenario 3: Skill Mismatch (Calls Waiting + Agents Idle)

**Symptoms:**
- Calls waiting in queue
- Agents on queue and idle
- Service level low despite available agents

**Diagnostic Steps:**

1. **Identify Required Skills**
   - What skills are attached to waiting interactions?
   - Use Genesys Skills Performance view

2. **Check Agent Skill Assignments**
   - Do on-queue agents have required skills?
   - Example: Queue requires "Billing + Spanish" but only "Billing" agents are available

3. **Review Bullseye Configuration**
   - Is bullseye routing set up?
   - Are skill requirements relaxing over time?
   - If bullseye Ring 1 requires Skill X but no one has it, calls stuck in Ring 1

4. **Check Evaluation Method**
   - Queue set to "All Skills Matching" vs. "Best Available Skills"?
   - "Disregard Skills" mode bypasses skill requirements (rarely appropriate)

5. **Validate Skill Definitions**
   - Are skill names spelled correctly in Architect flows?
   - Case-sensitive: "billing" ≠ "Billing"
   - Use Find Skill action to validate skill exists

**Root Causes & Solutions:**

| Root Cause | Evidence | Solution |
|------------|----------|----------|
| No agents with required skill | Waiting calls, idle agents, different skills | Train/assign skill to agents, or use bullseye to relax |
| Bullseye not expanding | Calls stuck in Ring 1 | Reduce ring timeout, add more rings |
| Wrong evaluation method | Best Available when should be All Skills | Change queue evaluation method |
| Skill definition error | Typo in Architect flow | Fix flow, validate skill names |
| Language mismatch | Spanish calls, no Spanish agents | Schedule Spanish-skilled agents, expand coverage |

---

### Scenario 4: Queue-to-Queue Performance Variance

**Symptoms:**
- Queue A consistently outperforms Queue B
- Same staffing model, different results

**Diagnostic Steps:**

1. **Compare Core Metrics**
   - SL%, Abandon Rate, AHT, ASA side-by-side
   - Identify which metrics differ most

2. **Normalize for Volume**
   - Calculate efficiency: Handled Calls ÷ Agent Hours
   - Queue A might have 2x volume but same agent hours = double efficiency

3. **Analyze Call Complexity**
   - Cross-reference with HelpDesk categories
   - Queue A = simple password resets (low AHT)
   - Queue B = technical troubleshooting (high AHT)

4. **Check Agent Skill Proficiency**
   - Are Queue A agents more experienced?
   - Use Best Available Skills evaluation to route to highest proficiency

5. **Review Routing Configuration**
   - Different bullseye settings?
   - Different agent groups assigned?

**Root Causes & Solutions:**

| Root Cause | Evidence | Solution |
|------------|----------|----------|
| Call complexity difference | Queue B AHT 15 min, Queue A AHT 6 min | Adjust staffing ratios, accept different targets |
| Agent experience gap | Queue A agents tenured, Queue B new hires | Cross-train, coaching, knowledge transfer |
| Routing inefficiency | Queue B has restrictive skills, Queue A open | Review skill requirements, consider bullseye |
| Volume mismatch | Queue B understaffed for volume | Rebalance agents, adjust schedules |

---

## Common Genesys Reporting Pitfalls

### Pitfall 1: Offered ≠ Handled in Short Intervals

**Problem:**
- Looking at 30-minute interval report
- Offered = 50 calls, Handled = 42 calls
- "Where did 8 calls go?"

**Explanation:**
- Genesys attributes metrics to interval when interaction **completes**
- A 45-minute call starting at 2:00 PM counts as "handled" in the 2:30-3:00 interval (when it ends)
- It counted as "offered" in the 2:00-2:30 interval (when it arrived)

**Solution:**
- Use daily/weekly aggregates for accurate totals
- For interval analysis, understand carryover calls span intervals

---

### Pitfall 2: ASA Looks Good But Abandons Are High

**Problem:**
- ASA = 20 seconds (within target)
- Abandon Rate = 15% (terrible)
- Manager thinks performance is good based on ASA

**Explanation:**
- ASA only measures answered calls
- Customers who hung up after 2 minutes don't count in ASA
- ASA is "survivorship bias" - only fast-answered calls counted

**Solution:**
- ALWAYS review ASA + Abandon Rate + AWT together
- AWT gives true picture (includes everyone)

---

### Pitfall 3: Double-Counting Transfers

**Problem:**
- Call transferred from Queue A to Queue B
- Summing "Offered" across both queues counts call twice

**Explanation:**
- Each queue counts the call as "offered" when it arrives
- Same interaction counted multiple times across queues

**Solution:**
- Use conversation-level reporting for unique call counts
- Acknowledge that queue-level "offered" includes transfers
- Track transfer rate as separate metric

---

### Pitfall 4: Callback Confusion

**Problem:**
- Customer requests callback
- Original call not counted as "abandoned"
- But also not "answered"
- Where did it go?

**Explanation:**
- Genesys counts callback requests as **flow-outs**, not abandons
- Customer willingly left queue for callback
- Callback later appears as outbound call (when agent calls back)

**Solution:**
- Track callbacks separately
- Understand flow-outs are callbacks, not lost calls
- Configure SLA to include/exclude flow-outs per business rules

---

### Pitfall 5: Short Abandons Skewing Metrics

**Problem:**
- Abandon rate looks high (12%)
- But many abandons are <10 seconds (wrong number, pocket dials)

**Explanation:**
- Genesys counts all abandons by default
- Short abandons (<60 sec) are often not "real" abandons

**ISPN Standard:**
- Only count abandons where Queue Time >= 60 seconds
- Filter out short abandons in reporting

**Solution:**
- Use Genesys "Short Abandon" threshold setting
- Exclude short abandons from SLA calculation
- Report "meaningful abandons" separately

---

## Queue Analysis Workflows

### Workflow 1: Daily Queue Health Check

**Inputs:**
- Genesys Queue Performance report (yesterday)
- ISPN targets (SL, Abandon%, AHT, AWT)

**Steps:**

1. **Load Queue Performance Data**
```python
# Use queue_health_analyzer.py script
python queue_health_analyzer.py --file queues_performance.csv --targets ispn_targets.json
```

2. **Flag Queues Missing Targets**
   - Identify queues where SL < 80%, Abandon > 5%, AWT > 90 sec

3. **Generate Summary**
   - Top 3 worst-performing queues
   - Root cause hypothesis for each (volume, staffing, AHT, skills)

4. **Recommendations**
   - Actionable next steps (add agents, review routing, coaching)

**Output:** Daily queue performance email to operations team

---

### Workflow 2: Skill Mismatch Investigation

**Inputs:**
- Genesys Skills Performance report
- Agent Status report (who was on queue)
- Queue configuration export

**Steps:**

1. **Identify Long-Wait Skill Groups**
   - Which skill combinations have ASA > 120 seconds?

2. **Check Agent Availability**
   - Were agents with those skills on queue during wait times?
   - Use Agent Status data filtered by skills

3. **Validate Routing Logic**
   - Review Architect flow for skill assignment
   - Check queue bullseye configuration

4. **Quantify Impact**
   - How many calls affected?
   - What's the FTE cost of extended waits?

**Output:** Skill coverage gap report with staffing recommendations

---

### Workflow 3: Intraday Performance Monitoring

**Inputs:**
- Genesys Intraday Monitoring view (live)
- WFM forecast (expected volume, AHT, agents)

**Steps:**

1. **Compare Actual vs. Forecast by Interval**
   - Volume variance (offered vs. forecast)
   - AHT variance (actual vs. forecast)
   - Agent variance (actual on queue vs. scheduled)

2. **Detect Adverse Trends**
   - If current interval SL < 70%, alert supervisor
   - If abandon rate spiking, trigger action

3. **Recommend Interventions**
   - Pull agents from back-office
   - Authorize overtime
   - Offer callbacks proactively

**Output:** Real-time alerts and staffing adjustment recommendations

---

### Workflow 4: Queue Efficiency Benchmarking

**Inputs:**
- Queue Performance data (all queues, past month)
- HelpDesk ticket categories (call complexity proxy)

**Steps:**

1. **Calculate Efficiency Metrics**
   - Calls handled per agent hour
   - AHT by queue
   - First-call resolution rate (if available)

2. **Normalize for Complexity**
   - Link queue to dominant HelpDesk categories
   - Adjust expectations (technical queues naturally higher AHT)

3. **Rank Queues**
   - Best performers (high efficiency, low AHT, high SL)
   - Worst performers (low efficiency, high abandons)

4. **Identify Best Practices**
   - What are top queues doing differently?
   - Routing config, agent training, tools?

**Output:** Queue efficiency scorecard with improvement opportunities

---

## Integration with Other Skills

### With `genesys-cloud-cx-reporting`
**How they work together:**
- `genesys-cloud-cx-reporting` tells you *which exports to run*
- `genesys-queue-performance-analysis` tells you *how to interpret them*

**Example:**
- User: "Which Genesys report shows queue abandons?"
- Use `genesys-cloud-cx-reporting` → "Run Interactions export filtered by Abandoned=Yes"
- User: "Why is abandon rate high?"
- Use `genesys-queue-performance-analysis` → diagnostic framework

---

### With `genesys-skills-routing`
**How they work together:**
- `genesys-skills-routing` explains *how routing works* (bullseye, eval methods)
- `genesys-queue-performance-analysis` diagnoses *why routing isn't working*

**Example:**
- User: "Calls are waiting but agents are idle"
- Use `genesys-queue-performance-analysis` → skill mismatch diagnosis
- Use `genesys-skills-routing` → how to fix bullseye config or skill assignments

---

### With `helpdesk-ticket-analysis`
**How they work together:**
- `helpdesk-ticket-analysis` shows *what* calls were about (categories, complexity)
- `genesys-queue-performance-analysis` shows *how efficiently* those calls were handled (queue metrics)

**Example:**
- User: "Queue A has high AHT, why?"
- Use `genesys-queue-performance-analysis` → AHT breakdown by component
- Use `helpdesk-ticket-analysis` → cross-reference with categories (maybe Queue A handles complex Connectivity issues)

---

### With `analyzing-ispn-wcs-reports`
**How they work together:**
- `analyzing-ispn-wcs-reports` provides weekly summary stats (call volume, AHT, partner performance)
- `genesys-queue-performance-analysis` provides detailed daily/interval-level diagnostics

**Example:**
- User: "WCS shows Gateway Fiber had elevated AHT this week"
- Use `genesys-queue-performance-analysis` → drill into daily queue performance to find which days/intervals spiked

---

## Reference Files

### 1. **queue-metrics-definitions.md**
Comprehensive definitions of all Genesys queue metrics with formulas, targets, and interpretation guidance.

### 2. **routing-impact-analysis.md**
How routing configuration (skills, bullseye, evaluation methods) affects queue performance. Includes troubleshooting checklist.

### 3. **ispn-calculation-methodology.md**
ISPN Network Services standardized KPI calculations, data sources, and filtering rules.

### 4. **common-pitfalls.md**
Catalog of frequent Genesys reporting mistakes and how to avoid them.

---

## Python Scripts

### `queue_health_analyzer.py`
Analyzes queue performance data against targets, flags underperformers, generates summary reports.

**Usage:**
```bash
python queue_health_analyzer.py --file queues_performance.csv --targets targets.json --output report.md
```

**Features:**
- Loads Genesys Queue Performance export
- Compares to target thresholds
- Calculates variance from baseline
- Generates markdown summary with flagged queues

---

### `routing_diagnostics.py`
Diagnoses skill mismatch issues by cross-referencing queue performance with agent status and skills.

**Usage:**
```bash
python routing_diagnostics.py --queues queues.csv --agents agent_status.csv --skills skills_performance.csv
```

**Features:**
- Identifies queues with skill mismatch (calls waiting + agents idle)
- Shows which skills are bottlenecks
- Recommends skill assignments or routing changes

---

### `interval_comparison.py`
Compares actual intraday performance vs. forecast to detect real-time issues.

**Usage:**
```bash
python interval_comparison.py --actual intraday_actual.csv --forecast wfm_forecast.csv --threshold 0.2
```

**Features:**
- Interval-by-interval variance analysis
- Flags intervals where SL dropped >20% vs. forecast
- Identifies root cause (volume spike, understaffing, AHT increase)

---

## Key Formulas (ISPN Standards)

### Service Level
```
SL% = (Calls Answered Within Threshold ÷ Total Eligible Calls) × 100
```
- Threshold: 30, 60, 90, or 120 seconds (queue-specific)
- Eligible Calls: Exclude abandoned calls <60 seconds

### Abandon Rate
```
Abandon Rate = (Abandoned Calls ÷ Offered Calls) × 100
```
- Count only abandons where Queue Time >= 60 seconds
- Target: <5%

### Average Handle Time
```
AHT = Total Handle Time ÷ Number of Handled Calls
```
- Include only: Inbound, not abandoned, handle time >= 20 seconds
- Result in minutes
- Target: <10.7 minutes (Gateway Fiber baseline)

### Average Wait Time
```
AWT = Total Queue Time ÷ Number of Inbound Calls
```
- Include ALL inbound (answered + abandoned)
- Result in seconds
- Target: <90 seconds

### Occupancy
```
Occupancy = (Inbound + Outbound + Callback Hours) ÷ On-Queue Hours × 100
```
- Target: >75%

### Utilization
```
Utilization = Inbound Call Hours ÷ (Logged In - Training) × 100
```
- Target: >55%

---

## Best Practices

### 1. Always Analyze Multiple Metrics Together
Don't evaluate queues on a single metric:
- High SL but also high AHT = inefficient (achieving SL through overstaffing)
- Low ASA but high abandons = misleading (survivorship bias)
- Use dashboard approach: SL + Abandons + AWT + AHT + Occupancy

### 2. Normalize for Call Complexity
Not all queues are equal:
- Technical support queues naturally have higher AHT
- Billing queues may have lower AHT but higher volume
- Compare queues handling similar call types

### 3. Use Interval Granularity for Root Cause
Daily totals hide problems:
- Queue might meet daily SL target (82%) but miss every morning interval
- Break down by 30-minute intervals to spot patterns

### 4. Validate Data Quality First
Before diagnosing performance issues, check:
- Are filters applied correctly? (Inbound only, handled only)
- Are thresholds consistent? (60-second abandon threshold)
- Do totals reconcile? (Offered = Answered + Abandoned + Flow-outs)

### 5. Tie Back to Business Impact
Quantify performance gaps:
- 10% abandon rate = 200 lost calls/day = $X revenue at risk
- 5-minute excess AHT = 2 FTE wasted = $XXX,XXX annual cost
- Helps justify staffing or technology investments

---

## Troubleshooting Common Issues

### Issue: "Queue SL is 85% but feels worse"
**Check:**
1. Is SLA configuration including abandons?
2. Are short abandons excluded?
3. What's the actual abandon rate?
4. Are we hitting target during peak hours or only off-peak?

**Likely cause:** SLA calculation excluding abandoned calls makes SL look better than customer experience

---

### Issue: "Added 5 agents but SL didn't improve"
**Check:**
1. Are those agents actually on queue? (Check adherence)
2. Do they have required skills?
3. Did call volume increase at same time?
4. Did AHT increase (negating capacity gain)?

**Likely cause:** Skill mismatch or agents not adhering to schedule

---

### Issue: "Queue A outperforms Queue B with same staffing"
**Check:**
1. Compare AHT (is one queue handling simpler calls?)
2. Compare offered volume (is one queue busier?)
3. Compare agent experience (tenured vs. new hires?)
4. Compare routing config (different bullseye/eval methods?)

**Likely cause:** Call complexity difference or agent proficiency gap

---

## Quick Reference: Metric Targets

| Metric | ISPN Target | Industry Benchmark |
|--------|-------------|-------------------|
| Service Level | 80%+ (within threshold) | 80-90% |
| Abandon Rate | <5% | <5-8% |
| Average Wait Time | <90 seconds | <60-120 seconds |
| Average Handle Time | <10.7 minutes | Varies by industry |
| Occupancy | >75% | 75-85% |
| Answer Rate | >90% | >90% |
| Average Speed of Answer | <60 seconds | <30-60 seconds |

---

## Summary

This skill provides:
- ✅ Comprehensive queue performance diagnostics
- ✅ Root cause analysis frameworks for common issues
- ✅ Integration with existing Genesys and ISPN reporting skills
- ✅ Python tools for automated analysis
- ✅ ISPN-specific calculation standards and targets

**Next steps after analysis:**
1. Use findings to inform coaching (agent-performance-coaching-framework skill)
2. Quantify FTE impact (workforce-management-optimization skill)
3. Generate executive summary (executive-briefing-builder skill)

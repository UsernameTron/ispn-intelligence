# Common Genesys Reporting Pitfalls
**Source:** Genesys Cloud Reporting and Analytics - Data Timing and Interpretation section

Catalog of frequent mistakes when interpreting Genesys Cloud reports and how to avoid them.

---

## Pitfall 1: Offered ≠ Handled in Interval Reports

### The Problem
Looking at a 30-minute interval report:
- Offered = 50 calls
- Handled = 42 calls
- **Question:** "Where did 8 calls go? Are they lost?"

### The Explanation
Genesys attributes metrics to the interval when the interaction **completes**, not when it starts.

**Timeline example:**
```
2:00 PM - Call arrives (counts as "Offered" in 2:00-2:30 interval)
2:15 PM - Agent answers
2:45 PM - Call ends with ACW complete (counts as "Handled" in 2:30-3:00 interval)
```

Result: Call counted as offered in one interval, handled in another.

### Why This Happens
- **Offered:** Counted when call enters queue
- **Answered:** Counted when agent picks up
- **Handled:** Counted when call **fully completes** (including ACW)

For **long calls spanning intervals**, metrics split across intervals.

### The Solution

**For accurate totals:**
- Use **daily or weekly aggregates** instead of 30-minute intervals
- Over a full day, Offered ≈ Handled (discrepancies reconcile)

**For interval analysis:**
- Understand that carryover is normal
- Look for patterns (peak hours) not exact interval math
- Use "Completed" metric instead of "Handled" (shows what finished in interval)

**Validation check:**
```
Daily Offered = Daily Handled + Active calls at midnight + Data errors
```
(Active calls = interactions still in progress at day boundary)

---

## Pitfall 2: ASA Looks Good But Abandons Are High

### The Problem
Performance dashboard shows:
- ASA = 20 seconds (within 30-second target! ✓)
- Abandon Rate = 15% (yikes! ✗)
- **Manager thinks performance is acceptable because ASA is good**

### The Explanation
ASA only measures **answered calls**. Customers who hung up after 2+ minutes don't count.

**Survivorship bias:**
```
100 calls offered:
- 70 answered quickly (avg 20 seconds wait) → ASA = 20 sec
- 30 abandoned after 120+ seconds → NOT in ASA calculation

ASA = 20 seconds (looks great!)
But 30% of customers waited 2+ minutes and gave up
```

### Why This Happens
**ASA formula:**
```
ASA = Total Wait Time for ANSWERED Calls ÷ Number of Answered Calls
```

Abandons are **excluded** from both numerator and denominator.

### The Solution

**ALWAYS analyze THREE metrics together:**
1. **ASA** - How long did answered calls wait?
2. **Abandon Rate** - What % hung up?
3. **AWT (Average Wait Time)** - How long did EVERYONE wait (includes abandons)?

**Red flag pattern:**
- ASA < 30 seconds (good)
- Abandon Rate > 10% (bad)
- AWT > 90 seconds (bad)

**Interpretation:** Only fast calls counted in ASA. Many customers waited much longer and abandoned.

**Correct metric to monitor:**
- If abandon rate is high, focus on **AWT** for true customer experience
- ASA is useful but incomplete

---

## Pitfall 3: Double-Counting Transfers

### The Problem
Summing queue metrics across all queues:
- Queue A: 100 offered calls
- Queue B: 50 offered calls
- **Total = 150 calls offered**

But unique customer calls = 125 (not 150).

### The Explanation
When a call transfers from Queue A to Queue B:
- Queue A counts it as "offered" (call arrived in Queue A)
- Queue B counts it as "offered" (call arrived in Queue B)
- **Same call counted twice**

**Transfer scenario:**
```
1. Customer calls, enters Queue A
   - Queue A: Offered +1
   
2. Agent A answers, realizes needs Queue B expertise, transfers
   - Queue A: Answered +1
   
3. Call now in Queue B waiting for Agent B
   - Queue B: Offered +1
   
4. Agent B answers and resolves
   - Queue B: Answered +1

Result:
- Total Offered = 2 (Queue A + Queue B)
- Unique customer calls = 1
```

### Why This Happens
Each queue tracks interactions **from its own perspective**. A transfer is a "new" interaction arrival for the receiving queue.

### The Solution

**For unique call counts:**
- Use **conversation-level reporting** (interaction ID)
- Count unique conversation IDs across all queues
- Genesys Conversation Detail API provides unique identifiers

**For queue performance:**
- Understand that "offered" includes transfers (by design)
- Track **transfer rate** as separate metric:
  ```
  Transfer Rate = (Calls Transferred Out ÷ Calls Answered) × 100
  ```

**For business reporting:**
- Report **unique customer contacts** separately from queue workload
- Queue workload (offered) legitimately higher due to transfers

**Data reconciliation:**
```
Total Queue Workload (Offered) = Unique Customer Calls + Internal Transfers
```

---

## Pitfall 4: Callback Confusion

### The Problem
Queue metrics show:
- 100 calls offered
- 80 answered
- 10 abandoned
- **Where are the other 10 calls?**

### The Explanation
The missing 10 calls are **callbacks** (flow-outs).

**What happened:**
```
Customer in queue, wait time = 2 minutes
IVR offers callback: "Press 1 to request callback"
Customer presses 1
Original call disconnects
Callback request created (stays in queue until agent available)
```

**From Genesys perspective:**
- Original call = **flow-out** (NOT abandoned, NOT answered)
- Callback later delivered to agent as outbound call

### Why This Happens
Genesys counts callback requests as **flow-outs**, a separate category from answers and abandons.

**Queue metric formula:**
```
Offered = Answered + Abandoned + Flow-outs
```

### The Solution

**Track callbacks separately:**
```
Callback Count = Interactions where Media Type = "callback"
```

**Monitor callback success:**
- How many callbacks were requested?
- How many callbacks reached customer?
- Callback success rate = (Callbacks connected ÷ Callbacks requested) × 100

**Configure Service Level calculation:**
- Decide if flow-outs (callbacks) count in SL denominator
- ISPN standard: Exclude flow-outs from SL (focus on live answer performance)

**Avoid confusion:**
- Callback request = NOT an abandoned call (customer chose callback)
- Callback request = NOT a lost call (will be delivered later)
- Monitor to ensure callbacks eventually connect

---

## Pitfall 5: Short Abandons Skewing Metrics

### The Problem
Abandon rate report shows:
- Abandon Rate = 12% (above 5% target)
- **But digging deeper: 50% of abandons are <10 seconds**

### The Explanation
Not all abandons are equal:
- **Short abandons (<10-60 sec):** Wrong number, pocket dials, changed mind immediately
- **Long abandons (>60 sec):** Customer waited, lost patience, hung up

**Example data:**
```
200 offered calls:
- 175 answered
- 25 abandoned:
  - 15 abandoned at 5-15 seconds (wrong number)
  - 10 abandoned at 90-180 seconds (lost patience)

Abandon Rate = 25/200 = 12.5% (looks bad)

But "meaningful" abandons (>60 sec) = 10/200 = 5% (target)
```

### Why This Happens
Genesys counts **all abandons** by default, regardless of how long customer waited.

### The Solution

**Configure short abandon threshold:**
- Genesys allows defining minimum queue time (e.g., 10, 30, 60 seconds)
- Abandons below threshold excluded from counts

**ISPN Standard:**
- Short abandon threshold = 60 seconds
- Only count abandons where Queue Time >= 60 seconds
- Excludes accidental dials and immediate hang-ups

**Report two metrics:**
1. **Total Abandon Rate:** All abandons (for completeness)
2. **Meaningful Abandon Rate:** Abandons >60 seconds (for action)

**Service Level configuration:**
- Exclude short abandons from SL calculation
- Focus on customers who genuinely waited

**Genesys configuration:**
```
Queue Settings > Service Level Configuration:
☐ Include Short Abandons
☑ Short Abandon Threshold: 60 seconds
```

---

## Pitfall 6: Occupancy vs. Utilization Confusion

### The Problem
Manager reports:
- "Agent occupancy is 90% - we're very efficient!"
- **But agents complain about burnout**

### The Explanation
**Occupancy** measures time on calls relative to **on-queue time** (excludes breaks, meetings).

**High occupancy (>90%) means:**
- Agents are back-to-back on calls
- No breathing room between calls
- No time for side tasks
- Burnout risk

**Confusion with Utilization:**
- **Utilization** = Productive time ÷ Total paid time (includes breaks)
- **Occupancy** = On-call time ÷ Available time (on-queue only)

**Example:**
```
Agent works 8-hour shift:
- 1 hour: Breaks, meals (not on-queue)
- 7 hours: On-queue
  - 6.3 hours: Handling calls
  - 0.7 hours: Idle (waiting for calls)

Occupancy = 6.3 / 7.0 = 90%
Utilization = 6.3 / 8.0 = 79%
```

### Why This Happens
Occupancy denominator is smaller (on-queue time only), so percentage is higher.

### The Solution

**Target sweet spots:**
- **Occupancy:** 75-85% (allows some breathing room)
- **Utilization:** 55-65% (accounts for breaks, training, meetings)

**Red flags:**
- Occupancy >95% = Burnout risk, quality may suffer
- Occupancy <60% = Understaffed or overstaffed

**Monitor both metrics:**
- High occupancy + low utilization = Agents idle for long periods then slammed
- High occupancy + high utilization = Sustained heavy workload

**Don't chase 100% occupancy:**
- Agents need brief recovery between calls
- Industry best practice: 80-85% occupancy

---

## Pitfall 7: Timezone and Business Hours Effects

### The Problem
Queue performance report shows:
- Service Level = 100% (perfect!)
- **But this includes 2 AM - 6 AM when zero calls arrived**

### The Explanation
Metrics calculated over **entire 24-hour period**, including hours when:
- Contact center closed
- No staff scheduled
- Zero call volume

**Example:**
```
Daily Service Level calculation:
- 8 AM - 6 PM (business hours): 400 calls, 85% in threshold
- 6 PM - 8 AM (after hours): 0 calls, 0% calculated as 0/0 = N/A or 100%

Overall SL = Weighted average appears artificially high
```

### Why This Happens
Empty intervals (no calls) can be treated as 100% SL or excluded depending on calculation method.

### The Solution

**Filter to business hours:**
```
Analysis period: 8:00 AM - 6:00 PM Monday-Friday
Exclude: Nights, weekends (unless 24/7 operation)
```

**Segment by time period:**
- Peak hours (10 AM - 12 PM)
- Standard hours (8 AM - 6 PM)
- After hours (if applicable)

**Report meaningful intervals only:**
- Don't average across closed hours
- Focus on intervals with actual volume

**Genesys configuration:**
- Set default timezone in Analytics Workspace
- Use business hour filters for reports

---

## Pitfall 8: Proficiency vs. Performance Confusion

### The Problem
Queue using "Best Available Skills" evaluation:
- Agent A: 5-star proficiency, AHT = 15 minutes
- Agent B: 3-star proficiency, AHT = 8 minutes
- **Agent A gets most calls despite being slower**

### The Explanation
Proficiency ratings are **admin-set star ratings** (1-5 stars), not actual performance.

**Genesys routes by proficiency, not by outcomes:**
```
Agent A: Rated 5-star (admin judgment)
Agent B: Rated 3-star (admin judgment)

Best Available Skills = Route to highest proficiency
Result: Agent A gets preferential routing
```

**But actual performance might differ:**
- Agent A slower due to thoroughness (or inefficiency)
- Agent B faster due to efficiency (or experience)

### Why This Happens
Proficiency ratings are **static** (rarely updated) and **subjective** (based on admin judgment).

### The Solution

**Option 1: Use Predictive Routing**
- AI looks at **actual performance** (AHT, CSAT, outcomes)
- Ignores proficiency ratings
- Routes to agent likely to perform best on THIS call

**Option 2: Keep Proficiency Updated**
- Review proficiency ratings quarterly
- Base on actual performance data (AHT, quality scores, FCR)
- Don't inflate ratings for fairness

**Option 3: Use All Skills Matching**
- Ignores proficiency (treats all skilled agents equally)
- Routes by longest-idle (fairness)
- Accept that outcomes may vary

**Monitor both:**
- Proficiency ratings (what we think)
- Actual performance (what's real)
- Adjust ratings to match reality

---

## Pitfall 9: Percentage Change Misinterpretation

### The Problem
Dashboard shows:
- Yesterday Service Level: 70%
- Today Service Level: 75%
- **Change: +7%** (shown on dashboard)

Manager says: "Service level improved 7%"

### The Explanation
**Percentage-point change ≠ Percent change**

**Two ways to express change:**

1. **Percentage-point change (correct interpretation):**
   ```
   75% - 70% = +5 percentage points
   ```

2. **Relative percent change (misleading for percentages):**
   ```
   (75% - 70%) / 70% = +7.1% increase
   ```

**Genesys typically shows percentage-point change** (the correct method for metrics already in percentages).

### Why This Happens
Confusion between "percent" and "percentage points."

### The Solution

**Use precise language:**
- ❌ "Service level increased 5%"
- ✓ "Service level increased 5 percentage points (from 70% to 75%)"

**For relative change, use different base:**
- "Service level improved by 7% relative to yesterday's level"
- Clear that 7% is calculated from base of 70%

**Avoid ambiguity:**
- Always specify "percentage points" vs. "percent increase"

---

## Pitfall 10: Real-Time vs. Historical Data Mismatch

### The Problem
Looking at queue dashboard at 3:00 PM:
- Real-time view: 50 calls handled
- Historical view (today): 48 calls handled
- **"Why don't the numbers match?"**

### The Explanation
**Real-time data:**
- Updates within seconds
- Includes calls currently in progress
- May count calls before ACW complete

**Historical data:**
- Finalizes after interaction complete
- Only counts fully closed interactions
- May have 1-2 minute lag

**At 3:00 PM:**
- 2 calls are at ACW stage (not yet complete)
- Real-time counts them
- Historical will count them after ACW ends (3:01-3:02 PM)

### Why This Happens
Different data sources update at different rates.

### The Solution

**Understand lag:**
- Real-time: Immediate but may include in-progress
- Historical: 1-2 minute lag but accurate

**For current monitoring:**
- Use real-time views

**For reporting:**
- Use historical data (wait until interval complete)

**Don't compare across data sources:**
- Real-time ≠ Historical (by design)
- Both are correct for their purpose

---

## Prevention Checklist

Before analyzing Genesys reports, verify:

- [ ] **Date ranges consistent** across all exports
- [ ] **Filters applied** (inbound only, handle >=20 sec, etc.)
- [ ] **Department filter** applied for agent metrics
- [ ] **Timezone** set correctly
- [ ] **Metric definitions** understood (ASA vs. AWT)
- [ ] **Short abandon threshold** configured
- [ ] **Business hours** filter applied (exclude closed hours)
- [ ] **Multiple metrics** analyzed together (not single metric isolation)
- [ ] **Interval effects** understood (offered ≠ handled)
- [ ] **Transfer impact** acknowledged (double-counting)

---

## Quick Reference: What to Trust

| Metric | Trust Level | Notes |
|--------|-------------|-------|
| Daily Offered = Daily Handled | ✓ High | Should reconcile over 24 hours |
| Interval Offered = Interval Handled | ✗ Low | Carryover normal |
| ASA alone | ✗ Low | Must pair with abandon rate |
| ASA + AWT + Abandons | ✓ High | Complete picture |
| Summed Offered across queues | ✗ Low | Includes transfers (double-count) |
| Unique conversation IDs | ✓ High | True unique call count |
| Short-abandon-inclusive rate | ✗ Low | Includes wrong numbers |
| Long-abandon-only rate (>60s) | ✓ High | Meaningful abandons |
| Occupancy >95% | ⚠ Warning | Burnout risk |
| Utilization 55-65% | ✓ Healthy | Normal with breaks |

---

## Reference

**Source:** Genesys Cloud Reporting and Analytics - Data Attribution and Timing sections

**Key principles:**
1. Understand when metrics are counted (offer vs. answer vs. complete)
2. Always analyze multiple metrics together
3. Validate filters and thresholds before reporting
4. Account for interval carryover in short-period reports
5. Use daily/weekly aggregates for accurate totals

**Related:**
- Metric Definitions
- Interval Attribution
- Service Level Configuration
- Callback Reporting

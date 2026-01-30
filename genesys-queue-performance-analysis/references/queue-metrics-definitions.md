# Queue Metrics Definitions
**Source:** Genesys Cloud Resource Center - Metric Definitions

Complete reference for all Genesys Cloud queue performance metrics.

---

## Core Metrics

### Offered
**Definition:** The number of interactions routed into a queue for agents to answer.

**What counts:**
- Every incoming call (or callback) when it enters the queue
- One of three outcomes: answered, abandoned, or flowed out

**Formula:**
```
Offered = Answered + Abandoned + Flow-outs
```

**Use cases:**
- Volume tracking
- Forecast validation (compare to predicted volume)
- Capacity planning

**Notes:**
- Offered interactions may span multiple queues if transferred
- Each queue counts the interaction as "offered" when it arrives
- Summing "offered" across queues can double-count transferred calls

---

### Answered
**Definition:** The count of interactions an agent actually answered (customer connected to agent).

**What counts:**
- Moment agent picks up the call
- Each offered call that connects with an agent increments this metric

**Formula:**
```
Answer Rate (%) = (Answered ÷ Offered) × 100
```

**Use cases:**
- Primary productivity metric
- Service level calculation (numerator)
- Agent workload measurement

**Notes:**
- Answered count increments at **moment of answer**
- "Handled" count increments at **completion** (may be different interval)
- For long calls spanning intervals, answered vs. handled may differ

---

### Abandoned
**Definition:** Count of interactions where customer hung up or disconnected before reaching agent.

**What counts:**
- Customer hangs up while in queue
- Customer does NOT request callback (callbacks = flow-outs, not abandons)

**What does NOT count:**
- Callback requests (counted as flow-outs)
- System disconnects or errors

**Formula:**
```
Abandon Rate (%) = (Abandoned ÷ Offered) × 100
```

**Configuration options:**
- Short Abandon Threshold: Define minimum queue time to count (e.g., 10, 30, 60 seconds)
- Include/exclude short abandons from Service Level calculation

**Related metrics:**
- **Average Abandon Time:** Average duration customers waited before abandoning
- **Total Abandon Time:** Sum of waiting time accrued by all abandons
- **Abandon Intervals:** Distribution of abandons by time bucket (0-30s, 30-60s, etc.)

**Use cases:**
- Customer experience indicator
- Staffing adequacy assessment
- Identify when customers lose patience

**Typical targets:**
- Standard: <5%
- High-touch service: <3%
- Self-service/overflow: <10%

---

### Average Wait Time (AWT)
**Definition:** Average time an interaction spends in queue waiting for an answer.

**What counts:**
- ALL interactions (answered, abandoned, flowed-out)
- Duration from queue entry until:
  - Agent answers (for answered calls)
  - Customer abandons (for abandoned calls)
  - Interaction flows out (for callbacks/transfers)

**Formula:**
```
AWT = Total Queue Time ÷ Total Interactions
```
(where Total Interactions = Offered)

**Use cases:**
- Overall queue delay measurement
- Customer experience metric
- More comprehensive than ASA (includes abandons)

**ISPN Standard:**
- Report in seconds
- Target: <90 seconds

**Notes:**
- AWT is typically HIGHER than ASA
- AWT includes long-wait abandons that ASA excludes
- Use AWT for true customer wait experience

---

### Average Speed of Answer (ASA)
**Definition:** Average wait time for interactions that were **answered** by agents.

**What counts:**
- Only interactions that reached an agent
- Queue time from entry to agent answer

**What does NOT count:**
- Abandoned calls
- Flow-outs (callbacks, transfers)

**Formula:**
```
ASA = Total Answer Wait Time ÷ Number of Answered Interactions
```

**Use cases:**
- Service level goal setting
- Customer satisfaction predictor (for answered calls)
- Staffing efficiency metric

**ISPN Standard:**
- Report in seconds
- Target: Varies by queue (typically <60 seconds)

**CRITICAL WARNING:**
ASA can be misleadingly low if abandon rate is high. Always analyze together:
- ASA = 15 seconds (looks great)
- Abandon Rate = 20% (terrible)
- Interpretation: Only fast-answered calls counted; many hung up after 2+ minutes

**Best practice:** Report ASA + Abandon Rate + AWT together for complete picture

---

### Service Level (SL)
**Definition:** Percentage of interactions answered within a defined threshold time.

**Common thresholds:**
- 80/20: 80% answered in 20 seconds
- 80/30: 80% answered in 30 seconds
- 80/60: 80% answered in 60 seconds
- 80/90: 80% answered in 90 seconds
- 80/120: 80% answered in 120 seconds

**Formula:**
```
Service Level % = (Answered Within Threshold ÷ Total Conversations) × 100
```

**Configuration options** (affects denominator):

1. **Include Abandons:** Counts abandoned calls in total conversations
   - ON: SL% typically lower (abandons count as "not answered in threshold")
   - OFF: SL% higher (abandons excluded from calculation)

2. **Include Short Abandons:** Counts quick hang-ups (<threshold)
   - ON: Even <10 sec hang-ups count against SL
   - OFF: Short abandons excluded (common for wrong numbers)

3. **Include Flow-outs:** Counts callbacks, transfers that exit queue
   - ON: Flow-outs included in denominator
   - OFF: Flow-outs excluded (common setting)

**ISPN Configuration:**
- Threshold: Varies by queue (typically 30-120 seconds)
- Include Abandons: NO (excluded)
- Include Short Abandons: NO (exclude <60 seconds)
- Include Flow-outs: NO (excluded)

**Formula with ISPN settings:**
```
Service Level % = (Answered Within Threshold ÷ Answered Interactions) × 100
```

**Use cases:**
- Primary operational target
- SLA compliance measurement
- Staffing adequacy indicator
- Real-time performance monitoring

**Typical targets:**
- Industry standard: 80% (within threshold)
- High-touch service: 85-90%
- Overflow queues: 70%

**Notes:**
- Genesys recalculates historical SL if settings change
- Target threshold only affects data going forward
- SL can look artificially high if abandons excluded
- Use with abandon rate for true performance picture

---

### Average Handle Time (AHT)
**Definition:** Total time to process an interaction from answer to completion.

**Components:**
```
AHT = Talk Time + Hold Time + After-Call Work (ACW)
```

For outbound calls:
```
AHT = Talk Time + Hold Time + ACW + Dial Time + Ring Time
```

**Formula:**
```
AHT = Sum of (Talk + Hold + ACW + Dial) ÷ Number of Handled Interactions
```

**Use cases:**
- Capacity planning (determines calls per hour per agent)
- Efficiency measurement
- Forecasting input
- Training needs identification

**Component breakdown:**

1. **Talk Time:** Time agent spends speaking with (or listening to) customer
   - High = complex calls or chatty agents
   - Low = efficient or rushed

2. **Hold Time:** Time customer is on hold while agent researches
   - High = knowledge gaps, system issues, consultations
   - Low = well-trained agents or simple calls

3. **After-Call Work (ACW):** Time spent on wrap-up after call ends
   - High = complex data entry, CRM updates, or inefficient processes
   - Low = efficient systems or skipped work

**ISPN Standard:**
- Report in minutes
- Target: <10.7 minutes (varies by queue/skill)
- Include only: Inbound, not abandoned, handle time >= 20 seconds

**Impact on capacity:**
```
Calls per Hour per Agent = 60 ÷ AHT (in minutes)
```

Example:
- AHT = 6 minutes → 10 calls/hour/agent
- AHT = 12 minutes → 5 calls/hour/agent

**Notes:**
- AHT varies by call type (simple vs. complex)
- Compare to forecast; if higher = need more agents
- Break down by component to identify root cause
- High AHT isn't always bad (quality vs. speed trade-off)

---

### Handle Count
**Definition:** Total number of interactions handled (answered and completed) by queue.

**What counts:**
- Interactions answered by agent AND fully completed (including ACW)

**When counted:**
- In the interval when interaction **concludes**
- NOT when it was offered or answered

**Formula:**
```
Handle Count = Count of Completed Interactions
```

**Difference from Answered:**
- Answered: Increments when agent picks up
- Handled: Increments when call fully completes (after ACW)

**Use cases:**
- Agent productivity measurement
- Queue throughput tracking
- Completed work volume

**Notes:**
- For long calls spanning intervals, handled count appears in later interval
- Daily totals: Offered ≈ Handled (over full day, they reconcile)
- Interval reports: Offered ≠ Handled (due to carryover)

---

### Occupancy
**Definition:** Percentage of on-queue time spent actively handling contacts.

**Formula:**
```
Occupancy = (Interacting Time ÷ On-Queue Time) × 100
```

Where:
- **Interacting Time:** Talk + Hold + ACW
- **On-Queue Time:** Time agent is available + interacting

**ISPN Standard:**
- Target: >75%

**Interpretation:**
- **High (>95%):** Agents back-to-back, no breathing room, burnout risk
- **Healthy (75-85%):** Balanced workload, sustainable
- **Low (<60%):** Agents idle frequently, possible overstaffing

**Use cases:**
- Efficiency measurement
- Staffing optimization
- Agent well-being monitoring
- Capacity planning

**Notes:**
- High occupancy isn't always good (quality suffers, agent stress)
- Low occupancy isn't always bad (could be training time, projects)
- Compare to forecast: actual vs. predicted occupancy
- Industry best practice: 80-85% for voice

---

### Flow-outs
**Definition:** Interactions that exit queue without agent handling and without customer abandoning.

**What counts:**
- Callbacks requested by customer
- IVR transfers to another queue
- Overflow to voicemail
- In-queue flow routing to different destination

**What does NOT count:**
- Agent transfers (those are handled interactions that transfer)
- Abandoned calls (customer hung up)

**Use cases:**
- Callback volume tracking
- Understanding queue exits
- Service level calculation (if included in denominator)

**Configuration:**
- Can be included or excluded from SL calculation
- Typically excluded from abandon count

**ISPN Standard:**
- Track separately as callback volume
- Exclude from SL calculation
- Monitor to ensure callbacks eventually connect

**Notes:**
- Flow-out is NOT a failure (customer chose alternate path)
- High flow-outs could indicate heavy callback usage
- Ensure callbacks tracked to completion

---

## Agent-Level Metrics (Queue Context)

### Agent Interactions Handled
**Definition:** Number of interactions an agent answered and processed (completed).

**What counts:**
- Both ACD (routed by queues) and non-ACD interactions
- Increments when interaction fully completed (including ACW)

**Use cases:**
- Individual productivity measurement
- Workload comparison across agents
- Capacity planning

---

### Agent AHT
**Definition:** Agent's average handle time across all interactions.

**Formula:**
```
Agent AHT = Sum of (Talk + Hold + ACW + Dial) ÷ Agent's Handled Count
```

**Use cases:**
- Efficiency comparison between agents
- Training needs identification
- Coaching opportunities

---

### Agent Occupancy
**Definition:** Percentage of agent's on-queue time spent handling interactions.

**Formula:**
```
Agent Occupancy = (Agent Interacting Time ÷ Agent On-Queue Time) × 100
```

**Use cases:**
- Workload distribution assessment
- Identify overworked or underutilized agents
- Schedule optimization

---

## Time-Based Metrics

### Total Talk Time
Sum of all talk time across interactions.

### Total Hold Time
Sum of all hold time across interactions.

### Total ACW Time
Sum of all after-call work time across interactions.

### Total Answer Time
Sum of all queue wait times for answered calls (used to calculate ASA).

---

## Workforce Metrics

### On-Queue Time
**Definition:** Total time agents were logged in and available to take ACD interactions.

**Components:**
- Idle time (waiting for calls)
- Interacting time (on calls)

**Use cases:**
- Capacity measurement
- Schedule adherence validation
- Occupancy calculation denominator

---

### Off-Queue Time
**Definition:** Time agents were logged in but NOT accepting ACD interactions.

**What counts:**
- After-call work done offline
- Break, meal, meeting, training statuses
- Other non-productive activities

**Use cases:**
- Shrinkage calculation
- Schedule compliance
- Utilization measurement

---

## Advanced Metrics

### Transfer Rate
**Definition:** Percentage of interactions that were transferred by agent.

**Formula:**
```
Transfer Rate = (Number of Transfers ÷ Total Answered) × 100
```

**Use cases:**
- First-call resolution proxy
- Routing accuracy assessment
- Training needs identification

**Typical targets:**
- Standard: <15%
- Specialized queues: <10%
- Tiered support: Varies by tier

---

### Agent Score (Idle Time)
**Internal Genesys metric** used for routing decisions.

**Factors:**
- Time since last interaction completed
- Time since went on queue (whichever more recent)
- Capped at 7 days (8+ days treated same as 7 days)

**Use cases:**
- Fair distribution of calls
- Longest-idle-first routing
- Used as tie-breaker in skill-based routing

---

## Calculation Notes

### Interval Attribution
Genesys assigns metrics to intervals based on when interactions **complete**, not when they start.

**Key principle:**
- Offered: Counted when call enters queue
- Answered: Counted when agent picks up
- Handled: Counted when call fully completes (after ACW)
- Talk/Hold/ACW times: Attributed to completion interval

**Implication:**
A 45-minute call starting at 2:00 PM will show:
- Offered: 2:00-2:30 PM interval
- Handled: 2:30-3:00 PM interval (when it completes)

### Data Latency
- **Real-time data:** Updates within seconds
- **Historical aggregates:** Available immediately after interval closes
- **Speech analytics:** Can take up to 72 hours
- **Custom attributes:** Depends on data source

---

## Metric Relationships

### Key Relationships:
```
Offered = Answered + Abandoned + Flow-outs

Answered = Handled (over daily aggregates)

Service Level = f(ASA, Staffing, Volume, AHT)

Occupancy = f(AHT, Call Volume, Staffing)

Capacity = (On-Queue Hours × 60) ÷ AHT
```

---

## Best Practices

1. **Never evaluate a single metric in isolation**
   - ASA + Abandon Rate + AWT = complete wait picture
   - SL + Occupancy = efficiency picture

2. **Use daily/weekly aggregates for accuracy**
   - Interval reports have carryover effects
   - Daily totals reconcile offered/handled discrepancies

3. **Understand configuration impact**
   - SL calculation varies based on inclusion settings
   - Short abandon threshold affects abandon count

4. **Validate data quality**
   - Check: Offered = Answered + Abandoned + Flow-outs
   - Investigate if equation doesn't balance

5. **Consider call complexity**
   - Normalize AHT by queue type
   - Technical support naturally higher than password resets

---

## Reference

**Source:** Genesys Cloud Resource Center - Metric Definitions
https://help.mypurecloud.com/articles/metric-definitions/

**Related:**
- Workforce Management Metric Definitions
- Service Level Calculation
- Real-time vs Historical Metrics

# Routing Impact Analysis
**Source:** Genesys Cloud Skills-Based Routing Deep Dive

How routing configuration affects queue performance and troubleshooting guide.

---

## Routing Methods Overview

Genesys Cloud supports three primary routing methods that directly impact queue performance:

### 1. Standard Routing
**How it works:**
- All available agents in queue are candidates
- Evaluation method determines selection

**Performance characteristics:**
- Simple, predictable
- No skill relaxation
- Best for homogeneous agent pools

**Use when:**
- All agents have same skills
- No tiered service levels
- Simplicity preferred over optimization

---

### 2. Bullseye Routing
**How it works:**
- Up to 5 configurable "rings" that expand over time
- Each ring has a delay timer
- Two strategies:
  - **Option 1:** Different agent groups per ring (same skills)
  - **Option 2:** Skill relaxation (drop skills in outer rings)

**Performance characteristics:**
- Balances skill matching with wait time
- Prevents indefinite waits for perfect match
- Can improve service level when skill coverage is thin

**Option 1: Agent Group Rings**
```
Ring 1 (0-20s):  Expert team (all have required skills)
Ring 2 (20-40s): General team (all have required skills)
Ring 3 (40-60s): Backup team (all have required skills)
```

**Use when:**
- Want to prioritize experts before generalists
- All agents have required skills, but prefer certain agents first

**Option 2: Skill Relaxation Rings**
```
Ring 1 (0-30s):  Require Skill A + Skill B
Ring 2 (30-60s): Require Skill A only (drop Skill B)
Ring 3 (60-90s): No skill requirements (anyone can answer)
```

**Use when:**
- Perfect match availability is limited
- Willing to trade skill match for reduced wait time
- Skill is "preferred" not "mandatory"

---

### 3. Predictive Routing
**How it works:**
- AI ranks agents based on predicted outcome (AHT, CSAT, etc.)
- Skills still enforced (unless skill matching disabled)
- Ignores proficiency ratings (uses actual performance history)

**Performance characteristics:**
- Optimizes chosen KPI (e.g., minimize AHT)
- May route to less-idle agent if AI predicts better outcome
- Requires historical data (90 days)

**Use when:**
- Have sufficient historical data
- Want to optimize specific KPI
- Willing to accept AI-driven decisions

---

## Evaluation Methods

Evaluation method determines HOW Genesys selects an agent from qualified candidates.

### 1. All Skills Matching
**How it works:**
- Selects agent who has all required skills
- Ignores proficiency ratings (all skilled agents treated equally)
- Tie-breaker: Longest idle time

**Formula:**
```
If Agent.hasAllSkills(requiredSkills):
    Select longest_idle_agent
```

**Impact on performance:**
- Fair distribution of calls across skilled agents
- No preference for expertise
- Simple, predictable routing

**Use when:**
- Want even workload distribution
- Proficiency levels not meaningful
- Agents have binary skill (either can or can't)

---

### 2. Best Available Skills
**How it works:**
- Calculates average proficiency across required skills per agent
- Routes to highest-proficiency agent
- Tie-breaker: Longest idle time

**Formula:**
```
For each agent with all required skills:
    Average_Proficiency = Sum(skill_ratings) ÷ Number_of_required_skills
    
Route to agent with highest Average_Proficiency
If tie: Route to longest_idle among tied agents
```

**Limitation:**
- Only searches top 100 longest-idle agents (for performance)

**Impact on performance:**
- Routes complex calls to experts
- Experts may get overloaded
- Potentially better outcomes (lower AHT, higher FCR)

**Use when:**
- Proficiency levels are meaningful (1-star vs. 5-star matters)
- Want to leverage expertise for optimal outcomes
- Willing to accept uneven workload distribution

---

### 3. Disregard Skills
**How it works:**
- Ignores skills altogether
- Routes to longest-idle agent regardless of skills

**Impact on performance:**
- Maximum agent utilization
- Risk of misrouted calls (unskilled agents)
- Equivalent to non-skilled routing

**Use when:**
- Backup/overflow scenarios only
- Skill requirements truly don't matter
- Emergency high-volume situations

**WARNING:** Rarely appropriate for normal operations

---

## Skill Matching Impact on Queue Performance

### Scenario 1: No Skill Mismatch
**Configuration:**
- Queue requires Skill X
- 10 agents on queue, all have Skill X
- Standard routing, All Skills evaluation

**Result:**
- All 10 agents eligible for calls
- Calls distributed evenly by longest-idle
- Optimal utilization

**Performance characteristics:**
- Low ASA (agents readily available)
- High service level
- High occupancy (all agents productive)

---

### Scenario 2: Skill Mismatch (Insufficient Coverage)
**Configuration:**
- Queue requires Skill X + Skill Y
- 10 agents on queue:
  - 3 have Skill X + Skill Y
  - 7 have Skill X only

**Result:**
- Only 3 agents eligible for calls
- 7 agents idle despite calls waiting
- Bottleneck at skilled agents

**Performance characteristics:**
- High ASA (calls wait for 3 agents)
- Low service level
- Uneven occupancy (3 agents overworked, 7 idle)

**Symptoms:**
- Calls waiting in queue
- Agents idle
- Customer complaints about wait times

**Solutions:**
1. Assign Skill Y to more agents (training)
2. Use bullseye to relax Skill Y requirement after 30s
3. Use separate queue for Skill X-only calls

---

### Scenario 3: Language Mismatch
**Configuration:**
- Queue requires Spanish language skill
- 10 agents on queue:
  - 2 have Spanish
  - 8 English only

**Result:**
- Only 2 agents can take Spanish calls
- Language is ALWAYS mandatory (never relaxes in bullseye)

**Performance characteristics:**
- Severe bottleneck for Spanish calls
- 8 agents underutilized if mostly Spanish volume
- High abandons for Spanish customers

**Symptoms:**
- Spanish calls wait >5 minutes
- English-only agents idle
- Spanish abandon rate >20%

**Solutions:**
1. Hire/train Spanish-speaking agents
2. Adjust schedules (ensure Spanish coverage during Spanish peak hours)
3. Consider separate Spanish queue with dedicated agents

**CRITICAL:** Language skills NEVER relax. If no Spanish agent available, call waits indefinitely (or abandons).

---

### Scenario 4: Over-Skilling
**Configuration:**
- Queue requires 5 different skills (A, B, C, D, E)
- Only 2 agents have all 5 skills
- 20 agents have 3-4 of the skills

**Result:**
- Overly restrictive requirements
- Artificial bottleneck
- Most agents can't help

**Performance characteristics:**
- Poor service level
- High abandon rate
- Low overall agent utilization

**Symptoms:**
- Calls waiting unnecessarily
- Most agents idle
- Skilled agents overwhelmed

**Solutions:**
1. Simplify skill requirements (do you really need all 5?)
2. Use bullseye to relax some skills
3. Re-evaluate skill taxonomy (are some skills redundant?)

**Best practice:** Require only essential skills. Prefer fewer, meaningful skills over many granular ones.

---

## Bullseye Configuration Impact

### Conservative Bullseye (Slow Expansion)
**Configuration:**
```
Ring 1 (0-60s):  Require Skill A + Skill B
Ring 2 (60-120s): Require Skill A only
Ring 3 (120-180s): No skills
```

**Impact:**
- Long wait for perfect match
- High skill adherence
- Potentially high abandons if Ring 1 coverage thin

**Use when:**
- Skill match is critical (e.g., language, specialized technical)
- Willing to accept longer waits for quality
- Ring 1 coverage is adequate for 80%+ of volume

---

### Aggressive Bullseye (Fast Expansion)
**Configuration:**
```
Ring 1 (0-20s): Require Skill A + Skill B
Ring 2 (20-40s): Require Skill A only
Ring 3 (40-60s): No skills
```

**Impact:**
- Fast fallback to broader agent pool
- Lower skill adherence
- Better service level, potentially lower quality

**Use when:**
- Service level is priority over skill match
- Ring 1 coverage is insufficient
- Skills are "preferred" not "required"

---

### Balanced Bullseye (Recommended)
**Configuration:**
```
Ring 1 (0-30s): Require primary skill(s)
Ring 2 (30-60s): Relax secondary skill
Ring 3 (60-90s): Relax to minimal skills
```

**Impact:**
- Balances skill matching with wait time
- Most calls answered by skilled agents
- Safety valve for high-volume periods

**Design principles:**
1. Ring 1 should handle 70-80% of volume during normal operations
2. Ring 2 expands pool by 50-100% (drops less critical skills)
3. Ring 3 is last resort (minimal requirements)

---

## Proficiency Rating Impact

### With Best Available Skills Evaluation

**Scenario:**
- Queue requires "Technical Support" skill
- 5 agents on queue:
  - Agent A: 5-star proficiency
  - Agent B: 5-star proficiency  
  - Agent C: 3-star proficiency
  - Agent D: 3-star proficiency
  - Agent E: 1-star proficiency

**Routing behavior:**
1. Call arrives
2. System calculates average proficiency (only 1 skill required, so avg = rating)
3. Agents A and B both have highest (5-star)
4. Tie-breaker: Whichever of A or B has been idle longer gets call

**Result:**
- Expert agents (A, B) get disproportionate share
- May become bottleneck if volume high
- Newer agents (C, D, E) get fewer calls

**Performance impact:**
- Lower AHT (experts handle calls faster)
- But: Experts overworked, potential burnout
- And: Junior agents don't get training opportunities

---

### With All Skills Matching Evaluation

**Same scenario, different evaluation:**

**Routing behavior:**
1. Call arrives
2. All 5 agents have required skill (proficiency ignored)
3. Longest-idle agent selected regardless of rating

**Result:**
- Even distribution across all skilled agents
- All agents get equal call volume

**Performance impact:**
- Higher AHT (junior agents slower)
- But: Fair workload distribution
- And: Training through experience

---

## Troubleshooting Checklist

### Issue: High ASA Despite Available Agents

**Diagnosis steps:**

1. ✅ **Check skill requirements**
   ```
   Question: What skills does interaction require?
   Tool: Skills Performance view
   ```

2. ✅ **Check agent skill assignments**
   ```
   Question: Do available agents have required skills?
   Tool: Agent Performance > Filter by skill
   ```

3. ✅ **Check bullseye configuration**
   ```
   Question: Is bullseye expanding appropriately?
   Tool: Queue configuration > Routing method
   ```

4. ✅ **Validate skill names**
   ```
   Question: Are skill names spelled correctly? (case-sensitive)
   Tool: Architect flow review + Skills list
   ```

**Common root causes:**
- ❌ Skill mismatch (agents lack required skill)
- ❌ Bullseye not configured (calls stuck requiring skill no one has)
- ❌ Typo in skill name in Architect flow
- ❌ Language skill with no agents

---

### Issue: Calls Going to Wrong Agents

**Diagnosis steps:**

1. ✅ **Check evaluation method**
   ```
   Question: Is queue using "Disregard Skills"?
   Tool: Queue configuration > Evaluation method
   ```

2. ✅ **Check bullseye rings**
   ```
   Question: Are skills being dropped in outer rings?
   Tool: Queue configuration > Bullseye rings
   ```

3. ✅ **Check for conditional routing**
   ```
   Question: Is there Preferred Agent or Last Agent routing enabled?
   Tool: Queue configuration > Advanced settings
   ```

4. ✅ **Review interaction details**
   ```
   Question: What skills were actually attached to interaction?
   Tool: Interactions view > Specific conversation
   ```

**Common root causes:**
- ❌ Bullseye dropped required skill (by design or misconfigured)
- ❌ Evaluation method set to "Disregard Skills"
- ❌ Preferred Agent routing overriding normal selection
- ❌ Skills not properly attached in Architect flow

---

### Issue: Uneven Agent Workload

**Diagnosis steps:**

1. ✅ **Check evaluation method**
   ```
   Question: Is "Best Available Skills" causing expert bottleneck?
   Tool: Queue configuration > Evaluation method
   ```

2. ✅ **Check proficiency distribution**
   ```
   Question: Are all agents rated 5-star or only a few?
   Tool: Directory > Agent skills and proficiencies
   ```

3. ✅ **Check multiple queue membership**
   ```
   Question: Are some agents in more queues than others?
   Tool: Agent configuration > Queue memberships
   ```

4. ✅ **Review adherence**
   ```
   Question: Are some agents frequently off-queue?
   Tool: WFM adherence reports
   ```

**Common root causes:**
- ❌ Best Available Skills + few high-proficiency agents = bottleneck
- ❌ Some agents in multiple busy queues
- ❌ Poor adherence (some agents less available)
- ❌ Preferred Agent routing favoring certain agents

---

## Routing Performance Metrics

### Skill Match Rate (Custom Metric)
**Definition:** Percentage of interactions answered by agent with all originally-required skills.

**Calculation:**
```
Skill Match Rate = (Calls answered in Ring 1 ÷ Total Answered) × 100
```
(Assuming Ring 1 = full skill requirement)

**Target:** >80%

**Use to measure:**
- Bullseye effectiveness
- Skill coverage adequacy
- If often falling to Ring 2/3, need more skilled agents

---

### Average Ring at Answer
**Definition:** Which bullseye ring typically answers calls.

**Calculation:**
```
Average Ring = Σ(Ring_Number × Calls_in_Ring) ÷ Total_Answered
```

**Interpretation:**
- Avg Ring = 1.0 → All calls answered in Ring 1 (perfect)
- Avg Ring = 1.5 → Mix of Ring 1 and Ring 2
- Avg Ring = 2.5 → Often falling to Ring 3 (skill coverage problem)

---

## Best Practices

### 1. Start with Minimal Skill Requirements
- Only require skills that truly differentiate service
- Avoid "skill explosion" (hundreds of granular skills)
- Each additional skill exponentially reduces eligible agent pool

### 2. Use Bullseye for "Preferred" Skills
- Ring 1: Ideal match
- Ring 2-3: Acceptable alternatives
- Prevents indefinite waits for perfect match

### 3. Match Evaluation Method to Goals
- **Even distribution:** All Skills Matching
- **Optimize outcomes:** Best Available Skills
- **Emergency:** Disregard Skills (rare)

### 4. Monitor Skill Performance
- Track ASA by skill group
- Identify skill bottlenecks
- Adjust skill assignments or routing config

### 5. Language Skills Are Always Mandatory
- Never use language as "preferred" skill
- Always ensure adequate language coverage
- Schedule language-skilled agents during language peak hours

### 6. Validate Proficiency Ratings
- If using Best Available, ratings should be meaningful
- 5-star = expert, 1-star = trainee
- Don't inflate ratings for "fairness" (defeats purpose)

### 7. Test Routing Changes
- Use Genesys comparison tests for predictive routing
- Monitor metrics after bullseye changes
- Roll back if performance degrades

---

## Reference

**Source:** Genesys Cloud Skills-Based Routing Deep Dive
- Routing Methods: Standard, Bullseye, Predictive
- Evaluation Methods: All Skills, Best Available, Disregard
- Bullseye Configuration Options
- Skill Matching and Performance Impact

**Related:**
- Queue Configuration
- Agent Skill Management
- Skills Performance Reporting

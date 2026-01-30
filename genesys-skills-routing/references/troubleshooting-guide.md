# Troubleshooting Guide Reference

## Diagnostic Framework

When investigating skills-based routing issues, gather these data points:

1. **Interaction details**: Required skills, language, priority, timestamps
2. **Agent state**: On Queue status, queue membership, assigned skills
3. **Queue config**: Routing method, evaluation method, bullseye rings
4. **Flow logic**: Transfer to ACD settings, Set Skills actions

## Common Scenarios and Solutions

### Scenario: Interaction Waiting Despite Idle Agents

**Symptoms:**
- Calls sitting in queue
- Agents showing available in real-time dashboard
- Long wait times for specific interaction types

**Diagnostic Steps:**

1. **Check skill match**
   - What skills are on the waiting interaction?
   - Do idle agents have ALL those skills?
   - Is a language skill required that agents lack?

2. **Verify queue membership**
   - Are skilled agents members of this queue?
   - Is queue activated for those agents?

3. **Check On Queue status**
   - Agents must be On Queue, not just logged in
   - Verify agents aren't in a non-ACD status

4. **Review bullseye config**
   - If using bullseye, has it expanded to their ring yet?
   - Are skilled agents in Ring 1 or outer rings?

**Solutions:**
- Add missing skills to agents
- Add agents to queue
- Adjust bullseye ring timing
- Consider skill relaxation if coverage insufficient

---

### Scenario: Wrong Agent Getting Calls

**Symptoms:**
- Calls going to less qualified agents
- Higher proficiency agents not receiving interactions
- Perceived unfair distribution

**Diagnostic Steps:**

1. **Check evaluation method**
   - All Skills: Proficiency ignored, longest idle wins
   - Best Available: Proficiency should matter
   - Disregard Skills: Skills ignored entirely

2. **Verify proficiency ratings**
   - Are ratings actually set (not all zeros)?
   - Are they differentiated meaningfully?

3. **Check for overriding features**
   - Preferred Agent routing enabled?
   - Last Agent routing enabled?
   - These override normal skill selection

4. **Review idle time calculation**
   - Agent may have been idle longest among qualified
   - 100-agent limit for Best Available search

**Solutions:**
- Change evaluation method to Best Available
- Set proficiency ratings appropriately
- Disable Preferred/Last Agent if not wanted
- Verify correct queue settings applied

---

### Scenario: Bullseye Bypassing Skills Too Quickly

**Symptoms:**
- Calls answered by unskilled agents
- Skill groups in reports show "None" frequently
- Quality issues from skill mismatch

**Diagnostic Steps:**

1. **Review ring timeouts**
   - How long before each ring expands?
   - Are timeouts appropriate for your SLA?

2. **Check skill relaxation config**
   - Which skills dropped at each ring?
   - Is critical skill dropped too early?

3. **Analyze ring answer distribution**
   - What percentage answered in Ring 1 vs later rings?
   - If most in outer rings, Ring 1 understaffed

4. **Verify staffing levels**
   - Do you have agents with required skills on shift?
   - Is Ring 1 always empty?

**Solutions:**
- Extend ring timeouts (give skilled agents more time)
- Reorder which skills relax first (drop least critical first)
- Add staffing for critical skills
- Train more agents in high-demand skills

---

### Scenario: Skill Not Being Applied to Interactions

**Symptoms:**
- Interactions arriving in queue without expected skills
- Skill Performance view shows "None" skill group
- Routing behaving like no skills configured

**Diagnostic Steps:**

1. **Audit Architect flow**
   - Is Transfer to ACD setting skills correctly?
   - Is Find Skill action finding the skill?
   - Is there a Set Skills clearing skills before transfer?

2. **Check skill name match**
   - Skills are case-sensitive
   - Verify exact spelling in flow vs admin config
   - Check for trailing spaces or special characters

3. **Review flow execution path**
   - Is the flow branch with skills being hit?
   - Use flow debug to trace execution

4. **Verify skill exists**
   - Skills must be created before use
   - Find Skill has "Not Found" path if missing

**Solutions:**
- Correct skill names in Architect flow
- Create missing skills in admin
- Fix flow logic to ensure skill assignment path executes
- Add error handling for Find Skill failures

---

### Scenario: Transferred Calls Waiting Unexpectedly

**Symptoms:**
- Warm or cold transfers sitting in new queue
- Original skill requirements blocking routing

**Diagnostic Steps:**

1. **Check if skills carried over**
   - Skills persist on transfer unless explicitly changed
   - New queue may lack agents with original skills

2. **Review transfer flow logic**
   - Does transfer flow use Set Skills to clear/change skills?
   - Is Transfer to ACD specifying new skills?

3. **Verify destination queue agents**
   - Do they have skills that were on original call?

**Solutions:**
- Add Set Skills action in transfer flow to adjust requirements
- Clear skills with empty list if general queue
- Train destination agents in relevant skills

---

### Scenario: Predictive Routing Not Optimizing as Expected

**Symptoms:**
- KPI not improving
- Routing seems random or unchanged
- Benefit analysis shows no improvement

**Diagnostic Steps:**

1. **Verify predictive is active**
   - Queue routing method set to Predictive?
   - License includes predictive routing?

2. **Check skill matching setting**
   - If ON and skill pool too narrow, limited optimization possible
   - If OFF, verify agents can handle interactions

3. **Review data volume**
   - Sufficient historical data for training?
   - Model needs volume to learn patterns

4. **Analyze factor weights**
   - Are expected attributes being used?
   - Unexpected factors might indicate data issues

**Solutions:**
- Run comparison test vs standard routing
- Adjust skill matching based on results
- Allow more time for model to learn
- Verify historical data quality

---

## Reporting-Based Diagnostics

### Using Skills Performance View

Key indicators to monitor:

| Metric | Warning Sign | Likely Cause |
|--------|-------------|--------------|
| High abandon rate for skill group | Understaffed for that skill | Add agents or relax skills |
| SLA missed for specific skills | Insufficient coverage | Adjust bullseye or staffing |
| "None" skill group has high volume | Skills not being tagged | Fix Architect flows |
| Handle time varies wildly by skill | Proficiency mismatch | Review skill assignments |

### Using Interactions View

Filter interactions by skill to investigate:
- Who handled calls with specific skills?
- What were outcomes for skill-tagged interactions?
- Were skills on interaction at answer vs at queue entry?

### Identifying Skill Relaxation

No direct "relaxation report" exists. Infer from:
- Skill group changes during interaction lifecycle
- Agent who answered lacks skills that were required
- Ring distribution data (if available via participant data)

**Workaround:** Add participant attribute in flow to track skill state:
- Set attribute when skills assigned
- Update attribute when skills relaxed
- Query attribute in interaction details

## Agent Skill Verification

Genesys Cloud UI doesn't provide "which agents have Skill X" view directly.

**Verification options:**
1. People admin view → Edit ACD Skills per agent
2. Performance views → Filter by skill, see which agents handled
3. Analytics API → Query agent profiles with skill filters
4. Directory export → List all users with skills

## Flow Debugging

For Architect flow troubleshooting:
1. Enable debug mode
2. Execute test call
3. Trace execution path
4. Verify skill assignment action executed
5. Check Find Skill results
6. Confirm Transfer to ACD parameters

## Escalation Checklist

Before escalating to Genesys support:

- [ ] Documented specific interaction IDs with issue
- [ ] Captured queue configuration screenshots
- [ ] Exported relevant Architect flow
- [ ] Verified agent skill assignments
- [ ] Checked recent configuration changes
- [ ] Reviewed Skills Performance data
- [ ] Tested with debug logging enabled

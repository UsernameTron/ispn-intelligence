# Routing Decision Logic Reference

## ACD Processing Flow

When an interaction enters a queue, Genesys Cloud's ACD follows this sequence:

### Agent Surplus Scenario (Agents Waiting)

1. **Build Candidate Pool**
   - Gather all agents who are On Queue and idle in the target queue
   - Standard routing: All available queue members considered
   - Bullseye routing: Only agents in current ring considered initially

2. **Apply Skill Filter**
   - Remove agents lacking ANY required skill
   - Remove agents lacking required language skill
   - Remaining pool = only fully qualified agents
   - If pool empty: interaction waits (or bullseye expands)

3. **Apply Evaluation Method**
   
   **All Skills Matching:**
   ```
   For each qualified agent:
     score = time_since_last_interaction
   Return agent with highest score (longest idle)
   ```

   **Best Available Skills:**
   ```
   Consider top 100 longest-idle qualified agents
   For each agent:
     avg_proficiency = average(proficiency for each required skill)
   Return agent with highest avg_proficiency
   Tie-breaker: longest idle wins
   ```

   **Disregard Skills:**
   ```
   For each On Queue agent (skill filtering skipped):
     score = time_since_last_interaction
   Return agent with highest score
   ```

4. **Assign and Alert**
   - Route interaction to selected agent
   - If agent fails to answer: select next best candidate

### Interaction Surplus Scenario (Calls Waiting)

When an agent becomes free:

1. **Gather Waiting Interactions**
   - All interactions queued for this agent's queue(s)

2. **Filter by Agent Qualification**
   - Only interactions where agent has all required skills
   - Only interactions where agent has required language

3. **Rank by Scoring Method**
   - **Conversation Score**: Based on wait time
   - **Priority Based**: Interaction priority + wait time

4. **Deliver Highest-Ranked Interaction**

## Time Since Last Interaction Scoring

Genesys Cloud uses idle time as primary fairness mechanism:

- Timer starts when agent completes interaction OR goes On Queue
- Longer idle = higher score = higher priority for next interaction
- **7-day cap**: Time beyond 7 days doesn't increase score further
- Prevents agents returning from leave from getting all calls at once

## Bullseye Ring Processing

### Ring Expansion Logic

```
Ring 1: t=0 to timeout_1
  - Only Ring 1 agents/skills considered
  - If answered: done
  - If timeout: expand to Ring 2

Ring 2: timeout_1 to timeout_2
  - Ring 1 + Ring 2 agents/skills now eligible
  - Ring 1 agent still preferred if they free up
  - If answered: done
  - If timeout: expand to Ring 3

[Continue through all configured rings]
```

### Ring Priority Behavior

If a Ring 1 agent becomes available while alerting Ring 2 agent:
- Ring 1 agent gets priority
- Interaction may be reassigned mid-alert

### Skill Relaxation Mechanics

When ring relaxes a skill:
- Skill stays tagged on interaction (for reporting)
- ACD evaluation ignores that skill for eligibility
- Agents without that skill become candidates
- All other skill requirements still enforced

## Language Skill Special Handling

Language skills receive strict enforcement:

1. **Never relaxed automatically** - Must be explicitly removed via flow or bullseye
2. **Evaluated separately** from other skills in routing logic
3. **Always mandatory** - No "preferred language" concept natively
4. **Communication requirement** - System assumes agent must speak to customer

To implement "preferred language" pattern:
- Ring 1: Require language skill
- Ring 2+: Use Set Skills to remove language requirement
- Requires accepting customer may get agent who doesn't speak their language

## Conditional Group Routing

Advanced routing option layering additional logic:

- Multiple groups can be defined with conditions
- Groups evaluated in order
- First matching group receives interaction
- Can include KPI guardrails (service level thresholds)
- More complex to troubleshoot—use sparingly

## Manual Assignment

Supervisors can bypass ACD:
- Assign waiting interaction directly to specific agent
- Agent must be member of queue
- Skill requirements may be overridden
- Use for: Escalations, special handling, emergency coverage

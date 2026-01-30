---
name: genesys-skills-routing
description: Expert guidance for Genesys Cloud skills-based routing configuration, optimization, and troubleshooting. Use when configuring ACD skills, queue routing methods, bullseye rings, predictive routing, Architect flow skill actions, proficiency ratings, skill relaxation strategies, or analyzing skills performance metrics. Triggers on "Genesys routing", "ACD skills", "bullseye configuration", "skill matching", "queue evaluation method", "predictive routing skills", "skill relaxation".
---

# Genesys Cloud Skills-Based Routing Expert

Comprehensive guidance for configuring, optimizing, and troubleshooting skills-based routing in Genesys Cloud contact center environments.

## Core Concepts

### Skill Categories
- **Language Skills**: Strictly enforced—agents without requested language are never eligible regardless of other skills
- **General Skills**: Attributes like "Warranty", "Windows OS", "Billing" assigned to agents
- **Proficiency Ratings**: 0-5 stars indicating expertise level (only used by Best Available Skills evaluation)

### Key Limits
| Resource | Limit | Notes |
|----------|-------|-------|
| Skills per org | 2,000 (default, can increase) | Request increase if needed |
| Skills per agent | 500 maximum | Keep focused on actual capabilities |
| Find Skill actions per flow | 25 unique lookups | Rarely a constraint |
| Bullseye rings | 5 per queue | Each with configurable timeout |

## Queue Routing Configuration

### Evaluation Methods

**All Skills Matching** (Default)
- Ignores proficiency ratings entirely
- Selects longest-idle agent among those with all required skills
- Use for: Fair distribution, training environments

**Best Available Skills**
- Calculates average proficiency across required skills per agent
- Highest average wins; ties broken by longest idle
- Limited to top 100 longest-idle agents for performance
- Use for: Prioritizing experts, complex skill scenarios

**Disregard Skills**
- Ignores skills completely, routes to longest-idle agent
- Use with caution: Can route to unqualified agents
- Use for: Overflow, backup scenarios only

### Routing Methods

**Standard**: Direct skill filtering + evaluation method

**Bullseye**: Progressive ring expansion with two strategies:
1. **Agent Rings** (same skills): Prioritize specific agent groups, expand over time
2. **Skill Relaxation**: Drop skill requirements progressively to expand pool

## Architect Flow Actions

### Transfer to ACD
Primary action for skill-based routing. Specify:
- Target queue
- Required skills (all are mandatory by default)
- Language skill
- Priority

```
Transfer to ACD → Queue: Support | Skills: [Billing, Technical] | Language: Spanish
```

### Set Skills (In-Queue Flow)
Dynamically adjust skill requirements while call waits:
- Replace current skills with new set
- Empty list removes all skill requirements
- Can change or remove language requirement

### Find Skill / Find Language Skill
Runtime skill lookup by name for dynamic routing:
- Store result in variable
- Use in subsequent Transfer to ACD
- Handle "Not Found" path for missing skills

## Bullseye Configuration

### Skill Relaxation Pattern
```
Ring 1 (0-30s):   Require Skill A + Skill B + Skill C
Ring 2 (30-60s):  Drop Skill C → Require A + B only
Ring 3 (60-90s):  Drop Skill B → Require A only
Ring 4 (90-120s): Drop all skills → Any qualified agent
Ring 5 (120s+):   Overflow or callback
```

### Best Practice Timing
- Start with full requirements for 20-30 seconds minimum
- Each ring expansion: 15-30 seconds typical
- Monitor which ring answers most calls—adjust accordingly
- If Ring 1 rarely answers, staffing or skill design needs attention

## Predictive Routing with Skills

### Skill Matching Setting

**ON (Default/Recommended)**
- AI constrained to agents with required skills
- Proficiency ratings NOT used by AI model
- AI ranks by actual performance history instead

**OFF (Use Cautiously)**
- AI can route to agents lacking skill tags
- Increases candidate pool for optimization
- Risk: May bypass formally required skills

### How AI Uses Skills
- Binary filter: has skill or doesn't (when matching ON)
- Performance history per skill type informs ranking
- Agent tenure, handle times, success rates weighted
- Weekly model retraining with 90-day data window

## Reporting and Monitoring

### Skills Performance View
Path: Performance > Workspace > Contact Center > Skills Performance

Metrics by skill group (unique skill combinations):
- Interaction volume
- Service levels
- Average handle time
- Abandonment rates
- Queue breakdown for each skill group

### Troubleshooting Checklist

**Call not routing:**
1. Verify agents On Queue AND members of target queue
2. Check skill names match exactly (case-sensitive)
3. Confirm agents have ALL required skills
4. Review language skill—always mandatory if set

**Wrong agent selected:**
1. Check evaluation method: All Skills ignores proficiency
2. Verify bullseye isn't dropping skills too early
3. Review Preferred Agent or Last Agent Routing settings
4. Confirm agent was actually idle longest among qualified

**Bullseye bypassing skills too fast:**
1. Extend ring timeouts
2. Review which skills are dropped at each ring
3. Check if Ring 1 has any eligible agents at all
4. Monitor ring answer distribution in reports

## Governance Best Practices

### Skill Taxonomy
- Establish naming conventions (prefix by department/type)
- Document each skill's purpose and assignment criteria
- Prevent duplicates: "TechSupport" vs "Technical Support"
- Remove unused skills quarterly

### Agent Skill Management
- Assign only skills agent can actually handle
- Update proficiency as agents develop
- Remove skills when agents change roles
- Cross-train strategically—don't over-skill everyone

### Common Pitfalls

| Pitfall | Impact | Solution |
|---------|--------|----------|
| Every agent has every skill | Skill routing becomes meaningless | Differentiate by actual capability |
| Too many skill combinations | Report complexity explodes | Simplify taxonomy |
| Proficiency all set to 5 | Best Available becomes All Skills | Use ratings meaningfully |
| Skills not cleared on transfer | Call waits in new queue | Use Set Skills in transfer flows |
| Language marked on non-language skill | Overly strict enforcement | Use Language category only for languages |

## Advanced References

For detailed information, see:
- [references/routing-decision-logic.md](references/routing-decision-logic.md) - Complete ACD processing flow
- [references/predictive-routing-details.md](references/predictive-routing-details.md) - AI model behavior and optimization
- [references/troubleshooting-guide.md](references/troubleshooting-guide.md) - Diagnostic scenarios and solutions

# Predictive Routing Details Reference

## How Predictive Routing Works

Predictive routing uses machine learning to optimize a chosen KPI by intelligently matching interactions with agents. Instead of longest-idle or proficiency ratings, an AI model ranks agents based on predicted outcomes.

## Supported KPIs

The model can optimize for:
- **Average Handle Time (AHT)** - Route to agents likely to resolve quickly
- **First Call Resolution (FCR)** - Route to agents likely to resolve on first contact
- **Customer Satisfaction (CSAT)** - Route to agents with highest predicted satisfaction
- **Transfer Rate** - Minimize likelihood of transfer
- **Custom metrics** - Depending on license and configuration

## Skill Matching Configuration

### Skill Matching ON (Default)

When enabled:
- Agent must have ALL required ACD skills to be considered
- Language skill always enforced regardless of setting
- Proficiency ratings (1-5 stars) are **NOT** used by the AI
- AI uses actual performance history instead of admin-set ratings

**Why proficiency is ignored:**
- AI already analyzes agent's historical outcomes
- Star ratings are subjective admin assessments
- Including ratings would unnecessarily narrow candidate pool
- Real performance is more predictive than assigned ratings

### Skill Matching OFF

When disabled:
- AI can consider agents lacking specific skill tags
- Increases candidate pool for optimization
- May improve KPI outcomes if high performers lack skill tags
- Risk: May route to technically unqualified agents

**Use cases for OFF:**
- Skills are soft preferences, not hard requirements
- Historical data shows skill tags don't correlate with outcomes
- Testing whether skill taxonomy needs revision

## Data Used by AI Model

### Agent Profile Data
- Assigned skills (binary: has/doesn't have)
- Certifications
- Tenure
- Team/group membership
- Working location

### Agent Performance Data
- Historical handle times by interaction type
- Resolution rates
- Customer feedback scores
- Transfer patterns
- After-call work duration

### Interaction Attributes
- Queue
- Required skills
- Priority
- Customer segment (if available)
- Prior interaction history

## Model Training and Updates

- Models retrain weekly
- Use up to 90 days of historical data
- Recent data weighted more heavily
- Adapts to agent skill development over time
- New agents get baseline predictions until sufficient data

## Predictive vs Standard Routing Comparison

| Aspect | Standard/Bullseye | Predictive |
|--------|-------------------|------------|
| Skill enforcement | All Skills or Best Available | Skill Matching ON/OFF |
| Proficiency use | Used by Best Available | Ignored |
| Agent ranking | Idle time + proficiency | AI predicted outcome |
| Fairness model | Longest idle wins ties | AI score determines |
| Adaptability | Static configuration | Learns from outcomes |
| Transparency | Rules-based, predictable | Model-based, analyzable |

## Fallback Behavior

If predictive routing interaction times out:
- Falls back to backup routing method (default: Standard ACD)
- Backup method uses its own evaluation rules
- Skills still enforced per backup configuration
- Configure backup to handle edge cases gracefully

## A/B Testing (Comparison Tests)

Genesys Cloud supports testing predictive against other methods:
- Split traffic between predictive and standard/bullseye
- Each method uses its own skill logic for its portion
- Compare KPI outcomes between groups
- Statistical significance calculated automatically

## Monitoring Predictive Routing

### Benefit Analysis
- Compares predicted vs actual outcomes
- Shows improvement over baseline
- Identifies which agent factors drive predictions

### Value Assessment
- Ongoing monitoring of KPI impact
- Alerts if benefit degrades
- Suggests configuration adjustments

### Factor Analysis
- View which attributes influenced model
- Example outputs: "Skill: French" and "Agent tenure" were strong predictors
- Helps validate model is using sensible signals

## Best Practices

1. **Start with Skill Matching ON** - Respect workforce planning assumptions
2. **Monitor factor analysis** - Ensure model aligns with expectations
3. **Test before full rollout** - Use comparison tests first
4. **Keep skills accurate** - Model only knows what's in profile data
5. **Allow sufficient data** - Predictive needs volume to learn effectively
6. **Review weekly** - Check benefit reports regularly
7. **Align with WFM** - Forecasting assumes certain agents handle certain skills

## Interaction with Bullseye

If using predictive with bullseye-like expansion:
- Configure via predictive routing queue settings
- Agent timeout can be set for fallback
- Not traditional ring-based expansion
- AI handles candidate pool management

## When Predictive May Not Help

- Very small agent pools (insufficient data)
- Homogeneous skill assignments (everyone handles everything)
- KPI not influenced by agent selection
- Extremely short interactions (little differentiation opportunity)
- Brand new contact center (no historical data)

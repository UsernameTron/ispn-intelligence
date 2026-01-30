---
name: ispn-sentiment-analysis
description: |
  Sentiment-driven customer experience intervention.
  TRIGGERS: "sentiment", "CSAT", "customer experience", "negative calls", "speech analytics"
  Part of ISPN Workforce Intelligence Suite
---

# ISPN Sentiment Analysis

## FILE IDENTIFICATION

| Pattern | Content |
|---------|---------|
| Speech_Analytics*.csv | Sentiment scores, call recordings analysis |
| Interactions*.csv | May include sentiment if Genesys SA enabled |

## TRIGGERS

```yaml
team_triggers:
  - Team negative sentiment > 15%
  - Sentiment score declining > -5 points/week
  - Sentiment-CSAT divergence (sentiment negative, CSAT high)
  - Specific call type with > 30% negative sentiment

agent_triggers:
  - Individual negative sentiment > 20%
  - Sentiment worsening during calls consistently
```

## THRESHOLDS

| KPI | GREEN | YELLOW | RED |
|-----|-------|--------|-----|
| Avg Sentiment Score | > +20 | 0 to +20 | < 0 |
| Positive % | > 60% | 50-60% | < 50% |
| Negative % | < 15% | 15-20% | > 20% |
| Sentiment Improving % | > 70% | 60-70% | < 60% |
| Sentiment Declining % | < 10% | 10-15% | > 15% |

## ROOT CAUSE CATEGORIES

| Root Cause | Indicator | Action |
|------------|-----------|--------|
| Issue-Driven | Frustrated by problem itself | Process/product improvement |
| Service-Driven | Frustrated by agent handling | Soft skills coaching |
| Wait-Driven | Frustrated by hold/queue time | Staffing adjustment |
| Resolution-Driven | Frustrated by outcome | Empowerment expansion |

## ANALYSIS PROTOCOL

1. **Signal Validation** - Sample size, SA accuracy verification
2. **Pattern Identification** - Time, agent, issue type, partner segmentation
3. **Root Cause Mapping** - Categorize top 3 drivers
4. **Intervention Design** - Actions, ownership, success metrics

## FORMULAS

```python
sentiment_score = weighted_average(values)  # -100 to +100
positive_pct = count(sentiment > +20) / total * 100
negative_pct = count(sentiment < -20) / total * 100
sentiment_trend = end_of_call - start_of_call  # improving/declining
```

## HANDOFFS

**Receives from:**
- ispn-skill-orchestrator: Query routing
- ispn-dpr-analysis: Interaction data correlation

**Sends to:**
- ispn-agent-coaching: Agents with negative patterns
- ispn-training-gap: Soft skills training needs

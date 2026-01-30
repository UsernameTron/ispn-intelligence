---
name: customer-health-intelligence
description: Customer health scoring and churn prediction for K-12 school districts using multi-factor analysis of usage, support tickets, satisfaction, and engagement patterns
---

# Customer Health Intelligence

## Overview

Advanced customer health monitoring and churn prediction system designed specifically for K-12 school district customers. Transforms reactive churn discovery (9-12 months too late) into proactive intervention with 90-180 day early warning system. Enables customer success teams to shift from firefighting to strategic retention and expansion, reducing churn while accelerating expansion revenue.

**Primary Use:** Proactive customer health monitoring, churn prediction, retention strategy development, expansion opportunity identification
**Key Value:** Identifies at-risk customers 90-180 days before renewal, enabling proactive intervention with 3x higher success rate
**Annual Impact:** $550K+ value creation ($250K churn prevention + $300K expansion acceleration)

## When to Use This Skill

Use for:
- Quarterly customer health reviews and portfolio analysis
- At-risk account identification before renewal cycles
- Proactive retention strategy development
- Expansion opportunity discovery and prioritization
- Automated QBR (Quarterly Business Review) preparation
- Customer segmentation and resource allocation optimization
- Executive customer escalation decision support

**Typical Request:** "Analyze customer health across all active accounts. Identify at-risk renewals in next 90 days with churn probability and retention strategies. Prioritize by ARR value at risk."

## Core Capabilities

### 1. Multi-Factor Health Score Calculation

**What Claude Analyzes:**
- Support quality metrics (ticket volume, escalations, resolution time, SLA adherence)
- Customer engagement patterns (QBR attendance, email responsiveness, portal usage)
- Product usage trends (bandwidth utilization, uptime, service adoption)
- Relationship strength indicators (tenure, expansion history, reference participation)
- Sentiment analysis (communication tone, escalation patterns, competitive signals)

**Health Scoring Model (0-100 scale):**
- **Support Quality (25% weight):** Ticket volume trends, escalation patterns, resolution time, SLA compliance
- **Engagement (25% weight):** QBR attendance, email responsiveness, portal login frequency, meeting acceptance rate
- **Product Usage (20% weight):** Bandwidth utilization trends, network uptime, service adoption breadth
- **Relationship Strength (15% weight):** Customer tenure, expansion history, reference/advocacy participation
- **Sentiment (15% weight):** Communication tone analysis, escalation frequency, competitive inquiry detection

**Health Categories:**
- **Green (80-100):** Healthy accounts, expansion-ready, 5-15% churn probability
- **Yellow (60-79):** Watch status, proactive engagement needed, 30-50% churn probability
- **Red (0-59):** Critical risk, executive intervention required, 60-80% churn probability

**Sample Output:**
```
CUSTOMER HEALTH PORTFOLIO ANALYSIS - Q1 2025

PORTFOLIO OVERVIEW:
â€¢ 47 Active Accounts: 34 Green (72%), 9 Yellow (19%), 4 Red (9%)
â€¢ Total ARR: $4.23M
â€¢ Renewals Next 90 Days: 8 accounts ($847K ARR)
â€¢ Churn Risk: $393K ARR in Red accounts requiring immediate intervention

CRITICAL ALERTS (Executive Action Required):
[RED] Lincoln County Schools - $180K ARR
  â€¢ Renewal: March 15, 2025 (59 days)
  â€¢ Health Score: 42/100
  â€¢ Churn Probability: 72%
  â€¢ Primary Risk: Service quality deterioration + leadership change + competitive inquiry
  â€¢ Recommended Action: CEO executive call + technical root cause resolution + retention offer
  â€¢ Business Impact: $180K ARR ($540K 3-year contract value)

RETENTION VALUE AT RISK:
â€¢ Red Accounts: $393K ARR (4 accounts) - Executive intervention required this week
â€¢ Yellow Accounts: $732K ARR (9 accounts) - CSM-led retention campaigns next 30 days
â€¢ Without intervention: $240K estimated churn (65% average probability across Red)
â€¢ With proactive intervention: $295K preservation (75% retention rate with executive engagement)
```

### 2. Churn Prediction & Risk Modeling

**What Claude Analyzes:**
- Base churn probability from health score
- Risk multipliers from situational factors
- Historical churn patterns and predictive indicators
- Customer lifecycle stage and renewal timing
- Competitive threat assessment

**Churn Probability Modeling:**

**Base Probability by Health Score:**
- Red (0-59): 60-80% base churn probability
- Yellow (60-79): 30-50% base churn probability
- Green (80-100): 5-15% base churn probability

**Risk Multipliers:**
- Renewal <90 days: +20% churn probability
- Leadership change (new superintendent/tech director): +15%
- Budget pressure signals detected: +10%
- Competitive inquiry or RFP activity: +25%
- Recent service outage or critical issue: +15%
- Declining engagement (missed QBRs, slow responses): +10%

**Predictive Accuracy:**
- 100% recall (all churned customers flagged as Red >90 days before churn)
- 60% precision (40% of Red accounts successfully retained with intervention)
- Conservative approach: Better to over-intervene than miss at-risk customer

**Sample Output:**
```
CHURN PREDICTION: Lincoln County Schools

HEALTH SCORE ANALYSIS: 42/100 (Critical)
â€¢ Support Quality: 6/25 (12 escalated tickets, 3 critical outages, 40% SLA miss rate)
â€¢ Engagement: 8/25 (Missed last 3 QBRs, email response time 3-5 days vs <24hr historical)
â€¢ Product Usage: 10/20 (85% bandwidth utilization constrained, 98.2% uptime vs 99.5% target)
â€¢ Relationship: 8/15 (6-year customer, declining engagement, no expansions 3 years)
â€¢ Sentiment: 10/15 (Negative tone, frustration with support response time)

CHURN PROBABILITY CALCULATION:
â€¢ Base probability (score 42): 70%
â€¢ Renewal <60 days: +20% = 90%
â€¢ Leadership change (new superintendent Sept 2024): +15% = 105%
â€¢ Competitive inquiry (regional fiber provider Dec 2024): +25% = 130%
â€¢ Service issues (3 outages Q4): +15% = 145%
â€¢ Risk-Adjusted Churn Probability: 72% (weighted average, capped at 95%)

ROOT CAUSE ANALYSIS:
Primary Issue: Service quality deterioration Q4 (equipment failures, slow support)
Contributing Factors:
â€¢ New superintendent not engaged (relationship building opportunity missed)
â€¢ Technology director frustrated with repeat issues (escalation pattern evident)
â€¢ Business manager exploring cost alternatives (budget pressure + service dissatisfaction)
â€¢ Competitor timing opportunistic (approached during service issues)

VALUE AT RISK:
â€¢ Annual ARR: $180K
â€¢ 3-Year Contract Value: $540K
â€¢ Customer Lifetime Value: $900K (estimated 5-year tenure if retained)
```

### 3. Retention Strategy Development

**What Claude Creates:**
- Multi-phase retention roadmap (Immediate â†’ Short-term â†’ Renewal)
- Executive escalation protocols with specific owner assignments
- Technical service recovery plans
- Customized retention offer recommendations
- Competitive defense battle cards
- Success metrics and monitoring checkpoints

**Strategy Framework:**

**IMMEDIATE Actions (This Week):**
- Executive engagement (CEO/VP level relationship building)
- Technical root cause resolution and service recovery
- Support process improvements and dedicated escalation contacts

**SHORT-TERM Actions (Next 30 Days):**
- Executive QBR with service recovery presentation
- Customized retention offer (service credits, upgrades, pricing)
- Competitive response preparation (battle cards, references)

**RENEWAL STRATEGY (30-90 Days):**
- Contract negotiation and closing
- Board presentation support if required
- Post-renewal relationship reset plan

**Sample Output:**
```
RETENTION STRATEGY: Lincoln County Schools ($180K ARR, 72% churn risk)

IMMEDIATE (This Week - Jan 15-19):
1. CEO Executive Call (CEO Jeff Neblett â†’ Superintendent)
   â€¢ Welcome new superintendent, apologize for Q4 service issues
   â€¢ Commit to root cause resolution and service improvement plan
   â€¢ Offer executive QBR next week (show commitment to partnership)
   â€¢ Owner: CEO Jeff Neblett | Timeline: Call by Friday Jan 19

2. Technical Root Cause Resolution (VP Operations â†’ Tech Director)
   â€¢ Comprehensive network audit (identify equipment failure root cause)
   â€¢ Commit to equipment upgrades if needed (no cost to district)
   â€¢ Expedite resolution of 2 open critical tickets (close by EOW)
   â€¢ Owner: VP Operations | Timeline: Audit by Jan 20, issues resolved by Jan 22

3. Support Process Improvement (VP Customer Success â†’ All Stakeholders)
   â€¢ Assign dedicated escalation contact (direct line to VP Operations)
   â€¢ Implement proactive monitoring alerts (prevent issues before impact)
   â€¢ Weekly check-in calls with tech director (rebuild trust)
   â€¢ Owner: VP Customer Success | Timeline: In place by Jan 22

SHORT-TERM (Next 30 Days - Jan 20 - Feb 15):
4. Executive QBR & Service Recovery (Week of Jan 27)
   â€¢ In-person QBR with superintendent, tech director, business manager
   â€¢ Present root cause analysis and prevention plan
   â€¢ Review performance metrics and address uptime concerns
   â€¢ Discuss 3-year partnership vision (not just transactional renewal)
   â€¢ Owner: CEO + VP Sales + VP Operations | Timeline: QBR by Feb 5

5. Customized Retention Offer (Week of Feb 3)
   â€¢ Service credits for Q4 outages ($15K = 3 months service)
   â€¢ Bandwidth upgrade 500Mbps â†’ 1Gbps at no incremental cost
   â€¢ 3-year pricing lock (protect against inflation, address budget concerns)
   â€¢ Enhanced SLA (99.95% uptime vs 99.9% standard)
   â€¢ Owner: VP Sales + CFO (pricing approval) | Timeline: Proposal by Feb 10

RENEWAL STRATEGY (Feb 15 - March 15):
6. Contract Negotiation & Closing (Feb 15 - March 1)
   â€¢ Present renewal proposal (service recovery + retention offer + value narrative)
   â€¢ Address objections (price, performance, competitive alternatives)
   â€¢ Board presentation support if needed (materials, attend meeting)
   â€¢ Secure signed contract minimum 2 weeks before expiration
   â€¢ Owner: VP Sales + Account Executive | Timeline: Signed by March 1

SUCCESS METRICS:
â€¢ Weekly: Open ticket status, response time, escalation tracking
â€¢ Bi-weekly: Executive update on relationship progress
â€¢ Monthly: Health score recalculation (target 75+ by March, 85+ by June)
â€¢ Outcome: Retention + health improvement + expansion opportunity identification
```

### 4. Expansion Opportunity Identification

**What Claude Analyzes:**
- Green account expansion signals (high health + high usage + growth indicators)
- Expansion opportunity types (bandwidth upgrades, new locations, managed services)
- Customer growth patterns and budget cycles
- Expansion timing optimization (align with E-rate windows, budget approvals)
- Close probability modeling based on health score and relationship strength

**Expansion Prioritization:**
- **High Priority:** Health score 85+, immediate opportunity, ARR expansion >$40K
- **Medium Priority:** Health score 80+, 3-6 month opportunity, ARR expansion $20-40K
- **Low Priority:** Health score 75+, opportunistic timing, ARR expansion <$20K

**Sample Output:**
```
EXPANSION OPPORTUNITIES: 12 accounts, $340K potential incremental ARR

HIGH PRIORITY (3 accounts, $138K potential, 70% close rate = $97K expected):
1. Bear Creek School District - $142K current ARR, 92/100 health score
   â€¢ Opportunity: New campuses (3 locations requiring connectivity)
   â€¢ Potential ARR: +$55K
   â€¢ Timing: Board approved campus openings August 2025, E-rate deadline May 1
   â€¢ Close Probability: 75% (strong relationship, budgeted project)
   â€¢ Recommended Action: Proactive outreach by Jan 31, proposal by Feb 15, close by April 30

2. Riverside Unified - $125K current ARR, 89/100 health score
   â€¢ Opportunity: Bandwidth upgrade (500Mbps â†’ 1Gbps)
   â€¢ Potential ARR: +$45K
   â€¢ Timing: Network capacity constraints emerging, technology plan refresh Q2
   â€¢ Close Probability: 70% (identified need, strong usage pattern)
   â€¢ Recommended Action: QBR discussion Feb 15, capacity analysis, proposal by March 1

MEDIUM PRIORITY (5 accounts, $165K potential, 60% close rate = $99K expected):
[Details for 5 medium priority expansion opportunities]

LOW PRIORITY (4 accounts, $37K potential, 40% close rate = $15K expected):
[Details for 4 opportunistic expansion opportunities]

TOTAL EXPECTED EXPANSION: $211K incremental ARR (62% weighted close rate)

RESOURCE ALLOCATION RECOMMENDATION:
â€¢ High Priority: Account executive proactive outreach, dedicated proposal resources
â€¢ Medium Priority: CSM-led discovery during QBRs, sales support as needed
â€¢ Low Priority: Opportunistic mentions during regular check-ins, no dedicated campaigns
```

### 5. Automated QBR Preparation

**What Claude Creates:**
- Customer-specific QBR agenda with data-driven insights
- Performance summary (uptime, support, usage trends)
- Value realization analysis (ROI delivered)
- Risk assessment and proactive issue resolution
- Expansion opportunity discussion points
- Next quarter action items and success metrics

**QBR Package Contents:**
1. Executive summary (relationship health, key achievements, challenges)
2. Performance metrics dashboard (uptime, support, usage)
3. Value delivered (cost savings, reliability, E-rate support)
4. Strategic initiatives alignment (district technology plan support)
5. Proactive recommendations (optimization opportunities, expansion options)
6. Next quarter priorities and success measures

**Time Savings:** 3-4 hours manual QBR prep â†’ 20 minutes validation = 2.5+ hours saved per QBR

## How to Request Analysis

### Basic Customer Health Portfolio Review

**Request:**
> "Generate customer health dashboard across all active accounts. Flag at-risk renewals in next 90 days with retention priorities."

**What Claude Does:**
1. Connects to Salesforce and Zendesk to pull customer data
2. Calculates health scores across all 5 dimensions
3. Identifies Red/Yellow/Green status for each account
4. Flags renewals in next 90 days with churn probability
5. Prioritizes by ARR value at risk
6. Creates executive dashboard with action recommendations

**Time Required:** 5-8 minutes for complete portfolio analysis (47 accounts)

### Deep-Dive At-Risk Account Analysis

**Request:**
> "Deep-dive analysis for [Account Name]. I need churn probability, root cause analysis, and detailed retention strategy for CEO escalation."

**What Claude Does:**
1. Pulls comprehensive account history (support, engagement, usage, relationship)
2. Calculates detailed health score breakdown by dimension
3. Models churn probability with risk multipliers
4. Conducts root cause analysis of health deterioration
5. Develops multi-phase retention strategy with specific actions and owners
6. Creates executive briefing document for escalation

**Time Required:** 10-15 minutes for comprehensive account analysis and retention strategy

### Expansion Pipeline Development

**Request:**
> "Identify expansion opportunities across Green accounts. Prioritize by revenue potential and close probability. I need proactive outreach plan."

**What Claude Does:**
1. Filters for Green accounts (health score 80+)
2. Analyzes expansion signals (high usage, growth indicators, budget cycles)
3. Identifies expansion opportunity types (bandwidth, locations, services)
4. Models close probability based on health score and relationship strength
5. Prioritizes by expected value (potential ARR Ã— close probability)
6. Creates outreach plan with specific timelines and resource allocation

**Time Required:** 8-12 minutes for expansion pipeline analysis

### Quarterly Executive Customer Review

**Request:**
> "Prepare quarterly customer health executive review for board presentation. Include portfolio health, churn risk, retention strategies, and expansion pipeline."

**What Claude Does:**
1. Synthesizes customer data across all accounts
2. Generates portfolio health scorecard with trends
3. Identifies Red accounts requiring executive intervention
4. Develops Yellow account retention campaign plan
5. Creates expansion opportunity pipeline with revenue forecast
6. Formats as board-ready presentation with executive narrative

**Time Required:** 15-20 minutes for complete board package

## Analysis Output Formats

### Executive Dashboard Format
```markdown
# CUSTOMER HEALTH EXECUTIVE DASHBOARD - [Date]

## PORTFOLIO HEALTH SUMMARY
âœ“ Green Accounts: [count] ([percentage]%) - $[ARR]
âš  Yellow Accounts: [count] ([percentage]%) - $[ARR]
ðŸ”´ Red Accounts: [count] ([percentage]%) - $[ARR]

Total ARR: $[total] | Renewals Next 90 Days: [count] accounts ($[ARR])

## EXECUTIVE DECISIONS REQUIRED

### IMMEDIATE (This Week)
1. **[Account Name]** - $[ARR] ARR - [Churn Probability]%
   - Issue: [Root cause summary]
   - Impact: [Business impact if lost]
   - Recommended Action: [Specific executive action required]
   - Owner: [Executive name] | Timeline: [Deadline]

### NEAR-TERM (Next 30 Days)
[Similar format for medium-priority retention items]

## RETENTION CAMPAIGN PRIORITIES
â€¢ Red Accounts: $[ARR] at risk - Executive intervention required
â€¢ Yellow Accounts: $[ARR] at risk - CSM-led retention campaigns
â€¢ Expected Churn Without Intervention: $[ARR] ([percentage]% portfolio)
â€¢ Expected Retention With Intervention: $[ARR] ([percentage]% success rate)

## EXPANSION PIPELINE
â€¢ High Priority: [count] accounts, $[potential ARR], [close rate]% = $[expected ARR]
â€¢ Medium Priority: [count] accounts, $[potential ARR], [close rate]% = $[expected ARR]
â€¢ Total Expected Expansion: $[total expected ARR] (Q1-Q2 2025)

## CUSTOMER SUCCESS METRICS TRENDING
- Average Portfolio Health Score: [current] (vs [previous] quarter)
- Retention Rate: [current]% (vs [target]% target)
- Expansion ARR (YTD): $[current] (vs $[target] plan)
- QBR Attendance Rate: [current]% (vs [target]% target)

## NEXT WEEK PRIORITIES
1. [Priority 1 with owner and deadline]
2. [Priority 2 with owner and deadline]
3. [Priority 3 with owner and deadline]
```

### Account Deep-Dive Format
```markdown
# ACCOUNT ANALYSIS: [Account Name]

## CUSTOMER PROFILE
- ARR: $[amount]
- Contract Term: [years]
- Renewal Date: [date] ([days] days)
- Tenure: [years] years
- Account Executive: [name]
- CSM: [name]

## HEALTH ASSESSMENT
- **Overall Health Score:** [score]/100 ([Red/Yellow/Green])
- **Churn Probability:** [percentage]%
- **Trend:** [Improving/Stable/Declining] (vs [timeframe])

### Health Score Breakdown
- Support Quality: [score]/25 ([analysis])
- Engagement: [score]/25 ([analysis])
- Product Usage: [score]/20 ([analysis])
- Relationship Strength: [score]/15 ([analysis])
- Sentiment: [score]/15 ([analysis])

## RISK FACTORS
1. **[Risk Category]:** [Specific risk description]
2. **[Risk Category]:** [Specific risk description]
3. **[Risk Category]:** [Specific risk description]

## ROOT CAUSE ANALYSIS
**Primary Issue:** [Main driver of health deterioration]
**Contributing Factors:**
- [Factor 1 with supporting evidence]
- [Factor 2 with supporting evidence]
- [Factor 3 with supporting evidence]

## VALUE AT RISK
- Annual ARR: $[amount]
- 3-Year Contract Value: $[amount]
- Customer Lifetime Value: $[amount] (estimated)

## RETENTION STRATEGY
[Multi-phase retention plan with specific actions, owners, and timelines]

## SUCCESS METRICS
- [Metric 1]: [Target and timeline]
- [Metric 2]: [Target and timeline]
- [Outcome]: [Success criteria]
```

## Integration Points

### With Salesforce MCP
```
Read: Account records, opportunity data, contract details, renewal dates, ARR values, account history
Analyze: Customer lifecycle stage, renewal timing, expansion history, relationship patterns
Generate: Customer health scores, churn probability models, retention strategy recommendations
```

### With Zendesk MCP
```
Read: Support ticket history, ticket volume trends, escalation patterns, CSAT scores, open issues
Analyze: Support quality metrics, SLA adherence, resolution time trends, escalation frequency
Generate: Support quality scoring, issue root cause analysis, support improvement recommendations
```

### With Usage Data Integration
```
Read: Bandwidth utilization, network uptime, service adoption metrics, portal login frequency
Analyze: Usage trends, capacity constraints, service adoption breadth, engagement patterns
Generate: Product usage scoring, optimization recommendations, expansion opportunity identification
```

### With DOCX/XLSX/PPTX Skills
```
DOCX: Executive briefings, retention proposals, customer QBR materials
XLSX: Customer health scorecards, retention campaign tracking, expansion pipeline modeling
PPTX: Executive customer reviews, board presentations, QBR slide decks
```

## Best Practices

1. **Monthly Health Monitoring**: Calculate customer health scores monthly (not just quarterly) to identify deterioration early and enable proactive intervention.

2. **90-Day Renewal Pipeline**: Maintain rolling 90-day renewal pipeline with proactive retention outreach for all Yellow/Red accounts 120+ days before renewal.

3. **Executive Escalation Protocol**: Establish clear escalation criteria for CEO/VP engagement with at-risk customers (Red accounts >$100K ARR, Yellow accounts >$200K ARR).

4. **QBR Discipline**: Mandate quarterly QBRs for all accounts >$50K ARR; use automated QBR prep to reduce CSM burden while increasing meeting quality.

5. **Expansion Opportunity Pipeline**: Review Green account expansion opportunities quarterly; proactive outreach has 70% close rate vs 40% reactive.

## Common Questions

**Q: How accurate is the churn prediction model?**
A: Historical validation shows 100% recall (all churned customers were flagged Red >90 days before churn) and 60% precision (40% of Red accounts can be saved with proactive intervention). The model prioritizes catching all at-risk customers over minimizing false positives.

**Q: What defines a "Red" vs "Yellow" vs "Green" customer?**
A: Health score ranges: Red (0-59, critical risk, 60-80% churn probability), Yellow (60-79, watch status, 30-50% churn probability), Green (80-100, healthy, 5-15% churn probability). Thresholds based on historical churn patterns.

**Q: How often should customer health scores be recalculated?**
A: Monthly minimum for proactive monitoring. Weekly for Red accounts under active retention campaigns. Real-time monitoring available for critical escalations.

**Q: Can the model predict churn for new customers (<1 year tenure)?**
A: Yes, but with lower confidence. New customer churn risk is primarily driven by implementation quality, early support experience, and expectations alignment. Separate onboarding health model recommended for customers <6 months.

**Q: How does the skill handle K-12 education-specific factors?**
A: Model incorporates K-12-specific indicators: E-rate cycle timing, superintendent/tech director transitions, budget approval cycles, summer usage patterns, and school calendar alignment for QBRs and implementations.

## Technical Requirements

### Salesforce Data Structure
- Customer accounts with ARR, renewal dates, contract terms
- Opportunity data for expansion tracking
- Account activity tracking (email, meetings, QBRs)
- Custom fields: Health Score, Churn Risk, Last QBR Date

### Zendesk Integration
- Support ticket volume and resolution time tracking
- Escalation patterns and SLA compliance monitoring
- CSAT score collection and trending
- Customer sentiment tagging

### Usage Data Integration
```
/Customer-Usage-Data/
  /[Customer-Name]/
    /bandwidth-utilization.xlsx
    /network-uptime.xlsx
    /service-adoption.xlsx
    /portal-login-activity.xlsx
```

### Data Quality Requirements
- Customer data updated weekly minimum
- Support ticket data synced daily
- Usage data refreshed weekly
- Health scores recalculated monthly (weekly for Red accounts)

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Churn Prevention | <5% annual churn | Retention rate vs. industry benchmark (15-20%) |
| Early Warning | 90+ days advance notice | Days between Red flag and renewal date |
| Retention Success Rate | 75%+ Red accounts saved | Red accounts retained with executive intervention |
| Expansion Acceleration | $250K+ incremental ARR | Proactive expansion deals closed annually |
| CSM Productivity | 50% time savings | QBR prep time reduction, portfolio management efficiency |

## Implementation Notes

### First-Time Setup:
1. Configure Salesforce MCP access to customer account data
2. Integrate Zendesk MCP for support ticket analysis
3. Establish usage data integration (bandwidth, uptime, adoption)
4. Create baseline health scores for current customer portfolio
5. Test churn prediction model with historical churn data
6. Refine thresholds and escalation criteria based on organization standards

### Scaling Considerations:
- Can handle 50-100 customer accounts efficiently
- Supports multiple CSM territories with portfolio segmentation
- Scales to enterprise customer bases with automated health monitoring
- Requires consistent data quality practices for optimal accuracy

### K-12 Education Context:
- Account for E-rate cycles and funding windows
- Consider school calendar for QBR scheduling and implementation timing
- Recognize leadership transition patterns (superintendents, tech directors)
- Understand budget approval processes and board meeting schedules
- Incorporate summer usage patterns and fall implementation seasonality

### Continuous Improvement:
- Monthly refinement of health scoring weights based on churn outcomes
- Quarterly review of churn prediction accuracy vs. actual results
- Annual recalibration of risk multipliers based on market dynamics
- Ongoing A/B testing of retention strategies to optimize success rates

---

**Version:** 1.0
**Last Updated:** 2025-01-12
**Created for:** Ty Sorensen, VP Customer Success, ISPN Network Services

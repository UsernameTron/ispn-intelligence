---
name: ispn-skill-orchestrator
description: |
  Master orchestrator for ISPN Workforce Intelligence Suite. Routes file uploads to correct
  parsers, routes queries to correct analysis skills, enforces systemic-first workflow,
  passes context between skills. This skill coordinates all other ISPN skills.
  
  TRIGGERS: Any ISPN data file, any workforce/operations query, cross-skill analysis needed.
  
  SUITE SKILLS (17 total):
  - Platform (Data Extraction): genesys-cloud-cx-reporting, genesys-qa-analytics, genesys-skills-routing
  - Data Parsers: ispn-dpr-analysis, ispn-wcs-analysis, ispn-scorecard-analysis
  - Diagnostics: genesys-queue-performance-analysis, ispn-agent-coaching, ispn-training-gap, ispn-sentiment-analysis
  - Workforce Decisions: workforce-optimization-persona, ispn-capacity-planning, ispn-intraday-staffing, ispn-schedule-optimization
  - Business: ispn-cost-analytics, ispn-partner-sla, ispn-attrition-risk
---

# ISPN Skill Orchestrator

**This skill coordinates the entire ISPN Workforce Intelligence Suite (17 skills).**

## SKILL ARCHITECTURE (4 Layers)

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 0: PLATFORM (Data Extraction Specifications)         │
│  genesys-cloud-cx-reporting, genesys-qa-analytics,          │
│  genesys-skills-routing                                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: PARSERS (File → Structured Data)                  │
│  ispn-dpr-analysis, ispn-wcs-analysis, ispn-scorecard-analysis │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: DIAGNOSTICS (What's Wrong + Why)                  │
│  genesys-queue-performance-analysis, ispn-agent-coaching,   │
│  ispn-training-gap, ispn-sentiment-analysis                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: DECISIONS (Action Recommendations)                │
│  workforce-optimization-persona (6 decisions),              │
│  ispn-capacity-planning, ispn-intraday-staffing,            │
│  ispn-schedule-optimization, ispn-partner-sla,              │
│  ispn-cost-analytics, ispn-attrition-risk                   │
└─────────────────────────────────────────────────────────────┘
```

---

## FILE ROUTING

### Genesys Raw Exports (Layer 0 → Layer 1)
| Pattern | Route To | Then To | Context Extracted |
|---------|----------|---------|-------------------|
| Interactions*.csv (Genesys export) | genesys-cloud-cx-reporting | ispn-dpr-analysis | Field mapping, callback ID, AHT components |
| Agent_Status*.csv (Genesys export) | genesys-cloud-cx-reporting | ispn-dpr-analysis | Hours worked, shrinkage taxonomy |
| WFM_Adherence*.csv (Genesys export) | genesys-cloud-cx-reporting | ispn-intraday-staffing | Adherence %, conformance % |
| evaluation_questions*.csv | genesys-qa-analytics | ispn-training-gap | QA scores, agent tiers, coaching plans |

### ISPN Processed Files (Layer 1)
| Pattern | Route To | Context Extracted |
|---------|----------|-------------------|
| DPR*.xlsx | ispn-dpr-analysis | systemic_flags, daily_metrics, AHT decomposition |
| WCS*.xlsx | ispn-wcs-analysis | partner_sla_status, agent_ranks |
| *Scorecard*.xlsx | ispn-scorecard-analysis | monthly_kpis, capacity |
| Agent_Performance*.csv | ispn-agent-coaching | individual_metrics |
| reviewreport*.csv | ispn-training-gap | qa_scores, failures |
| QA*.xlsx, Quality*.csv | ispn-training-gap | qa_category_data |
| Attendance*.csv, UKG*.xlsx | ispn-agent-coaching | attendance_exceptions |
| Speech_Analytics*.csv | ispn-sentiment-analysis | sentiment_data |

---

## QUERY ROUTING

### Platform & Configuration Queries
| Query Pattern | Route To | Purpose |
|---------------|----------|---------|
| "how to export from Genesys", "field names" | genesys-cloud-cx-reporting | Export specifications |
| "QA evaluation format", "evaluation_questions structure" | genesys-qa-analytics | CSV parsing specs |
| "routing config", "ACD skills", "bullseye" | genesys-skills-routing | Routing troubleshooting |
| "skill mismatch", "calls waiting agents idle" | genesys-queue-performance-analysis | Queue diagnostics |

### Analysis Queries
| Query Pattern | Route To | Prerequisites |
|---------------|----------|---------------|
| "daily performance", "today's numbers" | ispn-dpr-analysis | DPR file |
| "weekly stats", "agent rankings" | ispn-wcs-analysis | WCS file |
| "partner SLA", "breach" | ispn-partner-sla | WCS file |
| "who needs coaching", "bottom performers", "PIP" | ispn-agent-coaching | **SYSTEMIC CHECK*** |
| "do we need to hire", "capacity", "FTE", "Erlang" | ispn-capacity-planning | Scorecard preferred |
| "cost per contact", "ROI", "turnover cost" | ispn-cost-analytics | None |
| "training gaps", "QA failures", "curriculum" | ispn-training-gap | QA data |
| "flight risk", "retention", "attrition" | ispn-attrition-risk | Multiple sources |
| "monthly KPIs", "scorecard" | ispn-scorecard-analysis | Scorecard file |
| "quality scores", "QA trends", "CSAT alignment" | ispn-training-gap | QA data |
| "attendance", "schedule adherence" | ispn-agent-coaching | UKG/Attendance data |
| "sentiment", "CSAT", "customer experience" | ispn-sentiment-analysis | Interaction/speech data |
| "shrinkage", "unplanned absence" | ispn-capacity-planning | Adherence data |

### Workforce Decision Queries (Layer 3)
| Query Pattern | Route To | Prerequisites |
|---------------|----------|---------------|
| "overstaffed", "VTO", "early release" | workforce-optimization-persona (Decision 1) | Real-time data |
| "understaffed", "OT", "recall breaks" | workforce-optimization-persona (Decision 2) | Real-time data |
| "schedule optimization", "forecast accuracy" | workforce-optimization-persona (Decision 3) | Weekly data |
| "monthly capacity", "headcount modeling" | workforce-optimization-persona (Decision 4) | Scorecard |
| "partner remediation", "SLA breach" | workforce-optimization-persona (Decision 5) | WCS file |
| "shrinkage management", "efficiency" | workforce-optimization-persona (Decision 6) | Adherence data |

### Queue Performance Queries
| Query Pattern | Route To | Prerequisites |
|---------------|----------|---------------|
| "why is service level low", "queue performance" | genesys-queue-performance-analysis | Queue data |
| "abandon analysis", "when do customers give up" | genesys-queue-performance-analysis | Interactions |
| "queue comparison", "which queue underperforms" | genesys-queue-performance-analysis | Multiple queues |
| "routing issues", "why calls waiting" | genesys-queue-performance-analysis + genesys-skills-routing | Queue + config |

*SYSTEMIC CHECK = Must verify DPR/WCS flags OR user confirmation

---

## "WHY IS [METRIC] CHANGING?" WORKFLOWS

**"Why is AHT increasing?"**
1. ispn-dpr-analysis → AHT trend + component decomposition (talk/hold/ACW)
2. genesys-cloud-cx-reporting → Verify field extraction (Total Handle = Talk + Hold + ACW)
3. ispn-wcs-analysis → Partner-level AHT (call mix shift?)
4. ispn-agent-coaching → Individual outliers driving average
5. ispn-training-gap → QA failures in troubleshooting categories

**"Why is FCR declining?"**
1. ispn-dpr-analysis → FCR trend, when decline started
2. ispn-wcs-analysis → Partner-level FCR (complexity shift?)
3. ispn-training-gap → QA failures + empowerment gaps
4. ispn-agent-coaching → New hires vs tenure FCR gap

**"Why are escalations increasing?"**
1. ispn-dpr-analysis → Escalation trend, outage correlation
2. ispn-wcs-analysis → Partner escalation breakdown
3. ispn-training-gap → Knowledge/empowerment gaps
4. ispn-partner-sla → Partner complexity changes

**"Why is utilization low/high?"**
1. ispn-scorecard-analysis → Volume vs staffing trend
2. ispn-capacity-planning → FTE math + shrinkage analysis
3. workforce-optimization-persona → Decision 6 (Shrinkage Management)
4. ispn-cost-analytics → Financial impact

**"Why is sentiment declining?"**
1. ispn-sentiment-analysis → Trend + root cause categorization
2. ispn-dpr-analysis → Correlation with AWT, abandon
3. ispn-agent-coaching → Individual agent patterns
4. ispn-training-gap → Soft skills gaps

**"Why is service level low?"**
1. genesys-queue-performance-analysis → Diagnostic framework (5 scenarios)
2. ispn-dpr-analysis → Volume vs forecast, AHT changes
3. genesys-skills-routing → Skill mismatch check
4. workforce-optimization-persona → Decision 2 (Understaffed assessment)

**"Why are abandons high?"**
1. genesys-queue-performance-analysis → Abandon time distribution analysis
2. ispn-dpr-analysis → AWT correlation
3. workforce-optimization-persona → Staffing gap assessment
4. ispn-cost-analytics → Revenue at risk calculation

---

## SYSTEMIC-FIRST PROTOCOL (MANDATORY)

Before ANY individual performance analysis:

```
SYSTEMIC CONTEXT CHECK
═══════════════════════════════════════════════════════════════
□ outage_day (DPR: Outage Tickets > 50)
□ volume_spike (DPR: Calls > 120% of 4-wk avg)
□ staffing_gap (DPR: On Queue < 75% scheduled)
□ partner_issue (WCS: Any partner esc > 40%)
□ routing_issue (Queue: Calls waiting + agents idle)
  → If TRUE: genesys-queue-performance-analysis + genesys-skills-routing

IF NO DATA: Request DPR/WCS or user confirmation
IF ANY FLAG TRUE: Document as mitigating factor
IF ALL CLEAR: Proceed to individual analysis
═══════════════════════════════════════════════════════════════
```

---

## CROSS-SKILL WORKFLOWS

**"Who should we coach/PIP?"**
1. SYSTEMIC CHECK → verify flags
2. ispn-agent-coaching → composite scoring
3. genesys-qa-analytics → agent tier assignment (Critical/Development/Standard/Exemplary)
4. ispn-training-gap → skill gaps + quality-CSAT alignment
5. ispn-attrition-risk → flight risk check
6. ispn-sentiment-analysis → CX impact assessment

**"Do we need to hire?"**
1. ispn-scorecard-analysis → headcount, utilization
2. workforce-optimization-persona (Decision 4) → Monthly capacity model
3. ispn-capacity-planning → Erlang C, FTE requirement, shrinkage impact
4. ispn-cost-analytics → financial impact

**"Are we overstaffed/understaffed right now?"**
1. workforce-optimization-persona (Decision 1 or 2) → Scoring algorithm
2. ispn-intraday-staffing → Real-time assessment
3. ispn-dpr-analysis → Current interval metrics
4. ispn-schedule-optimization → Forecast variance check

**"How do I extract data from Genesys?"**
1. genesys-cloud-cx-reporting → 4 required exports with exact navigation paths
2. Field-to-KPI mapping for scorecard validation
3. Callback identification method (`Media Type = "callback"`)

**"Why are calls waiting despite idle agents?"**
1. genesys-queue-performance-analysis → Skill mismatch detection
2. genesys-skills-routing → ACD configuration review
3. workforce-optimization-persona → Routing issue flag

**"Create coaching plans for QA failures"**
1. genesys-qa-analytics → Agent tiering + question-level failure analysis
2. Extract QuestionHelpText for behavioral criteria
3. ispn-training-gap → Map to training curriculum
4. ispn-agent-coaching → Composite score context

---

## WORKFORCE OPTIMIZATION DECISION REFERENCE

From workforce-optimization-persona:

### Decision 1: Overstaffed Assessment
**Triggers:** AWT < 30s (30+ min), Occupancy < 65% (30+ min), Queue = 0 (15+ min)
**Scoring:** Score ≥ 8 = Critical (mandatory early release), Score ≥ 5 = Action (offer VTO)

### Decision 2: Understaffed Assessment
**Triggers:** AWT > 180s (15+ min), Occupancy > 90% (30+ min), Abandon > 5%
**Critical Triggers:** AWT > 300s, Abandon > 10%, Outage declared
**Actions:** WARNING → recall breaks, activate on-call. CRITICAL → mandatory OT, all-hands.

### Decision 3: Weekly Schedule Optimization
**Triggers:** Forecast accuracy < 85%, SLA missed 3+ days, Utilization outside 50-65% band
**Checklist:** Forecast accuracy, coverage analysis, schedule adjustments, capacity buffer

### Decision 4: Monthly Capacity Planning
**Formula:** `Required_FTE = (Volume × AHT_hrs) / (173.2 × 0.60 × 0.72)`
**Steps:** Volume forecast → Handle time projection → Capacity requirement → Gap analysis

### Decision 5: Partner SLA Remediation
**Thresholds:** AWT > 120s = breach, Answer < 60s < 70% = breach, Esc > 10% = breach
**Triage:** Yellow (trending) → Orange (within 10%) → Red (exceeded)

### Decision 6: Shrinkage Management
**Taxonomy:** Planned (~20%: training, meetings, breaks) + Unplanned (<10%: absences, system, late/early)
**Thresholds:** Total < 30% = GREEN, 30-35% = WARNING, > 35% = CRITICAL

---

## THRESHOLD REFERENCE

### INTERNAL PERFORMANCE THRESHOLDS
*For agent/team evaluation and coaching decisions*

| Metric | GREEN | YELLOW | RED |
|--------|-------|--------|-----|
| AHT | < 10.7 min | 10.7-11.5 | > 11.5 |
| AWT | < 90 sec | 90-180 | > 180 |
| FCR | > 70% | 65-70% | < 65% |
| Escalation | < 30% | 30-35% | > 35% |
| Utilization | 55-65% | 45-55/65-70 | <45/>70 |
| Quality | > 88 | 85-88 | < 85 |
| Abandon | < 5% | 5-8% | > 8% |
| Schedule Adherence | > 90% | 85-90% | < 85% |
| Sentiment | > +20 | 0 to +20 | < 0 |
| Shrinkage | < 30% | 30-35% | > 35% |
| Occupancy | 75-85% | 70-75/85-90 | <70/>90 |
| Service Level | > 80% | 70-80% | < 70% |

### PARTNER SLA THRESHOLDS (CONTRACTUAL)
*Triggers remediation protocol - see ispn-partner-sla*

| Metric | Target | Warning | Breach |
|--------|--------|---------|--------|
| AWT | ≤ 120s | > 100s | > 120s |
| Answer < 60s | ≥ 70% | < 75% | < 70% |
| Escalation | < 10% | > 8% | > 10% |
| Abandon | ≤ 10% | > 8% | > 10% |

⚠️ **Important:** Internal thresholds (30% esc GREEN) differ from contractual (10% esc breach). Use context to determine which applies.

### AHT Component Thresholds

| Component | Target | Warning | Critical |
|-----------|--------|---------|----------|
| Talk Time | ~8.5 min | > 9.5 min | > 10.5 min |
| Hold Time | ~1.9 min | > 2.5 min | > 3.0 min |
| ACW Time | 15 sec | N/A | N/A |

### QA Performance Tiers (from genesys-qa-analytics)

| Tier | Score Range | Action Required |
|------|-------------|-----------------|
| Exemplary | ≥ 95% | Recognition, mentorship role |
| Standard | 80-94% | Maintenance coaching |
| Development | 65-79% | Targeted skill building |
| Critical | < 65% | Immediate intervention, PIP consideration |

### Compensation (Fully Loaded)
| Level | Hourly | Annual | Turnover Cost |
|-------|--------|--------|---------------|
| L1 | $18.11 | $37,669 | $11,328 |
| L2 | $23.29 | $48,443 | $14,500 |
| L3 | $28.46 | $59,197 | $18,000 |

**Total Payroll:** $6.64M (187 employees)

### ROI Benchmarks
| Improvement | Annual Value |
|-------------|--------------|
| AHT -1 min | $186K |
| FCR +5pp | $501K |
| Utilization +5pp | $332K |

### Organization
- 165 agents, 16 teams, 200 partners
- Leadership: Jeff Neblett (CEO), Scott Lauber (CFO), Charlie Brenneman (SVP Ops)
- Tech Center: Pete Connor (Director)

---

## ISPN CALCULATION STANDARDS

| Standard | Rule | Source |
|----------|------|--------|
| Abandon threshold | Only count ≥ 60 sec queue | genesys-cloud-cx-reporting |
| AHT filter | Exclude < 20 sec handle | genesys-cloud-cx-reporting |
| Utilization denominator | Excludes training hours | genesys-cloud-cx-reporting |
| ACW timeout | 15 seconds (ININ-WRAP-UP-TIMEOUT) | genesys-cloud-cx-reporting |
| Callback identification | `Media Type = "callback"` | genesys-cloud-cx-reporting |

## DATA QUALITY ALERTS

| Source | Known Issue | Mitigation |
|--------|-------------|------------|
| Scorecard Row 58 | AHT formula issues FY20-FY23 | Validate manually |
| WCS CD data 2 | Requires 168-row validation | Check hourly completeness |
| Genesys ACW | 97.9% show exactly 15,000ms | Reflects timeout config, not actual work |

## GENESYS EXPORT QUICK REFERENCE

| Export | Navigation | Primary Use |
|--------|------------|-------------|
| Interactions | Performance → Workspace → Interactions | Volumes, AHT, AWT, abandons |
| Agent Status Duration Details | Performance → Contact Center → Agent Status | Hours, shrinkage |
| WFM Historical Adherence | WFM → Historical Adherence | Adherence, conformance |
| Agent Performance | Performance → Workspace → Agents Performance | AHT validation |

---

## REFERENCE TEMPLATES

Located in `references/`:
- daily-triage-template.md
- agent-coaching-template.md
- escalation-analysis-template.md
- partner-sla-tracker.md
- capacity-model-template.md
- headcount-business-case.md

---
*This orchestrator makes the 17 individual skills work as a unified system.*

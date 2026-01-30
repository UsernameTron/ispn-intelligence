---
name: genesys-qa-analytics
description: Transform Genesys Cloud QA evaluation exports into actionable gap-closing intelligence with agent coaching plans, calibration analysis, and performance dashboards. Processes Full Call Review (104pts/21Q), Auto-Evaluation (40pts/9Q), and Focus Review (100pts/1Q) forms.
metadata:
  version: 1.0.0
  dependencies: python>=3.8, pandas>=2.0.0, numpy>=1.24.0
  output_formats: html, markdown, xlsx
  csv_structure: 36-column Genesys evaluation_questions export
---

# Genesys QA Analytics Skill

## Overview

This skill transforms raw Genesys Cloud QA evaluation CSV exports into actionable coaching intelligence. The CSV structure is fixed and cannot be modified—all analytical power lives in this skill.

**Core Capability**: Close performance gaps by:
1. Identifying WHO needs coaching (agent-level performance tiers)
2. Determining WHAT behaviors to coach (question-level failure patterns)
3. Providing HOW to coach (extracting behavioral criteria from QuestionHelpText)
4. Validating WHO is calibrated (evaluator consistency analysis)

## CSV Structure Recognition

### Fixed Column Inventory (36 Columns)
The skill expects this exact structure from Genesys evaluation_questions exports:

| Column | Purpose | Key Values |
|--------|---------|------------|
| EvaluationId | Unique evaluation identifier | GUID |
| EvaluationFormName | Form type | Full Call Review, Auto-Evaluation, Focus Review |
| AgentName / AgentId | Evaluated technician | String / GUID |
| EvaluatorName / EvaluatorId | QA analyst | String / GUID |
| QuestionGroupName | Category grouping | 9 distinct groups |
| QuestionText | Evaluation criteria | 31 unique questions |
| QuestionHelpText | **Behavioral coaching criteria** | Detailed pass/fail conditions |
| AnswerYesNo | Response | Yes / No / null |
| Score | Points earned | 0-100 (varies by question) |
| MaxPoints | Maximum possible | 1, 5, 10, 100 |
| ConversationDate | Call date | ISO date |
| SubmittedDate | Evaluation completion | ISO datetime |

### Evaluation Form Types

**Full Call Review Evaluation Form** (26 evals in sample)
- 21 questions across 5 groups
- 104 maximum points
- Manual QA evaluation
- Groups: Opening/Closing, Communication & Courtesy, Troubleshooting & Security, Procedures & Resources, Auto-Fail Flags

**Auto-Evaluation Form - v0.1** (24 evals in sample)
- 9 questions across 3 groups
- 40 maximum points
- AI-assisted evaluation
- Groups: Script Compliance, Communication Markers, Auto-Fail Detection

**Focus Review Evaluation Form** (1 eval in sample)
- 1 question
- 100 maximum points
- Success/Missed Opportunity tracking

## Question Groups & Behavioral Criteria

### Script Compliance (40 pts max, 4 questions)

**Introductory Courtesies** [5 pts] — 41.7% failure rate
> *Coaching Criteria*: Please/thank you should be offered by the agent after requesting/receiving information like name, phone number, and address from the customer at the start of the interaction. This information should be confirmed within the first 5 minutes of the call.

**Opening Branding Statement** [5 pts] — 20.8% failure rate
> *Coaching Criteria*: Search the first 3 exchanges for greeting with BOTH company/provider name AND department identification (e.g., "Thank you for calling [Company] Technical Support").

**Subscriber Information Confirmation** [5 pts] — 8.3% failure rate
> *Coaching Criteria*: Confirm ALL: Customer first/last name, Service address/location, Callback number, Phone type (cell/landline).

**Escalation Procedures** [5 pts] — 8.3% failure rate
> *Coaching Criteria*: If escalation occurred, verify: explanation of next steps, callback number confirmed, courtesies during call end.

### Communication Markers (20 pts max, 3 questions)

**Courtesy Language Usage** [10 pts] — 20.8% failure rate
> *Coaching Criteria*: Count instances from TECHNICIAN ONLY: "Please", "Thank you/Thanks", "I appreciate", "If you don't mind", "Would you mind". PASS if 5+ instances.

**Hold Courtesies** [5 pts] — 37.5% failure rate
> *Coaching Criteria*: If hold detected, verify BOTH: Before-hold permission/notification AND after-hold acknowledgment ("Thank you for holding").

**Issue Acknowledgment** [5 pts] — 16.7% failure rate
> *Coaching Criteria*: After customer describes problem, search for: "I understand", "I can see why", "I'm sorry you're experiencing this", "Let's get this resolved", "That must be frustrating".

### Communication & Courtesy (30 pts max, 5 questions)

**Acknowledgement & Empathy** [5 pts] — 19.2% failure rate
**Dead Air** [5 pts] — 30.8% failure rate
**Excessive Hold** [5 pts] — 7.7% failure rate
**Courtesy & Professionalism** [5 pts] — 0% failure rate
**Tone & Demeanor** [10 pts] — 0% failure rate

### Procedures & Resources (25 pts max, 4 questions)

**Ticket Accuracy** [10 pts] — 30.8% failure rate
**Use of Support Flow** [5 pts] — 3.8% failure rate
**Application of U/L Instruction** [5 pts] — 3.8% failure rate
**Use of Tools/Admins** [5 pts] — 3.8% failure rate

### Opening/Closing (20 pts max, 4 questions)

**Call Closing/Escalation Procedures** [5 pts] — 23.1% failure rate
**Subscriber Location & Search Queries** [5 pts] — 19.2% failure rate
**Provider Call Branding** [5 pts] — 3.8% failure rate
**Introductory Courtesy** [5 pts] — 0% failure rate

### Troubleshooting & Security (25 pts max, 4 questions)

**Checking Fundamentals** [5 pts] — 15.4% failure rate
**Accurate Diagnosis** [5 pts] — 7.7% failure rate
**Efficiency of Troubleshooting** [5 pts] — 7.7% failure rate
**Verification of CPNI** [10 pts] — 0% failure rate

### Auto-Fail Flags (4 pts max, 4 questions)
All binary pass/fail (0% triggered in sample):
- Falsified Documentation
- Disconnected the Call
- Swore on the Call
- Excessively Rude or Aggressively Loud

### Auto-Fail Detection (0 pts, 2 questions)
Detection-only, no scoring impact:
- Profanity/inappropriate language detection
- Condescending/dismissive language detection

## Analysis Capabilities

### 1. Agent Performance Tiering

Calculate normalized scores across evaluation form types:

| Tier | Criteria | Action Required |
|------|----------|-----------------|
| **Exemplary** | ≥95% average | Recognition, mentorship role |
| **Standard** | 80-94% average | Maintenance coaching |
| **Development** | 65-79% average | Targeted skill building |
| **Critical** | <65% average | Immediate intervention, PIP consideration |

**Normalization Formula**: `(Σ Score / Σ MaxPoints) × 100`

### 2. Gap Analysis (Category-Level)

Identify systemic training needs by question group:

```
Gap% = 100 - (Σ Group Score / Σ Group MaxPoints × 100)
```

Priority ranking:
1. Communication Markers (24.0% gap)
2. Script Compliance (19.8% gap)
3. Procedures & Resources (14.6% gap)
4. Opening/Closing (11.5% gap)
5. Communication & Courtesy (9.6% gap)
6. Troubleshooting & Security (6.2% gap)

### 3. Question-Level Failure Analysis

Identify specific behaviors driving point loss:

| Metric | Formula |
|--------|---------|
| Failure Rate | `(Scores of 0) / (Total Evaluations) × 100` |
| Points Lost | `Σ MaxPoints - Σ Score` |
| Impact Score | `Failure Rate × MaxPoints weight` |

### 4. Coaching Plan Generation

For each agent in Development or Critical tier, generate:

```
AGENT COACHING PLAN
═══════════════════════════════════════════════════════════════

Agent: [Name]
Performance Tier: [Critical/Development]
Current Score: [XX.X%] | Target: 80%+ | Gap: [X.X%]
Evaluations Analyzed: [N]

─────────────────────────────────────────────────────────────
PRIORITY COACHING AREAS (Ranked by Impact)
─────────────────────────────────────────────────────────────

1. [Question Text]
   Category: [Group Name]
   Agent Failure Rate: [XX%] (vs team avg [XX%])
   Points at Risk: [X] per evaluation
   
   BEHAVIORAL CRITERIA:
   [QuestionHelpText content - exact pass/fail conditions]
   
   COACHING ACTIONS:
   • [Specific behavior to demonstrate]
   • [Observable milestone]
   • [Practice scenario]

2. [Next priority question...]

─────────────────────────────────────────────────────────────
SUCCESS METRICS
─────────────────────────────────────────────────────────────
• Target: Move to Standard tier (80%+) within 30 days
• Checkpoint: [Date] - re-evaluate 3 calls minimum
• KPI: Zero failures on Priority 1 items
```

### 5. Evaluator Calibration Analysis

Detect scoring inconsistency across QA analysts:

| Metric | Purpose | Threshold |
|--------|---------|-----------|
| Average Score | Central tendency | Compare to team mean |
| Standard Deviation | Scoring consistency | σ > 15 = calibration concern |
| Evaluation Count | Sample size | n ≥ 5 for validity |
| Harsh/Lenient Index | Deviation from norm | ±10% = recalibration needed |

### 6. Trend Detection

When multiple export periods are provided:
- Week-over-week score movement
- Category improvement/decline patterns
- Agent trajectory (improving/stable/declining)
- Evaluator drift over time

## Output Formats

### Executive Dashboard (HTML)

Obsidian-aesthetic visualization with:
- Team performance distribution (tier breakdown)
- Category gap analysis (horizontal bar chart)
- Agent leaderboard (top/bottom performers)
- Evaluator calibration status
- Coaching priority summary

Design specifications:
- Background: #09090b (warm near-black)
- Borders: 1px solid, not shadows
- Tier colors: Success (#4ade80), Cyan (#22d3ee), Amber (#fbbf24), Error (#ef4444)
- Typography: System fonts, monospace for data values
- Layout: Asymmetric three-panel grid

### Narrative Summary (Markdown)

Executive-ready prose covering:
- Period overview (date range, evaluation count, form mix)
- Performance distribution with tier counts
- Systemic gap findings (categories needing attention)
- Top 5 coaching priorities (agents + behaviors)
- Evaluator calibration assessment
- Recommended actions (prioritized)

### Agent Coaching Plans (Markdown/PDF)

Individual documents per Development/Critical agent:
- Current performance summary
- Ranked priority behaviors to address
- Exact behavioral criteria from QuestionHelpText
- Specific coaching actions
- Success metrics and timeline

### Calibration Report (Markdown)

Evaluator consistency analysis:
- Scoring distribution per evaluator
- Variance comparison
- Harsh/lenient flagging
- Calibration recommendations

## Instructions

### Step 1: CSV Validation

When a file is uploaded, verify:
1. File extension is .csv
2. Column headers match expected structure (36 columns)
3. EvaluationFormName contains recognized values
4. No critical data missing (EvaluationId, AgentName, Score, MaxPoints)

If validation fails, report specific issues and request corrected export.

### Step 2: Data Normalization

```python
# Multi-form normalization
for evaluation in unique_evaluations:
    total_score = sum(scores for questions in evaluation)
    total_max = sum(max_points for questions in evaluation)
    normalized_pct = (total_score / total_max) * 100
```

Handle form variations:
- Full Call Review: 104 max points
- Auto-Evaluation: 40 max points
- Focus Review: 100 max points

### Step 3: Agent Aggregation

Group by agent, calculate:
- Total evaluations
- Average normalized percentage
- Standard deviation (consistency)
- Score trend (if multiple evaluations)
- Assign performance tier

### Step 4: Question-Level Analysis

For each question:
- Calculate failure rate (Score=0 count / total evaluations)
- Calculate total points lost
- Extract QuestionHelpText for coaching criteria
- Rank by impact (failure rate × max points)

### Step 5: Evaluator Calibration

Group by evaluator, calculate:
- Mean score given
- Standard deviation
- Evaluation count
- Compare to team baseline

Flag if:
- σ > 15 (inconsistent scoring)
- Mean ±10% from team average (harsh/lenient)
- n < 5 (insufficient sample)

### Step 6: Output Generation

Based on user request, generate:

**For "analyze this QA export"**:
→ Executive dashboard + narrative summary

**For "who needs coaching"**:
→ Agent tier list + coaching plans for Critical/Development agents

**For "what are our quality gaps"**:
→ Category gap analysis + question-level failure ranking

**For "are evaluators calibrated"**:
→ Calibration report with recommendations

**For "create coaching plan for [agent]"**:
→ Individual agent coaching document

## Example Interactions

### Example 1: Full Analysis Request

**Input**: "Analyze this QA export and show me who needs coaching"

**Process**:
1. Parse CSV, validate structure
2. Normalize scores across form types
3. Calculate agent performance tiers
4. Identify Development/Critical agents
5. Generate question-level failure analysis for each
6. Extract QuestionHelpText coaching criteria
7. Produce dashboard + coaching plans

**Output**:
- HTML dashboard with team overview
- Markdown narrative with findings
- Individual coaching plans for flagged agents

### Example 2: Gap Analysis Request

**Input**: "What are our biggest quality gaps?"

**Process**:
1. Aggregate scores by QuestionGroupName
2. Calculate gap% for each category
3. Rank questions by failure rate × impact
4. Extract behavioral criteria for top failures

**Output**:
```
QUALITY GAP ANALYSIS
════════════════════════════════════════════════════════

Category Gaps (Ranked by Severity):
1. Communication Markers    — 24.0% gap (20 pts at risk)
2. Script Compliance        — 19.8% gap (20 pts at risk)
3. Procedures & Resources   — 14.6% gap (25 pts at risk)

Top Failing Behaviors:
1. Introductory Courtesies (Script Compliance)
   Failure Rate: 41.7% | Impact: 50 pts lost across team
   Fix: Ensure "please/thank you" offered when requesting
   customer information in first 5 minutes

2. Hold Courtesies (Communication Markers)
   Failure Rate: 37.5% | Impact: 45 pts lost across team
   Fix: Before hold: "May I place you on hold?"
        After hold: "Thank you for holding"
...
```

### Example 3: Evaluator Calibration Check

**Input**: "Are my evaluators scoring consistently?"

**Process**:
1. Group evaluations by EvaluatorName
2. Calculate mean, σ, count per evaluator
3. Compare to team baseline
4. Flag outliers

**Output**:
```
EVALUATOR CALIBRATION REPORT
════════════════════════════════════════════════════════

Evaluator         | Avg Score | σ      | n  | Status
──────────────────|───────────|────────|────|─────────
Jimmie Klein      | 84.7%     | 11.3   | 9  | ✓ Calibrated
Kyle Bonpua       | 81.5%     | 23.7   | 32 | ⚠ High Variance
Paige Rombou      | 82.3%     | 11.9   | 9  | ✓ Calibrated
Annie Pedrino     | 75.0%     | —      | 1  | ⚠ Insufficient Data

FINDINGS:
Kyle Bonpua shows σ=23.7 vs team norm ~12, suggesting
inconsistent application of scoring criteria. Recommend:
1. Calibration session reviewing borderline scenarios
2. Side-by-side scoring of same calls with Jimmie Klein
3. Re-evaluation after 10 additional scored calls
```

### Example 4: Individual Agent Focus

**Input**: "Create a coaching plan for Angelica Jones"

**Process**:
1. Filter to Angelica Jones evaluations (4 found)
2. Calculate average (59.86%), tier (Critical)
3. Identify her specific failure patterns
4. Extract QuestionHelpText for failed items
5. Generate personalized coaching document

**Output**: Individual coaching plan document with her specific failures and behavioral criteria.

## Guidelines

### Data Quality Checks
- Verify date range makes sense (not future dates)
- Flag evaluations with 100% or 0% scores for review
- Check for duplicate EvaluationIds
- Validate Score ≤ MaxPoints for all rows

### Performance Tier Thresholds
These are configurable but defaults are:
- Exemplary: ≥95%
- Standard: 80-94%
- Development: 65-79%
- Critical: <65%

### Coaching Priority Rules
Prioritize coaching by:
1. Points at risk (high MaxPoints questions first)
2. Failure frequency (commonly missed)
3. Behavioral specificity (clear QuestionHelpText)
4. Skill buildability (can be trained vs. inherent traits)

### Calibration Intervention Triggers
- Standard Deviation > 15: Schedule calibration session
- Mean ±10% from team: Review scoring criteria understanding
- Sample size < 5: Increase evaluation volume before flagging

### Communication Tone
- Coaching-focused, not punitive
- Specific behavioral language
- Actionable recommendations
- Measurable success criteria

## When to Use This Skill

Invoke when user:
- Uploads Genesys evaluation_questions CSV export
- Asks about QA scores, quality metrics, evaluation results
- Requests coaching plans or performance improvement guidance
- Wants to identify training gaps or quality issues
- Asks about evaluator calibration or scoring consistency
- Needs QA dashboards or executive summaries
- References agents needing development or quality coaching

## Scripts Reference

The `/scripts` directory contains:
- `qa_parser.py`: CSV parsing and validation
- `performance_calculator.py`: Agent scoring and tiering
- `gap_analyzer.py`: Category and question-level analysis
- `coaching_generator.py`: Agent coaching plan creation
- `calibration_checker.py`: Evaluator consistency analysis
- `dashboard_builder.py`: HTML dashboard generation

## Resources Reference

The `/resources` directory contains:
- `question_criteria.md`: Full QuestionHelpText reference
- `tier_thresholds.md`: Performance tier configuration
- `calibration_standards.md`: Evaluator consistency benchmarks
- `coaching_templates.md`: Coaching plan format templates

---

**Created**: 2025-01-15  
**Organization**: ISPN iGLASS Tech Center  
**Scope**: Genesys Cloud QA evaluation analytics  
**Form Support**: Full Call Review, Auto-Evaluation, Focus Review

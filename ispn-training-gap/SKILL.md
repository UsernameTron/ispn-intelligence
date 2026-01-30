---
name: ispn-training-gap
description: |
  Training needs from QA failures, performance patterns, and quality-CSAT alignment.
  TRIGGERS: reviewreport*.csv, QA*.xlsx, Quality*.csv, "training gaps", "QA failures", "curriculum"
  Part of ISPN Workforce Intelligence Suite
---

# ISPN Training Gap

## FILE IDENTIFICATION

### Primary: reviewreport*.csv
- Columns: AgentID, EvaluationDate, Category, Score, FailureReason, EvaluatorID

### Secondary: QA*.xlsx, Quality*.csv
- Columns: AgentID, Period, OverallScore, CategoryScores, CriticalErrors

## FAILURE → CURRICULUM MAPPING

| Failure Category | Training Module | Delivery |
|------------------|-----------------|----------|
| Technical Knowledge | Product deep-dive | eLearning + lab |
| Process Adherence | Workflow refresher | Supervisor 1:1 |
| Soft Skills | Customer handling | Role-play + coaching |
| System Navigation | Tool proficiency | Hands-on lab |
| Documentation | Ticket quality | Examples + audit |
| Empowerment | Authority levels | Policy review |

## AGENT SEGMENTATION

| Gap Type | Indicator | Intervention | Timeline |
|----------|-----------|--------------|----------|
| Knowledge | Consistent category fails | Training module | 1-2 weeks |
| Skill | Knows but inconsistent | Practice/shadowing | 2-3 weeks |
| Behavior | Can but doesn't | Accountability + coaching | Immediate |

## QUALITY-CSAT ALIGNMENT

### Thresholds

| KPI | Target | Warning | Critical |
|-----|--------|---------|----------|
| Quality Score | > 88 | 85-88 | < 85 |
| CSAT | > 90% | 85-90% | < 85% |
| Quality-CSAT Gap | < 5 pts | 5-10 pts | > 10 pts |
| Evaluation Coverage | > 5% | 3-5% | < 3% |

### Alignment Analysis

```python
def quality_csat_alignment(quality_scores, csat_scores):
    correlation = pearsonr(quality_scores, csat_scores)
    gap = mean(quality_scores) - mean(csat_scores)
    
    if correlation < 0.5:
        return "CALIBRATION_NEEDED: QA criteria may not reflect CX"
    if abs(gap) > 10:
        return "GAP_ALERT: Quality and CSAT diverging"
    return "ALIGNED"
```

### Actions by Finding

| Finding | Action | Timeline |
|---------|--------|----------|
| Specific criteria failing | Targeted training module | 2 weeks |
| Calibration drift | QA calibration session | 1 week |
| Quality-CSAT gap | Criteria relevance review | 1 month |
| Agent outlier low | Individual coaching plan | Immediate |

## PATTERN ANALYSIS

```python
def identify_training_gaps(qa_data):
    category_fails = qa_data.groupby(['AgentID', 'Category']).count()
    patterns = {
        "technical_gap": category_fails['Technical'] > 2,
        "process_gap": category_fails['Process'] > 2,
        "soft_skills_gap": category_fails['Communication'] > 2,
        "systemic_training_need": category_fails.sum() > team_avg * 1.5
    }
    return patterns
```

## HANDOFFS

**Receives from:**
- ispn-agent-coaching: Bottom performers for skill gap analysis
- ispn-dpr-analysis: FCR decline correlation, escalation breakdown
- ispn-sentiment-analysis: Soft skills training needs
- ispn-skill-orchestrator: Query routing, file routing

**Sends to:**
- ispn-agent-coaching: Training recommendations for coaching plans
- ispn-skill-orchestrator: Curriculum recommendations

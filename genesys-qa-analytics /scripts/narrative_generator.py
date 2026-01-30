#!/usr/bin/env python3
"""
Genesys QA Analytics - Narrative Generator
Produces executive-ready markdown summaries from analysis results.
"""

from typing import Dict, List
from datetime import datetime


def generate_narrative(results: Dict) -> str:
    """
    Generate executive narrative summary from analysis results.
    
    Args:
        results: Output from GenesysQAAnalyzer.analyze()
    
    Returns:
        Markdown formatted narrative document
    """
    
    meta = results['metadata']
    tiers = results['tier_distribution']
    agents = results['agents']
    categories = results['categories']
    evaluators = results['evaluators']
    questions = results['questions']
    coaching_needed = results['coaching_needed']
    calibration_issues = results['calibration_issues']
    
    # Calculate key metrics
    total_agents = sum(tiers.values())
    pct_coaching = (len(coaching_needed) / total_agents * 100) if total_agents > 0 else 0
    
    # Get top failing questions (non-zero failure rate)
    top_failures = [q for q in questions if q['failure_rate'] > 0][:5]
    
    md = f"""# QA Performance Analysis Report

**Period:** {meta['date_range'][0]} to {meta['date_range'][1]}  
**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M')}

---

## Executive Summary

This report analyzes **{meta['evaluation_count']} quality evaluations** across **{meta['agent_count']} technicians** conducted by **{meta['evaluator_count']} QA analysts** during the reporting period.

**Team Performance:** {meta['team_average']}% average quality score

### Performance Distribution

| Tier | Count | Percentage | Action Required |
|------|-------|------------|-----------------|
| Exemplary (≥95%) | {tiers.get('Exemplary', 0)} | {(tiers.get('Exemplary', 0) / total_agents * 100):.1f}% | Recognition & mentorship |
| Standard (80-94%) | {tiers.get('Standard', 0)} | {(tiers.get('Standard', 0) / total_agents * 100):.1f}% | Maintenance coaching |
| Development (65-79%) | {tiers.get('Development', 0)} | {(tiers.get('Development', 0) / total_agents * 100):.1f}% | Targeted skill building |
| Critical (<65%) | {tiers.get('Critical', 0)} | {(tiers.get('Critical', 0) / total_agents * 100):.1f}% | Immediate intervention |

**Coaching Priority:** {len(coaching_needed)} agents ({pct_coaching:.1f}% of team) require active coaching intervention.

---

## Category Gap Analysis

Quality gaps by evaluation category, ranked by severity:

"""
    
    for i, cat in enumerate(categories[:6], 1):
        if 'Auto-Fail' in cat['name']:
            continue
        status = "🔴" if cat['gap_percentage'] > 20 else "🟡" if cat['gap_percentage'] > 10 else "🟢"
        md += f"{i}. **{cat['name']}** — {cat['gap_percentage']:.1f}% gap {status}\n"
        md += f"   - Success Rate: {cat['success_rate']:.1f}%\n"
        md += f"   - Points at Risk: {cat['points_at_risk']:.0f}\n\n"
    
    md += """---

## Priority Coaching Behaviors

The following behaviors have the highest failure rates and should be prioritized in team training:

"""
    
    for i, q in enumerate(top_failures, 1):
        md += f"""### {i}. {q['question_text']}

**Category:** {q['group_name']}  
**Failure Rate:** {q['failure_rate']}% ({q['fail_count']}/{q['total_count']} evaluations)  
**Points at Risk:** {q['max_points']} per evaluation ({q['points_lost']:.0f} total lost)

"""
        if q['help_text']:
            md += f"""**Behavioral Criteria:**
> {q['help_text'][:500]}{'...' if len(q['help_text'] or '') > 500 else ''}

"""
        md += f"""**Coaching Focus:** {"High priority - affects multiple agents" if q['failure_rate'] > 30 else "Moderate priority - targeted coaching needed" if q['failure_rate'] > 15 else "Low priority - monitor"}

---

"""
    
    md += """## Agents Requiring Coaching

"""
    
    if coaching_needed:
        md += """| Agent | Score | Tier | Eval Count | Primary Gap |
|-------|-------|------|------------|-------------|
"""
        for agent in coaching_needed:
            primary_gap = list(agent['failure_patterns'].keys())[0] if agent['failure_patterns'] else 'N/A'
            primary_gap = f"{primary_gap[:30]}..." if len(primary_gap) > 30 else primary_gap
            md += f"| {agent['name']} | {agent['avg_percentage']}% | {agent['tier']} | {agent['eval_count']} | {primary_gap} |\n"
    else:
        md += "*No agents currently require coaching intervention. All team members are performing at Standard or above.*\n"
    
    md += """

---

## Evaluator Calibration Status

"""
    
    if calibration_issues:
        md += """⚠️ **Calibration Concerns Identified**

The following evaluators show scoring patterns that may indicate calibration drift:

"""
        for e in calibration_issues:
            md += f"""- **{e['name']}** ({e['status']})
  - Average Score: {e['avg_score']}%
  - Standard Deviation: {e['std_dev'] if e['std_dev'] else 'N/A'}
  - Evaluation Count: {e['eval_count']}
  - Deviation from Team Norm: {e['deviation_from_norm']:+.1f}%

"""
        md += """**Recommended Actions:**
1. Schedule calibration session to review scoring criteria
2. Conduct side-by-side evaluation of same calls
3. Re-assess after 10 additional evaluations

"""
    else:
        md += """✅ **All Evaluators Calibrated**

All QA analysts are scoring within acceptable variance parameters.

| Evaluator | Avg Score | σ | Count | Status |
|-----------|-----------|---|-------|--------|
"""
        for e in evaluators:
            md += f"| {e['name']} | {e['avg_score']}% | {e['std_dev'] if e['std_dev'] else '—'} | {e['eval_count']} | {e['status']} |\n"
    
    md += """

---

## Recommended Actions

### Immediate (This Week)

"""
    
    # Generate specific recommendations based on data
    if tiers.get('Critical', 0) > 0:
        critical_agents = [a for a in agents if a['tier'] == 'Critical']
        md += f"1. **Schedule 1:1 coaching sessions** with {tiers.get('Critical', 0)} Critical-tier agents: "
        md += ", ".join([a['name'] for a in critical_agents[:3]])
        if len(critical_agents) > 3:
            md += f", and {len(critical_agents) - 3} others"
        md += "\n"
    
    if top_failures:
        top_behavior = top_failures[0]
        md += f"2. **Address top failing behavior** ({top_behavior['failure_rate']}% failure rate): {top_behavior['question_text'][:50]}...\n"
    
    if calibration_issues:
        md += f"3. **Schedule evaluator calibration session** for {len(calibration_issues)} QA analyst(s) showing variance\n"
    
    md += """
### Short-Term (Next 2 Weeks)

1. Review coaching plan progress for Development-tier agents
2. Conduct targeted training on top 3 failing behaviors
3. Re-evaluate agents who received coaching to measure improvement

### Long-Term (This Month)

1. Analyze month-over-month trends to validate coaching effectiveness
2. Update training materials based on persistent gaps
3. Recognize and leverage Exemplary-tier agents as mentors

---

## Form Distribution

Evaluations by form type:

"""
    
    for form, count in meta.get('form_distribution', {}).items():
        pct = (count / meta['evaluation_count'] * 100) if meta['evaluation_count'] > 0 else 0
        md += f"- **{form}**: {count} evaluations ({pct:.1f}%)\n"
    
    md += f"""

---

*Report generated by Genesys QA Analytics | ISPN iGLASS Tech Center*
"""
    
    return md


def generate_coaching_summary(results: Dict) -> str:
    """
    Generate focused coaching summary document.
    
    Args:
        results: Output from GenesysQAAnalyzer.analyze()
    
    Returns:
        Markdown coaching priorities document
    """
    
    coaching_needed = results['coaching_needed']
    questions = results['questions']
    
    if not coaching_needed:
        return "# Coaching Summary\n\n✅ All agents performing at Standard tier or above. No immediate coaching required."
    
    md = f"""# Coaching Priority Summary

**Agents Requiring Coaching:** {len(coaching_needed)}

---

## Agent Coaching Queue (Prioritized)

"""
    
    for i, agent in enumerate(coaching_needed, 1):
        md += f"""### {i}. {agent['name']}

**Current Score:** {agent['avg_percentage']}% | **Tier:** {agent['tier']} | **Target:** ≥80%

**Failure Patterns:**
"""
        if agent['failure_patterns']:
            for q, rate in list(agent['failure_patterns'].items())[:3]:
                # Find matching question for help text
                q_data = next((x for x in questions if x['question_text'] == q), None)
                md += f"\n- **{q[:50]}{'...' if len(q) > 50 else ''}** ({rate}% failure)\n"
                if q_data and q_data['help_text']:
                    md += f"  - *Coach on:* {q_data['help_text'][:150]}...\n"
        else:
            md += "\n- No specific failure patterns identified\n"
        
        md += f"""
**Coaching Plan:**
- [ ] Schedule 1:1 review session
- [ ] Review 3 call recordings demonstrating correct behaviors
- [ ] Role-play practice scenarios
- [ ] Re-evaluate in 2 weeks (minimum 3 calls)

---

"""
    
    return md


if __name__ == '__main__':
    # Test with sample data
    print("Narrative generator loaded successfully")

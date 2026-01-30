#!/usr/bin/env python3
"""
Routing Diagnostics Tool
Diagnoses skill mismatch issues by cross-referencing queue performance, agent status, and skills data.

Usage:
    python routing_diagnostics.py --queues queues.csv --agents agent_status.csv --skills skills_performance.csv
"""

import pandas as pd
import argparse
import sys
from pathlib import Path
from datetime import datetime


def load_data(queue_file, agent_file, skills_file):
    """Load all required data files."""
    data = {}
    
    try:
        data['queues'] = pd.read_csv(queue_file)
        print(f"✓ Loaded {len(data['queues'])} queue records")
    except Exception as e:
        print(f"✗ Error loading queue data: {e}")
        sys.exit(1)
    
    if agent_file:
        try:
            data['agents'] = pd.read_csv(agent_file)
            print(f"✓ Loaded {len(data['agents'])} agent records")
        except Exception as e:
            print(f"⚠ Warning: Could not load agent data: {e}")
            data['agents'] = None
    else:
        data['agents'] = None
    
    if skills_file:
        try:
            data['skills'] = pd.read_csv(skills_file)
            print(f"✓ Loaded {len(data['skills'])} skill group records")
        except Exception as e:
            print(f"⚠ Warning: Could not load skills data: {e}")
            data['skills'] = None
    else:
        data['skills'] = None
    
    return data


def detect_skill_mismatch(data):
    """Identify queues with potential skill mismatch issues."""
    queues_df = data['queues']
    
    # Indicators of skill mismatch:
    # 1. High average wait time (ASA > 120 seconds)
    # 2. Low service level (<70%)
    # 3. High occupancy variance (some agents idle, others overworked)
    
    mismatch_candidates = []
    
    for idx, row in queues_df.iterrows():
        queue_name = row.get('Queue Name', row.get('Queue', row.get('queueName', 'Unknown')))
        
        # Calculate mismatch indicators
        indicators = []
        confidence = 0
        
        # Check ASA (Average Speed of Answer)
        asa = row.get('Avg Speed of Answer', row.get('ASA', None))
        if asa and asa > 120:
            indicators.append(f"High ASA ({asa:.0f}s)")
            confidence += 2
        
        # Check Service Level
        sl = row.get('Service Level', row.get('Service Level %', row.get('SL %', None)))
        if sl and sl < 70:
            indicators.append(f"Low SL ({sl:.1f}%)")
            confidence += 2
        
        # Check Abandon Rate
        abandon_rate = None
        abandoned = row.get('Abandoned', row.get('tAbandoned', None))
        offered = row.get('Offered', row.get('tInteracting', None))
        if abandoned is not None and offered and offered > 0:
            abandon_rate = (abandoned / offered) * 100
            if abandon_rate > 10:
                indicators.append(f"High Abandons ({abandon_rate:.1f}%)")
                confidence += 1
        
        # Check for calls waiting indicator (if available)
        waiting = row.get('Waiting', row.get('Interactions Waiting', None))
        if waiting and waiting > 5:
            indicators.append(f"{waiting:.0f} calls waiting")
            confidence += 3  # Strong indicator of mismatch
        
        if confidence >= 3:  # Threshold for flagging
            mismatch_candidates.append({
                'queue': queue_name,
                'confidence': confidence,
                'indicators': indicators,
                'asa': asa if asa else 0,
                'service_level': sl if sl else 0,
                'abandon_rate': abandon_rate if abandon_rate else 0,
                'offered': offered if offered else 0
            })
    
    # Sort by confidence level
    mismatch_candidates.sort(key=lambda x: x['confidence'], reverse=True)
    
    return mismatch_candidates


def analyze_skill_performance(data):
    """Analyze performance by skill group to identify bottlenecks."""
    if data['skills'] is None:
        return []
    
    skills_df = data['skills']
    
    skill_issues = []
    
    for idx, row in skills_df.iterrows():
        skill_group = row.get('Skill Group', row.get('Skills', 'Unknown'))
        
        # Check for poor performance indicators
        asa = row.get('Avg Speed of Answer', row.get('ASA', None))
        sl = row.get('Service Level', row.get('Service Level %', None))
        offered = row.get('Offered', row.get('tInteracting', 0))
        
        issue_flags = []
        
        if asa and asa > 120:
            issue_flags.append(f"ASA {asa:.0f}s")
        
        if sl and sl < 70:
            issue_flags.append(f"SL {sl:.1f}%")
        
        if issue_flags and offered > 10:  # Only flag if reasonable volume
            skill_issues.append({
                'skill_group': skill_group,
                'issues': issue_flags,
                'asa': asa if asa else 0,
                'service_level': sl if sl else 0,
                'volume': offered
            })
    
    # Sort by worst ASA
    skill_issues.sort(key=lambda x: x['asa'], reverse=True)
    
    return skill_issues


def generate_recommendations(mismatch_candidates, skill_issues):
    """Generate actionable recommendations based on findings."""
    recommendations = []
    
    # Queue-specific recommendations
    if mismatch_candidates:
        recommendations.append({
            'category': 'Skill Mismatch',
            'priority': 'HIGH',
            'actions': [
                f"Review skill assignments for {len(mismatch_candidates)} queue(s) with mismatch indicators",
                "Check if agents with required skills are scheduled during peak hours",
                "Validate skill requirements in Architect flows (check for typos)",
                "Consider implementing bullseye routing to relax skill requirements after 30-60 seconds"
            ]
        })
    
    # Skill coverage recommendations
    if skill_issues:
        top_skill = skill_issues[0]['skill_group']
        recommendations.append({
            'category': 'Skill Coverage Gaps',
            'priority': 'MEDIUM',
            'actions': [
                f"Primary bottleneck: '{top_skill}' skill group",
                "Train additional agents on this skill set",
                "Review if all required skills in this group are truly necessary",
                "Consider cross-training from related skill groups"
            ]
        })
    
    # General routing recommendations
    recommendations.append({
        'category': 'Routing Configuration Review',
        'priority': 'MEDIUM',
        'actions': [
            "Review queue evaluation method (All Skills vs. Best Available)",
            "Check if proficiency ratings are up-to-date",
            "Validate bullseye ring configuration and timing",
            "Ensure language skills have adequate coverage"
        ]
    })
    
    return recommendations


def generate_report(mismatch_candidates, skill_issues, recommendations, output_file):
    """Generate diagnostic report."""
    with open(output_file, 'w') as f:
        f.write("# Genesys Routing Diagnostics Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Executive Summary
        f.write("## Executive Summary\n\n")
        f.write(f"**Potential Skill Mismatch Issues Detected:** {len(mismatch_candidates)}\n")
        f.write(f"**Skill Groups with Performance Issues:** {len(skill_issues)}\n\n")
        
        if mismatch_candidates:
            f.write("⚠️ **Action Required:** Multiple queues showing skill mismatch indicators.\n\n")
        else:
            f.write("✓ **No critical skill mismatch issues detected.**\n\n")
        
        f.write("---\n\n")
        
        # Skill Mismatch Details
        if mismatch_candidates:
            f.write("## 🔍 Queues with Skill Mismatch Indicators\n\n")
            f.write("Queues showing patterns consistent with skill coverage gaps:\n\n")
            f.write("| Queue | Confidence | Indicators | ASA (s) | SL% | Volume |\n")
            f.write("|-------|------------|------------|---------|-----|--------|\n")
            
            for item in mismatch_candidates:
                indicators_str = ", ".join(item['indicators'])
                f.write(f"| {item['queue']} | ")
                f.write(f"{'🔴' if item['confidence'] >= 5 else '🟡'} {item['confidence']}/7 | ")
                f.write(f"{indicators_str} | ")
                f.write(f"{item['asa']:.0f} | ")
                f.write(f"{item['service_level']:.1f}% | ")
                f.write(f"{item['offered']:,.0f} |\n")
            
            f.write("\n**Confidence Scale:**\n")
            f.write("- 🔴 5-7: High confidence of skill mismatch\n")
            f.write("- 🟡 3-4: Moderate indicators, investigate further\n\n")
        
        # Skill Performance Issues
        if skill_issues:
            f.write("---\n\n")
            f.write("## 📊 Skill Group Performance Issues\n\n")
            f.write("Skill groups with poor performance metrics:\n\n")
            f.write("| Skill Group | Issues | ASA (s) | SL% | Volume |\n")
            f.write("|-------------|--------|---------|-----|--------|\n")
            
            for item in skill_issues:
                issues_str = ", ".join(item['issues'])
                f.write(f"| {item['skill_group']} | ")
                f.write(f"{issues_str} | ")
                f.write(f"{item['asa']:.0f} | ")
                f.write(f"{item['service_level']:.1f}% | ")
                f.write(f"{item['volume']:,.0f} |\n")
            
            f.write("\n")
        
        # Recommendations
        f.write("---\n\n")
        f.write("## 📋 Recommendations\n\n")
        
        for rec in recommendations:
            f.write(f"### {rec['category']} ({rec['priority']} Priority)\n\n")
            for action in rec['actions']:
                f.write(f"- {action}\n")
            f.write("\n")
        
        # Diagnostic Checklist
        f.write("---\n\n")
        f.write("## ✅ Diagnostic Checklist\n\n")
        f.write("Follow these steps to investigate skill mismatch issues:\n\n")
        f.write("### 1. Validate Skill Requirements\n")
        f.write("- [ ] Review Architect flows for skill assignment logic\n")
        f.write("- [ ] Check for spelling errors in skill names (case-sensitive)\n")
        f.write("- [ ] Verify skills exist in Genesys (use Find Skill action)\n")
        f.write("- [ ] Confirm language skills are correctly assigned\n\n")
        
        f.write("### 2. Check Agent Skill Assignments\n")
        f.write("- [ ] List agents in affected queues\n")
        f.write("- [ ] Verify agents have all required skills\n")
        f.write("- [ ] Check skill proficiency ratings\n")
        f.write("- [ ] Review agents' on-queue status during issue periods\n\n")
        
        f.write("### 3. Review Routing Configuration\n")
        f.write("- [ ] Check queue evaluation method (All Skills / Best Available / Disregard)\n")
        f.write("- [ ] Review bullseye configuration (if enabled)\n")
        f.write("- [ ] Validate ring timers and skill relaxation settings\n")
        f.write("- [ ] Check for Preferred Agent or Last Agent routing overrides\n\n")
        
        f.write("### 4. Analyze Real-Time Data\n")
        f.write("- [ ] Monitor queue activity during peak hours\n")
        f.write("- [ ] Check for calls waiting while agents idle\n")
        f.write("- [ ] Review Skills Performance view for wait times by skill\n")
        f.write("- [ ] Use Agent Status view to see agent availability by skill\n\n")
        
        # Next Steps
        f.write("---\n\n")
        f.write("## 🎯 Next Steps\n\n")
        f.write("1. **Immediate:** Review top 3 queues flagged for skill mismatch\n")
        f.write("2. **This Week:** Validate skill assignments for affected queues\n")
        f.write("3. **This Month:** Implement bullseye routing where appropriate\n")
        f.write("4. **Ongoing:** Monitor skill performance metrics weekly\n\n")
    
    print(f"✓ Report generated: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Diagnose Genesys routing and skill mismatch issues'
    )
    parser.add_argument(
        '--queues',
        required=True,
        help='Path to Genesys queue performance CSV export'
    )
    parser.add_argument(
        '--agents',
        help='Path to Agent Status CSV export (optional)'
    )
    parser.add_argument(
        '--skills',
        help='Path to Skills Performance CSV export (optional)'
    )
    parser.add_argument(
        '--output',
        default='routing_diagnostics_report.md',
        help='Output report filename (default: routing_diagnostics_report.md)'
    )
    
    args = parser.parse_args()
    
    # Validate queue file exists
    if not Path(args.queues).exists():
        print(f"✗ Error: Queue file not found: {args.queues}")
        sys.exit(1)
    
    print("=" * 60)
    print("Routing Diagnostics Tool")
    print("=" * 60)
    print()
    
    # Load data
    data = load_data(args.queues, args.agents, args.skills)
    
    # Detect skill mismatch
    print("\nAnalyzing queue performance for skill mismatch indicators...")
    mismatch_candidates = detect_skill_mismatch(data)
    print(f"✓ Found {len(mismatch_candidates)} queue(s) with potential skill mismatch")
    
    # Analyze skill performance
    if data['skills'] is not None:
        print("\nAnalyzing skill group performance...")
        skill_issues = analyze_skill_performance(data)
        print(f"✓ Found {len(skill_issues)} skill group(s) with performance issues")
    else:
        print("\n⚠ Skipping skill group analysis (no skills data provided)")
        skill_issues = []
    
    # Generate recommendations
    recommendations = generate_recommendations(mismatch_candidates, skill_issues)
    
    # Generate report
    generate_report(mismatch_candidates, skill_issues, recommendations, args.output)
    
    print()
    print("=" * 60)
    print(f"Diagnostics complete!")
    print(f"Potential skill mismatches: {len(mismatch_candidates)}")
    print(f"Skill groups with issues: {len(skill_issues)}")
    print("=" * 60)


if __name__ == "__main__":
    main()

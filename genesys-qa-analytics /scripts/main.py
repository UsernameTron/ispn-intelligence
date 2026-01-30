#!/usr/bin/env python3
"""
Genesys QA Analytics - Main Entry Point
Complete analysis pipeline for Genesys Cloud QA evaluation exports.

Usage:
    python main.py <csv_path> [--output-dir OUTPUT_DIR] [--agent AGENT_NAME]
    
Examples:
    python main.py evaluation_questions.csv
    python main.py evaluation_questions.csv --output-dir ./reports
    python main.py evaluation_questions.csv --agent "John Smith"
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

from qa_analyzer import GenesysQAAnalyzer
from dashboard_builder import generate_dashboard
from narrative_generator import generate_narrative, generate_coaching_summary


def main():
    parser = argparse.ArgumentParser(
        description='Analyze Genesys QA evaluation exports and generate coaching intelligence'
    )
    parser.add_argument('csv_path', help='Path to Genesys evaluation_questions CSV export')
    parser.add_argument('--output-dir', '-o', default='./qa_reports', 
                        help='Output directory for generated reports')
    parser.add_argument('--agent', '-a', help='Generate coaching plan for specific agent')
    parser.add_argument('--json-only', action='store_true', 
                        help='Output only JSON data, no HTML/Markdown')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Suppress progress messages')
    
    args = parser.parse_args()
    
    # Validate input
    if not os.path.exists(args.csv_path):
        print(f"Error: File not found: {args.csv_path}")
        return 1
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run analysis
    if not args.quiet:
        print(f"Analyzing: {args.csv_path}")
    
    analyzer = GenesysQAAnalyzer(args.csv_path)
    results = analyzer.analyze()
    
    if not results['success']:
        print("Analysis failed:")
        for error in results.get('errors', []):
            print(f"  - {error}")
        return 1
    
    if not args.quiet:
        print(f"  ✓ {results['metadata']['evaluation_count']} evaluations")
        print(f"  ✓ {results['metadata']['agent_count']} agents")
        print(f"  ✓ {results['metadata']['evaluator_count']} evaluators")
    
    # Generate timestamp for filenames
    ts = datetime.now().strftime('%Y%m%d_%H%M')
    
    # Save JSON data
    json_path = output_dir / f'qa_analysis_{ts}.json'
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    if not args.quiet:
        print(f"  → JSON: {json_path}")
    
    if args.json_only:
        return 0
    
    # Generate specific agent coaching plan if requested
    if args.agent:
        if not args.quiet:
            print(f"\nGenerating coaching plan for: {args.agent}")
        plan = analyzer.generate_coaching_plan(args.agent)
        if plan:
            plan_path = output_dir / f'coaching_plan_{args.agent.replace(" ", "_")}_{ts}.md'
            with open(plan_path, 'w') as f:
                f.write(plan)
            print(f"  → Coaching Plan: {plan_path}")
        else:
            print(f"  ✗ Agent '{args.agent}' not found in data")
        return 0
    
    # Generate full report suite
    if not args.quiet:
        print("\nGenerating reports...")
    
    # HTML Dashboard
    dashboard_html = generate_dashboard(results)
    dashboard_path = output_dir / f'qa_dashboard_{ts}.html'
    with open(dashboard_path, 'w') as f:
        f.write(dashboard_html)
    if not args.quiet:
        print(f"  → Dashboard: {dashboard_path}")
    
    # Markdown Narrative
    narrative_md = generate_narrative(results)
    narrative_path = output_dir / f'qa_narrative_{ts}.md'
    with open(narrative_path, 'w') as f:
        f.write(narrative_md)
    if not args.quiet:
        print(f"  → Narrative: {narrative_path}")
    
    # Coaching Summary
    coaching_md = generate_coaching_summary(results)
    coaching_path = output_dir / f'coaching_summary_{ts}.md'
    with open(coaching_path, 'w') as f:
        f.write(coaching_md)
    if not args.quiet:
        print(f"  → Coaching Summary: {coaching_path}")
    
    # Generate individual coaching plans for Critical/Development agents
    coaching_needed = results.get('coaching_needed', [])
    if coaching_needed:
        coaching_dir = output_dir / 'coaching_plans'
        coaching_dir.mkdir(exist_ok=True)
        
        if not args.quiet:
            print(f"\nGenerating {len(coaching_needed)} individual coaching plans...")
        
        for agent in coaching_needed:
            plan = analyzer.generate_coaching_plan(agent['name'])
            if plan:
                safe_name = agent['name'].replace(' ', '_').replace('/', '-')
                plan_path = coaching_dir / f'{safe_name}_coaching_plan.md'
                with open(plan_path, 'w') as f:
                    f.write(plan)
                if not args.quiet:
                    print(f"  → {agent['name']}: {plan_path}")
    
    # Print summary
    if not args.quiet:
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)
        print(f"Team Average: {results['metadata']['team_average']}%")
        print(f"Tier Distribution:")
        for tier, count in results['tier_distribution'].items():
            print(f"  - {tier}: {count}")
        
        if coaching_needed:
            print(f"\n⚠️  {len(coaching_needed)} agents need coaching:")
            for agent in coaching_needed[:5]:
                print(f"  - {agent['name']} ({agent['avg_percentage']}% - {agent['tier']})")
            if len(coaching_needed) > 5:
                print(f"  ... and {len(coaching_needed) - 5} more")
        
        calibration_issues = results.get('calibration_issues', [])
        if calibration_issues:
            print(f"\n⚠️  {len(calibration_issues)} evaluators need calibration:")
            for e in calibration_issues:
                print(f"  - {e['name']} ({e['status']})")
        
        print(f"\nReports saved to: {output_dir.absolute()}")
    
    return 0


if __name__ == '__main__':
    exit(main())

#!/usr/bin/env python3
"""
Queue Health Analyzer
Analyzes Genesys queue performance data against targets and generates summary report.

Usage:
    python queue_health_analyzer.py --file queues_performance.csv --targets targets.json --output report.md
"""

import pandas as pd
import json
import argparse
import sys
from datetime import datetime
from pathlib import Path


def load_targets(targets_file):
    """Load target thresholds from JSON file."""
    if not targets_file:
        # Default ISPN targets
        return {
            "service_level_pct": 80.0,
            "abandon_rate_pct": 5.0,
            "avg_wait_time_sec": 90,
            "avg_handle_time_min": 10.7,
            "avg_speed_of_answer_sec": 60,
            "occupancy_pct": 75.0,
            "answer_rate_pct": 90.0
        }
    
    with open(targets_file, 'r') as f:
        return json.load(f)


def load_queue_data(queue_file):
    """Load Genesys queue performance data from CSV."""
    try:
        df = pd.read_csv(queue_file)
        print(f"✓ Loaded {len(df)} queue records from {queue_file}")
        return df
    except Exception as e:
        print(f"✗ Error loading queue data: {e}")
        sys.exit(1)


def standardize_column_names(df):
    """Standardize column names to match expected format."""
    # Common column name variations from Genesys exports
    column_mapping = {
        'Queue Name': 'queue_name',
        'queueName': 'queue_name',
        'Queue': 'queue_name',
        'Offered': 'offered',
        'tInteracting': 'offered',
        'Answered': 'answered',
        'tAnswered': 'answered',
        'Abandoned': 'abandoned',
        'tAbandoned': 'abandoned',
        'Service Level': 'service_level_pct',
        'Service Level %': 'service_level_pct',
        'SL %': 'service_level_pct',
        'Avg Wait Time': 'avg_wait_time_sec',
        'Average Wait Time': 'avg_wait_time_sec',
        'Avg Handle Time': 'avg_handle_time_min',
        'Average Handle Time': 'avg_handle_time_min',
        'AHT': 'avg_handle_time_min',
        'Avg Speed of Answer': 'avg_speed_of_answer_sec',
        'ASA': 'avg_speed_of_answer_sec',
        'Occupancy': 'occupancy_pct',
        'Occupancy %': 'occupancy_pct'
    }
    
    df_renamed = df.rename(columns=column_mapping)
    return df_renamed


def calculate_derived_metrics(df):
    """Calculate additional metrics from base data."""
    # Abandon rate
    if 'abandon_rate_pct' not in df.columns and 'abandoned' in df.columns and 'offered' in df.columns:
        df['abandon_rate_pct'] = (df['abandoned'] / df['offered'] * 100).fillna(0)
    
    # Answer rate
    if 'answer_rate_pct' not in df.columns and 'answered' in df.columns and 'offered' in df.columns:
        df['answer_rate_pct'] = (df['answered'] / df['offered'] * 100).fillna(0)
    
    return df


def flag_underperformers(df, targets):
    """Flag queues that don't meet target thresholds."""
    flags = []
    
    for idx, row in df.iterrows():
        queue_flags = []
        
        # Service level
        if 'service_level_pct' in row and row['service_level_pct'] < targets.get('service_level_pct', 80):
            variance = row['service_level_pct'] - targets['service_level_pct']
            queue_flags.append(f"SL {variance:+.1f}pp")
        
        # Abandon rate
        if 'abandon_rate_pct' in row and row['abandon_rate_pct'] > targets.get('abandon_rate_pct', 5):
            variance = row['abandon_rate_pct'] - targets['abandon_rate_pct']
            queue_flags.append(f"Abandon {variance:+.1f}pp")
        
        # Average wait time
        if 'avg_wait_time_sec' in row and row['avg_wait_time_sec'] > targets.get('avg_wait_time_sec', 90):
            variance = row['avg_wait_time_sec'] - targets['avg_wait_time_sec']
            queue_flags.append(f"AWT +{variance:.0f}s")
        
        # Average handle time
        if 'avg_handle_time_min' in row and row['avg_handle_time_min'] > targets.get('avg_handle_time_min', 10.7):
            variance = row['avg_handle_time_min'] - targets['avg_handle_time_min']
            queue_flags.append(f"AHT +{variance:.1f}m")
        
        # Occupancy
        if 'occupancy_pct' in row and row['occupancy_pct'] < targets.get('occupancy_pct', 75):
            variance = row['occupancy_pct'] - targets['occupancy_pct']
            queue_flags.append(f"Occ {variance:+.1f}pp")
        
        flags.append(" | ".join(queue_flags) if queue_flags else "✓ All targets met")
    
    df['performance_flags'] = flags
    return df


def generate_summary_stats(df, targets):
    """Generate summary statistics across all queues."""
    summary = {
        'total_queues': len(df),
        'total_offered': df['offered'].sum() if 'offered' in df.columns else 0,
        'total_answered': df['answered'].sum() if 'answered' in df.columns else 0,
        'total_abandoned': df['abandoned'].sum() if 'abandoned' in df.columns else 0,
        'avg_service_level': df['service_level_pct'].mean() if 'service_level_pct' in df.columns else 0,
        'avg_abandon_rate': df['abandon_rate_pct'].mean() if 'abandon_rate_pct' in df.columns else 0,
        'queues_missing_sl_target': len(df[df['service_level_pct'] < targets['service_level_pct']]) if 'service_level_pct' in df.columns else 0,
        'queues_exceeding_abandon_target': len(df[df['abandon_rate_pct'] > targets['abandon_rate_pct']]) if 'abandon_rate_pct' in df.columns else 0
    }
    return summary


def generate_markdown_report(df, targets, summary, output_file):
    """Generate markdown-formatted analysis report."""
    with open(output_file, 'w') as f:
        f.write("# Genesys Queue Performance Analysis Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Executive Summary
        f.write("## Executive Summary\n\n")
        f.write(f"**Total Queues Analyzed:** {summary['total_queues']}\n\n")
        f.write(f"**Total Volume:**\n")
        f.write(f"- Offered: {summary['total_offered']:,}\n")
        f.write(f"- Answered: {summary['total_answered']:,}\n")
        f.write(f"- Abandoned: {summary['total_abandoned']:,}\n\n")
        
        f.write(f"**Average Metrics:**\n")
        f.write(f"- Service Level: {summary['avg_service_level']:.1f}% (Target: {targets['service_level_pct']:.0f}%)\n")
        f.write(f"- Abandon Rate: {summary['avg_abandon_rate']:.1f}% (Target: <{targets['abandon_rate_pct']:.0f}%)\n\n")
        
        f.write(f"**Performance Gaps:**\n")
        f.write(f"- {summary['queues_missing_sl_target']} queue(s) below service level target\n")
        f.write(f"- {summary['queues_exceeding_abandon_target']} queue(s) above abandon rate target\n\n")
        
        f.write("---\n\n")
        
        # Underperforming Queues
        underperformers = df[df['performance_flags'] != "✓ All targets met"]
        
        if len(underperformers) > 0:
            f.write("## ⚠️ Queues Missing Targets\n\n")
            f.write("| Queue | Offered | SL% | Abandon% | AWT (s) | AHT (m) | Issues |\n")
            f.write("|-------|---------|-----|----------|---------|---------|--------|\n")
            
            for _, row in underperformers.iterrows():
                queue_name = row.get('queue_name', 'Unknown')
                offered = row.get('offered', 0)
                sl = row.get('service_level_pct', 0)
                abandon = row.get('abandon_rate_pct', 0)
                awt = row.get('avg_wait_time_sec', 0)
                aht = row.get('avg_handle_time_min', 0)
                flags = row['performance_flags']
                
                f.write(f"| {queue_name} | {offered:,.0f} | {sl:.1f}% | {abandon:.1f}% | {awt:.0f} | {aht:.1f} | {flags} |\n")
            
            f.write("\n")
        else:
            f.write("## ✓ All Queues Meeting Targets\n\n")
            f.write("No queues flagged for performance issues.\n\n")
        
        f.write("---\n\n")
        
        # Top Performers
        f.write("## 🏆 Top Performing Queues\n\n")
        if 'service_level_pct' in df.columns:
            top_performers = df.nlargest(5, 'service_level_pct')
            f.write("**By Service Level:**\n\n")
            f.write("| Rank | Queue | SL% | Offered | Abandon% |\n")
            f.write("|------|-------|-----|---------|----------|\n")
            
            for rank, (_, row) in enumerate(top_performers.iterrows(), 1):
                queue_name = row.get('queue_name', 'Unknown')
                sl = row.get('service_level_pct', 0)
                offered = row.get('offered', 0)
                abandon = row.get('abandon_rate_pct', 0)
                
                f.write(f"| {rank} | {queue_name} | {sl:.1f}% | {offered:,.0f} | {abandon:.1f}% |\n")
            
            f.write("\n")
        
        # Recommendations
        f.write("---\n\n")
        f.write("## 📋 Recommendations\n\n")
        
        if summary['queues_missing_sl_target'] > 0:
            f.write("### Service Level Gaps\n\n")
            f.write("**Action items:**\n")
            f.write("1. Review staffing levels during peak intervals\n")
            f.write("2. Check schedule adherence (are agents on queue as planned?)\n")
            f.write("3. Investigate skill mismatches (calls waiting despite idle agents)\n")
            f.write("4. Consider bullseye routing for skill relaxation\n\n")
        
        if summary['queues_exceeding_abandon_target'] > 0:
            f.write("### High Abandon Rates\n\n")
            f.write("**Action items:**\n")
            f.write("1. Implement or promote callback options\n")
            f.write("2. Increase staffing during abandon-heavy intervals\n")
            f.write("3. Review average abandon time (when do customers give up?)\n")
            f.write("4. Set customer expectations via IVR (estimated wait time)\n\n")
        
        f.write("---\n\n")
        f.write("## Target Thresholds Used\n\n")
        for metric, value in targets.items():
            f.write(f"- **{metric.replace('_', ' ').title()}:** {value}\n")
    
    print(f"✓ Report generated: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze Genesys queue performance data against targets'
    )
    parser.add_argument(
        '--file',
        required=True,
        help='Path to Genesys queue performance CSV export'
    )
    parser.add_argument(
        '--targets',
        help='Path to JSON file with target thresholds (optional, uses ISPN defaults if not provided)'
    )
    parser.add_argument(
        '--output',
        default='queue_health_report.md',
        help='Output report filename (default: queue_health_report.md)'
    )
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not Path(args.file).exists():
        print(f"✗ Error: File not found: {args.file}")
        sys.exit(1)
    
    print("=" * 60)
    print("Queue Health Analyzer")
    print("=" * 60)
    print()
    
    # Load targets
    targets = load_targets(args.targets)
    print(f"✓ Loaded targets (SL: {targets['service_level_pct']}%, Abandon: <{targets['abandon_rate_pct']}%)")
    
    # Load queue data
    df = load_queue_data(args.file)
    
    # Standardize column names
    df = standardize_column_names(df)
    
    # Calculate derived metrics
    df = calculate_derived_metrics(df)
    
    # Flag underperformers
    df = flag_underperformers(df, targets)
    
    # Generate summary statistics
    summary = generate_summary_stats(df, targets)
    
    # Generate report
    generate_markdown_report(df, targets, summary, args.output)
    
    print()
    print("=" * 60)
    print(f"Analysis complete!")
    print(f"Queues analyzed: {summary['total_queues']}")
    print(f"Queues below SL target: {summary['queues_missing_sl_target']}")
    print(f"Queues above abandon target: {summary['queues_exceeding_abandon_target']}")
    print("=" * 60)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Agent Performance Analysis
==========================

Analyze individual agent performance from HelpDesk ticket data.

Usage:
    python analyze_agent_performance.py --files "helpdesk_*.xls" --provider "Gateway Fiber"
    python analyze_agent_performance.py --files parsed_tickets.csv --min-tickets 10
"""

import pandas as pd
import argparse
import sys
from pathlib import Path

# Import parser utilities
try:
    from parse_tickets import load_tickets, parse_handle_time
except ImportError:
    print("Error: parse_tickets.py must be in same directory", file=sys.stderr)
    sys.exit(1)


def calculate_agent_stats(df, min_tickets=5):
    """
    Calculate comprehensive agent performance statistics.
    
    Args:
        df: Ticket DataFrame
        min_tickets: Minimum ticket count for inclusion
        
    Returns:
        DataFrame: Agent statistics
    """
    # Filter to valid tickets only
    valid = df[df['Handle_Min'] > 0].copy()
    
    # Calculate stats by agent
    stats = valid.groupby('Agent_Key').agg({
        'Handle_Min': ['count', 'mean', 'median', 'std'],
        'Is_Escalated': 'sum',
        'Is_Long_Call': 'sum',
        'Ticket': 'count'
    }).round(2)
    
    # Flatten column names
    stats.columns = ['Tickets', 'Avg_AHT', 'Median_AHT', 'AHT_StdDev', 
                     'Escalations', 'Long_Calls', 'Total_Tickets']
    
    # Calculate rates
    stats['Esc_Rate'] = (stats['Escalations'] / stats['Tickets'] * 100).round(1)
    stats['Long_Call_Rate'] = (stats['Long_Calls'] / stats['Tickets'] * 100).round(1)
    
    # Filter by minimum tickets
    stats = stats[stats['Tickets'] >= min_tickets]
    
    # Add agent names if available
    if 'Agent_Name' in df.columns:
        agent_names = df.groupby('Agent_Key')['Agent_Name'].first()
        stats['Agent_Name'] = stats.index.map(agent_names)
    
    return stats


def compare_to_peers(agent_stats, df):
    """
    Compare each agent to peer benchmarks.
    
    Args:
        agent_stats: Agent statistics DataFrame
        df: Full ticket DataFrame
        
    Returns:
        DataFrame: Agent stats with peer comparisons
    """
    # Calculate peer benchmarks by category
    peer_benchmarks = df[df['Handle_Min'] > 0].groupby('Category')['Handle_Min'].median()
    
    # For each agent, calculate deviation from benchmark
    deviations = []
    for agent in agent_stats.index:
        agent_tickets = df[df['Agent_Key'] == agent]
        
        # Calculate weighted average deviation
        total_deviation = 0
        total_weight = 0
        
        for category in agent_tickets['Category'].unique():
            cat_tickets = agent_tickets[agent_tickets['Category'] == category]
            cat_aht = cat_tickets['Handle_Min'].mean()
            cat_benchmark = peer_benchmarks.get(category, 0)
            cat_count = len(cat_tickets)
            
            if cat_benchmark > 0:
                deviation = cat_aht - cat_benchmark
                total_deviation += deviation * cat_count
                total_weight += cat_count
        
        if total_weight > 0:
            avg_deviation = total_deviation / total_weight
        else:
            avg_deviation = 0
        
        deviations.append(avg_deviation)
    
    agent_stats['Peer_Deviation'] = deviations
    agent_stats['Peer_Deviation'] = agent_stats['Peer_Deviation'].round(2)
    
    return agent_stats


def calculate_excess_minutes(agent_stats, df):
    """
    Calculate excess handle time minutes for each agent.
    
    Args:
        agent_stats: Agent statistics DataFrame
        df: Full ticket DataFrame
        
    Returns:
        DataFrame: Agent stats with excess minutes
    """
    # Calculate category benchmarks (median)
    benchmarks = df[df['Handle_Min'] > 0].groupby('Category')['Handle_Min'].median()
    
    # Calculate excess for each agent
    excess_list = []
    for agent in agent_stats.index:
        agent_tickets = df[df['Agent_Key'] == agent]
        
        total_excess = 0
        for _, ticket in agent_tickets.iterrows():
            if pd.notna(ticket['Handle_Min']) and ticket['Handle_Min'] > 0:
                benchmark = benchmarks.get(ticket['Category'], 0)
                if benchmark > 0:
                    excess = max(0, ticket['Handle_Min'] - benchmark)
                    total_excess += excess
        
        excess_list.append(total_excess)
    
    agent_stats['Excess_Min'] = excess_list
    agent_stats['Excess_Min'] = agent_stats['Excess_Min'].round(0)
    
    return agent_stats


def identify_outliers(agent_stats, std_threshold=1.5):
    """
    Identify agents with outlier performance (high or low).
    
    Args:
        agent_stats: Agent statistics DataFrame
        std_threshold: Number of std devs for outlier threshold
        
    Returns:
        dict: {'high_performers': DataFrame, 'concerns': DataFrame}
    """
    mean_aht = agent_stats['Avg_AHT'].mean()
    std_aht = agent_stats['Avg_AHT'].std()
    
    # High performers (significantly below average)
    high_perf_threshold = mean_aht - (std_threshold * std_aht)
    high_performers = agent_stats[agent_stats['Avg_AHT'] < high_perf_threshold]
    
    # Performance concerns (significantly above average)
    concern_threshold = mean_aht + (std_threshold * std_aht)
    concerns = agent_stats[agent_stats['Avg_AHT'] > concern_threshold]
    
    return {
        'high_performers': high_performers.sort_values('Avg_AHT'),
        'concerns': concerns.sort_values('Avg_AHT', ascending=False)
    }


def print_agent_report(agent_stats, outliers, df):
    """
    Print formatted agent performance report.
    """
    print("\n" + "="*80)
    print("AGENT PERFORMANCE ANALYSIS")
    print("="*80)
    
    print(f"\nTotal Agents Analyzed: {len(agent_stats)}")
    print(f"Date Range: {df['Date'].min()} to {df['Date'].max()}")
    
    # Overall statistics
    print("\n--- OVERALL STATISTICS ---")
    print(f"  Mean AHT: {agent_stats['Avg_AHT'].mean():.2f} min")
    print(f"  Median AHT: {agent_stats['Median_AHT'].median():.2f} min")
    print(f"  Mean Escalation Rate: {agent_stats['Esc_Rate'].mean():.1f}%")
    print(f"  Mean Long Call Rate: {agent_stats['Long_Call_Rate'].mean():.1f}%")
    
    # High performers
    if len(outliers['high_performers']) > 0:
        print("\n--- TOP PERFORMERS (Lowest AHT) ---")
        top_n = min(10, len(outliers['high_performers']))
        for idx, (agent, row) in enumerate(outliers['high_performers'].head(top_n).iterrows(), 1):
            name = row.get('Agent_Name', agent)
            print(f"  {idx:2}. {name:<25} {row['Avg_AHT']:>6.1f} min " +
                  f"({int(row['Tickets'])} tickets, {row['Esc_Rate']:.1f}% esc)")
    
    # Performance concerns
    if len(outliers['concerns']) > 0:
        print("\n--- PERFORMANCE CONCERNS (Highest AHT) ---")
        top_n = min(10, len(outliers['concerns']))
        for idx, (agent, row) in enumerate(outliers['concerns'].head(top_n).iterrows(), 1):
            name = row.get('Agent_Name', agent)
            print(f"  {idx:2}. {name:<25} {row['Avg_AHT']:>6.1f} min " +
                  f"({int(row['Tickets'])} tickets, {row['Esc_Rate']:.1f}% esc, " +
                  f"+{row['Peer_Deviation']:.1f} vs peers)")
    
    # Excess minutes
    if 'Excess_Min' in agent_stats.columns:
        print("\n--- TOP EXCESS MINUTE GENERATORS ---")
        top_excess = agent_stats.nlargest(10, 'Excess_Min')
        for idx, (agent, row) in enumerate(top_excess.iterrows(), 1):
            name = row.get('Agent_Name', agent)
            print(f"  {idx:2}. {name:<25} {int(row['Excess_Min']):>5} excess min " +
                  f"({int(row['Tickets'])} tickets)")
        
        # Calculate FTE impact
        total_excess = agent_stats['Excess_Min'].sum()
        fte_impact = total_excess / (40 * 60 * 0.55)  # Productive mins per FTE
        print(f"\n  Total Excess Minutes: {int(total_excess):,}")
        print(f"  FTE Equivalent: {fte_impact:.2f}")
    
    print("\n" + "="*80)


def analyze_by_category(df, agent_key, top_n=5):
    """
    Break down agent performance by category.
    
    Args:
        df: Ticket DataFrame
        agent_key: Agent identifier
        top_n: Number of top categories to show
        
    Returns:
        DataFrame: Category statistics for agent
    """
    agent_tickets = df[(df['Agent_Key'] == agent_key) & (df['Handle_Min'] > 0)]
    
    if len(agent_tickets) == 0:
        return None
    
    # Calculate category stats
    cat_stats = agent_tickets.groupby('Category').agg({
        'Handle_Min': ['count', 'mean', 'median']
    }).round(2)
    
    cat_stats.columns = ['Count', 'Avg_AHT', 'Median_AHT']
    
    # Calculate peer benchmark
    peer_benchmarks = df[df['Handle_Min'] > 0].groupby('Category')['Handle_Min'].median()
    cat_stats['Peer_Avg'] = cat_stats.index.map(peer_benchmarks).round(2)
    cat_stats['Deviation'] = (cat_stats['Avg_AHT'] - cat_stats['Peer_Avg']).round(2)
    
    # Sort by count
    cat_stats = cat_stats.sort_values('Count', ascending=False)
    
    return cat_stats


def main():
    parser = argparse.ArgumentParser(
        description="Analyze agent performance from HelpDesk tickets",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--files',
        nargs='+',
        required=True,
        help='Input file(s) - .xls exports or .csv from parse_tickets'
    )
    
    parser.add_argument(
        '--provider',
        help='Filter to specific provider'
    )
    
    parser.add_argument(
        '--min-tickets',
        type=int,
        default=5,
        help='Minimum tickets per agent (default: 5)'
    )
    
    parser.add_argument(
        '--output',
        help='Save detailed agent stats to CSV'
    )
    
    parser.add_argument(
        '--agent',
        help='Show detailed breakdown for specific agent'
    )
    
    args = parser.parse_args()
    
    # Load data
    file_pattern = args.files[0] if len(args.files) == 1 else args.files
    
    # Check if CSV (already parsed) or XLS (needs parsing)
    if isinstance(file_pattern, str) and file_pattern.endswith('.csv'):
        df = pd.read_csv(file_pattern)
        # Re-parse handle time if needed
        if 'Handle_Min' not in df.columns:
            df['Handle_Min'] = df['Handle Time'].apply(parse_handle_time)
    else:
        df = load_tickets(file_pattern)
    
    # Filter by provider if specified
    if args.provider:
        df = df[df['Provider'].str.contains(args.provider, case=False, na=False)]
        print(f"\nFiltered to provider: {args.provider}")
        print(f"Tickets: {len(df):,}")
    
    # Calculate agent statistics
    agent_stats = calculate_agent_stats(df, min_tickets=args.min_tickets)
    
    # Add peer comparisons
    agent_stats = compare_to_peers(agent_stats, df)
    
    # Calculate excess minutes
    agent_stats = calculate_excess_minutes(agent_stats, df)
    
    # Identify outliers
    outliers = identify_outliers(agent_stats)
    
    # Print report
    print_agent_report(agent_stats, outliers, df)
    
    # Detailed agent breakdown if requested
    if args.agent:
        print(f"\n\n{'='*80}")
        print(f"DETAILED BREAKDOWN: {args.agent}")
        print('='*80)
        
        cat_breakdown = analyze_by_category(df, args.agent)
        if cat_breakdown is not None:
            print("\nTop Categories:")
            print(cat_breakdown.head(10).to_string())
        else:
            print(f"No tickets found for agent: {args.agent}")
    
    # Save output if requested
    if args.output:
        agent_stats.to_csv(args.output)
        print(f"\n✓ Saved agent statistics to {args.output}")


if __name__ == '__main__':
    main()

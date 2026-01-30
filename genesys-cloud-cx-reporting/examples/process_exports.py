#!/usr/bin/env python3
"""
Genesys Cloud CX Export Processor
Calculates ISPN Tech Center KPIs from 4 standard exports.

Usage:
    python process_exports.py --interactions interactions.csv \
                              --agent-status agent_status.csv \
                              --adherence adherence.csv \
                              --agent-perf agent_performance.csv
"""

import pandas as pd
import argparse
from datetime import datetime


def load_interactions(filepath: str) -> pd.DataFrame:
    """Load and prepare Interactions export."""
    df = pd.read_csv(filepath)
    
    # Convert time fields to numeric (milliseconds)
    time_cols = ['Total Queue', 'Total Alert', 'Total Handle', 
                 'Total Talk', 'Total Hold', 'Total ACW']
    for col in time_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def load_agent_status(filepath: str) -> pd.DataFrame:
    """Load and prepare Agent Status Duration Details export."""
    df = pd.read_csv(filepath)
    
    # Convert time fields to numeric (milliseconds)
    time_cols = ['Logged In', 'On Queue', 'Off Queue', 'Training',
                 'Break', 'Meal', 'Meeting', 'Away', 'Interacting', 'Idle']
    for col in time_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def load_adherence(filepath: str) -> pd.DataFrame:
    """Load and prepare WFM Historical Adherence export."""
    df = pd.read_csv(filepath, encoding='utf-8-sig')
    
    # Convert adherence percentage strings to floats
    if 'Adherence (%)' in df.columns:
        df['Adherence_pct'] = df['Adherence (%)'].str.replace('%', '').astype(float)
    
    return df


def load_agent_performance(filepath: str) -> pd.DataFrame:
    """Load and prepare Agent Performance export."""
    df = pd.read_csv(filepath)
    
    # Convert numeric fields
    numeric_cols = ['Handle', 'Total Handle', 'Total Talk', 'Total Hold', 
                    'Total ACW', 'Avg Handle', 'Outbound']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def calculate_call_metrics(interactions: pd.DataFrame) -> dict:
    """Calculate call metrics from Interactions export."""
    
    # Filter definitions
    inbound = interactions[interactions['Direction'] == 'Inbound']
    inbound_handled = inbound[
        (inbound['Abandoned'] == 'NO') & 
        (inbound['Total Handle'] >= 20000)
    ]
    abandoned = inbound[
        (inbound['Abandoned'] == 'YES') & 
        (inbound['Total Queue'] >= 60000)
    ]
    outbound = interactions[
        (interactions['Direction'] == 'Outbound') & 
        (interactions['Media Type'] == 'voice')
    ]
    callbacks = interactions[interactions['Media Type'] == 'callback']
    
    # Calculate metrics
    metrics = {
        # Row 22: Inbound Call Count
        'inbound_count': len(inbound_handled),
        
        # Row 19: AHT (minutes)
        'aht_minutes': inbound_handled['Total Handle'].mean() / 60000,
        
        # Row 20: Inbound Call Minutes
        'inbound_minutes': inbound_handled['Total Handle'].sum() / 60000,
        
        # Row 21: Inbound Call Hours
        'inbound_hours': inbound_handled['Total Handle'].sum() / 3600000,
        
        # Row 23: AWT (seconds) - includes all offered
        'awt_seconds': inbound['Total Queue'].mean() / 1000,
        
        # Rows 24-27: Answer thresholds
        'answered_30s': (inbound_handled['Total Alert'] <= 30000).sum(),
        'answered_60s': (inbound_handled['Total Alert'] <= 60000).sum(),
        'answered_90s': (inbound_handled['Total Alert'] <= 90000).sum(),
        'answered_120s': (inbound_handled['Total Alert'] <= 120000).sum(),
        
        # Row 28: Abandoned (≥60s)
        'abandoned_count': len(abandoned),
        
        # Row 29: Outbound Count
        'outbound_count': len(outbound),
        
        # Row 30: Outbound Hours
        'outbound_hours': outbound['Total Handle'].sum() / 3600000,
        
        # Row 31: Callback Count
        'callback_count': len(callbacks),
        
        # Row 32: Callback Hours
        'callback_hours': callbacks['Total Handle'].sum() / 3600000,
        
        # Row 44: ACW Hours
        'acw_hours': inbound_handled['Total ACW'].sum() / 3600000,
        
        # AHT Decomposition
        'avg_talk_min': inbound_handled['Total Talk'].mean() / 60000,
        'avg_hold_min': inbound_handled['Total Hold'].mean() / 60000,
        'avg_acw_min': inbound_handled['Total ACW'].mean() / 60000,
    }
    
    return metrics


def calculate_workforce_metrics(agent_status: pd.DataFrame, 
                                call_metrics: dict) -> dict:
    """Calculate workforce metrics from Agent Status export."""
    
    # Filter to Tech Center
    tc = agent_status[agent_status['Department'] == 'Tech Center']
    
    # Row 59: Training Hours
    training_hours = tc['Training'].sum() / 3600000
    
    # Row 60: Total Hours Worked
    logged_in_hours = tc['Logged In'].sum() / 3600000
    
    # Row 61: Hours Worked (excl. training)
    hours_excl_training = logged_in_hours - training_hours
    
    # Row 62: On-Queue Hours
    on_queue_hours = tc['On Queue'].sum() / 3600000
    
    # Row 63: Shrinkage Hours
    shrinkage_hours = hours_excl_training - on_queue_hours
    
    # Shrinkage components
    break_hours = tc['Break'].sum() / 3600000
    meal_hours = tc['Meal'].sum() / 3600000
    meeting_hours = tc['Meeting'].sum() / 3600000
    
    metrics = {
        # Row 59
        'training_hours': training_hours,
        
        # Row 60
        'total_hours_worked': logged_in_hours,
        
        # Row 61
        'hours_excl_training': hours_excl_training,
        
        # Row 62
        'on_queue_hours': on_queue_hours,
        
        # Row 63
        'shrinkage_hours': shrinkage_hours,
        
        # Row 64: % Shrinkage
        'shrinkage_pct': (shrinkage_hours / hours_excl_training * 100) 
                         if hours_excl_training > 0 else 0,
        
        # Row 66: Utilization
        'utilization_pct': (call_metrics['inbound_hours'] / hours_excl_training * 100)
                           if hours_excl_training > 0 else 0,
        
        # Row 67: Occupancy
        'occupancy_pct': ((call_metrics['inbound_hours'] + 
                          call_metrics['outbound_hours'] + 
                          call_metrics['callback_hours']) / on_queue_hours * 100)
                         if on_queue_hours > 0 else 0,
        
        # Shrinkage breakdown
        'break_hours': break_hours,
        'meal_hours': meal_hours,
        'meeting_hours': meeting_hours,
        
        # Agent count
        'agent_count': len(tc),
    }
    
    return metrics


def calculate_adherence_metrics(adherence: pd.DataFrame) -> dict:
    """Calculate adherence metrics from WFM export."""
    
    # Filter out invalid conformance
    valid = adherence[~adherence['Conformance (%)'].str.contains('Infinity', na=False)]
    
    metrics = {
        'agent_count': len(adherence),
        'mean_adherence': adherence['Adherence_pct'].mean(),
        'min_adherence': adherence['Adherence_pct'].min(),
        'max_adherence': adherence['Adherence_pct'].max(),
        'total_exceptions': adherence['Exceptions'].sum(),
        'total_exception_hours': adherence['Exceptions Duration Minutes'].sum() / 60,
    }
    
    return metrics


def generate_report(call_metrics: dict, 
                   workforce_metrics: dict, 
                   adherence_metrics: dict) -> str:
    """Generate formatted KPI report."""
    
    report = f"""
================================================================================
                    ISPN TECH CENTER PERFORMANCE REPORT
                    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================================================================

CALL METRICS
------------
Inbound Handled Calls (≥20s):     {call_metrics['inbound_count']:,}
Inbound Call Hours:               {call_metrics['inbound_hours']:.2f}
AHT (minutes):                    {call_metrics['aht_minutes']:.2f}  (Target: < 10.7)
AWT (seconds):                    {call_metrics['awt_seconds']:.2f}  (Target: < 90)

Answer Speed Distribution:
  Answered ≤30s:                  {call_metrics['answered_30s']:,}
  Answered ≤60s:                  {call_metrics['answered_60s']:,}
  Answered ≤90s:                  {call_metrics['answered_90s']:,}
  Answered ≤120s:                 {call_metrics['answered_120s']:,}

Abandoned Calls (≥60s):           {call_metrics['abandoned_count']:,}

Outbound Calls:                   {call_metrics['outbound_count']:,}
Outbound Hours:                   {call_metrics['outbound_hours']:.2f}

Callbacks:                        {call_metrics['callback_count']:,}
Callback Hours:                   {call_metrics['callback_hours']:.2f}

AHT Decomposition:
  Avg Talk:                       {call_metrics['avg_talk_min']:.2f} min
  Avg Hold:                       {call_metrics['avg_hold_min']:.2f} min
  Avg ACW:                        {call_metrics['avg_acw_min']:.2f} min

WORKFORCE METRICS
-----------------
Tech Center Agent Count:          {workforce_metrics['agent_count']}

Time Allocation:
  Total Hours Worked:             {workforce_metrics['total_hours_worked']:.2f}
  Training Hours:                 {workforce_metrics['training_hours']:.2f}
  Hours Worked (excl. training):  {workforce_metrics['hours_excl_training']:.2f}
  On-Queue Hours:                 {workforce_metrics['on_queue_hours']:.2f}

Shrinkage Breakdown:
  Shrinkage Hours:                {workforce_metrics['shrinkage_hours']:.2f}
  % Shrinkage:                    {workforce_metrics['shrinkage_pct']:.1f}%  (Target: ≤ 20%)
  - Break:                        {workforce_metrics['break_hours']:.2f} hrs
  - Meal:                         {workforce_metrics['meal_hours']:.2f} hrs
  - Meeting:                      {workforce_metrics['meeting_hours']:.2f} hrs

Efficiency Metrics:
  Utilization:                    {workforce_metrics['utilization_pct']:.1f}%  (Target: > 55%)
  Occupancy:                      {workforce_metrics['occupancy_pct']:.1f}%  (Target: > 75%)

WFM ADHERENCE
-------------
Agents in WFM:                    {adherence_metrics['agent_count']}
Mean Adherence:                   {adherence_metrics['mean_adherence']:.1f}%
Adherence Range:                  {adherence_metrics['min_adherence']:.1f}% - {adherence_metrics['max_adherence']:.1f}%
Total Exceptions:                 {adherence_metrics['total_exceptions']:,}
Total Exception Hours:            {adherence_metrics['total_exception_hours']:.2f}

================================================================================
"""
    return report


def main():
    parser = argparse.ArgumentParser(description='Process Genesys Cloud CX exports')
    parser.add_argument('--interactions', required=True, help='Interactions CSV file')
    parser.add_argument('--agent-status', required=True, help='Agent Status CSV file')
    parser.add_argument('--adherence', required=True, help='WFM Adherence CSV file')
    parser.add_argument('--agent-perf', help='Agent Performance CSV file (optional)')
    parser.add_argument('--output', help='Output file for report')
    
    args = parser.parse_args()
    
    # Load data
    print("Loading Interactions export...")
    interactions = load_interactions(args.interactions)
    
    print("Loading Agent Status export...")
    agent_status = load_agent_status(args.agent_status)
    
    print("Loading WFM Adherence export...")
    adherence = load_adherence(args.adherence)
    
    # Calculate metrics
    print("Calculating call metrics...")
    call_metrics = calculate_call_metrics(interactions)
    
    print("Calculating workforce metrics...")
    workforce_metrics = calculate_workforce_metrics(agent_status, call_metrics)
    
    print("Calculating adherence metrics...")
    adherence_metrics = calculate_adherence_metrics(adherence)
    
    # Generate report
    report = generate_report(call_metrics, workforce_metrics, adherence_metrics)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to {args.output}")
    else:
        print(report)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Interval Comparison Tool
Compares actual intraday queue performance vs. WFM forecast to detect real-time issues.

Usage:
    python interval_comparison.py --actual intraday_actual.csv --forecast wfm_forecast.csv --threshold 0.2
"""

import pandas as pd
import argparse
import sys
from pathlib import Path
from datetime import datetime


def load_intraday_data(actual_file, forecast_file):
    """Load actual and forecast data."""
    data = {}
    
    try:
        data['actual'] = pd.read_csv(actual_file)
        print(f"✓ Loaded {len(data['actual'])} actual intervals")
    except Exception as e:
        print(f"✗ Error loading actual data: {e}")
        sys.exit(1)
    
    try:
        data['forecast'] = pd.read_csv(forecast_file)
        print(f"✓ Loaded {len(data['forecast'])} forecast intervals")
    except Exception as e:
        print(f"✗ Error loading forecast data: {e}")
        sys.exit(1)
    
    return data


def standardize_columns(df, data_type):
    """Standardize column names for actual vs. forecast data."""
    if data_type == 'actual':
        column_mapping = {
            'Interval': 'interval',
            'Interval Start': 'interval',
            'Offered': 'offered',
            'Answered': 'answered',
            'Service Level': 'service_level',
            'Service Level %': 'service_level',
            'Avg Handle Time': 'aht',
            'AHT': 'aht',
            'Agents On Queue': 'agents',
            'Staffed': 'agents'
        }
    else:  # forecast
        column_mapping = {
            'Interval': 'interval',
            'Interval Start': 'interval',
            'Forecast Offered': 'forecast_offered',
            'Forecast AHT': 'forecast_aht',
            'Required Agents': 'forecast_agents',
            'Forecast Agents': 'forecast_agents'
        }
    
    return df.rename(columns=column_mapping)


def merge_data(actual_df, forecast_df):
    """Merge actual and forecast data by interval."""
    # Ensure interval columns are same type
    actual_df['interval'] = pd.to_datetime(actual_df['interval'])
    forecast_df['interval'] = pd.to_datetime(forecast_df['interval'])
    
    # Merge on interval
    merged = pd.merge(
        actual_df,
        forecast_df,
        on='interval',
        how='outer',
        suffixes=('_actual', '_forecast')
    )
    
    return merged


def calculate_variances(df, threshold):
    """Calculate variances between actual and forecast."""
    # Volume variance
    if 'offered' in df.columns and 'forecast_offered' in df.columns:
        df['volume_variance_pct'] = ((df['offered'] - df['forecast_offered']) / df['forecast_offered'] * 100).fillna(0)
        df['volume_variance_flag'] = (abs(df['volume_variance_pct']) > threshold * 100).astype(int)
    
    # AHT variance
    if 'aht' in df.columns and 'forecast_aht' in df.columns:
        df['aht_variance_pct'] = ((df['aht'] - df['forecast_aht']) / df['forecast_aht'] * 100).fillna(0)
        df['aht_variance_flag'] = (abs(df['aht_variance_pct']) > threshold * 100).astype(int)
    
    # Agent variance
    if 'agents' in df.columns and 'forecast_agents' in df.columns:
        df['agent_variance'] = (df['agents'] - df['forecast_agents']).fillna(0)
        df['agent_variance_flag'] = (abs(df['agent_variance']) >= 2).astype(int)
    
    # Service level flag
    if 'service_level' in df.columns:
        df['sl_flag'] = (df['service_level'] < 80).astype(int)
    
    # Overall concern level
    df['concern_level'] = (
        df.get('volume_variance_flag', 0) +
        df.get('aht_variance_flag', 0) +
        df.get('agent_variance_flag', 0) +
        df.get('sl_flag', 0)
    )
    
    return df


def identify_root_causes(df):
    """Identify root cause for each flagged interval."""
    root_causes = []
    
    for idx, row in df.iterrows():
        if row['concern_level'] == 0:
            continue
        
        causes = []
        
        # Volume spike
        if row.get('volume_variance_pct', 0) > 15:
            causes.append(f"Volume spike ({row['volume_variance_pct']:+.1f}%)")
        elif row.get('volume_variance_pct', 0) < -15:
            causes.append(f"Volume drop ({row['volume_variance_pct']:+.1f}%)")
        
        # AHT increase
        if row.get('aht_variance_pct', 0) > 10:
            causes.append(f"AHT elevated ({row['aht_variance_pct']:+.1f}%)")
        
        # Understaffing
        if row.get('agent_variance', 0) < -1:
            causes.append(f"{abs(row['agent_variance']):.0f} fewer agents than planned")
        
        # Service level miss
        if row.get('sl_flag', 0) == 1:
            sl = row.get('service_level', 0)
            causes.append(f"SL {sl:.1f}% (below 80%)")
        
        root_causes.append({
            'interval': row['interval'],
            'concern_level': row['concern_level'],
            'causes': causes
        })
    
    return root_causes


def generate_recommendations(root_causes):
    """Generate interval-specific recommendations."""
    recommendations = []
    
    # Categorize issues
    volume_spikes = []
    aht_issues = []
    staffing_gaps = []
    
    for item in root_causes:
        for cause in item['causes']:
            if 'Volume spike' in cause:
                volume_spikes.append(item)
            elif 'AHT elevated' in cause:
                aht_issues.append(item)
            elif 'fewer agents' in cause:
                staffing_gaps.append(item)
    
    # Volume spike recommendations
    if volume_spikes:
        recommendations.append({
            'category': 'Volume Variance',
            'intervals_affected': len(volume_spikes),
            'actions': [
                "Check for unexpected events (marketing campaign, system outage, holiday impact)",
                "Update future forecasts if volume pattern continues",
                "Consider authorizing overtime for next similar interval",
                "Implement proactive callback offers during high volume"
            ]
        })
    
    # AHT recommendations
    if aht_issues:
        recommendations.append({
            'category': 'Handle Time Increase',
            'intervals_affected': len(aht_issues),
            'actions': [
                "Review HelpDesk tickets for this period (check for complex issue spike)",
                "Check if new issue types emerged requiring longer handling",
                "Verify agents have access to knowledge base and tools",
                "Consider brief team huddle to share handling tips if pattern continues"
            ]
        })
    
    # Staffing recommendations
    if staffing_gaps:
        recommendations.append({
            'category': 'Staffing Shortfall',
            'intervals_affected': len(staffing_gaps),
            'actions': [
                "Check schedule adherence (were agents on queue as planned?)",
                "Review for unplanned absences or late arrivals",
                "Pull agents from back-office tasks if available",
                "Adjust future schedules if gap is recurring pattern"
            ]
        })
    
    return recommendations


def generate_report(df, root_causes, recommendations, threshold, output_file):
    """Generate interval comparison report."""
    with open(output_file, 'w') as f:
        f.write("# Intraday Performance vs. Forecast Analysis\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Variance Threshold:** {threshold * 100:.0f}%\n\n")
        f.write("---\n\n")
        
        # Executive Summary
        total_intervals = len(df)
        flagged_intervals = len(root_causes)
        
        f.write("## Executive Summary\n\n")
        f.write(f"**Total Intervals Analyzed:** {total_intervals}\n")
        f.write(f"**Intervals Flagged:** {flagged_intervals} ({flagged_intervals/total_intervals*100:.1f}%)\n\n")
        
        if flagged_intervals > 0:
            avg_concern = sum(item['concern_level'] for item in root_causes) / flagged_intervals
            f.write(f"**Average Concern Level:** {avg_concern:.1f}/4\n\n")
            f.write("⚠️ **Significant variances detected requiring attention**\n\n")
        else:
            f.write("✓ **All intervals within acceptable variance**\n\n")
        
        f.write("---\n\n")
        
        # Flagged Intervals Detail
        if root_causes:
            f.write("## 🚨 Flagged Intervals\n\n")
            f.write("Intervals where actual performance significantly deviated from forecast:\n\n")
            f.write("| Time | Concern Level | Root Causes |\n")
            f.write("|------|--------------|-------------|\n")
            
            for item in root_causes:
                time_str = item['interval'].strftime('%H:%M')
                concern_emoji = ['', '🟡', '🟠', '🔴', '🔴'][min(item['concern_level'], 4)]
                causes_str = "; ".join(item['causes'])
                
                f.write(f"| {time_str} | {concern_emoji} {item['concern_level']}/4 | {causes_str} |\n")
            
            f.write("\n**Concern Level Legend:**\n")
            f.write("- 1: Minor variance (monitor)\n")
            f.write("- 2: Moderate variance (investigate)\n")
            f.write("- 3: Significant variance (take action)\n")
            f.write("- 4: Critical variance (immediate intervention)\n\n")
        
        # Variance Summary
        f.write("---\n\n")
        f.write("## 📊 Variance Summary\n\n")
        
        # Volume variance
        if 'volume_variance_pct' in df.columns:
            avg_vol_var = df['volume_variance_pct'].mean()
            max_vol_var = df['volume_variance_pct'].max()
            min_vol_var = df['volume_variance_pct'].min()
            
            f.write("### Call Volume\n")
            f.write(f"- Average variance: {avg_vol_var:+.1f}%\n")
            f.write(f"- Largest overforecast: {min_vol_var:+.1f}% (fewer calls than expected)\n")
            f.write(f"- Largest underforecast: {max_vol_var:+.1f}% (more calls than expected)\n\n")
        
        # AHT variance
        if 'aht_variance_pct' in df.columns:
            avg_aht_var = df['aht_variance_pct'].mean()
            f.write("### Average Handle Time\n")
            f.write(f"- Average variance: {avg_aht_var:+.1f}%\n")
            
            if avg_aht_var > 5:
                f.write(f"⚠️ AHT consistently higher than forecast (may need more agents)\n\n")
            elif avg_aht_var < -5:
                f.write(f"✓ AHT better than forecast (agents efficient)\n\n")
            else:
                f.write(f"✓ AHT tracking closely to forecast\n\n")
        
        # Agent staffing
        if 'agent_variance' in df.columns:
            avg_agent_var = df['agent_variance'].mean()
            f.write("### Staffing Levels\n")
            f.write(f"- Average variance: {avg_agent_var:+.1f} agents\n")
            
            if avg_agent_var < -0.5:
                f.write(f"⚠️ Consistent understaffing (adherence issue or forecast gap)\n\n")
            elif avg_agent_var > 0.5:
                f.write(f"ℹ️ Slightly overstaffed on average\n\n")
            else:
                f.write(f"✓ Staffing tracking to plan\n\n")
        
        # Recommendations
        if recommendations:
            f.write("---\n\n")
            f.write("## 📋 Recommended Actions\n\n")
            
            for rec in recommendations:
                f.write(f"### {rec['category']} ({rec['intervals_affected']} interval(s) affected)\n\n")
                for action in rec['actions']:
                    f.write(f"- {action}\n")
                f.write("\n")
        
        # Interval-by-Interval Data
        f.write("---\n\n")
        f.write("## 📈 Interval Details\n\n")
        f.write("| Time | Offered | Forecast | Var% | Agents | Forecast | Var | SL% |\n")
        f.write("|------|---------|----------|------|--------|----------|-----|-----|\n")
        
        for _, row in df.iterrows():
            time_str = row['interval'].strftime('%H:%M')
            offered = row.get('offered', 0)
            forecast_offered = row.get('forecast_offered', 0)
            vol_var = row.get('volume_variance_pct', 0)
            agents = row.get('agents', 0)
            forecast_agents = row.get('forecast_agents', 0)
            agent_var = row.get('agent_variance', 0)
            sl = row.get('service_level', 0)
            
            # Flag significant variances
            vol_flag = '⚠️' if abs(vol_var) > threshold * 100 else ''
            agent_flag = '⚠️' if abs(agent_var) >= 2 else ''
            sl_flag = '⚠️' if sl < 80 else ''
            
            f.write(f"| {time_str} | ")
            f.write(f"{offered:.0f} | {forecast_offered:.0f} | {vol_flag}{vol_var:+.1f}% | ")
            f.write(f"{agents:.0f} | {forecast_agents:.0f} | {agent_flag}{agent_var:+.0f} | ")
            f.write(f"{sl_flag}{sl:.1f}% |\n")
        
        f.write("\n")
        
        # Next Steps
        f.write("---\n\n")
        f.write("## 🎯 Next Steps\n\n")
        f.write("1. **Immediate:** Review intervals with concern level 3-4\n")
        f.write("2. **Today:** Investigate root causes for flagged intervals\n")
        f.write("3. **This Week:** Adjust tomorrow's staffing if patterns continue\n")
        f.write("4. **Ongoing:** Update forecast model if consistent variances detected\n\n")
    
    print(f"✓ Report generated: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Compare actual intraday performance vs. forecast'
    )
    parser.add_argument(
        '--actual',
        required=True,
        help='Path to intraday actual performance CSV'
    )
    parser.add_argument(
        '--forecast',
        required=True,
        help='Path to WFM forecast CSV'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.2,
        help='Variance threshold for flagging (default: 0.2 = 20%%)'
    )
    parser.add_argument(
        '--output',
        default='interval_comparison_report.md',
        help='Output report filename'
    )
    
    args = parser.parse_args()
    
    # Validate files exist
    if not Path(args.actual).exists():
        print(f"✗ Error: Actual file not found: {args.actual}")
        sys.exit(1)
    
    if not Path(args.forecast).exists():
        print(f"✗ Error: Forecast file not found: {args.forecast}")
        sys.exit(1)
    
    print("=" * 60)
    print("Interval Comparison Tool")
    print("=" * 60)
    print()
    
    # Load data
    data = load_intraday_data(args.actual, args.forecast)
    
    # Standardize columns
    data['actual'] = standardize_columns(data['actual'], 'actual')
    data['forecast'] = standardize_columns(data['forecast'], 'forecast')
    
    # Merge data
    print("\nMerging actual and forecast data by interval...")
    merged_df = merge_data(data['actual'], data['forecast'])
    print(f"✓ Merged {len(merged_df)} intervals")
    
    # Calculate variances
    print(f"\nCalculating variances (threshold: {args.threshold*100:.0f}%)...")
    merged_df = calculate_variances(merged_df, args.threshold)
    
    # Identify root causes
    print("\nIdentifying root causes for flagged intervals...")
    root_causes = identify_root_causes(merged_df)
    print(f"✓ Found {len(root_causes)} interval(s) with significant variances")
    
    # Generate recommendations
    recommendations = generate_recommendations(root_causes)
    
    # Generate report
    generate_report(merged_df, root_causes, recommendations, args.threshold, args.output)
    
    print()
    print("=" * 60)
    print(f"Analysis complete!")
    print(f"Intervals analyzed: {len(merged_df)}")
    print(f"Intervals flagged: {len(root_causes)}")
    print("=" * 60)


if __name__ == "__main__":
    main()

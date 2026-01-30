"""
ISPN File Parsers
Parse Genesys Cloud exports into structured JSON

VALIDATED AGAINST ACTUAL GENESYS EXPORTS (Jan 2026):
- Interactions export: 25 columns, times in milliseconds
- Agent Performance Summary: 32 columns, times in milliseconds  
- Agent Status Summary: 24 columns, times in milliseconds, percentages as decimals
- Skills Performance: 24 columns, percentages as decimals
- Historical Adherence: 13 columns, percentages with % sign, times in MINUTES
- WFM Scheduled/Required: 11 columns, 15-minute intervals
- WFM Activities: 9 columns, activity codes
- Agent Schedules: 11 columns, agent configuration
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import re


# =============================================================================
# GENESYS FIELD MAPPINGS (VALIDATED FROM ACTUAL EXPORTS)
# =============================================================================

# Interactions Export (Performance → Workspace → Interactions)
INTERACTIONS_COLUMNS = {
    'full_export': 'Full Export Completed',
    'partial_timestamp': 'Partial Result Timestamp',
    'filters': 'Filters',
    'media_type': 'Media Type',
    'agent': 'Users - Interacted',
    'date': 'Date',
    'direction': 'Direction',
    'queue': 'Queue',
    'wrapup': 'Wrap-up',
    'conversation_id': 'Conversation ID',
    'transferred': 'Transferred',
    'abandoned': 'Abandoned',
    'non_acd': 'Non-ACD',
    'first_queue': 'First Queue',
    'disconnect_type': 'Disconnect Type',
    'flowout_type': 'Flow-Out Type',
    'skills': 'Skills',
    'routing_used': 'Routing Used',
    'total_queue': 'Total Queue',      # milliseconds - wait time
    'total_alert': 'Total Alert',      # milliseconds - ring time
    'total_talk': 'Total Talk',        # milliseconds
    'total_hold': 'Total Hold',        # milliseconds
    'total_acw': 'Total ACW',          # milliseconds - 15000 = timeout
    'total_handle': 'Total Handle',    # milliseconds = talk + hold + acw
    'transfers': 'Transfers',
}

# Agent Performance Summary (Performance → Workspace → Agents Performance)
AGENT_PERF_COLUMNS = {
    'interval_start': 'Interval Start',
    'interval_end': 'Interval End',
    'agent_id': 'Agent Id',
    'agent_name': 'Agent Name',
    'email': 'Email',
    'handle_count': 'Handle',
    'avg_handle': 'Avg Handle',        # milliseconds
    'avg_talk': 'Avg Talk',            # milliseconds
    'avg_hold': 'Avg Hold',            # milliseconds
    'avg_acw': 'Avg ACW',              # milliseconds
    'asa': 'ASA',                      # milliseconds
    'total_handle': 'Total Handle',    # milliseconds
    'total_talk': 'Total Talk',        # milliseconds
    'total_hold': 'Total Hold',        # milliseconds
    'total_acw': 'Total ACW',          # milliseconds
    'held_count': 'Held',
    'transferred': 'Transferred',
    'outbound': 'Outbound',
    'department': 'Department',
    'title': 'Title',
}

# Agent Status Summary (Performance → Contact Center → Agent Status)
AGENT_STATUS_COLUMNS = {
    'interval_start': 'Interval Start',
    'interval_end': 'Interval End',
    'agent_id': 'Agent Id',
    'agent_name': 'Agent Name',
    'logged_in': 'Logged In',          # milliseconds
    'on_queue': 'On Queue',            # milliseconds
    'idle': 'Idle',                    # milliseconds
    'available': 'Available',          # milliseconds
    'away': 'Away',                    # milliseconds
    'break': 'Break',                  # milliseconds
    'meal': 'Meal',                    # milliseconds
    'not_responding': 'Not Responding',# milliseconds
    'off_queue': 'Off Queue',          # milliseconds
    'title': 'Title',
    'department': 'Department',
    'off_queue_pct': 'Off Queue %',    # decimal (0.28 = 28%)
    'on_queue_pct': 'On Queue %',      # decimal
    'occupancy': 'Occupancy',          # decimal
    'interacting': 'Interacting',      # milliseconds
    'interacting_pct': 'Interacting %',# decimal
    'idle_pct': 'Idle %',              # decimal
}

# Skills Performance (Analytics → Queue Activity → Skills)
SKILLS_PERF_COLUMNS = {
    'interval_start': 'Interval Start',
    'interval_end': 'Interval End',
    'media_type': 'Media Type',
    'aggregate_detail': 'Aggregate or Detailed',
    'skill_id': 'Skill Id',
    'skill_name': 'Skill Name',
    'queue_id': 'Queue Id',
    'queue_name': 'Queue Name',
    'offer': 'Offer',
    'answer': 'Answer',
    'answer_pct': 'Answer %',          # decimal
    'abandon': 'Abandon',
    'abandon_pct': 'Abandon %',        # decimal
    'asa': 'ASA',                      # milliseconds
    'service_level_pct': 'Service Level %',  # decimal
    'sl_target_pct': 'Service Level Target %',
    'avg_handle': 'Avg Handle',        # milliseconds
    'avg_talk': 'Avg Talk',            # milliseconds
    'avg_hold': 'Avg Hold',            # milliseconds
    'avg_acw': 'Avg ACW',              # milliseconds
}

# Historical Adherence (WFM → Historical Adherence)
ADHERENCE_COLUMNS = {
    'agent': 'Agent',
    'management_unit': 'Management Unit',
    'adherence_pct': 'Adherence (%)',      # string with % sign
    'conformance_pct': 'Conformance (%)',  # string with % sign
    'exceptions': 'Exceptions',
    'exceptions_duration': 'Exceptions Duration Minutes',  # MINUTES
    'scheduled_minutes': 'Scheduled Minutes',              # MINUTES
    'actual_time': 'Actual Time',                         # MINUTES
    'scheduled_on_queue': 'Scheduled On Queue',           # MINUTES
    'work_time_on_queue': 'Work Time On Queue',           # MINUTES
}

# WFM Scheduled and Required
WFM_SCHEDULED_COLUMNS = {
    'time_utc': 'Time (UTC)',
    'scheduled': 'Scheduled',
    'required': 'Required Staff',
    'difference': 'Difference',
    'required_shrinkage': 'Required Staff with Shrinkage',
    'diff_shrinkage': 'Difference with Shrinkage',
    'time_local': 'Time (Chicago)',
}

# WFM Activities (individual agent activities)
WFM_ACTIVITIES_COLUMNS = {
    'agent_name': 'Agent Name',
    'activity_code': 'Activity Code Name',
    'start': 'Start',
    'end': 'End',
    'is_paid': 'Is Paid',
    'length_minutes': 'Length In Minutes',
}


# =============================================================================
# ISPN CALCULATION STANDARDS
# =============================================================================

ISPN_STANDARDS = {
    'abandon_threshold_ms': 60000,     # Only count abandons >= 60 seconds
    'aht_min_threshold_ms': 20000,     # Exclude < 20 second handles
    'acw_timeout_ms': 15000,           # Standard ACW timeout (confirmed!)
}


# =============================================================================
# PARSER FUNCTIONS
# =============================================================================

def parse_interactions(filepath: Path) -> dict:
    """
    Parse Genesys Cloud Interactions export CSV.
    
    Export location: Performance → Workspace → Interactions
    Time values: milliseconds
    
    Key fields:
    - Total Queue: Wait time (milliseconds)
    - Total Handle: Talk + Hold + ACW (milliseconds)
    - Abandoned: YES/NO
    - Non-ACD: YES = exclude from queue metrics
    - Media Type: voice, callback
    """
    df = pd.read_csv(filepath)
    
    result = {
        'source': 'genesys_interactions',
        'filepath': str(filepath),
        'parsed_at': datetime.now().isoformat(),
        'record_count': len(df),
        'columns': df.columns.tolist(),
        'field_validation': {},
        'metrics': {},
        'callbacks': {},
        'by_queue': {},
        'by_agent': {},
    }
    
    # Validate expected columns
    expected = ['Total Handle', 'Total Talk', 'Total Hold', 'Total ACW', 
                'Total Queue', 'Direction', 'Media Type', 'Abandoned', 'Non-ACD']
    for col in expected:
        result['field_validation'][col] = col in df.columns
    
    # Convert time columns to numeric (handle empty strings)
    time_cols = ['Total Handle', 'Total Talk', 'Total Hold', 'Total ACW', 'Total Queue', 'Total Alert']
    for col in time_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Filter: Inbound only, exclude Non-ACD
    df_inbound = df[df['Direction'] == 'Inbound'].copy() if 'Direction' in df.columns else df.copy()
    df_acd = df_inbound[df_inbound['Non-ACD'] != 'YES'].copy() if 'Non-ACD' in df.columns else df_inbound.copy()
    
    result['total_count'] = len(df)
    result['inbound_count'] = len(df_inbound)
    result['acd_count'] = len(df_acd)
    
    # Apply ISPN standards: exclude < 20 second handles
    df_valid = df_acd[df_acd['Total Handle'] >= ISPN_STANDARDS['aht_min_threshold_ms']].copy()
    result['valid_handle_count'] = len(df_valid)
    
    if len(df_valid) > 0:
        # Core metrics (convert ms to minutes/seconds)
        result['metrics']['avg_handle_time_min'] = df_valid['Total Handle'].mean() / 60000
        result['metrics']['avg_talk_time_min'] = df_valid['Total Talk'].mean() / 60000
        result['metrics']['avg_hold_time_min'] = df_valid['Total Hold'].mean() / 60000
        result['metrics']['avg_acw_time_sec'] = df_valid['Total ACW'].mean() / 1000
        
        # AWT calculation (only answered calls)
        answered = df_acd[df_acd['Abandoned'] == 'NO']
        if len(answered) > 0 and 'Total Queue' in df.columns:
            result['metrics']['avg_wait_time_sec'] = answered['Total Queue'].mean() / 1000
            result['metrics']['answer_count'] = len(answered)
        
        # Handle distribution
        result['metrics']['p50_handle_min'] = df_valid['Total Handle'].median() / 60000
        result['metrics']['p90_handle_min'] = df_valid['Total Handle'].quantile(0.9) / 60000
        result['metrics']['max_handle_min'] = df_valid['Total Handle'].max() / 60000
    
    # Callback identification (Media Type = "callback")
    if 'Media Type' in df.columns:
        callbacks = df[df['Media Type'].str.lower() == 'callback']
        result['callbacks']['count'] = len(callbacks)
        result['callbacks']['pct_of_total'] = (len(callbacks) / len(df) * 100) if len(df) > 0 else 0
    
    # Abandon analysis (queue time >= 60 seconds per ISPN standard)
    if 'Abandoned' in df.columns and 'Total Queue' in df.columns:
        abandoned = df_acd[df_acd['Abandoned'] == 'YES']
        valid_abandons = abandoned[abandoned['Total Queue'] >= ISPN_STANDARDS['abandon_threshold_ms']]
        result['metrics']['abandon_count'] = len(valid_abandons)
        result['metrics']['abandon_count_total'] = len(abandoned)
        result['metrics']['abandon_rate'] = (len(valid_abandons) / len(df_acd) * 100) if len(df_acd) > 0 else 0
        
        # Abandon timing distribution
        if len(abandoned) > 0:
            result['metrics']['avg_abandon_wait_sec'] = abandoned['Total Queue'].mean() / 1000
    
    # By Queue breakdown
    if 'Queue' in df.columns:
        queue_stats = df_acd.groupby('Queue').agg({
            'Total Handle': ['count', 'mean'],
            'Total Queue': 'mean',
        }).reset_index()
        queue_stats.columns = ['queue', 'call_count', 'avg_handle_ms', 'avg_wait_ms']
        
        for _, row in queue_stats.iterrows():
            if pd.notna(row['queue']) and row['queue']:
                result['by_queue'][row['queue']] = {
                    'call_count': int(row['call_count']),
                    'avg_handle_min': row['avg_handle_ms'] / 60000 if pd.notna(row['avg_handle_ms']) else None,
                    'avg_wait_sec': row['avg_wait_ms'] / 1000 if pd.notna(row['avg_wait_ms']) else None,
                }
    
    # By Agent breakdown
    if 'Users - Interacted' in df.columns:
        agent_stats = df_valid.groupby('Users - Interacted').agg({
            'Total Handle': ['count', 'mean'],
        }).reset_index()
        agent_stats.columns = ['agent', 'call_count', 'avg_handle_ms']
        
        for _, row in agent_stats.iterrows():
            if pd.notna(row['agent']) and row['agent']:
                result['by_agent'][row['agent']] = {
                    'call_count': int(row['call_count']),
                    'avg_handle_min': row['avg_handle_ms'] / 60000 if pd.notna(row['avg_handle_ms']) else None,
                }
    
    # ACW timeout analysis
    if 'Total ACW' in df.columns:
        acw_at_timeout = df_valid[df_valid['Total ACW'] == ISPN_STANDARDS['acw_timeout_ms']]
        result['metrics']['acw_timeout_count'] = len(acw_at_timeout)
        result['metrics']['acw_timeout_pct'] = (len(acw_at_timeout) / len(df_valid) * 100) if len(df_valid) > 0 else 0
    
    return result


def parse_agent_performance(filepath: Path) -> dict:
    """
    Parse Genesys Cloud Agent Performance Summary export.
    
    Export location: Performance → Workspace → Agents Performance
    Time values: milliseconds
    """
    df = pd.read_csv(filepath)
    
    result = {
        'source': 'genesys_agent_performance',
        'filepath': str(filepath),
        'parsed_at': datetime.now().isoformat(),
        'record_count': len(df),
        'columns': df.columns.tolist(),
        'agents': {},
        'totals': {},
    }
    
    # Skip template/placeholder rows
    df = df[df['Agent Name'] != '1 - New Hire Skills and Queues Template'].copy()
    df = df[df['Handle'].notna() & (df['Handle'] != '')].copy()
    
    # Convert numeric columns
    num_cols = ['Handle', 'Avg Handle', 'Avg Talk', 'Avg Hold', 'Avg ACW', 
                'Total Handle', 'Total Talk', 'Total Hold', 'Total ACW', 'ASA']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    result['agent_count'] = len(df)
    
    if len(df) > 0:
        # Totals
        result['totals']['total_calls'] = int(df['Handle'].sum())
        result['totals']['total_handle_hours'] = df['Total Handle'].sum() / 3600000  # ms to hours
        
        # Weighted averages
        total_handle = df['Total Handle'].sum()
        if total_handle > 0:
            result['totals']['avg_handle_min'] = total_handle / df['Handle'].sum() / 60000
            result['totals']['avg_talk_min'] = df['Total Talk'].sum() / df['Handle'].sum() / 60000
            result['totals']['avg_hold_min'] = df['Total Hold'].sum() / df['Handle'].sum() / 60000
            result['totals']['avg_acw_sec'] = df['Total ACW'].sum() / df['Handle'].sum() / 1000
        
        # By agent
        for _, row in df.iterrows():
            agent = row['Agent Name']
            if pd.notna(agent) and agent:
                result['agents'][agent] = {
                    'call_count': int(row['Handle']) if pd.notna(row['Handle']) else 0,
                    'avg_handle_min': row['Avg Handle'] / 60000 if pd.notna(row['Avg Handle']) else None,
                    'avg_talk_min': row['Avg Talk'] / 60000 if pd.notna(row['Avg Talk']) else None,
                    'avg_hold_min': row['Avg Hold'] / 60000 if pd.notna(row['Avg Hold']) else None,
                    'avg_acw_sec': row['Avg ACW'] / 1000 if pd.notna(row['Avg ACW']) else None,
                    'asa_sec': row['ASA'] / 1000 if pd.notna(row['ASA']) else None,
                    'title': row.get('Title', ''),
                    'department': row.get('Department', ''),
                }
    
    return result


def parse_agent_status(filepath: Path) -> dict:
    """
    Parse Genesys Cloud Agent Status Summary export.
    
    Export location: Performance → Contact Center → Agent Status Duration Details
    Time values: milliseconds
    Percentages: decimals (0.72 = 72%)
    """
    df = pd.read_csv(filepath)
    
    result = {
        'source': 'genesys_agent_status',
        'filepath': str(filepath),
        'parsed_at': datetime.now().isoformat(),
        'record_count': len(df),
        'columns': df.columns.tolist(),
        'agents': {},
        'totals': {},
        'shrinkage': {},
    }
    
    # Skip template rows
    df = df[df['Agent Name'] != '1 - New Hire Skills and Queues Template'].copy()
    df = df[df['Logged In'].notna() & (df['Logged In'] != '')].copy()
    
    # Convert numeric columns
    time_cols = ['Logged In', 'On Queue', 'Idle', 'Available', 'Away', 'Break', 
                 'Meal', 'Not Responding', 'Off Queue', 'Interacting']
    for col in time_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    result['agent_count'] = len(df)
    
    if len(df) > 0:
        # Totals (convert ms to hours)
        for col in time_cols:
            if col in df.columns:
                result['totals'][col.lower().replace(' ', '_') + '_hours'] = df[col].sum() / 3600000
        
        # Shrinkage calculation
        total_logged = df['Logged In'].sum()
        if total_logged > 0:
            # Planned shrinkage: Break + Meal + Training (if exists)
            planned = df['Break'].sum() + df['Meal'].sum()
            if 'Training' in df.columns:
                planned += df['Training'].sum()
            
            # Unplanned: Away + Off Queue
            unplanned = df['Away'].sum() + df['Off Queue'].sum()
            
            result['shrinkage']['planned_pct'] = (planned / total_logged) * 100
            result['shrinkage']['unplanned_pct'] = (unplanned / total_logged) * 100
            result['shrinkage']['total_pct'] = ((planned + unplanned) / total_logged) * 100
            
            # Productive time
            on_queue = df['On Queue'].sum()
            result['shrinkage']['on_queue_pct'] = (on_queue / total_logged) * 100
        
        # By agent
        for _, row in df.iterrows():
            agent = row['Agent Name']
            if pd.notna(agent) and agent:
                logged = row['Logged In'] if pd.notna(row['Logged In']) else 0
                result['agents'][agent] = {
                    'logged_in_hours': logged / 3600000 if logged else 0,
                    'on_queue_pct': float(row['On Queue %']) * 100 if pd.notna(row.get('On Queue %')) else None,
                    'occupancy_pct': float(row['Occupancy']) * 100 if pd.notna(row.get('Occupancy')) else None,
                    'idle_pct': float(row['Idle %']) * 100 if pd.notna(row.get('Idle %')) else None,
                    'title': row.get('Title', ''),
                    'department': row.get('Department', ''),
                }
    
    return result


def parse_skills_performance(filepath: Path) -> dict:
    """
    Parse Genesys Cloud Skills Performance export.
    
    Export location: Analytics → Queue Activity → Skills Performance
    Percentages: decimals (0.85 = 85%)
    Times: milliseconds
    """
    df = pd.read_csv(filepath)
    
    result = {
        'source': 'genesys_skills_performance',
        'filepath': str(filepath),
        'parsed_at': datetime.now().isoformat(),
        'record_count': len(df),
        'columns': df.columns.tolist(),
        'by_queue': {},
        'by_skill': {},
        'totals': {},
    }
    
    # Convert numeric columns
    num_cols = ['Offer', 'Answer', 'Abandon', 'ASA', 'Avg Handle', 'Avg Talk', 'Avg Hold', 'Avg ACW']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Aggregate rows (total across skills)
    df_agg = df[df['Aggregate or Detailed'] == 'Aggregate'].copy() if 'Aggregate or Detailed' in df.columns else df.copy()
    df_detail = df[df['Aggregate or Detailed'] == 'Detailed'].copy() if 'Aggregate or Detailed' in df.columns else pd.DataFrame()
    
    if len(df_agg) > 0:
        result['totals']['offered'] = int(df_agg['Offer'].sum())
        result['totals']['answered'] = int(df_agg['Answer'].sum())
        result['totals']['abandoned'] = int(df_agg['Abandon'].sum())
        
        if result['totals']['offered'] > 0:
            result['totals']['answer_rate'] = (result['totals']['answered'] / result['totals']['offered']) * 100
            result['totals']['abandon_rate'] = (result['totals']['abandoned'] / result['totals']['offered']) * 100
    
    # By Queue
    if 'Queue Name' in df_detail.columns:
        queue_stats = df_detail.groupby('Queue Name').agg({
            'Offer': 'sum',
            'Answer': 'sum',
            'Abandon': 'sum',
            'ASA': 'mean',
            'Avg Handle': 'mean',
        }).reset_index()
        
        for _, row in queue_stats.iterrows():
            queue = row['Queue Name']
            if pd.notna(queue) and queue:
                result['by_queue'][queue] = {
                    'offered': int(row['Offer']) if pd.notna(row['Offer']) else 0,
                    'answered': int(row['Answer']) if pd.notna(row['Answer']) else 0,
                    'abandoned': int(row['Abandon']) if pd.notna(row['Abandon']) else 0,
                    'asa_sec': row['ASA'] / 1000 if pd.notna(row['ASA']) else None,
                    'avg_handle_min': row['Avg Handle'] / 60000 if pd.notna(row['Avg Handle']) else None,
                }
    
    return result


def parse_historical_adherence(filepath: Path) -> dict:
    """
    Parse Genesys WFM Historical Adherence export.
    
    Export location: WFM → Historical Adherence
    Time values: MINUTES (not milliseconds!)
    Percentages: strings with % sign (need parsing)
    """
    df = pd.read_csv(filepath)
    
    result = {
        'source': 'genesys_adherence',
        'filepath': str(filepath),
        'parsed_at': datetime.now().isoformat(),
        'record_count': len(df),
        'columns': df.columns.tolist(),
        'agents': {},
        'totals': {},
    }
    
    # Parse percentage columns (remove % sign, handle Infinity)
    def parse_pct(val):
        if pd.isna(val):
            return None
        val_str = str(val).replace('%', '').strip()
        if 'Infinity' in val_str or val_str == '':
            return None
        try:
            return float(val_str)
        except:
            return None
    
    if 'Adherence (%)' in df.columns:
        df['adherence_parsed'] = df['Adherence (%)'].apply(parse_pct)
    if 'Conformance (%)' in df.columns:
        df['conformance_parsed'] = df['Conformance (%)'].apply(parse_pct)
    
    # Filter out invalid rows
    df_valid = df[df['adherence_parsed'].notna()].copy()
    
    result['agent_count'] = len(df_valid)
    
    if len(df_valid) > 0:
        # Totals
        result['totals']['avg_adherence_pct'] = df_valid['adherence_parsed'].mean()
        result['totals']['avg_conformance_pct'] = df_valid['conformance_parsed'].mean()
        
        if 'Scheduled Minutes' in df.columns:
            result['totals']['total_scheduled_hours'] = pd.to_numeric(df_valid['Scheduled Minutes'], errors='coerce').sum() / 60
        if 'Work Time On Queue' in df.columns:
            result['totals']['total_work_hours'] = pd.to_numeric(df_valid['Work Time On Queue'], errors='coerce').sum() / 60
        
        # By agent
        for _, row in df_valid.iterrows():
            agent = row['Agent']
            if pd.notna(agent) and agent:
                result['agents'][agent] = {
                    'adherence_pct': row['adherence_parsed'],
                    'conformance_pct': row['conformance_parsed'],
                    'exceptions': int(row['Exceptions']) if pd.notna(row.get('Exceptions')) else 0,
                    'scheduled_hours': float(row['Scheduled Minutes']) / 60 if pd.notna(row.get('Scheduled Minutes')) else None,
                }
    
    return result


def parse_wfm_scheduled(filepath: Path) -> dict:
    """
    Parse WFM Scheduled and Required export.
    
    15-minute interval staffing data.
    """
    df = pd.read_csv(filepath)
    
    result = {
        'source': 'wfm_scheduled_required',
        'filepath': str(filepath),
        'parsed_at': datetime.now().isoformat(),
        'record_count': len(df),
        'columns': df.columns.tolist(),
        'summary': {},
        'intervals': [],
    }
    
    # Convert numeric columns
    num_cols = ['Scheduled', 'Required Staff', 'Difference', 
                'Required Staff with Shrinkage', 'Difference with Shrinkage']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    if len(df) > 0:
        result['summary']['total_intervals'] = len(df)
        result['summary']['avg_scheduled'] = df['Scheduled'].mean()
        result['summary']['avg_required'] = df['Required Staff'].mean()
        result['summary']['avg_difference'] = df['Difference'].mean()
        
        # Understaffed/Overstaffed intervals
        result['summary']['understaffed_intervals'] = int((df['Difference'] < 0).sum())
        result['summary']['overstaffed_intervals'] = int((df['Difference'] > 0).sum())
        result['summary']['understaffed_pct'] = (df['Difference'] < 0).mean() * 100
    
    return result


def parse_wfm_activities(filepath: Path) -> dict:
    """
    Parse WFM Activities export.
    
    Individual agent scheduled activities.
    """
    df = pd.read_csv(filepath)
    
    result = {
        'source': 'wfm_activities',
        'filepath': str(filepath),
        'parsed_at': datetime.now().isoformat(),
        'record_count': len(df),
        'columns': df.columns.tolist(),
        'by_activity': {},
        'by_agent': {},
    }
    
    # Standardize column names (handle BOM)
    df.columns = [c.strip().replace('\ufeff', '') for c in df.columns]
    
    if 'Activity Code Name' in df.columns:
        activity_summary = df.groupby('Activity Code Name').agg({
            'Length In Minutes': 'sum'
        }).reset_index()
        
        for _, row in activity_summary.iterrows():
            activity = row['Activity Code Name']
            if pd.notna(activity):
                result['by_activity'][activity] = {
                    'total_hours': row['Length In Minutes'] / 60 if pd.notna(row['Length In Minutes']) else 0
                }
    
    if 'Agent Name' in df.columns:
        agent_summary = df.groupby('Agent Name').agg({
            'Length In Minutes': 'sum'
        }).reset_index()
        
        for _, row in agent_summary.iterrows():
            agent = row['Agent Name']
            if pd.notna(agent):
                result['by_agent'][agent] = {
                    'total_hours': row['Length In Minutes'] / 60 if pd.notna(row['Length In Minutes']) else 0
                }
    
    return result


def parse_agent_schedules(filepath: Path) -> dict:
    """
    Parse Agents Permanent Schedules export.
    
    Agent configuration: skills, queues, planning groups.
    """
    df = pd.read_csv(filepath)
    
    # Standardize column names (handle BOM and quotes)
    df.columns = [c.strip().replace('\ufeff', '').replace('"', '') for c in df.columns]
    
    result = {
        'source': 'agent_schedules',
        'filepath': str(filepath),
        'parsed_at': datetime.now().isoformat(),
        'record_count': len(df),
        'columns': df.columns.tolist(),
        'agents': {},
        'summary': {},
    }
    
    result['summary']['total_agents'] = len(df)
    result['summary']['schedulable'] = int((df['Schedulable'] == 'Yes').sum()) if 'Schedulable' in df.columns else 0
    
    # Skills distribution
    if 'Skills' in df.columns:
        all_skills = []
        for skills in df['Skills'].dropna():
            all_skills.extend([s.strip() for s in str(skills).split(',')])
        skill_counts = pd.Series(all_skills).value_counts()
        result['summary']['top_skills'] = skill_counts.head(10).to_dict()
    
    # Planning groups
    if 'Planning Groups' in df.columns:
        pg_counts = df['Planning Groups'].value_counts()
        result['summary']['planning_groups'] = pg_counts.to_dict()
    
    # Work teams
    if 'Work Team' in df.columns:
        team_counts = df['Work Team'].value_counts()
        result['summary']['work_teams'] = team_counts.to_dict()
    
    return result


# =============================================================================
# LEGACY PARSERS (for internal ISPN files)
# =============================================================================

def parse_scorecard(filepath: Path) -> dict:
    """Parse LT Scorecard Excel file."""
    df = pd.read_excel(filepath, sheet_name='ISPN_Scorecard-Monthly_INPUT', header=None)
    
    result = {
        'source': 'scorecard',
        'filepath': str(filepath),
        'parsed_at': datetime.now().isoformat(),
        'kpis': {}
    }
    
    kpi_rows = {
        'calls_offered': 51,
        'aht': 57,
        'awt': 58,
        'fcr': 59,
        'escalation': 60,
        'utilization': 61,
        'shrinkage': 62,
        'quality': 63,
        'headcount': 64
    }
    
    for col in range(df.shape[1] - 1, 0, -1):
        has_data = False
        for row in kpi_rows.values():
            val = df.iloc[row, col] if row < df.shape[0] else None
            if pd.notna(val) and isinstance(val, (int, float)):
                has_data = True
                break
        
        if has_data:
            for kpi, row in kpi_rows.items():
                if row < df.shape[0]:
                    val = df.iloc[row, col]
                    if pd.notna(val):
                        result['kpis'][kpi] = float(val) if isinstance(val, (int, float)) else None
            break
    
    return result


def parse_dpr(filepath: Path) -> dict:
    """Parse Daily Performance Report Excel file."""
    xl = pd.ExcelFile(filepath)
    
    result = {
        'source': 'dpr',
        'filepath': str(filepath),
        'parsed_at': datetime.now().isoformat(),
        'days': []
    }
    
    for sheet in xl.sheet_names:
        if re.match(r'[A-Z]{3}\d{2}', sheet):
            df = pd.read_excel(filepath, sheet_name=sheet)
            cols = df.columns.tolist()
            date_col = next((c for c in cols if 'date' in str(c).lower()), None)
            
            for idx, row in df.iterrows():
                day_data = {}
                if date_col and pd.notna(row.get(date_col)):
                    day_data['date'] = str(row[date_col])
                if day_data:
                    result['days'].append(day_data)
            break
    
    return result


def parse_wcs(filepath: Path) -> dict:
    """Parse Weekly Call Statistics Excel file."""
    xl = pd.ExcelFile(filepath)
    
    result = {
        'source': 'wcs',
        'filepath': str(filepath),
        'parsed_at': datetime.now().isoformat(),
        'hourly_data': [],
        'partners': {}
    }
    
    if 'CD data 2' in xl.sheet_names:
        df = pd.read_excel(filepath, sheet_name='CD data 2')
        result['hourly_row_count'] = len(df)
        result['hourly_valid'] = len(df) == 168
    
    return result


# =============================================================================
# FILE TYPE IDENTIFICATION
# =============================================================================

def identify_file_type(filepath: Path) -> str:
    """
    Identify file type based on filename pattern and content.
    
    Returns one of:
    - Genesys exports: 'genesys_interactions', 'genesys_agent_performance',
      'genesys_agent_status', 'genesys_skills_performance', 'genesys_adherence',
      'wfm_scheduled', 'wfm_activities', 'agent_schedules'
    - Internal files: 'scorecard', 'dpr', 'wcs'
    - 'unknown'
    """
    name = filepath.name.lower()
    
    # Check filename patterns
    if 'scorecard' in name:
        return 'scorecard'
    elif name.startswith('dpr'):
        return 'dpr'
    elif name.startswith('wcs') or re.match(r'\d{6}-\d{6}', name):
        return 'wcs'
    elif 'interaction' in name:
        return 'genesys_interactions'
    elif 'agent_performance' in name or 'agentperformance' in name:
        return 'genesys_agent_performance'
    elif 'agent_status' in name or 'agentstatus' in name:
        return 'genesys_agent_status'
    elif 'skills_performance' in name or 'skillsperformance' in name:
        return 'genesys_skills_performance'
    elif 'adherence' in name:
        return 'genesys_adherence'
    elif 'scheduledand' in name or 'scheduledrequired' in name:
        return 'wfm_scheduled'
    elif 'activities' in name and 'activity' not in name:
        return 'wfm_activities'
    elif 'activitycount' in name:
        return 'wfm_activity_counts'
    elif 'permanent_schedule' in name or 'agents_permanent' in name:
        return 'agent_schedules'
    
    # Check CSV content
    if filepath.suffix.lower() == '.csv':
        try:
            df = pd.read_csv(filepath, nrows=5)
            cols = ' '.join([str(c).lower() for c in df.columns])
            
            if 'total handle' in cols and 'conversation id' in cols:
                return 'genesys_interactions'
            if 'avg handle' in cols and 'agent name' in cols and 'handle' in cols:
                return 'genesys_agent_performance'
            if 'logged in' in cols and 'on queue' in cols and 'occupancy' in cols:
                return 'genesys_agent_status'
            if 'skill name' in cols and 'queue name' in cols:
                return 'genesys_skills_performance'
            if 'adherence' in cols and 'conformance' in cols:
                return 'genesys_adherence'
            if 'required staff' in cols and 'scheduled' in cols:
                return 'wfm_scheduled'
            if 'activity code' in cols:
                return 'wfm_activities'
            if 'planning groups' in cols and 'skills' in cols:
                return 'agent_schedules'
        except:
            pass
    
    return 'unknown'


def parse_file(filepath: Path) -> dict:
    """Auto-detect file type and parse accordingly."""
    file_type = identify_file_type(filepath)
    
    parsers = {
        # Genesys exports
        'genesys_interactions': parse_interactions,
        'genesys_agent_performance': parse_agent_performance,
        'genesys_agent_status': parse_agent_status,
        'genesys_skills_performance': parse_skills_performance,
        'genesys_adherence': parse_historical_adherence,
        'wfm_scheduled': parse_wfm_scheduled,
        'wfm_activities': parse_wfm_activities,
        'agent_schedules': parse_agent_schedules,
        # Internal files
        'scorecard': parse_scorecard,
        'dpr': parse_dpr,
        'wcs': parse_wcs,
    }
    
    if file_type in parsers:
        return parsers[file_type](filepath)
    else:
        return {
            'source': 'unknown',
            'filepath': str(filepath),
            'parsed_at': datetime.now().isoformat(),
            'error': 'Unknown file type'
        }

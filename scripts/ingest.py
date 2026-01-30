#!/usr/bin/env python3
"""
ISPN Data Ingestion Pipeline v2.0

CRITICAL: This pipeline uses ISPN Canonical Calculations.
All metrics flow through ISPNCalculationEngine - NEVER use Genesys
pre-calculated percentages directly.

Processes Genesys Cloud exports and internal ISPN files:
1. Auto-detects file type
2. Extracts RAW data (counts and milliseconds ONLY)
3. Applies ISPN canonical formulas via ISPNCalculationEngine
4. Validates against ISPN standards
5. Stores to appropriate location
6. Updates metrics history with ISPN-calculated values

Usage:
    python scripts/ingest.py                    # Process all files in data/raw/
    python scripts/ingest.py path/to/file.csv   # Process single file
    python scripts/ingest.py --calculate        # Run ISPN calculations on stored raw data
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.parsers import parse_file, identify_file_type
from utils.validators import validate_data, get_status, THRESHOLDS
from utils.ispn_calculations import (
    ISPNCalculationEngine, 
    GenesysRawData, 
    ISPNCalculatedMetrics,
    TARGETS,
    MS_TO_HOURS,
    MS_TO_MINUTES,
)


# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
RAW_DIR = DATA_DIR / 'raw'
PARSED_DIR = DATA_DIR / 'parsed'
METRICS_DIR = DATA_DIR / 'metrics'

# Output subdirectories by source type
OUTPUT_DIRS = {
    'genesys_interactions': PARSED_DIR / 'genesys' / 'interactions',
    'genesys_agent_performance': PARSED_DIR / 'genesys' / 'agent_performance',
    'genesys_agent_status': PARSED_DIR / 'genesys' / 'agent_status',
    'genesys_skills_performance': PARSED_DIR / 'genesys' / 'skills_performance',
    'genesys_adherence': PARSED_DIR / 'genesys' / 'adherence',
    'wfm_scheduled_required': PARSED_DIR / 'wfm' / 'scheduled_required',
    'wfm_activities': PARSED_DIR / 'wfm' / 'activities',
    'agent_schedules': PARSED_DIR / 'wfm' / 'agent_schedules',
    'scorecard': PARSED_DIR / 'scorecard',
    'dpr': PARSED_DIR / 'dpr',
    'wcs': PARSED_DIR / 'wcs',
}

# ISPN Calculation Engine instance
CALC_ENGINE = ISPNCalculationEngine()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def ensure_dirs():
    """Create all required directories."""
    for d in OUTPUT_DIRS.values():
        d.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)


def load_raw_data_store() -> dict:
    """Load the raw data store for ISPN calculations."""
    store_file = METRICS_DIR / 'raw_data_store.json'
    if store_file.exists():
        with open(store_file) as f:
            return json.load(f)
    return {'periods': {}, 'last_updated': None}


def save_raw_data_store(store: dict):
    """Save the raw data store."""
    store_file = METRICS_DIR / 'raw_data_store.json'
    store['last_updated'] = datetime.now().isoformat()
    with open(store_file, 'w') as f:
        json.dump(store, f, indent=2, default=str)


def update_raw_data_store(source: str, raw_data: dict, period: str = None):
    """
    Update raw data store with extracted values.
    Raw data accumulates across file types until ISPN calculation is triggered.
    """
    if period is None:
        period = datetime.now().strftime('%Y-%m')
    
    store = load_raw_data_store()
    
    if period not in store['periods']:
        store['periods'][period] = {
            'interactions': {},
            'agent_status': {},
            'helpdesk': {},
            'quality': {},
            'manual': {},
            'metadata': {'files_processed': []}
        }
    
    period_data = store['periods'][period]
    
    # Map source types to store sections
    if source == 'genesys_interactions':
        period_data['interactions'].update(raw_data)
    elif source == 'genesys_agent_status':
        period_data['agent_status'].update(raw_data)
    elif source == 'genesys_agent_performance':
        # Can be used for validation/cross-check
        period_data['agent_performance'] = raw_data
    elif source == 'genesys_adherence':
        period_data['adherence'] = raw_data
    
    period_data['metadata']['files_processed'].append({
        'source': source,
        'timestamp': datetime.now().isoformat()
    })
    
    save_raw_data_store(store)
    return period


def extract_raw_for_ispn(parsed_data: dict) -> dict:
    """
    Extract RAW values from parsed data for ISPN calculations.
    Returns only counts and milliseconds - NO pre-calculated percentages.
    """
    source = parsed_data.get('source', '')
    raw = {}
    
    if source == 'genesys_interactions':
        # Extract RAW counts and totals
        raw['inbound_call_count'] = parsed_data.get('acd_count', 0)
        raw['total_records'] = parsed_data.get('total_records', 0)
        
        # Get raw millisecond totals from metrics
        metrics = parsed_data.get('metrics', {})
        
        # These need to be stored as totals, not averages
        # If we have average and count, we can reconstruct total
        if 'total_handle_ms' in metrics:
            raw['inbound_total_handle_ms'] = metrics['total_handle_ms']
        elif 'avg_handle_time_min' in metrics and raw['inbound_call_count'] > 0:
            # Convert back: avg_min * count * 60000 = total_ms
            raw['inbound_total_handle_ms'] = int(
                metrics['avg_handle_time_min'] * raw['inbound_call_count'] * 60000
            )
        
        if 'total_queue_ms' in metrics:
            raw['inbound_total_queue_ms'] = metrics['total_queue_ms']
        elif 'avg_wait_time_sec' in metrics and raw['inbound_call_count'] > 0:
            raw['inbound_total_queue_ms'] = int(
                metrics['avg_wait_time_sec'] * raw['inbound_call_count'] * 1000
            )
        
        # Abandon counts
        raw['abandoned_call_count'] = metrics.get('abandoned_count', 0)
        
        # Answer thresholds
        raw['answered_under_30s'] = metrics.get('answered_under_30s', 0)
        raw['answered_under_60s'] = metrics.get('answered_under_60s', 0)
        raw['answered_under_90s'] = metrics.get('answered_under_90s', 0)
        raw['answered_under_120s'] = metrics.get('answered_under_120s', 0)
        
        # Outbound/Callback
        raw['outbound_call_count'] = metrics.get('outbound_count', 0)
        raw['outbound_total_handle_ms'] = metrics.get('outbound_handle_ms', 0)
        raw['callback_call_count'] = metrics.get('callback_count', 0)
        raw['callback_total_handle_ms'] = metrics.get('callback_handle_ms', 0)
    
    elif source == 'genesys_agent_status':
        # Extract RAW millisecond totals
        totals = parsed_data.get('totals', {})
        
        raw['total_logged_in_ms'] = totals.get('logged_in_ms', 0)
        raw['total_on_queue_ms'] = totals.get('on_queue_ms', 0)
        raw['total_interacting_ms'] = totals.get('interacting_ms', 0)
        raw['total_idle_ms'] = totals.get('idle_ms', 0)
        raw['total_available_ms'] = totals.get('available_ms', 0)
        raw['total_away_ms'] = totals.get('away_ms', 0)
        raw['total_break_ms'] = totals.get('break_ms', 0)
        raw['total_meal_ms'] = totals.get('meal_ms', 0)
        raw['total_not_responding_ms'] = totals.get('not_responding_ms', 0)
        
        raw['agent_count'] = parsed_data.get('agent_count', 0)
    
    elif source == 'genesys_adherence':
        totals = parsed_data.get('totals', {})
        raw['avg_adherence_pct'] = totals.get('avg_adherence_pct', 0)
        raw['avg_conformance_pct'] = totals.get('avg_conformance_pct', 0)
    
    return raw


def run_ispn_calculations(period: str = None) -> Tuple[ISPNCalculatedMetrics, dict]:
    """
    Run ISPN canonical calculations on accumulated raw data for a period.
    
    Args:
        period: Period to calculate (YYYY-MM format). None = current month.
    
    Returns:
        Tuple of (ISPNCalculatedMetrics, dict of warnings)
    """
    if period is None:
        period = datetime.now().strftime('%Y-%m')
    
    store = load_raw_data_store()
    
    if period not in store['periods']:
        return None, {'error': f'No raw data found for period {period}'}
    
    period_data = store['periods'][period]
    
    # Build GenesysRawData from stored values
    interactions = period_data.get('interactions', {})
    agent_status = period_data.get('agent_status', {})
    helpdesk = period_data.get('helpdesk', {})
    quality = period_data.get('quality', {})
    manual = period_data.get('manual', {})
    
    raw = GenesysRawData(
        # Interactions data
        inbound_call_count=interactions.get('inbound_call_count', 0),
        inbound_total_handle_ms=interactions.get('inbound_total_handle_ms', 0),
        inbound_total_queue_ms=interactions.get('inbound_total_queue_ms', 0),
        abandoned_call_count=interactions.get('abandoned_call_count', 0),
        answered_under_30s=interactions.get('answered_under_30s', 0),
        answered_under_60s=interactions.get('answered_under_60s', 0),
        answered_under_90s=interactions.get('answered_under_90s', 0),
        answered_under_120s=interactions.get('answered_under_120s', 0),
        outbound_call_count=interactions.get('outbound_call_count', 0),
        outbound_total_handle_ms=interactions.get('outbound_total_handle_ms', 0),
        callback_call_count=interactions.get('callback_call_count', 0),
        callback_total_handle_ms=interactions.get('callback_total_handle_ms', 0),
        
        # Agent status data
        total_logged_in_ms=agent_status.get('total_logged_in_ms', 0),
        total_on_queue_ms=agent_status.get('total_on_queue_ms', 0),
        total_interacting_ms=agent_status.get('total_interacting_ms', 0),
        total_idle_ms=agent_status.get('total_idle_ms', 0),
        total_available_ms=agent_status.get('total_available_ms', 0),
        total_away_ms=agent_status.get('total_away_ms', 0),
        total_break_ms=agent_status.get('total_break_ms', 0),
        total_meal_ms=agent_status.get('total_meal_ms', 0),
        total_not_responding_ms=agent_status.get('total_not_responding_ms', 0),
        agent_count=agent_status.get('agent_count', 0),
        
        # Helpdesk data (manual input or from helpdesk system)
        call_tickets=helpdesk.get('call_tickets', 0),
        escalations=helpdesk.get('escalations', 0),
        alert_tickets=helpdesk.get('alert_tickets', 0),
        
        # Quality data
        tech_review_scores=quality.get('tech_review_scores', []),
        efficacy_scores=quality.get('efficacy_scores', []),
        
        # Manual inputs
        training_hours=manual.get('training_hours', 0),
        
        # Wave/secondary platform (if applicable)
        wave_call_count=manual.get('wave_call_count', 0),
        wave_total_minutes=manual.get('wave_total_minutes', 0),
        wave_awt_seconds=manual.get('wave_awt_seconds', 0),
    )
    
    # Run calculations
    metrics = CALC_ENGINE.calculate_all(raw)
    
    # Save calculated metrics
    save_ispn_metrics(period, metrics, raw)
    
    return metrics, {'warnings': metrics.warnings}


def save_ispn_metrics(period: str, metrics: ISPNCalculatedMetrics, raw: GenesysRawData):
    """Save ISPN-calculated metrics to history."""
    history_file = METRICS_DIR / 'ispn_metrics_history.json'
    
    history = {}
    if history_file.exists():
        with open(history_file) as f:
            history = json.load(f)
    
    if 'periods' not in history:
        history['periods'] = {}
    
    # Build KPI dict with status
    kpis = {}
    statuses = {}
    
    kpi_mapping = [
        ('fcr', 'fcr_pct', metrics.fcr_pct, lambda x: f"{x:.1%}" if x else 'N/A'),
        ('escalation', 'escalation_pct', metrics.escalation_pct, lambda x: f"{x:.1%}" if x else 'N/A'),
        ('aht', 'aht_minutes', metrics.aht_minutes, lambda x: f"{x:.2f}" if x else 'N/A'),
        ('awt', 'awt_seconds', metrics.awt_seconds, lambda x: f"{x:.1f}" if x else 'N/A'),
        ('shrinkage', 'shrinkage_pct', metrics.shrinkage_pct, lambda x: f"{x:.1%}" if x else 'N/A'),
        ('utilization', 'utilization_pct', metrics.utilization_pct, lambda x: f"{x:.1%}" if x else 'N/A'),
        ('occupancy', 'occupancy_pct', metrics.occupancy_pct, lambda x: f"{x:.1%}" if x else 'N/A'),
        ('quality', 'quality_score', metrics.quality_score, lambda x: f"{x:.1f}" if x else 'N/A'),
        ('abandon', 'abandon_pct', metrics.abandon_pct, lambda x: f"{x:.1%}" if x else 'N/A'),
    ]
    
    for display_name, attr_name, value, formatter in kpi_mapping:
        kpis[display_name] = value
        
        if value is not None:
            status = CALC_ENGINE.get_status(attr_name, value)
            target_info = TARGETS.get(attr_name, {})
            target = target_info.get('target')
            direction = target_info.get('direction', 'above')
            
            # Format target for display
            if target:
                if 'pct' in attr_name:
                    target_display = f"{'>' if direction == 'above' else '<'} {target:.0%}"
                elif attr_name == 'aht_minutes':
                    target_display = f"< {target} min"
                elif attr_name == 'awt_seconds':
                    target_display = f"< {target} sec"
                elif attr_name == 'quality_score':
                    target_display = f"> {target}"
                else:
                    target_display = str(target)
            else:
                target_display = 'N/A'
            
            statuses[display_name] = {
                'value': formatter(value),
                'raw_value': value,
                'target': target_display,
                'status': status.upper()
            }
    
    history['periods'][period] = {
        'kpis': kpis,
        'statuses': statuses,
        'call_volume': {
            'inbound_count': metrics.total_inbound_call_count,
            'inbound_hours': metrics.total_inbound_call_hours,
            'outbound_count': metrics.total_outbound_call_count,
            'outbound_hours': metrics.total_outbound_call_hours,
            'callback_count': metrics.total_callback_count,
            'callback_hours': metrics.total_callback_hours,
        },
        'agent_hours': {
            'total_hours_worked': metrics.total_hours_worked,
            'on_queue_hours': metrics.on_queue_hours,
            'hours_unavailable': metrics.hours_unavailable,
            'acw_hours': metrics.acw_hours,
        },
        'headcount': metrics.headcount,
        'metadata': {
            'calculation_timestamp': metrics.calculation_timestamp,
            'formula_version': metrics.formula_version,
            'warnings': metrics.warnings,
        }
    }
    
    history['last_updated'] = datetime.now().isoformat()
    
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2, default=str)


def update_kpi_history(source: str, metrics: dict, filepath: str):
    """
    Append metrics to legacy KPI history file.
    Uses a list structure for time-series tracking.
    """
    history_file = METRICS_DIR / 'kpi_history.json'
    
    # Load existing history or create new list
    history = []
    if history_file.exists():
        with open(history_file) as f:
            data = json.load(f)
            # Handle both old dict format and new list format
            if isinstance(data, list):
                history = data
            elif isinstance(data, dict) and 'entries' in data:
                history = data['entries']
            # Otherwise start fresh with empty list
    
    entry = {
        'timestamp': datetime.now().isoformat(),
        'source': source,
        'file': filepath,
        'metrics': metrics,
    }
    
    history.append(entry)
    
    # Keep last 1000 entries
    history = history[-1000:]
    
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2, default=str)


def print_validation_results(is_valid: bool, issues: list, statuses: dict):
    """Pretty print validation results."""
    if is_valid:
        print("  ✓ Validation: PASSED")
    else:
        print("  ✗ Validation: FAILED")
    
    for issue in issues:
        if issue.startswith('RED:') or issue.startswith('CRITICAL:'):
            print(f"    🔴 {issue}")
        elif issue.startswith('YELLOW:') or issue.startswith('WARNING:'):
            print(f"    🟡 {issue}")
        else:
            print(f"    ℹ️  {issue}")
    
    if statuses:
        print("  Status Summary:")
        for metric, status in statuses.items():
            if status == 'green':
                print(f"    🟢 {metric}")
            elif status == 'yellow':
                print(f"    🟡 {metric}")
            elif status == 'red':
                print(f"    🔴 {metric}")


def print_metrics_summary(data: dict):
    """Print key metrics from parsed data."""
    source = data.get('source', 'unknown')
    
    print("  Key Metrics (Raw Data Extracted):")
    
    if source == 'genesys_interactions':
        m = data.get('metrics', {})
        print(f"    Records: {data.get('acd_count', 0):,} ACD calls")
        print(f"    ⚠️  NOTE: AHT/AWT shown below are for reference only.")
        print(f"    ⚠️  Final metrics will be calculated using ISPN formulas.")
        if 'avg_handle_time_min' in m:
            aht = m['avg_handle_time_min']
            print(f"    [Reference] Genesys AHT: {aht:.2f} min")
        if 'avg_wait_time_sec' in m:
            awt = m['avg_wait_time_sec']
            print(f"    [Reference] Genesys AWT: {awt:.1f} sec")
    
    elif source == 'genesys_agent_performance':
        t = data.get('totals', {})
        print(f"    Agents: {data.get('agent_count', 0)}")
        print(f"    Total Calls: {t.get('total_calls', 0):,}")
        if 'avg_handle_min' in t:
            print(f"    [Reference] Team AHT: {t['avg_handle_min']:.2f} min")
    
    elif source == 'genesys_agent_status':
        totals = data.get('totals', {})
        print(f"    Agents: {data.get('agent_count', 0)}")
        print(f"    ⚠️  NOTE: Shrinkage will be calculated using ISPN formula:")
        print(f"    ⚠️  Shrinkage = (Logged In - On Queue) / Logged In")
        if 'logged_in_hours' in totals:
            print(f"    Logged In Hours: {totals['logged_in_hours']:,.1f}")
        if 'on_queue_hours' in totals:
            print(f"    On-Queue Hours: {totals['on_queue_hours']:,.1f}")
        # Show what ISPN shrinkage would be
        if totals.get('logged_in_hours', 0) > 0:
            ispn_shrink = (totals['logged_in_hours'] - totals.get('on_queue_hours', 0)) / totals['logged_in_hours']
            print(f"    [ISPN] Shrinkage: {ispn_shrink:.1%}")
    
    elif source == 'genesys_skills_performance':
        t = data.get('totals', {})
        print(f"    Offered: {t.get('offered', 0):,}")
        print(f"    Answered: {t.get('answered', 0):,}")
    
    elif source == 'genesys_adherence':
        t = data.get('totals', {})
        print(f"    Agents: {data.get('agent_count', 0)}")
        if 'avg_adherence_pct' in t:
            adh = t['avg_adherence_pct']
            status = get_status(adh, 'adherence_pct')
            icon = '🟢' if status == 'green' else ('🟡' if status == 'yellow' else '🔴')
            print(f"    Adherence: {adh:.1f}% {icon} (target: >90%)")
    
    elif source == 'wfm_scheduled_required':
        s = data.get('summary', {})
        print(f"    Intervals: {s.get('total_intervals', 0)}")
        print(f"    Understaffed: {s.get('understaffed_intervals', 0)} ({s.get('understaffed_pct', 0):.1f}%)")
        print(f"    Overstaffed: {s.get('overstaffed_intervals', 0)}")
    
    elif source == 'agent_schedules':
        s = data.get('summary', {})
        print(f"    Total Agents: {s.get('total_agents', 0)}")
        print(f"    Schedulable: {s.get('schedulable', 0)}")


def print_ispn_calculations(metrics: ISPNCalculatedMetrics):
    """Print ISPN-calculated metrics with status indicators."""
    print("\n" + "="*60)
    print("ISPN CANONICAL CALCULATIONS")
    print("="*60)
    
    kpis = [
        ('FCR', 'fcr_pct', metrics.fcr_pct, '> 70%', lambda x: f"{x:.1%}"),
        ('Escalation', 'escalation_pct', metrics.escalation_pct, '< 30%', lambda x: f"{x:.1%}"),
        ('AHT', 'aht_minutes', metrics.aht_minutes, '< 10.7 min', lambda x: f"{x:.2f} min"),
        ('AWT', 'awt_seconds', metrics.awt_seconds, '< 90 sec', lambda x: f"{x:.1f} sec"),
        ('Shrinkage', 'shrinkage_pct', metrics.shrinkage_pct, '< 30%', lambda x: f"{x:.1%}"),
        ('Utilization', 'utilization_pct', metrics.utilization_pct, '> 55%', lambda x: f"{x:.1%}"),
        ('Occupancy', 'occupancy_pct', metrics.occupancy_pct, '> 65%', lambda x: f"{x:.1%}"),
        ('Quality', 'quality_score', metrics.quality_score, '> 88', lambda x: f"{x:.1f}"),
        ('Abandon', 'abandon_pct', metrics.abandon_pct, '< 5%', lambda x: f"{x:.1%}"),
    ]
    
    print(f"{'KPI':<15} {'Value':<15} {'Target':<12} {'Status':<8}")
    print("-"*50)
    
    for name, attr, value, target, formatter in kpis:
        if value is not None:
            status = CALC_ENGINE.get_status(attr, value)
            icon = '🟢' if status == 'green' else ('🟡' if status == 'yellow' else '🔴')
            print(f"{name:<15} {formatter(value):<15} {target:<12} {icon}")
        else:
            print(f"{name:<15} {'N/A':<15} {target:<12} {'⚠️'}")
    
    if metrics.warnings:
        print("\n⚠️  Warnings:")
        for w in metrics.warnings:
            print(f"   • {w}")


# =============================================================================
# MAIN PROCESSING
# =============================================================================

def process_file(filepath: Path, move_after: bool = False) -> dict:
    """
    Process a single file through the pipeline.
    
    Args:
        filepath: Path to the file
        move_after: Whether to move file to archive after processing
    
    Returns:
        Parsed data dictionary
    """
    print(f"\n{'='*60}")
    print(f"Processing: {filepath.name}")
    print(f"{'='*60}")
    
    # 1. Identify file type
    file_type = identify_file_type(filepath)
    print(f"  Detected Type: {file_type}")
    
    if file_type == 'unknown':
        print("  ⚠️  Unknown file type - skipping")
        return {'error': 'Unknown file type'}
    
    # 2. Parse file
    print("  Parsing...")
    data = parse_file(filepath)
    
    if 'error' in data:
        print(f"  ❌ Parse Error: {data['error']}")
        return data
    
    # 3. Print metrics summary
    print_metrics_summary(data)
    
    # 4. Extract RAW data for ISPN calculations
    source = data.get('source', 'unknown')
    if source.startswith('genesys_'):
        raw_data = extract_raw_for_ispn(data)
        period = update_raw_data_store(source, raw_data)
        print(f"  ✓ Raw data stored for ISPN calculations (period: {period})")
    
    # 5. Validate (basic validation on raw data)
    print("  Validating...")
    is_valid, issues, statuses = validate_data(data)
    print_validation_results(is_valid, issues, statuses)
    
    # 6. Save parsed data
    output_dir = OUTPUT_DIRS.get(source, PARSED_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f"{filepath.stem}_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"  Saved: {output_file.relative_to(BASE_DIR)}")
    
    # 7. Update legacy metrics history (for backwards compatibility)
    metrics_to_track = {}
    if 'metrics' in data:
        metrics_to_track.update(data['metrics'])
    if 'totals' in data:
        metrics_to_track.update(data['totals'])
    
    if metrics_to_track:
        update_kpi_history(source, metrics_to_track, str(filepath))
    
    # 8. Move file to archive if requested
    if move_after:
        archive_dir = RAW_DIR / 'archive'
        archive_dir.mkdir(exist_ok=True)
        archived = archive_dir / f"{filepath.stem}_{timestamp}{filepath.suffix}"
        shutil.move(str(filepath), str(archived))
        print(f"  Archived: {archived.name}")
    
    return data


def process_directory(directory: Path, move_after: bool = False) -> list:
    """
    Process all supported files in a directory.
    """
    results = []
    
    # Supported extensions
    extensions = ['.csv', '.xlsx', '.xls']
    
    files = [f for f in directory.iterdir() 
             if f.is_file() and f.suffix.lower() in extensions]
    
    if not files:
        print(f"No supported files found in {directory}")
        return results
    
    print(f"Found {len(files)} files to process")
    
    for filepath in sorted(files):
        result = process_file(filepath, move_after)
        results.append({
            'file': str(filepath),
            'source': result.get('source', 'unknown'),
            'success': 'error' not in result,
        })
    
    return results


def add_manual_data(period: str = None, **kwargs):
    """
    Add manual data inputs for ISPN calculations.
    
    Args:
        period: Period to add data to (YYYY-MM format)
        **kwargs: Manual data values (training_hours, call_tickets, escalations, etc.)
    
    Example:
        add_manual_data(
            period='2025-01',
            training_hours=500,
            call_tickets=57743,
            escalations=17770,
            tech_review_scores=[94.3, 92.1, 95.0]
        )
    """
    if period is None:
        period = datetime.now().strftime('%Y-%m')
    
    store = load_raw_data_store()
    
    if period not in store['periods']:
        store['periods'][period] = {
            'interactions': {},
            'agent_status': {},
            'helpdesk': {},
            'quality': {},
            'manual': {},
            'metadata': {'files_processed': []}
        }
    
    period_data = store['periods'][period]
    
    # Map kwargs to appropriate sections
    helpdesk_fields = ['call_tickets', 'escalations', 'alert_tickets']
    quality_fields = ['tech_review_scores', 'efficacy_scores']
    manual_fields = ['training_hours', 'wave_call_count', 'wave_total_minutes', 'wave_awt_seconds']
    
    for key, value in kwargs.items():
        if key in helpdesk_fields:
            period_data['helpdesk'][key] = value
        elif key in quality_fields:
            period_data['quality'][key] = value
        elif key in manual_fields:
            period_data['manual'][key] = value
    
    save_raw_data_store(store)
    print(f"✓ Manual data added for period {period}")
    return period


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def main():
    """Main entry point."""
    ensure_dirs()
    
    # Check for --calculate flag
    if '--calculate' in sys.argv:
        # Run ISPN calculations
        period = None
        for i, arg in enumerate(sys.argv):
            if arg == '--period' and i + 1 < len(sys.argv):
                period = sys.argv[i + 1]
        
        print("="*60)
        print("Running ISPN Canonical Calculations")
        print("="*60)
        
        metrics, info = run_ispn_calculations(period)
        
        if metrics:
            print_ispn_calculations(metrics)
            print(f"\n✓ Metrics saved to: {METRICS_DIR / 'ispn_metrics_history.json'}")
        else:
            print(f"\n❌ Error: {info.get('error', 'Unknown error')}")
        
        return
    
    if len(sys.argv) > 1 and not sys.argv[1].startswith('--'):
        # Process specific file
        filepath = Path(sys.argv[1])
        if not filepath.exists():
            print(f"Error: File not found: {filepath}")
            sys.exit(1)
        
        process_file(filepath)
        
        # Prompt for ISPN calculation
        print("\n" + "="*60)
        print("TIP: Run with --calculate to compute ISPN metrics")
        print("     python scripts/ingest.py --calculate")
        print("="*60)
    else:
        # Process all files in raw directory
        results = process_directory(RAW_DIR)
        
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        
        success = sum(1 for r in results if r['success'])
        print(f"Processed: {len(results)} files")
        print(f"Success: {success}")
        print(f"Failed: {len(results) - success}")
        
        # Group by source type
        by_source = {}
        for r in results:
            source = r['source']
            by_source[source] = by_source.get(source, 0) + 1
        
        print("\nBy Source Type:")
        for source, count in sorted(by_source.items()):
            print(f"  {source}: {count}")
        
        # Prompt for ISPN calculation
        if results:
            print("\n" + "="*60)
            print("TIP: Run with --calculate to compute ISPN metrics")
            print("     python scripts/ingest.py --calculate")
            print("="*60)


if __name__ == '__main__':
    main()

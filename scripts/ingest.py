#!/usr/bin/env python3
"""
ISPN Data Ingestion Pipeline

Processes Genesys Cloud exports and internal ISPN files:
1. Auto-detects file type
2. Parses to structured JSON
3. Validates against ISPN standards
4. Stores to appropriate location
5. Updates metrics history

Usage:
    python scripts/ingest.py                    # Process all files in data/raw/
    python scripts/ingest.py path/to/file.csv   # Process single file
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.parsers import parse_file, identify_file_type
from utils.validators import validate_data, get_status, THRESHOLDS


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


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def ensure_dirs():
    """Create all required directories."""
    for d in OUTPUT_DIRS.values():
        d.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)


def update_kpi_history(source: str, metrics: dict, filepath: str):
    """
    Append metrics to KPI history file.
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
    
    print("  Key Metrics:")
    
    if source == 'genesys_interactions':
        m = data.get('metrics', {})
        print(f"    Records: {data.get('acd_count', 0):,} ACD calls")
        if 'avg_handle_time_min' in m:
            aht = m['avg_handle_time_min']
            status = get_status(aht, 'aht_min')
            icon = '🟢' if status == 'green' else ('🟡' if status == 'yellow' else '🔴')
            print(f"    AHT: {aht:.2f} min {icon}")
        if 'avg_wait_time_sec' in m:
            awt = m['avg_wait_time_sec']
            status = get_status(awt, 'awt_sec')
            icon = '🟢' if status == 'green' else ('🟡' if status == 'yellow' else '🔴')
            print(f"    AWT: {awt:.1f} sec {icon}")
        if 'abandon_rate' in m:
            abandon = m['abandon_rate']
            status = get_status(abandon, 'abandon_pct')
            icon = '🟢' if status == 'green' else ('🟡' if status == 'yellow' else '🔴')
            print(f"    Abandon Rate: {abandon:.2f}% {icon}")
    
    elif source == 'genesys_agent_performance':
        t = data.get('totals', {})
        print(f"    Agents: {data.get('agent_count', 0)}")
        print(f"    Total Calls: {t.get('total_calls', 0):,}")
        if 'avg_handle_min' in t:
            aht = t['avg_handle_min']
            status = get_status(aht, 'aht_min')
            icon = '🟢' if status == 'green' else ('🟡' if status == 'yellow' else '🔴')
            print(f"    Team AHT: {aht:.2f} min {icon}")
    
    elif source == 'genesys_agent_status':
        s = data.get('shrinkage', {})
        print(f"    Agents: {data.get('agent_count', 0)}")
        if 'total_pct' in s:
            shrink = s['total_pct']
            status = get_status(shrink, 'shrinkage_pct')
            icon = '🟢' if status == 'green' else ('🟡' if status == 'yellow' else '🔴')
            print(f"    Total Shrinkage: {shrink:.1f}% {icon} (target: <30%)")
        if 'on_queue_pct' in s:
            print(f"    On-Queue: {s['on_queue_pct']:.1f}%")
    
    elif source == 'genesys_skills_performance':
        t = data.get('totals', {})
        print(f"    Offered: {t.get('offered', 0):,}")
        print(f"    Answered: {t.get('answered', 0):,}")
        if 'answer_rate' in t:
            rate = t['answer_rate']
            status = get_status(rate, 'answer_rate_pct')
            icon = '🟢' if status == 'green' else ('🟡' if status == 'yellow' else '🔴')
            print(f"    Answer Rate: {rate:.1f}% {icon}")
        if 'abandon_rate' in t:
            abandon = t['abandon_rate']
            status = get_status(abandon, 'abandon_pct')
            icon = '🟢' if status == 'green' else ('🟡' if status == 'yellow' else '🔴')
            print(f"    Abandon Rate: {abandon:.1f}% {icon}")
    
    elif source == 'genesys_adherence':
        t = data.get('totals', {})
        print(f"    Agents: {data.get('agent_count', 0)}")
        if 'avg_adherence_pct' in t:
            adh = t['avg_adherence_pct']
            status = get_status(adh, 'adherence_pct')
            icon = '🟢' if status == 'green' else ('🟡' if status == 'yellow' else '🔴')
            print(f"    Adherence: {adh:.1f}% {icon} (target: >90%)")
        if 'avg_conformance_pct' in t:
            print(f"    Conformance: {t['avg_conformance_pct']:.1f}%")
    
    elif source == 'wfm_scheduled_required':
        s = data.get('summary', {})
        print(f"    Intervals: {s.get('total_intervals', 0)}")
        print(f"    Understaffed: {s.get('understaffed_intervals', 0)} ({s.get('understaffed_pct', 0):.1f}%)")
        print(f"    Overstaffed: {s.get('overstaffed_intervals', 0)}")
    
    elif source == 'agent_schedules':
        s = data.get('summary', {})
        print(f"    Total Agents: {s.get('total_agents', 0)}")
        print(f"    Schedulable: {s.get('schedulable', 0)}")
        if 'work_teams' in s:
            print(f"    Work Teams: {len(s['work_teams'])}")
    
    elif source == 'scorecard':
        kpis = data.get('kpis', {})
        for kpi, val in kpis.items():
            if val is not None:
                print(f"    {kpi}: {val:.2f}")


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
    
    # 4. Validate
    print("  Validating...")
    is_valid, issues, statuses = validate_data(data)
    print_validation_results(is_valid, issues, statuses)
    
    # 5. Save parsed data
    source = data.get('source', 'unknown')
    output_dir = OUTPUT_DIRS.get(source, PARSED_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f"{filepath.stem}_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"  Saved: {output_file.relative_to(BASE_DIR)}")
    
    # 6. Update metrics history
    metrics_to_track = {}
    if 'metrics' in data:
        metrics_to_track.update(data['metrics'])
    if 'totals' in data:
        metrics_to_track.update(data['totals'])
    if 'shrinkage' in data:
        metrics_to_track['shrinkage'] = data['shrinkage']
    
    if metrics_to_track:
        update_kpi_history(source, metrics_to_track, str(filepath))
    
    # 7. Move file to archive if requested
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


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def main():
    """Main entry point."""
    ensure_dirs()
    
    if len(sys.argv) > 1:
        # Process specific file
        filepath = Path(sys.argv[1])
        if not filepath.exists():
            print(f"Error: File not found: {filepath}")
            sys.exit(1)
        
        process_file(filepath)
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


if __name__ == '__main__':
    main()

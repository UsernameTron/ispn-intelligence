#!/usr/bin/env python3
"""
ISPN Data Ingestion Script
Watches data/raw/, parses files, validates, and stores in data/parsed/
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
import argparse

from utils.parsers import parse_file, identify_file_type
from utils.validators import validate_data
from utils.thresholds import get_all_statuses

# Paths
BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PARSED_DIR = BASE_DIR / "data" / "parsed"
METRICS_DIR = BASE_DIR / "data" / "metrics"
ARCHIVE_DIR = RAW_DIR / "archive"

def ensure_dirs():
    """Create necessary directories."""
    for d in [RAW_DIR, PARSED_DIR, METRICS_DIR, ARCHIVE_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    for subdir in ['dpr', 'wcs', 'scorecard', 'interactions']:
        (PARSED_DIR / subdir).mkdir(exist_ok=True)

def get_files_to_process() -> list:
    """Get all unprocessed files in raw directory."""
    files = []
    for ext in ['*.xlsx', '*.csv']:
        files.extend(RAW_DIR.glob(ext))
    return [f for f in files if f.is_file() and not f.name.startswith('.')]


def process_file(filepath: Path, archive: bool = True) -> dict:
    """
    Process a single file: parse, validate, store.
    Returns processing result.
    """
    print(f"\nProcessing: {filepath.name}")
    
    # Identify file type
    file_type = identify_file_type(filepath)
    print(f"  Type: {file_type}")
    
    if file_type == 'unknown':
        return {
            'file': filepath.name,
            'status': 'skipped',
            'reason': 'Unknown file type'
        }
    
    # Parse file
    try:
        data = parse_file(filepath)
    except Exception as e:
        return {
            'file': filepath.name,
            'status': 'error',
            'reason': f'Parse error: {str(e)}'
        }
    
    # Validate
    is_valid, issues = validate_data(data)
    data['validation'] = {
        'is_valid': is_valid,
        'issues': issues
    }
    
    if issues:
        print(f"  Warnings: {issues}")
    
    # Calculate statuses for scorecard
    if file_type == 'scorecard' and 'kpis' in data:
        data['statuses'] = get_all_statuses(data['kpis'])
    
    # Generate output filename
    timestamp = datetime.now().strftime('%Y-%m-%d')
    output_file = PARSED_DIR / file_type / f"{timestamp}.json"
    
    # Save parsed data
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"  Saved: {output_file}")
    
    # Update KPI history if scorecard
    if file_type == 'scorecard':
        update_kpi_history(data)
    
    # Archive original
    if archive:
        archive_file = ARCHIVE_DIR / f"{timestamp}_{filepath.name}"
        shutil.move(str(filepath), str(archive_file))
        print(f"  Archived: {archive_file.name}")
    
    return {
        'file': filepath.name,
        'status': 'success',
        'type': file_type,
        'output': str(output_file),
        'valid': is_valid
    }


def update_kpi_history(scorecard_data: dict):
    """Append scorecard KPIs to historical time series."""
    history_file = METRICS_DIR / "kpi_history.json"
    
    # Load existing history
    if history_file.exists():
        with open(history_file, 'r') as f:
            history = json.load(f)
    else:
        history = {'periods': {}}
    
    # Determine period (use current month)
    period = datetime.now().strftime('%Y-%m')
    
    # Add this period's data
    history['periods'][period] = {
        'kpis': scorecard_data.get('kpis', {}),
        'statuses': scorecard_data.get('statuses', {}),
        'ingested_at': datetime.now().isoformat()
    }
    history['last_updated'] = datetime.now().isoformat()
    
    # Save
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)
    print(f"  Updated KPI history: {period}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='ISPN Data Ingestion')
    parser.add_argument('--no-archive', action='store_true', 
                        help='Do not archive processed files')
    parser.add_argument('--file', type=str, 
                        help='Process specific file instead of all')
    args = parser.parse_args()
    
    ensure_dirs()
    
    print("=" * 60)
    print("ISPN Data Ingestion")
    print("=" * 60)
    
    if args.file:
        files = [Path(args.file)]
    else:
        files = get_files_to_process()
    
    if not files:
        print("\nNo files to process in data/raw/")
        print("Drop Genesys exports there and run again.")
        return
    
    print(f"\nFound {len(files)} file(s) to process")
    
    results = []
    for f in files:
        result = process_file(f, archive=not args.no_archive)
        results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    success = [r for r in results if r['status'] == 'success']
    errors = [r for r in results if r['status'] == 'error']
    skipped = [r for r in results if r['status'] == 'skipped']
    
    print(f"  Success: {len(success)}")
    print(f"  Errors:  {len(errors)}")
    print(f"  Skipped: {len(skipped)}")
    
    if errors:
        print("\nErrors:")
        for r in errors:
            print(f"  - {r['file']}: {r['reason']}")


if __name__ == '__main__':
    main()

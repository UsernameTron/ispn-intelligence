"""
ISPN File Parsers
Parse Genesys exports into structured JSON
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import re

def parse_scorecard(filepath: Path) -> dict:
    """
    Parse LT Scorecard Excel file.
    Sheet: ISPN_Scorecard-Monthly_INPUT
    Key rows: 52-65 for 9 core KPIs
    """
    df = pd.read_excel(filepath, sheet_name='ISPN_Scorecard-Monthly_INPUT', header=None)
    
    # Find the most recent month column with data
    # FY columns: FY24 (BC-BN), FY25 (BO-BZ), FY26 (CA-CL)
    # We'll scan from right to left to find the latest populated column
    
    result = {
        'source': 'scorecard',
        'filepath': str(filepath),
        'parsed_at': datetime.now().isoformat(),
        'kpis': {}
    }
    
    # Row mappings (0-indexed, so subtract 1)
    kpi_rows = {
        'calls_offered': 51,  # Row 52
        'aht': 57,            # Row 58
        'awt': 58,            # Row 59
        'fcr': 59,            # Row 60
        'escalation': 60,     # Row 61
        'utilization': 61,    # Row 62
        'shrinkage': 62,      # Row 63
        'quality': 63,        # Row 64
        'headcount': 64       # Row 65
    }
    
    # Find latest month column (scan from right)
    for col in range(df.shape[1] - 1, 0, -1):
        # Check if column has numeric data in KPI rows
        has_data = False
        for row in kpi_rows.values():
            val = df.iloc[row, col] if row < df.shape[0] else None
            if pd.notna(val) and isinstance(val, (int, float)):
                has_data = True
                break
        
        if has_data:
            # Extract KPIs from this column
            for kpi, row in kpi_rows.items():
                if row < df.shape[0]:
                    val = df.iloc[row, col]
                    if pd.notna(val):
                        result['kpis'][kpi] = float(val) if isinstance(val, (int, float)) else None
            break
    
    return result


def parse_dpr(filepath: Path) -> dict:
    """
    Parse Daily Performance Report Excel file.
    Sheet names are month abbreviations (OCT23, NOV23, etc.)
    """
    xl = pd.ExcelFile(filepath)
    
    result = {
        'source': 'dpr',
        'filepath': str(filepath),
        'parsed_at': datetime.now().isoformat(),
        'days': []
    }
    
    # Find most recent sheet (month)
    sheets = xl.sheet_names
    if not sheets:
        return result
    
    # Use first sheet that looks like a month
    for sheet in sheets:
        if re.match(r'[A-Z]{3}\d{2}', sheet):
            df = pd.read_excel(filepath, sheet_name=sheet)
            
            # Look for key columns
            cols = df.columns.tolist()
            date_col = next((c for c in cols if 'date' in str(c).lower()), None)
            calls_col = next((c for c in cols if 'call' in str(c).lower() and 'total' in str(c).lower()), None)
            aht_col = next((c for c in cols if 'aht' in str(c).lower() or 'handle' in str(c).lower()), None)
            fcr_col = next((c for c in cols if 'fcr' in str(c).lower()), None)
            
            # Extract daily data
            for idx, row in df.iterrows():
                day_data = {}
                if date_col and pd.notna(row.get(date_col)):
                    day_data['date'] = str(row[date_col])
                if calls_col and pd.notna(row.get(calls_col)):
                    day_data['calls'] = float(row[calls_col])
                if aht_col and pd.notna(row.get(aht_col)):
                    day_data['aht'] = float(row[aht_col])
                if fcr_col and pd.notna(row.get(fcr_col)):
                    day_data['fcr'] = float(row[fcr_col])
                
                if day_data:
                    result['days'].append(day_data)
            break
    
    return result


def parse_wcs(filepath: Path) -> dict:
    """
    Parse Weekly Call Statistics Excel file.
    Sheet "CD data 2": 168-row hourly breakdown
    Partner summary tabs for aggregated metrics
    """
    xl = pd.ExcelFile(filepath)
    
    result = {
        'source': 'wcs',
        'filepath': str(filepath),
        'parsed_at': datetime.now().isoformat(),
        'hourly_data': [],
        'partners': {}
    }
    
    # Parse CD data 2 for hourly breakdown
    if 'CD data 2' in xl.sheet_names:
        df = pd.read_excel(filepath, sheet_name='CD data 2')
        result['hourly_row_count'] = len(df)
        result['hourly_valid'] = len(df) == 168
    
    # Parse partner tabs
    for sheet in xl.sheet_names:
        if sheet not in ['CD data 2', 'Summary', 'Instructions']:
            try:
                df = pd.read_excel(filepath, sheet_name=sheet)
                # Extract partner metrics (simplified)
                result['partners'][sheet] = {
                    'row_count': len(df)
                }
            except:
                pass
    
    return result


def parse_interactions(filepath: Path) -> dict:
    """
    Parse Interactions CSV from Genesys Cloud.
    Call-level detail for AHT distribution, abandon timing, etc.
    """
    df = pd.read_csv(filepath)
    
    result = {
        'source': 'interactions',
        'filepath': str(filepath),
        'parsed_at': datetime.now().isoformat(),
        'record_count': len(df),
        'columns': df.columns.tolist()
    }
    
    # Calculate aggregates if expected columns exist
    if 'HandleTime' in df.columns:
        result['avg_handle_time'] = df['HandleTime'].mean()
    if 'QueueTime' in df.columns:
        result['avg_queue_time'] = df['QueueTime'].mean()
    
    return result


def identify_file_type(filepath: Path) -> str:
    """
    Identify file type based on filename pattern.
    Returns: 'scorecard', 'dpr', 'wcs', 'interactions', or 'unknown'
    """
    name = filepath.name.lower()
    
    if 'scorecard' in name:
        return 'scorecard'
    elif name.startswith('dpr'):
        return 'dpr'
    elif name.startswith('wcs') or re.match(r'\d{6}-\d{6}', name):
        return 'wcs'
    elif name.startswith('interactions'):
        return 'interactions'
    else:
        return 'unknown'


def parse_file(filepath: Path) -> dict:
    """
    Auto-detect file type and parse accordingly.
    """
    file_type = identify_file_type(filepath)
    
    parsers = {
        'scorecard': parse_scorecard,
        'dpr': parse_dpr,
        'wcs': parse_wcs,
        'interactions': parse_interactions
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

"""
ISPN Data Validators
Validate parsed data before storage
"""

from typing import Tuple, List

def validate_scorecard(data: dict) -> Tuple[bool, List[str]]:
    """
    Validate parsed scorecard data.
    Returns: (is_valid, list of warnings/errors)
    """
    issues = []
    
    kpis = data.get('kpis', {})
    
    # Check for required KPIs
    required = ['aht', 'awt', 'fcr', 'escalation', 'utilization', 'quality']
    for kpi in required:
        if kpi not in kpis or kpis[kpi] is None:
            issues.append(f"Missing required KPI: {kpi}")
    
    # Validate ranges
    if 'aht' in kpis and kpis['aht'] is not None:
        if kpis['aht'] < 1 or kpis['aht'] > 60:
            issues.append(f"AHT out of expected range: {kpis['aht']}")
    
    if 'fcr' in kpis and kpis['fcr'] is not None:
        if kpis['fcr'] < 0 or kpis['fcr'] > 100:
            issues.append(f"FCR out of expected range: {kpis['fcr']}")
    
    if 'utilization' in kpis and kpis['utilization'] is not None:
        if kpis['utilization'] < 0 or kpis['utilization'] > 100:
            issues.append(f"Utilization out of expected range: {kpis['utilization']}")
    
    is_valid = len([i for i in issues if 'Missing required' in i]) == 0
    return is_valid, issues


def validate_wcs(data: dict) -> Tuple[bool, List[str]]:
    """
    Validate parsed WCS data.
    CD data 2 should have exactly 168 rows (24hrs × 7days)
    """
    issues = []
    
    if not data.get('hourly_valid', False):
        row_count = data.get('hourly_row_count', 0)
        issues.append(f"CD data 2 has {row_count} rows, expected 168")
    
    if not data.get('partners'):
        issues.append("No partner data found")
    
    is_valid = data.get('hourly_valid', False)
    return is_valid, issues


def validate_dpr(data: dict) -> Tuple[bool, List[str]]:
    """
    Validate parsed DPR data.
    """
    issues = []
    
    days = data.get('days', [])
    if len(days) == 0:
        issues.append("No daily data found")
    
    is_valid = len(days) > 0
    return is_valid, issues


def validate_data(data: dict) -> Tuple[bool, List[str]]:
    """
    Auto-detect source and validate accordingly.
    """
    source = data.get('source', 'unknown')
    
    validators = {
        'scorecard': validate_scorecard,
        'wcs': validate_wcs,
        'dpr': validate_dpr
    }
    
    if source in validators:
        return validators[source](data)
    else:
        return True, []

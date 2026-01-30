"""
ISPN Threshold Logic
Centralized GREEN/YELLOW/RED status calculations
"""

import json
from pathlib import Path

TARGETS_FILE = Path(__file__).parent.parent.parent / "data" / "metrics" / "targets.json"

def load_targets():
    """Load targets from JSON file."""
    with open(TARGETS_FILE, 'r') as f:
        return json.load(f)

def get_status(metric: str, value: float, targets: dict = None) -> str:
    """
    Calculate status for a given metric value.
    Returns: 'GREEN', 'YELLOW', or 'RED'
    """
    if targets is None:
        targets = load_targets()
    
    if metric not in targets:
        return 'UNKNOWN'
    
    t = targets[metric]
    direction = t.get('direction', 'lower_better')
    
    # Handle range-based metrics (utilization)
    if direction == 'range':
        if value < t.get('red_low', 0) or value > t.get('red_high', 100):
            return 'RED'
        elif value < t.get('yellow_low', 0) or value > t.get('yellow_high', 100):
            return 'YELLOW'
        elif t.get('target_low', 0) <= value <= t.get('target_high', 100):
            return 'GREEN'
        return 'YELLOW'
    
    # Handle lower-is-better metrics (AHT, AWT, escalation, abandon, shrinkage)
    elif direction == 'lower_better':
        if value > t.get('red', float('inf')):
            return 'RED'
        elif value > t.get('yellow', float('inf')):
            return 'YELLOW'
        elif value <= t.get('target', float('inf')):
            return 'GREEN'
        return 'YELLOW'
    
    # Handle higher-is-better metrics (FCR, quality)
    elif direction == 'higher_better':
        if value < t.get('red', 0):
            return 'RED'
        elif value < t.get('yellow', 0):
            return 'YELLOW'
        elif value >= t.get('target', 0):
            return 'GREEN'
        return 'YELLOW'
    
    return 'UNKNOWN'

def get_all_statuses(metrics: dict) -> dict:
    """
    Calculate status for all metrics in a dict.
    Returns dict with {metric: {value, target, status}}
    """
    targets = load_targets()
    results = {}
    
    for metric, value in metrics.items():
        if metric in targets:
            t = targets[metric]
            target = t.get('target') or t.get('target_low', 'N/A')
            results[metric] = {
                'value': value,
                'target': target,
                'status': get_status(metric, value, targets)
            }
    
    return results

def count_by_status(statuses: dict) -> dict:
    """Count metrics by status."""
    counts = {'GREEN': 0, 'YELLOW': 0, 'RED': 0, 'UNKNOWN': 0}
    for metric, data in statuses.items():
        status = data.get('status', 'UNKNOWN')
        counts[status] = counts.get(status, 0) + 1
    return counts

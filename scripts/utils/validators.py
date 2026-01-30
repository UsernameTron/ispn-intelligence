"""
ISPN Data Validators
Validate parsed Genesys exports against ISPN standards

Thresholds based on ISPN operational targets:
- AHT: < 10.7 min (warning: 11.5, critical: 12.0)
- AWT: < 90 sec (warning: 120, critical: 180)
- FCR: > 70% (warning: 65%, critical: 60%)
- Abandon: < 5% (warning: 8%, critical: 10%)
- Utilization: 55-65% (warning: <50% or >70%)
- Shrinkage: < 30% (warning: 35%, critical: 40%)
- Adherence: > 90% (warning: 85%, critical: 80%)
- Occupancy: 75-85% (warning: <70% or >90%)
"""

from typing import Tuple, List, Dict, Any


# =============================================================================
# THRESHOLD DEFINITIONS
# =============================================================================

THRESHOLDS = {
    'aht_min': {'target': 10.7, 'warning': 11.5, 'critical': 12.0},
    'awt_sec': {'target': 90, 'warning': 120, 'critical': 180},
    'fcr_pct': {'target': 70, 'warning': 65, 'critical': 60},
    'abandon_pct': {'target': 5, 'warning': 8, 'critical': 10},
    'utilization_pct': {'target_low': 55, 'target_high': 65, 'warning_low': 50, 'warning_high': 70},
    'shrinkage_pct': {'target': 30, 'warning': 35, 'critical': 40},
    'adherence_pct': {'target': 90, 'warning': 85, 'critical': 80},
    'occupancy_pct': {'target_low': 75, 'target_high': 85, 'warning_low': 70, 'warning_high': 90},
    'answer_rate_pct': {'target': 90, 'warning': 85, 'critical': 80},
    'on_queue_pct': {'target': 70, 'warning': 60, 'critical': 50},
}


def get_status(value: float, metric: str) -> str:
    """
    Determine status (green/yellow/red) based on threshold.
    
    Returns: 'green', 'yellow', or 'red'
    """
    if metric not in THRESHOLDS:
        return 'unknown'
    
    t = THRESHOLDS[metric]
    
    # Metrics where lower is better
    if metric in ['aht_min', 'awt_sec', 'abandon_pct', 'shrinkage_pct']:
        if value <= t['target']:
            return 'green'
        elif value <= t['warning']:
            return 'yellow'
        else:
            return 'red'
    
    # Metrics where higher is better
    elif metric in ['fcr_pct', 'adherence_pct', 'answer_rate_pct', 'on_queue_pct']:
        if value >= t['target']:
            return 'green'
        elif value >= t['warning']:
            return 'yellow'
        else:
            return 'red'
    
    # Range metrics
    elif metric in ['utilization_pct', 'occupancy_pct']:
        if t['target_low'] <= value <= t['target_high']:
            return 'green'
        elif t['warning_low'] <= value <= t['warning_high']:
            return 'yellow'
        else:
            return 'red'
    
    return 'unknown'


# =============================================================================
# GENESYS INTERACTIONS VALIDATOR
# =============================================================================

def validate_interactions(data: dict) -> Tuple[bool, List[str], Dict[str, str]]:
    """
    Validate parsed Interactions export.
    
    Returns: (is_valid, issues, statuses)
    """
    issues = []
    statuses = {}
    
    # Required fields
    if not data.get('field_validation', {}).get('Total Handle', False):
        issues.append("CRITICAL: Missing 'Total Handle' column")
    if not data.get('field_validation', {}).get('Abandoned', False):
        issues.append("CRITICAL: Missing 'Abandoned' column")
    
    # Record count validation
    record_count = data.get('record_count', 0)
    if record_count == 0:
        issues.append("CRITICAL: No records found")
    elif record_count < 100:
        issues.append(f"WARNING: Low record count ({record_count})")
    
    # ACD filtering
    acd_count = data.get('acd_count', 0)
    total_count = data.get('total_count', 0)
    if total_count > 0 and acd_count / total_count < 0.5:
        issues.append(f"WARNING: High Non-ACD ratio ({(1 - acd_count/total_count)*100:.1f}%)")
    
    # Metric validations
    metrics = data.get('metrics', {})
    
    if 'avg_handle_time_min' in metrics:
        aht = metrics['avg_handle_time_min']
        statuses['aht'] = get_status(aht, 'aht_min')
        if statuses['aht'] == 'red':
            issues.append(f"RED: AHT {aht:.2f} min exceeds critical threshold")
        elif statuses['aht'] == 'yellow':
            issues.append(f"YELLOW: AHT {aht:.2f} min exceeds target")
    
    if 'avg_wait_time_sec' in metrics:
        awt = metrics['avg_wait_time_sec']
        statuses['awt'] = get_status(awt, 'awt_sec')
        if statuses['awt'] == 'red':
            issues.append(f"RED: AWT {awt:.1f} sec exceeds critical threshold")
        elif statuses['awt'] == 'yellow':
            issues.append(f"YELLOW: AWT {awt:.1f} sec exceeds target")
    
    if 'abandon_rate' in metrics:
        abandon = metrics['abandon_rate']
        statuses['abandon'] = get_status(abandon, 'abandon_pct')
        if statuses['abandon'] == 'red':
            issues.append(f"RED: Abandon rate {abandon:.1f}% exceeds critical threshold")
        elif statuses['abandon'] == 'yellow':
            issues.append(f"YELLOW: Abandon rate {abandon:.1f}% exceeds target")
    
    # ACW timeout analysis
    if 'acw_timeout_pct' in metrics and metrics['acw_timeout_pct'] > 80:
        issues.append(f"INFO: High ACW timeout rate ({metrics['acw_timeout_pct']:.1f}%) - agents may need more wrap-up time")
    
    is_valid = not any('CRITICAL' in i for i in issues)
    return is_valid, issues, statuses


# =============================================================================
# AGENT PERFORMANCE VALIDATOR
# =============================================================================

def validate_agent_performance(data: dict) -> Tuple[bool, List[str], Dict[str, str]]:
    """
    Validate parsed Agent Performance Summary export.
    """
    issues = []
    statuses = {}
    
    agent_count = data.get('agent_count', 0)
    if agent_count == 0:
        issues.append("CRITICAL: No agent data found")
    elif agent_count < 10:
        issues.append(f"WARNING: Low agent count ({agent_count})")
    
    totals = data.get('totals', {})
    
    if 'avg_handle_min' in totals:
        aht = totals['avg_handle_min']
        statuses['aht'] = get_status(aht, 'aht_min')
        if statuses['aht'] == 'red':
            issues.append(f"RED: Team AHT {aht:.2f} min exceeds critical threshold")
        elif statuses['aht'] == 'yellow':
            issues.append(f"YELLOW: Team AHT {aht:.2f} min exceeds target")
    
    # Identify high-AHT agents
    agents = data.get('agents', {})
    high_aht_agents = []
    for name, agent_data in agents.items():
        if agent_data.get('avg_handle_min', 0) > THRESHOLDS['aht_min']['critical']:
            high_aht_agents.append(name)
    
    if high_aht_agents:
        issues.append(f"INFO: {len(high_aht_agents)} agents exceed critical AHT threshold")
    
    is_valid = not any('CRITICAL' in i for i in issues)
    return is_valid, issues, statuses


# =============================================================================
# AGENT STATUS VALIDATOR
# =============================================================================

def validate_agent_status(data: dict) -> Tuple[bool, List[str], Dict[str, str]]:
    """
    Validate parsed Agent Status Summary export.
    """
    issues = []
    statuses = {}
    
    agent_count = data.get('agent_count', 0)
    if agent_count == 0:
        issues.append("CRITICAL: No agent data found")
    
    shrinkage = data.get('shrinkage', {})
    
    if 'total_pct' in shrinkage:
        shrink = shrinkage['total_pct']
        statuses['shrinkage'] = get_status(shrink, 'shrinkage_pct')
        if statuses['shrinkage'] == 'red':
            issues.append(f"RED: Shrinkage {shrink:.1f}% exceeds critical threshold (target: <30%)")
        elif statuses['shrinkage'] == 'yellow':
            issues.append(f"YELLOW: Shrinkage {shrink:.1f}% exceeds target")
    
    if 'on_queue_pct' in shrinkage:
        on_queue = shrinkage['on_queue_pct']
        statuses['on_queue'] = get_status(on_queue, 'on_queue_pct')
        if statuses['on_queue'] == 'red':
            issues.append(f"RED: On-queue time {on_queue:.1f}% below critical threshold")
    
    if 'unplanned_pct' in shrinkage and shrinkage['unplanned_pct'] > 15:
        issues.append(f"WARNING: High unplanned shrinkage ({shrinkage['unplanned_pct']:.1f}%)")
    
    is_valid = not any('CRITICAL' in i for i in issues)
    return is_valid, issues, statuses


# =============================================================================
# SKILLS PERFORMANCE VALIDATOR
# =============================================================================

def validate_skills_performance(data: dict) -> Tuple[bool, List[str], Dict[str, str]]:
    """
    Validate parsed Skills Performance export.
    """
    issues = []
    statuses = {}
    
    totals = data.get('totals', {})
    
    if 'answer_rate' in totals:
        rate = totals['answer_rate']
        statuses['answer_rate'] = get_status(rate, 'answer_rate_pct')
        if statuses['answer_rate'] == 'red':
            issues.append(f"RED: Answer rate {rate:.1f}% below critical threshold")
        elif statuses['answer_rate'] == 'yellow':
            issues.append(f"YELLOW: Answer rate {rate:.1f}% below target")
    
    if 'abandon_rate' in totals:
        abandon = totals['abandon_rate']
        statuses['abandon'] = get_status(abandon, 'abandon_pct')
        if statuses['abandon'] == 'red':
            issues.append(f"RED: Abandon rate {abandon:.1f}% exceeds critical threshold")
    
    # Check for queues with poor performance
    by_queue = data.get('by_queue', {})
    poor_queues = []
    for queue, stats in by_queue.items():
        offered = stats.get('offered', 0)
        answered = stats.get('answered', 0)
        if offered > 50 and answered / offered < 0.8:
            poor_queues.append(queue)
    
    if poor_queues:
        issues.append(f"WARNING: {len(poor_queues)} queues below 80% answer rate")
    
    is_valid = not any('CRITICAL' in i for i in issues)
    return is_valid, issues, statuses


# =============================================================================
# ADHERENCE VALIDATOR
# =============================================================================

def validate_adherence(data: dict) -> Tuple[bool, List[str], Dict[str, str]]:
    """
    Validate parsed Historical Adherence export.
    """
    issues = []
    statuses = {}
    
    agent_count = data.get('agent_count', 0)
    if agent_count == 0:
        issues.append("CRITICAL: No adherence data found")
    
    totals = data.get('totals', {})
    
    if 'avg_adherence_pct' in totals:
        adherence = totals['avg_adherence_pct']
        statuses['adherence'] = get_status(adherence, 'adherence_pct')
        if statuses['adherence'] == 'red':
            issues.append(f"RED: Adherence {adherence:.1f}% below critical threshold (target: >90%)")
        elif statuses['adherence'] == 'yellow':
            issues.append(f"YELLOW: Adherence {adherence:.1f}% below target")
    
    if 'avg_conformance_pct' in totals:
        conformance = totals['avg_conformance_pct']
        if conformance < 80:
            issues.append(f"WARNING: Conformance {conformance:.1f}% indicates schedule issues")
    
    # Identify low-adherence agents
    agents = data.get('agents', {})
    low_adherence_agents = [name for name, d in agents.items() 
                           if d.get('adherence_pct', 100) < 70]
    
    if len(low_adherence_agents) > agent_count * 0.2:
        issues.append(f"WARNING: {len(low_adherence_agents)} agents ({len(low_adherence_agents)/agent_count*100:.0f}%) below 70% adherence")
    
    is_valid = not any('CRITICAL' in i for i in issues)
    return is_valid, issues, statuses


# =============================================================================
# WFM SCHEDULED/REQUIRED VALIDATOR
# =============================================================================

def validate_wfm_scheduled(data: dict) -> Tuple[bool, List[str], Dict[str, str]]:
    """
    Validate parsed WFM Scheduled/Required export.
    """
    issues = []
    statuses = {}
    
    summary = data.get('summary', {})
    
    understaffed_pct = summary.get('understaffed_pct', 0)
    if understaffed_pct > 30:
        statuses['staffing'] = 'red'
        issues.append(f"RED: {understaffed_pct:.1f}% of intervals understaffed")
    elif understaffed_pct > 15:
        statuses['staffing'] = 'yellow'
        issues.append(f"YELLOW: {understaffed_pct:.1f}% of intervals understaffed")
    else:
        statuses['staffing'] = 'green'
    
    avg_diff = summary.get('avg_difference', 0)
    if avg_diff < -2:
        issues.append(f"WARNING: Average understaffing of {abs(avg_diff):.1f} FTE")
    elif avg_diff > 5:
        issues.append(f"INFO: Average overstaffing of {avg_diff:.1f} FTE - VTO opportunity")
    
    is_valid = True
    return is_valid, issues, statuses


# =============================================================================
# AGENT SCHEDULES VALIDATOR
# =============================================================================

def validate_agent_schedules(data: dict) -> Tuple[bool, List[str], Dict[str, str]]:
    """
    Validate parsed Agent Permanent Schedules export.
    """
    issues = []
    statuses = {}
    
    summary = data.get('summary', {})
    
    total = summary.get('total_agents', 0)
    schedulable = summary.get('schedulable', 0)
    
    if total == 0:
        issues.append("CRITICAL: No agents found")
    elif schedulable < total * 0.9:
        issues.append(f"WARNING: Only {schedulable}/{total} agents schedulable")
    
    # Check skill distribution
    top_skills = summary.get('top_skills', {})
    if top_skills:
        most_common = max(top_skills.values())
        if most_common < total * 0.5:
            issues.append("INFO: Skill coverage may be fragmented")
    
    is_valid = not any('CRITICAL' in i for i in issues)
    return is_valid, issues, statuses


# =============================================================================
# LEGACY VALIDATORS
# =============================================================================

def validate_scorecard(data: dict) -> Tuple[bool, List[str]]:
    """Validate parsed scorecard data."""
    issues = []
    
    kpis = data.get('kpis', {})
    required = ['aht', 'awt', 'fcr', 'escalation', 'utilization', 'quality']
    
    for kpi in required:
        if kpi not in kpis or kpis[kpi] is None:
            issues.append(f"Missing required KPI: {kpi}")
    
    if 'aht' in kpis and kpis['aht'] is not None:
        if kpis['aht'] < 1 or kpis['aht'] > 60:
            issues.append(f"AHT out of expected range: {kpis['aht']}")
    
    is_valid = len([i for i in issues if 'Missing required' in i]) == 0
    return is_valid, issues


def validate_wcs(data: dict) -> Tuple[bool, List[str]]:
    """Validate parsed WCS data."""
    issues = []
    
    if not data.get('hourly_valid', False):
        row_count = data.get('hourly_row_count', 0)
        issues.append(f"CD data 2 has {row_count} rows, expected 168")
    
    is_valid = data.get('hourly_valid', False)
    return is_valid, issues


def validate_dpr(data: dict) -> Tuple[bool, List[str]]:
    """Validate parsed DPR data."""
    issues = []
    days = data.get('days', [])
    
    if len(days) == 0:
        issues.append("No daily data found")
    
    is_valid = len(days) > 0
    return is_valid, issues


# =============================================================================
# MAIN VALIDATOR
# =============================================================================

def validate_data(data: dict) -> Tuple[bool, List[str], Dict[str, str]]:
    """
    Auto-detect source and validate accordingly.
    
    Returns: (is_valid, issues, statuses)
    """
    source = data.get('source', 'unknown')
    
    validators = {
        'genesys_interactions': validate_interactions,
        'genesys_agent_performance': validate_agent_performance,
        'genesys_agent_status': validate_agent_status,
        'genesys_skills_performance': validate_skills_performance,
        'genesys_adherence': validate_adherence,
        'wfm_scheduled_required': validate_wfm_scheduled,
        'agent_schedules': validate_agent_schedules,
    }
    
    if source in validators:
        return validators[source](data)
    
    # Legacy validators (return 2 values)
    legacy = {
        'scorecard': validate_scorecard,
        'wcs': validate_wcs,
        'dpr': validate_dpr,
    }
    
    if source in legacy:
        is_valid, issues = legacy[source](data)
        return is_valid, issues, {}
    
    return True, [], {}

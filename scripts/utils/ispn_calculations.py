"""
ISPN Canonical Calculations Engine
===================================
Single Source of Truth for ALL KPI calculations.

This module implements the EXACT formulas from Charlie's LT Scorecard.
ALL metrics MUST flow through this module - never use pre-calculated
values from Genesys exports directly.

Source: ISPN_iGLASS_LT_Scorecard_Weekly_Monthly_2025.xlsx
        "Tech Center -->HOW TO CALCULATE" sheet
        Charlie's_LT_Scorecard_Formulas.docx

Author: Pete Connor (Director, Technical Center Operations)
Date: 2026-01-30
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
import json


# =============================================================================
# CONSTANTS - DO NOT MODIFY
# =============================================================================

# Fixed ACW assumption per ISPN standard (15 seconds per call)
ISPN_ACW_SECONDS_PER_CALL = 15

# Time conversion factors
MS_TO_SECONDS = 1 / 1000
MS_TO_MINUTES = 1 / 60000
MS_TO_HOURS = 1 / 3600000
SECONDS_TO_HOURS = 1 / 3600
MINUTES_TO_HOURS = 1 / 60

# Minimum call duration to count (Genesys standard: >20 seconds)
MIN_CALL_DURATION_SECONDS = 20

# FY25 KPI Targets (from 9 KPIs-Monthly sheet)
TARGETS = {
    'fcr_pct': {'target': 0.70, 'direction': 'above'},
    'escalation_pct': {'target': 0.30, 'direction': 'below'},
    'aht_minutes': {'target': 10.7, 'direction': 'below'},
    'awt_seconds': {'target': 90, 'direction': 'below'},
    'utilization_pct': {'target': 0.55, 'direction': 'above'},
    'occupancy_pct': {'target': 0.65, 'direction': 'above'},  # Implicit from utilization
    'shrinkage_pct': {'target': 0.30, 'direction': 'below'},
    'quality_score': {'target': 88.0, 'direction': 'above'},
    'abandon_pct': {'target': 0.05, 'direction': 'below'},
    'adherence_pct': {'target': 0.90, 'direction': 'above'},
}


# =============================================================================
# RAW DATA CONTAINERS
# =============================================================================

@dataclass
class GenesysRawData:
    """
    Raw data extracted from Genesys exports.
    These values feed into ISPN calculations - NEVER use Genesys
    pre-calculated percentages directly.
    """
    # From Interactions Export
    inbound_call_count: int = 0                  # Calls with Total Handle > 20s
    inbound_total_handle_ms: int = 0             # Sum of Total Handle for inbound
    inbound_total_talk_ms: int = 0               # Sum of Total Talk
    inbound_total_hold_ms: int = 0               # Sum of Total Hold
    inbound_total_acw_ms: int = 0                # Sum of Total ACW (actual measured)
    inbound_total_queue_ms: int = 0              # Sum of Total Queue (wait time)
    
    outbound_call_count: int = 0
    outbound_total_handle_ms: int = 0
    
    callback_call_count: int = 0
    callback_total_handle_ms: int = 0
    
    abandoned_call_count: int = 0                # Abandoned = YES
    abandoned_after_60s_count: int = 0           # Abandoned with queue > 60s
    
    # Answer threshold counts
    answered_under_30s: int = 0
    answered_under_60s: int = 0
    answered_under_90s: int = 0
    answered_under_120s: int = 0
    
    # From Agent Status Duration Details Export
    total_logged_in_ms: int = 0                  # Sum of Logged In across all agents
    total_on_queue_ms: int = 0                   # Sum of On Queue across all agents
    total_interacting_ms: int = 0                # Sum of Interacting (actual call time)
    total_idle_ms: int = 0                       # Sum of Idle
    total_available_ms: int = 0                  # Sum of Available
    total_away_ms: int = 0                       # Sum of Away
    total_break_ms: int = 0                      # Sum of Break
    total_meal_ms: int = 0                       # Sum of Meal
    total_not_responding_ms: int = 0             # Sum of Not Responding
    
    # From UKG / Manual Input (NOT from Genesys)
    training_hours: float = 0.0                  # Manual input required
    
    # From Helpdesk System (NOT from Genesys)
    call_tickets: int = 0                        # Total tickets from calls
    escalations: int = 0                         # Escalated tickets
    alert_tickets: int = 0                       # Alert-related tickets
    
    # From QA System
    efficacy_scores: list = field(default_factory=list)
    tech_review_scores: list = field(default_factory=list)
    
    # Metadata
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    agent_count: int = 0
    
    # Wave/Secondary Platform Data (if applicable)
    wave_call_count: int = 0
    wave_total_minutes: float = 0.0
    wave_awt_seconds: float = 0.0


@dataclass 
class ISPNCalculatedMetrics:
    """
    Metrics calculated using ISPN canonical formulas.
    These are the ONLY values that should appear in board reports.
    """
    # Primary KPIs (9 KPIs-Monthly)
    fcr_pct: Optional[float] = None
    escalation_pct: Optional[float] = None
    aht_minutes: Optional[float] = None
    awt_seconds: Optional[float] = None
    utilization_pct: Optional[float] = None
    occupancy_pct: Optional[float] = None
    shrinkage_pct: Optional[float] = None
    quality_score: Optional[float] = None
    headcount: Optional[int] = None
    
    # Secondary Metrics
    abandon_pct: Optional[float] = None
    adherence_pct: Optional[float] = None
    alert_ticket_pct: Optional[float] = None
    
    # Call Volume Metrics
    total_inbound_call_count: int = 0
    total_inbound_call_hours: float = 0.0
    total_inbound_call_minutes: float = 0.0
    total_outbound_call_count: int = 0
    total_outbound_call_hours: float = 0.0
    total_callback_count: int = 0
    total_callback_hours: float = 0.0
    
    # Agent Hours
    total_hours_worked: float = 0.0
    on_queue_hours: float = 0.0
    hours_unavailable: float = 0.0              # Shrinkage numerator
    acw_hours: float = 0.0                      # ISPN calculated (15s per call)
    
    # Answer Thresholds
    pct_answered_30s: Optional[float] = None
    pct_answered_60s: Optional[float] = None
    pct_answered_90s: Optional[float] = None
    pct_answered_120s: Optional[float] = None
    
    # Ticket/Call Variance
    ticket_call_variance: Optional[float] = None
    
    # Calculation metadata
    calculation_timestamp: Optional[str] = None
    formula_version: str = "1.0.0"
    warnings: list = field(default_factory=list)


# =============================================================================
# ISPN CANONICAL CALCULATION ENGINE
# =============================================================================

class ISPNCalculationEngine:
    """
    Implements EXACT formulas from Charlie's LT Scorecard.
    
    CRITICAL: This is the SINGLE SOURCE OF TRUTH for all metric calculations.
    Never use Genesys pre-calculated values - always calculate from raw data.
    """
    
    def __init__(self):
        self.formula_version = "1.0.0"
        self.source_document = "ISPN_iGLASS_LT_Scorecard_Weekly_Monthly_2025.xlsx"
        
    def calculate_all(self, raw: GenesysRawData) -> ISPNCalculatedMetrics:
        """
        Calculate all ISPN metrics from raw Genesys data.
        
        Args:
            raw: GenesysRawData containing extracted values
            
        Returns:
            ISPNCalculatedMetrics with all calculated values
        """
        metrics = ISPNCalculatedMetrics()
        metrics.calculation_timestamp = datetime.now().isoformat()
        metrics.formula_version = self.formula_version
        
        # =====================================================================
        # STEP 1: Convert raw milliseconds to hours/minutes
        # =====================================================================
        
        # Genesys Inbound
        genesys_inbound_minutes = raw.inbound_total_handle_ms * MS_TO_MINUTES
        genesys_inbound_hours = raw.inbound_total_handle_ms * MS_TO_HOURS
        genesys_inbound_awt_seconds = (
            raw.inbound_total_queue_ms / raw.inbound_call_count * MS_TO_SECONDS
            if raw.inbound_call_count > 0 else 0
        )
        
        # Genesys Outbound
        genesys_outbound_hours = raw.outbound_total_handle_ms * MS_TO_HOURS
        
        # Genesys Callback
        genesys_callback_hours = raw.callback_total_handle_ms * MS_TO_HOURS
        
        # Agent Status Hours
        total_logged_in_hours = raw.total_logged_in_ms * MS_TO_HOURS
        total_on_queue_hours = raw.total_on_queue_ms * MS_TO_HOURS
        
        # =====================================================================
        # STEP 2: Calculate derived values
        # =====================================================================
        
        # Total Inbound Call Count (Genesys + Wave)
        # Formula: Row 45 = Row 40 (Wave) + Row 25 (Genesys)
        total_inbound_count = raw.inbound_call_count + raw.wave_call_count
        metrics.total_inbound_call_count = total_inbound_count
        
        # Total Inbound Minutes (Genesys + Wave)
        # Formula: Row 43 = Row 23 (Genesys) + Row 38 (Wave)
        total_inbound_minutes = genesys_inbound_minutes + raw.wave_total_minutes
        metrics.total_inbound_call_minutes = total_inbound_minutes
        
        # Total Inbound Hours
        # Formula: Row 44 = Row 43 / 60
        metrics.total_inbound_call_hours = total_inbound_minutes * MINUTES_TO_HOURS
        
        # Total ACW Hours - ISPN STANDARD: 15 seconds per call
        # Formula: Row 47 = (15/60/60) * Row 45
        metrics.acw_hours = (ISPN_ACW_SECONDS_PER_CALL * SECONDS_TO_HOURS) * total_inbound_count
        
        # Total Call Hours (Inbound + Outbound)
        # Formula: Row 52 = Row 24 (Genesys Hours) + Row 34 (Outbound Hours)
        total_call_hours = genesys_inbound_hours + genesys_outbound_hours
        
        # Outbound metrics
        metrics.total_outbound_call_count = raw.outbound_call_count
        metrics.total_outbound_call_hours = genesys_outbound_hours
        
        # Callback metrics
        metrics.total_callback_count = raw.callback_call_count
        metrics.total_callback_hours = genesys_callback_hours
        
        # =====================================================================
        # STEP 3: Calculate Agent Hours
        # =====================================================================
        
        # Total Hours Worked (L1-L3 Techs)
        # This should come from Agent Status "Logged In" column
        metrics.total_hours_worked = total_logged_in_hours
        
        # Total Hours Worked excluding Training
        # Formula: Row 63 = Row 62 - Row 60
        hours_worked_no_training = total_logged_in_hours - raw.training_hours
        
        # On-Queue Hours
        metrics.on_queue_hours = total_on_queue_hours
        
        # Hours Unavailable for Interaction (Shrinkage numerator)
        # Formula: Row 65 = Row 62 - Row 64
        metrics.hours_unavailable = total_logged_in_hours - total_on_queue_hours
        
        # =====================================================================
        # STEP 4: Calculate KPIs using ISPN CANONICAL FORMULAS
        # =====================================================================
        
        # ---------------------------------------------------------------------
        # 1. FCR % (First Call Resolution)
        # Formula: 1 - (Escalations / Call Tickets)
        # Source: Helpdesk, NOT Genesys
        # ---------------------------------------------------------------------
        if raw.call_tickets > 0:
            metrics.escalation_pct = raw.escalations / raw.call_tickets
            metrics.fcr_pct = 1 - metrics.escalation_pct
        else:
            metrics.warnings.append("FCR: No call tickets - cannot calculate")
        
        # ---------------------------------------------------------------------
        # 2. % of Alert Tickets
        # Formula: Alert Tickets / Call Tickets
        # ---------------------------------------------------------------------
        if raw.call_tickets > 0:
            metrics.alert_ticket_pct = raw.alert_tickets / raw.call_tickets
        
        # ---------------------------------------------------------------------
        # 3. AHT (Average Handle Time) in minutes
        # Formula: Row 58 = Row 95 / Row 45
        #          Total Call Min / Total Inbound Call Count
        # ---------------------------------------------------------------------
        if total_inbound_count > 0:
            metrics.aht_minutes = total_inbound_minutes / total_inbound_count
        else:
            metrics.warnings.append("AHT: No inbound calls - cannot calculate")
        
        # ---------------------------------------------------------------------
        # 4. AWT (Average Wait Time) in seconds - WEIGHTED AVERAGE
        # Formula: Row 72 = (Row 25/Row 45 × Row 26) + (Row 40/Row 45 × Row 41)
        #          (Genesys Calls/Total × Genesys AWT) + (Wave Calls/Total × Wave AWT)
        # ---------------------------------------------------------------------
        if total_inbound_count > 0:
            genesys_weight = raw.inbound_call_count / total_inbound_count
            wave_weight = raw.wave_call_count / total_inbound_count
            
            metrics.awt_seconds = (
                (genesys_weight * genesys_inbound_awt_seconds) +
                (wave_weight * raw.wave_awt_seconds)
            )
        else:
            metrics.warnings.append("AWT: No inbound calls - cannot calculate")
        
        # ---------------------------------------------------------------------
        # 5. % Shrinkage of Total Hours Worked
        # Formula: Row 66 = Row 65 / Row 62
        #          Hours Unavailable / Total Hours Worked
        # 
        # *** THIS IS DIFFERENT FROM GENESYS "SHRINKAGE" ***
        # Genesys breaks down by category. ISPN uses simple formula.
        # ---------------------------------------------------------------------
        if metrics.total_hours_worked > 0:
            metrics.shrinkage_pct = metrics.hours_unavailable / metrics.total_hours_worked
        else:
            metrics.warnings.append("Shrinkage: No hours worked - cannot calculate")
        
        # ---------------------------------------------------------------------
        # 6. L1-L3 Tech Utilization % (FY25+ Formula)
        # Formula: Row 68 = Row 44 / Row 63
        #          Total Inbound Call Hours (incl. ACW) / (Hours Worked - Training)
        # 
        # *** REQUIRES TRAINING HOURS INPUT ***
        # ---------------------------------------------------------------------
        if hours_worked_no_training > 0:
            # Include ACW in numerator
            inbound_hours_with_acw = metrics.total_inbound_call_hours + metrics.acw_hours
            metrics.utilization_pct = inbound_hours_with_acw / hours_worked_no_training
        else:
            metrics.warnings.append("Utilization: No hours (excl training) - cannot calculate")
        
        # ---------------------------------------------------------------------
        # 7. L1-L3 Occupancy %
        # Formula: Row 69 = Row 52 / Row 64
        #          Total Call Hours (Inbound+Outbound) / On-Queue Hours
        # 
        # *** THIS IS DIFFERENT FROM GENESYS "OCCUPANCY" ***
        # Genesys uses Interacting / On-Queue. ISPN uses Call Hours / On-Queue.
        # ---------------------------------------------------------------------
        if metrics.on_queue_hours > 0:
            metrics.occupancy_pct = total_call_hours / metrics.on_queue_hours
        else:
            metrics.warnings.append("Occupancy: No on-queue hours - cannot calculate")
        
        # ---------------------------------------------------------------------
        # 8. Quality Score (Average Tech Review Score)
        # Formula: AVERAGE(Tech Review Scores Range)
        # Target: >88.0
        # ---------------------------------------------------------------------
        if raw.tech_review_scores:
            metrics.quality_score = sum(raw.tech_review_scores) / len(raw.tech_review_scores)
        elif raw.efficacy_scores:
            # Fallback to efficacy if no tech review
            metrics.quality_score = sum(raw.efficacy_scores) / len(raw.efficacy_scores)
        
        # ---------------------------------------------------------------------
        # 9. Abandon Rate
        # Formula: Abandoned Calls / Total Offered
        # Typically count abandons after 60 seconds
        # ---------------------------------------------------------------------
        total_offered = total_inbound_count + raw.abandoned_call_count
        if total_offered > 0:
            metrics.abandon_pct = raw.abandoned_call_count / total_offered
        
        # ---------------------------------------------------------------------
        # 10. Answer Threshold Percentages
        # ---------------------------------------------------------------------
        if raw.inbound_call_count > 0:
            metrics.pct_answered_30s = raw.answered_under_30s / raw.inbound_call_count
            metrics.pct_answered_60s = raw.answered_under_60s / raw.inbound_call_count
            metrics.pct_answered_90s = raw.answered_under_90s / raw.inbound_call_count
            metrics.pct_answered_120s = raw.answered_under_120s / raw.inbound_call_count
        
        # ---------------------------------------------------------------------
        # 11. Ticket vs Calls Variance
        # Formula: Row 49 = Row 6 / (Row 33 + Row 45)
        #          Call Tickets / (Outbound + Inbound Count)
        # ---------------------------------------------------------------------
        total_calls = raw.outbound_call_count + total_inbound_count
        if total_calls > 0 and raw.call_tickets > 0:
            metrics.ticket_call_variance = raw.call_tickets / total_calls
        
        # ---------------------------------------------------------------------
        # 12. Headcount
        # Sum of L1 + L2 + L3 + Salaried
        # ---------------------------------------------------------------------
        metrics.headcount = raw.agent_count
        
        return metrics
    
    def to_dict(self, metrics: ISPNCalculatedMetrics) -> dict:
        """Convert metrics to dictionary for JSON serialization."""
        return {
            'kpis': {
                'fcr_pct': metrics.fcr_pct,
                'escalation_pct': metrics.escalation_pct,
                'aht_minutes': metrics.aht_minutes,
                'awt_seconds': metrics.awt_seconds,
                'utilization_pct': metrics.utilization_pct,
                'occupancy_pct': metrics.occupancy_pct,
                'shrinkage_pct': metrics.shrinkage_pct,
                'quality_score': metrics.quality_score,
                'headcount': metrics.headcount,
                'abandon_pct': metrics.abandon_pct,
            },
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
            'answer_thresholds': {
                'pct_under_30s': metrics.pct_answered_30s,
                'pct_under_60s': metrics.pct_answered_60s,
                'pct_under_90s': metrics.pct_answered_90s,
                'pct_under_120s': metrics.pct_answered_120s,
            },
            'metadata': {
                'calculation_timestamp': metrics.calculation_timestamp,
                'formula_version': metrics.formula_version,
                'warnings': metrics.warnings,
            }
        }
    
    def get_status(self, metric_name: str, value: float) -> str:
        """
        Get RAG status for a metric based on ISPN targets.
        
        Returns: 'green', 'yellow', or 'red'
        """
        if metric_name not in TARGETS or value is None:
            return 'unknown'
        
        target = TARGETS[metric_name]['target']
        direction = TARGETS[metric_name]['direction']
        
        if direction == 'above':
            if value >= target:
                return 'green'
            elif value >= target * 0.9:  # Within 10%
                return 'yellow'
            else:
                return 'red'
        else:  # below
            if value <= target:
                return 'green'
            elif value <= target * 1.1:  # Within 10%
                return 'yellow'
            else:
                return 'red'


# =============================================================================
# GENESYS DATA EXTRACTOR - Raw Data Only
# =============================================================================

def extract_raw_from_interactions(df) -> dict:
    """
    Extract RAW data from Interactions export.
    Returns only counts and millisecond totals - NO percentages.
    
    Critical filters:
    - Inbound only: Direction = "Inbound"
    - Voice only: Media Type = "voice"
    - Valid calls: Total Handle > 20000ms (20 seconds)
    - Exclude internal: Queue Name not containing ISPN/Test/Tyler/eTech
    """
    import pandas as pd
    
    raw = {}
    
    # Apply standard filters
    mask = (
        (df['Direction'] == 'Inbound') &
        (df['Media Type'] == 'voice') &
        (df['Total Handle'] > 20000) &  # >20 seconds
        (~df['Queue Name'].str.contains('ISPN|Test|Tyler|eTech', case=False, na=False))
    )
    
    inbound = df[mask]
    
    # Inbound metrics
    raw['inbound_call_count'] = len(inbound)
    raw['inbound_total_handle_ms'] = inbound['Total Handle'].sum()
    raw['inbound_total_talk_ms'] = inbound['Total Talk'].sum()
    raw['inbound_total_hold_ms'] = inbound['Total Hold'].sum()
    raw['inbound_total_acw_ms'] = inbound['Total ACW'].sum()
    raw['inbound_total_queue_ms'] = inbound['Total Queue'].sum()
    
    # Answer thresholds (queue time in ms)
    raw['answered_under_30s'] = len(inbound[inbound['Total Queue'] < 30000])
    raw['answered_under_60s'] = len(inbound[inbound['Total Queue'] < 60000])
    raw['answered_under_90s'] = len(inbound[inbound['Total Queue'] < 90000])
    raw['answered_under_120s'] = len(inbound[inbound['Total Queue'] < 120000])
    
    # Abandons
    abandons = df[
        (df['Abandoned'] == 'YES') &
        (df['Media Type'] == 'voice') &
        (~df['Queue Name'].str.contains('ISPN|Test|Tyler|eTech', case=False, na=False))
    ]
    raw['abandoned_call_count'] = len(abandons)
    raw['abandoned_after_60s_count'] = len(abandons[abandons['Total Queue'] > 60000])
    
    # Outbound
    outbound = df[
        (df['Direction'] == 'Outbound') &
        (df['Media Type'] == 'voice')
    ]
    raw['outbound_call_count'] = len(outbound)
    raw['outbound_total_handle_ms'] = outbound['Total Handle'].sum()
    
    # Callbacks
    callbacks = df[df['Media Type'] == 'callback']
    raw['callback_call_count'] = len(callbacks)
    raw['callback_total_handle_ms'] = callbacks['Total Handle'].sum()
    
    return raw


def extract_raw_from_agent_status(df) -> dict:
    """
    Extract RAW data from Agent Status Duration Details export.
    Returns only millisecond totals - NO percentages.
    
    Critical: Filter by Department = "Tech Center" for L1-L3 only
    """
    raw = {}
    
    # Filter for Tech Center only
    if 'Department' in df.columns:
        df = df[df['Department'].str.contains('Tech Center', case=False, na=False)]
    
    # Sum all agent times (these are already totals per agent)
    raw['total_logged_in_ms'] = df['Logged In'].sum()
    raw['total_on_queue_ms'] = df['On Queue'].sum()
    raw['total_interacting_ms'] = df['Interacting'].sum()
    raw['total_idle_ms'] = df['Idle'].sum()
    raw['total_available_ms'] = df['Available'].sum()
    raw['total_away_ms'] = df['Away'].sum()
    raw['total_break_ms'] = df['Break'].sum()
    raw['total_meal_ms'] = df['Meal'].sum()
    raw['total_not_responding_ms'] = df['Not Responding'].sum()
    
    raw['agent_count'] = len(df)
    
    return raw


# =============================================================================
# COMPARISON UTILITY - Show ISPN vs Genesys differences
# =============================================================================

def compare_calculations(ispn_metrics: ISPNCalculatedMetrics, genesys_values: dict) -> dict:
    """
    Compare ISPN canonical calculations against Genesys pre-calculated values.
    Useful for auditing and understanding metric drift.
    """
    comparisons = {}
    
    if 'shrinkage_pct' in genesys_values and ispn_metrics.shrinkage_pct:
        comparisons['shrinkage'] = {
            'ispn_value': ispn_metrics.shrinkage_pct,
            'genesys_value': genesys_values['shrinkage_pct'],
            'difference': ispn_metrics.shrinkage_pct - genesys_values['shrinkage_pct'],
            'note': 'ISPN uses (Hours Worked - On-Queue) / Hours Worked'
        }
    
    if 'occupancy_pct' in genesys_values and ispn_metrics.occupancy_pct:
        comparisons['occupancy'] = {
            'ispn_value': ispn_metrics.occupancy_pct,
            'genesys_value': genesys_values['occupancy_pct'],
            'difference': ispn_metrics.occupancy_pct - genesys_values['occupancy_pct'],
            'note': 'ISPN uses Call Hours / On-Queue Hours (Genesys uses Interacting / On-Queue)'
        }
    
    if 'aht_minutes' in genesys_values and ispn_metrics.aht_minutes:
        comparisons['aht'] = {
            'ispn_value': ispn_metrics.aht_minutes,
            'genesys_value': genesys_values['aht_minutes'],
            'difference': ispn_metrics.aht_minutes - genesys_values['aht_minutes'],
            'note': 'ISPN includes Wave calls in weighted average'
        }
    
    return comparisons


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Example: Calculate from sample data
    raw = GenesysRawData(
        # Interactions data
        inbound_call_count=50403,
        inbound_total_handle_ms=538180 * 60000,  # Convert minutes to ms
        inbound_total_queue_ms=39 * 50403 * 1000,  # AWT 39s × calls
        outbound_call_count=5913,
        outbound_total_handle_ms=int(512.77 * 3600000),  # 512.77 hours
        callback_call_count=1388,
        callback_total_handle_ms=int(304.13 * 3600000),  # 304.13 hours
        
        # Agent Status data
        total_logged_in_ms=int(19869.67 * 3600000),  # 19,869.67 hours
        total_on_queue_ms=int(14113.82 * 3600000),   # 14,113.82 hours
        
        # Training (manual input)
        training_hours=0,  # Would need manual input
        
        # Helpdesk data
        call_tickets=57743,
        escalations=17770,
        alert_tickets=2939,
        
        # Quality scores
        tech_review_scores=[94.3],
        
        agent_count=123,
    )
    
    engine = ISPNCalculationEngine()
    metrics = engine.calculate_all(raw)
    
    print("\n" + "="*60)
    print("ISPN CANONICAL METRICS (Calculated from Raw Data)")
    print("="*60)
    print(f"FCR %:           {metrics.fcr_pct:.1%}" if metrics.fcr_pct else "FCR %: N/A")
    print(f"Escalation %:    {metrics.escalation_pct:.1%}" if metrics.escalation_pct else "")
    print(f"AHT:             {metrics.aht_minutes:.2f} min" if metrics.aht_minutes else "")
    print(f"AWT:             {metrics.awt_seconds:.1f} sec" if metrics.awt_seconds else "")
    print(f"Shrinkage %:     {metrics.shrinkage_pct:.1%}" if metrics.shrinkage_pct else "")
    print(f"Utilization %:   {metrics.utilization_pct:.1%}" if metrics.utilization_pct else "")
    print(f"Occupancy %:     {metrics.occupancy_pct:.1%}" if metrics.occupancy_pct else "")
    print(f"Quality Score:   {metrics.quality_score:.1f}" if metrics.quality_score else "")
    print(f"Headcount:       {metrics.headcount}")
    
    if metrics.warnings:
        print("\nWarnings:")
        for w in metrics.warnings:
            print(f"  ⚠️  {w}")

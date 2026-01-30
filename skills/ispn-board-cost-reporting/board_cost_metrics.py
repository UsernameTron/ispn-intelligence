#!/usr/bin/env python3
"""
ISPN Board Cost Reporting Module

PURPOSE: Four cost metrics for board reporting. Nothing else.

METRICS:
1. Cost per Call (weekly)
2. Cost per Minute (weekly)
3. Labor Spend vs Budget
4. Savings Impact Estimate

LOCKED DEFINITIONS - DO NOT MODIFY WITHOUT PETE APPROVAL:
- Cost per Call = Weekly Fully-Loaded Labor Cost ÷ Weekly Handled Calls
- Cost per Minute = Weekly Fully-Loaded Labor Cost ÷ Weekly Handled Minutes
- Handled Minutes = Talk + Hold + ACW (NOT AHT × Calls)
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

# Integration with ISPN Calculation Engine
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

try:
    from utils.ispn_calculations import ISPNCalculationEngine, ISPNCalculatedMetrics
except ImportError:
    ISPNCalculationEngine = None
    ISPNCalculatedMetrics = None


# =============================================================================
# LOCKED CONSTANTS - DO NOT MODIFY
# =============================================================================

# Blended hourly rate (weighted average across L1/L2/L3)
BLENDED_HOURLY_RATE = 21.95

# Targets for savings calculation
UTILIZATION_TARGET = 0.60  # 60% (midpoint of 55-65% band)
AHT_TARGET_MINUTES = 10.7  # 10.7 minutes

# Variance thresholds
VARIANCE_GREEN_PCT = 5.0   # ±5% is acceptable
VARIANCE_YELLOW_PCT = 10.0 # ±10% needs monitoring

# Weeks per year for annualization
WEEKS_PER_YEAR = 52


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class FinanceInput:
    """Weekly finance data input."""
    week_ending: str
    weekly_labor_cost: float
    weekly_budget: float
    notes: Optional[str] = None


@dataclass
class OperationalInput:
    """Weekly operational data from Genesys/ISPN."""
    week_ending: str
    handled_calls: int
    handled_minutes: float  # Talk + Hold + ACW in minutes
    hours_worked: float
    utilization_pct: float
    aht_minutes: float


@dataclass
class CostMetrics:
    """The four board cost metrics."""
    week_ending: str
    
    # Metric 1: Cost per Call
    cost_per_call: Optional[float] = None
    
    # Metric 2: Cost per Minute
    cost_per_minute: Optional[float] = None
    
    # Metric 3: Labor vs Budget
    labor_actual: Optional[float] = None
    labor_budget: Optional[float] = None
    labor_variance: Optional[float] = None
    labor_variance_pct: Optional[float] = None
    labor_status: str = "UNKNOWN"
    
    # Metric 4: Savings Opportunity (annualized)
    util_gap_pct: Optional[float] = None
    util_impact_annual: Optional[float] = None
    aht_gap_minutes: Optional[float] = None
    aht_impact_annual: Optional[float] = None
    total_opportunity_annual: Optional[float] = None
    
    # Metadata
    calculation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    notes: List[str] = field(default_factory=list)


# =============================================================================
# BOARD COST METRICS ENGINE
# =============================================================================

class BoardCostMetrics:
    """
    Board-level cost calculations. Four metrics only.
    
    This class is intentionally constrained. It calculates:
    1. Cost per Call
    2. Cost per Minute
    3. Labor Spend vs Budget
    4. Savings Impact Estimate
    
    It refuses to calculate or provide any other metrics.
    """
    
    def __init__(self):
        self.formula_version = "1.0.0"
        self._locked_definitions = {
            "cost_per_call": "Weekly Fully-Loaded Labor Cost ÷ Weekly Handled Calls",
            "cost_per_minute": "Weekly Fully-Loaded Labor Cost ÷ Weekly Handled Minutes",
            "handled_minutes": "Talk Time + Hold Time + ACW Time (NOT AHT × Calls)",
            "labor_variance": "(Actual - Budget) ÷ Budget × 100",
            "savings_opportunity": "Utilization Gap + AHT Gap, annualized"
        }
    
    def get_locked_definitions(self) -> dict:
        """Return locked formula definitions. These cannot be modified at runtime."""
        return self._locked_definitions.copy()
    
    # =========================================================================
    # METRIC 1: COST PER CALL
    # =========================================================================
    
    def calculate_cost_per_call(self, weekly_labor_cost: float, handled_calls: int) -> Optional[float]:
        """
        Cost per Call = Weekly Fully-Loaded Labor Cost ÷ Weekly Handled Calls
        
        LOCKED DEFINITION - DO NOT MODIFY
        """
        if handled_calls <= 0:
            return None
        return weekly_labor_cost / handled_calls
    
    # =========================================================================
    # METRIC 2: COST PER MINUTE
    # =========================================================================
    
    def calculate_cost_per_minute(self, weekly_labor_cost: float, handled_minutes: float) -> Optional[float]:
        """
        Cost per Minute = Weekly Fully-Loaded Labor Cost ÷ Weekly Handled Minutes
        
        CRITICAL: handled_minutes MUST be Talk + Hold + ACW
        Never use AHT × Calls as a substitute.
        
        LOCKED DEFINITION - DO NOT MODIFY
        """
        if handled_minutes <= 0:
            return None
        return weekly_labor_cost / handled_minutes
    
    # =========================================================================
    # METRIC 3: LABOR SPEND VS BUDGET
    # =========================================================================
    
    def calculate_labor_variance(self, actual: float, budget: float) -> dict:
        """
        Labor Spend vs Budget
        
        Returns:
            dict with actual, budget, variance, variance_pct, status
        
        LOCKED DEFINITION - DO NOT MODIFY
        """
        if budget <= 0:
            return {
                "actual": actual,
                "budget": budget,
                "variance": None,
                "variance_pct": None,
                "status": "NO BUDGET"
            }
        
        variance = actual - budget
        variance_pct = (variance / budget) * 100
        
        # Determine status
        if abs(variance_pct) <= VARIANCE_GREEN_PCT:
            status = "ON TRACK"
        elif variance_pct > VARIANCE_GREEN_PCT:
            status = "OVER BUDGET"
        else:
            status = "UNDER BUDGET"
        
        return {
            "actual": actual,
            "budget": budget,
            "variance": variance,
            "variance_pct": variance_pct,
            "status": status
        }
    
    # =========================================================================
    # METRIC 4: SAVINGS IMPACT ESTIMATE
    # =========================================================================
    
    def calculate_savings_opportunity(
        self,
        actual_util: float,
        actual_aht: float,
        hours_worked: float,
        call_volume: int
    ) -> dict:
        """
        Savings Impact Estimate (Annualized)
        
        Calculates the financial opportunity from closing:
        1. Utilization gap (actual vs 60% target)
        2. AHT gap (actual vs 10.7 min target)
        
        LOCKED DEFINITION - DO NOT MODIFY
        """
        # Utilization gap (if below target)
        util_gap = max(0, UTILIZATION_TARGET - actual_util)
        util_impact = util_gap * hours_worked * BLENDED_HOURLY_RATE * WEEKS_PER_YEAR
        
        # AHT gap (if above target)
        aht_gap = max(0, actual_aht - AHT_TARGET_MINUTES)
        # Convert minutes to fraction of hour for cost
        aht_impact = aht_gap * call_volume * (BLENDED_HOURLY_RATE / 60) * WEEKS_PER_YEAR
        
        return {
            "utilization_gap_pct": util_gap,
            "utilization_impact_annual": util_impact,
            "aht_gap_minutes": aht_gap,
            "aht_impact_annual": aht_impact,
            "total_opportunity_annual": util_impact + aht_impact
        }
    
    # =========================================================================
    # COMBINED CALCULATION
    # =========================================================================
    
    def calculate_all(self, finance: FinanceInput, ops: OperationalInput) -> CostMetrics:
        """
        Calculate all four board cost metrics.
        
        Args:
            finance: Weekly finance data (labor cost, budget)
            ops: Weekly operational data (calls, minutes, utilization, AHT)
        
        Returns:
            CostMetrics dataclass with all four metrics
        """
        metrics = CostMetrics(week_ending=finance.week_ending)
        notes = []
        
        # Metric 1: Cost per Call
        metrics.cost_per_call = self.calculate_cost_per_call(
            finance.weekly_labor_cost,
            ops.handled_calls
        )
        if metrics.cost_per_call is None:
            notes.append("Cost per Call: No handled calls")
        
        # Metric 2: Cost per Minute
        metrics.cost_per_minute = self.calculate_cost_per_minute(
            finance.weekly_labor_cost,
            ops.handled_minutes
        )
        if metrics.cost_per_minute is None:
            notes.append("Cost per Minute: No handled minutes")
        
        # Metric 3: Labor vs Budget
        variance = self.calculate_labor_variance(
            finance.weekly_labor_cost,
            finance.weekly_budget
        )
        metrics.labor_actual = variance["actual"]
        metrics.labor_budget = variance["budget"]
        metrics.labor_variance = variance["variance"]
        metrics.labor_variance_pct = variance["variance_pct"]
        metrics.labor_status = variance["status"]
        
        # Metric 4: Savings Opportunity
        savings = self.calculate_savings_opportunity(
            ops.utilization_pct,
            ops.aht_minutes,
            ops.hours_worked,
            ops.handled_calls
        )
        metrics.util_gap_pct = savings["utilization_gap_pct"]
        metrics.util_impact_annual = savings["utilization_impact_annual"]
        metrics.aht_gap_minutes = savings["aht_gap_minutes"]
        metrics.aht_impact_annual = savings["aht_impact_annual"]
        metrics.total_opportunity_annual = savings["total_opportunity_annual"]
        
        # Add finance notes if provided
        if finance.notes:
            notes.append(f"Finance: {finance.notes}")
        
        metrics.notes = notes
        
        return metrics
    
    # =========================================================================
    # OUTPUT FORMATTING
    # =========================================================================
    
    def format_board_summary(self, metrics: CostMetrics) -> str:
        """Format metrics for board presentation."""
        
        # Format currency
        def fmt_currency(val, decimals=2):
            if val is None:
                return "N/A"
            if val >= 1_000_000:
                return f"${val/1_000_000:,.1f}M"
            elif val >= 1_000:
                return f"${val:,.0f}"
            else:
                return f"${val:,.{decimals}f}"
        
        def fmt_pct(val):
            if val is None:
                return "N/A"
            return f"{val:+.1f}%"
        
        output = f"""
ISPN TECH CENTER - COST METRICS
Week of {metrics.week_ending}
═══════════════════════════════════════════════════

COST PER CALL         {fmt_currency(metrics.cost_per_call)}
COST PER MINUTE       {fmt_currency(metrics.cost_per_minute)}

LABOR VS BUDGET
  Actual:             {fmt_currency(metrics.labor_actual)}
  Budget:             {fmt_currency(metrics.labor_budget)}
  Variance:           {fmt_currency(metrics.labor_variance)} ({fmt_pct(metrics.labor_variance_pct)})
  Status:             {metrics.labor_status}

SAVINGS OPPORTUNITY (ANNUALIZED)
  Utilization Gap:    {fmt_currency(metrics.util_impact_annual)} ({metrics.util_gap_pct:.1%} below target)
  AHT Gap:            {fmt_currency(metrics.aht_impact_annual)} ({metrics.aht_gap_minutes:.1f} min above target)
  Total Opportunity:  {fmt_currency(metrics.total_opportunity_annual)}

═══════════════════════════════════════════════════
Data: Genesys Interactions + Finance Actuals
Method: ISPN Canonical Calculations
"""
        
        if metrics.notes:
            output += "\nNotes:\n"
            for note in metrics.notes:
                output += f"  • {note}\n"
        
        return output.strip()
    
    def to_dict(self, metrics: CostMetrics) -> dict:
        """Convert metrics to dictionary for JSON export."""
        return {
            "week_ending": metrics.week_ending,
            "cost_per_call": metrics.cost_per_call,
            "cost_per_minute": metrics.cost_per_minute,
            "labor": {
                "actual": metrics.labor_actual,
                "budget": metrics.labor_budget,
                "variance": metrics.labor_variance,
                "variance_pct": metrics.labor_variance_pct,
                "status": metrics.labor_status
            },
            "savings_opportunity": {
                "utilization_gap_pct": metrics.util_gap_pct,
                "utilization_impact_annual": metrics.util_impact_annual,
                "aht_gap_minutes": metrics.aht_gap_minutes,
                "aht_impact_annual": metrics.aht_impact_annual,
                "total_opportunity_annual": metrics.total_opportunity_annual
            },
            "metadata": {
                "calculation_timestamp": metrics.calculation_timestamp,
                "formula_version": self.formula_version,
                "notes": metrics.notes
            }
        }


# =============================================================================
# SCOPE ENFORCEMENT
# =============================================================================

class BoardCostReporter:
    """
    High-level interface that enforces scope boundaries.
    
    This class REFUSES to answer questions outside the four metrics.
    """
    
    ALLOWED_QUESTIONS = [
        "cost per call",
        "cost per minute", 
        "labor spend",
        "labor vs budget",
        "budget variance",
        "savings opportunity",
        "savings estimate",
        "savings impact",
        "cost metrics",
        "board cost"
    ]
    
    REDIRECT_MAP = {
        "aht": "ispn-dpr-analysis",
        "awt": "ispn-dpr-analysis",
        "fcr": "ispn-dpr-analysis",
        "escalation": "ispn-dpr-analysis",
        "utilization trend": "ispn-scorecard-analysis",
        "coaching": "ispn-agent-coaching",
        "pip": "ispn-agent-coaching",
        "training": "ispn-training-gap",
        "hire": "ispn-capacity-planning",
        "capacity": "ispn-capacity-planning",
        "fte": "ispn-capacity-planning",
        "partner": "ispn-partner-sla",
        "sla": "ispn-partner-sla",
        "attrition": "ispn-attrition-risk",
        "retention": "ispn-attrition-risk",
    }
    
    def __init__(self):
        self.calculator = BoardCostMetrics()
    
    def is_in_scope(self, query: str) -> bool:
        """Check if query is within this skill's scope."""
        query_lower = query.lower()
        return any(allowed in query_lower for allowed in self.ALLOWED_QUESTIONS)
    
    def get_redirect(self, query: str) -> Optional[str]:
        """Get redirect skill for out-of-scope query."""
        query_lower = query.lower()
        for keyword, skill in self.REDIRECT_MAP.items():
            if keyword in query_lower:
                return skill
        return None
    
    def refuse_out_of_scope(self, query: str) -> str:
        """Generate refusal message for out-of-scope query."""
        redirect = self.get_redirect(query)
        
        base_msg = ("That's outside this skill's scope. I only report: "
                   "cost per call, cost per minute, labor vs budget, and savings impact.")
        
        if redirect:
            return f"{base_msg} For that topic, use {redirect}."
        else:
            return base_msg
    
    def report(self, finance: FinanceInput, ops: OperationalInput) -> str:
        """Generate the board cost report."""
        metrics = self.calculator.calculate_all(finance, ops)
        return self.calculator.format_board_summary(metrics)


# =============================================================================
# CLI / TESTING
# =============================================================================

if __name__ == "__main__":
    # Example usage
    calculator = BoardCostMetrics()
    
    # Sample data
    finance = FinanceInput(
        week_ending="2025-01-31",
        weekly_labor_cost=127692.31,
        weekly_budget=125000.00,
        notes="Includes OT for weather event"
    )
    
    ops = OperationalInput(
        week_ending="2025-01-31",
        handled_calls=14500,
        handled_minutes=155150.0,  # Talk + Hold + ACW
        hours_worked=6240.0,
        utilization_pct=0.462,  # 46.2%
        aht_minutes=10.68
    )
    
    # Calculate
    metrics = calculator.calculate_all(finance, ops)
    
    # Output
    print(calculator.format_board_summary(metrics))
    print("\n" + "="*50)
    print("JSON Export:")
    print(json.dumps(calculator.to_dict(metrics), indent=2))

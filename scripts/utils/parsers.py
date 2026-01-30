"""
ISPN File Parsers
Parse Genesys exports into structured JSON

Updated with genesys-cloud-cx-reporting field specifications:
- Validated field names from Genesys Cloud exports
- Callback identification: Media Type = "callback"
- ACW timeout: 15 seconds (ININ-WRAP-UP-TIMEOUT)
- Non-ACD filtering: Non-ACD = "YES" exclusion
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import re


# =============================================================================
# GENESYS FIELD MAPPINGS (from genesys-cloud-cx-reporting skill)
# =============================================================================

GENESYS_INTERACTIONS_FIELDS = {
    # Core identifiers
    'interaction_id': 'Interaction ID',
    'conversation_id': 'Conversation ID',
    'session_id': 'Session ID',
    
    # Time fields (in milliseconds)
    'total_handle': 'Total Handle',       # Talk + Hold + ACW
    'total_talk': 'Total Talk',
    'total_hold': 'Total Hold',
    'total_acw': 'Total ACW',
    'total_queue': 'Total Queue',         # AWT
    'total_alert': 'Total Alert',
    
    # Direction and type
    'direction': 'Direction',             # Inbound, Outbound
    'media_type': 'Media Type',           # Voice, callback
    'non_acd': 'Non-ACD',                 # YES/NO - filter out YES
    'answered': 'Answered',               # YES/NO
    
    # Queue and agent
    'queue_name': 'Queue Name',
    'user_name': 'User Name',
    
    # Dates
    'conversation_start': 'Conversation Start',
    'conversation_end': 'Conversation End',
}

GENESYS_AGENT_STATUS_FIELDS = {
    # Status duration fields
    'user_name': 'User Name',
    'logged_in': 'Logged In',
    'available': 'Available',
    'on_queue': 'On Queue',
    'idle': 'Idle',
    'busy': 'Busy',
    'not_responding': 'Not Responding',
    'away': 'Away',
    'break': 'Break',
    'meal': 'Meal',
    'training': 'Training',
    'meeting': 'Meeting',
    'off_queue': 'Off Queue',
}

GENESYS_QA_EVALUATION_FIELDS = {
    'evaluation_id': 'EvaluationId',
    'form_name': 'EvaluationFormName',
    'agent_name': 'AgentName',
    'agent_id': 'AgentId',
    'evaluator_name': 'EvaluatorName',
    'evaluator_id': 'EvaluatorId',
    'question_group': 'QuestionGroupName',
    'question_text': 'QuestionText',
    'question_help': 'QuestionHelpText',
    'answer_yes_no': 'AnswerYesNo',
    'score': 'Score',
    'max_points': 'MaxPoints',
    'conversation_date': 'ConversationDate',
    'submitted_date': 'SubmittedDate',
}

# =============================================================================
# ISPN CALCULATION STANDARDS
# =============================================================================

ISPN_STANDARDS = {
    'abandon_threshold_ms': 60000,     # Only count abandons >= 60 seconds
    'aht_min_threshold_ms': 20000,     # Exclude < 20 second handles
    'acw_timeout_ms': 15000,           # Standard ACW timeout
}


# =============================================================================
# PARSER FUNCTIONS
# =============================================================================

def parse_scorecard(filepath: Path) -> dict:
    """
    Parse LT Scorecard Excel file.
    Sheet: ISPN_Scorecard-Monthly_INPUT
    Key rows: 52-65 for 9 core KPIs
    """
    df = pd.read_excel(filepath, sheet_name='ISPN_Scorecard-Monthly_INPUT', header=None)
    
    result = {
        'source': 'scorecard',
        'filepath': str(filepath),
        'parsed_at': datetime.now().isoformat(),
        'kpis': {}
    }
    
    # Row mappings (0-indexed)
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
    
    # Find latest month column with data (scan from right)
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
    
    sheets = xl.sheet_names
    if not sheets:
        return result
    
    for sheet in sheets:
        if re.match(r'[A-Z]{3}\d{2}', sheet):
            df = pd.read_excel(filepath, sheet_name=sheet)
            
            cols = df.columns.tolist()
            date_col = next((c for c in cols if 'date' in str(c).lower()), None)
            calls_col = next((c for c in cols if 'call' in str(c).lower() and 'total' in str(c).lower()), None)
            aht_col = next((c for c in cols if 'aht' in str(c).lower() or 'handle' in str(c).lower()), None)
            fcr_col = next((c for c in cols if 'fcr' in str(c).lower()), None)
            
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
    
    if 'CD data 2' in xl.sheet_names:
        df = pd.read_excel(filepath, sheet_name='CD data 2')
        result['hourly_row_count'] = len(df)
        result['hourly_valid'] = len(df) == 168  # 24 hours × 7 days
    
    for sheet in xl.sheet_names:
        if sheet not in ['CD data 2', 'Summary', 'Instructions']:
            try:
                df = pd.read_excel(filepath, sheet_name=sheet)
                result['partners'][sheet] = {'row_count': len(df)}
            except:
                pass
    
    return result


def parse_genesys_interactions(filepath: Path) -> dict:
    """
    Parse Genesys Cloud Interactions export CSV.
    
    Required export: Performance → Workspace → Interactions
    
    Field mappings from genesys-cloud-cx-reporting:
    - Total Handle (ms) = Talk + Hold + ACW
    - Total Queue (ms) = Wait time
    - Media Type = "callback" identifies callbacks
    - Non-ACD = "YES" should be filtered out for queue metrics
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
    }
    
    # Validate expected columns exist
    expected = ['Total Handle', 'Total Talk', 'Total Hold', 'Total ACW', 
                'Total Queue', 'Direction', 'Media Type', 'Answered']
    for col in expected:
        result['field_validation'][col] = col in df.columns
    
    # Filter: Inbound only, exclude Non-ACD
    df_filtered = df.copy()
    if 'Direction' in df.columns:
        df_filtered = df_filtered[df_filtered['Direction'] == 'Inbound']
    if 'Non-ACD' in df.columns:
        df_filtered = df_filtered[df_filtered['Non-ACD'] != 'YES']
    
    result['inbound_count'] = len(df_filtered)
    
    # Apply ISPN standards: exclude < 20 second handles
    if 'Total Handle' in df.columns:
        df_valid = df_filtered[df_filtered['Total Handle'] >= ISPN_STANDARDS['aht_min_threshold_ms']]
        result['valid_handle_count'] = len(df_valid)
        
        if len(df_valid) > 0:
            # Convert milliseconds to appropriate units
            result['metrics']['avg_handle_time_min'] = df_valid['Total Handle'].mean() / 60000
            
            if 'Total Talk' in df.columns:
                result['metrics']['avg_talk_time_min'] = df_valid['Total Talk'].mean() / 60000
            if 'Total Hold' in df.columns:
                result['metrics']['avg_hold_time_min'] = df_valid['Total Hold'].mean() / 60000
            if 'Total ACW' in df.columns:
                result['metrics']['avg_acw_time_sec'] = df_valid['Total ACW'].mean() / 1000
    
    # AWT calculation
    if 'Total Queue' in df.columns and 'Answered' in df.columns:
        answered = df_filtered[df_filtered['Answered'] == 'YES']
        if len(answered) > 0:
            result['metrics']['avg_wait_time_sec'] = answered['Total Queue'].mean() / 1000
    
    # Callback identification (Media Type = "callback")
    if 'Media Type' in df.columns:
        callbacks = df[df['Media Type'].str.lower() == 'callback']
        result['callbacks']['count'] = len(callbacks)
        result['callbacks']['pct_of_total'] = (len(callbacks) / len(df) * 100) if len(df) > 0 else 0
    
    # Abandon analysis (queue time >= 60 seconds)
    if 'Answered' in df.columns and 'Total Queue' in df.columns:
        abandoned = df_filtered[df_filtered['Answered'] == 'NO']
        valid_abandons = abandoned[abandoned['Total Queue'] >= ISPN_STANDARDS['abandon_threshold_ms']]
        result['metrics']['abandon_count'] = len(valid_abandons)
        result['metrics']['abandon_rate'] = (len(valid_abandons) / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
    
    return result


def parse_genesys_agent_status(filepath: Path) -> dict:
    """
    Parse Genesys Cloud Agent Status Duration Details export.
    
    Required export: Performance → Contact Center → Agent Status Duration Details
    
    Provides: Hours worked, shrinkage breakdown, on-queue hours
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
    }
    
    # Expected columns for shrinkage calculation
    shrinkage_cols = ['Break', 'Meal', 'Training', 'Meeting', 'Away']
    productive_cols = ['On Queue', 'Available']
    
    # Aggregate by agent
    if 'User Name' in df.columns:
        for col in df.columns:
            if col not in ['User Name']:
                try:
                    result['totals'][col] = df[col].sum()
                except:
                    pass
        
        # Calculate shrinkage
        total_logged = result['totals'].get('Logged In', 0)
        if total_logged > 0:
            shrinkage_time = sum(result['totals'].get(col, 0) for col in shrinkage_cols if col in result['totals'])
            result['totals']['shrinkage_pct'] = (shrinkage_time / total_logged) * 100
            
            on_queue_time = result['totals'].get('On Queue', 0)
            result['totals']['on_queue_pct'] = (on_queue_time / total_logged) * 100
    
    return result


def parse_genesys_qa_evaluations(filepath: Path) -> dict:
    """
    Parse Genesys Cloud QA evaluation_questions export.
    
    Structure: 36-column CSV from Genesys evaluation exports
    Form types: Full Call Review (104pts/21Q), Auto-Evaluation (40pts/9Q), Focus Review (100pts/1Q)
    
    From genesys-qa-analytics skill:
    - Agent tiering: Exemplary ≥95%, Standard 80-94%, Development 65-79%, Critical <65%
    - Calibration flags: σ > 15 = concern, ±10% from mean = recalibration
    """
    df = pd.read_csv(filepath)
    
    result = {
        'source': 'genesys_qa_evaluations',
        'filepath': str(filepath),
        'parsed_at': datetime.now().isoformat(),
        'record_count': len(df),
        'columns': df.columns.tolist(),
        'field_validation': {},
        'evaluations': {},
        'agents': {},
        'question_failures': {},
    }
    
    # Validate expected columns
    expected = ['EvaluationId', 'EvaluationFormName', 'AgentName', 'Score', 'MaxPoints']
    for col in expected:
        result['field_validation'][col] = col in df.columns
    
    if not all(result['field_validation'].values()):
        return result
    
    # Count by form type
    if 'EvaluationFormName' in df.columns:
        result['form_counts'] = df['EvaluationFormName'].value_counts().to_dict()
    
    # Calculate agent scores
    if 'EvaluationId' in df.columns:
        # Group by evaluation first, sum scores
        eval_scores = df.groupby(['EvaluationId', 'AgentName']).agg({
            'Score': 'sum',
            'MaxPoints': 'sum'
        }).reset_index()
        
        eval_scores['normalized_pct'] = (eval_scores['Score'] / eval_scores['MaxPoints']) * 100
        
        # Aggregate by agent
        agent_summary = eval_scores.groupby('AgentName').agg({
            'normalized_pct': ['mean', 'std', 'count']
        })
        agent_summary.columns = ['avg_score', 'std_score', 'eval_count']
        
        # Assign tiers
        def assign_tier(score):
            if score >= 95:
                return 'Exemplary'
            elif score >= 80:
                return 'Standard'
            elif score >= 65:
                return 'Development'
            else:
                return 'Critical'
        
        agent_summary['tier'] = agent_summary['avg_score'].apply(assign_tier)
        result['agents'] = agent_summary.to_dict('index')
        
        # Count by tier
        result['tier_counts'] = agent_summary['tier'].value_counts().to_dict()
    
    # Question failure analysis
    if 'QuestionText' in df.columns and 'Score' in df.columns and 'MaxPoints' in df.columns:
        failures = df[df['Score'] == 0].groupby('QuestionText').size()
        totals = df.groupby('QuestionText').size()
        
        for q in failures.index:
            if totals[q] > 0:
                result['question_failures'][q] = {
                    'failure_count': int(failures[q]),
                    'total_count': int(totals[q]),
                    'failure_rate': round(failures[q] / totals[q] * 100, 1)
                }
        
        # Sort by failure rate
        result['question_failures'] = dict(
            sorted(result['question_failures'].items(), 
                   key=lambda x: x[1]['failure_rate'], 
                   reverse=True)
        )
    
    return result


def parse_wfm_adherence(filepath: Path) -> dict:
    """
    Parse Genesys WFM Historical Adherence export.
    
    Required export: WFM → Historical Adherence
    
    Provides: Schedule adherence %, conformance %
    """
    df = pd.read_csv(filepath)
    
    result = {
        'source': 'wfm_adherence',
        'filepath': str(filepath),
        'parsed_at': datetime.now().isoformat(),
        'record_count': len(df),
        'columns': df.columns.tolist(),
        'metrics': {},
    }
    
    # Look for adherence columns
    adherence_cols = [c for c in df.columns if 'adherence' in c.lower()]
    conformance_cols = [c for c in df.columns if 'conformance' in c.lower()]
    
    if adherence_cols:
        for col in adherence_cols:
            try:
                result['metrics'][f'avg_{col}'] = df[col].mean()
            except:
                pass
    
    if conformance_cols:
        for col in conformance_cols:
            try:
                result['metrics'][f'avg_{col}'] = df[col].mean()
            except:
                pass
    
    return result


# =============================================================================
# FILE TYPE IDENTIFICATION
# =============================================================================

def identify_file_type(filepath: Path) -> str:
    """
    Identify file type based on filename pattern and content.
    
    Returns: 'scorecard', 'dpr', 'wcs', 'genesys_interactions', 
             'genesys_agent_status', 'genesys_qa', 'wfm_adherence', or 'unknown'
    """
    name = filepath.name.lower()
    
    # Check by filename pattern first
    if 'scorecard' in name:
        return 'scorecard'
    elif name.startswith('dpr'):
        return 'dpr'
    elif name.startswith('wcs') or re.match(r'\d{6}-\d{6}', name):
        return 'wcs'
    elif 'evaluation' in name or 'qa' in name.lower():
        return 'genesys_qa'
    elif 'agent_status' in name or 'agentstatus' in name:
        return 'genesys_agent_status'
    elif 'adherence' in name or 'wfm' in name:
        return 'wfm_adherence'
    elif name.startswith('interactions'):
        return 'genesys_interactions'
    
    # If CSV, check content for Genesys patterns
    if filepath.suffix.lower() == '.csv':
        try:
            df = pd.read_csv(filepath, nrows=5)
            cols = [c.lower() for c in df.columns]
            
            # Genesys Interactions export has these columns
            if 'total handle' in ' '.join(cols) or 'media type' in ' '.join(cols):
                return 'genesys_interactions'
            
            # QA evaluations have EvaluationId
            if 'evaluationid' in ' '.join(cols):
                return 'genesys_qa'
            
            # Agent status has specific duration columns
            if 'logged in' in ' '.join(cols) and 'on queue' in ' '.join(cols):
                return 'genesys_agent_status'
        except:
            pass
    
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
        'genesys_interactions': parse_genesys_interactions,
        'genesys_agent_status': parse_genesys_agent_status,
        'genesys_qa': parse_genesys_qa_evaluations,
        'wfm_adherence': parse_wfm_adherence,
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

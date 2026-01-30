#!/usr/bin/env python3
"""
HelpDesk Ticket Parser
======================

Standardized parsing and loading of ISPN HelpDesk ticket exports.

Usage:
    python parse_tickets.py --files "helpdesk_*.xls" --output parsed_tickets.csv
    
    # Or import in other scripts:
    from parse_tickets import load_tickets, parse_handle_time
"""

import pandas as pd
import glob
import argparse
import sys
from pathlib import Path


# ====================================================================================
# AGENT NAME LOOKUP (Common ISPN Agents)
# ====================================================================================

AGENT_LOOKUP = {
    # A
    'aaronmuccino': 'Aaron Muccino',
    'adrienbanuelos': 'Adrien Banuelos',
    'alvarosolis': 'Alvaro Solis',
    'angelicajones': 'Angelica Jones',
    
    # B
    'brenthank': 'Brent Hanks',
    'brittanyrosenbaugh': 'Brittany Rosenbaugh',
    'brocboyd': 'Broc Boyd',
    'brunobraschi': 'Bruno Braschi',
    
    # C
    'camdenmckinney': 'Camden McKinney',
    
    # D
    'danroof': 'Dan Roof',
    'davidaskew': 'David Askew',
    'davidliao': 'David Liao',
    'davidmcwilliams': 'David McWilliams',
    'derenhinckley': 'Deren Hinckley',
    'dewardabsher': 'Deward Absher',
    'dezzimmerman': 'Dez Zimmerman',
    'douglasrasmussen': 'Douglas Rasmussen',
    
    # E
    'elvisfrazier': 'Elvis Frazier',
    'ethankumke': 'Ethan Kumke',
    
    # F
    'fisherfoster': 'Fisher Foster',
    'franciscoguerrero': 'Francisco Guerrero',
    
    # G
    'grantwilliams': 'Grant Williams',
    
    # I
    'isaiahgalloway': 'Isaiah Galloway',
    
    # J
    'jaymurray': 'Jay Murray',
    'jeffstokes': 'Jeff Stokes',
    'jimmcmeen': 'Jim McMeen',
    'joshuahines': 'Joshua Hines',
    
    # L
    'lakemoore': 'Lake Moore',
    'luisvargas': 'Luis Vargas',
    
    # M
    'maetransier': 'Mae Transier',
    'matthewdevlin': 'Matthew Devlin',
    'mikealvarez': 'Mike Alvarez',
    
    # N
    'nathanaelbays': 'Nathanael Bays',
    
    # P
    'phalenwilliams': 'Phalen Williams',
    
    # R
    'rebeccafunk': 'Rebecca Funk',
    'robertwhite': 'Robert White',
    
    # S
    'sammcfarland': 'Sam McFarland',
    'scottyheritage': 'Scotty Heritage',
    'serataeschner': 'Sera Taeschner',
    'shawnawicklund': 'Shawna Wicklund',
    'skylarbeans': 'Skylar Bean',
    
    # T
    'terrellmorris': 'Terrell Morris',
    
    # Z
    'zacfreedle': 'Zac Freedle',
    'zeeyoyoung': 'Zee Young',
}


# ====================================================================================
# CORE PARSING FUNCTIONS
# ====================================================================================

def parse_handle_time(val):
    """
    Convert handle time string (H:MM:SS) to float minutes.
    
    Args:
        val: Handle time string or numeric value
        
    Returns:
        float: Handle time in minutes, or None if invalid
        
    Examples:
        >>> parse_handle_time("0:15:30")
        15.5
        >>> parse_handle_time("1:05:00")
        65.0
        >>> parse_handle_time("45:30")
        45.5
    """
    if pd.isna(val):
        return None
    try:
        parts = str(val).split(':')
        if len(parts) == 3:  # H:MM:SS or HH:MM:SS
            return int(parts[0]) * 60 + int(parts[1]) + int(parts[2]) / 60
        elif len(parts) == 2:  # MM:SS
            return int(parts[0]) + int(parts[1]) / 60
        # If no colons, assume it's already numeric
        return float(val)
    except (ValueError, AttributeError):
        return None


def extract_agent_info(email_address, agent_lookup=None):
    """
    Extract agent key and name from email address.
    
    Args:
        email_address: Agent email (e.g., "jaymurray@helpcafe.com")
        agent_lookup: Optional dictionary mapping keys to full names
        
    Returns:
        dict: {'agent_key': str, 'agent_name': str}
    """
    if pd.isna(email_address):
        return {'agent_key': None, 'agent_name': None}
    
    # Extract username from email
    agent_key = str(email_address).replace('@helpcafe.com', '').lower().strip()
    
    # Map to full name if lookup provided
    if agent_lookup and agent_key in agent_lookup:
        agent_name = agent_lookup[agent_key]
    else:
        agent_name = agent_key.title()  # Fallback: capitalize
    
    return {'agent_key': agent_key, 'agent_name': agent_name}


def load_single_file(filepath, engine='xlrd'):
    """
    Load a single HelpDesk ticket file.
    
    Args:
        filepath: Path to .xls file
        engine: Pandas Excel engine (default: 'xlrd' for old .xls format)
        
    Returns:
        DataFrame: Loaded ticket data
    """
    try:
        df = pd.read_excel(filepath, engine=engine)
        return df
    except Exception as e:
        print(f"Error loading {filepath}: {e}", file=sys.stderr)
        return None


def load_tickets(file_pattern, agent_lookup=None):
    """
    Load and parse one or more HelpDesk ticket files.
    
    Args:
        file_pattern: Glob pattern or list of file paths
        agent_lookup: Optional agent name lookup dictionary
        
    Returns:
        DataFrame: Combined and processed ticket data
    """
    # Handle glob pattern or list of files
    if isinstance(file_pattern, str):
        files = sorted(glob.glob(file_pattern))
    else:
        files = file_pattern
    
    if not files:
        raise ValueError(f"No files found matching pattern: {file_pattern}")
    
    print(f"Loading {len(files)} file(s)...")
    
    # Load all files
    dfs = []
    for f in files:
        df = load_single_file(f)
        if df is not None:
            # Add source file column
            df['Source_File'] = Path(f).name
            dfs.append(df)
    
    if not dfs:
        raise ValueError("No files loaded successfully")
    
    # Combine all files
    combined = pd.concat(dfs, ignore_index=True)
    
    # Apply standard parsing
    combined = parse_tickets(combined, agent_lookup=agent_lookup)
    
    print(f"Loaded {len(combined):,} tickets from {len(files)} file(s)")
    
    return combined


def parse_tickets(df, agent_lookup=None):
    """
    Apply standard parsing/enrichment to raw ticket data.
    
    Adds:
        - Handle_Min: Parsed handle time in minutes
        - Agent_Key: Extracted agent identifier
        - Agent_Name: Full agent name (if lookup provided)
        - Date: Date extracted from 'Entered On'
        - Is_Escalated: Boolean escalation flag
        - Is_Long_Call: Boolean flag for calls >20 min
        
    Args:
        df: Raw ticket DataFrame
        agent_lookup: Optional agent name lookup dictionary
        
    Returns:
        DataFrame: Enriched ticket data
    """
    if agent_lookup is None:
        agent_lookup = AGENT_LOOKUP
    
    # Parse handle time
    df['Handle_Min'] = df['Handle Time'].apply(parse_handle_time)
    
    # Extract agent info
    agent_info = df['By'].apply(lambda x: extract_agent_info(x, agent_lookup))
    df['Agent_Key'] = agent_info.apply(lambda x: x['agent_key'])
    df['Agent_Name'] = agent_info.apply(lambda x: x['agent_name'])
    
    # Extract date
    df['Date'] = pd.to_datetime(df['Entered On'], errors='coerce').dt.date
    
    # Escalation flag
    df['Is_Escalated'] = df['Esc'] == 1.0
    
    # Long call flag (>20 min)
    df['Is_Long_Call'] = df['Handle_Min'] > 20
    
    # Add day of week
    df['Day_of_Week'] = pd.to_datetime(df['Entered On'], errors='coerce').dt.day_name()
    
    return df


# ====================================================================================
# DATA QUALITY VALIDATION
# ====================================================================================

def validate_tickets(df):
    """
    Perform data quality checks on ticket data.
    
    Prints warnings for:
        - Invalid handle times
        - Missing required fields
        - Unexpected date ranges
        - Schema changes
        
    Args:
        df: Ticket DataFrame
    """
    print("\n" + "="*70)
    print("DATA QUALITY VALIDATION")
    print("="*70)
    
    # Expected columns
    expected_cols = [
        'Provider', 'Customer', 'Ticket', 'Interaction', 'Handle Time',
        'Service', 'Category', 'Entered On', 'By'
    ]
    
    missing_cols = set(expected_cols) - set(df.columns)
    if missing_cols:
        print(f"\n⚠️  WARNING: Missing expected columns: {missing_cols}")
    else:
        print("\n✓ All expected columns present")
    
    # Handle time validation
    invalid_ht = df['Handle_Min'].isna() | (df['Handle_Min'] < 0)
    if invalid_ht.sum() > 0:
        print(f"\n⚠️  WARNING: {invalid_ht.sum()} tickets with invalid handle time")
    else:
        print("\n✓ All handle times valid")
    
    # Date range
    try:
        date_range = f"{df['Date'].min()} to {df['Date'].max()}"
        print(f"\n✓ Date range: {date_range}")
    except:
        print("\n⚠️  WARNING: Could not determine date range")
    
    # Provider/Agent coverage
    print(f"\n✓ Unique providers: {df['Provider'].nunique()}")
    print(f"✓ Unique agents: {df['Agent_Key'].nunique()}")
    print(f"✓ Total tickets: {len(df):,}")
    
    # Category coverage
    print(f"✓ Unique categories: {df['Category'].nunique()}")
    
    print("\n" + "="*70)


# ====================================================================================
# COMMAND-LINE INTERFACE
# ====================================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Parse ISPN HelpDesk ticket exports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Load all files in directory
  python parse_tickets.py --files "helpdesk_*.xls" --output parsed.csv
  
  # Load specific files
  python parse_tickets.py --files file1.xls file2.xls --output parsed.csv
  
  # Validate only (no output)
  python parse_tickets.py --files "helpdesk_*.xls" --validate-only
        """
    )
    
    parser.add_argument(
        '--files',
        nargs='+',
        required=True,
        help='File pattern or list of files to load'
    )
    
    parser.add_argument(
        '--output',
        help='Output CSV file path'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate data, do not save output'
    )
    
    args = parser.parse_args()
    
    # Load tickets
    file_pattern = args.files[0] if len(args.files) == 1 else args.files
    tickets = load_tickets(file_pattern)
    
    # Validate
    validate_tickets(tickets)
    
    # Save output if requested
    if not args.validate_only:
        if not args.output:
            print("\nError: --output required unless --validate-only specified")
            sys.exit(1)
        
        tickets.to_csv(args.output, index=False)
        print(f"\n✓ Saved {len(tickets):,} tickets to {args.output}")


if __name__ == '__main__':
    main()

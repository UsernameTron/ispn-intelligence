---
name: helpdesk-ticket-analysis
description: Comprehensive analysis of ISPN HelpDesk ticket reports including handle time metrics, agent performance, category breakdowns, escalation tracking, and provider-specific KPIs. Use when analyzing daily/weekly ticket exports, comparing agent performance, identifying category trends, calculating excess handle time, or investigating provider-specific issues. Triggers on "analyze tickets", "HelpDesk report", "ticket categories", "agent handle time", "escalation analysis".
version: 1.0.0
---

# HelpDesk Ticket Analysis Skill

## File Structure & Format

HelpDesk ticket reports are exported as `.xls` files (old Excel format) with the naming convention:
```
helpdesk_ticket_report_daily_YYYY-MM-DD.xls
```

### Standard Schema (17 columns, consistent across all exports)

| Column | Type | Description | Null % |
|--------|------|-------------|--------|
| Provider | string | Partner/provider name | 0% |
| Customer | string | Customer name | ~1% |
| Customer Id | int | Unique customer identifier | 0% |
| Ticket | int | Ticket ID | 0% |
| Interaction | string | Genesys interaction UUID | 0% |
| Handle Time | string | Duration in H:MM:SS format | 0% |
| Service | string | Service type (Fiber, Cable, etc.) | ~3% |
| Category | string | Ticket category | 0% |
| Entered On | string | Timestamp (YYYY-MM-DD HH:MM) | 0% |
| By | string | Agent email (agent@helpcafe.com) | 0% |
| Esc | float | Escalation flag (1.0 = escalated) | ~78% null |
| CS Ref | float | Customer service reference | ~93% null |
| Partner Code Name | string | Partner escalation code | ~33% null |
| Tag Id | float | Tag identifier | ~11% null |
| Tag Name | string | Tag label | ~11% null |
| Alert Related | int | Alert flag (0/1) | 0% |
| Alert ID | int | Alert identifier | 0% |

## Core Analysis Patterns

### 1. Loading & Parsing Tickets

**ALWAYS use this standardized approach:**

```python
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Load single file
df = pd.read_excel('helpdesk_ticket_report_daily_2026-01-04.xls', engine='xlrd')

# Load multiple files (for weekly/period analysis)
files = ['helpdesk_ticket_report_daily_2026-01-04.xls', 
         'helpdesk_ticket_report_daily_2026-01-05.xls']
dfs = [pd.read_excel(f, engine='xlrd') for f in files]
all_tickets = pd.concat(dfs, ignore_index=True)
```

**Note:** Must use `engine='xlrd'` for old .xls format. Install if needed: `pip install xlrd --break-system-packages`

### 2. Handle Time Conversion

Handle Time is stored as string in `H:MM:SS` or `HH:MM:SS` format. Convert to minutes:

```python
def parse_handle_time(val):
    """Convert H:MM:SS string to minutes (float)"""
    if pd.isna(val): 
        return None
    try:
        parts = str(val).split(':')
        if len(parts) == 3:  # H:MM:SS or HH:MM:SS
            return int(parts[0]) * 60 + int(parts[1]) + int(parts[2])/60
        elif len(parts) == 2:  # MM:SS
            return int(parts[0]) + int(parts[1])/60
        return float(val)
    except:
        return None

df['Handle_Min'] = df['Handle Time'].apply(parse_handle_time)
```

### 3. Agent Name Extraction

Agent names are stored as email addresses. Extract clean names:

```python
# Create agent lookup dictionary (common ISPN agents)
agent_lookup = {
    'jaymurray': 'Jay Murray',
    'rebeccafunk': 'Rebecca Funk',
    'brunobraschi': 'Bruno Braschi',
    # ... add more as needed
}

# Extract agent key from email
df['Agent_Key'] = df['By'].str.replace('@helpcafe.com', '', regex=False).str.lower()

# Map to full names (optional)
df['Agent_Name'] = df['Agent_Key'].map(agent_lookup)
```

### 4. Provider Filtering

Always use case-insensitive substring matching for providers:

```python
# Filter to specific provider
gateway = df[df['Provider'].str.contains('Gateway', case=False, na=False)]

# Filter to multiple providers
providers = ['Gateway Fiber', 'Allo Communications', 'GVTC']
filtered = df[df['Provider'].isin(providers)]
```

### 5. Escalation Analysis

Identify escalated tickets:

```python
# Escalated tickets have Esc = 1.0
escalated = df[df['Esc'] == 1.0]

# Calculate escalation rate by agent
esc_rate = df.groupby('Agent_Key').agg({
    'Esc': lambda x: (x == 1.0).sum() / len(x) * 100
}).rename(columns={'Esc': 'Esc_Rate'})
```

## Common Analysis Scenarios

### Scenario 1: Agent Performance Comparison

**Goal:** Compare agents on same issue categories to identify performance gaps.

```python
# Filter to specific category
category_df = df[df['Category'] == 'Connectivity Basic']

# Calculate stats by agent (min 5 tickets)
agent_stats = category_df.groupby('Agent_Key').agg({
    'Handle_Min': ['count', 'mean', 'median']
}).round(2)
agent_stats.columns = ['Tickets', 'Avg_AHT', 'Median_AHT']
agent_stats = agent_stats[agent_stats['Tickets'] >= 5]

# Identify high-AHT agents (>1 std dev above mean)
threshold = agent_stats['Avg_AHT'].mean() + agent_stats['Avg_AHT'].std()
high_aht = agent_stats[agent_stats['Avg_AHT'] > threshold]
```

### Scenario 2: Category Trend Analysis

**Goal:** Identify which categories drive handle time elevation.

```python
# Group by category
cat_stats = df.groupby('Category').agg({
    'Handle_Min': ['count', 'mean', 'sum']
}).round(2)
cat_stats.columns = ['Count', 'Avg_AHT', 'Total_Min']

# Sort by total minutes (impact)
cat_stats = cat_stats.sort_values('Total_Min', ascending=False)

# Calculate percentage of total time
cat_stats['Pct_Time'] = cat_stats['Total_Min'] / cat_stats['Total_Min'].sum() * 100
```

### Scenario 3: Provider-Specific Issue Analysis

**Goal:** Analyze specific provider's ticket patterns and compare to overall.

```python
provider_name = 'Gateway Fiber'
provider_df = df[df['Provider'].str.contains(provider_name, case=False, na=False)]
other_df = df[~df['Provider'].str.contains(provider_name, case=False, na=False)]

# Compare category distribution
provider_cats = provider_df['Category'].value_counts(normalize=True) * 100
overall_cats = other_df['Category'].value_counts(normalize=True) * 100

# Compare handle times by category
comparison = pd.DataFrame({
    'Provider_AHT': provider_df.groupby('Category')['Handle_Min'].mean(),
    'Overall_AHT': other_df.groupby('Category')['Handle_Min'].mean()
})
comparison['Gap'] = comparison['Provider_AHT'] - comparison['Overall_AHT']
```

### Scenario 4: Excess Handle Time Calculation

**Goal:** Quantify wasted time from underperforming agents.

```python
# Define peer benchmark (agents performing at standard)
peer_benchmark = df.groupby('Category')['Handle_Min'].median()

# Calculate excess for each ticket
def calc_excess(row):
    benchmark = peer_benchmark.get(row['Category'], 0)
    return max(0, row['Handle_Min'] - benchmark)

df['Excess_Min'] = df.apply(calc_excess, axis=1)

# Aggregate by agent
agent_excess = df.groupby('Agent_Key').agg({
    'Excess_Min': 'sum',
    'Handle_Min': 'count'
}).rename(columns={'Handle_Min': 'Tickets'})

# Sort by total excess
agent_excess = agent_excess.sort_values('Excess_Min', ascending=False)
```

## Category Taxonomy

For comprehensive category groupings and definitions, see [references/category-taxonomy.md](references/category-taxonomy.md).

**Major Category Groups:**
- **Connectivity Issues** (~40% of tickets): Basic, Advanced, Intermittent, Speed Issues
- **Outages** (~11%): OUTAGE category
- **Setup & Configuration** (~4%): Equipment setup, Router WiFi
- **General Support** (~15%): Billing, Password, CS Referrals, Dead Air
- **Specialized** (~30%): Video, Phone, Email, Provider-specific

## KPI Calculation Methods

For detailed KPI definitions and calculation formulas, see [references/kpi-definitions.md](references/kpi-definitions.md).

**Key Metrics:**
- **Average Handle Time (AHT)**: Mean of Handle_Min where Handle_Min > 0
- **Median Handle Time**: Median of Handle_Min (more robust to outliers)
- **Escalation Rate**: (Tickets with Esc=1.0) / Total Tickets * 100
- **Productivity**: Total Tickets / Unique Agents
- **Long Call Rate**: (Tickets > 20 min) / Total Tickets * 100

## Advanced Scripts

For complex multi-file analysis, use bundled scripts:

### Agent Performance Analysis
```bash
python scripts/analyze_agent_performance.py \
  --files "helpdesk_*.xls" \
  --provider "Gateway Fiber" \
  --min-tickets 5
```

### Category Comparison
```bash
python scripts/category_analysis.py \
  --files "helpdesk_*.xls" \
  --compare-agents \
  --output category_report.csv
```

### Time Aggregation
```bash
python scripts/time_aggregation.py \
  --files "helpdesk_*.xls" \
  --period weekly \
  --metrics aht,escalation,volume
```

## Data Quality Checks

**Always perform these validations:**

1. **Handle Time Validation**
   ```python
   # Check for invalid times
   invalid = df[df['Handle_Min'].isna() | (df['Handle_Min'] < 0)]
   print(f"Invalid handle times: {len(invalid)}")
   ```

2. **Date Range Validation**
   ```python
   # Verify expected date range
   df['Date'] = pd.to_datetime(df['Entered On']).dt.date
   print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
   ```

3. **Schema Validation**
   ```python
   # Verify all expected columns present
   expected_cols = ['Provider', 'Customer', 'Ticket', 'Handle Time', 
                    'Category', 'By', 'Interaction']
   missing = set(expected_cols) - set(df.columns)
   if missing:
       print(f"WARNING: Missing columns: {missing}")
   ```

## Cross-Reference with Genesys Data

HelpDesk tickets can be joined to Genesys Interactions data using the `Interaction` field (UUID):

```python
# Load both datasets
tickets = pd.read_excel('helpdesk_ticket_report_daily_2026-01-04.xls', engine='xlrd')
genesys = pd.read_csv('2026-01-12_Interactions.csv')

# Join on interaction ID
merged = tickets.merge(
    genesys, 
    left_on='Interaction', 
    right_on='Conversation Id',
    how='inner'
)

# Now you can correlate ticket categories with Genesys metrics
# (AHT from Genesys vs Handle Time from tickets, etc.)
```

## Best Practices

1. **Always filter out null handle times** before calculating averages
2. **Use median over mean** when outliers are present (20+ min calls)
3. **Require minimum ticket counts** (n≥5) for agent comparisons
4. **Group similar categories** using category taxonomy for higher-level insights
5. **Cross-validate with Genesys** when available for comprehensive analysis
6. **Document assumptions** when defining "peer benchmarks" or targets

## Common Pitfalls

❌ **Don't compare raw counts** without accounting for agent availability/shift length  
✅ Use handle time per ticket, not total tickets

❌ **Don't use mean AHT** with long-tail distributions  
✅ Use median or calculate after removing outliers (>20 min)

❌ **Don't assume category names are standardized**  
✅ Use substring matching and group variants (see category taxonomy)

❌ **Don't filter by agent name strings directly**  
✅ Extract agent keys from emails first for consistency

❌ **Don't aggregate without validating date ranges**  
✅ Always check actual dates in 'Entered On' field

## Output Formatting

When presenting analysis results, use this structure:

```python
print("=" * 70)
print("HELPDESK TICKET ANALYSIS SUMMARY")
print("=" * 70)
print(f"\nDate Range: {start_date} to {end_date}")
print(f"Total Tickets: {len(df):,}")
print(f"Unique Providers: {df['Provider'].nunique()}")
print(f"Unique Agents: {df['By'].nunique()}")

print("\n--- TOP CATEGORIES BY VOLUME ---")
top_cats = df['Category'].value_counts().head(10)
for cat, count in top_cats.items():
    pct = count / len(df) * 100
    print(f"  {cat:<50} {count:>5} ({pct:>5.1f}%)")

print("\n--- HANDLE TIME METRICS ---")
print(f"  Overall Mean AHT: {df['Handle_Min'].mean():.2f} min")
print(f"  Overall Median AHT: {df['Handle_Min'].median():.2f} min")
print(f"  Long Calls (>20 min): {(df['Handle_Min'] > 20).sum()} ({(df['Handle_Min'] > 20).mean()*100:.1f}%)")
```

## Integration Points

This skill integrates with:
- **`genesys-cloud-cx-reporting`**: Cross-reference via Interaction UUID
- **`analyzing-ispn-wcs-reports`**: Validate partner-level AHT calculations
- **`analyzing-ispn-lt-scorecard`**: Connect ticket metrics to KPI targets

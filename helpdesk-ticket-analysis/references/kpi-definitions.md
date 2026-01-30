# HelpDesk Ticket KPI Definitions

This document defines standard Key Performance Indicators (KPIs) calculated from HelpDesk ticket data.

---

## Core Handle Time Metrics

### Average Handle Time (AHT)

**Definition:** Mean duration of ticket resolution measured in minutes.

**Calculation:**
```python
# Exclude zero or null handle times
valid_tickets = df[df['Handle_Min'] > 0]
aht = valid_tickets['Handle_Min'].mean()
```

**Target Ranges by Category:**
- Connectivity Basic: 10-12 minutes
- Connectivity Advanced: 13-15 minutes
- Outage Notification: 4-6 minutes
- Setup & Configuration: 12-16 minutes
- Overall Center: 10.5-11.5 minutes

**Notes:**
- Use **median** instead of mean when distribution has long tail (>10% of calls over 20 min)
- Exclude Dead Air/Hang Up categories (non-productive time)
- Cross-validate with Genesys data when available

---

### Median Handle Time

**Definition:** Middle value of handle time distribution.

**Calculation:**
```python
median_aht = valid_tickets['Handle_Min'].median()
```

**When to Use:**
- When distribution is skewed by outliers
- For executive reporting (more stable metric)
- When comparing agents with different case mixes

**Interpretation:**
- If median << mean: Distribution has long tail (investigate 20+ min calls)
- If median ≈ mean: Distribution is relatively normal

---

### Percentile Analysis

**Definition:** Handle time at specific percentiles.

**Calculation:**
```python
p50 = df['Handle_Min'].quantile(0.50)  # Median
p75 = df['Handle_Min'].quantile(0.75)  # 75th percentile
p90 = df['Handle_Min'].quantile(0.90)  # 90th percentile
p95 = df['Handle_Min'].quantile(0.95)  # 95th percentile
```

**Interpretation:**
- **P75:** Threshold for "long call" alert (typically 15-18 min)
- **P90:** Outlier threshold (typically 20-25 min)
- **P95:** Extreme outlier threshold (typically 30+ min)

---

## Volume Metrics

### Total Ticket Volume

**Definition:** Count of tickets in specified time period.

**Calculation:**
```python
total_tickets = len(df)
```

**Segmentation:**
- By provider
- By category
- By agent
- By day of week
- By hour of day (if timestamp available)

---

### Tickets Per Agent

**Definition:** Productivity measure (tickets handled per agent).

**Calculation:**
```python
tickets_per_agent = df.groupby('Agent_Key').size()
```

**Target:**
- Varies by shift length and availability
- Typical: 15-25 tickets per 8-hour shift
- Adjust for breaks, meetings, non-phone time

**Warning:** Raw counts don't account for case complexity. Use alongside AHT.

---

### Long Call Rate

**Definition:** Percentage of tickets exceeding a threshold (typically 20 minutes).

**Calculation:**
```python
long_calls = (df['Handle_Min'] > 20).sum()
long_call_rate = long_calls / len(df) * 100
```

**Thresholds:**
- **15 minutes:** Warning threshold (supervisor attention recommended)
- **20 minutes:** Long call threshold (coaching opportunity)
- **30 minutes:** Extreme outlier (process failure indicator)

**Target:** < 5% of tickets should exceed 20 minutes

---

## Quality Metrics

### Escalation Rate

**Definition:** Percentage of tickets escalated to higher-tier support.

**Calculation:**
```python
escalated = (df['Esc'] == 1.0).sum()
escalation_rate = escalated / len(df) * 100
```

**Target:** 10-15% (varies by partner and category)

**Interpretation:**
- High rate (>20%): Possible knowledge gap, improper routing, or complex partner
- Low rate (<5%): May indicate under-escalation or strong agent knowledge

**Segmentation:**
- By agent (identify training needs)
- By category (identify process gaps)
- By provider (identify partner complexity)

---

### Tag Analysis

**Definition:** Distribution of tags applied to tickets.

**Calculation:**
```python
tag_dist = df['Tag Name'].value_counts()
tag_rate = df['Tag Name'].notna().sum() / len(df) * 100
```

**Common Tags:**
- "Escalated For Review"
- "Callback Required"
- "Customer Satisfaction Issue"

**Note:** Only ~11% of tickets have tags; absence doesn't mean no issue.

---

## Agent Performance Metrics

### Agent AHT Comparison

**Definition:** Compare individual agent AHT to peer benchmark.

**Calculation:**
```python
# Calculate peer benchmark (median or mean of agents with similar volume)
peer_benchmark = df.groupby('Category')['Handle_Min'].median()

# Calculate agent performance vs benchmark
agent_performance = df.groupby('Agent_Key').apply(
    lambda x: pd.Series({
        'Tickets': len(x),
        'Avg_AHT': x['Handle_Min'].mean(),
        'Benchmark': peer_benchmark[x['Category']].mean(),
        'Deviation': x['Handle_Min'].mean() - peer_benchmark[x['Category']].mean()
    })
)
```

**Interpretation:**
- Deviation > +2 min: Performance concern, coaching needed
- Deviation > +5 min: Critical performance issue
- Deviation < -2 min: Possible quality trade-off (check escalation rate)

**Requirements:**
- Minimum 5 tickets per agent for statistical validity
- Compare within same category mix
- Control for complexity (partner, time of day)

---

### Excess Handle Time

**Definition:** Wasted minutes from underperforming agents.

**Calculation:**
```python
# Define benchmark (use median by category)
benchmarks = df.groupby('Category')['Handle_Min'].median()

# Calculate excess for each ticket
def calc_excess(row):
    benchmark = benchmarks.get(row['Category'], 0)
    return max(0, row['Handle_Min'] - benchmark)

df['Excess_Min'] = df.apply(calc_excess, axis=1)

# Aggregate by agent
agent_excess = df.groupby('Agent_Key')['Excess_Min'].sum()
```

**FTE Impact:**
```python
# Productive minutes per FTE per week (40 hrs * 60 min * 55% utilization)
productive_min_per_fte = 40 * 60 * 0.55  # 1,320 minutes

# Calculate FTE equivalent
fte_wasted = total_excess_min / productive_min_per_fte
```

**Interpretation:**
- Total excess > 500 min/week: Significant opportunity (~0.4 FTE)
- Total excess > 1000 min/week: Critical opportunity (~0.75 FTE)

---

### Agent Consistency Score

**Definition:** Standard deviation of agent handle times (lower = more consistent).

**Calculation:**
```python
agent_consistency = df.groupby('Agent_Key')['Handle_Min'].std()
```

**Interpretation:**
- Low std dev (<5 min): Consistent process adherence
- High std dev (>10 min): Inconsistent approach or varied case mix

---

## Category Performance Metrics

### Category AHT

**Definition:** Average handle time by category.

**Calculation:**
```python
category_aht = df.groupby('Category').agg({
    'Handle_Min': ['count', 'mean', 'median', 'std']
})
```

**Use Cases:**
- Identify high-impact categories (high volume + high AHT)
- Compare agent performance within same category
- Establish category-specific benchmarks

---

### Category Distribution

**Definition:** Percentage of tickets by category.

**Calculation:**
```python
category_dist = df['Category'].value_counts(normalize=True) * 100
```

**Use Cases:**
- Identify training priorities (high-volume categories)
- Compare agent case mix
- Validate routing effectiveness

---

## Provider-Specific Metrics

### Provider AHT

**Definition:** Handle time by provider/partner.

**Calculation:**
```python
provider_aht = df.groupby('Provider').agg({
    'Handle_Min': ['count', 'mean', 'median']
})
```

**Use Cases:**
- Identify complex partners requiring specialized knowledge
- Validate partner-specific training needs
- Negotiate support agreements

---

### Provider Escalation Rate

**Definition:** Escalation rate by provider.

**Calculation:**
```python
provider_esc = df.groupby('Provider').agg({
    'Esc': lambda x: (x == 1.0).sum() / len(x) * 100
})
```

**Interpretation:**
- High rate: Partner complexity or documentation gaps
- Compare to overall center rate (10-15%)

---

## Time-Based Metrics

### Day-of-Week Trends

**Definition:** Volume and AHT by day of week.

**Calculation:**
```python
df['Day_of_Week'] = pd.to_datetime(df['Entered On']).dt.day_name()
daily_stats = df.groupby('Day_of_Week').agg({
    'Handle_Min': ['count', 'mean']
})
```

**Typical Patterns:**
- Monday: High volume (post-weekend issues)
- Friday: Lower volume
- AHT may increase on high-volume days

---

### Hour-of-Day Trends

**Definition:** Volume and AHT by hour (if timestamp available).

**Calculation:**
```python
df['Hour'] = pd.to_datetime(df['Entered On']).dt.hour
hourly_stats = df.groupby('Hour').agg({
    'Handle_Min': ['count', 'mean']
})
```

**Typical Patterns:**
- Morning (8-10 AM): Moderate volume
- Midday (12-2 PM): Peak volume
- Evening (6-9 PM): Lower volume but may have higher complexity

---

## Composite Scores

### Agent Performance Index (API)

**Definition:** Weighted score combining multiple metrics.

**Calculation:**
```python
# Normalize each metric to 0-100 scale
normalized_aht = 100 - (agent_aht - min_aht) / (max_aht - min_aht) * 100
normalized_volume = (agent_volume - min_volume) / (max_volume - min_volume) * 100
normalized_esc = 100 - (agent_esc_rate - min_esc) / (max_esc - min_esc) * 100

# Weighted composite (adjust weights as needed)
api = (normalized_aht * 0.5) + (normalized_volume * 0.3) + (normalized_esc * 0.2)
```

**Weights (recommended):**
- AHT: 50% (primary efficiency metric)
- Volume: 30% (productivity)
- Escalation Rate: 20% (quality proxy)

**Interpretation:**
- API > 80: Top performer
- API 60-80: Meeting expectations
- API < 60: Performance concern

---

## Statistical Significance

### Minimum Sample Sizes

When comparing agents or categories, ensure adequate sample sizes:

| Comparison Type | Minimum n |
|----------------|-----------|
| Agent vs Agent | 5 tickets each |
| Agent vs Benchmark | 10 tickets |
| Category Analysis | 20 tickets |
| Provider Analysis | 30 tickets |

### Confidence Intervals

**95% Confidence Interval for Mean AHT:**

```python
import scipy.stats as stats

mean_aht = df['Handle_Min'].mean()
sem = stats.sem(df['Handle_Min'])  # Standard error of mean
ci = stats.t.interval(0.95, len(df)-1, loc=mean_aht, scale=sem)

print(f"95% CI: {ci[0]:.2f} to {ci[1]:.2f} minutes")
```

**When to Use:**
- Small sample sizes (n < 30)
- Executive reporting (show uncertainty)
- Comparing time periods

---

## Benchmarking Standards

### ISPN Tech Center Targets

| Metric | Target | Warning Threshold | Critical Threshold |
|--------|--------|-------------------|-------------------|
| Overall AHT | 10.7 min | 11.5 min | 12.0 min |
| Connectivity Basic | 10.0 min | 11.0 min | 12.0 min |
| Long Call Rate | <5% | 7% | 10% |
| Escalation Rate | 10-15% | 18% | 20% |
| Tickets/Agent/Day | 18-22 | <15 | <12 |

### Industry Standards

| Metric | Tier 1 Support | Tier 2 Support |
|--------|---------------|----------------|
| AHT | 8-12 min | 15-25 min |
| FCR | 70-80% | 85-95% |
| Escalation | 15-20% | 5-10% |

**Note:** ISPN operates as combined Tier 1/2 for many partners.

---

## Reporting Templates

### Executive Summary Format

```python
print("=" * 70)
print("WEEKLY HELPDESK PERFORMANCE SUMMARY")
print("=" * 70)
print(f"\nPeriod: {start_date} to {end_date}")
print(f"Total Tickets: {total_tickets:,}")
print(f"\n--- KEY METRICS ---")
print(f"  Overall AHT: {overall_aht:.2f} min (Target: 10.7 min)")
print(f"  Long Call Rate: {long_call_rate:.1f}% (Target: <5%)")
print(f"  Escalation Rate: {esc_rate:.1f}% (Target: 10-15%)")
print(f"\n--- TOP PERFORMERS (Lowest Excess) ---")
# List top 5
print(f"\n--- OPPORTUNITIES (Highest Excess) ---")
# List bottom 5
```

### Detailed Agent Report Format

```python
print(f"\nAgent: {agent_name}")
print(f"  Tickets: {ticket_count}")
print(f"  Avg AHT: {agent_aht:.2f} min (Peer Avg: {peer_aht:.2f} min)")
print(f"  Deviation: {deviation:+.2f} min")
print(f"  Escalation Rate: {esc_rate:.1f}%")
print(f"  Long Calls: {long_calls} ({long_call_pct:.1f}%)")
print(f"  Excess Minutes: {excess_min:.0f} min")
```

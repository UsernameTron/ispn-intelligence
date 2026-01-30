# Genesys Cloud CX KPI Formulas Quick Reference

## Time Unit Conversions

```
Milliseconds to Hours:   ms / 3,600,000
Milliseconds to Minutes: ms / 60,000
Milliseconds to Seconds: ms / 1,000
Minutes to Hours:        min / 60
```

## Core Call Metrics

### AHT (Average Handle Time)
```
AHT (minutes) = SUM(Total Handle) / COUNT(Handled Calls) / 60,000

Filter:
- Direction = "Inbound"
- Abandoned = "NO"
- Total Handle >= 20,000 (20 seconds minimum)
```

### AWT (Average Wait Time)
```
AWT (seconds) = SUM(Total Queue) / COUNT(All Offered) / 1,000

Filter:
- Direction = "Inbound"
- Include both Abandoned=YES and Abandoned=NO
```

### Service Level (Answered ≤ X seconds)
```
SL % = COUNT(Total Alert <= X000) / COUNT(Handled Calls) × 100

Thresholds:
- ≤30 sec:  Total Alert <= 30,000
- ≤60 sec:  Total Alert <= 60,000
- ≤90 sec:  Total Alert <= 90,000
- ≤120 sec: Total Alert <= 120,000
```

### Abandonment Rate
```
Abandon Rate % = COUNT(Abandoned) / COUNT(All Offered) × 100

Long Abandons (≥60s):
- Abandoned = "YES"
- Total Queue >= 60,000
```

## Workforce Metrics

### Total Hours Worked
```
Hours Worked = SUM(Logged In) / 3,600,000

Filter:
- Department = "Tech Center"
```

### On-Queue Hours
```
On-Queue Hours = SUM(On Queue) / 3,600,000

Filter:
- Department = "Tech Center"
```

### Training Hours
```
Training Hours = SUM(Training) / 3,600,000

Filter:
- Department = "Tech Center"
```

### Shrinkage
```
Hours Worked (excl. training) = Total Hours Worked - Training Hours
Shrinkage Hours = Hours Worked (excl. training) - On-Queue Hours
Shrinkage % = Shrinkage Hours / Hours Worked (excl. training) × 100

Target: ≤ 20%
```

### Utilization
```
Utilization % = Inbound Call Hours / Hours Worked (excl. training) × 100

Where:
- Inbound Call Hours = SUM(Total Handle for Inbound) / 3,600,000

Target: > 55%
```

### Occupancy
```
Occupancy % = Total Call Hours / On-Queue Hours × 100

Where:
- Total Call Hours = Inbound + Outbound + Callback Hours

Target: > 75%
```

## Call Type Filters

### Inbound Handled (≥20s)
```python
(Direction == "Inbound") & 
(Abandoned == "NO") & 
(Total_Handle >= 20000)
```

### Callbacks
```python
(Media_Type == "callback")
```

### Outbound (excluding callbacks)
```python
(Direction == "Outbound") & 
(Media_Type == "voice")
```

### Abandoned (≥60s)
```python
(Direction == "Inbound") & 
(Abandoned == "YES") & 
(Total_Queue >= 60000)
```

## AHT Decomposition
```
AHT = Avg Talk + Avg Hold + Avg ACW

Components:
- Avg Talk = SUM(Total Talk) / COUNT(Handled) / 60,000
- Avg Hold = SUM(Total Hold) / COUNT(Handled) / 60,000
- Avg ACW  = SUM(Total ACW)  / COUNT(Handled) / 60,000
```

## WFM Metrics

### Adherence
```
Adherence % = (Scheduled Time - Exception Duration) / Scheduled Time × 100
```

### Conformance
```
Conformance % = Actual Time In Status / Scheduled Time In Status × 100
```

## Target Benchmarks

| Metric | Target | Direction |
|--------|--------|-----------|
| AHT | < 10.7 min | Lower is better |
| AWT | < 90 sec | Lower is better |
| FCR | > 70% | Higher is better |
| Utilization | > 55% | Higher is better |
| Occupancy | > 75% | Higher is better |
| Shrinkage | ≤ 20% | Lower is better |
| Adherence | > 90% | Higher is better |

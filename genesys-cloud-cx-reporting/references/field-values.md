# Genesys Cloud CX Field Values Reference

This document contains validated field values from live ISPN Tech Center exports.

## Interactions Export Field Values

### Direction
| Value | Description | Count (Sample Week) |
|-------|-------------|---------------------|
| `Inbound` | Customer-initiated calls to queue | 15,315 |
| `Outbound` | Agent-initiated outbound calls | 2,264 |
| `Inbound/Outbound` | Callback interactions (both legs) | 2,222 |

**Usage Notes:**
- Callbacks always show as `Inbound/Outbound`
- Use with `Media Type` to distinguish voice from callback

### Media Type
| Value | Description | Count (Sample Week) |
|-------|-------------|---------------------|
| `voice` | Standard voice calls | 18,888 |
| `callback` | Callback interactions | 871 |
| `message` | Chat/messaging | 42 |

**Usage Notes:**
- **Use `Media Type = "callback"` to identify callbacks** (most reliable method)
- Exclude `message` from voice metrics

### Abandoned
| Value | Description |
|-------|-------------|
| `YES` | Call abandoned before agent answer |
| `NO` | Call handled by agent |

### Disconnect Type
| Value | Description | Typical Scenario |
|-------|-------------|------------------|
| `External` | Customer/external party disconnected | Normal call completion |
| `Agent` | Agent disconnected | Normal call completion |
| `System` | System disconnected | Timeout, error, transfer |

### Flow-Out Type
| Value | Description | Count (Sample Week) |
|-------|-------------|---------------------|
| `callback` | Flowed to callback | 410 |
| `voicemail` | Flowed to voicemail | 219 |
| `acd; voicemail` | ACD then voicemail | 191 |
| `acd; callback` | ACD then callback | 46 |
| `ivr` | Remained in IVR | 5 |
| `group` | Flowed to group | 2 |
| `acd` | Flowed to ACD | 1 |

**Usage Notes:**
- Flow-out indicates where abandoned/non-handled calls went
- Can be used as secondary callback identifier

### Wrap-up
| Value | Description | Count (Sample Week) |
|-------|-------------|---------------------|
| `ININ-WRAP-UP-TIMEOUT` | Agent timed out (15s limit) | 15,383 |
| `Default Wrap-up Code` | Manual selection | 193 |
| Combined values | Multiple codes applied | 13 |

**Critical Finding:**
97.9% of calls show `ININ-WRAP-UP-TIMEOUT`, indicating:
- System enforces 15-second ACW timeout
- Agents are not manually selecting wrap-up codes
- The workbook's 15-second ACW assumption is accurate

### Non-ACD
| Value | Description | Count (Sample Week) |
|-------|-------------|---------------------|
| `NO` | Queue-routed interaction | 14,319 |
| `YES` | Non-queue (direct, internal) | 5,482 |

**Usage Notes:**
- **Exclude `Non-ACD = "YES"` from queue metrics**
- These have blank Queue field

### Transferred
| Value | Description |
|-------|-------------|
| `YES` | Interaction was transferred |
| `NO` | No transfer occurred |

---

## Agent Status Duration Details Field Values

### Department
| Value | Agent Count (Sample) | Include in TC Metrics |
|-------|---------------------|----------------------|
| `Tech Center` | 146 | ✅ Yes |
| `Engineering` | 9 | ❌ No |
| `Administration` | 3 | ❌ No |
| `QC` | 2 | ❌ No |
| `Finance` | 2 | ❌ No |
| `Human Resources` | 2 | ❌ No |
| `Training` | 1 | ❌ No |
| `Recruiting` | 1 | ❌ No |
| `Sales` | 1 | ❌ No |
| (blank/NaN) | 15 | ❌ No |

**Usage Notes:**
- Filter to `Department = "Tech Center"` for L1-L3 metrics
- 146 agents in Tech Center

### Division Name
| Value | Description |
|-------|-------------|
| `Home` | Default division |

---

## WFM Historical Adherence Field Values

### Management Unit
| Value | Agent Count (Sample) |
|-------|---------------------|
| `Permanent Schedules MU` | 146 |

### Net Impact
| Value | Description | Count (Sample) |
|-------|-------------|----------------|
| `Negative` | Worked less than scheduled | 138 |
| `Positive` | Worked more than scheduled | 6 |
| `Neutral` | On target | 1 |
| `Unknown` | Cannot calculate | 1 |

### Adherence (%) / Conformance (%)
- Format: Percentage string (e.g., "80.95%")
- Range: 0.96% to 100.00%
- Special value: `Infinity%` for conformance when no scheduled time

---

## Agent Performance Field Values

### Media Type
| Value | Description |
|-------|-------------|
| `voice` | Voice interactions |

### Department
Same as Agent Status Duration Details (filter to `Tech Center`)

---

## Time Unit Reference

### Milliseconds (Interactions, Agent Status, Agent Performance)
| To Convert To | Divide By |
|---------------|-----------|
| Seconds | 1,000 |
| Minutes | 60,000 |
| Hours | 3,600,000 |

### Minutes (WFM Adherence)
| To Convert To | Operation |
|---------------|-----------|
| Seconds | Multiply by 60 |
| Hours | Divide by 60 |

---

## Queue Names (Sample - Top 20)

| Queue | Volume (Sample Week) |
|-------|---------------------|
| Fastwyre | 909 |
| Lightcurve | 766 |
| Gateway Fiber | 760 |
| CNSNext | 670 |
| BTC Broadband (Online Plus) | 562 |
| IdeaTek | 492 |
| GVTC | 484 |
| Amherst Communications | 471 |
| Mid-Rivers | 470 |
| Twin Valley | 462 |
| KCTC (Kalona Cooperative Telephone) | 385 |
| Allo Communications | 385 |
| ISPN Callcenter Backline - 2 | 382 |
| FOCUS Broadband | 356 |
| Vero Broadband | 346 |
| WTC Customer Service | 310 |
| Norvado | 266 |
| TCT WY/West | 237 |
| Chariton Valley | 229 |
| WTC (Wamego Telephone) | 216 |

---

## ACW (After Call Work) Distribution

| ACW Value | Count | Percentage | Significance |
|-----------|-------|------------|--------------|
| 15,000ms (15s) | 15,261 | 97.9% | System timeout |
| 30,000ms (30s) | 127 | 0.8% | Extended wrap-up |
| 45,000ms (45s) | 6 | <0.1% | Long wrap-up |
| < 15,000ms | 179 | 1.1% | Early completion |
| > 45,000ms | 0 | 0% | None observed |

**Key Insight:** The 15-second ACW timeout is system-enforced via `ININ-WRAP-UP-TIMEOUT` wrap-up code.

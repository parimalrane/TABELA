
# TABELA FUTURE ROADMAP (REVISED)

## CURRENT STATUS

```text
CORE ENGINE            → STABLE
HISTORY LAYER         → STABLE
LONG ENGINE           → PROTECTED
DATA COLLECTION       → ACTIVE
OBSERVATION PHASE     → ACTIVE
```

Current rule:

```text
No major architecture changes until enough live market history exists.
```

---

# P0 — OBSERVATION PHASE (ACTIVE NOW)

Duration:

```text
15–20 live trading sessions minimum
```

Daily validation:

* Long output quality
* Short output quality
* Theme rotation consistency
* Unknown classification quality
* Historical logging integrity

Rules:

* No scoring changes
* No architecture redesign
* No history redesign

Status:

```text
ACTIVE
```

---

# P1 — SHORT ENGINE REBUILD (HIGHEST PRIORITY)

Current issue:

Short engine is weakest component.

Problem:

Weak stock ≠ Short opportunity

Need better distinction:

```text
Healthy Pullback
vs
Institutional Distribution
vs
Structural Weakness
```

Future buckets:

```text
Bucket 1 → Distribution Watchlist
Bucket 2 → Weakness Watchlist
Bucket 3 → True Short Candidates
```

Priority:

```text
CRITICAL
```

---

# P2 — UNKNOWN CLASSIFICATION LEARNING LOOP

Current system exists.

Weekly process:

```text
Review unknown_emerging_leaders.csv
Update company_theme_mapping.csv
Improve classification accuracy
```

Purpose:

Allow market behavior to improve theme intelligence.

Priority:

```text
HIGH
```

Status:

```text
ACTIVE
```

---

# P3 — THEME ARCHITECTURE REDESIGN

Current weaknesses:

* Hardcoded ticker mapping
* Multiple theme authority sources
* Manual maintenance burden

Future structure:

```text
config/

company_theme_mapping.csv
theme_rules.csv
theme_taxonomy.csv
```

Objectives:

* Remove hardcoded dictionaries
* Single source of truth
* Weekly maintenance only

Priority:

```text
HIGH
```

---

# P4 — ARCHITECTURE CLEANUP

Current issue:

```text
main.py becoming orchestration bottleneck
```

Future structure:

```text
main.py
core_pipeline.py
logging_pipeline.py
reporting_pipeline.py
```

Rule:

Optional modules never break core engine.

Priority:

```text
HIGH
```

Deferred until observation phase ends.

---

# P5 — SCORING ENGINE REVIEW

Audit:

* RS weighting
* Theme weighting
* Sales growth weighting
* Margin weighting
* Zacks weighting

Question:

```text
Are analyst/fundamental factors overweighted?
```

Principle:

```text
Price leads analyst opinion
```

Priority:

```text
HIGH
```

---

# P6 — ROTATION INTELLIGENCE ENGINE

Purpose:

Track:

* Theme acceleration
* Theme weakening
* Theme persistence
* Entry/exit from leadership

Example:

```text
Semiconductors strengthening 6 sessions
Biotech emerging 4 sessions
Software weakening 3 sessions
```

Requires sufficient historical data.

Priority:

```text
HIGH
```

Do not build before 30+ sessions.

---

# P7 — LEADERSHIP DETERIORATION ENGINE

Purpose:

Detect leaders losing sponsorship.

Signals:

* RS deterioration
* Long score deterioration
* Theme deterioration
* Exit from long candidate universe

Goal:

Detect institutional distribution.

Requires historical database.

Priority:

```text
HIGH
```

---

# P8 — THEME BREADTH EXPANSION ENGINE

Track:

* Breadth expansion trend
* Breadth deterioration trend
* Internal participation changes

Questions:

```text
Is participation broadening?
Is leadership narrowing?
```

Priority:

```text
HIGH
```

---

# P9 — INTERNAL ROTATION ENGINE

Detect divergence inside strong themes.

Example:

```text
Semiconductors strong

NVDA strong
MU strong
AMD weakening
AVGO weakening
```

Interpretation:

Capital rotating internally.

Priority:

```text
MEDIUM
```

Requires history.

---

# P10 — MARKET REGIME ENGINE

Classify environment.

Possible regimes:

```text
Broad Bull Market
Narrow Leadership
Defensive Rotation
Risk Off
Commodity Cycle
AI Supercycle
```

Purpose:

Understand macro institutional behavior.

Priority:

```text
MEDIUM
```

---

# P11 — QUIET ACCUMULATION ENGINE

Goal:

Detect silent institutional accumulation before breakout.

Requires:

Large historical database.

Priority:

```text
LATER
```

Minimum 3 months data first.

---

# P12 — PRE BREAKOUT FINGERPRINT ENGINE

Study past winners.

Examples:

```text
NVDA
PLTR
ARM
APP
CRDO
```

Question:

```text
What recurring behavior exists before explosive moves?
```

Priority:

```text
LATER
```

Need substantial history.

---

# LONG TERM DESTINATION

## HISTORICAL INTELLIGENCE ENGINE

Final objective:

Learn recurring institutional behavior.

Detect:

* Capital accumulation
* Distribution
* Theme persistence
* Leadership deterioration
* Rotation sequences

Goal:

```text
Understand institutional behavior before market recognizes it.
```

---

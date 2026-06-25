Excellent. This is the right moment to formalize operating discipline.

I am treating this as **institutional operating manual**, not documentation.

Purpose:

```text
Make TABELA sustainable for 3+ years

Prevent architecture drift

Ensure intelligence quality improves over time

Avoid random feature building

Keep maintenance low friction
```

Below is what I would put in **MAINTENANCE_RULES.md** (I would consider this production-grade).

---

# `MAINTENANCE_RULES.md`

# TABELA Maintenance & Review Framework

## Core Philosophy

TABELA is an **Institutional Capital Rotation Intelligence Engine**.

Primary mission:

* Detect institutional capital flow
* Identify strongest themes for LONG opportunities
* Identify weakest themes for SHORT opportunities
* Track theme rotation over time
* Build long-term market intelligence database

TABELA is NOT:

* Stock screener
* Coding experiment
* Technical analysis engine
* Static stock classification database

---

# Architecture Rule (Permanent)

TABELA follows strict 3-layer architecture.

## Layer 1 → Core Engine (Protected)

Mandatory daily runtime.

Runs ONLY with:

* ETF.csv
* stocks.csv

Protected modules:

* ETF Engine
* Theme Engine
* Stock Mapping Engine
* Scoring Engine
* Long Engine
* Short Engine
* Rotation Engine

Rules:

* Must work independently
* Must NEVER depend on optional modules
* Must continue working even if all optional layers are deleted

---

## Layer 2 → Intelligence Layer (Optional)

Purpose:

Improve intelligence quality through periodic review.

Examples:

* History Engine
* Snapshot Engine
* Weekly Review Engine
* Mapping Drift Detection
* Theme Rotation Analysis
* Leadership Deterioration Detection

Rules:

* Can be deleted safely
* Core engine must remain unaffected

---

## Layer 3 → Experimental Layer

Purpose:

Research and experimentation.

Examples:

* Anomaly Detection
* Machine Learning Models
* AI Prediction Models
* Behavioral Models

Rules:

* Can fail safely
* Must NEVER affect production stability

---

# Weekly Review Process (Mandatory)

Frequency:

* Every Friday or Weekend

Maximum time:

* 30 minutes

---

## Files User Provides to ChatGPT

Every week submit:

1. Latest ETF.csv

2. Latest stocks.csv

3. Last 5–7 JSON snapshot files

4. Friday terminal output

---

## ChatGPT Weekly Review Responsibilities

ChatGPT acts as:

* Senior Solution Architect
* Quant Research Specialist
* Institutional Capital Flow Analyst
* Market Maker
* Hedge Fund Portfolio Manager
* Professional Trader

ChatGPT performs:

---

### 1. Theme Rotation Review

Detect:

* Strengthening themes
* Weakening themes
* Emerging themes
* Deteriorating themes

Example:

* AI weakening
* Financials strengthening
* Defense emerging

---

### 2. Mapping Drift Review

Detect:

* Unmapped stocks repeatedly appearing
* Stocks mapped incorrectly
* Obsolete stock mappings

Example output:

```text
Add:

SEZL → Fintech
SNEX → Financial Services

Remove:

XYZ obsolete mapping
```

---

### 3. Behavioral Narrative Shift Detection

Behavior-based inference only.

Examples:

```text
PLTR behaving more like AI than Defense

HOOD trading increasingly with Digital Assets cohort
```

No external research required.

---

### 4. Output Quality Review

Audit:

LONG engine quality.

Question:

```text
Would professional traders open these charts?
```

Reject weak output immediately.

---

### 5. SHORT Engine Review

Audit:

* Structural weakness quality
* Junk stocks entering short list
* Weak theme confirmation

Question:

```text
Are these genuinely weak institutional names?
```

---

### 6. Hardcoding Review

Audit:

* Stock mappings becoming stale
* Obsolete assumptions
* Theme classification drift

Output:

Exact CSV/config changes required.

---

### 7. Config Review

Review:

* Threshold values
* Weight values
* Signal degradation

Only change when evidence supports change.

---

# Monthly Review Process (Mandatory)

Frequency:

* Once per month

Maximum time:

* 30 minutes

---

## Files User Provides

1. 20–30 JSON history files

2. Current config.py

3. Recent terminal outputs

4. Current CSV mapping files

---

## Monthly Deep Audit Areas

Review:

### Scoring Engine

Challenge weights assigned to:

* RS Rating
* Theme Strength
* Zacks Rank
* Sales Growth
* Margin
* Price Position

Question:

```text
Are strongest charts still appearing?
```

---

### ETF Ranking Logic

Review:

* 1 Week weighting
* 1 Month weighting
* 3 Month weighting
* Ranking methodology

Question:

```text
Is recent market behavior being weighted correctly?
```

---

### Long Engine Quality

Question:

```text
Would Mark Minervini or Dan Zanger open these charts?
```

If NO:

Review immediately.

---

### Short Engine Quality

Question:

```text
Are weak stocks structurally weak?

Or random junk names appearing?
```

---

### Hardcoded Assumptions Audit

Review all hardcoded assumptions inside:

* config.py
* CSV files
* Classification logic

Question:

```text
Should this assumption still exist?
```

---

# Development Rules (Permanent)

Before ANY new feature:

Follow mandatory protocol.

## Phase 1

Audit architecture.

## Phase 2

Design review.

## Phase 3

Identify exact impacted files.

## Phase 4

Minimal safe implementation.

## Phase 5

Validate output using real market data.

Never code before completing design review.

---

# Hardcoding Rules

Hardcoding is allowed ONLY if assumptions are reviewable.

Move assumptions to:

* config.py
* CSV files

Never bury assumptions permanently inside engine files.

Examples:

* Theme mappings
* Threshold values
* Weight values
* Classification rules

Engine files contain logic.

Config/CSV files contain assumptions.

---

# Long Engine Rule

Long engine is production stable.

Default assumption:

DO NOT MODIFY LONG ENGINE.

Protected architecture.

Any modification must be heavily challenged first.

---

# Short Engine Rule

Short engine identifies weakness.

It is NOT true short-selling engine.

Purpose:

* Weak stocks
* Weak themes
* Poor institutional sponsorship
* Structural weakness candidates

Weakness ≠ automatic short opportunity.

Chart review always required.

---

# Decision Filter (Apply Always)

Before any feature ask:

```text
Does this improve capital flow detection?

Does available data support this idea?

Would professional traders care?

Would institutional traders care?

Would I open the chart?
```

If answer is NO:

Reject immediately.

---

# Final Principle

TABELA intelligence improves through disciplined review process.

NOT through continuous code modifications.

Best system is NOT smartest system.

Best system is system sustainable for years.

---

## My architect comment

I would save this immediately.

This document is now as important as your Python code.

Because from now onward:

```text
We stop building random features.

We follow operating discipline.
```

---

**Next after this (strict order):**

```text
1. Move hardcoded mappings from company_theme_engine.py → CSV

2. Remove other hidden hardcoding

3. Begin first weekly review cycle
```

No deviation.

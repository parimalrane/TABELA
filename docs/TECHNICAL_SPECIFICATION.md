# TECHNICAL_SPECIFICATION.md

# TABELA Technical Specification

---

# 1. Purpose

This document defines the technical responsibilities of each major engine, the data exchanged between engines, execution dependencies, and implementation requirements.

It is intended for developers maintaining or extending TABELA.

---

# 2. Processing Pipeline

The production execution sequence is:

```text
Configuration
    ↓
ETF Engine
    ↓
Theme Mapping
    ↓
Composite Engine
    ↓
Breadth Engine
    ↓
Institutional Leader
    ↓
Distribution Engine
    ↓
Structural Weakness Engine
    ↓
Rotation Engine
    ↓
Snapshot Engine
    ↓
Historical Intelligence Engine
    ↓
Report Generation
```

Each stage depends only on outputs from earlier stages.

---

# 3. Engine Specification

---

## 3.1 Configuration

### Purpose

Provide all application settings from a single location.

### Inputs

None.

### Outputs

Application configuration object.

### Responsibilities

* File locations
* Score weights
* Thresholds
* Output paths
* Feature flags

### Dependencies

None.

---

## 3.2 ETF Engine

### Purpose

Load, validate and prepare ETF data.

### Inputs

* ETF.csv

### Outputs

Normalized ETF dataset.

### Responsibilities

* Read CSV
* Validate columns
* Remove invalid rows
* Apply ETF filters
* Calculate base metrics

### Dependencies

Configuration.

### Downstream Consumers

* Theme Mapping
* Composite Engine

---

## 3.3 Theme Mapping

### Purpose

Convert ETF industries into standardized investment themes.

### Inputs

* ETF dataset
* Mapping tables

### Outputs

Theme dataset.

### Responsibilities

* Industry normalization
* Theme assignment
* Unknown classification
* Mapping validation

### Dependencies

ETF Engine.

---

## 3.4 Composite Engine

### Purpose

Calculate overall strength for every investment theme.

### Inputs

* Theme dataset

### Outputs

Theme rankings.

### Responsibilities

* Apply weighting model
* Normalize metrics
* Rank themes
* Generate composite score

### Dependencies

Theme Mapping.

---

## 3.5 Breadth Engine

### Purpose

Measure participation inside each theme.

### Inputs

* Stock universe
* Theme assignments

### Outputs

Breadth statistics.

### Responsibilities

* Count participating stocks
* Strong vs weak participation
* Breadth percentage
* Internal leadership

### Dependencies

Composite Engine.

---

## 3.6 Institutional Leader Engine

### Purpose

Identify the strongest stocks within strong themes.

### Inputs

* Stock universe
* Theme scores
* Breadth results

### Outputs

Institutional leader list.

### Responsibilities

* Rank stocks
* Remove low-quality candidates
* Produce leadership list

### Dependencies

Breadth Engine.

---

## 3.7 Distribution Engine

### Purpose

Identify deterioration before structural weakness develops.

### Inputs

* Ranked stocks

### Outputs

Distribution watchlist.

### Responsibilities

* Detect weakening leadership
* Rank distribution candidates
* Preserve supporting metrics

### Dependencies

Institutional Leader Engine.

---

## 3.8 Structural Weakness Engine

### Purpose

Identify stocks showing persistent deterioration.

### Inputs

* Stock universe
* Historical information (when available)

### Outputs

Structural weakness watchlist.

### Responsibilities

* Detect long-term weakness
* Avoid temporary pullbacks
* Rank candidates

### Dependencies

Distribution Engine.

---

## 3.9 Rotation Engine

### Purpose

Compare today's market with previous market state.

### Inputs

* Current snapshot
* Previous snapshot

### Outputs

Rotation Delta.

### Responsibilities

* Theme movement
* Rank movement
* Score movement
* Leadership changes

### Dependencies

Snapshot history.

---

## 3.10 Snapshot Engine

### Purpose

Persist today's market state.

### Inputs

Current engine outputs.

### Outputs

Snapshot JSON.

### Responsibilities

* Serialize market state
* Maintain schema consistency
* Save daily snapshot

### Dependencies

Rotation Engine.

---

## 3.11 Historical Intelligence Engine

### Purpose

Transform historical data into market intelligence.

### Inputs

* Snapshots
* Rotation Delta
* Stock history

### Outputs

Historical intelligence report.

### Responsibilities

* Multi-day analysis
* Trend persistence
* Rotation persistence
* Leadership persistence
* Historical summaries

### Dependencies

Snapshot Engine.

---

# 4. Engine Dependency Matrix

| Engine                  | Depends On           |
| ----------------------- | -------------------- |
| Configuration           | None                 |
| ETF                     | Configuration        |
| Theme Mapping           | ETF                  |
| Composite               | Theme Mapping        |
| Breadth                 | Composite            |
| Institutional Leader    | Breadth              |
| Distribution            | Institutional Leader |
| Structural Weakness     | Distribution         |
| Rotation                | Snapshot History     |
| Snapshot                | Rotation             |
| Historical Intelligence | Snapshot             |

---

# 5. Data Contracts

Every engine should expose:

### Inputs

Required data from previous stages.

### Outputs

Structured Python objects.

### Rules

* Never mutate upstream data.
* Never depend on console output.
* Never read another engine's internal variables.
* Exchange data only through defined interfaces.

---

# 6. Error Handling

Recoverable errors:

* Missing optional files
* Empty datasets
* Unknown mappings

Fatal errors:

* Missing configuration
* Missing required input files
* Invalid schema
* Corrupt historical data

---

# 7. Performance Guidelines

Expected workload:

* Hundreds of ETFs
* Thousands of stocks
* Years of historical snapshots

Guidelines:

* Single-pass processing where practical.
* Avoid repeated file reads.
* Cache reusable lookups.
* Prefer dictionaries for key-based access.
* Keep algorithms close to O(n).

---

# 8. Engine Design Rules

Each engine should:

* Have one primary responsibility.
* Produce deterministic output.
* Avoid hidden side effects.
* Be independently testable.
* Avoid business logic duplication.

---

# 9. Data Persistence Rules

Persist only structured data.

Persist:

* Scores
* Rankings
* Counts
* Identifiers
* Dates
* Relationships

Do not persist:

* Console formatting
* Report text
* ANSI colors
* Presentation layout

---

# 10. Interface Standards

Each engine should expose a single public execution method where practical.

Guidelines:

* Accept structured input.
* Return structured output.
* Avoid global state.
* Avoid direct console printing.
* Raise exceptions only for unrecoverable failures.

---

# 11. Validation Checklist

Each engine should verify:

* Required inputs exist.
* Required columns are present.
* Numeric fields are valid.
* Duplicate identifiers are handled.
* Empty datasets are processed safely.
* Outputs conform to expected schema.

---

# 12. Extension Guidelines

New engines should:

* Consume existing outputs.
* Avoid duplicating calculations.
* Minimize additional dependencies.
* Integrate into the pipeline at a single insertion point.
* Preserve backward compatibility for persisted data.

---

# 13. Stability Classification

| Component                  | Stability          |
| -------------------------- | ------------------ |
| Configuration              | Stable             |
| ETF Engine                 | Stable             |
| Theme Mapping              | Stable             |
| Composite Engine           | Stable             |
| Breadth Engine             | Stable             |
| Institutional Leader       | Stable             |
| Distribution Engine        | Active Development |
| Structural Weakness Engine | Active Development |
| Rotation Engine            | Stable             |
| Snapshot Engine            | Stable             |
| Historical Intelligence    | Active Development |
| Reports                    | Active Development |

---

# 14. Recommended Development Order

When implementing from scratch:

1. Configuration
2. Data loading
3. Theme mapping
4. Composite scoring
5. Breadth
6. Leadership
7. Distribution
8. Structural weakness
9. Snapshot persistence
10. Rotation analysis
11. Historical intelligence
12. Reporting

Each stage should be fully validated before the next is implemented.

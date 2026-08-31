# ARCHITECTURE.md

# TABELA System Architecture

---

# 1. Overview

TABELA is a modular data-processing pipeline.

Each engine performs one responsibility and passes its output to the next stage.

The architecture is intentionally linear to simplify debugging, testing, and future enhancements.

```
                ETF.csv
                   │
                   ▼
            ETF Processing
                   │
                   ▼
         Theme Classification
                   │
                   ▼
          Composite Scoring
                   │
                   ▼
          Breadth Analysis
                   │
                   ▼
         Stock Evaluation
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
      Long               Distribution
        │                     │
        └──────────┬──────────┘
                   ▼
          Rotation Analysis
                   ▼
          Snapshot Creation
                   ▼
      Historical Intelligence
                   ▼
         Console / CSV Output
```

---

# 2. Architecture Goals

* One responsibility per engine
* Minimal engine coupling
* Deterministic execution
* Historical persistence
* Easy to extend
* Easy to debug

---

# 3. Directory Structure

```text
TABELA/

│
├── runners/
│   ├── main.py
│   └── run_historical.py
│
├── pipeline/
│   └── pipeline.py
│
├── config/
│   └── config.py
│
├── themes/
│   └── company_theme_engine.py
│
├── scoring/
│   └── long_scoring_engine.py
│
├── lifecycle/
│   └── stock_transition_engine.py
│
├── data_layer/
│   └── snapshot_engine.py
│
├── reporting/
│   └── presentation_engine.py
│
├── data/
│
├── market_data/
│
└── main.bat
```

---

# 4. Layered Architecture

```
Presentation
        ▲
Historical Intelligence
        ▲
Business Engines
        ▲
Core Pipeline
        ▲
Input Data
```

---

# 5. Layer Responsibilities

## Input Layer

Responsible for loading external data.

Typical sources:

* ETF.csv
* stocks.csv
* theme mapping tables

No calculations occur here.

---

## Core Layer

Responsibilities:

* configuration
* pipeline orchestration
* shared utilities
* theme mapping
* validation

The Core layer contains no market intelligence.

---

## Engine Layer

Contains all business logic.

Every engine performs one task.

Typical responsibilities:

* ranking
* scoring
* filtering
* classification
* breadth
* historical comparison

Engines should not perform console formatting.

---

## Persistence Layer

Stores historical information.

Current storage:

```
market_data/

snapshots/

rotation_delta/

stock_universe/
```

Only structured data is stored.

---

## Presentation Layer

Produces:

* console reports
* TradingView exports
* CSV outputs

Presentation should not perform calculations.

---

# 6. Execution Pipeline

The expected execution sequence is:

```
1 Load Configuration

2 Load ETF Data

3 ETF Processing

4 Theme Mapping

5 Composite Score

6 Breadth

7 Institutional Leaders

8 Distribution

9 Rotation

10 Snapshot Save

11 Historical Intelligence

12 Report Generation
```

Execution order is significant.

Changing the order may invalidate downstream calculations.

---

# 7. Engine Dependencies

```
ETF Engine
        │
        ▼
Theme Mapping
        │
        ▼
Composite Engine
        │
        ▼
Breadth Engine
        │
        ▼
Institutional Leader
        │
        ▼
   Distribution 
        │
        ▼
               ▼
      Rotation Engine
               ▼
     Snapshot Engine
               ▼
Historical Intelligence
```

---

# 8. Data Flow

Input data flows in one direction.

```
CSV

↓

Python Objects

↓

Theme Objects

↓

Scored Objects

↓

Historical Objects

↓

Reports
```

No engine should modify upstream data.

---

# 9. Engine Responsibilities

| Engine                  | Responsibility                            |
| ----------------------- | ----------------------------------------- |
| ETF                     | Load and filter ETF universe              |
| Theme Mapping           | Convert industries to themes              |
| Composite               | Calculate theme strength                  |
| Breadth                 | Measure participation                     |
| Institutional Leader    | Identify strongest stocks                 |
| Distribution            | Detect structurally weak shorts and breakdowns|
| Rotation                | Compare current and previous market state |
| Snapshot                | Persist current market state              |
| Historical Intelligence | Multi-day trend analysis                  |

---

# 10. Historical Data Architecture

Historical information is built from three independent sources.

```
Daily Snapshot

+

Rotation Delta

+

Stock History

↓

Historical Intelligence
```

Each source has a distinct purpose and should remain independent.

---

# 11. Configuration Flow

```
config.py

↓

Pipeline

↓

Engines

↓

Reports
```

Engines should consume configuration values rather than hard-code thresholds.

---

# 12. Error Handling

Each engine should:

* validate required inputs
* handle missing files gracefully
* return empty collections rather than terminate processing where possible
* log recoverable errors
* fail fast for unrecoverable configuration issues

---

# 13. Extension Points

Preferred locations for new functionality:

* New analysis engine
* New report generator
* New exporter
* New historical metric
* New validation module

Avoid modifying stable engines unless necessary.

---

# 14. Data Ownership

| Data                 | Owner                   |
| -------------------- | ----------------------- |
| ETF universe         | ETF Engine              |
| Theme mapping        | Theme Mapper            |
| Theme scores         | Composite Engine        |
| Breadth metrics      | Breadth Engine          |
| Leader lists         | Institutional Leader    |
| Rotation data        | Rotation Engine         |
| Snapshots            | Snapshot Engine         |
| Historical summaries | Historical Intelligence |

Only the owning engine should create or update its data.

---

# 15. Design Rules

* Keep engines independent.
* Keep interfaces simple.
* Avoid circular dependencies.
* Prefer composition over shared state.
* Separate calculations from presentation.
* Persist structured facts, not formatted output.
* Preserve backward compatibility for historical JSON files whenever practical.

---

# 16. Future Expansion

The architecture supports additional engines without redesign.

Recommended insertion points:

```
Theme Mapping
        │
        ▼
[New Analysis Engine]
        │
        ▼
Composite Engine
```

or

```
Snapshot Engine
        │
        ▼
[New Historical Engine]
        │
        ▼
Historical Intelligence
```

New engines should consume existing outputs rather than duplicate calculations.

---

# 17. Rebuild Priority

If rebuilding TABELA, implement modules in this order:

1. Configuration
2. ETF Engine
3. Theme Mapping
4. Composite Engine
5. Breadth Engine
6. Institutional Leader
7. Distribution
8. Rotation
9. Snapshot
10. Historical Intelligence
11. Reporting

Each stage should be validated before proceeding to the next.

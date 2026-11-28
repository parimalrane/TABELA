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
          Watchlist Deltas (Stateless)
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
│   ├── presentation_engine.py
│   └── watchlist_delta_engine.py
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

Responsible for loading external data and reference mappings.

Typical sources:

* ETF.csv (e.g. `market_data/input_files/YYYY-MM/YYYYMMDD_ETF.csv`)
* stocks.csv (e.g. `market_data/input_files/YYYY-MM/YYYYMMDD_stocks.csv`)
* Relational theme mapping tables in `data/`:
  - `data/macro_theme_mapping.csv` (Micro/Narrative $\rightarrow$ Macro Benchmark Theme)
  - `data/theme_etf_mapping.csv` (Theme $\rightarrow$ SPDR Sector & Pure-Play ETFs)
  - `data/industry_theme_mapping.csv` (Raw Zacks Industry $\rightarrow$ Narrative Theme)
  - `data/stock_theme_mapping.csv` (Explicit ticker-level dominant narrative overrides)

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
  snapshots/           # Daily market state JSONs
  rotation_delta/      # Theme rank change JSONs
  stock_universe/      # Stock history JSONs
  watchlist_history/   # Watchlist snapshot JSONs with days-on-list tracking
  market_context/      # Market regime (Accumulation/Distribution) JSONs
  daily_reports/       # Terminal output capture (.txt)
  stock_transition/    # Stock lifecycle registry JSONs
  unknown_classification/  # Unclassified ticker audit JSONs
  dropped_list/        # dropped_history.csv (accumulating point-in-time drop audit ledger)
  reentry_tracker.json # Active re-entry timestamp and hold-window tracker
  dropped_accumulator.json # Active mild pullback & relief rally accumulator
```

Only structured data is stored.

---

## Presentation Layer

Produces:

* Console reports:
  - Macro Weather Report & Breadth X-Ray (Multi-timeframe index returns, advance/decline streaks, 52W extremes)
  - Sector Intelligence Engine Rankings (Multi-timeframe SPDR performance vs SPY)
  - Theme Breadth Analysis (Top-down macro rank, micro tier, pure-play ETFs, active stock breadth leaders)
  - Long Universe (Screened Stage 2 Institutional Leaders)
  - Short Universe (Screened Stage 4 Breakdown Candidates)
* TradingView Watchlist Exports:
  - `TRADINGVIEW WATCHLIST : BULLISH`: Filtered by Dual-Gate Structural Health (`RS >= 0%` vs SPY AND `52W Range >= 50%`) with Actionable 1:1 Pruning ($\ge 1$ stock required), generating `###leading_ETF,...` header with granular ETF stock buckets (`###XBI,...`, `###XRT,...`). Disqualifies low-range defensive assets (e.g. `VOX`) and empty secondary ETFs.
  - `TRADINGVIEW WATCHLIST : BEARISH`: Filtered by Dual-Gate Structural Health (`RS < 0%` vs SPY AND `52W Range <= 50%`) with Actionable 1:1 Pruning ($\ge 1$ stock required), generating `###lagging_ETF,...` header with granular ETF stock buckets (`###SMH,...`, `###COPX,...`). Disqualifies high-range pullbacks in bull markets (e.g. `CLOU`, `SKYY`, `IGV`) and empty secondary ETFs.
  - Neutral Zone: Assets with conflicting signals are cleanly dropped from both watchlists.
  - Dropped Watchlists: `###Dropped_Leading_ETF,...` and `###Dropped_Lagging_ETF,...`.
* File Captures & Ledgers:
  - Daily report captures in `market_data/daily_reports/YYYY-MM/YYYY-MM-DD.txt`
  - Dropped candidate audit ledger in `market_data/dropped_list/dropped_history.csv`

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
| ETF Scoring             | Calculate individual ETF RS using unified config weights |
| Theme Mapping           | Convert industries to themes (raw Zacks casing preserved) |
| Composite               | Calculate theme strength (config-driven weights) |
| Breadth                 | Measure bidirectional participation (Long strength for Leading, Short weakness for Lagging) |
| Watchlist Engine        | Identify strongest institutional long leaders meeting LONG_ENTRY |
| Distribution            | Detect structurally weak breakdown shorts meeting SHORT_ENTRY |
| Rotation                | Compare current and previous market state |
| Snapshot                | Persist current market state              |
| Historical Intelligence | Multi-day trend analysis                  |
| Stock History           | Date-aware previous-day lookup for days-on-list tracking |

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
| Theme mapping        | Theme Mapper (`data/macro_theme_mapping.csv`, `data/theme_etf_mapping.csv`) |
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

# PROJECT_OVERVIEW.md

# TABELA

**Version:** Current Development
**Language:** Python 3.12+
**Platform:** Windows (Primary), Cross-platform Python compatible

---

# 1. Purpose

TABELA is a market intelligence application that analyzes ETFs and stocks to identify institutional capital rotation.

Its primary output is a daily market assessment consisting of:

* Strongest themes
* Weakest themes
* Institutional leaders
* Distribution candidates
* Structural weakness candidates
* Historical market intelligence

TABELA is a research engine. It does not generate buy/sell recommendations.

---

# 2. Objectives

The system is designed to:

* Rank investment themes
* Measure theme breadth
* Detect institutional leadership
* Track capital rotation over time
* Preserve historical market state
* Produce consistent daily reports

---

# 3. Input Files

Daily execution requires:

```
data/
    ETF.csv
    stocks.csv
```

Supporting reference data:

```
data/
    industry_theme_mapping.csv
    stock_theme_mapping.csv
```

---

# 4. Primary Outputs

Typical outputs include:

* Market report
* Theme rankings
* Breadth analysis
* Institutional leader list
* Distribution watchlist
* Structural weakness watchlist
* TradingView watchlists
* Historical intelligence report

Persistent data:

```
market_data/
    snapshots/
    stock_universe/
    rotation_delta/
```

---

# 5. High-Level Workflow

```
ETF Data
        │
        ▼
Theme Classification
        │
        ▼
Theme Scoring
        │
        ▼
Breadth Analysis
        │
        ▼
Stock Classification
        │
        ▼
Rotation Analysis
        │
        ▼
Historical Intelligence
        │
        ▼
Daily Reports
```

---

# 6. Major Components

| Component   | Responsibility                         |
| ----------- | -------------------------------------- |
| Core        | Pipeline, configuration, theme mapping |
| Engines     | Business logic                         |
| Data        | Static mapping files                   |
| Market Data | Historical JSON storage                |
| Reports     | Console and exported outputs           |

---

# 7. Core Processing Stages

1. Load configuration
2. Read ETF universe
3. Filter ETFs
4. Translate industries into themes
5. Calculate theme scores
6. Analyze breadth
7. Score stocks
8. Build long candidates
9. Build distribution candidates
10. Build structural weakness candidates
11. Detect market rotation
12. Save snapshot
13. Update historical intelligence
14. Generate reports

---

# 8. Directory Layout

```
core/
    Pipeline
    Configuration
    Theme Mapping

engines/
    Business Logic

data/
    Static Mapping Tables

market_data/
    Historical Data

main.py
```

---

# 9. Key Concepts

| Term                    | Description                                              |
| ----------------------- | -------------------------------------------------------- |
| Theme                   | Investment narrative shared by multiple stocks           |
| Breadth                 | Participation level within a theme                       |
| Composite Score         | Overall strength score for a theme                       |
| Institutional Leader    | Highest-quality stock within a strong theme              |
| Distribution            | Early signs of institutional selling                     |
| Structural Weakness     | Persistent deterioration rather than short-term weakness |
| Snapshot                | Daily market state stored as JSON                        |
| Rotation Delta          | Day-over-day change between snapshots                    |
| Historical Intelligence | Multi-day analysis generated from stored history         |

---

# 10. Design Principles

* Modular engine architecture
* Deterministic processing
* Configuration-driven behavior
* Daily historical persistence
* Clear separation between calculation and presentation
* JSON used as the historical data store

---

# 11. Intended Users

* Swing traders
* Position traders
* Market researchers
* Quantitative analysts
* Developers maintaining the project

---

# 12. Project Status

Current implementation includes:

* ETF analysis
* Theme classification
* Composite scoring
* Breadth analysis
* Institutional leader identification
* Distribution analysis
* Structural weakness analysis
* Historical snapshot storage
* Rotation analysis
* Historical intelligence generation

Future enhancements are documented separately in `ROADMAP.md`.

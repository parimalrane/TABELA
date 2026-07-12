# DATA_MODEL.md

# TABELA Data Model

---

# 1. Purpose

This document defines the persistent data structures used throughout TABELA.

It documents:

* Input files
* Internal data objects
* Historical storage
* Relationships
* Ownership

Business logic is documented elsewhere.

---

# 2. Data Flow

```text
ETF.csv
            \
             \
              -> Theme Mapping
             /
stocks.csv  /

↓

Theme Scores

↓

Breadth

↓

Stock Rankings

↓

Watchlists

↓

Market Snapshot

↓

Rotation Delta

↓

Historical Intelligence
```

---

# 3. Input Data

## 3.1 ETF.csv

Owner

ETF Engine

Purpose

Daily ETF universe.

Typical Fields

| Field               | Description             |
| ------------------- | ----------------------- |
| Symbol              | ETF ticker              |
| Name                | ETF name                |
| Category            | ETF category            |
| Industry            | Industry classification |
| AUM                 | Assets under management |
| Price               | Latest price            |
| Volume              | Trading volume          |
| Performance metrics | Time-based returns      |

Required

Yes

Updated

Daily

---

## 3.2 stocks.csv

Owner

Stock Processing

Purpose

Daily stock universe.

Typical Fields

| Field             | Description      |
| ----------------- | ---------------- |
| Symbol            | Stock ticker     |
| Company           | Company name     |
| Sector            | Market sector    |
| Industry          | Industry         |
| Price             | Latest price     |
| Volume            | Trading volume   |
| Relative Strength | Ranking metric   |
| Technical metrics | Screening values |

Required

Yes

Updated

Daily

---

# 4. Reference Data

Reference files are relatively static.

Examples

```text
industry_theme_mapping.csv

stock_theme_mapping.csv

configuration files
```

Purpose

* Standardization
* Theme assignment
* Classification

---

# 5. Internal Objects

## Theme Object

Represents one investment theme.

Typical attributes

```text
Theme

Composite Score

Rank

ETF Count

Breadth %

Strong Stocks

Weak Stocks

Leader Count
```

Produced by

Composite Engine

Consumed by

All downstream engines.

---

## Stock Object

Represents one stock after processing.

Typical attributes

```text
Ticker

Theme

Composite Score

Relative Strength

Leadership Status

Distribution Status

Structural Weakness Status
```

Produced by

Stock processing engines.

---

# 6. Watchlists

## Institutional Leaders

Purpose

Highest-quality candidates.

Owner

Institutional Leader Engine.

---

## Distribution Watchlist

Purpose

Potential deterioration.

Owner

Distribution Engine.

---

## Structural Weakness Watchlist

Purpose

Persistent weakness.

Owner

Structural Weakness Engine.

---

# 7. Persistent Storage

Historical information is stored under

```text
market_data/
```

Subdirectories

```text
snapshots/

rotation_delta/

stock_universe/
```

---

# 8. Snapshot

Purpose

Represents complete market state for one trading day.

One file per day.

Naming

```text
YYYY-MM-DD_market_snapshot.json
```

Contains

* Date
* Theme rankings
* Breadth
* Leaders
* Watchlists
* Scores

Snapshot is the primary historical record.

---

# 9. Rotation Delta

Purpose

Difference between two snapshots.

Naming

```text
YYYY-MM-DD_rotation_delta.json
```

Contains

* Rank changes
* Score changes
* Theme movement
* Leadership changes

Rotation Delta is derived.

It is not the source of truth.

---

# 10. Stock History

Purpose

Historical record of stock-level information.

Naming

```text
YYYY-MM-DD_stock_history.json
```

Contains

* Rankings
* Theme assignments
* Scores
* Status changes

---

# 11. Historical Intelligence

Generated from

```text
Snapshots

+

Rotation Delta

+

Stock History
```

Produces

Historical reports.

Historical reports are regenerated.

They are not treated as source data.

---

# 12. Relationships

```text
ETF

↓

Theme

↓

Stocks

↓

Watchlists

↓

Snapshot

↓

Rotation Delta

↓

Historical Intelligence
```

---

# 13. Ownership Matrix

| Data                    | Owner                          |
| ----------------------- | ------------------------------ |
| ETF.csv                 | ETF Engine                     |
| stocks.csv              | Stock Processing               |
| Theme Mapping           | Theme Mapper                   |
| Theme Scores            | Composite Engine               |
| Breadth                 | Breadth Engine                 |
| Institutional Leaders   | Institutional Leader Engine    |
| Distribution            | Distribution Engine            |
| Structural Weakness     | Structural Weakness Engine     |
| Snapshot                | Snapshot Engine                |
| Rotation Delta          | Rotation Engine                |
| Historical Intelligence | Historical Intelligence Engine |

Only the owning engine should create or update its data.

---

# 14. Naming Standards

CSV

```text
ETF.csv

stocks.csv
```

Snapshots

```text
YYYY-MM-DD_market_snapshot.json
```

Rotation

```text
YYYY-MM-DD_rotation_delta.json
```

Stock History

```text
YYYY-MM-DD_stock_history.json
```

Use ISO-8601 dates throughout the project.

---

# 15. Persistence Rules

Persist:

* Identifiers
* Rankings
* Scores
* Counts
* Dates
* Relationships
* Status flags

Do not persist:

* Console formatting
* ANSI colors
* Generated narratives
* Report layout
* Debug information

---

# 16. Schema Evolution

When extending a persisted schema:

* Prefer additive changes.
* Avoid renaming existing fields.
* Preserve backward compatibility.
* Default missing fields during loading.
* Version migrations only when unavoidable.

---

# 17. Data Validation

Every persisted dataset should satisfy:

* Required fields present
* Valid identifiers
* No duplicate primary keys
* Numeric values validated
* Dates in ISO format
* Consistent theme names
* Valid JSON encoding

---

# 18. Storage Principles

* One responsibility per file.
* One snapshot per trading day.
* Immutable historical records.
* Structured data only.
* Reports are generated from persisted data, never treated as authoritative storage.

---

# 19. Data Lifecycle

```text
Input CSV

↓

Validation

↓

Normalization

↓

Processing

↓

Ranking

↓

Classification

↓

Persistence

↓

Historical Analysis

↓

Reporting
```

---

# 20. Future Data Extensions

Recommended additions should remain independent of existing schemas.

Examples

* Theme history
* Breadth history
* Sector history
* Leadership history
* Contribution analysis

New datasets should reference existing identifiers instead of duplicating information.

# REBUILD_GUIDE.md

# Rebuilding TABELA From Scratch

---

# 1. Objective

This guide describes the recommended implementation order for rebuilding TABELA.

The goal is to produce a working system incrementally while minimizing rework.

Each phase should compile, execute, and pass validation before moving to the next phase.

---

# 2. Technology Stack

| Component          | Technology        |
| ------------------ | ----------------- |
| Language           | Python 3.12+      |
| Data Storage       | CSV, JSON         |
| Package Management | pip               |
| Primary Libraries  | pandas, numpy     |
| Platform           | Windows (Primary) |

---

# 3. Recommended Repository Structure

```text
TABELA/

main.py

core/
engines/
data/
market_data/
reports/
tests/
docs/
```

Do not create additional top-level folders unless required.

---

# 4. Phase 1 — Project Skeleton

Create:

```text
main.py

core/
engines/
data/
market_data/
reports/
docs/
tests/
```

Validation

* Project starts.
* Configuration loads.
* Folder structure is created automatically if missing.

---

# 5. Phase 2 — Configuration

Implement:

* config.py
* path management
* constants
* thresholds
* scoring weights

Validation

* Configuration loads successfully.
* No hard-coded paths remain.

---

# 6. Phase 3 — Data Loading

Implement loaders for:

* ETF.csv
* stocks.csv

Requirements

* CSV validation
* Missing column detection
* Type conversion
* Duplicate detection

Validation

* Both datasets load successfully.

---

# 7. Phase 4 — Theme Mapping

Implement:

* Industry normalization
* Theme assignment
* Unknown classification

Outputs

Theme assigned to every ETF.

Validation

* Every ETF has a valid theme.

---

# 8. Phase 5 — Composite Engine

Implement

* Score calculation
* Ranking
* Normalization

Outputs

Theme rankings.

Validation

* Rankings remain deterministic.

---

# 9. Phase 6 — Breadth Engine

Implement

* Theme participation
* Strong stock count
* Weak stock count
* Breadth percentage

Validation

* Breadth values are internally consistent.

---

# 10. Phase 7 — Institutional Leader Engine

Implement

* Stock ranking
* Leader selection
* Theme leader identification

Validation

* Every strong theme has candidate leaders.

---

# 11. Phase 8 — Distribution Engine

Implement

Distribution detection.

Outputs

Distribution watchlist.

Validation

* Stocks appear only once.
* Rankings are deterministic.

---

# 12. Phase 9 — Structural Weakness Engine

Implement

Persistent weakness detection.

Outputs

Structural weakness watchlist.

Validation

* Temporary weakness is filtered.
* Rankings remain stable.

---

# 13. Phase 10 — Snapshot Engine

Implement

Daily persistence.

Create

```text
market_snapshot.json
```

Requirements

* One snapshot per trading day.
* ISO-8601 dates.
* Stable schema.

Validation

Snapshots reload correctly.

---

# 14. Phase 11 — Rotation Engine

Implement

Snapshot comparison.

Outputs

Rotation Delta.

Validation

* Detect added themes.
* Detect removed themes.
* Detect rank changes.
* Detect score changes.

---

# 15. Phase 12 — Historical Intelligence

Implement

Historical analysis from:

* Snapshots
* Rotation Delta
* Stock history

Outputs

Historical report.

Validation

Historical summaries match source data.

---

# 16. Phase 13 — Reporting

Generate

* Theme rankings
* Breadth
* Leaders
* Distribution
* Structural weakness
* Historical intelligence

Presentation should consume processed data only.

---

# 17. Phase 14 — Export

Implement

* TradingView watchlists
* CSV exports

Validation

Files open without modification.

---

# 18. Phase 15 — Testing

Minimum tests

Configuration

Data loading

Theme mapping

Composite scoring

Breadth

Snapshot creation

Rotation

Historical intelligence

Pipeline execution

---

# 19. Validation Gates

A phase is complete only if:

* Builds successfully.
* Executes successfully.
* Produces deterministic output.
* Passes regression tests.
* Documentation updated.

---

# 20. Dependency Order

```text
Configuration

↓

CSV Loading

↓

Theme Mapping

↓

Composite

↓

Breadth

↓

Institutional Leaders

↓

Distribution

↓

Structural Weakness

↓

Snapshot

↓

Rotation

↓

Historical Intelligence

↓

Reporting

↓

Exports
```

No phase should skip dependencies.

---

# 21. Rebuild Priorities

Priority 1

Core pipeline

Priority 2

Historical persistence

Priority 3

Market intelligence

Priority 4

Reporting

Priority 5

Additional analytics

---

# 22. Acceptance Criteria

A rebuilt TABELA is considered complete when it can:

✓ Load daily ETF data

✓ Load daily stock data

✓ Produce theme rankings

✓ Measure breadth

✓ Identify institutional leaders

✓ Generate distribution watchlists

✓ Generate structural weakness watchlists

✓ Save daily snapshots

✓ Calculate rotation

✓ Generate historical intelligence

✓ Produce daily reports

without manual intervention.

---

# 23. Common Mistakes

Avoid:

* Mixing presentation with calculations.
* Hard-coded file paths.
* Circular engine dependencies.
* Duplicate scoring logic.
* Persisting formatted reports.
* Breaking historical schema compatibility.
* Reading the same CSV multiple times in a single execution.

---

# 24. Future Enhancements

After the core rebuild is complete, additional engines can be added without changing the existing architecture.

Recommended additions should consume existing outputs rather than modify core processing stages.

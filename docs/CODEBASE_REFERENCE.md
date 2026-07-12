# CODEBASE_REFERENCE.md

# Purpose

This document provides a directory-level reference for the TABELA source code.

It complements the technical specification by documenting where functionality is implemented.

---

# Entry Point

## main.py

Responsibilities

- Application entry point
- Initializes execution
- Starts pipeline

---

# Core

## core/

Contains application infrastructure.

Typical responsibilities

- Configuration
- Pipeline orchestration
- Theme mapping
- Shared utilities

---

## pipeline.py

Responsibilities

- Execute processing stages
- Control execution order
- Pass data between engines

---

## config.py

Responsibilities

- Configuration
- File paths
- Thresholds
- Weights

---

# Engines

## etf_engine.py

Purpose

ETF processing.

Produces

Normalized ETF dataset.

---

## composite_engine.py

Purpose

Theme scoring.

Produces

Theme rankings.

---

## breadth_engine.py

Purpose

Theme participation analysis.

Produces

Breadth metrics.

---

## institutional_leader.py

Purpose

Institutional leader selection.

Produces

Leader watchlist.

---

## distribution_engine.py

Purpose

Distribution analysis.

Produces

Distribution watchlist.

---

## short_engine.py

Purpose

Structural weakness analysis.

Produces

Structural weakness watchlist.

---

## rotation_engine.py

Purpose

Market rotation detection.

Produces

Rotation Delta.

---

## snapshot_engine.py

Purpose

Daily persistence.

Produces

Market snapshot JSON.

---

## historical_intelligence_engine.py

Purpose

Historical analysis.

Produces

Historical intelligence report.

---

# Data

## data/

Static reference data.

Contains

- ETF.csv
- stocks.csv
- Mapping tables

---

# Historical Storage

## market_data/

Contains

- snapshots
- rotation_delta
- stock_universe

---

# Reports

Contains exported reports and watchlists.

---

# Documentation

All project documentation is maintained in

```
docs/
```

---

# Maintenance Notes

When adding a new engine:

1. Add the engine.
2. Integrate with the pipeline.
3. Update TECHNICAL_SPECIFICATION.md.
4. Update ARCHITECTURE.md.
5. Update DATA_MODEL.md if persistence changes.
6. Update this document.
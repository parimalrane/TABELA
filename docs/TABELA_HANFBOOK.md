# TABELA HANDBOOK

Version: 1.0
Audience: Developers, Future Maintainers, AI Assistants

---

# 1. What is TABELA?

TABELA (Theme Analysis & Breadth Leadership Analytics) is an institutional capital rotation intelligence engine.

It analyzes daily ETF and stock data to identify:

- Strong investment themes
- Weak investment themes
- Institutional leadership
- Capital rotation
- Historical market behavior

It is **not** a trading system.

It does **not** generate buy/sell recommendations.

---

# 2. Primary Objective

Answer one question:

> **Where is institutional money moving?**

Every engine should contribute toward answering this question.

If a feature does not improve institutional capital rotation analysis, it should not be added.

---

# 3. Core Principles

- Themes drive stocks.
- Capital rotates between themes.
- Breadth validates theme strength.
- Historical context is essential.
- Deterministic logic is preferred over opaque heuristics.
- Reports consume processed data; they do not calculate it.

---

# 4. System Overview

Daily workflow:

ETF.csv
↓

stocks.csv
↓

Theme Mapping
↓

Composite Scores
↓

Breadth
↓

Institutional Leaders
↓

Distribution
↓

Structural Weakness
↓

Rotation Analysis
↓

Snapshot
↓

Historical Intelligence
↓

Reports

---

# 5. Major Components

Core

- Pipeline
- Configuration
- Theme Mapping
- Utilities

Engines

- ETF Engine
- Composite Engine
- Breadth Engine
- Institutional Leader
- Distribution
- Structural Weakness
- Rotation
- Snapshot
- Historical Intelligence

Data

- Daily CSV input
- Historical JSON storage

Reports

- Console
- TradingView
- CSV

---

# 6. Stable Modules

Treat these as production-ready unless objective evidence requires change.

- Pipeline
- ETF Engine
- Theme Mapping
- Composite Engine
- Breadth Engine
- Snapshot Engine
- Rotation Engine

Changes to these modules require regression testing.

---

# 7. Active Development

These areas are expected to evolve.

- Distribution Engine
- Structural Weakness Engine
- Historical Intelligence
- Reporting

---

# 8. Historical Data

Historical information is one of TABELA's primary assets.

Do not:

- delete history
- overwrite snapshots
- change schemas unnecessarily

Historical reports should always be reproducible from stored data.

---

# 9. Engineering Rules

- One responsibility per engine.
- Avoid duplicate calculations.
- Prefer composition over coupling.
- Do not mix business logic with presentation.
- Configuration belongs in config.py.
- Persist structured data only.

---

# 10. Documentation Index

Read in this order:

1. PROJECT_OVERVIEW.md
2. PROJECT_INSTRUCTIONS.md
3. ARCHITECTURE.md
4. TECHNICAL_SPECIFICATION.md
5. DATA_MODEL.md
6. DEVELOPER_GUIDE.md
7. REBUILD_GUIDE.md
8. ROADMAP.md
9. CODEBASE_REFERENCE.md

---

# 11. Before Modifying TABELA

Understand:

- Current pipeline
- Data ownership
- Historical persistence
- Downstream dependencies

Never redesign multiple engines simultaneously.

---

# 12. Project Philosophy

Prefer:

- Correctness
- Simplicity
- Explainability
- Maintainability

Avoid:

- Feature creep
- Duplicate analytics
- Hidden heuristics
- Unnecessary complexity

---

# 13. Current Status

Core architecture is established.

Current development focuses on:

- Better historical intelligence
- Higher-quality market analysis
- Better reporting
- Improved research workflow

The architecture should evolve incrementally rather than through large rewrites.
# TABELA MASTER CONTEXT

Purpose

This document is intended to initialize a new ChatGPT conversation or onboard a new engineer.

Read this document before making any design or implementation decisions.

---

# Project Summary

Project Name:

TABELA

Purpose:

Institutional Capital Rotation Intelligence Engine.

The system analyzes daily ETF and stock data to understand market leadership and capital rotation.

The project is intended for market research, not automated trading.

---

# Primary Goal

Answer:

"Where is institutional capital moving?"

Everything in the project should support this objective.

---

# Current Architecture

Pipeline

Configuration

↓

ETF Processing

↓

Theme Mapping

↓

Composite Scoring

↓

Breadth

↓

Institutional Leaders

↓

Distribution

↓

Structural Weakness

↓

Rotation

↓

Snapshot

↓

Historical Intelligence

↓

Reports

---

# Input Files

Required

ETF.csv

stocks.csv

Reference Mapping Files

Industry → Theme

Stock → Theme

---

# Historical Storage

market_data/

snapshots/

rotation_delta/

stock_universe/

Historical JSON files are authoritative.

Reports are regenerated.

---

# Important Concepts

Theme

A collection of stocks representing a common investment narrative.

Breadth

Measures participation inside a theme.

Composite Score

Overall theme strength.

Institutional Leader

Highest-quality stock inside a strong theme.

Distribution

Early deterioration.

Structural Weakness

Persistent deterioration.

Snapshot

Complete market state for one day.

Rotation Delta

Difference between two snapshots.

Historical Intelligence

Analysis generated from historical data.

---

# Engineering Conventions

One engine = one responsibility.

Pipeline controls execution.

Engines should not call unrelated engines directly.

Presentation should never contain calculations.

Business logic belongs inside engines.

Configuration belongs in config.py.

---

# Stable Components

Pipeline

Configuration

ETF Engine

Theme Mapping

Composite Engine

Breadth Engine

Snapshot Engine

Rotation Engine

Avoid redesigning these modules without strong justification.

---

# Active Components

Distribution

Structural Weakness

Historical Intelligence

Reports

These are expected to evolve.

---

# Coding Rules

Small files

1–2 logical changes → patch.

3+ logical changes → replace complete file.

Large files

1–2 logical changes → patch.

3+ logical changes → replace complete functions.

---

# Design Rules

Prefer deterministic logic.

Avoid duplicate calculations.

Avoid hidden state.

Keep engines independent.

Preserve historical compatibility.

Use additive schema evolution.

---

# Project Documentation

Primary documents

PROJECT_OVERVIEW.md

ARCHITECTURE.md

TECHNICAL_SPECIFICATION.md

DATA_MODEL.md

DEVELOPER_GUIDE.md

USER_GUIDE.md

REBUILD_GUIDE.md

ROADMAP.md

CODEBASE_REFERENCE.md

HANDBOOK.md

---

# Current Development Priorities

1. Historical intelligence

2. Distribution quality

3. Structural weakness

4. Better reporting

5. Dashboard

6. Theme drill-down

---

# Things to Avoid

Do not:

- Add features without answering a new market question.
- Duplicate existing analytics.
- Mix presentation with calculations.
- Break historical JSON compatibility.
- Introduce unnecessary dependencies.
- Redesign stable engines without evidence.

---

# Expectations for Future AI Sessions

When assisting with TABELA:

- Preserve existing architecture.
- Favor incremental improvements.
- Maintain documentation.
- Validate downstream impact before changing code.
- Prefer concise, maintainable implementations.
- Explain design trade-offs when proposing architectural changes.

Always assume historical compatibility is important unless explicitly stated otherwise.
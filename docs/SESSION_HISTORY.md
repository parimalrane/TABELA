# SESSION_HISTORY.md

Version: 1.0

Purpose

This document captures the major architectural milestones, design decisions, lessons learned, and project evolution that occurred during TABELA development.

It is not intended to document code.

It explains how the project evolved and why important decisions were made.

---

# Project Timeline

## Phase 1 — Initial Concept

Project Name

ThemePulse

Objective

Rank ETFs and identify strong investment themes.

Characteristics

- ETF-centric
- Basic scoring
- Limited historical analysis
- Primarily a daily ranking engine

Lessons

ETF rankings alone were insufficient to understand institutional capital movement.

---

## Phase 2 — Theme Intelligence

Major Changes

- Introduced Theme Classification
- Industry → Theme mapping
- Composite theme scoring
- Standardized theme naming

Result

Themes became the primary analysis unit instead of ETFs.

---

## Phase 3 — Breadth Analysis

Problem

A strong ETF did not necessarily indicate a strong theme.

Solution

Develop Breadth Engine.

Added

- Strong stock count
- Weak stock count
- Breadth %
- Internal participation

Lesson

Breadth validates theme quality.

Strong themes require broad participation.

---

## Phase 4 — Institutional Leaders

Problem

Strong themes still contained weak companies.

Solution

Create Institutional Leader Engine.

Objective

Identify highest-quality companies inside strong themes.

Lesson

Theme quality and stock quality are separate measurements.

---

## Phase 5 — Distribution & Structural Weakness

Problem

Not every declining stock should be shorted.

Solution

Separate deterioration into two categories.

Distribution

Early warning.

Structural Weakness

Persistent deterioration.

Lesson

Avoid shorting temporary weakness.

---

## Phase 6 — Historical Intelligence

Major Milestone

The project evolved from a daily scanner into a historical intelligence engine.

New Capability

Instead of asking

"What happened today?"

TABELA began answering

"What has been changing over time?"

This fundamentally changed the project.

---

## Phase 7 — Snapshot Architecture

Decision

Store complete daily market state.

Reason

Historical reports should be reproducible.

Snapshot became the primary source of truth.

Lesson

Never generate historical analysis from console output.

---

## Phase 8 — Rotation Delta

Initial Idea

Store only changes.

Problem

Changes alone cannot reconstruct history.

Decision

Snapshots remain authoritative.

Rotation Delta becomes diagnostic.

Lesson

Derived information should never replace source data.

---

## Phase 9 — Historical Intelligence Redesign

Several iterations improved:

- Rotation summaries
- Historical summaries
- Leadership persistence
- Multi-day analysis

Goal

Reduce noise.

Increase actionable market intelligence.

---

## Phase 10 — ThemePulse → TABELA

Reason

The project had evolved far beyond simple theme tracking.

New identity reflected:

- institutional capital
- breadth
- leadership
- historical intelligence
- market structure

---

# Major Architectural Decisions

## One Engine = One Responsibility

Reason

Simplifies testing.

Simplifies maintenance.

Reduces coupling.

---

## Pipeline Architecture

Decision

Linear execution.

Reason

Deterministic.

Easy debugging.

Predictable dependencies.

---

## JSON Persistence

Decision

Store structured facts.

Do not store presentation.

Reason

Reports should always be reproducible.

---

## Historical Data

Decision

Never overwrite history.

Reason

Historical knowledge compounds.

It is one of TABELA's competitive advantages.

---

## Configuration

Decision

Centralize thresholds.

Reason

Avoid hard-coded logic.

---

# Ideas That Were Rejected

Database backend

Reason

JSON is sufficient for current scale.

---

Real-time streaming

Reason

Daily analysis is the project objective.

---

Machine Learning

Reason

Insufficient historical data.

Premature complexity.

---

Automatic trade execution

Reason

Outside project scope.

---

Prediction engine

Reason

TABELA measures capital flow.

It does not predict markets.

---

Buy/Sell recommendations

Reason

User performs discretionary technical analysis.

---

# Important Lessons

Breadth matters.

Theme rankings alone are insufficient.

---

Historical context is essential.

Single-day analysis is often misleading.

---

Deterministic logic is easier to trust than opaque heuristics.

---

Reports should consume processed data.

They should not perform calculations.

---

Historical JSON files are assets.

Treat them as production data.

---

Pipeline order matters.

Changing execution order can invalidate downstream engines.

---

Avoid feature creep.

Every new engine should answer a market question that TABELA cannot already answer.

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

These should change only with strong evidence.

---

# Components Under Active Development

Historical Intelligence

Distribution

Structural Weakness

Reporting

These areas are expected to improve over time.

---

# Development Philosophy

Prefer

- Simplicity
- Deterministic logic
- Small focused engines
- Structured persistence
- Incremental improvements

Avoid

- Large rewrites
- Hidden heuristics
- Duplicate analytics
- Unnecessary dependencies
- Breaking historical compatibility

---

# Long-Term Vision

TABELA should become a comprehensive institutional capital rotation intelligence platform.

Future enhancements should build upon the existing architecture rather than replace it.

Historical knowledge should continue compounding with each trading day.

---

# If Rebuilding TABELA

Read these documents in order:

1. TABELA_MASTER_CONTEXT.md
2. TABELA_HANDBOOK.md
3. PROJECT_OVERVIEW.md
4. ARCHITECTURE.md
5. TECHNICAL_SPECIFICATION.md
6. DATA_MODEL.md
7. DEVELOPER_GUIDE.md
8. REBUILD_GUIDE.md
9. ROADMAP.md
10. CODEBASE_REFERENCE.md

Then review this SESSION_HISTORY.md before making architectural decisions.

Understanding *why* previous decisions were made is as important as understanding *how* the current system works.

---

# Final Note

The architecture will evolve.

The objective should not.

Every change should improve TABELA's ability to answer one question:

**"Where is institutional capital moving?"**
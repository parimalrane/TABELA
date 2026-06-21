# VERSION 2.3

Date: 2026-06-21

Major Architecture Discovery

TABELA long side and short side should NOT use symmetrical logic.

Critical discovery:

Institutional accumulation behavior and institutional distribution behavior are fundamentally different market processes.

Previous architecture assumption:

Strong stock detection and weak stock detection are mirror images.

This assumption proved incorrect.

---

## Major Changes Implemented

### 1. Stock History Engine Added

New automated historical database.

Stores daily stock universe.

Overwrites same day.

Purpose:

Long term intelligence research.

Stored fields:

* Ticker
* Last Close
* Avg Volume
* 52 Week High
* 52 Week Low
* Price Position in 52 Week Range
* Theme
* Theme Class
* RS Rating
* Composite Score
* Sales Score
* Zacks Score

---

### 2. Weakness Score Engine Added

New field added:

Weakness Score

Formula:

Weakness Score = 100 - Percentile

Purpose:

Provide weakness ranking granularity for short side.

Reason:

Existing RS system compressed weak stocks into identical buckets.

Example previous issue:

Bottom 40 percent stocks all assigned RS = 40

This prevented proper short ranking.

---

### 3. Short Engine Architecture Redesigned

Old logic:

Weak theme + weak stock + weak fundamentals

Problem:

Favored structurally weak companies.

Generated low quality short candidates.

---

New logic:

Short candidates selected using:

* Weakness Score
* Weakening or Lagging themes
* Composite score filter

Result:

Improved short ranking quality.

---

### 4. Architecture Philosophy Updated

Old philosophy:

Institutional Capital Rotation Engine

New philosophy:

Institutional Market Intelligence Engine

---

### 5. Critical Long Term Discovery

Long side measures:

Institutional accumulation.

Short side measures:

Institutional distribution.

These are fundamentally different.

Future architecture must treat them independently.

---

## Future Architectural Direction

Short side future development:

* Internal Rotation Shorts
* Distribution Engine
* Former Leader Breakdown Engine

Long term research direction:

Learn behavior patterns before future leaders emerge.

---

## Current Architecture Score

ETF Engine: 9.5

Theme Classification: 7.5

RS Engine: 9.0

Composite Engine: 9.0

Long Engine: 9.5

Short Engine: 8.0

Historical Logging: 10.0

Overall Architecture:

9.1 / 10

---

## Project Status

TABELA V2.3 Stable

Observation Phase Active

Historical Intelligence Layer Started

No major architecture redesign recommended immediately.

Next action:

Observe live market behavior for 5–10 sessions.

No immediate coding recommended.

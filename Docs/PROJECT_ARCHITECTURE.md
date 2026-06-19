# THEMEPULSE VERSION HISTORY & FUTURE ROADMAP

==================================================
VERSION HISTORY
===============

## VERSION 1.0 (INITIAL ARCHITECTURE)

Original architecture.

Design:

* Manually curated ETF universe
* Small ETF.csv dataset (~20 major themes)
* Theme ranking engine
* Stock classification engine
* Composite scoring engine
* Long candidate engine
* Short candidate engine

Limitations discovered:

* ETF universe too narrow
* New market narratives missed
* Sector coverage incomplete
* Heavy dependence on manual taxonomy updates

Examples missed:

* Telecom
* Consumer Staples
* Restaurants
* Retail
* REITs
* Digital Assets Infrastructure

Status:

Deprecated architecture.

---

## VERSION 2.0 (TAXONOMY EXPANSION PHASE)

Major improvements.

Changes:

Expanded manual stock classification system.

Updated:

* company_theme_engine.py
* stock_mapper.py
* theme_hierarchy.py

Major fixes:

Resolved high priority classification errors.

Examples fixed:

* SNDK → Memory
* SIMO → Memory
* COHR → Optical Networking
* VIAV → Optical Networking
* RIOT → Digital Assets Infrastructure
* BTDR → Digital Assets Infrastructure
* GLW → Optical Infrastructure
* ONTO → Semiconductor Equipment

Improvements:

* Better long watchlist quality
* Better company narrative detection

Status:

Partially active architecture.

---

## VERSION 3.0 (ETF UNIVERSE EXPANSION ARCHITECTURE)

Major architectural pivot.

Most important architecture upgrade in project history.

Design change:

Old approach:

Manually curated ETF universe.

New approach:

Full ETF universe export from Zacks.

New workflow:

Export ALL ETFs from Zacks.

Approximate ETF universe:

5000+ ETFs

Architecture change:

ETF.csv (5000+ ETFs)

↓

ETF Filter Engine

↓

Theme Rotation Engine

↓

Stock Classification Engine

↓

Long / Short Candidate Engine

New file created:

* etf_filter.py

Benefits:

* System automatically adapts to new market narratives
* No manual ETF selection required
* Theme discovery becomes dynamic
* Market structure coverage expands dramatically

Examples of newly detected themes:

* Telecom
* Networking
* Steel
* Clean Tech
* Automobiles
* Community Banks
* Healthcare
* Infrastructure
* Transportation

Status:

Current production architecture.

---

## VERSION 3.1 (ETF FILTER ENGINE REFINEMENT)

Major filtering improvements.

Problem discovered:

5000+ ETF universe introduced large amount of ETF noise.

Examples:

* Alpha ETFs
* Beta ETFs
* Country ETFs
* Bond ETFs
* Dividend ETFs
* Inverse ETFs
* Leveraged ETFs
* Strategy wrapper ETFs

New ETF filtering architecture implemented.

Automatic exclusions:

* Bonds
* Treasury ETFs
* Country ETFs
* Factor ETFs
* Income ETFs
* Inverse ETFs
* Leveraged ETFs
* Asset allocation ETFs
* Strategy wrapper ETFs

Filtering results:

Raw ETF universe:

~5192 ETFs

Filtered ETF universe:

~2500 ETFs

Benefits:

Institutional capital flow detection improved substantially.

Status:

Stable.

==================================================
CURRENT PRODUCTION VERSION
==========================

Current version:

ThemePulse Version 3.1

Architecture status:

Stable production architecture.

Estimated completion:

90%

==================================================
CURRENT SYSTEM STABILITY STATUS
===============================

Stable components:

ETF Architecture → Stable

ETF Filter Engine → Stable

Theme Rotation Engine → Stable

Long Candidate Engine → Stable

Composite Scoring Engine → Stable

Needs improvement:

Stock taxonomy coverage → Partial

Rotation historical intelligence → Missing

Historical logging → Missing

==================================================
FUTURE ROADMAP (REVISED)
========================

Priority order re-evaluated.

Only high-value enhancements remain.

---

P0 — LONG ENGINE VALIDATION (HIGHEST PRIORITY)

Reason:

ETF architecture changed significantly.

Old system:

20 ETF themes

New system:

2500+ filtered ETFs

Need validation:

Are highest ranked long candidates truly strongest market leaders?

Audit required.

Test against known leaders.

Examples:

* NVDA
* AVGO
* CRDO
* ALAB
* PLTR
* GOOG
* META
* ARM
* MU
* AMD
* TSM

Questions:

* Are top 40 longs correct?
* Are strongest leaders missing?
* Does theme scoring have excessive influence?

Purpose:

Validate long engine after ETF architecture upgrade.

Status:

Next highest priority.

---

P1 — HISTORICAL SNAPSHOT ENGINE

Old idea rejected:

No separate weekly or monthly logs required.

New architecture:

Store one snapshot every run.

Create:

history/

Each run automatically generates:

YYYY-MM-DD.json

Example:

history/

2026-06-18.json

2026-06-19.json

2026-06-20.json

Each snapshot stores:

* Leading themes
* Emerging themes
* Weakening themes
* Lagging themes
* Top long candidates
* Top short candidates

Purpose:

Permanent institutional market history database.

Status:

High priority.

---

P2 — ROTATION DELTA ENGINE

Purpose:

Compare current market structure with historical snapshots.

Example:

Software

Leading → Weakening

Biotech

Lagging → Emerging

Semiconductors

Leading → Emerging

Detect:

Institutional accumulation.

Institutional distribution.

Theme leadership rotation.

Potential file:

rotation_delta.py

Purpose:

Largest future edge in ThemePulse.

Status:

High priority.

---

P3 — STOCK TAXONOMY EXPANSION

Problem:

Still too many unknown stocks.

Examples:

* NKE
* CAG
* WHR
* PLAY
* KHC
* KMB
* DEO
* WBD

Current impact:

Mostly affects short candidate engine.

Target:

Unknown stocks < 5%

Approach:

Gradual maintenance.

No urgent redesign required.

Status:

Medium priority.

---

LOW PRIORITY / DEFERRED ITEMS

Currently NOT required.

Removed from roadmap:

* Weekly maintenance workflow
* Monthly maintenance workflow
* Weekly log generation
* Monthly log generation
* Separate short engine redesign
* Theme normalization engine

Reason:

System architecture now largely self-adaptive.

==================================================
ENGINEERING PRINCIPLES (UPDATED)
================================

Priority order:

1. Capital rotation detection

2. Long candidate quality

3. Historical institutional intelligence

4. Rotation detection over time

5. Stock classification refinement

6. Short candidate refinement

Rules:

Do not redesign stable architecture.

Do not over-engineer logging.

Avoid unnecessary maintenance burden.

System should adapt automatically to future market narratives.

Theme detection is primary.

Stock selection is secondary.

==================================================
TARGET END STATE
================

ThemePulse becomes:

Institutional Capital Rotation Intelligence Engine

Capabilities:

* Detect strongest themes
* Detect weakest themes
* Detect theme rotation early
* Build historical institutional database
* Adapt automatically to future narratives
* Generate best long candidates
* Generate weak short candidates

Final architecture target:

Production-grade market intelligence engine.

END OF DOCUMENT

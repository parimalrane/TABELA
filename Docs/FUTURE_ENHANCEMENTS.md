# THEMEPULSE ROADMAP

## Current Version: V2.0

Status: Production Stable

---

# PROJECT PURPOSE

ThemePulse is an Institutional Capital Rotation Intelligence Engine.

Primary Objective:

* Detect institutional capital rotation
* Identify strongest themes for LONG trades
* Identify weakest themes for SHORT trades
* Detect emerging market narratives early
* Build historical institutional market intelligence database over time

ThemePulse is NOT a stock scanner.

Stock selection is secondary.

Institutional capital flow detection is primary.

---

# CURRENT SYSTEM STATUS

Completed Architecture:

* ETF Engine → Stable
* ETF Universe Expansion (5000+ ETFs) → Stable
* Theme Classification Engine → Stable
* Theme Parent Mapping → Stable
* Composite Scoring Engine → Stable
* Long Engine → Validated
* Short Engine → Acceptable
* Zacks Rank Filtering → Stable
* Snapshot Engine → Completed
* Historical Database Generation → Active

Current Production Version:

VERSION 2.0

---

# CORE SYSTEM PHILOSOPHY

ThemePulse prioritizes accelerating institutional capital rotation.

ThemePulse does NOT attempt to identify the best company.

ThemePulse attempts to identify where institutional money is moving aggressively right now.

Examples:

* MU may rank above NVDA
* CRDO may rank above AVGO
* ALAB may rank above META

This is expected behavior.

Priority Logic:

Recent acceleration > Established leadership

Swing trading opportunity > Long term company quality

Institutional momentum > Company reputation

---

# SCORING PRIORITY (LOCKED)

Stock Ranking Priority:

1. Relative Strength (Highest priority)
2. Theme Strength
3. Sales Growth
4. Zacks Rank
5. Profit Margin

Current scoring engine approved.

No immediate redesign required.

---

# FUTURE ENHANCEMENT PRIORITY

---

## PRIORITY 1

## ROTATION DELTA ENGINE

Objective:

Compare today vs previous market snapshot.

Purpose:

Detect capital rotation changes automatically.

Example:

Day 1:

Software → Leading

Day 2:

Software → Emerging

Interpretation:

Institutional distribution beginning.

Output Example:

ROTATION CHANGES

* Software → Leading → Emerging
* Biotech → Emerging → Leading
* Cloud Computing → Emerging → Weakening

Strategic Value:

Extremely High

Status:

Next development phase

---

## PRIORITY 2

## HISTORICAL MARKET ANALYSIS ENGINE

Objective:

Analyze historical snapshots over longer periods.

Purpose:

Study institutional behavior patterns over weeks/months.

Questions answered:

* Which themes remain strongest consistently
* Which themes repeatedly weaken
* Which themes rotate frequently
* Which new narratives are emerging

Example:

Semiconductors led market for 19 out of 24 sessions.

Interpretation:

Persistent institutional accumulation.

Strategic Value:

Very High

Status:

Future analysis phase

---

## PRIORITY 3

## TAXONOMY EXPANSION SYSTEM

Objective:

Reduce Unknown stock classifications.

Current challenge:

Some stocks still classified as Unknown.

Example:

* Consumer Staples
* Restaurants
* Footwear
* Building Materials
* Homebuilders
* Telecom Infrastructure

Approach:

Gradually expand stock classification dictionary.

Design rule:

System must remain easily maintainable.

Weekly manual updates should remain simple.

Strategic Value:

High

Status:

Incremental maintenance task

---

## PRIORITY 4

## AUTOMATED THEME DISCOVERY

Objective:

Detect new business narratives automatically.

Examples:

New themes may emerge unexpectedly.

Examples:

* Quantum Computing
* Robotics
* Nuclear Infrastructure
* AI Agents
* Autonomous Vehicles
* Space Infrastructure

System should detect newly emerging themes before manual classification.

Purpose:

Adapt system to changing market narratives.

Strategic Value:

Very High

Status:

Research phase

---

## PRIORITY 5

## INSTITUTIONAL PERSISTENCE SCORE

Objective:

Measure strength of themes over time.

Purpose:

Identify persistent institutional accumulation.

Example:

Last 30 sessions:

Semiconductors → Leading 23 days

Software → Weakening 18 days

Output:

Institutional Strength Score

Example:

Semiconductors = 94/100

Software = 42/100

Biotech = 71/100

Strategic Value:

High

Status:

Future phase

---

# LOW PRIORITY ITEMS

Not urgent.

---

## Long Engine Validation

System currently validated.

Periodic review only.

No code work required.

---

## Short Engine Review

Current short engine acceptable.

Review later only if poor live performance observed.

No immediate development required.

---

## Composite Score Redesign

Current engine approved.

No redesign required.

Weights remain stable.

---

# SYSTEM DESIGN RULES

Non Negotiable Rules:

* Do not redesign architecture unnecessarily
* Historical data must remain automatically generated
* User should never manually copy terminal output
* New market narratives must remain adaptable
* System should scale with changing market cycles
* Market memory is core architecture
* Institutional capital flow detection is primary objective
* Stock selection is secondary objective

---

# DAILY WORKFLOW

Every market day:

Step 1

Export:

* ETF.csv
* stocks.csv

from Zacks.

Step 2

Run:

python main.py

Step 3

System automatically creates:

history/YYYY-MM-DD.json

Step 4

Repeat daily.

No manual logging required.

---

# MONTHLY REVIEW PROCESS

After 20-30 market sessions:

Upload history folder into ChatGPT.

Analyze:

* Persistent leadership themes
* Weakening institutional themes
* New emerging themes
* Rotation changes
* Strongest long side themes
* Weakest short side themes
* Market structure changes

Primary focus:

Institutional capital movement

Stock selection remains secondary.

---

# ARCHITECTURE PRINCIPLE

ThemePulse exists to answer one question:

Where is institutional capital rotating aggressively RIGHT NOW?

Everything in system design must support this objective.

Never optimize stock selection before optimizing capital rotation detection.

ThemePulse is a capital rotation intelligence engine first.

Stock scanner second.

---

END OF ROADMAP

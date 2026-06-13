# PROJECT_CHANGELOG.md

## Purpose

Engineering log for AI Swing Trading Scanner project.

This file records:

* What was changed
* Bugs discovered
* Bugs fixed
* Architectural decisions
* Next work items

Do NOT overwrite.

Append new entries chronologically.

---

# SESSION 1 — June 11 2026

Initial project architecture created.

Files created:

* etf_engine.py
* stock_mapper.py
* scoring_engine.py
* composite_engine.py
* main.py

Goal:

Build theme rotation based swing trading scanner.

Architecture:

ETF Layer + Stock Layer.

Status:

Prototype started.

---

# SESSION 2 — June 11 2026

ETF engine completed.

Implemented:

ETF RS Raw Score calculation.

Weights:

1Y = 35%

YTD = 25%

6M = 20%

3M = 10%

1M = 5%

52 Week Range = 5%

Created:

etf_master.csv

Added quartile classification:

Leading

Emerging

Weakening

Lagging

Status:

ETF engine stable.

---

# SESSION 3 — June 12 2026

Stock scoring engine created.

Implemented:

RS Raw Score

RS Rating

Sales Score

Zacks Score

Margin Score

Composite Score

Weights:

Theme = 40%

RS = 30%

Sales = 20%

Zacks = 7%

Margin = 3%

Status:

Scoring engine stable.

---

# SESSION 4 — June 12 2026

Discovered first architecture problem.

Problem:

Most top ranked stocks concentrated in Semiconductors.

Initial assumption:

Need better diversification.

Later determined assumption was wrong.

Real issue:

Poor stock classification.

Important lesson:

Diversification was NOT the problem.

Classification engine was weak.

Status:

Architecture review required.

---

# SESSION 5 — June 12 2026

Built company level override system.

Created:

company_theme_engine.py

Purpose:

Override stock classification for high conviction names.

Examples:

CRDO → AI Infrastructure

MRVL → AI ASIC

NVDA → AI Accelerators

ARM → AI Compute

AAOI → Optical Networking

PANW → Cybersecurity

Status:

Working correctly.

---

# SESSION 6 — June 12 2026

Built ETF translation layer.

Created:

theme_translation_engine.py

Purpose:

Convert company business theme to ETF theme.

Examples:

AI Infrastructure → Artificial Intelligence

AI ASIC → Artificial Intelligence

Memory → Semiconductors

Cybersecurity → Software

Cloud Infrastructure → Cloud Computing

Status:

Working correctly.

---

# SESSION 7 — June 12 2026

Major taxonomy bug discovered.

Problem:

stock_mapper.py used invalid themes.

Examples:

Materials

Financials

Technology

Real Estate

These themes did NOT exist in ETF taxonomy.

Result:

main.py crashed with KeyError.

Example errors:

KeyError: Materials

KeyError: Unknown

Root cause:

ETF.csv is canonical theme source.

Stock layer was inventing invalid theme names.

Status:

Taxonomy redesign initiated.

---

# SESSION 8 — June 12 2026

Created canonical theme architecture.

Created:

ETF_CANONICAL_THEMES.md

New project rule:

No Python file may introduce theme names unless theme exists in ETF taxonomy.

Affected files:

stock_mapper.py

company_theme_engine.py

theme_translation_engine.py

main.py

Status:

Architecture stabilized.

---

# SESSION 9 — June 12 2026

Main pipeline stabilized.

Fixed:

main.py crash bug.

Problem:

theme_score lookup executed outside IF statement.

Bug:

theme_score = theme_score_map[etf_theme]

This caused:

KeyError: Unknown

Fixed by moving theme_score assignment inside conditional block.

Added fallback:

Unknown → Theme Score = 20

Pipeline now runs without crashing.

Status:

Stable.

---

# CURRENT STATUS

Project quality estimate:

8.2 / 10

Working:

ETF engine

Theme ranking

Stock scoring

Composite scoring

Company override engine

Translation engine

Main pipeline

No crash bugs.

---

# CURRENT BIGGEST PROBLEM

Too many stocks mapped to:

Unknown

Reason:

stock_mapper.py relies too heavily on:

Industry field

Sector field

Many companies are misclassified.

Examples:

Retail

Consumer

Payments

Advertising

Travel

Gaming

Industrial Automation

Robotics

E-commerce

Fintech

Defense software

Not properly classified.

---

# NEXT DEVELOPMENT PHASE

Highest priority.

Build Stock Mapping Engine V2.

Do NOT modify:

ETF engine

Scoring engine

Composite engine

Main ranking logic

Focus:

Better stock classification intelligence.

---

# FUTURE DEVELOPMENT PLAN

Build classification engine V2.

Add Layer 1

Manual mapping for high conviction stocks.

Add Layer 2

Keyword engine.

Example:

payment → Fintech

robotics → Artificial Intelligence

data center → AI Infrastructure

adtech → Internet

gaming → Internet

defense software → Aerospace & Defense

industrial automation → Artificial Intelligence

Add Layer 3

Industry + sector fallback.

---

# IMPORTANT RULE

Never make manual code edits under pressure.

Preferred workflow:

Ask ChatGPT to regenerate complete file.

Replace entire file.

Avoid manual search/replace mistakes.

This workflow has proven safer.

---

LAST UPDATED

June 12 2026

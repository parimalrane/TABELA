# VERSION_HISTORY.md

# THEMEPULSE PROJECT VERSION HISTORY

============================================================
THEMEPULSE V1
=============

Release Date: 2026-06-12

Status: Production Ready

---

## PROJECT DESCRIPTION

ThemePulse is a proprietary institutional capital rotation research engine.

Primary Objective:

Identify where institutional money is flowing across market themes and sectors.

Core Philosophy:

Trade LONG where institutional capital is flowing.

Trade SHORT where institutional capital is leaving.

Final trading decisions are based on manual chart review and technical analysis.

---

## CORE DESIGN PHILOSOPHY

Primary Principle:

Institutional Narrative > Traditional Sector Classification

Key Insight Learned During Development:

Traditional sector classification frequently fails to capture real institutional positioning.

Example:

A company classified under Technology sector may actually belong to:

AI Infrastructure

Optical Networking

Semiconductor Equipment

Cloud Infrastructure

Defense AI

Institutional narrative matters more than textbook sector labels.

---

## COMPLETED MODULES

1. ETF Relative Strength Engine

Ranks ETF universe using relative strength model.

2. Theme Rotation Engine

Classifies ETF themes into:

Leading

Emerging

Weakening

Lagging

3. Stock Mapping Engine

Maps all stocks to related market themes using:

Industry

Sector

Business model

Institutional narrative

4. Company Narrative Engine

Manual override engine for high conviction stocks.

Examples:

CRDO → AI Infrastructure

LITE → Optical Networking

MRVL → AI ASIC

VRT → AI Power Infrastructure

5. Theme Translation Engine

Converts company narrative themes into ETF recognized themes.

6. Relative Strength Engine

Calculates custom stock relative strength score.

7. Scoring Engine

Calculates:

RS Score

Sales Score

Zacks Score

Margin Score

8. Composite Scoring Engine

Final weighted score:

Theme Score → 40%

RS Score → 30%

Sales Score → 20%

Zacks Score → 7%

Margin Score → 3%

9. Long Watchlist Engine

Finds strongest stocks in strongest themes.

Requirements:

Leading / Emerging theme

Strong RS

Strong Sales

Strong Zacks

10. Short Watchlist Engine

Detects stocks experiencing institutional capital exit.

Methodology:

Weak theme + weak stock

OR

Relative weakness model

11. Theme Breadth Engine

Measures internal participation inside each theme.

Formula:

Strong Stocks ÷ Total Stocks

12. Production Output Engine

Daily market scan output with:

Market Rotation Summary

Theme Breadth Analysis

Long Watchlist

Short Watchlist

Institutional Leaders

---

## CURRENT SYSTEM METRICS

Total Stocks Covered:

1385

Unknown Theme Stocks:

74

Unknown Ratio:

5.34%

ETF Theme Coverage:

Full ETF Universe

System Stability:

Stable

Architecture Status:

Frozen

---

## CURRENT OUTPUT CAPABILITIES

ThemePulse Daily Market Scan generates:

1. Market Rotation Summary

Leading Themes

Emerging Themes

Weakening Themes

Lagging Themes

2. Theme Breadth Analysis

Theme

Total Stocks

Strong Stocks

Breadth Percentage

3. Top Long Watchlist

Best institutional accumulation candidates

4. Top Short Watchlist

Weak stocks and capital exit candidates

5. Top 20 Institutional Leaders

Highest quality stocks in current market

---

## IMPORTANT ARCHITECTURE DECISIONS

Decision 1

Do not rely purely on Industry and Sector columns.

Decision 2

Institutional Narrative mapping is more important than sector classification.

Decision 3

Unknown theme stocks should NOT be automatically discarded.

Decision 4

Strong unknown stocks can be classified as:

Unclassified Leader

Decision 5

Short candidates should detect institutional capital exit, not simply weak companies.

Decision 6

Broad market stock mapping coverage is more important than perfect mapping accuracy.

Decision 7

Production stability is more important than adding continuous new features.

---

## CURRENT LIMITATIONS

Some stocks remain difficult to classify.

Examples:

GM

HON

BAH

PCAR

LI

Breadth engine can produce misleading output for themes with very few stocks.

Example:

1 stock out of 1 stock = 100% breadth.

ETF universe still includes geographic ETF themes.

Examples:

South Korea

Taiwan

Peru

Chile

Poland

---

## NEXT DEVELOPMENT CYCLE (V2)

Highest Priority

1. Institutional Behavior Engine

Detect institutional accumulation and distribution.

2. Volume Dry Up Detection

Find tight volume before breakout.

3. Distribution Day Detection

Detect institutional selling pressure.

4. Accumulation Day Detection

Detect institutional buying.

5. Relative Weakness Trend Engine

Detect gradual institutional exit.

6. Breadth Trend Engine

Track whether theme participation is improving over time.

7. Theme Quality Engine

Measure average quality inside each theme.

8. ETF Universe Quality Filter

Remove geographic ETFs and irrelevant ETFs.

---

## REFERENCE PHILOSOPHY

Inspired by:

DeepVue

IBD / MarketSurge

Institutional Growth Investing

Theme Rotation Investing

---

## PROJECT STATUS

ThemePulse V1

Production Ready

No major architecture changes recommended.

System ready for daily use.

Current Recommendation:

Run daily for 2 weeks.

Observe market behavior.

Collect notes.

Do NOT add more code immediately.

---

## FINAL PROJECT OBJECTIVE

Build a proprietary institutional market intelligence engine superior to retail stock scanners.

---

## VERSION CONTROL

Current Version:

V1

Next Planned Version:

V1.1

Long Term Vision:

ThemePulse Pro

Created: 2026-06-12
Architecture Frozen: YES
Production Ready: YES



VERSION 1.1 — ETF Pipeline Restoration

Major Fixes

• Restored ETF.csv as active input source
• Removed stale etf_master.csv dependency
• Reconnected etf_engine.py to main.py
• Reconnected theme_parser.py to ETF processing pipeline
• Integrated curated ETF whitelist (42 ETFs)
• Eliminated country/region ETF contamination

Results

• Market rotation now reflects US institutional sector rotation
• Theme classification significantly improved
• Long watchlist quality improved substantially

Pending Issues

• Breadth engine redesign
• Institutional leaders duplicate output
• ETF theme mapping cleanup
• Unknown stock mapping cleanup


ETF DISCOVERY ENGINE

Purpose

Tabela currently uses a manually curated Allowed ETF universe.

Risk

New institutional themes may emerge which are not currently tracked.

Example

Artificial Intelligence
Quantum Computing
Nuclear Energy
Robotics Automation
Defense AI
Space Infrastructure

Future Solution

Build ETF Discovery Engine.

Workflow

1. Scan complete ETF.csv universe daily

2. Exclude currently approved Allowed ETFs

3. Identify strongest untracked ETFs using:

   • ETF RS Rating
   • 3 Month Performance
   • Relative Volume / AUM (future)

4. Generate Candidate ETF Report

5. Manual approval required before adding new ETF to allowed_etfs.py

Principle

Tabela should detect emerging institutional themes automatically but should never auto-add ETFs without manual review.


VERSION 1.3 STABLE
Date: 2026-06-16

Major Architecture Repairs

Core Pipeline Fixes

• Fixed critical bug where ETF.csv was not actively driving system logic
• Removed hidden dependency on stale etf_master.csv architecture
• Reconnected ETF processing pipeline to main.py
• Reconnected etf_engine.py and theme parsing workflow

ETF Universe Fixes

• Integrated curated allowed ETF whitelist (42 approved ETFs)
• Removed country and region ETF contamination
• Eliminated incorrect theme detection caused by broad ETF universe

Breadth Engine Improvements

• Fixed breadth ranking flaw where themes with 1 stock could rank above dominant themes
• Introduced weighted breadth scoring logic using theme size weighting
• Large institutional themes now rank correctly above tiny isolated themes

Long Candidate Engine Improvements

• Removed duplicate output between Long Watchlist and Institutional Leaders
• Merged both systems into single Long Candidate Universe
• Long Candidate Universe now represents union of:

* Primary theme qualified candidates
* Institutional accumulation candidates

Institutional Flow Marker

• Added * marker to stocks added only through institutional flow engine
• Allows visual identification of secondary institutional accumulation candidates

Output Improvements

• Removed unnecessary pandas dataframe index numbers from console output
• Improved readability of final market scan report

Current Architecture Status

Tabela V1.3 Stable

Known Remaining Issues

• ETF Discovery Engine not implemented
• Theme cleanup required (Broad, broad, Socially Responsible)
• Unknown stock mapping cleanup pending


- Rebuilt theme_parser.py

- Removed broad ETF contamination

- Removed country theme contamination

- Removed Socially Responsible / China / Broad labels

- Added invalid theme rejection logic

- Excluded filtered themes from ETF ranking engine


# VERSION 1.5 — ETF Scoring Architecture Upgrade

**Date:** 2026-06-16

## Major Changes Implemented

### 1. ETF Relative Strength Formula Rebuilt

Old Formula:

* 1Y Performance = 35%
* YTD Performance = 25%
* 6M Performance = 20%
* 3M Performance = 10%
* 1M Performance = 5%
* 52 Week Range = 5%

New Formula:

* 3M Performance = 35%
* 1M Performance = 30%
* 6M Performance = 20%
* 1Y Performance = 10%
* 1W Performance = 5%

Removed:

* YTD Performance
* Price as % of 52 Week Range

Purpose:

Prioritize recent institutional capital rotation instead of historical performance.

---

### 2. Theme Engine Cleanup Completed

Removed invalid ETF theme contamination.

Removed invalid themes:

* Broad
* broad
* China
* Socially Responsible
* Country ETF contamination

Root cause identified in:

* theme_parser.py

---

### 3. Theme Filtering Logic Added

Invalid ETF themes now excluded from rotation engine before ranking.

Filtered themes no longer pollute output.

---

### 4. Architecture Discovery

Identified that ETF ranking alone is insufficient.

Breadth participation should eventually influence final theme ranking.

Future architecture redesign required.

---

## System Status

Tabela architecture stable.

Production remains operational.




VERSION 2.0

Completed:

- Expanded ETF universe (5000+ ETF architecture)
- Composite score weights configurable
- Long engine validated against institutional rotation philosophy
- Short engine filtering stabilized
- Zacks rank filtering enforced
- Snapshot Engine implemented
- Automatic historical database generation

Architecture philosophy locked:

ThemePulse prioritizes accelerating institutional capital rotation rather than established market leaders.
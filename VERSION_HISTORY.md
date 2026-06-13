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

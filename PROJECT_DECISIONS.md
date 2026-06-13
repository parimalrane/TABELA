# PROJECT_MASTER_DECISIONS.md

## Project Name

AI Swing Trading Scanner
Theme Rotation First Architecture

Author: Parimal
Start Date: June 2026

---

# 1. CORE PHILOSOPHY

Objective is NOT stock screening.

Objective is:

* Detect institutional money flow
* Identify strongest market themes
* Rank stocks inside strongest themes
* Focus on swing trading candidates

Primary principle:

Trade where institutional money is flowing.

Priority:

1. Theme Strength
2. Relative Strength
3. Sales Growth
4. Zacks Rank
5. Profitability

Inspired by:

* DeepVue
* IBD (Investor’s Business Daily)
* MarketSurge
* Institutional Growth Investing

---

# 2. ARCHITECTURE DECISION

Final architecture uses TWO datasets.

## ETF Layer

ETF.csv

Purpose:

* Detect market leadership
* Detect sector rotation
* Detect theme rotation
* Rank strongest and weakest themes

ETF is SINGLE SOURCE OF TRUTH for theme classification.

No stock can invent its own ETF strength.

---

## Stock Layer

stocks.csv

Purpose:

* Map each stock to ETF theme
* Inherit ETF strength
* Rank strongest stocks inside strongest themes

Stock layer cannot independently decide theme strength.

Theme strength ALWAYS comes from ETF layer.

---

# 3. ETF ENGINE RULES

Input:

ETF.csv

Exclude:

* Bond ETFs
* Treasury ETFs
* Currency ETFs
* Volatility ETFs
* Inverse ETFs
* Leveraged ETFs
* Commodity only ETFs
* Cash equivalent ETFs

Allowed ETFs:

* Sector ETFs
* Industry ETFs
* Growth ETFs
* Innovation ETFs
* Thematic ETFs

---

# 4. ETF SCORING MODEL

ETF RS Raw Score

Weights:

1Y Performance = 35%

YTD Performance = 25%

6M Performance = 20%

3M Performance = 10%

1M Performance = 5%

52 Week Range Position = 5%

Formula:

ETF_RS_Raw

Classification:

Top 25% → Leading → Score 100

Next 25% → Emerging → Score 75

Next 25% → Weakening → Score 40

Bottom 25% → Lagging → Score 20

Output file:

etf_master.csv

---

# 5. ETF TAXONOMY RULE

ETF.csv is ONLY source of allowed themes.

Allowed themes must exist inside ETF universe.

Examples:

Valid:

* Semiconductors
* Artificial Intelligence
* Software
* Cloud Computing
* Gold Mining
* Copper Mining
* Uranium Mining
* Medical Devices
* Pharma
* Banking
* Insurance

Invalid generic themes:

* Technology
* Financials
* Materials
* Healthcare Sector
* Energy Sector

Never use generic sector names if ETF taxonomy has more specific themes.

---

# 6. STOCK MAPPING ENGINE V1

Current file:

stock_mapper.py

Current mapping priority:

Priority 1

Manual company override

company_theme_engine.py

Example:

NVDA → AI Accelerators

CRDO → AI Infrastructure

MRVL → AI ASIC

AAOI → Optical Networking

PANW → Cybersecurity

---

Priority 2

Industry field from stocks.csv

Example:

Semiconductor → Semiconductors

Medical → Medical Devices

Pharma → Pharma

Insurance → Insurance

REIT → REITs

---

Priority 3

Sector fallback

Example:

Technology → Broad

Medical → Healthcare

Finance → Banking

Energy → Exploration

---

Priority 4

Unknown

If no mapping found:

Return Unknown

---

# 7. COMPANY BUSINESS LAYER

File:

company_theme_engine.py

Purpose:

Capture REAL business exposure.

Examples:

CRDO → AI Infrastructure

MRVL → AI ASIC

NVDA → AI Accelerators

ARM → AI Compute

DDOG → Cloud Infrastructure

PANW → Cybersecurity

This layer intentionally uses NON ETF names.

This is correct.

Do not change.

---

# 8. ETF TRANSLATION LAYER

File:

theme_translation_engine.py

Purpose:

Convert company business exposure into ETF theme.

Examples:

AI Infrastructure → Artificial Intelligence

AI ASIC → Artificial Intelligence

AI Accelerators → Artificial Intelligence

Optical Networking → Semiconductors

Memory → Semiconductors

Cybersecurity → Software

Cloud Infrastructure → Cloud Computing

Important:

Company theme != ETF theme

Stock may keep business label.

ETF strength inherited from translated ETF theme.

---

# 9. STOCK SCORING MODEL

Weighting:

Theme Strength = 40%

RS Score = 30%

Sales Growth = 20%

Zacks Score = 7%

Margin Score = 3%

Formula:

Composite Score

Current files:

scoring_engine.py

composite_engine.py

---

# 10. RS RATING MODEL

Weights:

Relative Price Change YTD = 35%

Price Change YTD = 25%

12 Week = 20%

4 Week = 10%

1 Week = 5%

52 Week Range = 5%

Rank all stocks.

Percentile ranking.

Convert to:

99

98

97

95

90

80

70

60

40

Current status:

Working correctly.

---

# 11. CURRENT PROJECT STATUS

Current project quality:

8.2 / 10

Completed:

ETF engine → stable

ETF ranking → stable

Theme classification → stable

RS scoring → stable

Sales scoring → stable

Zacks scoring → stable

Margin scoring → stable

Composite score → stable

Company override engine → stable

ETF translation engine → stable

Main pipeline → stable

No crash bugs.

---

# 12. BIGGEST CURRENT PROBLEM

Too many stocks mapped to:

Unknown

Observed:

Hundreds of:

MISSING ETF THEME: Unknown

Reason:

stock_mapper.py is too shallow.

Currently relies heavily on:

* Industry
* Sector

This causes poor classification.

This is biggest weakness.

---

# 13. IMPORTANT LESSON LEARNED

Diversification was NOT the problem.

Earlier assumption:

Need broader theme diversification.

This was wrong.

Real problem:

Poor stock classification intelligence.

Parimal correctly identified this issue.

Architecture changed after this realization.

---

# 14. NEXT DEVELOPMENT PHASE

Build Stock Mapping Engine V2

Highest priority.

Do NOT touch scoring engine.

Do NOT touch ETF engine.

Do NOT touch composite engine.

Focus ONLY on better classification.

---

# 15. STOCK MAPPING ENGINE V2 PLAN

Add Layer 1

Manual high conviction mapping

Examples:

PLTR → Artificial Intelligence

SNOW → Cloud Infrastructure

PANW → Cybersecurity

RKLB → Aerospace & Defense

AVAV → Aerospace & Defense

CELH → Consumer Growth

SHOP → E Commerce

UBER → Transportation Platform

---

Add Layer 2

Keyword engine

Examples:

payment → Fintech

robotics → Artificial Intelligence

data center → AI Infrastructure

adtech → Internet

gaming → Internet

e commerce → Internet

defense software → Aerospace & Defense

industrial automation → Artificial Intelligence

---

Add Layer 3

Current industry mapper

---

# 16. LONG TERM GOAL

Final system should replicate institutional style research.

Workflow:

ETF Rotation → Theme Leadership

Stock Mapping → Business Exposure

Theme Inheritance → ETF Strength

Stock Ranking → Composite Score

Long Watchlist

Short Watchlist

Institutional Leaders

No trade execution.

Human makes final decision after chart review.

---

# 17. IMPORTANT RULES

Never use generic sector labels if ETF universe is more specific.

ETF.csv is single source of theme classification.

Theme strength matters more than stock strength.

Stock strength matters more than sales growth.

Sales growth matters more than Zacks.

Zacks matters more than margin.

Always preserve architecture.

Never change scoring weights without deliberate review.

---

END OF MASTER FILE

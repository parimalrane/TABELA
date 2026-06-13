CAPITAL ROTATION ENGINE — FUTURE ENHANCEMENTS

Version Status

Current Version: V1 Production Beta

Core Architecture Status:

Completed

---

PRIORITY A — INSTITUTIONAL BEHAVIOR ENGINE
(HIGH PRIORITY)
---------------

Objective:

Improve short and long candidate quality by detecting institutional accumulation and distribution behavior.

A1 — Volume Dry Up Detection

Goal:

Detect stocks where selling pressure is disappearing before breakout.

Logic:

Current Volume < 50 Day Average Volume

Use Cases:

Long Watchlist confirmation

A2 — Distribution Day Detection

Goal:

Detect institutional selling.

Logic:

Down Day + Volume Above Average

Use Cases:

Short Watchlist confirmation

Detect broken leaders

A3 — Relative Weakness Trend

Goal:

Detect stocks losing institutional sponsorship.

Logic:

Stock underperforming benchmark over rolling period

Possible Factors:

4 Week Relative Performance deterioration

12 Week Relative Performance deterioration

Use Cases:

Short Watchlist ranking

---

## PRIORITY B — ADVANCED MARKET BEHAVIOR

B1 — Earnings Gap Detection

Detect earnings breakouts and earnings breakdowns.

B2 — Gap Up / Gap Down Engine

Measure institutional reaction after earnings.

B3 — Accumulation Days Engine

Up Day + Above Average Volume

B4 — Distribution Days Count

Track institutional selling over rolling 20 days.

---

## PRIORITY C — TECHNICAL CONFIRMATION ENGINE

C1 — Moving Average Alignment

20 EMA > 50 SMA > 200 SMA

C2 — Distance From 52 Week High

C3 — Volatility Contraction Pattern Detection

C4 — Breakout Detection

---

## PRIORITY D — THEME EVOLUTION ENGINE

Detect emerging themes BEFORE ETF providers classify them.

Examples:

Quantum Computing

Stablecoins

Robotics

Defense AI

Space Infrastructure

Nuclear Infrastructure

---

## LONG TERM GOAL

Build proprietary institutional money flow research engine superior to retail scanners.

Reference Philosophy:

DeepVue

IBD / MarketSurge

Institutional Growth Investing

Theme Rotation First Approach

---

## IMPORTANT PROJECT PRINCIPLE

Institutional Narrative > Traditional Sector Classification

Price Action reveals institutional behavior before classification systems catch up.


# THEMEPULSE — FUTURE ENHANCEMENTS ROADMAP

Current Version: V1 Production Beta

Core Architecture Status:
Stable

Current Capabilities:
- ETF Relative Strength Engine
- Theme Rotation Engine
- Stock Mapping Engine
- Institutional Narrative Database
- Long Watchlist Engine
- Short Watchlist Engine
- Composite Scoring Engine


===========================================================
PRIORITY A — INSTITUTIONAL BEHAVIOR ENGINE
(HIGHEST PRIORITY)
===========================================================

Objective:

Detect institutional accumulation and institutional distribution.

This can become the biggest edge of the entire system.


A1 — Volume Dry Up Detection

Goal:

Identify stocks where selling pressure is disappearing.

Logic:

Current Volume < 50 Day Average Volume

Use Cases:

Long Watchlist confirmation

Example:

Tight volume before breakout


-----------------------------------------------------------

A2 — Distribution Day Detection

Goal:

Detect institutional selling pressure.

Logic:

Price closes down
AND
Volume > Average Volume

Use Cases:

Short Watchlist confirmation

Detect broken leaders early


-----------------------------------------------------------

A3 — Accumulation Day Detection

Goal:

Detect institutional buying.

Logic:

Price closes up
AND
Volume > Average Volume

Use Cases:

Long Watchlist confirmation


-----------------------------------------------------------

A4 — Relative Weakness Trend

Goal:

Detect gradual institutional exit.

Logic:

4 Week relative performance deterioration

12 Week relative performance deterioration

Use Cases:

Short Watchlist ranking


===========================================================
PRIORITY B — TECHNICAL CONFIRMATION ENGINE
===========================================================

B1 — Moving Average Alignment

Goal:

Trend confirmation.

Logic:

20 EMA > 50 SMA > 200 SMA

Use Cases:

Long confirmation


-----------------------------------------------------------

B2 — Distance From 52 Week High

Goal:

Find true leaders.

Logic:

Percent distance from 52 week high

Use Cases:

Long ranking


-----------------------------------------------------------

B3 — Breakout Detection Engine

Goal:

Detect fresh breakouts.

Logic:

Price crosses resistance zone


-----------------------------------------------------------

B4 — Volatility Contraction Pattern Detection

Goal:

Detect institutional accumulation patterns.

Reference:

Mark Minervini methodology


===========================================================
PRIORITY C — MARKET STRUCTURE ENGINE
===========================================================

C1 — Theme Breadth Analysis

Goal:

Measure strength inside each theme.

Output:

Theme | Stocks | Strong Stocks | Breadth %

Strong Stock Definition:

RS Rating >= 80
AND
Composite Score >= 75


-----------------------------------------------------------

C2 — Market Health Dashboard

Goal:

Understand market quality.

Metrics:

Number of Leading Themes

Number of Lagging Themes

Number of Strong Stocks

Number of Weak Stocks

Breadth expansion / contraction


-----------------------------------------------------------

C3 — ETF Leadership Momentum

Goal:

Detect emerging sector rotation.

Logic:

Acceleration in ETF relative strength ranking


===========================================================
PRIORITY D — STOCK CLASSIFICATION ENGINE
===========================================================

D1 — Expand stock_mapper.py

Current Problem:

Poor coverage outside growth sectors.

Need better mapping for:

- Consumer
- Retail
- Restaurants
- Housing
- Construction
- Telecom
- Utilities
- Industrials
- Manufacturing
- Transportation
- Entertainment


-----------------------------------------------------------

D2 — Expand company_theme_engine.py

Current Status:

Strong growth stock coverage

Need expansion for:

- Consumer leaders
- Financial leaders
- Industrial leaders
- Emerging narratives


-----------------------------------------------------------

D3 — Auto Classification Engine

Goal:

Reduce manual mapping.

Logic:

Automatically classify stocks using business descriptions.

Example:

If company description contains:

GPU
Datacenter
AI Inference
Cybersecurity
Cloud Infrastructure

Then assign probable narrative automatically.


===========================================================
PRIORITY E — ADVANCED MARKET EVENTS ENGINE
===========================================================

E1 — Earnings Gap Detection

Detect gap up / gap down after earnings.


-----------------------------------------------------------

E2 — Earnings Surprise Engine

Track positive and negative earnings reactions.


-----------------------------------------------------------

E3 — Post Earnings Drift Detection

Detect institutional continuation after earnings.


===========================================================
PRIORITY F — AI / MACHINE LEARNING
(LONG TERM)
===========================================================

F1 — Automatic Theme Discovery

Goal:

Detect new themes BEFORE ETF providers launch ETFs.

Examples:

- Quantum Computing
- Stablecoins
- Robotics
- Defense AI
- Space Infrastructure
- Nuclear Infrastructure


-----------------------------------------------------------

F2 — Adaptive Theme Evolution Engine

Goal:

Re-rank themes automatically as market narratives evolve.


===========================================================
PRIORITY G — DATA QUALITY ENGINE
===========================================================

G1 — Missing Theme Detection

Detect stocks classified as Unknown.


-----------------------------------------------------------

G2 — Theme Mapping Audit Report

Output:

Total Stocks

Mapped Stocks

Unmapped Stocks


-----------------------------------------------------------

G3 — Confidence Score

Every stock gets classification confidence.

Example:

NVDA → 95%

Unknown stock → 20%


===========================================================
PRIORITY H — REPORTING ENGINE
===========================================================

H1 — Daily Report Generator

Output:

Top Long Candidates

Top Short Candidates

Leading Themes

Lagging Themes


-----------------------------------------------------------

H2 — Export to Excel

Auto generate ranked Excel output.


-----------------------------------------------------------

H3 — Historical Database

Store previous daily scans.

Track changes over time.


===========================================================
PROJECT PHILOSOPHY
===========================================================

Core Principle:

Institutional Narrative > Traditional Sector Classification


Price action reveals institutional behavior before classification systems catch up.


===========================================================
REFERENCE PHILOSOPHY
===========================================================

Inspired by:

- DeepVue
- IBD / MarketSurge
- Theme Rotation Investing
- Institutional Growth Investing


===========================================================
IMPORTANT RULE
===========================================================

Do NOT continuously change stable architecture.

New features must be validated against real market behavior.

Production stability is more important than feature expansion.


===========================================================
PRIORITY C4 — BREADTH TREND ENGINE
(HIGH PRIORITY)
===========================================================

Current Problem:

Breadth analysis only shows current snapshot.

No ability to measure change over time.


Objective:

Track whether internal participation inside themes is improving or deteriorating.


Example:

Semiconductors

Yesterday Breadth = 42%

Today Breadth = 55%

Interpretation:

Institutional participation expanding.

Theme strengthening.


-----------------------------------------------------------

C4.1 — Historical Breadth Database

Store daily breadth values for every theme.

Example:

Date | Theme | Breadth %

2026-06-12 | Semiconductors | 42%

2026-06-13 | Semiconductors | 48%


-----------------------------------------------------------

C4.2 — Breadth Acceleration Score

Measure speed of participation change.

Example:

Semiconductors

5 Day Breadth Change = +12%

Interpretation:

Theme rapidly strengthening.


-----------------------------------------------------------

C4.3 — Breadth Deterioration Detection

Detect weakening internal participation.

Example:

Artificial Intelligence

Yesterday = 65%

Today = 48%

Interpretation:

Institutions reducing participation.

Potential early warning signal.


-----------------------------------------------------------

C4.4 — Minimum Breadth Threshold Filter

Current Problem:

Themes with 1 stock create misleading 100% breadth.

Example:

AI ASIC = 1 stock = 100%

This does NOT represent broad institutional participation.


Solution:

Ignore themes with fewer than 5 stocks.

Rule:

If Total Stocks < 5

Label:

Insufficient Breadth Data


-----------------------------------------------------------

C4.5 — Breadth Leadership Ranking

Rank themes by:

Breadth %

AND

Breadth acceleration

Formula Example:

Breadth Score =

Current Breadth × 70%

5 Day Breadth Change × 30%


Use Cases:

Detect emerging leadership before price breakout.



===========================================================
PRIORITY C5 — THEME QUALITY ENGINE
(HIGH PRIORITY)
===========================================================

Problem:

Theme can show strong breadth but average stock quality may be poor.


Objective:

Measure average quality inside each theme.


Metrics:

Average Composite Score

Average RS Rating

Average Sales Score


Example:

Semiconductors

Average Composite Score = 82

Average RS Rating = 88


Cloud Computing

Average Composite Score = 54

Average RS Rating = 61


Interpretation:

Higher quality themes receive stronger institutional sponsorship.


Use Cases:

Improve theme ranking system beyond ETF relative strength alone.
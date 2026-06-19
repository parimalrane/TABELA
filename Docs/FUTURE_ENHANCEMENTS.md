# FUTURE_ENHANCEMENTS.md

# THEMEPULSE FUTURE DEVELOPMENT ROADMAP

============================================================
PROJECT STATUS
==============

Current Version:

ThemePulse V1

Current Status:

Production Ready

Architecture Status:

Frozen

Important Rule:

Do NOT continuously modify stable production architecture.

Future enhancements must be tested against real market behavior before implementation.

Core Philosophy:

Institutional Narrative > Traditional Sector Classification

Primary Objective:

Track institutional capital rotation before retail market recognizes leadership changes.

############################################################
TIER 1 — HIGHEST PRIORITY
(Core Future Edge)
############################################################

============================================================

1. INSTITUTIONAL BEHAVIOR ENGINE
   (HIGHEST PRIORITY)
   ============================================================

Importance:

10/10

Modules:

Volume Dry Up Detection

Distribution Day Detection

Accumulation Day Detection

Relative Weakness Trend Engine

Objective:

Detect institutional accumulation and distribution before price expansion.

############################################################
TIER 2 — VERY HIGH PRIORITY
(Market Structure Intelligence)
############################################################

============================================================
2. BREADTH TREND ENGINE
=======================

Importance:

9.5/10

Current Problem:

Breadth engine shows only current snapshot.

No trend detection.

Modules:

Historical Breadth Database

Breadth Acceleration Score

Breadth Deterioration Detection

Minimum Breadth Filter

Current Known Issue:

1 stock out of 1 stock = 100% breadth.

This creates mathematically correct but intellectually misleading output.

Example:

AI ASIC = 100%

Semiconductors = 73%

Market Interpretation:

Semiconductors represent much broader institutional participation.

Future Rule:

Ignore themes with fewer than 5 stocks.

---

2E — BREADTH QUALITY ENGINE
(NEW FROM LIVE PRODUCTION OBSERVATION)
--------------------------------------

Importance:

9.5/10

Problem:

Breadth % alone does not measure theme importance.

Example:

AI ASIC

1 strong stock out of 1 stock = 100%

Semiconductors

61 strong stocks out of 83 stocks = 73%

Current engine incorrectly makes AI ASIC look stronger.

Objective:

Measure breadth quality, not only breadth ratio.

Possible Formula:

Breadth Score =

(Breadth Percent × 40%)

*

(Theme Size Weight × 30%)

*

(Average Composite Score × 30%)

Purpose:

Prioritize institutional participation depth.

############################################################
TIER 3 — HIGH PRIORITY
(Theme Intelligence Improvements)
############################################################

============================================================
3. THEME QUALITY ENGINE
=======================

Importance:

9/10

Problem:

Theme can show strong breadth while underlying stock quality remains weak.

Metrics:

Average Composite Score

Average RS Rating

Average Sales Score

Average Margin Score

Goal:

Measure average quality of stocks inside theme.

############################################################
TIER 4 — HIGH PRIORITY
(DATA QUALITY IMPROVEMENTS)
############################################################

============================================================
4. ETF UNIVERSE QUALITY FILTER
==============================

Importance:

8.5/10

Current Problem:

ETF engine includes irrelevant geographic ETFs.

Examples:

South Korea

Taiwan

Peru

Chile

Poland

Broad Pacific

Problem:

These geographic ETFs pollute market rotation output.

Solution:

Remove non-actionable ETF themes.

Exclude:

Country ETFs

Regional ETFs

Broad International ETFs

Broad Index ETFs

---

## 4A — UNKNOWN STOCK REDUCTION ENGINE

Goal:

Reduce Unknown ratio below 3%

Method:

Expand stock_mapper.py continuously.

---

## 4B — THEME CONFIDENCE SCORE

Goal:

Assign confidence score to every mapping.

Example:

NVDA → 95%

Unknown → 20%

---

4C — US MARKET ETF PURIFICATION ENGINE
(NEW FROM LIVE PRODUCTION OBSERVATION)
--------------------------------------

Importance:

9/10

Observation:

User trades US market only.

Market rotation output currently dominated by geographic ETF themes.

Current Output Problem:

Leading Themes includes:

South Korea

Taiwan

Peru

Israel

Broad Pacific

Issue:

These ETFs are US-listed but do not represent actionable internal US sector rotation.

Goal:

Restrict ETF universe to US institutional capital rotation themes.

Keep:

Semiconductors

Artificial Intelligence

Software

Cloud Computing

Cybersecurity

Biotech

Infrastructure

Energy

Healthcare

Remove:

Country ETFs

Regional ETFs

Broad international exposure ETFs

############################################################
TIER 5 — ADVANCED MARKET EVENT ENGINE
############################################################

============================================================
5. EARNINGS REACTION ENGINE
===========================

Importance:

8/10

Modules:

Earnings Gap Up Detection

Earnings Gap Down Detection

Post Earnings Drift Detection

Positive Earnings Surprise Detection

Negative Earnings Surprise Detection

############################################################
TIER 6 — ADVANCED TECHNICAL ENGINE
############################################################

============================================================
6. TECHNICAL CONFIRMATION ENGINE
================================

Importance:

7.5/10

Modules:

Moving Average Alignment

Breakout Detection

Volatility Contraction Pattern Detection

Important Rule:

Avoid indicator overload.

Do NOT Add:

RSI

MACD

Stochastic

############################################################
TIER 7 — AUTOMATION & REPORTING ENGINE
############################################################

============================================================
7. DAILY REPORT AUTOMATION
==========================

Importance:

7/10

Features:

Automatic daily scan

Historical database

CSV reports

Excel reports

Historical report storage

############################################################
TIER 8 — ADVANCED AI ENGINE
(Long Term Vision)
############################################################

============================================================
8. AUTOMATIC THEME DISCOVERY ENGINE
===================================

Importance:

Future Research

Goal:

Detect emerging institutional narratives before ETF providers recognize them.

Examples:

Quantum Computing

Defense AI

Robotics

Space Infrastructure

Autonomous Mobility

############################################################
TIER 9 — OPTIONAL SMALL ENHANCEMENTS
############################################################

============================================================
9. OUTPUT FORMATTING ENGINE
===========================

Importance:

Low

Features:

Pretty console tables

CSV export

HTML report generation

---

## 9A — VERSION CONTROL DOCUMENTATION

Maintain:

VERSION_HISTORY.md

---

## 9B — DAILY TRADING WORKFLOW DOCUMENT

Formal workflow around scanner usage.

---

9C — INSTITUTIONAL LEADERS REDESIGN
(NEW FROM LIVE PRODUCTION OBSERVATION)
--------------------------------------

Importance:

Medium

Observation:

TOP LONG WATCHLIST and TOP 20 INSTITUTIONAL LEADERS currently produce nearly identical output.

Reason:

Composite Score heavily weights Theme Score.

Strongest stocks naturally overlap with Long Watchlist.

Current Problem:

Institutional Leaders section adds little new information.

Future Options:

Option A

Remove completely.

Option B

Redesign as highest RS stocks ignoring Theme Score.

Option C (Preferred Long Term)

Redesign using Institutional Behavior Engine.

Metrics:

Accumulation Days

Volume Dry Up

Tight Consolidation

Repeated High Volume Buying

Purpose:

Show true institutional accumulation independent of long watchlist logic.

############################################################
IMPORTANT DEVELOPMENT RULES
############################################################

Rule 1

Production stability is more important than new features.

Rule 2

Observe system behavior for weeks before coding.

Rule 3

Real market feedback is more valuable than more code.

Rule 4

Never continuously modify stable architecture.

Rule 5

Institutional behavior remains biggest future edge.

Rule 6

Do NOT add random technical indicators.

Rule 7

ThemePulse must remain institutional capital intelligence engine.

============================================================
LATEST V1 OBSERVATIONS FROM PRODUCTION USE
==========================================

Observation 1

Breadth engine overvalues tiny themes with 100% breadth.

Observation 2

ETF universe polluted by geographic ETFs.

Observation 3

Institutional Leaders section redundant with Long Watchlist.

Conclusion

Live market usage has identified architecture improvements for future versions.

No immediate code changes required.

Continue observing system behavior for 2–4 weeks before modifying architecture.

============================================================
FINAL DEVELOPMENT PRINCIPLE
===========================

Follow the money.

Not the news.

Not opinions.

Not indicators.

Institutional capital flow determines market leadership.

Created: 2026-06-12

Updated After Live Production Review: 2026-06-14

Architecture Frozen: YES



UPDATED PRIORITY ROADMAP

HIGH PRIORITY

1. ETF Discovery Engine

Purpose

Detect new institutional themes emerging outside manually approved ETF universe.

Problem

Allowed ETF list is static. Market creates new themes dynamically.

Examples

Quantum Computing
Defense AI
Space Infrastructure
Robotics Automation
Gene Editing

Solution

Daily scan full ETF.csv universe.

Process

• Exclude approved ETFs
• Detect strongest untracked ETFs
• Generate candidate ETF report
• Manual approval required before adding new ETF

2. Theme Cleanup Engine

Problem

ETF universe still produces noisy themes.

Examples

Broad
broad
Socially Responsible
China

Solution

Review ETF.csv mapping logic and normalize theme definitions.

3. Unknown Stock Mapping Cleanup

Problem

Some stocks still classified as Unknown.

Solution

Improve stock to theme mapping engine and fallback logic.


# HIGH PRIORITY FUTURE ENHANCEMENTS

## PRIORITY 1 — Breadth Integrated Theme Ranking

Current limitation:

Theme ranking uses ETF_RS_Raw only.

Problem:

Strong ETF performance alone does not confirm broad institutional participation.

Future design:

Final Theme Score =

70% ETF_RS_Raw

30% Weighted Breadth Score

Architecture change required in main.py pipeline.

Current blocker:

theme_breadth currently generated after theme classification.

Requires pipeline redesign.

---

## PRIORITY 2 — Equipment and Services Theme Cleanup

Current suspicious output:

Equipment and services

Need trace:

Identify ETF source in ETF.csv causing generic theme label.

Likely parser improvement required.

---

## PRIORITY 3 — Short Engine Philosophy Review

Need review whether short candidates represent:

True weak themes in US market

OR

Weakest themes inside current ETF universe.

Potential redesign required.

---

## PRIORITY 4 — ETF Discovery Engine

Purpose:

Detect new emerging themes not currently present in allowed_etfs.py

Process:

Full ETF.csv

↓

Detect strong ETFs not already approved

↓

Recommend new ETF for theme expansion

Example:

* Quantum Computing
* Defense AI
* Robotics
* Space Infrastructure





## PRIORITY FUTURE ENHANCEMENT — SCALABLE THEME CLASSIFICATION ENGINE

Current limitation:

ThemePulse uses hardcoded:

Ticker → Theme mapping.

Problem:

Company business models evolve over time.

Hardcoded classification becomes outdated.

Example:

META

2022 → Social Media

2026 → AI Platform

Future → Robotics / Wearables

TSLA

2022 → EV

2026 → Autonomous Mobility

Future → Robotics

---

Future architecture design:

Layer 1

Ticker → Business Category

Example:

NVDA → Semiconductor GPU

MSFT → Cloud Software

META → Digital Platform

XOM → Integrated Energy

---

Layer 2

Business Category → Market Theme Translation

Example:

Semiconductor GPU → Artificial Intelligence

Cloud Software → Cloud Computing

Integrated Energy → Energy

---

Layer 3

Automatic discovery engine

Process:

Find strongest RS_Rating stocks missing from classification dictionary.

Print review candidates.

Purpose:

Reduce manual maintenance burden.

Improve long term scalability.

Architecture complexity intentionally delayed for future version.





## THEME ENGINE V2 (Graph Based Architecture)

Current limitation:

One ticker mapped to one theme.

Problem:

Institutional capital rotates through narratives, not isolated sectors.

New architecture:

Ticker → Multiple Business Categories

Business Category → Multiple Institutional Themes

Institutional Themes carry weighted contribution percentages.

Example:

NVDA

GPU Compute → AI (60%), Semiconductors (40%)

Autonomous Driving → AI (70%), Robotics (30%)

Benefits:

* More realistic institutional capital flow detection
* Better theme clustering
* Better long and short candidate ranking
* Scalable architecture
* Reduced manual maintenance

Priority:

Highest future architecture upgrade




# FUTURE_ENHANCEMENTS.md

## THEMEPULSE V2 ROADMAP

Architecture Status: PRODUCTION STABLE
Core Philosophy: Institutional Capital Rotation First

---

## CURRENT PRIORITY ORDER

### PRIORITY 1 — AUTOMATED LOGGING ENGINE (HIGHEST PRIORITY)

Build fully automated logging system.

Requirements:

* Zero manual copy/paste
* Trigger automatically every run of main.py
* Save output locally

Files to create:

* logger_engine.py

Folder structure:

logs/
daily/
weekly/
monthly/
rotation/

Daily log requirements:

Store:

* Leading Themes
* Emerging Themes
* Weakening Themes
* Lagging Themes
* Top Long Candidates
* Top Short Candidates

Weekly log requirements:

Store:

* Dominant Themes
* New Emerging Themes
* Themes Losing Strength
* Best Long Candidates
* Best Short Candidates

Monthly log requirements:

Store:

* Dominant Monthly Themes
* Improving Themes
* Deteriorating Themes
* Consistent Long Candidates
* Consistent Short Candidates

---

### PRIORITY 2 — ROTATION DELTA ENGINE

Build automatic rotation comparison engine.

Purpose:

Compare latest output against previous historical logs.

New file:

* rotation_tracker.py

Detect:

* New Leaders
* Losing Leaders
* Improving Themes
* Deteriorating Themes

Store inside:

logs/rotation/

---

### PRIORITY 3 — WEEKLY INSTITUTIONAL REVIEW SYSTEM

Workflow:

Every week review ThemePulse weekly logs.

Primary objective:

Detect institutional capital rotation.

Questions:

* Which themes gained sponsorship?
* Which themes lost sponsorship?
* Which themes improved?
* Which themes deteriorated?

---

### PRIORITY 4 — MONTHLY STRUCTURAL REVIEW

Monthly review of historical weekly logs.

Primary objective:

Detect regime shifts.

Questions:

* Which themes consistently led?
* Which themes consistently weakened?
* Which sectors deserve focus next month?

---

### PRIORITY 5 — CLASSIFICATION DATABASE IMPROVEMENT

Lower priority.

Improve:

company_theme_engine.py

Approach:

Gradually add 5–10 missing stocks per week.

No mass rebuild.

No attempt to classify entire market.

---

STRICT RULE

Do NOT redesign architecture again without strong reason.



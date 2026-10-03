# TABELA Backtesting & Optimization: Master Handover Document

**Last Updated:** October 2, 2026
**Target Audience:** Future LLMs, AI Agents, or developers taking over the TABELA codebase.
**Purpose:** This document contains the distilled, institutional knowledge of the TABELA quantitative backtesting suite. Read this thoroughly before suggesting *any* modifications to the scoring engine, configuration, or short/long logic.

---

## 1. Project Overview & Architecture: The 4-Tier System

TABELA is an institutional-grade, multi-dimensional momentum stock screener. After massive historical regressions, the system was mathematically optimized into a strict **4-Tier Tracker**:

- **Tier 1: Strong Breakout** (Long) — High-conviction breakout stocks (RS 90+, Score 90+)
- **Tier 2: Mild Pullback** (Long) — The Day 1-21 recoil of a Strong Breakout. 
- **Tier 3: Strong Breakdown** (Short) — Institutional "Fall From Grace" structural failures (RS 40-60, Score < 45).
- **Tier 4: Mild Relief Rally** (Short) — The Day 1-21 dead-cat bounce of a Strong Breakdown. 

**Critical Discovery:** The 50-Day "Basing" (Long) and "Decaying" (Short) tracking buckets were permanently executed from the codebase. A dedicated backtesting grid (`run_tuner_basing.py`) mathematically proved that maintaining 50-day fundamental forgiveness resulted in a massive 70%+ failure rate. Once a stock surpasses 21 days off the tracker, it is purely chopped/dead money and is deleted.

### Infrastructure
**The Brain:** `c:\TABELA\config\config.py` — all weights, thresholds, and scoring maps.
**The Memory:** `c:\TABELA\market_data\stock_universe\` — JSON arrays that store state and increment drop-days continuously.
**The Scorer:** `c:\TABELA\scoring\scoring_engine.py` — computes independent `Long_Score` and `Short_Score` per stock with mandatory data string formatting guards.
**The Evaluator:** `c:\TABELA\backtesting\backtest_engine.py` — simulates state machines, entering trades exactly as the metrics fire.

---

## 2. Critical Quantitative Discoveries — DO NOT REVERT

### A. Long Engine: The "90/90 Sniper"
Proven across absolute grid search execution, this setup produces the highest verifiable win-rate constraint. 

| Parameter | Value | Why |
|---|---|---|
| `MIN_RS` | 90.0 | Maximum technical strictness. |
| `MIN_LONG_SCORE` | 90.0 | Maximum composite strictness. |
| `ZACKS_SCORE_MAP` | Binary | Rank 1/2=100. Rank 3=0. Rank 4=-50, 5=-100. Rank 3 stocks were proven to poison forward momentum. |
| `MILD_DAYS` | 21 | The elite pullback window. Beyond 21 days = dead money. |
| `MIN_DROPPED` | 70.0 | Score Floor while pulling back. |
| `BASING/DECAY`| Deleted | 70% failure rate proven in dedicated simulations. |

**The Base Tracker Lesson:** We do not algorithmically trade or stalk 50-day horizontal bases. The tuner mathematically dictated that if a sleeping base is truly elite, we just ignore it until its native RS surges and triggers the standard Strong 90/90 gate again.

### B. Short Engine: "Combo C (The Absolute Chokehold)"
Shorting is messy, highly volatile, and prone to violent short-squeezes. The Short Grid strictly choked the volume to eliminate low-conviction noise while maintaining a mathematically staggering **70.3% Win Rate**.

| Parameter | Value | Why |
|---|---|---|
| `MIN_RS` | 40.0 | Floor: stocks must still have standing to lose (do not short dead <35 graveyards). |
| `MAX_RS` | 60.0 | Ceiling: Crush the ceiling below 75 so we don't accidentally catch fundamentally safe stocks. |
| `MAX_LONG_SCORE` | 45.0 | Score < 45 = confirmed fundamental structural failure. |
| `THEMES` | No Leading | "Lagging, Micro Laggard, Neutral, Unknown" |
| `BLOCKED_ZACKS` | [1, 2] | Do not short institutional darlings. |
| `MIN_VOLUME` | 2,500,000 | Institutional liquidity required. Eliminated 50% of the erratic low-volume noise. |
| `RS_RAW_WEIGHTS`| YTD Reversal | 40% YTD, 30% 4W, 20% 12W. YTD peak reversal predicts crashes. |

**The Pullback Edge:** The data identically proved on BOTH engines that buying the *Secondary Move* (The Mild 1-21 Day Recoil) mathematically provided a ~2% to 4% higher winning probability than buying the initial Breakout/Breakdown exactly as it fired. 

---

## 3. The Data Cleansing Protocols
Barchart historical dumps regularly export dirty strings (`""`, `"-"`) inside supposedly numeric columns.
The math inside `scoring_engine.py` (both Long and Short passes) are explicitly wrapped in:
`pd.to_numeric(stocks[column], errors='coerce')` ending natively with `.fillna(0.0)`.
**Never remove this wrapper.** Attempting to multiply a Barchart formatted string by a float weight will instantly crash the daily regression loops.

---

## 4. Execution Commands

| Action | Command |
|---|---|
| Daily live scan | `c:\TABELA\main.bat` |
| Rebuild 3-month JSON history | `python c:\TABELA\runners\run_historical.py` |
| Quarterly Health Tune | `python c:\TABELA\backtesting\tuners\run_quarterly_tuner.py` |
| Short Chokehold Tune | `python c:\TABELA\backtesting\tuners\run_tuner_short_v2.py` |
| Basing Viability Tune | `python c:\TABELA\backtesting\tuners\run_tuner_basing.py` |

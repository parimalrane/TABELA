# TABELA Backtesting & Optimization: Master Handover Document

**Last Updated:** Oct 2, 2026
**Target Audience:** Future LLMs, AI Agents, or developers taking over the TABELA codebase.
**Purpose:** This document contains the distilled, institutional knowledge of the TABELA quantitative backtesting suite. Read this thoroughly before suggesting *any* modifications to the scoring engine, configuration, or short/long logic.


---

## 1. Project Overview & Architecture

TABELA is an institutional-grade, multi-dimensional momentum stock screener utilizing a strict 4-tier trading setup:
- **Strong Bullish** (Trend Continuation) — High-conviction trend breakouts (RS 85+, Score 85+, Leading/Neutral themes). Market entry.
- **Mild Bullish** (Watch For Pullback Setup) — Structural leaders temporarily decoupling (RS < 85 but > 70). Buy-the-dip window after 8-21 day Fibonacci cooldown.
- **Strong Bearish** (Trend Breakdown) — Structural trend breakdowns targeting the True Mid tier (RS 30-60). Market short entry.
- **Mild Bearish** (Watch For Relief Rally Fade) — Dead-cat bounces in structural laggards. Wait 3-8 days for relief momentum to exhaust, then short.

**The Brain:** `c:\TABELA\config\config.py` — all weights, thresholds, and scoring maps.
**The Memory:** `c:\TABELA\lifecycle\stock_transition_engine.py` — tracks how many days a stock has been in each state. Saves to `c:\TABELA\market_data\stock_transition\`.
**The Scorer:** `c:\TABELA\scoring\scoring_engine.py` — computes both `Long_Score` and `Short_Score` per stock.
**The History:** `c:\TABELA\data_layer\stock_history_engine.py` — saves daily JSON per stock including `long_score`, `short_score`, `rs_rating`, `short_rs_rating`, `avg_volume`, `last_close`.
**The Evaluator:** `c:\TABELA\backtesting\backtest_engine.py` — evaluates the ruleset over a 3-month hold period.

---

## 2. Unified Quarterly Super-Cycle Suite

The `run_quarterly_tuner.py` is now a fully autonomous Phase 1-4 super-cycle. It completely abstracts away manual grid testing, config updating, and regression.

```
c:\TABELA\backtesting\
    backtest_engine.py              ← Unified daily evaluating engine (long + short modes)
    tuners\
        run_quarterly_tuner.py      ← Master unified suite (Phase 1-4 Autonomous Orchestrator)
        run_tuner.py                ← Contains the 30 active Long test cases (invoked by master)
        run_tuner_short_v2.py       ← Contains the 14 active Shorts test cases (invoked by master)
    attribution\
        run_alpha_attribution.py    ← Fundamental edge harvester (invoked by master)
        run_pullback_tuner.py       ← Fibonacci MFE wait-time calculator (invoked by master)
    results\
        master_execution_log.txt    ← Final printout log of the Quarterly Cycle
```

---

## 3. Running the Backtesting Engine

**Evaluate current Long config performance (3-month hold):**
```cmd
python c:\TABELA\backtesting\backtest_engine.py long
```

**Evaluate current Short config performance (3-month hold):**
```cmd
python c:\TABELA\backtesting\backtest_engine.py short
```

**Full Unified Quarterly Optimization (Automatically iterates all 44 Long/Short tests):**
```cmd
python c:\TABELA\backtesting\tuners\run_quarterly_tuner.py
```
*Note: You must run this once a quarter to capture shifting market dynamics. Once complete, manually transfer the grid search winner parameters into `config.py` and run `regression.bat`.*

---

## 4. Critical Quantitative Discoveries — Q4 2026 Lock

### A. Long Engine: "Zacks: Pure Binary"
Proven as the ultimate strategy across 30 grid search experiments:

| Parameter | Value | Why |
|---|---|---|
| `MIN_RS` | 85.0 | Widened from 90 to allow earlier fundamental setups |
| `MIN_LONG_SCORE` | 85.0 | Matches widened RS gate |
| `ZACKS_SCORE_MAP` | Binary: 1/2=100, 3=0, 4=-50, 5=-100 | The engine mathematically proved that "Zacks: Pure Binary" is the golden standard. The market doesn't care about nuanced earnings. Either Rank 1-2 (Buy) or fail. |
| `MIN_DROPPED_WATCH_SCORE`| 70.0 | The Mild Bullish transition threshold |

**Alpha Differential Fingerprints (Why the winners win):**
*   **Modest Growth Beats Hyper Growth:** Winners averaged 12% sales growth. Losers averaged 30%. The street ruthlessly punishes hyper-growth names that fail whisper numbers. Target steady foundation builders.
*   **Deeper Bases:** The best breakouts occur when the price is ~78% of the 52-week high, not scraping the absolute 99% ceiling (where losers clustered).
*   **Sector Density:** "Internet - Software" was responsible for ~23% of the entire system's Long win rate.

### B. Short Engine: "P3-D: Slow Bleed + Theme Heavy + True Mid Wide"
Proven via multi-dimensional short grid testing:

| Parameter | Value | Why |
|---|---|---|
| `MIN_SHORT_RS` | 30.0 | **True Mid Tier:** The system proved that shorting absolute bottom graveyards (RS < 10) gets you killed on dead-cat bounces. The sweet spot is RS 30-60. |
| `MAX_SHORT_RS` | 60.0 | Ceiling: Ensures stock has structurally decayed out of leadership. |
| `SHORT_COMPOSITE_WEIGHTS` | RS: 40%, Theme: 40%, Zacks: 15%, Growth: 5% | Heavy Theme weighting combined with heavy RS confirms macro capital flight. |
| `SHORT_RS_RAW_WEIGHTS`| 12W = 0.7 | Highly emphasizes 12-week Slow Bleeds over 1-week cliff dives. |

### C. Fibonacci Pullback Timing (Mild Bullish)
The MFE (Maximum Favorable Excursion) engine mathematically calculated the exact optimal wait times for buying a "Mild Bullish" dropped long:
*   Wait **2 Days**: +0.98% return
*   Wait **8 Days**: +5.07% return
*   Wait **13-21 Days**: +7% to +9% return
**Rule:** When a leader drops into Mild Bullish, lock the crosshairs but wait. Allow the 8-to-13-day Fibonacci cooldown to exhaust weak hands before entering.

---

## 5. The Two-Scoring-Engine Architecture (Key Concept)

The pipeline runs **two completely independent scoring passes** per stock every day:

```
Daily CSV Input
     │
     ├──► Long Scoring Engine ──► Long_Score, RS_Rating   (used by watchlist_engine.py)
     │
     └──► Short Scoring Engine ──► Short_Score, Short_RS_Rating  (used by distribution_engine.py)
```

Both scores are saved to the daily JSON. The Long and Short engines use entirely separate weight maps from `config.py`. **Changing `SHORT_*` variables has zero impact on Long output.**

---

## 6. Operational Rules for Future AI Agents

1. **Sandbox Principle:** Any tuner script MUST `shutil.copy2` backup `config.py` at start and restore it at exit — even if an exception occurs. Never leave `config.py` mutated.

2. **The Regression Rule:** After any permanent `config.py` change, ALWAYS run `c:\TABELA\regression.bat` to rebuild 3 months of JSON history. Without this, the JSON state will be misaligned with the new config.

3. **Minimum Trade Threshold:** A backtest result with fewer than 100 trades over 3 months is statistically unreliable. Do not recommend a config change based on thin samples.

4. **Do NOT touch the Long engine** unless win rate drops significantly below 50% in a quarterly health check. It is at its mathematically proven optimum for the current dataset.

5. **Quarterly Schedule:** Next optimization run is **December 31, 2026**.

---

## 7. Execution Commands

| Action | Command |
|---|---|
| Daily live scan | `c:\TABELA\runners\main.py` |
| Rebuild 3-month JSON history | `c:\TABELA\runners\run_historical.py` |
| Quarterly health check (Long) | `python c:\TABELA\backtesting\backtest_engine.py long` |
| Quarterly health check (Short) | `python c:\TABELA\backtesting\backtest_engine.py short` |
| **Fully Autonomous Quarterly Re-tune** | `python c:\TABELA\backtesting\tuners\run_quarterly_tuner.py` |

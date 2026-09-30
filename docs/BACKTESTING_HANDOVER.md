# TABELA Backtesting & Optimization: Master Handover Document

**Last Updated:** Sep 30, 2026
**Target Audience:** Future LLMs, AI Agents, or developers taking over the TABELA codebase.
**Purpose:** This document contains the distilled, institutional knowledge of the TABELA quantitative backtesting suite. Read this thoroughly before suggesting *any* modifications to the scoring engine, configuration, or short/long logic.

---

## 1. Project Overview & Architecture

TABELA is an institutional-grade, multi-dimensional momentum stock screener. It identifies:
- **Long candidates** — High-conviction breakout stocks (RS 90+, Score 90+, Leading/Neutral themes)
- **Short candidates** — "Fall From Grace" breakdowns (RS 50-75, Score < 50, Neutral themes actively losing momentum)

**The Brain:** `c:\TABELA\config\config.py` — all weights, thresholds, and scoring maps.
**The Memory:** `c:\TABELA\lifecycle\stock_transition_engine.py` — tracks how many days a stock has been in each state. Saves to `c:\TABELA\market_data\stock_transition\`.
**The Scorer:** `c:\TABELA\scoring\scoring_engine.py` — computes both `Long_Score` and `Short_Score` per stock.
**The History:** `c:\TABELA\data_layer\stock_history_engine.py` — saves daily JSON per stock including `long_score`, `short_score`, `rs_rating`, `short_rs_rating`, `avg_volume`, `last_close`.
**The Evaluator:** `c:\TABELA\backtesting\backtest_engine.py` — evaluates the ruleset over a 3-month hold period.

---

## 2. Backtesting Directory Structure

```
c:\TABELA\backtesting\
    backtest_engine.py              ← Unified engine (long + short modes)
    run_quarterly_optimization.py   ← Master script to run all tuners + merge CSVs
    tuners\
        run_tuner.py                ← Phase 1: Long engine RS/Score grid
        run_tuner_phase2.py         ← Phase 2: Long composite weight combos
        run_tuner_phase3.py         ← Phase 3: Zacks Binary + Growth curve combos
        run_tuner_short.py          ← Original short gate grid (deprecated, superseded by v2)
        run_tuner_short_floor.py    ← Short RS floor test (graveyard avoidance)
        run_tuner_short_v2.py       ← Multi-dimensional short scoring grid (14 experiments)
        run_tuner_short_phase2.py   ← Theme precision + score tightening grid (8 experiments)
        run_baseline_short_p3c.py   ← Single-run baseline with full trade detail CSV output
    results\
        master_optimization_results_20260930.csv   ← All Phase 1-3 long results merged
        optimization_results_short_v2_20260930.csv ← Short scoring grid results
        optimization_results_short_phase2_20260930.csv ← Phase 2 tightening results
        short_trade_detail_20260930.csv            ← Trade-level detail (winner anatomy)
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

**Run trade-level detail for Short (generates CSV with every trade, Win/Loss, Return%):**
```cmd
python c:\TABELA\backtesting\tuners\run_baseline_short_p3c.py
```

**Full quarterly optimization (all tuners + auto-merge results):**
```cmd
python c:\TABELA\backtesting\run_quarterly_optimization.py
```

---

## 4. Critical Quantitative Discoveries — DO NOT REVERT

### A. Long Engine: The "Sniper" Configuration
Proven across 60+ grid search experiments:

| Parameter | Value | Why |
|---|---|---|
| `MIN_RS` | 90.0 | 90/90 gate = 53.97% WR, +2.58% avg return, 126 trades |
| `MIN_LONG_SCORE` | 90.0 | Same gate, proven optimal |
| `ZACKS_SCORE_MAP` | Binary: 1/2=100, 3=0, 4=-50, 5=-100 | Rank 3 "Hold" stocks are statistically poisonous to momentum |
| `BLOCKED_ZACKS` | [4, 5] | Hard block on confirmed sells |
| `MIN_PRICE` | $10.00 | Kill penny stock noise |
| `MIN_VOLUME` | 300,000 | Kill illiquid traps |

**The Genius of Zacks Binary:** Because Zacks carries 15% weight, a Rank 3 score of `0` caps a stock's maximum possible Long_Score at `85.0`. Since the gate is `90.0`, Rank 3 stocks are automatically eliminated without needing to be in `BLOCKED_ZACKS`.

### B. Short Engine: The "Fall From Grace" Configuration
Proven across 22+ targeted experiments in 2 phases:

| Parameter | Value | Why |
|---|---|---|
| `MIN_SHORT_RS` | 50.0 | Floor: must have had standing to lose (no graveyards) |
| `MAX_SHORT_RS` | 75.0 | Ceiling: catch before collapse becomes obvious |
| `MAX_SHORT_SCORE` | 50.0 | Score < 50 = confirmed breakdown conviction |
| `THEMES` | Neutral, Unknown | Lagging stocks at RS 50-75 add noise, not signal |
| `MIN_PRICE` | $10.00 | Never short penny stocks |
| `MIN_VOLUME` | 1,000,000 | Institutional liquidity required (borrow availability) |
| `SHORT_RS_RAW_WEIGHTS` | YTD: 40%, 4W: 30%, 12W: 20%, 1W: 10% | YTD reversal = peak-to-trough momentum |
| `SHORT_COMPOSITE_WEIGHTS` | RS: 65%, Theme: 20%, Zacks: 10%, Growth: 5% | Technicals dominate for shorts |

**Final short performance:** 73.28% Win Rate | +5.16% avg return | ~11 stocks/day

**Critical: The Short RS Rating is computed separately** using `SHORT_RS_RAW_WEIGHTS` in `scoring_engine.py → calculate_short_score()`. It is stored as `short_score` and `short_rs_rating` in the daily JSON. The Long engine columns are never touched.

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
| Daily live scan | `c:\TABELA\main.bat` |
| Rebuild 3-month JSON history | `c:\TABELA\regression.bat` |
| Quarterly health check (Long) | `python c:\TABELA\backtesting\backtest_engine.py long` |
| Quarterly health check (Short) | `python c:\TABELA\backtesting\backtest_engine.py short` |
| Short trade anatomy detail | `python c:\TABELA\backtesting\tuners\run_baseline_short_p3c.py` |
| Full quarterly re-tune | `python c:\TABELA\backtesting\run_quarterly_optimization.py` |

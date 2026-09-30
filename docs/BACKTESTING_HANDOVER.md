# TABELA Backtesting & Optimization: Master Handover Document

**Target Audience:** Future LLMs, AI Agents, or developers taking over the TABELA code base.
**Purpose:** This document contains the distilled, institutional knowledge of the TABELA quantitative backtesting suite. Read this thoroughly before suggesting *any* modifications to the scoring engine, configuration, or shorting logic.

---

## 1. Project Overview & Architecture
TABELA is an institutional-grade, multi-dimensional momentum stock screener. It identifies high-conviction breakout candidates (Longs) and exhaustion breakdowns (Shorts/Distribution) using a blend of Momentum (RS Rating), Macro Sector Capital Flows (Theme Class), and Fundamental filters (Zacks Rank & Growth Grade).

**The Brain:** `c:\TABELA\config\config.py` controls all weights and thresholds.
**The Memory:** `c:\TABELA\lifecycle\stock_transition_engine.py` remembers how many days a stock has been breaking out or breaking down, saving states to local JSON files (`c:\TABELA\market_data\stock_transition\`).
**The Evaluator:** `c:\TABELA\backtesting\backtest_engine.py` evaluates the performance of the ruleset over a 3-month hold period.

---

## 2. The Backtesting Engine (c:\TABELA\backtesting\)
We built an automated, sandbox-safe grid search (Auto-Tuner) that programmatically mutates `config.py`, runs historical regressions, calculates backtest metrics, and restores the original config. 

### Key Files:
*   `backtest_engine.py`: The core calculator. 
    *   `python backtest_engine.py long` calculates standard profit (exit price > entry).
    *   `python backtest_engine.py short` calculates inverse profit (exit price < entry).
*   `run_quarterly_optimization.py`: A wrapper that executes all historical script experiments located in `\tuners\`, consolidates their CSV logs into a master sheet, and date-stamps it into `\results\`.
*   `tuners\run_tuner_*.py`: Historical grid-search experiments.

---

## 3. Critical Quantitative Discoveries (DO NOT REVERT THESE)
Through running over 70 rigorous grid-search experiments, we mathematically proved several laws about this dataset. If you are modifying the pipeline, you must respect these structural edge characteristics:

### A. The Long Engine (The "Sniper" Setup)
*   **The 90/90 Gate:** The optimal entry threshold is mathematically proven to be `MIN_RS: 90.0` and `MIN_LONG_SCORE: 90.0`. Do not loosen this without quantitative proof.
*   **Zacks Binary Map:** We proved that Zacks Rank 3 ("Hold") stocks are poisonous to momentum portfolios (high failure rate). We mapped `ZACKS_SCORE_MAP = {1: 100, 2: 100, 3: 0, 4: -50, 5: -100}`. 
    *   *The Genius Mechanism:* Because Zacks is 15% of the Composite Score, a `0` on Zacks caps a stock's total possible score at `85.0`. Therefore, a Rank 3 stock is automatically blocked from passing the 90.0 Gate without needing to be explicitly hardcoded into `BLOCKED_ZACKS`.
*   **Flat Growth:** We proved that applying a Fibonacci curve to Growth grades strangled too many valid trades. Growth remains a standard linear taper.

### B. The Short Engine (The "Goldilocks" Breakdown Zone)
*   **Catch Breakdowns Early:** We widened the short entry funnel (`MAX_RS: 15.0`, `MAX_LONG_SCORE: 25.0`). Shorting stocks immediately as they lose momentum yields a much higher win rate than waiting for them to collapse completely.
*   **The Terminal Oversold Floor:** We instituted `"MIN_RS": 8.0`. We proved that shorting stocks with an RS rating below 8 results in massive losses due to violent "Dead-Cat Bounces" (short squeezes). The Short Engine only targets stocks strictly within the `8.0 < RS < 15.0` window.

---

## 4. Operational Boundaries & Rules for Future AI

1. **Sandbox Principle for Testing:** If you build a new Tuner script or modify an existing one, you **must** use `shutil.copy2` to backup `config.py` at the script's start, and restore it at the script's exit (even if exceptions occur). Never leave the live `config.py` mutated.
2. **The "Regression" Rule:** If the user approves a permanent update to `config.py`, you **must** instruct the user to run `c:\TABELA\regression.bat` immediately. This sweeps historical CSVs and updates the JSON state memory so that live tracking logic matches the new math.
3. **Execution Commands:** 
    *   To evaluate live config performance: `python c:\TABELA\backtesting\backtest_engine.py long` (or `short`).
    *   To run the full suite for quarterly checkups: `python c:\TABELA\backtesting\run_quarterly_optimization.py`
    *   To run daily scans for live trading: `c:\TABELA\main.bat`

Read this document fully before responding to the user's prompt. You are now equipped with the institutional history of TABELA.

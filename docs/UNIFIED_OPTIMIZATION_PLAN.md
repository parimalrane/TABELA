# Unified Optimization Upgrade: Vectorized Backtest + Alpha Attribution

## Problem

The current quarterly tuner (`run_quarterly_tuner.py` → `run_tuner.py` → `run_historical.py`) has two fatal flaws:

1. **2-hour bottleneck:** For each of 30 experiments, it *overwrites `config.py`*, then calls `run_historical.py` which **deletes all JSON files** and re-runs the full pipeline from scratch for every single experiment. 30 experiments × ~4 minutes each = ~2 hours.

2. **Data corruption risk:** `run_historical.py` (lines 29-34) calls `os.remove()` on every JSON file in `market_data/` before regenerating them. If the process crashes mid-run, the historical data is destroyed.

3. **No attribution:** The current backtest collapses all trades into a single "Win Rate %" number with no visibility into *why* trades won or lost.

## Key Insight

The ~59 JSON files in `market_data/stock_universe/` already contain **every field needed** for backtesting: `rs_rating`, `long_score`, `short_score`, `theme_class`, `zacks_rank`, `last_close`, `avg_volume`, `sales_growth`, `operating_margin`, `theme_strength_score`, etc. We do NOT need to re-run the scoring pipeline to simulate the backtest. We only need to load these JSONs into a single Pandas DataFrame and run the state machine in RAM.

> [!IMPORTANT]
> **`config.py` will NOT be touched.** The new engine reads `config.py` once at startup for the production thresholds and then operates entirely in memory. Experiment overrides are injected as Python dicts, never written to disk.

---

## Proposed Changes

### Vectorized Backtest Engine

#### [NEW] [vectorized_backtest.py](file:///c:/TABELA/backtesting/vectorized_backtest.py)

A self-contained, read-only backtesting engine. Core architecture:

1. **Data Ingestion (one-time, ~3 seconds):**
   - Walks `market_data/stock_universe/` and reads all `*_stock_history.json` files
   - Walks `market_data/input_files/` and reads all `*_stocks.csv` files (for price lookup)
   - Builds a single Pandas DataFrame (`master_matrix`) indexed by `(scan_date, ticker)` with columns: `rs_rating`, `long_score`, `short_score`, `theme_class`, `zacks_rank`, `last_close`, `avg_volume`, `sales_growth`, `operating_margin`, `theme_strength_score`, etc.
   - This matrix is built ONCE and reused across ALL experiments

2. **Vectorized State Machine:**
   - Replicates the exact logic from `backtest_engine.py` (Strong → Dropped → Mild → Basing → Purged) but operates on the pre-built DataFrame
   - For each experiment, overrides are applied as in-memory dict substitutions (thresholds, score weights, etc.)
   - Returns a `trades_df` DataFrame with one row per triggered trade, including all entry characteristics

3. **Zero File I/O:**
   - Never writes to disk
   - Never modifies `config.py`
   - Never deletes or modifies any JSON files
   - All experiment parameter overrides are applied as in-memory Python variables

Key function: `run_vectorized_backtest(matrix, overrides=None, mode="long", silent=False)` → returns `result_dict` with `_detail_df` (identical schema to current `backtest_engine.py` output, plus enriched columns for attribution).

---

### Alpha Attribution Engine

#### [NEW] [alpha_attribution.py](file:///c:/TABELA/backtesting/attribution/alpha_attribution.py)

Replaces the current `run_alpha_attribution.py` which does slow row-by-row CSV lookups. The new engine:

1. **Receives the `trades_df`** directly from the vectorized backtest (no re-running the backtest, no CSV re-parsing)
2. **Slices into Winners vs. Losers** cohorts
3. **Produces the "Winners vs. Losers" Characteristics Report:**

| Dimension | Analysis |
|---|---|
| **RS Rating** | Median, distribution, "% with RS > 95" for each cohort |
| **Theme Class** | Density distribution (e.g., "75% of losers were in Lagging themes") |
| **Zacks Rank** | Concentration (e.g., "82% of winners had Rank 1-2") |
| **Sales Growth** | Mean/median comparison |
| **Operating Margin** | Mean/median comparison |
| **Price (Entry)** | Distribution by price bucket |
| **Volume** | Avg daily volume distribution |
| **Theme Strength Score** | Mean/median comparison |
| **52W Position** | How close to 52-week high at entry |

4. **Saves report** as CSV + prints formatted terminal summary
5. **Returns the raw analysis DataFrame** so the user can investigate further

---

### Unified Runner

#### [NEW] [run_vectorized_tuner.py](file:///c:/TABELA/backtesting/tuners/run_vectorized_tuner.py)

Replaces `run_quarterly_tuner.py` as the new entry point. Architecture:

1. Builds the master matrix ONCE (~3 seconds)
2. Loops through all 30 Long experiments from `run_tuner.py` EXPERIMENTS list
3. For each experiment, calls `run_vectorized_backtest(matrix, overrides=exp)` — no file I/O, no subprocess spawn
4. After all experiments complete, runs Alpha Attribution on the production config's trades
5. Saves:
   - `backtesting/results/vectorized_optimization_results.csv` (experiment comparison)
   - `backtesting/results/alpha_attribution_report.csv` (winners vs. losers)
   - Terminal printout of both reports

> [!NOTE]
> The existing files (`run_tuner.py`, `run_quarterly_tuner.py`, `run_alpha_attribution.py`, `backtest_engine.py`) will **not be modified or deleted**. The new files exist alongside them. The user can switch to the new engine at any time.

---

## Files NOT Modified

| File | Reason |
|---|---|
| `config/config.py` | **LOCKED. Sacred. Never touched.** |
| `backtesting/backtest_engine.py` | Legacy engine preserved for reference |
| `backtesting/tuners/run_tuner.py` | Experiment definitions reused, file not modified |
| `backtesting/tuners/run_quarterly_tuner.py` | Legacy orchestrator preserved |
| `backtesting/attribution/run_alpha_attribution.py` | Legacy attribution preserved |
| `scoring/scoring_engine.py` | Not touched |
| `market_data/*` | Read-only. Never written to. |

---

## Verification Plan

### Automated Validation

1. **Run the vectorized backtest** with production config thresholds and compare output to the current `backtest_engine.py`:
   ```bat
   python c:\TABELA\backtesting\tuners\run_vectorized_tuner.py
   ```
   - Verify trade count, win rate, and avg return match the legacy engine's numbers (within floating-point tolerance)
   - The script will print a side-by-side comparison

2. **Run the alpha attribution report** and verify it produces a non-empty Winners vs. Losers table with all expected dimensions

### Manual Verification (by user)

1. Review the terminal output showing experiment comparison table
2. Review the Winners vs. Losers report to confirm the characteristics make intuitive sense
3. Compare the top-line numbers (WR%, Avg Return) from the vectorized engine against known historical results from `master_optimization_results_20260930.csv`

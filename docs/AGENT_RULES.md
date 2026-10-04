# TABELA — Agent Operating Rules
**Last Updated:** October 4, 2026  
**Audience:** Any LLM agent, coding assistant, or AI pair programmer working on this codebase.  
**Purpose:** Strict rules of engagement to prevent regressions and unauthorized parameter changes.

---

> [!CAUTION]
> **READ THIS ENTIRE DOCUMENT BEFORE TOUCHING ANY FILE.**  
> Violations of these rules have historically caused multi-session debugging marathons, destroyed backtested parameter sets, and produced mathematically invalid pipeline outputs.

---

## Rule 1: config.py is Sacred

`c:\TABELA\config\config.py` contains the **exact mathematical outputs of multi-hour grid-search backtests**. Every number in this file was earned through quantitative regression across 3+ months of real market data.

### You Are Forbidden From:
- Changing any threshold (e.g., `MIN_RS`, `MAX_SHORT_SCORE`, `MILD_DAYS`, `MIN_VOLUME`) to "fix" a display issue
- Changing any threshold to "resolve a conflict" between two parameters
- Changing any threshold because the output list appears empty
- Changing any threshold because you think a different value "makes more sense"

### The Only Correct Process:
1. Identify the suspected misconfiguration
2. **Explain the math** — show the user exactly why you believe the value is wrong
3. **Wait for explicit human authorization** (the user must say "go ahead" or "approved")
4. Make exactly the approved change, nothing else
5. Confirm the diff matches what was approved

---

## Rule 2: Never Change config.py During Backtesting

The in-memory backtest engine (`run_cartesian_long.py`, `run_cartesian_short.py`) injects parameters directly into RAM at runtime. It reads `config.py` once at startup for structural references, then operates entirely in memory.

**You must never modify `config.py` as part of a backtesting loop or experiment.**  
The correct workflow is:
```
Backtest → Report → Human Reviews → Human Approves → config.py Updated
```

---

## Rule 3: Do Not Confuse "Display Bug" with "Config Bug"

If the terminal shows "0 Longs" or an empty Mild Bearish list, **this is almost always mathematically correct** given the current parameters. Resist the urge to "fix" it by lowering thresholds.

**Before assuming it is a bug, ask:**
- Is the RS or Score threshold simply not being met by any stock today?
- Is the Mild waitlist empty because no stocks have exited the Strong list recently?
- Has the pipeline been running with these parameters for fewer days than `MILD_DAYS`?

Only after ruling out mathematical correctness should you investigate code logic.

---

## Rule 4: Backtesting Engine Architecture (What You Can and Cannot Do)

### You CAN modify freely:
- `run_cartesian_long.py` — the Cartesian grid axes and scenarios
- `run_cartesian_short.py` — the Cartesian grid axes and scenarios
- Any file under `backtesting/tuners/`
- Any file under `scripts/`
- Any file under `docs/`

### You MUST get approval to modify:
- `config/config.py` — The quantitative configuration bible
- `backtesting/backtest_engine.py` — The core state machine (changes here invalidate all historical results)
- `scoring/scoring_engine.py` — The composite score formula
- `lifecycle/stock_transition_engine.py` — The live pipeline state machine

### You MUST NOT modify:
- Any file under `market_data/` — This is historical data, not code
- Any existing `_stock_history.json` or `_registry.json` files

---

## Rule 5: One Change at a Time

When the user approves a config change, make **exactly one change** and stop. Then confirm the diff. Only proceed to the next change after the user reviews and approves.

Do not bundle multiple config changes into a single edit even if they seem logically related.

---

## Rule 6: Backtesting Report First, Config Second

The correct order of operations is always:

```
1. Run the Cartesian backtest
2. Present the top results in plain language (Win Rate, Avg Return, Trade Count)
3. Explain the winning parameters and why they won
4. Wait for user to say "deploy" or "go ahead"
5. Update config.py with exactly the winning parameters
```

**Never update config.py and then run the backtest to "confirm."** The backtest must come first.

---

## Rule 7: The Approved Method for Proposing Config Changes

When presenting a config change for approval, always format it as:

```
Proposed Change:
- Parameter: MAX_SHORT_SCORE
- Current Value: 45.0
- Proposed Value: 65.0
- Source: optimization_results_short_v2_20261002.csv, Experiment P1-F (71.11% WR)
- Reason: [explain the mathematical justification]

Awaiting your authorization to proceed.
```

---

## Rule 8: The "Empty List" is Not Always Wrong

| Observation | What It Means |
|---|---|
| 0 Strong Longs today | No stocks cleared the 90/90 gate. Correct behavior. |
| 0 Mild Longs today | No 90/90 stocks have pulled back recently. Correct behavior. |
| 0 Mild Shorts today | Either the Mild window has just started, or all short bounces exceeded the ceiling. |
| `W_Brdth = 0.00` | No stocks meet the internal breadth qualifier (RS ≥ 90 AND Score ≥ 90). Correct behavior. |

Always check if the "empty" result is mathematically correct before treating it as a bug.

---

## Rule 9: How to Run a Full System Check

If you are a new agent taking over this system, execute in this order:

```bat
# Step 1: Verify the live pipeline works
main.bat

# Step 2: Verify the Long Cartesian tuner works
python run_cartesian_long.py

# Step 3: Verify the Short Cartesian tuner works
python run_cartesian_short.py

# Step 4: Review the results in backtesting/results/
# Step 5: Present findings to the user
# Step 6: Await authorization before any config.py changes
```

---

## Rule 10: Key Backtesting Discoveries — Never Regress These

These results took multiple sessions of 2–3 hour regressions to discover. Do not undo them without running a new backtest that mathematically disproves them.

| Discovery | Proven Result | File |
|---|---|---|
| 90/90 gate is optimal for Long | 44.58% WR, +0.95% avg | `master_optimization_results_20260930.csv` |
| Volume 1.5M eliminates retail whipsaw | Significant WR lift over 300K | `cartesian_mild_long.csv` |
| 21-day mild expiry beats 50-day | Dead money beyond Day 21 | `optimization_results_basing_20261003.csv` |
| P1-F beats Combo C for short | 71.11% vs 70.33% WR | `optimization_results_short_v2_20261002.csv` |
| Mild bounce ceiling 75.0 is optimal | Best Mild WR, avoids reversals | `cartesian_mild_short.csv` |
| 50-day basing = dead money | 70%+ failure rate | `optimization_results_basing_20261003.csv` |

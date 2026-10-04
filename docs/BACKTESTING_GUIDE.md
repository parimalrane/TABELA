# TABELA Backtesting Engine — Complete Guide
**Last Updated:** October 4, 2026  
**Audience:** New developers, LLM agents, or any person taking this system forward.  
**Purpose:** One-stop guide to run, design, and extend the backtesting engine.

---

## 1. The Golden Rule

> [!CAUTION]
> **`config.py` is immutable during backtesting.**  
> The backtesting engine runs experiments by injecting parameters directly into memory.  
> It **never** writes to `config.py`. Only a human with full context may update `config.py`  
> after explicitly reviewing and approving a backtest report.

---

## 2. What the Backtesting Engine Does

The TABELA backtesting engine replays historical daily stock data (stored as JSON snapshots in `market_data/stock_universe/`) against various parameter combinations to determine which scoring thresholds produce the best **win rate** and **average return** for both Long and Short trade ideas.

It answers the question:  
**"Given the historical data we already have, which exact parameter combination produces the highest-probability swing trade ideas?"**

---

## 3. One-Click Execution

### Run Long Cartesian Sweep (in-memory, ~2 min)
```bat
python c:\TABELA\run_cartesian_long.py
```
Output: `c:\TABELA\backtesting\results\cartesian_mild_long.csv`

### Run Short Cartesian Sweep (in-memory, ~2 min)
```bat
python c:\TABELA\run_cartesian_short.py
```
Output: `c:\TABELA\backtesting\results\cartesian_mild_short.csv`

### Run Full Long Quarterly Grid (slow, ~2 hours, all formulas)
```bat
python c:\TABELA\backtesting\tuners\run_quarterly_tuner.py
```
Output: `c:\TABELA\backtesting\results\master_optimization_results_YYYYMMDD.csv`

### Run Full Short Grid (slow, ~2 hours, all formulas)
```bat
python c:\TABELA\backtesting\tuners\run_tuner_short_v2.py
```
Output: `c:\TABELA\backtesting\results\optimization_results_short_v2_YYYYMMDD.csv`

---

## 4. Architecture: In-Memory Cartesian Engine (Fast Path)

The fast-path tuners (`run_cartesian_long.py`, `run_cartesian_short.py`) use a revolutionary in-memory architecture to avoid the multi-hour disk-write loops of the legacy tuners.

```
Step 1: Load ALL daily JSON snapshots into RAM (once)
Step 2: Load ALL daily price CSVs into RAM (once)
Step 3: Generate Cartesian product of all parameter axes
Step 4: For each permutation, simulate the full state machine in RAM
Step 5: Collect results into a DataFrame
Step 6: Rank by Mild WR% (then Strong WR%), write top-N to CSV
```

**Key Design Principle:** No file I/O occurs inside the experiment loop. All state transitions are computed entirely in Python dictionaries held in memory. This reduces 288 experiments from ~5 hours down to ~2-3 minutes.

---

## 5. How to Design a Cartesian Grid

Each grid is defined by a set of **parameter axes**. The engine takes the product of all axes automatically via `itertools.product`.

### Long Engine Axes (current production grid)
| Axis | Current Values | Description |
|---|---|---|
| `MIN_RS / MIN_SCORE` (Gate) | `(90,90), (90,85)` | RS and composite score entry gate |
| `MIN_VOLUME` | `300K, 1.5M` | Institutional liquidity floor |
| `BLOCKED_ZACKS` | `[4,5], [3,4,5]` | Fundamental quality filter |
| `MILD_FLOOR` | `70.0, 80.0` | Waitlist drop floor |
| `MILD_DAYS` | `14, 21, 35, 50` | Waitlist expiry in trading days |

### Short Engine Axes (current production grid)
| Axis | Current Values | Description |
|---|---|---|
| `MAX_SCORE` | `35.0, 40.0, 45.0, 50.0` | Max composite score (active breakdown entry) |
| `MAX_RS` | `60.0, 75.0` | Max RS (ceiling above which stock is not yet broken) |
| `BLOCKED_ZACKS` | `[1,2], [1,2,3]` | Block institutional darlings from short list |
| `MIN_VOLUME` | `1M, 2.5M, 3M` | Institutional liquidity floor |
| `MILD_FLOOR` | `65.0, 75.0, 85.0` | Bounce ceiling for relief rally tracking |
| `THEMES` | Strict (2), Wide (4) | Theme classification filter |

### Adding a New Axis
1. Open `run_cartesian_long.py` or `run_cartesian_short.py`.
2. Add a new list to the `grid_*` variables section in `main()`.
3. Add the new list to the `itertools.product(...)` call.
4. Add the new variable to the `scenario` dict inside the loop.
5. Add logic in `run_scenario()` to consume the new parameter.

---

## 6. How to Read the Output Report

The output CSV ranks permutations from best to worst. Key columns:

| Column | Meaning |
|---|---|
| `Str.WR%` | Win rate of initial Strong breakout/breakdown entries |
| `Str.Trd` | Number of Strong entries (lower = higher conviction) |
| `Mil.WR%` | Win rate of Mild pullback/relief-rally secondary entries |
| `Mil.Trd` | Number of Mild entries |
| `Avg%` | Average return across all trades |
| `MILD_FLOOR` | The bounce ceiling that held — the key waitlist parameter |

**What to look for:** The ideal row has **high `Mil.WR%`** with **low `Mil.Trd`** — this is the "Low Volume / High Probability" sweet spot.

---

## 7. Decision Workflow (Human + LLM Review Process)

```
1. Run Cartesian sweep
2. LLM reads the output CSV and presents Top 3 winners
3. Human reviews the parameters in context of current market conditions
4. Human explicitly says "deploy [X] parameters"
5. LLM updates config.py exactly once, with exactly those parameters
6. Confirm config.py diff matches the approved values
7. Run main.bat for live trading
```

> [!WARNING]
> **Step 4 requires explicit human authorization.** An LLM agent must never skip to Step 5 on its own judgement, even if the winning combination is "obvious."

---

## 8. What Variables Can Be Backtested

These are the variables the in-memory engine can sweep without rebuilding historical data:

### Entry Gates
- `MIN_RS` / `MIN_LONG_SCORE` (Long) 
- `MIN_SHORT_RS` / `MAX_SHORT_RS` / `MAX_SHORT_SCORE` (Short)

### Fundamental Filters
- `BLOCKED_ZACKS` — Which Zacks ranks to exclude

### Liquidity Filters
- `MIN_VOLUME` — Minimum average daily volume
- `MIN_PRICE` — Minimum stock price

### Theme Filters
- `THEMES` — Which theme classifications are allowed (Long or Short)

### Waitlist / Mild State
- `MIN_DROPPED_WATCH_SCORE` / `MILD_FLOOR` — How far a pullback can go before the trade is considered dead
- `MILD_DAYS` — How many days to track a pullback before expiring it

### What CANNOT Be Backtested Without Rebuilding History
These require re-running `run_historical.py` (2+ hours) because they change the underlying daily score for every stock:
- `RS_RAW_WEIGHTS` (the formula for the RS Rating)
- `LONG_WEIGHTS` / `SHORT_COMPOSITE_WEIGHTS` (the composite score formula)
- `ZACKS_SCORE_MAP` / `GROWTH_SCORE_MAP` (the fundamental point values)
- `THEME_STRENGTH_CONFIG` (ETF weighting periods)

---

## 9. Key Files Reference

| File | Role |
|---|---|
| `config/config.py` | 🔒 Single source of truth for all parameters. Read-only during backtesting. |
| `backtesting/backtest_engine.py` | Core state machine: replays JSON history and evaluates trade returns |
| `run_cartesian_long.py` | In-memory Cartesian sweep for Long engine parameters |
| `run_cartesian_short.py` | In-memory Cartesian sweep for Short engine parameters |
| `backtesting/tuners/run_quarterly_tuner.py` | Full quarterly grid (slow, tests RS/Score formulas too) |
| `backtesting/tuners/run_tuner_short_v2.py` | Full short grid (slow, tests RS/Score formulas too) |
| `backtesting/results/` | All CSV output reports |
| `market_data/stock_universe/` | Historical daily JSON snapshots (the "training data") |
| `market_data/input_files/` | Historical daily price CSVs |
| `docs/BACKTESTING_HANDOVER.md` | Distilled knowledge from previous backtesting sessions |

---

## 10. The 4-Tier State Machine (What the Engine Simulates)

The backtest engine simulates the exact same 4-tier state machine as the live pipeline:

```
Tier 1: STRONG LONG    — RS >= 90, Score >= 90, Leading theme
Tier 2: MILD LONG      — Was Strong Long, now pulling back (Days 1–21)
Tier 3: STRONG SHORT   — RS 40–75, Score < 45, Lagging/Neutral theme
Tier 4: MILD SHORT     — Was Strong Short, now relief rallying (Days 1–50)
```

Each tier has its own independent win rate in the output CSV. The ideal configuration maximizes **Tier 2 (Mild Long)** and **Tier 4 (Mild Short)** win rates because the secondary move statistically provides ~2-4% higher win probability than the initial breakout/breakdown.

---

## 11. Proven Historical Results (Do Not Revert)

| Engine | Best Config | Win Rate | Key Insight |
|---|---|---|---|
| Long | 90/90 Gate, 1.5M Vol | 44.6–53.9% | Raising volume from 300K to 1.5M eliminates retail whipsaw |
| Short | P1-F (RS 40-75, Score < 65) | 71.1% WR, 4.31% avg | "Fall From Grace" zone far outperforms "Graveyard" zone |
| Short Mild | 75.0 bounce ceiling | Best Mild WR | Too tight (30.0) deletes trades; too loose (85.0) holds reversals |
| Basing/Decay | Deleted | N/A | 70%+ failure rate proven — never re-implement 50-day basing |

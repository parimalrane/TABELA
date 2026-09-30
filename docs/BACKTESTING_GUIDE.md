# TABELA Backtesting & Optimization Guide

## Architecture Overview
The backtesting suite was rigorously designed to mathematically determine the highest-conviction parameter setups for both the **LONG** and **SHORT (Distribution)** engines. The logic is now unified and securely organized within the `c:\TABELA\backtesting` folder.

**Objective:** Run this optimization protocol on a **Quarterly Schedule** (Next run Date: **Dec 31, 2026**) to ensure MACRO changes and fundamental shifts have not degraded the engine's edge over time.

---

## Directory Structure
Moved out of the project root to keep the workspace clean:
* `\backtesting\backtest_engine.py` - Single, combined engine supporting both `long` and `short` modes.
* `\backtesting\tuners\` - Historical grid-search scripts we used to prove the 90/90 gate and Zacks Binary setups.
* `\backtesting\results\` - Date-stamped `.csv` outputs.

---

## Running a Health Check Backtest (Quarterly)

If you simply want to test how the *current* live `config.py` performed over the last 3 months, run the unified backtest engine directly:

**Evaluate Long Engine Performance:**
```cmd
python c:\TABELA\backtesting\backtest_engine.py long
```

**Evaluate Short Engine Performance:**
```cmd
python c:\TABELA\backtesting\backtest_engine.py short
```
*Note: A positive return % on the Short test means the stock's price successfully dropped after entry.*

---

## Modifying or Tuning Parameters (Quarterly Workflow)

If the quarterly performance drops below expectations (e.g., win rate falls significantly below 50%), you will need to re-run the parameter Tuner grids to discover what Wall Street changed.

1. **Safety First:** The Tuner scripts internally backup your `config.py` before running tests, and automatically restore it when finished.
2. **Execute Tuner Grids:**
   ```cmd
   python c:\TABELA\backtesting\tuners\run_tuner_phase3.py
   ```
   *(You can run any of the historical tuners to sweep variables like Thresholds, Compound Weights, and Zacks Blocking).*
3. **Analyze CSV Log:** Look at `c:\TABELA\backtesting\results\optimization_results_[DATE].csv`. Find the configuration with the highest Win Rate, positive average profit, and a statistically relevant amount of Total Trades (>100).
4. **Update `config.py`:** Hardcode the newly discovered winning parameters into `c:\TABELA\config\config.py`.
5. **Re-Regression:** Crucially, after modifying `config.py`, you **must** run `c:\TABELA\regression.bat` to sweep historical tracking data so that your live local JSON history respects the new rules.

---

## Important Architectural Notes for New Models/Devs:

- **ZACKS BINARY:** We proved via 60+ experiments that Rank 3 ("Hold") stocks act as poison turnarounds. We manually force them to `0` in `config.py`.
- **SHORT OVERSOLD FLOOR:** Setting `MIN_RS = 8` on the short side prevents shorting stocks that are already terminally oversold, preventing massive short-squeeze losses.
- **STATISTICAL SAMPLE:** A 50% Win Rate loop that generates 4 trades in 3 months is bad data. The target minimum trade threshold to consider a combo "Valid" is ~100 trades over a 90-day backtest period.

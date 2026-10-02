# TABELA Quarterly Engine Autotuning Guide

## Overview
TABELA requires a periodic health-check and parameter optimization (grid search) to adapt to changing macro-economic conditions. This process is fully automated.

The **Quarterly Master Tuner** tests the pipeline mathematically. It brute-forces dozens of combinations of RS velocities (YTD vs 12W), ETF theme weighting (1M vs 3M flows), fundamental penalty curves (Zacks / Growth scores), and state-gate thresholds (85 vs 90) across 90 days of live market history.

By running this once per quarter, you guarantee that TABELA is using the mathematically optimal parameters to capture structural stock market shifts with maximum win rates and optimized average returns.

## How to Execute the Quarterly Optimization

### 1. Run the Tuner
Navigate to your main workspace terminal and execute the master suite:
```cmd
python backtesting\tuners\run_quarterly_tuner.py
```
This script will:
1. Back up your live `config.py` safely.
2. Execute **30 structured test cases** across the Long Engine.
3. Automatically run a 90-day regression and historical backtest on every test case.
4. Execute **14 structured test cases** across the Short Engine (using Phase 1 / Phase 3 configurations).
5. Restore your live `config.py` perfectly.

*Note: Execution takes approximately ~5-8 minutes total as it iterates over 44 separate 3-month regressions.*

### 2. Review the Output
Once the script completes, navigate to `backtesting\results\`. You will find the newly generated CSV files containing the master optimization matrices:
- `optimization_results.csv` (Long Engine)
- `optimization_results_short_v2_YYYYMMDD.csv` (Short Engine)

Open the CSVs and sort by **Win Rate (%)** and **Avg Return (%)**. Identify the "Winner" experiment.

### 3. Lock In The Winners
Once you've identified which test cases produced the highest institutional-grade performance:
1. Open `config\config.py`.
2. Update `LONG_ENTRY`, `DIST_ENTRY`, and the related `SHORT_*` weights to match the variables defined by your winning test.
3. Once the configs are saved, run:
```cmd
regression.bat
```
This single command re-runs the previous 3-months with your new locked-in rules, syncing your background state completely. Your daily run (`main.bat`) will now execute on the freshly optimized framework.

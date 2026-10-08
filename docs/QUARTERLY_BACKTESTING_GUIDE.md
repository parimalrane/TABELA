# TABELA Quarterly Engine Autotuning Guide

## Overview
TABELA requires a periodic health-check and parameter optimization (grid search) to adapt to changing macro-economic conditions. This process is fully automated.

The **Quarterly Master Tuner** tests the pipeline mathematically. It brute-forces dozens of combinations of RS velocities (YTD vs 12W), ETF theme weighting (1M vs 3M flows), fundamental penalty curves (Zacks / Growth scores), and state-gate thresholds (85 vs 90) across 90 days of live market history.

By running this once per quarter, you guarantee that TABELA is using the mathematically optimal parameters to capture structural stock market shifts with maximum win rates and optimized average returns.

## How to Execute the Quarterly Optimization

### 1. Run the Tuner
Navigate to your main workspace terminal and execute the master suite:
```cmd
backtesting\run_quarterly_backtest.bat
```
This script will automatically trigger two high-speed algorithms in sequence:
1. `run_quarterly_in_memory_tuner.py` (Long Matrix)
2. `run_quarterly_in_memory_tuner_short.py` (Short Matrix)

These algorithms use a highly optimized, fully in-memory pandas vectorized loop that completely bypasses legacy JSON I/O loading, testing the complete combinatorial math arrays specified within `backtesting\tuners\quarterly_grid_config.py`.

*Note: Due to the vectorized design, the multi-phase test sequence executes in under ~2 minutes, bypassing all production config files.*

### 2. Review the Output
Once the script completes, navigate to `backtesting\tuners\`. You will find the newly generated CSV files containing the master optimization matrices:
- `YYYYMMDD_quarterly_master_results.csv` (Long Engine)
- `YYYYMMDD_quarterly_short_master_results.csv` (Short Engine)

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

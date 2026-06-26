# TABELA User Guide

## What TABELA does

TABELA scans daily market data and produces a practical market-rotation view that highlights themes gaining institutional strength and stocks that align with those themes.

The workflow is:

1. Read daily ETF and stock data.
2. Filter and rank ETF themes.
3. Map stocks to themes.
4. Score each stock using momentum, theme strength, sales, analyst rank, and margin.
5. Produce long and short watchlists plus a rotation summary.

## Inputs

TABELA expects the following files in the market_data folder:

- ETF.csv
- stocks.csv

These files are read by the main pipeline each time the scan runs.

## How to run

From the project root:

```bash
python main.py
```

The script runs the full scan and prints the daily market report to the terminal.

## What you will see

When the run completes, TABELA prints:

- a theme rotation summary with Leading, Emerging, Weakening, and Lagging themes
- theme breadth analysis
- a long-candidate universe
- a short-candidate universe
- a TradingView-style watchlist export

The pipeline also saves supporting outputs under the market_data folders, including:

- snapshots
- rotation deltas
- stock history
- unknown emerging leader exports

## How to interpret the output

- Leading themes: strongest institutional themes for the day.
- Emerging themes: themes gaining traction.
- Weakening themes: themes losing momentum.
- Lagging themes: weakest themes in the current scan.

Long candidates are stocks that meet the long-side scoring and theme filters. Short candidates are stocks that fit the weakness-based short logic.

## Notes

- The main entrypoint is intentionally thin; most behavior lives in the pipeline and engine modules.
- The pipeline is designed to keep running even if optional intelligence outputs fail.
- If the output looks off, the first place to inspect is the current ETF and stock input files.

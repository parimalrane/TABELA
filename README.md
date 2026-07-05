# TABELA

TABELA is a market intelligence product focused on institutional capital rotation.
It analyzes ETF leadership, theme strength, and stock-level relative strength to surface long opportunities, identify weakening areas, and generate daily market reports.

## What It Does

- Runs a daily pipeline from `main.py`
- Tracks institutional rotation using ETF behavior as a proxy
- Scores long and short candidates using relative strength, theme alignment, sales, margins, and Zacks inputs
- Stores market snapshots, watchlist history, stock history, and daily text reports under `market_data`

## Project Structure

- `main.py` runs the pipeline and writes the daily report
- `core/` contains pipeline orchestration, configuration, theme logic, and stock mapping
- `engines/` contains scoring, rotation, ETF, breadth, snapshot, history, and watchlist engines
- `market_data/` stores generated reports, snapshots, rotation deltas, and classification history
- `docs/` contains architecture and operational notes

## Requirements

- Python 3.10+
- `pandas`

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Run

Execute the product from the project root:

```bash
python main.py
```

The run writes a dated report to `market_data/daily_reports/` and updates supporting data artifacts used by the engines.

## Ownership

This product is owned by Parimal Rane.

Copyright (c) 2026 Parimal Rane. All rights reserved.

## License

See the `LICENSE` file for the current repository license terms.
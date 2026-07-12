# USER_GUIDE.md

# TABELA User Guide

---

# 1. Purpose

This guide explains how to install, configure, run and interpret TABELA.

It is intended for users running the application, not developers.

---

# 2. Requirements

- Python 3.12+
- Required Python packages
- Windows (primary platform)

---

# 3. Folder Structure

```
TABELA/

core/
engines/
data/
market_data/
reports/
docs/

main.py
```

---

# 4. Required Input Files

Place the following files inside the data directory.

```
ETF.csv

stocks.csv
```

Verify that both files are generated from the supported data sources.

---

# 5. Running TABELA

Execute

```
python main.py
```

The application automatically executes the complete processing pipeline.

---

# 6. Daily Workflow

1. Download latest ETF data.
2. Download latest stock universe.
3. Replace existing CSV files.
4. Execute TABELA.
5. Review generated reports.
6. Archive outputs if required.

---

# 7. Output Overview

TABELA produces:

- Theme Rankings
- Breadth Analysis
- Institutional Leaders
- Distribution Watchlist
- Structural Weakness Watchlist
- Historical Intelligence
- TradingView Watchlists

---

# 8. Historical Data

Historical data is automatically stored under

```
market_data/
```

Do not manually edit historical JSON files.

---

# 9. Troubleshooting

## Missing ETF.csv

Verify the file exists in the data directory.

---

## Missing stocks.csv

Verify the latest stock universe has been exported.

---

## Unknown Themes

Update the mapping tables.

---

## Empty Reports

Check:

- Input CSV files
- Mapping files
- Console errors

---

# 10. Best Practices

- Use fresh market data.
- Do not modify generated JSON files.
- Keep historical snapshots.
- Review warnings after every execution.
- Backup the project periodically.
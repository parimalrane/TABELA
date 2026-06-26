# TABELA Module Reference

This page summarizes what each module in the repository is responsible for.

## Entry Point

- main.py: very small wrapper that launches the daily pipeline.

## Core Package

- core/pipeline.py: the main orchestration layer for the full scan.
- core/config.py: configuration values for scoring, filters, thresholds, and output paths.
- core/company_theme_engine.py: manual company-to-theme mapping lookup.
- core/stock_mapper.py: heuristic mapping for stocks that do not have a manual override.
- core/theme_parser.py: parses ETF strategy text into sector/theme/subtheme values.
- core/theme_translation_engine.py: translates internal themes to ETF theme names.
- core/theme_hierarchy.py: maps theme aliases and parent themes.

## Engine Package

- engines/etf_filter.py: filters out ETFs that are not relevant for the scan.
- engines/etf_engine.py: computes ETF relative strength and ETF theme classes.
- engines/scoring_engine.py: calculates RS, sales, Zacks, and margin scores for stocks.
- engines/composite_engine.py: combines stock scores into a composite score.
- engines/long_scoring_engine.py: creates the long-side score.
- engines/short_scoring_engine.py: creates the short-side score.
- engines/watchlist_engine.py: selects long candidates.
- engines/short_engine.py: selects short candidates.
- engines/institutional_leaders_engine.py: adds institutional-style leader candidates.
- engines/breadth_engine.py: measures theme breadth across stocks.
- engines/snapshot_engine.py: writes the daily snapshot JSON file.
- engines/rotation_engine.py: calculates and saves rotation deltas between snapshots.
- engines/stock_history_engine.py: saves historical stock-universe data.
- engines/unknown_classification_engine.py: exports unknown emerging leader candidates.
- engines/watchlist_delta_engine.py: compares long and short watchlist sets.

## Data Files

- data/stock_theme_mapping.csv: manual stock-to-theme mapping table.
- market_data/ETF.csv: ETF universe input.
- market_data/stocks.csv: stock universe input.

## Output Locations

- market_data/snapshots: daily snapshot JSON files.
- market_data/rotation_delta: rotation delta JSON files.
- market_data/stock_universe: daily stock-history JSON files.
- market_data/unknown_classification: daily CSV exports for unknown emerging leaders.

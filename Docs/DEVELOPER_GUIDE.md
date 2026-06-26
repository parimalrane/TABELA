# TABELA Developer Guide

## Architecture overview

The project is organized around a simple pipeline:

- main.py is the entrypoint.
- core/pipeline.py owns the orchestration.
- engine modules provide focused calculations and output generation.
- core/config.py holds configuration values and thresholds.

This arrangement keeps the top-level script simple and makes the analysis stages easier to maintain.

## Current execution flow

The current scan flow is implemented in core/pipeline.py and follows this order:

1. Load and filter ETF data.
2. Parse ETF strategy text into sector/theme/subtheme values.
3. Calculate ETF relative strength and assign ETF theme classes.
4. Load stocks and filter them to the active Zacks rank range.
5. Map each stock to a theme using manual overrides or heuristic mapping.
6. Translate mapped themes into ETF-friendly theme names.
7. Score each stock on momentum, theme strength, sales, Zacks rank, and margin.
8. Build composite, long, and short scores.
9. Build long/short watchlists and theme breadth output.
10. Save history, snapshots, rotation data, and unknown-leader exports.

## Module responsibilities

### Core modules

- core/pipeline.py: orchestrates the full daily scan.
- core/config.py: centralizes thresholds, scoring weights, and output paths.
- core/company_theme_engine.py: manual stock-to-theme overrides from the CSV mapping file.
- core/stock_mapper.py: heuristic fallback mapping for stocks without manual overrides.
- core/theme_parser.py: parses ETF strategy text into structured values.
- core/theme_translation_engine.py: maps internal themes to ETF theme names.
- core/theme_hierarchy.py: parent-theme mapping used during theme inheritance logic.

### Engine modules

- engines/etf_filter.py: removes irrelevant or low-quality ETFs.
- engines/etf_engine.py: computes ETF momentum and assigns ETF theme classes.
- engines/scoring_engine.py: calculates stock-level RS, sales, Zacks, and margin scores.
- engines/composite_engine.py: creates the composite score used in breadth and ranking logic.
- engines/long_scoring_engine.py: builds the long-side scoring formula.
- engines/short_scoring_engine.py: builds the short-side scoring formula.
- engines/watchlist_engine.py: builds the long watchlist.
- engines/short_engine.py: builds the short watchlist.
- engines/institutional_leaders_engine.py: adds institutional-style leader candidates.
- engines/breadth_engine.py: computes theme breadth metrics.
- engines/snapshot_engine.py: writes daily market snapshot JSON files.
- engines/rotation_engine.py: compares snapshots and writes rotation-delta files.
- engines/stock_history_engine.py: writes the daily stock-universe history.
- engines/unknown_classification_engine.py: exports unknown emerging leaders for review.
- engines/watchlist_delta_engine.py: compares long and short watchlist sets.

## Extension guidance

### Adding a new scoring factor

1. Add the new calculation in the relevant engine module.
2. Add any configuration values to core/config.py.
3. Wire the new score into the pipeline and downstream engines.
4. Update the output logic if the new factor should be shown.

### Adding a new output

1. Create a focused engine module for the new output.
2. Call it from core/pipeline.py at the appropriate stage.
3. Keep the output generation isolated from the scoring logic.

### Keeping changes safe

- Do not put business logic in main.py.
- Prefer small, focused modules over large monolithic functions.
- Keep configuration values in core/config.py instead of hard-coding thresholds throughout the code.
- Preserve the current output format unless a change is explicitly required.

## Testing

The project now includes a small regression test for the theme-classification helper in tests/test_pipeline.py.

Run tests with:

```bash
python -m pytest -q
```

## Development notes

- The code is intentionally data-driven and uses pandas heavily.
- The pipeline is the central coordination point for the daily scan.
- Optional intelligence outputs such as snapshots and rotation data should not break the core scan if they fail.

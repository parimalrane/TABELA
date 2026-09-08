# TABELA Pipeline: Handover Context

## 1. Current State of the Architecture
*   **Fully Stateless Engine:** The platform is configured as a stateless, cross-sectional engine. It evaluates 100% of candidate logic purely on the daily score differentials relative to the engine configurations, removing legacy chronological state-tracking requirements.
*   **Institutional Alignment:** 
    *   Macro scoring logic utilizes a smoothed, 6-period momentum approach (3M, 6M, 1Y, 1M, 1W, 1D at `40/25/15/15/3/2`).
    *   Stock `RS_RAW_WEIGHTS` uniquely map to this macro curve using proxy available datasets: 12-Week (40%), YTD (25%), 52-Wk Range (15%), 4-Week (15%), and 1-Week (5%).
    *   Theme distribution splits are actively anchored at 25% Leading, 50% Neutral, and 25% Lagging.

## 2. Recent Reporting/UI Optimizations
*   The `Theme Classification` column was stripped entirely from the **Long Candidate Universe** and **Distribution Watchlist** active views to remove redundancy (Longs are strictly Leading; Shorts are strictly Lagging).
*   **Exception Flags:** Special classifications are prepended directly to the Ticker column:
    *   `^` (Micro Leaders / Micro Laggards)
    *   `~` (Unknowns / Unclassified Leaders)
*   **TradingView Export Safety:** The `presentation_engine.py` scrubbing logic forces `^` and `~` to be completely stripped out before generating the raw comma-separated payload.
*   **Dropped Detail Views:** The theme state was merged cleanly into the `Mapped_Theme` column (e.g., `Software (Neutral)`) for the 'Dropped' lists instead of being hosted in a standalone column, explicitly proving when a "Theme Downgrade" triggers an exit.

## 3. Config.py Status
`config.py` acts as the command center for the entire pipeline.
*   `LONG_ENTRY` and `DIST_ENTRY` thresholds act as hard gateways (MIN_RS, MIN_LONG_SCORE).
*   Theme weights, classification constraints, and entry allowances are fully externalized here. No logic parameters should be manually hardcoded in `pipeline.py` or `scoring_engine.py`.

## 4. Known Dynamics to Respect
*   Never use `LONG_ENTRY["THEMES"]` without expecting strict gating; they control exactly what passes.
*   Ensure that any column adjustments made to `presentation_engine.py` dataframes sync identical layouts for both Longs and Distributions.
*   The data ingestion pipeline relies on variable `stocks.csv` headers. Always use safe `.get()` or `.fillna()` access methods for unpredictable missing data (like Zacks Rank).

# TABELA Pipeline: Handover Context
**Last Updated: 2026-09-22**

## 1. Current State of the Architecture
*   **Fully Stateless Engine:** The platform is configured as a stateless, cross-sectional engine. It evaluates 100% of candidate logic purely on the daily score differentials relative to the engine configurations.
*   **Institutional Alignment (O'Neil / Minervini / Livermore):**
    *   Macro scoring logic utilizes a smoothed, 6-period momentum approach (3M, 6M, 1Y, 1M, 1W, 1D at `40/25/15/15/3/2`).
    *   Stock `RS_RAW_WEIGHTS` uniquely map to this macro curve using proxy available datasets: 12-Week (40%), YTD (25%), 52-Wk Range (15%), 4-Week (15%), and 1-Week (5%).
    *   Theme distribution splits are actively anchored at 25% Leading, 50% Neutral, and 25% Lagging.
*   **Unified Weight System:** Both ETF-level individual scoring (`etf_engine.py`) and Theme-level aggregation (`pipeline.py`) now use the identical `THEME_STRENGTH_CONFIG["PERIOD_WEIGHTS"]` from `config.py`. There are zero hardcoded weight sets in the codebase.

## 2. Crowding Logic (Micro Theme Grouping)
*   **Grouping Key:** The `MAX_PER_THEME` cap is applied at the **Micro Theme** (`Mapped_Theme`) level, NOT the Macro ETF level.
*   **Cap Value:** `MAX_PER_THEME = 3` for both Longs and Distributions.
*   **Rationale:** This enforces the O'Neil/Minervini "Top 2-3 leaders per industry group" rule. A stock like MU (Memory) competes only against other Memory stocks, not against unrelated Foundry or Equipment stocks that share the "Semiconductors" macro tag.
*   **Theme Classification** remains at the **Macro (ETF) level** for institutional accuracy. Only the crowding cap operates at the Micro level.
*   **"Crowded Out" Exit Reason:** When a dropped stock passes all gates (Theme, RS, Score) but is missing from the board, the presentation engine deduces it was displaced by higher-scoring peers within its Micro Theme.

## 3. Reporting/UI Optimizations
*   The `Theme Classification` column is stripped from the **Long Candidate Universe** and **Distribution Watchlist** active views to remove redundancy.
*   **Exception Flags** are prepended directly to the Ticker column:
    *   `^` (Micro Leaders / Micro Laggards)
    *   `~` (Unknowns / Unclassified Leaders)
*   **TradingView Export:** Scoped to **NEW entries only** (`Days = 1`). Full list exports were removed. The section auto-hides if no new entries exist.
*   **Dropped Detail Views:** The theme state is merged into the `Mapped_Theme` column (e.g., `Software (Neutral)`) for the 'Dropped' lists.
*   **Theme Breadth Board:** Only displays themes that have at least one actionable Long or Distribution candidate. Empty themes are auto-hidden for clean board reading.
*   **Rank Delta Signs:** Positive (`+N`) means the theme improved N positions. Negative (`-N`) means deterioration. This matches institutional convention (lower rank = better).

## 4. Config.py Status
`config.py` acts as the command center for the entire pipeline.
*   `LONG_ENTRY`: MIN_RS=85, MIN_LONG_SCORE=80, MAX_PER_THEME=3, THEMES=[Leading, Micro Leader, Unclassified Leader, Unknown]
*   `DIST_ENTRY`: MAX_RS=40, MAX_LONG_SCORE=40, MAX_PER_THEME=3, THEMES=[Lagging, Micro Laggard]
*   Theme weights, classification constraints, and entry allowances are fully externalized. No logic parameters are hardcoded in `pipeline.py` or `scoring_engine.py`.

## 5. Critical Bug Fixes Applied (2026-09-20)
1. **Double-Scoring Eliminated:** `score_stocks()` no longer re-calculates RS, Sales, Zacks scores that were already computed before theme classification.
2. **ETF Weight Unification:** `etf_engine.py` imports weights from config instead of using its own conflicting hardcoded set.
3. **Theme Parser Casing Fix:** Removed `.title()` from `theme_parser.py` to preserve raw Zacks casing and prevent silent mapping mismatches (e.g., "and" → "And").
4. **Rank Delta Sign Fix:** Corrected inverted movement arrows in Theme Breadth display.
5. **Missing Config Key Fix:** Replaced non-existent `STOCK_TRANSITION_CONFIG` import with canonical path in presentation engine.
6. **Stock History Lookup Fix:** Replaced fragile `files[-2]` indexing with date-aware lookup for previous day's stock history.

## 6. Known Dynamics to Respect
*   Never use `LONG_ENTRY["THEMES"]` without expecting strict gating; they control exactly what passes.
*   Ensure that any column adjustments made to `presentation_engine.py` dataframes sync identical layouts for both Longs and Distributions.
*   The data ingestion pipeline relies on variable `stocks.csv` headers. Always use safe `.get()` or `.fillna()` access methods for unpredictable missing data (like Zacks Rank).
*   The `macro_theme_mapping.csv` entries must match the **raw Zacks ETF casing** (no `.title()` transformation is applied).
*   The core scoring engine is considered **V1.0 Complete** — no structural changes should be made unless a literal software bug is discovered.

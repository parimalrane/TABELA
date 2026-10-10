# Sector Intelligence Engine

The **Sector Intelligence Engine** is a point-in-time, deterministic macro sector analysis subsystem integrated natively into the TABELA algorithmic screener. 

It evaluates the 11 major SPDR sector ETFs to identify capital rotation, macroeconomic tailwinds, and relative strength, serving as a top-down confirmation layer before individual stock selection.

## Terminal Display Metrics

When executing the daily pipeline, the engine produces a condensed, institutional-grade summary table:

`Rank  Sector            SPDR  1-Qtr      YTD  Strength   Rank Δ(1W)   SPY Ex(1M)   Impact   Status`

### Metric Definitions

*   **Rank**: The current rank of the sector (1 to 11) relative to peers, sorted by the composite `Strength` score. `1` represents the strongest bullish momentum.
*   **Sector & SPDR**: The human-readable sector category (e.g., Technology) and its tracking ETF ticker (e.g., XLK).
*   **1-Qtr & YTD**: The raw performance of the sector ETF over the trailing 3-month (Quarter) and Year-To-Date timeframes. This provides macro-level context.
*   **Strength**: A mathematically weighted composite score evaluating multi-timeframe momentum. (e.g., 20% 1-Week, 40% 1-Month, 30% 1-Quarter, 10% YTD). This smooths out noise and identifies true trend velocity.
*   **Rank Δ (1W)**: *Rank Delta*. This calculates rotational capital flow by comparing today's `Rank` against where the sector ranked exactly 7 calendar days ago using historical snapshot data. A positive `+` indicates the sector is moving *up* the leaderboard.
*   **SPY Ex (1M)**: *Excess Return vs. SPY*. The sector's 1-Month return minus the S&P 500 (SPY) 1-Month return. A positive percentage indicates true alpha-generation and outperformance relative to the broader market index.
*   **Impact**: *Capital Flow Gravity*. A specialized metric calculated by scaling raw momentum against the log-value of the sector's Assets Under Management (AUM). This ensures massive, systemic sectors displaying momentum carry appropriate weight.
*   **Status**: The final derived state, which dictates the engine's internal watchlists:
    *   `LEADING`: The sector ranks in the elite top tier (Ranks 1-3).
    *   `LAGGING`: The sector ranks in the bottom tier (Ranks 9-11).
    *   `IMPROVING`: The sector is rotating positively with a `Rank Δ` of `+2` or better.
    *   `DETERIORATING`: The sector is rotating negatively with a `Rank Δ` of `-2` or worse.
    *   `NEUTRAL`: Stable middle-of-the-pack performance lacking significant rotation.

## Architecture & Execution

*   **Decoupled Logic**: Resides entirely within `scoring/sector_intelligence.py`. It operates strictly on the presentation layer and does NOT alter or contaminate downstream individual equity scoring.
*   **Zero Look-Ahead Bias**: Uses strict date-matched `_ETF.csv` files from the `market_data` sequence to ensure perfect point-in-time accuracy during backtesting, crawling sequentially backwards to identify `T-7` rotation.
*   **Verification Module**: Includes `backtesting/sector_backtest.py` which chronologically validates edge by generating forward absolute and spread returns across 1-day, 3-day, 5-day, and 10-day holding periods.


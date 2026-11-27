# TABELA — Future Enhancements & Pending Work
**Last Updated:** November 27, 2026

---

## Status Legend
| Symbol | Meaning |
|---|---|
| 🔴 | Not started — high priority |
| 🟡 | Partially implemented or designed but not coded |
| 🟢 | Completed |
| ⚫ | On hold / deferred |

---

## 🟢 COMPLETED: Thematic Architecture & Watchlist Restructuring
1. **Industry & Stock Thematic Relational Mappings:**
   - Decoupled misclassified stocks out of improper thematic ETFs (e.g. general industrials and base metal miners out of ###GDX) into legitimate pure-play themes (Infrastructure, Copper Mining, Silver Mining, Industrials, Utilities).
   - Integrated data/industry_theme_mapping.csv, data/stock_theme_mapping.csv, and data/theme_etf_mapping.csv.
2. **TradingView Watchlist Restructuring:**
   - Header lists (###leading_ETF,... and ###lagging_ETF,...) dynamically include all primary and secondary pure-play ETFs displayed in the Theme Breadth table.
   - Individual ETF relative strength scored against SPY (20% 1W + 40% 1M + 40% 3M) with deterministic mutual exclusion.
   - Stocks segmented into single granular ETF buckets with zero cross-bucket duplicates.

---

## 🟡 PENDING: Dual-Engine Theme Classification (Top-Down + Bottom-Up)
**What:** Address remaining trust issues on themes where micro-themes inherit macro-theme ETF ranks via cloning without confirmed stock participation.
1. **Dual-Score Blending:** Compute Theme Score as 50% Top-Down ETF RS + 50% Bottom-Up Stock Breadth.
2. **Absolute Outperformance Floor:** Require Theme Score > 0.0% (outperforming SPY) to qualify as Leading.
3. **Institutional Confirmation Threshold:** Require >= 7 active institutional stocks for a micro-theme to qualify as a standalone Micro Leader.
4. **Configuration Safety:** All weights, floors, and thresholds exposed via config/config.py.

---

## 🚀 TOP PRIORITY: The Unified Optimization Upgrade
**What:** We must fix the slow 2-hour fundamental tuning bottleneck and the lack of Winner vs. Loser characteristic tracking in a **single architectural operation**.

1. **Fully Vectorized (In-Memory) Backtesting:** Rewrite `run_quarterly_tuner.py` into a fully vectorized Pandas matrix. It must never delete or overwrite the 3 years of daily JSON histories on the hard drive. It must calculate `RS_Rating` and `Long_Score` variations entirely in RAM. This will drop the 2-hour backtest to 3 minutes.
2. **Alpha Attribution (Winners vs. Losers Comparison):** Once the backtest runs exclusively in a Pandas matrix, intercept that matrix before it collapses into a single "Win Rate %" number. Output an attribution report that explicitly groups the characteristics of Winning trades vs. Losing trades (e.g., "75% of your losers had Zacks Rank 2" or "Winners overwhelmingly had RS > 95"). This allows the user to program precise negative constraints into the pipeline.

**Execution Requirement:** Both of these must be built together because the Pandas matrix structure required for #1 natively enables the slicing required for #2.

---

## 🛠️ Codebase Maintenance & Housekeeping
For non-functional technical debt items, dead code removals, and modular engine refactorings, see **[housekeep.md](file:///c:/TABELA/housekeep.md)**.

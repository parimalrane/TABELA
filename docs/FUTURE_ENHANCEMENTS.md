# TABELA — Future Enhancements & Pending Work
**Last Updated:** October 4, 2026

---

## Status Legend
| Symbol | Meaning |
|---|---|
| 🔴 | Not started — high priority |
| 🟡 | Partially implemented or designed but not coded |
| 🟢 | Completed |
| ⚫ | On hold / deferred |

---

## 🚀 TOP PRIORITY: The Unified Optimization Upgrade
**What:** We must fix the slow 2-hour fundamental tuning bottleneck and the lack of Winner vs. Loser characteristic tracking in a **single architectural operation**.

1. **Fully Vectorized (In-Memory) Backtesting:** Rewrite `run_quarterly_tuner.py` into a fully vectorized Pandas matrix. It must never delete or overwrite the 3 years of daily JSON histories on the hard drive. It must calculate `RS_Rating` and `Long_Score` variations entirely in RAM. This will drop the 2-hour backtest to 3 minutes.
2. **Alpha Attribution (Winners vs. Losers Comparison):** Once the backtest runs exclusively in a Pandas matrix, intercept that matrix before it collapses into a single "Win Rate %" number. Output an attribution report that explicitly groups the characteristics of Winning trades vs. Losing trades (e.g., "75% of your losers had Zacks Rank 2" or "Winners overwhelmingly had RS > 95"). This allows the user to program precise negative constraints into the pipeline.

**Execution Requirement:** Both of these must be built together because the Pandas matrix structure required for #1 natively enables the slicing required for #2.

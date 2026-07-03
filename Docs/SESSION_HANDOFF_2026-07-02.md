# TABELA Session Handoff - 2026-07-02

## Context
This note is a development handoff so the next session can resume without re-auditing everything.

## What Changed Today

### 1. Theme engine redesign (core pipeline behavior changed)
- Daily classification moved from 4-state to 3-state:
  - Old: Leading / Emerging / Weakening / Lagging
  - New: Leading / Neutral / Lagging
- `build_theme_classification` in `core/pipeline.py` now:
  - Uses top 20% as Leading, bottom 20% as Lagging, middle as Neutral
  - Uses continuous `Theme_Score` formula instead of buckets:
    - `Theme_Score = 20 + 80 * (total_themes - rank) / (total_themes - 1)`

### 2. Watchlist filter behavior changed
- `engines/watchlist_engine.py` long filter now allows:
  - `Leading`, `Unclassified Leader`
- `Emerging` was removed from long eligibility due to 3-state model.

### 3. Historical intelligence skeleton + iterative refinements
- Added `engines/historical_intelligence_engine.py`.
- Pipeline calls historical report safely (try/except), so core flow remains resilient.
- Historical report now works with snapshot history and prints report sections.
- Final sort behavior requested and applied:
  - Emerging: sort by `last_rank` ASC, then `rank_improvement` DESC, then `score_improvement` DESC
  - Weakening: sort by `last_rank` ASC, then `rank_deterioration` DESC, then `score_decline` DESC
- Weighted emerging/weakening scoring was removed; report currently uses raw movement metrics.

## PANW Forensic Audit Outcome (Key)

### Why PANW Long_Score changed even with same ETF.csv and stocks.csv
- PANW market inputs stayed effectively unchanged (RS/Sales/Zacks).
- The score change is from `Theme_Score` logic redesign in `core/pipeline.py`.

### Exact PANW Theme_Score explanation
- Old 4-state bucket logic:
  - Rank 4 in top 25% bucket -> `Theme_Score = 100`
- New continuous logic:
  - With 34 themes and rank 4:
  - `Theme_Score = 20 + 80*(34-4)/(34-1) = 92.73`
- This directly reduced PANW Long_Score from `90.75` to `88.93`.

### PANW Long_Score component decomposition observed
- Formula in `engines/long_scoring_engine.py`:
  - `0.55*RS_Rating + 0.25*Theme_Score + 0.12*Sales_Score + 0.05*Zacks_Score + 0.03*Margin_Score`
- Delta (07-02 minus 07-01) approximately:
  - RS: `0.00`
  - Theme: `-1.8175`
  - Sales: `0.00`
  - Zacks: `0.00`
  - Margin residual: very small rounding drift
  - Total: `-1.82`

## Important Repo State Notes
- There are many unrelated working-tree changes and generated file deltas in `market_data`, docs, and pycache.
- `core/pipeline.py` has active user-side edits in this workspace; always re-read before changing.
- Some historical JSON files have had corruption/merge-marker issues in earlier audits (notably older stock history file during prior troubleshooting).

## What To Do First Next Session
1. Re-check current git status before any edits.
2. Confirm intended final architecture rules for:
   - Daily classing (3-state)
   - Historical intelligence responsibilities
3. Decide whether PANW behavior is expected under continuous theme scoring, or whether a policy adjustment is desired:
   - Option A: keep strict continuous rank scoring
   - Option B: add protected cap/floor behavior for top-ranked themes
4. If changing scoring policy, update tests first in `tests/test_pipeline.py` to lock expected behavior.

## Files Most Relevant From Today
- `core/pipeline.py`
- `engines/watchlist_engine.py`
- `engines/historical_intelligence_engine.py`
- `engines/long_scoring_engine.py`
- `engines/scoring_engine.py`
- `tests/test_pipeline.py`
- `market_data/stock_universe/2026-07-01_stock_history.json`
- `market_data/stock_universe/2026-07-02_stock_history.json`
- `market_data/watchlist_history/watchlist_2026-07-01.json`
- `market_data/watchlist_history/watchlist_2026-07-02.json`

## One-line Session Summary
Today established the 3-state daily theme model, moved historical intelligence to optional layer, and confirmed PANW score drop was caused by Theme_Score formula redesign (bucket -> continuous), not by market CSV changes.

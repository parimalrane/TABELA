# Recent Changes Log

**Date:** 2026-10-15  
**Session:** Mild Watchlist Config-Driven Filters Implementation

---

## Summary

Implemented config-driven theme and Zacks rank filters for mild/swing watchlists.

---

## Changes Made

### 1. config/config.py

**Added:**
- `MILD_LONG_ENTRY` configuration block
- `MILD_SHORT_ENTRY` configuration block

**MILD_LONG_ENTRY Criteria:**
```python
MILD_LONG_ENTRY = {
    "BLOCKED_THEMES": ["Lagging", "Micro Laggard"],
    "ALLOWED_ZACKS": [1, 2],
    "MIN_RS": 70.0,
    "MIN_LONG_SCORE": 60.0,
    "MIN_PRICE": 10.0,
    "MIN_VOLUME": 1_000_000,
}
```

**MILD_SHORT_ENTRY Criteria:**
```python
MILD_SHORT_ENTRY = {
    "BLOCKED_THEMES": ["Leading", "Micro Leader", "Unclassified Leader"],
    "ALLOWED_ZACKS": [4, 5],
    "MAX_SHORT_RS": 70.0,
    "MAX_SHORT_SCORE": 60.0,
    "MIN_PRICE": 10.0,
    "MIN_VOLUME": 1_000_000,
}
```

### 2. reporting/presentation_engine.py

**Modified:** `clean_accumulator()` function in `print_daily_scan()`

**What it does:**
- Applies theme/Zacks filters to dropped stocks before adding to mild watchlists
- Long: Excludes lagging themes, requires Zacks 1-2
- Short: Excludes leading themes, requires Zacks 4-5

---

## How Mild/Swing Watchlists Work

**Entry Criteria (Bullish_Swing / Bearish_Swing):**

1. Was in strong watchlist (momentum)
2. Got dropped (fell below thresholds)
3. Within `MILD_DAYS` window (configurable, default 21)
4. **Config Filter:** Not from blocked themes
5. **Config Filter:** Zacks rank in allowed list

**Long Side:**
- Must NOT be from: Lagging, Micro Laggard
- Must have Zacks: 1 or 2

**Short Side:**
- Must NOT be from: Leading, Micro Leader, Unclassified Leader  
- Must have Zacks: 4 or 5

---

## Key Design Decisions

1. **Strong takes precedence** - A stock in momentum cannot also be in swing
2. **Dropped-based system** - Swing entries come from former momentum stocks
3. **Config-driven** - All filters via `config.py`, no hard coding
4. **Time-bound** - `MILD_DAYS` controls how long dropped stocks stay in swing

---

## Files Modified Today

- `config/config.py` - Added MILD_* config blocks
- `lifecycle/watchlist_engine.py` - Removed standalone mild functions (cleanup)
- `pipeline/pipeline.py` - Removed mild watchlist building (cleanup)
- `reporting/presentation_engine.py` - Modified `clean_accumulator()` with filters
- `lifecycle/stock_transition_engine.py` - Added MILD_* imports (kept _meets_criteria extensions)

---

## Testing Notes

After changes, verify:
- `Bullish_Swing` only contains stocks with Zacks 1-2, not from lagging themes
- `Bearish_Swing` only contains stocks with Zacks 4-5, not from leading themes
- No duplicates between Momentum and Swing lists

---

## Related Documentation

- See `BACKTESTING_GUIDE.md` for parameter tuning
- See `ARCHITECTURE.md` for data flow
- See `AGENT_RULES.md` - config.py is sacred, requires approval for changes

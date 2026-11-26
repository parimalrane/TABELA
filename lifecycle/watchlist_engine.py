import pandas as pd
from config.config import LONG_ENTRY, PULLBACK_CONFIG

def build_long_watchlist(stocks, registry=None):
    stocks_clean = stocks.copy()

    # 1. NEW ENTRY (Get-In Criteria)
    allowed_entry_themes = LONG_ENTRY.get("THEMES", ["Leading", "Micro Leader"])
    blocked_zacks = LONG_ENTRY.get("BLOCKED_ZACKS", [])

    min_52w = PULLBACK_CONFIG.get("LONG_MIN_52W_RANGE", 85.0)
    col_52w = "Price as a % of 52 Wk H-L Range"
    range_52w = pd.to_numeric(stocks_clean[col_52w], errors="coerce").fillna(0.0) if col_52w in stocks_clean.columns else pd.Series(0.0, index=stocks_clean.index)
    zacks_numeric = pd.to_numeric(stocks_clean["Zacks Rank"], errors="coerce").fillna(0).astype(int) if "Zacks Rank" in stocks_clean.columns else pd.Series(0, index=stocks_clean.index)
    close_numeric = pd.to_numeric(stocks_clean["Last Close"].astype(str).str.replace(r'[%$,]', '', regex=True), errors="coerce").fillna(0.0) if "Last Close" in stocks_clean.columns else pd.Series(0.0, index=stocks_clean.index)
    vol_numeric = pd.to_numeric(stocks_clean["Avg Volume"].astype(str).str.replace(r'[%$,]', '', regex=True), errors="coerce").fillna(0.0) if "Avg Volume" in stocks_clean.columns else pd.Series(0.0, index=stocks_clean.index)
    dollar_vol = close_numeric * vol_numeric
    growth_score = stocks_clean["Growth Score"].astype(str).str.strip().str.upper() if "Growth Score" in stocks_clean.columns else pd.Series("", index=stocks_clean.index)

    # 1. STATELESS DAILY EVALUATION (Pure Breakout Standards)
    # A stock must satisfy today's full breakout criteria to qualify for Strong Bullish.
    # No sticky stay retention buffer holding decaying momentum.
    standard_entry_mask = (
        stocks_clean["Theme_Class"].isin(allowed_entry_themes)
        & (stocks_clean["RS_Rating"] >= LONG_ENTRY["MIN_RS"])
        & (~zacks_numeric.isin(blocked_zacks))
        & (range_52w >= min_52w)
        & (close_numeric >= LONG_ENTRY.get("MIN_PRICE", 10.0))
        & (vol_numeric >= LONG_ENTRY.get("MIN_VOLUME", 1_000_000))
    )

    # Elite Momentum Exception (Configurable from LONG_ENTRY):
    # Leading theme + Exceptional RS + Range >= 85% + Zacks 3 allowed ONLY IF Growth A/B
    # Liquidity: Volume >= 1M OR Dollar Volume >= $30,000,000 (with volume >= 500k)
    elite_min_rs = LONG_ENTRY.get("ELITE_MIN_RS", 95.0)
    elite_growth = LONG_ENTRY.get("ELITE_ALLOWED_GROWTH", ["A", "B"])
    alt_min_vol = LONG_ENTRY.get("ELITE_ALT_MIN_VOLUME", 500_000)
    alt_min_dvol = LONG_ENTRY.get("ELITE_ALT_MIN_DOLLAR_VOL", 30_000_000)

    elite_exception_mask = (
        stocks_clean["Theme_Class"].isin(allowed_entry_themes)
        & (stocks_clean["RS_Rating"] >= elite_min_rs)
        & (range_52w >= min_52w)
        & (close_numeric >= LONG_ENTRY.get("MIN_PRICE", 10.0))
        & (
            (~zacks_numeric.isin(blocked_zacks))  # Zacks 1 or 2
            | ((zacks_numeric == 3) & growth_score.isin(elite_growth))  # Zacks 3 with verified growth
        )
        & (
            (vol_numeric >= LONG_ENTRY.get("MIN_VOLUME", 1_000_000))
            | ((vol_numeric >= alt_min_vol) & (dollar_vol >= alt_min_dvol))
        )
    )

    # Tag elite exception stocks for visual clarity
    stocks_clean["Is_Elite_Exception"] = False
    new_elite_mask = elite_exception_mask & (~standard_entry_mask)
    if new_elite_mask.any():
        stocks_clean.loc[new_elite_mask, "Is_Elite_Exception"] = True

    qualifying_mask = standard_entry_mask | elite_exception_mask

    long_watchlist = stocks_clean[qualifying_mask].copy()
    
    if long_watchlist.empty:
        return long_watchlist
        
    long_watchlist = long_watchlist.sort_values(
        ["RS_Rating"],
        ascending=[False]
    )

    # Deduplicate to prevent a duplicate stock from appearing multiple times
    long_watchlist = long_watchlist.drop_duplicates(subset=["Ticker"])
    
    # Re-sort natively post-grouping to ensure it drops into presentation smoothly
    long_watchlist = long_watchlist.sort_values(
        ["RS_Rating"],
        ascending=[False]
    )


    return long_watchlist

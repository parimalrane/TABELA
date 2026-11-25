import pandas as pd
from config.config import LONG_ENTRY, LONG_STAY, PULLBACK_CONFIG
from reporting.watchlist_delta_engine import load_previous_long_watchlist

def build_long_watchlist(stocks, registry=None):
    # Determine which stocks were in the watchlist yesterday (TABELA Retention)
    prev_wl = load_previous_long_watchlist()
    prev_tickers = set(prev_wl["Ticker"].str.upper().tolist()) if not prev_wl.empty else set()

    stocks_clean = stocks.copy()
    ticker_clean = stocks_clean["Ticker"].astype(str).str.replace("*", "", regex=False).str.strip().str.upper()

    is_existing = ticker_clean.isin(prev_tickers)

    # 1. NEW ENTRY (Get-In Criteria)
    allowed_entry_themes = LONG_ENTRY.get("THEMES", ["Leading", "Micro Leader", "Unclassified Leader", "Unknown"])
    blocked_zacks = LONG_ENTRY.get("BLOCKED_ZACKS", [])

    min_52w = PULLBACK_CONFIG.get("LONG_MIN_52W_RANGE", 85.0)
    col_52w = "Price as a % of 52 Wk H-L Range"
    range_52w = pd.to_numeric(stocks_clean[col_52w], errors="coerce").fillna(0.0) if col_52w in stocks_clean.columns else pd.Series(0.0, index=stocks_clean.index)
    zacks_numeric = pd.to_numeric(stocks_clean["Zacks Rank"], errors="coerce").fillna(0).astype(int) if "Zacks Rank" in stocks_clean.columns else pd.Series(0, index=stocks_clean.index)
    close_numeric = pd.to_numeric(stocks_clean["Last Close"].astype(str).str.replace(r'[%$,]', '', regex=True), errors="coerce").fillna(0.0) if "Last Close" in stocks_clean.columns else pd.Series(0.0, index=stocks_clean.index)
    vol_numeric = pd.to_numeric(stocks_clean["Avg Volume"].astype(str).str.replace(r'[%$,]', '', regex=True), errors="coerce").fillna(0.0) if "Avg Volume" in stocks_clean.columns else pd.Series(0.0, index=stocks_clean.index)
    dollar_vol = close_numeric * vol_numeric
    growth_score = stocks_clean["Growth Score"].astype(str).str.strip().str.upper() if "Growth Score" in stocks_clean.columns else pd.Series("", index=stocks_clean.index)

    # Standard Entry: Zacks 1-2, RS >= 90, Range >= 85%, Volume >= 1M
    standard_entry_mask = (
        (~is_existing)
        & stocks_clean["Theme_Class"].isin(allowed_entry_themes)
        & (stocks_clean["RS_Rating"] >= LONG_ENTRY["MIN_RS"])
        & (~zacks_numeric.isin(blocked_zacks))
        & (range_52w >= min_52w)
        & (close_numeric >= LONG_ENTRY.get("MIN_PRICE", 10.0))
        & (vol_numeric >= LONG_ENTRY.get("MIN_VOLUME", 1_000_000))
    )

    # Elite Momentum Exception (e.g. KNSA):
    # Leading theme + Exceptional RS (>= 95) + Range >= 85% + Zacks 3 allowed ONLY IF Growth A/B
    # Liquidity: Volume >= 1M OR Dollar Volume >= $30,000,000 (with volume >= 500k)
    elite_exception_mask = (
        (~is_existing)
        & stocks_clean["Theme_Class"].isin(allowed_entry_themes)
        & (stocks_clean["RS_Rating"] >= 95.0)
        & (range_52w >= min_52w)
        & (close_numeric >= LONG_ENTRY.get("MIN_PRICE", 10.0))
        & (
            (~zacks_numeric.isin(blocked_zacks))  # Zacks 1 or 2
            | ((zacks_numeric == 3) & growth_score.isin(["A", "B"]))  # Zacks 3 with verified growth
        )
        & (
            (vol_numeric >= LONG_ENTRY.get("MIN_VOLUME", 1_000_000))
            | ((vol_numeric >= 500_000) & (dollar_vol >= 30_000_000))
        )
    )

    # Tag elite exception stocks for visual clarity
    stocks_clean["Is_Elite_Exception"] = False
    new_elite_mask = elite_exception_mask & (~standard_entry_mask)
    if new_elite_mask.any():
        stocks_clean.loc[new_elite_mask, "Is_Elite_Exception"] = True

    entry_mask = standard_entry_mask | elite_exception_mask

    # 2. RETENTION (TABELA Stay-In Criteria)
    stay_themes = LONG_STAY.get("THEMES", ["Leading", "Neutral", "Unclassified Leader"])
    stay_min_rs = LONG_STAY.get("MIN_RS", 75.0)
    stay_allowed_zacks = LONG_STAY.get("ALLOWED_ZACKS", [1, 2, 3])

    stay_mask = (
        is_existing
        & stocks_clean["Theme_Class"].isin(stay_themes)
        & (stocks_clean["RS_Rating"] >= stay_min_rs)
        & zacks_numeric.isin(stay_allowed_zacks)
        & (close_numeric >= LONG_ENTRY.get("MIN_PRICE", 10.0))
        & (
            (vol_numeric >= LONG_ENTRY.get("MIN_VOLUME", 1_000_000))
            | ((vol_numeric >= 500_000) & (dollar_vol >= 30_000_000))
        )
    )

    standard_entry = entry_mask | stay_mask

    long_watchlist = stocks_clean[standard_entry].copy()
    
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

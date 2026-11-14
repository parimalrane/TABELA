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
    entry_mask = (
        (~is_existing)
        & stocks_clean["Theme_Class"].isin(allowed_entry_themes)
        & (stocks_clean["RS_Rating"] >= LONG_ENTRY["MIN_RS"])
    )

    if blocked_zacks:
        zacks_numeric = pd.to_numeric(stocks_clean["Zacks Rank"], errors="coerce").fillna(0).astype(int)
        entry_mask = entry_mask & (~zacks_numeric.isin(blocked_zacks))

    # 52W Range Gate on entry only
    min_52w = PULLBACK_CONFIG.get("LONG_MIN_52W_RANGE", 85.0)
    col_52w = "Price as a % of 52 Wk H-L Range"
    if col_52w in stocks_clean.columns:
        range_52w = pd.to_numeric(stocks_clean[col_52w], errors="coerce").fillna(0.0)
        entry_mask = entry_mask & (range_52w >= min_52w)

    # 2. RETENTION (TABELA Stay-In Criteria)
    stay_themes = LONG_STAY.get("THEMES", ["Leading", "Neutral", "Unclassified Leader"])
    stay_min_rs = LONG_STAY.get("MIN_RS", 75.0)
    stay_allowed_zacks = LONG_STAY.get("ALLOWED_ZACKS", [1, 2, 3])

    stay_mask = (
        is_existing
        & stocks_clean["Theme_Class"].isin(stay_themes)
        & (stocks_clean["RS_Rating"] >= stay_min_rs)
    )
    if "Zacks Rank" in stocks_clean.columns:
        zacks_numeric = pd.to_numeric(stocks_clean["Zacks Rank"], errors="coerce").fillna(0).astype(int)
        stay_mask = stay_mask & zacks_numeric.isin(stay_allowed_zacks)

    standard_entry = entry_mask | stay_mask
        
    min_price = LONG_ENTRY.get("MIN_PRICE", 0.0)
    min_volume = LONG_ENTRY.get("MIN_VOLUME", 0)
    
    if "Last Close" in stocks_clean.columns:
        valid_price = pd.to_numeric(stocks_clean["Last Close"], errors="coerce").fillna(0) >= min_price
        standard_entry = standard_entry & valid_price
        
    if "Avg Volume" in stocks_clean.columns:
        valid_volume = pd.to_numeric(stocks_clean["Avg Volume"], errors="coerce").fillna(0) >= min_volume
        standard_entry = standard_entry & valid_volume

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

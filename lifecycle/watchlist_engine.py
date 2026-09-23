import pandas as pd
from config.config import LONG_ENTRY

def build_long_watchlist(stocks, registry=None):
    # Pure Cross-Sectional Entry
    allowed_themes = LONG_ENTRY.get("THEMES", ["Leading", "Micro Leader", "Unclassified Leader", "Unknown"])
    blocked_zacks = LONG_ENTRY.get("BLOCKED_ZACKS", [])
    standard_entry = (
        stocks["Theme_Class"].isin(allowed_themes)
        & (stocks["RS_Rating"] >= LONG_ENTRY["MIN_RS"])
        & (stocks["Long_Score"] >= LONG_ENTRY["MIN_LONG_SCORE"])
    )
    if blocked_zacks:
        zacks_numeric = pd.to_numeric(stocks["Zacks Rank"], errors="coerce").fillna(0).astype(int)
        standard_entry = standard_entry & (~zacks_numeric.isin(blocked_zacks))

    long_watchlist = stocks[standard_entry].copy()
    
    if long_watchlist.empty:
        return long_watchlist
        
    long_watchlist = long_watchlist.sort_values(
        ["Long_Score", "RS_Rating"],
        ascending=[False, False]
    )

    # Deduplicate to prevent a duplicate stock from appearing multiple times
    long_watchlist = long_watchlist.drop_duplicates(subset=["Ticker"])
    
    # Re-sort natively post-grouping to ensure it drops into presentation smoothly
    long_watchlist = long_watchlist.sort_values(
        ["Long_Score", "RS_Rating"],
        ascending=[False, False]
    )

    return long_watchlist
from config.config import LONG_ENTRY

def build_long_watchlist(stocks, registry=None):
    # Pure Cross-Sectional Entry
    standard_entry = (
        stocks["Theme_Class"].isin(["Leading", "Unclassified Leader", "Unknown"])
        & (stocks["RS_Rating"] >= LONG_ENTRY["MIN_RS"])
        & (stocks["Long_Score"] >= LONG_ENTRY["MIN_LONG_SCORE"])
    )

    long_watchlist = stocks[standard_entry].copy()
    
    if long_watchlist.empty:
        return long_watchlist
        
    long_watchlist = long_watchlist.sort_values(
        ["Long_Score", "RS_Rating"],
        ascending=[False, False]
    )

    max_size = LONG_ENTRY.get("MAX_LIST_SIZE", 21)
    return long_watchlist.head(max_size)
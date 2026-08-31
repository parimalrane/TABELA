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

    max_per_theme = LONG_ENTRY.get("MAX_PER_THEME", 3)
    
    # Deduplicate before grouping to prevent a duplicate stock from eating multiple slots
    long_watchlist = long_watchlist.drop_duplicates(subset=["Ticker"])
    
    # Use ETF_Theme to group, ensuring we grab the top 3 per macro bucket
    long_watchlist = long_watchlist.groupby("ETF_Theme").head(max_per_theme)
    
    # Re-sort natively post-grouping to ensure it drops into presentation smoothly
    long_watchlist = long_watchlist.sort_values(
        ["Long_Score", "RS_Rating"],
        ascending=[False, False]
    )

    return long_watchlist
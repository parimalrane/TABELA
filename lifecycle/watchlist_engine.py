from config.config import LONG_ENTRY

def build_long_watchlist(stocks, registry=None):
    # Pure Cross-Sectional Entry
    allowed_themes = LONG_ENTRY.get("THEMES", ["Leading", "Micro Leader", "Unclassified Leader", "Unknown"])
    standard_entry = (
        stocks["Theme_Class"].isin(allowed_themes)
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

    max_per_theme = LONG_ENTRY.get("MAX_PER_THEME", 5)
    
    # Deduplicate before grouping to prevent a duplicate stock from eating multiple slots
    long_watchlist = long_watchlist.drop_duplicates(subset=["Ticker"])
    
    # Group by MICRO THEME (Mapped_Theme) to prevent giant macro sectors from crowding out niche leaders
    long_watchlist = long_watchlist.groupby("Mapped_Theme").head(max_per_theme)
    
    # Re-sort natively post-grouping to ensure it drops into presentation smoothly
    long_watchlist = long_watchlist.sort_values(
        ["Long_Score", "RS_Rating"],
        ascending=[False, False]
    )

    return long_watchlist
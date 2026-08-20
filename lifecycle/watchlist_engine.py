from config.config import LONG_FILTERS


def build_long_watchlist(stocks, registry):

    # Standard Macro-backed entry
    standard_entry = (
        stocks["Theme_Class"].isin(["Leading", "Unclassified Leader"])
        & (stocks["RS_Rating"] >= LONG_FILTERS["MIN_RS"])
        & (stocks["Long_Score"] >= LONG_FILTERS["MIN_LONG_SCORE"])
    )

    # Idiosyncratic Exemption override - Strictly for Non-Leading Themes
    idiosyncratic_entry = (
        ~stocks["Theme_Class"].isin(["Leading", "Unclassified Leader"])
        & (stocks["RS_Rating"] >= LONG_FILTERS["IDIOSYNCRATIC_MIN_RS"])
        & (stocks["Long_Score"] >= LONG_FILTERS["IDIOSYNCRATIC_MIN_LONG_SCORE"])
    )

    from config.config import RE_ENTRY_MIN_RS, RE_ENTRY_MIN_LONG_SCORE
    
    reentry_eligible_tickers = {
        ticker for ticker, state in registry.items()
        if state["tracking_state"] in ["OBSERVATION", "DISTRIBUTION"]
    }
    
    is_reentry_eligible = stocks["Ticker"].astype(str).str.upper().str.replace("*", "", regex=False).isin(reentry_eligible_tickers)

    re_entry = (
        is_reentry_eligible
        & stocks["Theme_Class"].isin(["Leading", "Unclassified Leader"])
        & (stocks["RS_Rating"] >= RE_ENTRY_MIN_RS)
        & (stocks["Long_Score"] >= RE_ENTRY_MIN_LONG_SCORE)
    )

    idiosyncratic_re_entry = (
        is_reentry_eligible
        & ~stocks["Theme_Class"].isin(["Leading", "Unclassified Leader"])
        & (stocks["RS_Rating"] >= LONG_FILTERS["IDIOSYNCRATIC_MIN_RS"])
        & (stocks["Long_Score"] >= LONG_FILTERS["IDIOSYNCRATIC_MIN_LONG_SCORE"])
    )

    # Combine and ban Lagging themes (Rule 1)
    long_watchlist = stocks[
        (standard_entry | idiosyncratic_entry | re_entry | idiosyncratic_re_entry) & 
        ~stocks["Theme_Class"].str.contains("Lagging", na=False)
    ].copy()
    
    # Mark which ones are re-entries to flag in the UI
    long_watchlist["Is_Reentry"] = re_entry | idiosyncratic_re_entry


    long_watchlist = long_watchlist.sort_values(

        "Long_Score",
        ascending=False

    )


    return long_watchlist
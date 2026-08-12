from core.config import LONG_FILTERS


def build_long_watchlist(stocks):

    # Standard Macro-backed entry
    standard_entry = (
        stocks["Theme_Class"].isin(["Leading", "Unclassified Leader"])
        & (stocks["RS_Rating"] >= LONG_FILTERS["MIN_RS"])
        & (stocks["Long_Score"] >= LONG_FILTERS["MIN_LONG_SCORE"])
    )

    # Idiosyncratic Exemption override
    idiosyncratic_entry = (
        (stocks["RS_Rating"] >= LONG_FILTERS["IDIOSYNCRATIC_MIN_RS"])
        & (stocks["Long_Score"] >= LONG_FILTERS["IDIOSYNCRATIC_MIN_LONG_SCORE"])
    )

    long_watchlist = stocks[standard_entry | idiosyncratic_entry].copy()


    long_watchlist = long_watchlist.sort_values(

        "Long_Score",
        ascending=False

    )


    return long_watchlist
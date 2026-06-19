from config import LONG_FILTERS


def build_long_watchlist(stocks):

    long_watchlist = stocks[

        (stocks["Theme_Class"].isin(["Leading", "Emerging", "Unclassified Leader"])) &

        (stocks["Composite_Score"] >= LONG_FILTERS["MIN_COMPOSITE"]) &

        (stocks["RS_Rating"] >= LONG_FILTERS["MIN_RS"]) &

        (stocks["Sales_Score"] >= LONG_FILTERS["MIN_SALES"]) &

        (stocks["Zacks_Score"] >= LONG_FILTERS["MIN_ZACKS"])

    ]


    long_watchlist = long_watchlist.sort_values(

        "Composite_Score",
        ascending=False

    )


    return long_watchlist
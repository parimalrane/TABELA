from config import SHORT_FILTERS


def build_short_watchlist(stocks):

    short_watchlist = stocks[

        (stocks["RS_Rating"] <= SHORT_FILTERS["MAX_RS"]) &

        (stocks["Composite_Score"] <= SHORT_FILTERS["MAX_COMPOSITE"]) &

        (

            (stocks["Sales_Score"] <= SHORT_FILTERS["MAX_SALES"]) |

            (stocks["Zacks_Score"] <= SHORT_FILTERS["MAX_ZACKS"])

        ) &

        (stocks["Theme_Class"] != "Unclassified Leader")

    ]


    short_watchlist = short_watchlist.sort_values(

        ["RS_Rating", "Composite_Score"],

        ascending=True

    )


    return short_watchlist
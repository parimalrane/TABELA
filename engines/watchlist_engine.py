from core.config import LONG_FILTERS


def build_long_watchlist(stocks):

    long_watchlist = stocks[

        (
            stocks["Theme_Class"].isin(
                ["Leading", "Unclassified Leader"]
            )
        )

        &

        (
            stocks["RS_Rating"] >= LONG_FILTERS["MIN_RS"]
        )

        &

        (
            stocks["Long_Score"] >= LONG_FILTERS["MIN_LONG_SCORE"]
        )

    ]


    long_watchlist = long_watchlist.sort_values(

        "Long_Score",
        ascending=False

    )


    return long_watchlist
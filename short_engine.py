from config import SHORT_FILTERS


def build_short_watchlist(stocks):

    short_watchlist = stocks[

        (stocks["Weakness_Score"] >= 70) &

        (stocks["Composite_Score"] <= SHORT_FILTERS["MAX_COMPOSITE"]) &

        (

            (stocks["Theme_Class"] == "Weakening") |

            (stocks["Theme_Class"] == "Lagging")

        )

    ]

    short_watchlist = short_watchlist.sort_values(

        ["Weakness_Score", "Composite_Score"],

        ascending=False

    )

    return short_watchlist
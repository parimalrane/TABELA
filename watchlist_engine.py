def build_long_watchlist(stocks):

    long_watchlist = stocks[

        (stocks["Theme_Class"].isin(["Leading", "Emerging"])) &

        (stocks["Composite_Score"] >= 80) &

        (stocks["RS_Rating"] >= 80) &

        (stocks["Sales_Score"] >= 60) &

        (stocks["Zacks_Score"] >= 60)

    ]


    long_watchlist = long_watchlist.sort_values(

        "Composite_Score",
        ascending=False
    )


    return long_watchlist
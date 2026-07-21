
import math


def build_theme_breadth(stocks):

    # ==========================================
    # DEFINE STRONG STOCKS
    # ==========================================

    strong_stocks = stocks[

        (stocks["RS_Rating"] >= 80)

        &

        (stocks["Composite_Score"] >= 75)

    ].copy()

    # ==========================================
    # TOP LEADERS PER THEME
    # ==========================================

    leaders_by_theme = (

        strong_stocks

        .sort_values(

            ["Long_Score", "RS_Rating"],

            ascending=[False, False],

        )

        .groupby("Mapped_Theme")["Ticker"]

        .apply(lambda s: ", ".join(s.head(5)))

        .reset_index(name="Leaders")

    )

    # ==========================================
    # TOTAL STOCKS PER THEME
    # ==========================================

    total_by_theme = (

        stocks

        .groupby("Mapped_Theme")

        .size()

        .reset_index(name="Total_Stocks")

    )

    # ==========================================
    # STRONG STOCKS PER THEME
    # ==========================================

    strong_by_theme = (

        strong_stocks

        .groupby("Mapped_Theme")

        .agg(

            Strong_Stocks=("Mapped_Theme", "size"),

            Avg_Strong_RS=("RS_Rating", "mean"),

        )

        .reset_index()

    )

    # ==========================================
    # MERGE
    # ==========================================

    breadth = (

        total_by_theme

        .merge(

            strong_by_theme,

            on="Mapped_Theme",

            how="left",

        )

        .merge(

            leaders_by_theme,

            on="Mapped_Theme",

            how="left",

        )

    )

    breadth["Strong_Stocks"] = breadth["Strong_Stocks"].fillna(0)
    breadth["Avg_Strong_RS"] = breadth["Avg_Strong_RS"].fillna(0)
    breadth["Leaders"] = breadth["Leaders"].fillna("")

    # ==========================================
    # STANDARD BREADTH %
    # ==========================================

    breadth["Breadth_Percent"] = round(

        (breadth["Strong_Stocks"] / breadth["Total_Stocks"]) * 100,

        2,

    )

    # ==========================================
    # WEIGHTED BREADTH SCORE
    # ==========================================

    breadth["Weighted_Breadth_Score"] = round(

        breadth["Breadth_Percent"]

        *

        (breadth["Avg_Strong_RS"] / 100)

        *

        breadth["Total_Stocks"].apply(

            lambda x: math.log(x + 1)

        ),

        2,

    )

    # ==========================================
    # SORT
    # ==========================================

    breadth = breadth.sort_values(

        "Weighted_Breadth_Score",

        ascending=False,

    )

    return breadth

    # ==========================================
    # DEFINE STRONG STOCKS
    # ==========================================

    strong_stocks = stocks[

        (stocks["RS_Rating"] >= 80) &

        (stocks["Composite_Score"] >= 75)

    ]


    # ==========================================
    # TOTAL STOCKS PER THEME
    # ==========================================

    total_by_theme = (

        stocks

        .groupby("Mapped_Theme")

        .size()

        .reset_index(name="Total_Stocks")

    )


    # ==========================================
    # STRONG STOCKS PER THEME
    # ==========================================

    strong_by_theme = (

        strong_stocks

        .groupby("Mapped_Theme")

        .agg(

            Strong_Stocks=("Mapped_Theme", "size"),

            Avg_Strong_RS=("RS_Rating", "mean")

        )
        .reset_index()

    )


    # ==========================================
    # MERGE
    # ==========================================

    breadth = total_by_theme.merge(

        strong_by_theme,

        on="Mapped_Theme",

        how="left"

    )


    breadth["Strong_Stocks"] = breadth["Strong_Stocks"].fillna(0)
    breadth["Avg_Strong_RS"] = breadth["Avg_Strong_RS"].fillna(0)


    # ==========================================
    # STANDARD BREADTH %
    # ==========================================

    breadth["Breadth_Percent"] = round(

        (breadth["Strong_Stocks"] / breadth["Total_Stocks"]) * 100,

        2

    )


    # ==========================================
    # WEIGHTED BREADTH SCORE
    # ==========================================

    breadth["Weighted_Breadth_Score"] = round(

        breadth["Breadth_Percent"]

        *

        (breadth["Avg_Strong_RS"] / 100)

        *

        breadth["Total_Stocks"].apply(

            lambda x: math.log(x + 1)

        ),

        2

    )


    # ==========================================
    # SORT BY WEIGHTED SCORE
    # ==========================================

    breadth = breadth.sort_values(

        "Weighted_Breadth_Score",

        ascending=False

    )


    return breadth
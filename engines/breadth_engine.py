import math


def build_theme_breadth(stocks):

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

        .size()

        .reset_index(name="Strong_Stocks")

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

        breadth["Breadth_Percent"] *

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
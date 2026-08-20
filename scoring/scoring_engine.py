import pandas as pd


# ----------------------------
# RS RAW SCORE
# ----------------------------

# ----------------------------
# RS RAW SCORE V2
# ----------------------------

def calculate_rs_raw(stocks):

    stocks["RS_Raw"] = (

        stocks["% Price Change (12 Weeks)"] * 0.35 +

        stocks["% Price Change (4 Weeks)"] * 0.30 +

        stocks["Relative Price Change (YTD)"] * 0.15 +

        stocks["Price as a % of 52 Wk H-L Range"] * 0.15 +

        stocks["% Price Change (1 Week)"] * 0.05

    )

    return stocks


# ----------------------------
# RS RATING
# ----------------------------

def assign_rs(percentile):

    if percentile >= 99:
        return 99
    elif percentile >= 98:
        return 98
    elif percentile >= 97:
        return 97
    elif percentile >= 95:
        return 95
    elif percentile >= 90:
        return 90
    elif percentile >= 80:
        return 80
    elif percentile >= 70:
        return 70
    elif percentile >= 60:
        return 60
    elif percentile >= 50:
        return 50
    elif percentile >= 40:
        return 40
    elif percentile >= 30:
        return 30
    elif percentile >= 20:
        return 20
    elif percentile >= 10:
        return 10
    else:
        return 1


def calculate_rs_rating(stocks):

    stocks = stocks.sort_values(
        "RS_Raw",
        ascending=False
    ).reset_index(drop=True)

    total = len(stocks)

    stocks["Percentile"] = (

        (1 - (stocks.index / total)) * 100
    )

    stocks["RS_Rating"] = (

        stocks["Percentile"]

        .apply(assign_rs)
    )

    # NEW FIELD FOR SHORT ENGINE ONLY

    stocks["Weakness_Score"] = (

        100 - stocks["Percentile"]

    )

    return stocks



# ----------------------------
# SALES SCORE
# ----------------------------

def sales_score(growth):

    if growth >= 50:
        return 100
    elif growth >= 30:
        return 90
    elif growth >= 20:
        return 80
    elif growth >= 10:
        return 70
    elif growth >= 0:
        return 60
    else:
        return 40


def calculate_sales_score(stocks):

    stocks["Sales_Score"] = (

        stocks["Sales Growth F(0)/F(-1)"]

        .apply(sales_score)
    )

    return stocks


# ----------------------------
# ZACKS SCORE
# ----------------------------

def zacks_score(rank):

    if rank == 1:
        return 100
    elif rank == 2:
        return 85
    elif rank == 3:
        return 60
    elif rank == 4:
        return 40
    elif rank == 5:
        return 20
    else:
        return 40


def calculate_zacks_score(stocks):

    stocks["Zacks_Score"] = (

        stocks["Zacks Rank"]

        .apply(zacks_score)
    )

    return stocks


# ----------------------------
# MARGIN SCORE
# ----------------------------

def margin_score(p):

    if p >= 0.80:
        return 100
    elif p >= 0.60:
        return 80
    elif p >= 0.40:
        return 70
    elif p >= 0.20:
        return 60
    else:
        return 40


def calculate_margin_score(stocks):

    stocks["Margin_Percentile"] = (

        stocks["Net Margin %"]

        .rank(pct=True)
    )

    stocks["Margin_Score"] = (

        stocks["Margin_Percentile"]

        .apply(margin_score)
    )

    return stocks
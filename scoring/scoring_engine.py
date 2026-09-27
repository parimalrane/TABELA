import pandas as pd


# ----------------------------
# RS RAW SCORE
# ----------------------------

# ----------------------------
# RS RAW SCORE V2
# ----------------------------

from config.config import RS_RAW_WEIGHTS

def calculate_rs_raw(stocks):

    # Start with a series of zeros
    stocks["RS_Raw"] = 0.0
    for column, weight in RS_RAW_WEIGHTS.items():
        if column in stocks.columns:
            stocks["RS_Raw"] += stocks[column].fillna(0) * weight

    return stocks


# ----------------------------
# RS RATING
# ----------------------------

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

        stocks["Percentile"].clip(lower=1.0, upper=99.0).round().astype(int)

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

def zacks_score_legacy(rank):

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

def zacks_score_momentum(rank):
    # Using Fibonacci Retracement Levels
    if rank == 1:
        return 100.0
    elif rank == 2:
        return 78.6
    elif rank == 3:
        return 61.8
    elif rank == 4:
        return 38.2
    elif rank == 5:
        return -61.8
    else:
        return 38.2


def calculate_zacks_score(stocks):
    stocks["Zacks_Score_Legacy"] = stocks["Zacks Rank"].apply(zacks_score_legacy)
    stocks["Zacks_Score_Momentum"] = stocks["Zacks Rank"].apply(zacks_score_momentum)
    # Default to legacy for compatibility with obsolete files
    stocks["Zacks_Score"] = stocks["Zacks_Score_Legacy"]
    return stocks

# ----------------------------
# GROWTH SCORE
# ----------------------------

def growth_score(grade):
    grade = str(grade).strip().upper()
    # Using Fibonacci Retracement Levels
    if grade == 'A':
        return 100.0
    elif grade == 'B':
        return 78.6
    elif grade == 'C':
        return 61.8
    elif grade == 'D':
        return 38.2
    else:
        return 0.0

def calculate_growth_score(stocks):
    if "Growth Score" in stocks.columns:
        stocks["Growth_Score"] = stocks["Growth Score"].apply(growth_score)
    else:
        stocks["Growth_Score"] = 0.0
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
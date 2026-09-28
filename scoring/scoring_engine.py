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
# ZACKS SCORE
# ----------------------------

def zacks_score(rank):
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
    stocks["Zacks_Score"] = stocks["Zacks Rank"].apply(zacks_score)
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
        stocks["Growth_Score"] = stocks["Growth Score"].fillna('C').apply(growth_score)
    else:
        stocks["Growth_Score"] = growth_score('C')
    return stocks
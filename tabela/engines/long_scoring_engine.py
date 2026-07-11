# engines/long_scoring_engine.py

from core.config import LONG_WEIGHTS


def calculate_long_score(stocks):

    stocks["Long_Score"] = (

        stocks["RS_Rating"] * LONG_WEIGHTS["RS_WEIGHT"]

        + stocks["Theme_Score"] * LONG_WEIGHTS["THEME_WEIGHT"]

        + stocks["Sales_Score"] * LONG_WEIGHTS["SALES_WEIGHT"]

        + stocks["Zacks_Score"] * LONG_WEIGHTS["ZACKS_WEIGHT"]

        + stocks["Margin_Score"] * LONG_WEIGHTS["MARGIN_WEIGHT"]

    )

    return stocks
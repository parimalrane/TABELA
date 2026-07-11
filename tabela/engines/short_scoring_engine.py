# engines/short_scoring_engine.py

from core.config import SHORT_WEIGHTS


def calculate_short_score(stocks):

    stocks["RS_Weakness"] = 100 - stocks["RS_Rating"]

    stocks["Theme_Weakness"] = 100 - stocks["Theme_Score"]

    stocks["Zacks_Weakness"] = 100 - stocks["Zacks_Score"]

    stocks["Margin_Weakness"] = 100 - stocks["Margin_Score"]


    stocks["Short_Score"] = (

        stocks["RS_Weakness"] * SHORT_WEIGHTS["RS_WEIGHT"]

        + stocks["Theme_Weakness"] * SHORT_WEIGHTS["THEME_WEIGHT"]

        + stocks["Zacks_Weakness"] * SHORT_WEIGHTS["ZACKS_WEIGHT"]

        + stocks["Margin_Weakness"] * SHORT_WEIGHTS["MARGIN_WEIGHT"]

    )

    return stocks
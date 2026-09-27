# engines/long_scoring_engine.py

from config.config import LONG_WEIGHTS


def calculate_long_score(stocks):
    if "Growth Score" in stocks.columns:
        # Live CANSLIM Logic
        stocks["Long_Score"] = (
            stocks["RS_Rating"] * LONG_WEIGHTS["RS_WEIGHT"]
            + stocks["Theme_Score"] * LONG_WEIGHTS["THEME_WEIGHT"]
            + stocks["Zacks_Score_Momentum"] * LONG_WEIGHTS["ZACKS_WEIGHT_MOMENTUM"]
            + stocks["Growth_Score"] * LONG_WEIGHTS["GROWTH_WEIGHT"]
        )
    else:
        # Historical Regression Fallback
        stocks["Long_Score"] = (
            stocks["RS_Rating"] * LONG_WEIGHTS["RS_WEIGHT"]
            + stocks["Theme_Score"] * LONG_WEIGHTS["THEME_WEIGHT"]
            + stocks["Sales_Score"] * LONG_WEIGHTS["SALES_WEIGHT"]
            + stocks["Zacks_Score_Legacy"] * LONG_WEIGHTS["ZACKS_WEIGHT_LEGACY"]
            + stocks["Margin_Score"] * LONG_WEIGHTS["MARGIN_WEIGHT"]
        )
    
    return stocks
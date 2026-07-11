from core.config import COMPOSITE_WEIGHTS


def calculate_composite_score(stocks):

    rs_weight = COMPOSITE_WEIGHTS["RS_WEIGHT"]
    theme_weight = COMPOSITE_WEIGHTS["THEME_WEIGHT"]
    margin_weight = COMPOSITE_WEIGHTS["MARGIN_WEIGHT"]
    zacks_weight = COMPOSITE_WEIGHTS["ZACKS_WEIGHT"]

    # Remaining weight automatically goes to Sales Score
    sales_weight = 1 - (
        rs_weight +
        theme_weight +
        margin_weight +
        zacks_weight
    )

    stocks["Composite_Score"] = (

        stocks["RS_Rating"] * rs_weight +

        stocks["Theme_Score"] * theme_weight +

        stocks["Sales_Score"] * sales_weight +

        stocks["Zacks_Score"] * zacks_weight +

        stocks["Margin_Score"] * margin_weight

    )

    return stocks
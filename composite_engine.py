def calculate_composite_score(stocks):

    stocks["Composite_Score"] = (

        stocks["Theme_Score"] * 0.40 +

        stocks["RS_Rating"] * 0.30 +

        stocks["Sales_Score"] * 0.20 +

        stocks["Zacks_Score"] * 0.07 +

        stocks["Margin_Score"] * 0.03

    )

    return stocks
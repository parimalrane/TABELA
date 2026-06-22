import pandas as pd


# ---------------------------------------------------
# ETF Valid Categories
# ---------------------------------------------------
VALID_CATEGORIES = [

    "Technology ETFs",

    "Broad Emerging Market ETFs",

    "Materials ETFs",

    "Industrials ETFs",

    "Real Estate ETFs",

    "Energy ETFs",

    "Financials ETFs",

    "Health Care ETFs",

    "Utilities/Infrastructure ETFs",

    "Artificial Intelligence and Robotics ETF",

    "MLP ETFs",

    "Communication Services ETFs",

    "Alternative Energy ETFs",

    "Consumer Staples ETFs",

    "Consumer Discretionary ETFs",

    "European Equity ETFs",

    "Asia-Pacific (Developed) ETFs",

    "Asia-Pacific (Emerging) ETFs",

    "Latin American Equity ETFs",

    "Canadian Equity ETFs",

    "Africa-Middle East Equity ETFs",

    "Frontier Markets",

    "Marijuana ETFs"
]


# ETF types to exclude
EXCLUDE_KEYWORDS = [
    "Bond",
    "Treasury",
    "Currency",
    "Volatility",
    "Inverse",
    "Ultra",
    "Leveraged",
    "Commodity",
    "Hedged",
    # remove "Cash",
    "Short",

    # add these
    "Derivative",
    "Option",
    "Options",
    "Covered Call",
    "Income Strategy",
    "Buffer",
    "Defined Outcome"
]



# ---------------------------------------------------
# ETF Relative Strength Score
# ---------------------------------------------------
def calculate_etf_rs(df):

    df["ETF_RS_Raw"] = (

        df["Performance 3M (%)"] * 0.35 +

        df["Performance 1M (%)"] * 0.30 +

        df["Performance 6M (%)"] * 0.20 +

        df["Performance 1Y (%)"] * 0.10 +

        df["Performance 1W (%)"] * 0.05

    )

    return df


# ---------------------------------------------------
# ETF Classification
# ---------------------------------------------------
def assign_theme_score(df):

    df = df.sort_values("ETF_RS_Raw", ascending=False)

    total = len(df)

    q1 = int(total * 0.25)
    q2 = int(total * 0.50)
    q3 = int(total * 0.75)

    theme_class = []

    for i in range(total):

        if i < q1:
            theme_class.append("Leading")

        elif i < q2:
            theme_class.append("Emerging")

        elif i < q3:
            theme_class.append("Weakening")

        else:
            theme_class.append("Lagging")

    df["Theme_Class"] = theme_class

    return df

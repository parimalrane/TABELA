import pandas as pd




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

import pandas as pd




# ---------------------------------------------------
# ETF Relative Strength Score
# ---------------------------------------------------
def calculate_etf_rs(df):

    period_weights = {
        "Performance 3M (%)": 0.35,
        "Performance 1M (%)": 0.30,
        "Performance 6M (%)": 0.20,
        "Performance 1Y (%)": 0.10,
        "Performance 1W (%)": 0.05,
    }

    shorter_periods = {
        "Performance 3M (%)": ["Performance 1M (%)", "Performance 1W (%)"],
        "Performance 6M (%)": ["Performance 3M (%)", "Performance 1M (%)", "Performance 1W (%)"],
        "Performance 1Y (%)": ["Performance 6M (%)", "Performance 3M (%)", "Performance 1M (%)", "Performance 1W (%)"],
    }

    def score_row(row):
        available_values = {}

        for period, weight in period_weights.items():
            value = pd.to_numeric(row[period], errors="coerce")

            if pd.isna(value):
                continue

            if period in shorter_periods and value == 0.0:
                if any(
                    not pd.isna(pd.to_numeric(row[shorter_period], errors="coerce"))
                    and pd.to_numeric(row[shorter_period], errors="coerce") != 0.0
                    for shorter_period in shorter_periods[period]
                ):
                    continue

            available_values[period] = (value, weight)

        if not available_values:
            return 0.0

        total_weight = sum(weight for _, weight in available_values.values())

        return sum(
            value * (weight / total_weight)
            for value, weight in available_values.values()
        )

    df["ETF_RS_Raw"] = df.apply(score_row, axis=1)

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

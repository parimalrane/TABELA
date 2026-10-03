import pandas as pd

from config.config import THEME_STRENGTH_CONFIG



# ---------------------------------------------------
# ETF Relative Strength Score
# ---------------------------------------------------
def calculate_etf_rs(df):

    # Use the same period weights as the Theme Strength engine
    # to ensure mathematical coherence across the entire pipeline.
    period_weights = dict(THEME_STRENGTH_CONFIG["PERIOD_WEIGHTS"])

    shorter_periods = {
        "Performance 3M (%)": ["Performance 1M (%)", "Performance 1W (%)"],
        "Performance 6M (%)": ["Performance 3M (%)", "Performance 1M (%)", "Performance 1W (%)"],
        "Performance 1Y (%)": ["Performance 6M (%)", "Performance 3M (%)", "Performance 1M (%)", "Performance 1W (%)"],
    }

    def score_row(row):
        available_values = {}

        for period, weight in period_weights.items():
            val_str = str(row[period]).replace('%', '').replace('$', '').replace(',', '').strip()
            if val_str.startswith('(') and val_str.endswith(')'):
                val_str = '-' + val_str[1:-1]
            value = pd.to_numeric(val_str, errors="coerce")

            if pd.isna(value):
                continue

            if period in shorter_periods and value == 0.0:
                short_valid = False
                for shorter_period in shorter_periods[period]:
                    s_val = str(row[shorter_period]).replace('%', '').replace('$', '').replace(',', '').strip()
                    if s_val.startswith('(') and s_val.endswith(')'):
                        s_val = '-' + s_val[1:-1]
                    s_num = pd.to_numeric(s_val, errors="coerce")
                    if pd.notna(s_num) and s_num != 0.0:
                        short_valid = True
                        break
                if short_valid:
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

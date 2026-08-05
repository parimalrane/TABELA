import pandas as pd

def build_institutional_leaders(stocks):
    """
    Identifies elite institutional leaders purely on objective merit.
    No artificial padding or capping enforced.
    """

    # ==========================================
    # ELITE INSTITUTIONAL LEADERS
    # ==========================================
    
    strong_themes = stocks[
        stocks["Theme_Class"].isin(["Leading"])
    ]

    theme_leaders = strong_themes[
        (strong_themes["Composite_Score"] >= 90)
        |
        (strong_themes["RS_Rating"] >= 95)
    ].copy()

    if theme_leaders.empty:
        return pd.DataFrame(columns=stocks.columns)

    leaders_df = theme_leaders.sort_values(
        "Composite_Score",
        ascending=False
    ).reset_index(drop=True)

    return leaders_df
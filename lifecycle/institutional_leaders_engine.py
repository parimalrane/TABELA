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

    from config.config import INSTITUTIONAL_LEADERS_FILTERS
    
    min_comp = INSTITUTIONAL_LEADERS_FILTERS.get("MIN_COMPOSITE_SCORE", 90)
    min_rs = INSTITUTIONAL_LEADERS_FILTERS.get("MIN_RS", 95)

    theme_leaders = strong_themes[
        (strong_themes["Composite_Score"] >= min_comp)
        |
        (strong_themes["RS_Rating"] >= min_rs)
    ].copy()

    if theme_leaders.empty:
        return pd.DataFrame(columns=stocks.columns)

    leaders_df = theme_leaders.sort_values(
        "Composite_Score",
        ascending=False
    ).reset_index(drop=True)

    return leaders_df
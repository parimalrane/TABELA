import math
import pandas as pd

def build_theme_breadth(stocks, long_candidates, distribution_watchlist):

    # ==========================================
    # DEFINE STRONG STOCKS (For aggregate breadth stats only)
    # ==========================================

    s_rs = 80
    s_long = 80

    strong_stocks = stocks[

        (stocks["RS_Rating"] >= s_rs)

        &

        (stocks["Long_Score"] >= s_long)

    ].copy()

    # ==========================================
    # TOP LEADERS PER THEME (Sourced from shared state long_candidates)
    # ==========================================

    # True Longs
    true_long_tickers = set(stocks[stocks["Is_Long_Candidate"]]["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper())
    
    # Remove re-entry prefix appending (stateless rebuild)
    formatted_longs = long_candidates[long_candidates["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper().isin(true_long_tickers)].copy()
    
    true_longs_series = (
        formatted_longs
        .sort_values(["Long_Score", "RS_Rating"], ascending=[False, False])
        .groupby("Mapped_Theme")["Ticker"]
        .apply(lambda s: ", ".join(s.astype(str).str.replace("*", "", regex=False)))
    )

    # Pre-Observation (Deprecated)
    pre_obs_series = pd.Series(dtype=str)

    # Observation
    obs_series = pd.Series(dtype=str)
        
    # Distribution
    if not distribution_watchlist.empty:
        dist_series = (
            distribution_watchlist
            .sort_values("Ticker")
            .groupby("Mapped_Theme")["Ticker"]
            .apply(lambda s: ", ".join(f"#{t}" for t in s.astype(str).str.replace("*", "", regex=False)))
        )
    else:
        dist_series = pd.Series(dtype=str)

    # Combine All States
    all_themes = set(true_longs_series.index) | set(pre_obs_series.index) | set(obs_series.index) | set(dist_series.index)
    combined_leaders = {}
    for t in all_themes:
        parts = []
        if t in true_longs_series and true_longs_series[t]: parts.append(true_longs_series[t])
        if t in pre_obs_series and pre_obs_series[t]: parts.append(pre_obs_series[t])
        if t in obs_series and obs_series[t]: parts.append(obs_series[t])
        if t in dist_series and dist_series[t]: parts.append(dist_series[t])
        combined_leaders[t] = ", ".join(parts)
        
    leaders_by_theme = pd.Series(combined_leaders).rename_axis("Mapped_Theme").reset_index(name="Leaders")

    # ==========================================
    # TOTAL STOCKS PER THEME
    # ==========================================

    total_by_theme = (

        stocks

        .groupby("Mapped_Theme")

        .size()

        .reset_index(name="Total_Stocks")

    )

    # ==========================================
    # STRONG STOCKS PER THEME
    # ==========================================

    strong_by_theme = (

        strong_stocks

        .groupby("Mapped_Theme")

        .agg(

            Strong_Stocks=("Mapped_Theme", "size"),

            Avg_Strong_RS=("RS_Rating", "mean"),

        )

        .reset_index()

    )

    # ==========================================
    # MERGE
    # ==========================================

    breadth = (

        total_by_theme

        .merge(

            strong_by_theme,

            on="Mapped_Theme",

            how="left",

        )

        .merge(

            leaders_by_theme,

            on="Mapped_Theme",

            how="left",

        )

    )

    breadth["Strong_Stocks"] = breadth["Strong_Stocks"].fillna(0)
    breadth["Avg_Strong_RS"] = breadth["Avg_Strong_RS"].fillna(0)
    breadth["Leaders"] = breadth["Leaders"].fillna("")

    # ==========================================
    # STANDARD BREADTH %
    # ==========================================

    breadth["Breadth_Percent"] = round(

        (breadth["Strong_Stocks"] / breadth["Total_Stocks"]) * 100,

        2,

    )

    # ==========================================
    # WEIGHTED BREADTH SCORE
    # ==========================================

    breadth["Weighted_Breadth_Score"] = round(

        breadth["Breadth_Percent"]

        *

        (breadth["Avg_Strong_RS"] / 100)

        *

        breadth["Total_Stocks"].apply(

            lambda x: math.log(x + 1)

        ),

        2,

    )

    # ==========================================
    # SORT
    # ==========================================

    breadth = breadth.sort_values(

        "Weighted_Breadth_Score",

        ascending=False,

    )

    return breadth

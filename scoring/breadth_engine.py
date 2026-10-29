import math
import pandas as pd

def build_theme_breadth(stocks, long_candidates, distribution_watchlist):

    # ==========================================
    # DEFINE STRONG STOCKS (For aggregate breadth stats only)
    # ==========================================

    from config.config import LONG_ENTRY, SHORT_ENTRY
    s_rs = LONG_ENTRY.get("MIN_RS", 80.0)
    s_long = LONG_ENTRY.get("MIN_LONG_SCORE", 80.0)

    s_rs = LONG_ENTRY.get("MIN_RS", 80.0)
    s_long = LONG_ENTRY.get("MIN_LONG_SCORE", 80.0)
    allowed_long_themes = LONG_ENTRY.get("THEMES", ["Leading", "Unclassified Leader"])
    s_short_max_score = SHORT_ENTRY.get("MAX_SHORT_SCORE", 25.0)
    s_short_min_rs = SHORT_ENTRY.get("MIN_SHORT_RS", 15.0)
    s_short_max_rs = SHORT_ENTRY.get("MAX_SHORT_RS", 60.0)

    stocks = stocks.copy()
    stocks["Qual_Strength"] = 0.0
    stocks["Is_Qual"] = False

    is_long_cand = stocks["Is_Long_Candidate"] if "Is_Long_Candidate" in stocks.columns else False
    long_mask = is_long_cand | (
        (stocks["RS_Rating"] >= s_rs) & (stocks["Long_Score"] >= s_long) & (stocks["Theme_Class"].isin(allowed_long_themes))
    )
    stocks.loc[long_mask, "Is_Qual"] = True
    stocks.loc[long_mask, "Qual_Strength"] = stocks.loc[long_mask, "RS_Rating"]

    is_short_cand = stocks["Is_Short_Candidate"] if "Is_Short_Candidate" in stocks.columns else False
    short_score_col = stocks["Short_Score"] if "Short_Score" in stocks.columns else pd.Series(999, index=stocks.index)
    short_rs_col = stocks["Short_RS_Rating"] if "Short_RS_Rating" in stocks.columns else pd.Series(999, index=stocks.index)

    short_mask = is_short_cand | (
        (short_score_col <= s_short_max_score) & (short_rs_col >= s_short_min_rs) & (short_rs_col <= s_short_max_rs) & (stocks["Theme_Class"] == "Lagging")
    )
    stocks.loc[short_mask, "Is_Qual"] = True
    stocks.loc[short_mask, "Qual_Strength"] = (100.0 - pd.to_numeric(short_rs_col.loc[short_mask], errors="coerce")).fillna(50.0)

    strong_stocks = stocks[stocks["Is_Qual"]].copy()
    _legacy_ignore = stocks[

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

            Avg_Strong_RS=("Qual_Strength", "mean"),

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

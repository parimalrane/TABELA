import pandas as pd
from etf_engine import (
    filter_valid_etfs,
    calculate_etf_rs,
    assign_theme_score
)
from stock_mapper import map_stock_theme
from company_theme_engine import COMPANY_THEME
from theme_translation_engine import THEME_TRANSLATION

from scoring_engine import (
    calculate_rs_raw,
    calculate_rs_rating,
    calculate_sales_score,
    calculate_zacks_score,
    calculate_margin_score
)
from theme_parser import parse_theme
from composite_engine import calculate_composite_score
from watchlist_engine import build_long_watchlist
from short_engine import build_short_watchlist
from breadth_engine import build_theme_breadth
from institutional_leaders_engine import build_institutional_leaders
from watchlist_engine import build_long_watchlist
from short_engine import build_short_watchlist


# LOAD FILES

stocks = pd.read_csv("stocks.csv")
etf_df = pd.read_csv("ETF.csv")


# ETF PROCESSING PIPELINE

etf_df = filter_valid_etfs(etf_df)


# CREATE THEME COLUMNS

etf_df[["Sector","Theme","Subtheme"]] = etf_df[
    "Investment Strategy"
].apply(
    lambda x: pd.Series(parse_theme(x))
)


# CONTINUE PIPELINE

etf_df = calculate_etf_rs(etf_df)

etf_df = assign_theme_score(etf_df)


# FINAL ETF MASTER DATASET

etf_master = etf_df.copy()


# ==========================================
# STEP 1 — BUILD THEME STRENGTH TABLE
# ==========================================

theme_strength = (

    etf_master

    .groupby("Theme")["ETF_RS_Raw"]

    .mean()

    .reset_index()
)

theme_strength = theme_strength[

    theme_strength["Theme"] != "Filtered"

]



theme_strength = theme_strength.sort_values(

    "ETF_RS_Raw",
    ascending=False

).reset_index(drop=True)

total_themes = len(theme_strength)


# ==========================================
# ASSIGN ETF THEME CLASSIFICATION
# ==========================================

theme_class_map = {}
theme_score_map = {}

for i, row in theme_strength.iterrows():

    percentile = (i + 1) / total_themes

    theme = row["Theme"]

    if percentile <= 0.25:

        theme_class = "Leading"
        theme_score = 100

    elif percentile <= 0.50:

        theme_class = "Emerging"
        theme_score = 75

    elif percentile <= 0.75:

        theme_class = "Weakening"
        theme_score = 40

    else:

        theme_class = "Lagging"
        theme_score = 20

    theme_class_map[theme] = theme_class
    theme_score_map[theme] = theme_score


# ==========================================
# STEP 2 — MAP STOCKS TO THEMES ONLY
# ==========================================

mapped_themes = []
etf_themes = []

for _, row in stocks.iterrows():

    ticker = row["Ticker"]

    # Priority 1 → Manual company mapping

    if ticker in COMPANY_THEME:

        stock_theme = COMPANY_THEME[ticker]

    else:

        stock_theme = map_stock_theme(

            row["Industry"],
            row["Sector"]
        )

    # Translate to ETF theme


    if stock_theme in THEME_TRANSLATION:

        etf_theme = THEME_TRANSLATION[stock_theme]

    else:

        etf_theme = stock_theme
    
    mapped_themes.append(stock_theme)
    etf_themes.append(etf_theme)


stocks["Mapped_Theme"] = mapped_themes
stocks["ETF_Theme"] = etf_themes


# ==========================================
# STEP 3 — STOCK SCORING ENGINE
# ==========================================

stocks = calculate_rs_raw(stocks)

stocks = calculate_rs_rating(stocks)

stocks = calculate_sales_score(stocks)

stocks = calculate_zacks_score(stocks)


# ==========================================
# STEP 4 — ASSIGN FINAL THEME SCORE
# ==========================================

theme_classes = []
theme_scores = []

for _, row in stocks.iterrows():

    etf_theme = row["ETF_Theme"]

    # Normal ETF classified stocks

    if etf_theme in theme_class_map:

        theme_class = theme_class_map[etf_theme]

        theme_score = theme_score_map[etf_theme]

    # Unknown theme stocks

    else:

        # Exceptional unknown stocks

        if (

            row["RS_Rating"] >= 90 and

            row["Sales_Score"] >= 80 and

            row["Zacks_Score"] >= 85
        ):

            theme_class = "Unclassified Leader"

            theme_score = 75

            print("UNCLASSIFIED LEADER:", row["Ticker"])

        else:

            theme_class = "Unknown"

            theme_score = 20

    theme_classes.append(theme_class)

    theme_scores.append(theme_score)


stocks["Theme_Class"] = theme_classes
stocks["Theme_Score"] = theme_scores


# ==========================================
# STEP 5 — MARGIN SCORE
# ==========================================

stocks = calculate_margin_score(stocks)


# ==========================================
# STEP 6 — COMPOSITE SCORE
# ==========================================

stocks = calculate_composite_score(stocks)


# ==========================================
# STEP 7 — BUILD LONG WATCHLIST
# ==========================================

long_watchlist = build_long_watchlist(stocks)


# ==========================================
# STEP 8 — BUILD SHORT WATCHLIST
# ==========================================

short_watchlist = build_short_watchlist(stocks)


# ==========================================
# STEP 9 — THEME BREADTH
# ==========================================
theme_breadth = build_theme_breadth(stocks)



# ==========================================
# FINAL OUTPUT — THEMEPULSE DAILY SCAN
# ==========================================

import datetime

today = datetime.date.today()

# sort outputs

long_watchlist = long_watchlist.sort_values(

    "Composite_Score",
    ascending=False
)

short_watchlist = short_watchlist.sort_values(

    "Composite_Score",
    ascending=True
)


institutional_leaders = build_institutional_leaders(stocks)



import pandas as pd

# ==========================================
# BUILD LONG CANDIDATE UNIVERSE
# ==========================================

# Get primary long tickers
long_tickers = set(long_watchlist["Ticker"])


# Combine both lists
long_candidates = pd.concat(

    [long_watchlist, institutional_leaders]

)


# Remove duplicates
long_candidates = long_candidates.drop_duplicates(

    subset="Ticker"

)


# Mark stocks added only through institutional flow
long_candidates["Ticker"] = long_candidates.apply(

    lambda row:

        row["Ticker"]

        if row["Ticker"] in long_tickers

        else row["Ticker"] + "*",

    axis=1

)


# Final sorting
long_candidates = long_candidates.sort_values(

    "Composite_Score",
    ascending=False

)

# ==========================================
# HEADER
# ==========================================

print("\n")
print("==============================================")
print("THEMEPULSE DAILY MARKET SCAN")
print("DATE:", today)
print("==============================================")
print("\n")


# ==========================================
# MARKET ROTATION SUMMARY
# ==========================================

print("MARKET ROTATION SUMMARY")
print("----------------------------")


print()

print(theme_strength.sort_values(

    "ETF_RS_Raw",

    ascending=False

).to_string(index=False))

print("\n\n")


print("\nLEADING THEMES")

print(

    theme_strength[

        theme_strength["Theme"].isin(

            [k for k, v in theme_class_map.items() if v == "Leading"]

        )

    ]["Theme"].tolist()

)

print("\nEMERGING THEMES")

print(

    theme_strength[

        theme_strength["Theme"].isin(

            [k for k, v in theme_class_map.items() if v == "Emerging"]

        )

    ]["Theme"].tolist()

)

print("\nWEAKENING THEMES")

print(

    theme_strength[

        theme_strength["Theme"].isin(

            [k for k, v in theme_class_map.items() if v == "Weakening"]

        )

    ]["Theme"].tolist()

)

print("\nLAGGING THEMES")

print(

    theme_strength[

        theme_strength["Theme"].isin(

            [k for k, v in theme_class_map.items() if v == "Lagging"]

        )

    ]["Theme"].tolist()

)

print("\n\n")


# ==========================================
# THEME BREADTH
# ==========================================

print("THEME BREADTH ANALYSIS")
print("----------------------------")

print(

    theme_breadth[[
        "Mapped_Theme",
        "Total_Stocks",
        "Strong_Stocks",
        "Breadth_Percent",
        "Weighted_Breadth_Score"
    ]]

    .head(20).to_string(index=False)

)

print("\n\n")


print("----------------------------")

# ==========================================
# SHORT CANDIDATE UNIVERSE
# ==========================================

print("LONG CANDIDATE UNIVERSE")
print("----------------------------")


print(

    long_candidates[[
        "Ticker",
        "Mapped_Theme",
        "Theme_Class",
        "RS_Rating",
        "Composite_Score"
    ]]

    .head(40).to_string(index=False)

    )

print("\n\n")

print()

print("----------------------------")

# ==========================================
# SHORT CANDIDATE UNIVERSE
# ==========================================

print("SHORT CANDIDATE UNIVERSE")
print("----------------------------")

print(

    short_watchlist[[
        "Ticker",
        "Mapped_Theme",
        "Theme_Class",
        "RS_Rating",
        "Composite_Score"
    ]]

    .head(20).to_string(index=False)

)

print("\n\n")


print("\n")
print("==============================================")
print("END OF THEMEPULSE SCAN")
print("==============================================")

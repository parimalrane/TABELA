import pandas as pd

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

from composite_engine import calculate_composite_score
from watchlist_engine import build_long_watchlist
from short_engine import build_short_watchlist

# ==========================================
# LOAD FILES
# ==========================================

stocks = pd.read_csv("stocks.csv")
etf_master = pd.read_csv("etf_master.csv")


# ==========================================
# STEP 1 — BUILD THEME STRENGTH TABLE
# ==========================================

theme_strength = (

    etf_master

    .groupby("Theme")["ETF_RS_Raw"]

    .mean()

    .reset_index()
)

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
# FINAL OUTPUT
# ==========================================

long_watchlist = long_watchlist.sort_values(

    "Composite_Score",
    ascending=False
)

print(

    short_watchlist[[
        "Ticker",
        "Mapped_Theme",
        "Theme_Class",
        "Theme_Score",
        "RS_Rating",
        "Composite_Score"
    ]]

    .head(50)
)

print("\n\n")

print(

    long_watchlist[[
        "Ticker",
        "Mapped_Theme",
        "Theme_Class",
        "Theme_Score",
        "RS_Rating",
        "Composite_Score"
    ]]

    .head(50)
)
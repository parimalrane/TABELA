import os
import pandas as pd
import datetime

from engines.etf_engine import (
    calculate_etf_rs,
    assign_theme_score
)

from core.stock_mapper import map_stock_theme
from core.company_theme_engine import COMPANY_THEME
from core.theme_translation_engine import THEME_TRANSLATION

from engines.scoring_engine import (
    calculate_rs_raw,
    calculate_rs_rating,
    calculate_sales_score,
    calculate_zacks_score,
    calculate_margin_score
)

from core.theme_parser import parse_theme
from engines.composite_engine import calculate_composite_score
from engines.watchlist_engine import build_long_watchlist
from engines.short_engine import build_short_watchlist
from engines.breadth_engine import build_theme_breadth
from engines.institutional_leaders_engine import build_institutional_leaders
from core.theme_hierarchy import THEME_PARENT_MAP
from engines.etf_filter import filter_valid_etfs
from engines.etf_filter import filter_institutional_etfs

# NEW IMPORT PATHS
from engines.snapshot_engine import save_daily_snapshot
from engines.rotation_engine import calculate_rotation_delta, print_rotation_report
from engines.stock_history_engine import save_stock_history
from engines.persistence_engine import print_persistence_report


# ==========================================
# PATH CONFIGURATION
# ==========================================

DATA_DIR = "market_data"

ETF_FILE = os.path.join(DATA_DIR, "ETF.csv")
STOCK_FILE = os.path.join(DATA_DIR, "stocks.csv")


# ==========================================
# DEBUG THEME AUDIT
# ==========================================

AUDIT_THEMES = [

    "Crude Oil",
    "Aerospace & Defense",
    "Software",
    "Banking"

]


print("\n")


# ==========================================
# LOAD STOCKS FILE
# ==========================================

stocks = pd.read_csv(STOCK_FILE)

stocks = stocks[
    stocks["Zacks Rank"].astype(str).str.startswith(
        ("1", "2", "3", "4", "5")
    )
].copy()


# ==========================================
# LOAD ETF FILE
# ==========================================

etf_df = pd.read_csv(ETF_FILE)


# ETF PROCESSING PIPELINE
etf_df = filter_valid_etfs(etf_df)
etf_df = filter_institutional_etfs(etf_df)


# CREATE THEME COLUMNS
etf_df[["Sector", "Theme", "Subtheme"]] = etf_df[
    "Investment Strategy"
].apply(
    lambda x: pd.Series(parse_theme(x))
)


# CONTINUE PIPELINE
etf_df = calculate_etf_rs(etf_df)
etf_df = assign_theme_score(etf_df)

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

    if ticker in COMPANY_THEME:

        stock_theme = COMPANY_THEME[ticker]

    else:

        stock_theme = map_stock_theme(
            row["Industry"],
            row["Sector"]
        )

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
    mapped_theme = row["Mapped_Theme"]

    if mapped_theme in THEME_PARENT_MAP:
        etf_theme = THEME_PARENT_MAP[mapped_theme]

    if etf_theme in theme_class_map:

        theme_class = theme_class_map[etf_theme]
        theme_score = theme_score_map[etf_theme]

    else:

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

save_stock_history(stocks)


# ==========================================
# STEP 7 — BUILD WATCHLISTS
# ==========================================

long_watchlist = build_long_watchlist(stocks)
short_watchlist = build_short_watchlist(stocks)


# ==========================================
# STEP 8 — THEME BREADTH
# ==========================================

theme_breadth = build_theme_breadth(stocks)


today = datetime.date.today()

long_watchlist = long_watchlist.sort_values(
    "Composite_Score",
    ascending=False
)

short_watchlist = short_watchlist.sort_values(
    "Composite_Score",
    ascending=True
)

institutional_leaders = build_institutional_leaders(stocks)


# ==========================================
# BUILD LONG CANDIDATES
# ==========================================

long_tickers = set(long_watchlist["Ticker"])

long_candidates = pd.concat(
    [long_watchlist, institutional_leaders]
)

long_candidates = long_candidates.drop_duplicates(
    subset="Ticker"
)

long_candidates["Ticker"] = long_candidates.apply(
    lambda row:
        row["Ticker"]
        if row["Ticker"] in long_tickers
        else row["Ticker"] + "*",
    axis=1
)

long_candidates = long_candidates.sort_values(
    "Composite_Score",
    ascending=False
)


# ==========================================
# OUTPUT
# ==========================================

print("\n")
print("==============================================")
print("TABELA DAILY MARKET SCAN")
print("DATE:", today)
print("==============================================")
print("\n")


leading_themes = theme_strength[
    theme_strength["Theme"].isin(
        [k for k, v in theme_class_map.items() if v == "Leading"]
    )
]["Theme"].tolist()

emerging_themes = theme_strength[
    theme_strength["Theme"].isin(
        [k for k, v in theme_class_map.items() if v == "Emerging"]
    )
]["Theme"].tolist()

weakening_themes = theme_strength[
    theme_strength["Theme"].isin(
        [k for k, v in theme_class_map.items() if v == "Weakening"]
    )
]["Theme"].tolist()

lagging_themes = theme_strength[
    theme_strength["Theme"].isin(
        [k for k, v in theme_class_map.items() if v == "Lagging"]
    )
]["Theme"].tolist()


print("MARKET ROTATION SUMMARY")
print("----------------------------")
print("\n")

print("\nLEADING THEMES")
print(leading_themes)

print("\nEMERGING THEMES")
print(emerging_themes)

print("\nWEAKENING THEMES")
print(weakening_themes)

print("\nLAGGING THEMES")
print(lagging_themes)

print("\n\n")

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

    .head(40).to_string(index=False)

)

print("\n")
print("----------------------------")
print("TRADINGVIEW WATCHLIST EXPORT")
print("----------------------------")

long_list = ",".join(
    long_candidates["Ticker"]
    .head(50)
    .astype(str)
    .tolist()
)

short_list = ",".join(
    short_watchlist["Ticker"]
    .head(50)
    .astype(str)
    .tolist()
)

print("###LONG," + long_list + ",")
print("###SHORT," + short_list)


save_daily_snapshot(
    leading_themes,
    emerging_themes,
    weakening_themes,
    lagging_themes,
    long_candidates,
    short_watchlist,
    len(stocks)
)

rotation_data = calculate_rotation_delta()
print_rotation_report(rotation_data)
print_persistence_report()



print("\n")
print("==============================================")
print("END OF TABELA SCAN")
print("==============================================")
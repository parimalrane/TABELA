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
from engines.watchlist_delta_engine import compare_watchlists
# NEW IMPORT PATHS
from engines.snapshot_engine import save_daily_snapshot
from engines.stock_history_engine import save_stock_history
from engines.long_scoring_engine import calculate_long_score
from engines.short_scoring_engine import calculate_short_score
from engines.unknown_classification_engine import save_unknown_classification
from engines.rotation_engine import (
    calculate_rotation_delta,
    print_rotation_report,
    save_rotation_delta
)


def normalize_theme(theme):
    if pd.isna(theme):
        return None
    return str(theme).strip().title()

# ==========================================
# PATH CONFIGURATION
# ==========================================

DATA_DIR = "market_data"

ETF_FILE = os.path.join(DATA_DIR, "ETF.csv")
STOCK_FILE = os.path.join(DATA_DIR, "stocks.csv")




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

theme_strength["Theme_Rank"] = range(
    1,
    len(theme_strength) + 1
)

total_themes = len(theme_strength)


# ==========================================
# ASSIGN ETF THEME CLASSIFICATION
# ==========================================

theme_class_map = {}
theme_score_map = {}
theme_rank_map = {}
theme_raw_score_map = {}

for i, row in theme_strength.iterrows():

    percentile = (i + 1) / total_themes
    theme = row["Theme"]
    theme_rank_map[theme] = i + 1
    theme_raw_score_map[theme] = round(row["ETF_RS_Raw"], 2)

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

stocks["ETF_Theme"] = stocks["ETF_Theme"].apply(
    normalize_theme
)

stocks["Theme_Rank"] = stocks["ETF_Theme"].map(
    theme_rank_map
)


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
stocks["Theme_State"] = stocks["ETF_Theme"].map(
    theme_class_map
)

stocks["ETF_Raw_Score"] = stocks["ETF_Theme"].map(
    theme_raw_score_map
)


# ==========================================
# STEP 5 — MARGIN SCORE
# ==========================================

stocks = calculate_margin_score(stocks)


# ==========================================
# STEP 6 — COMPOSITE SCORE
# ==========================================

stocks = calculate_composite_score(stocks)

stocks = calculate_long_score(stocks)

stocks = calculate_short_score(stocks)



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
    "Long_Score",
    ascending=False
)


short_watchlist = short_watchlist.sort_values(
    "Short_Score",
    ascending=False
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
    "Long_Score",
    ascending=False
)

stocks["Long_Rank"] = None
stocks["Short_Rank"] = None
stocks["Is_Long_Candidate"] = False
stocks["Is_Short_Candidate"] = False


for rank, ticker in enumerate(
    long_candidates["Ticker"],
    start=1
):

    clean_ticker = ticker.replace("*", "")

    stocks.loc[
        stocks["Ticker"] == clean_ticker,
        "Long_Rank"
    ] = rank

    stocks.loc[
        stocks["Ticker"] == clean_ticker,
        "Is_Long_Candidate"
    ] = True


for rank, ticker in enumerate(
    short_watchlist["Ticker"],
    start=1
):

    stocks.loc[
        stocks["Ticker"] == ticker,
        "Short_Rank"
    ] = rank

    stocks.loc[
        stocks["Ticker"] == ticker,
        "Is_Short_Candidate"
    ] = True

try:

    save_stock_history(stocks)

except Exception as e:

    print()
    print("STOCK HISTORY ERROR:", e)    

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
][["Theme", "Theme_Rank", "ETF_RS_Raw"]].to_dict("records")


emerging_themes = theme_strength[
    theme_strength["Theme"].isin(
        [k for k, v in theme_class_map.items() if v == "Emerging"]
    )
][["Theme", "Theme_Rank", "ETF_RS_Raw"]].to_dict("records")


weakening_themes = theme_strength[
    theme_strength["Theme"].isin(
        [k for k, v in theme_class_map.items() if v == "Weakening"]
    )
][["Theme", "Theme_Rank", "ETF_RS_Raw"]].to_dict("records")


lagging_themes = theme_strength[
    theme_strength["Theme"].isin(
        [k for k, v in theme_class_map.items() if v == "Lagging"]
    )
][["Theme", "Theme_Rank", "ETF_RS_Raw"]].to_dict("records")


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
        "Long_Score"
    ]]

    .head(21).to_string(index=False)

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
        "Short_Score"
    ]]
    
    .head(21).to_string(index=False)

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

compare_watchlists(
    long_candidates["Ticker"].head(50).tolist(),
    short_watchlist["Ticker"].head(50).tolist()
)


# ==========================================
# SNAPSHOT METADATA
# ==========================================

total_stock_count = len(stocks)

classified_stock_count = len(

    stocks[
        stocks["Theme_Class"] != "Unknown"
    ]

)

unclassified_stock_count = len(

    stocks[
        stocks["Theme_Class"] == "Unknown"
    ]

)

# ==========================================
# OPTIONAL INTELLIGENCE LAYER
# ==========================================

try:

    save_daily_snapshot(
        leading_themes,
        emerging_themes,
        weakening_themes,
        lagging_themes,
        total_stock_count,
        classified_stock_count,
        unclassified_stock_count,
        theme_breadth
    )

    rotation_data = calculate_rotation_delta()

    save_rotation_delta(rotation_data)

    print_rotation_report(rotation_data)

except Exception as e:

    print()
    print("INTELLIGENCE LAYER ERROR:", e)



try:

    save_unknown_classification(stocks)

except Exception as e:

    print()

    print("UNKNOWN CLASSIFICATION ERROR:", e)

print("\n")
print("==============================================")
print("END OF TABELA SCAN")
print("==============================================")
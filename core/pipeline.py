import datetime
import math
import os

import pandas as pd

from core.company_theme_engine import COMPANY_THEME
from core.config import THEME_STRENGTH_CONFIG
from core.industry_theme_engine import INDUSTRY_THEME
from core.stock_mapper import map_stock_theme
from core.theme_hierarchy import THEME_PARENT_MAP
from core.theme_parser import parse_theme
from core.theme_translation_engine import THEME_TRANSLATION
from engines.breadth_engine import build_theme_breadth
from engines.composite_engine import calculate_composite_score
from engines.etf_engine import assign_theme_score, calculate_etf_rs
from engines.etf_filter import (
    filter_etfs_with_sufficient_history,
    filter_institutional_etfs,
    filter_valid_etfs,
)
from engines.historical_intelligence_engine import build_historical_intelligence_report
from engines.institutional_leaders_engine import build_institutional_leaders
from engines.long_scoring_engine import calculate_long_score
from engines.rotation_engine import (
    calculate_rotation_delta,
    print_rotation_report,
    save_rotation_delta,
)
from engines.scoring_engine import (
    calculate_margin_score,
    calculate_rs_raw,
    calculate_rs_rating,
    calculate_sales_score,
    calculate_zacks_score,
)
from engines.short_engine import build_short_watchlist
from engines.short_scoring_engine import calculate_short_score
from engines.snapshot_engine import save_daily_snapshot
from engines.stock_history_engine import save_stock_history
from engines.unknown_classification_engine import save_unknown_classification
from engines.watchlist_delta_engine import compare_watchlists
from engines.watchlist_engine import build_long_watchlist


DATA_DIR = "market_data"
ETF_FILE = os.path.join(DATA_DIR, "ETF.csv")
STOCK_FILE = os.path.join(DATA_DIR, "stocks.csv")


def normalize_theme(theme):

    if pd.isna(theme):
        return None

    theme = str(theme).strip()

    normalization_map = {

        "natural gas": "Natural Gas",
        "Natural Gas": "Natural Gas",

        "broad": "Broad",
        "Broad": "Broad",

        "mlp": "MLP",
        "MLP": "MLP",

        "reits": "REITs",
        "REITs": "REITs"

    }

    return normalization_map.get(theme, theme)


def print_theme_group(title, themes):
    print(f"\n{title}")
    print("-" * 65)
    print(f"{'Rank':<6} {'Theme':<40} {'ETF Strength':>12}")
    print("-" * 65)

    for item in themes:
        print(
            f"{item['Theme_Rank']:<6} "
            f"{item['Theme']:<40} "
            f"{item['ETF_RS_Raw']:>12.2f}"
        )


def _period_label(period_name):
    return (
        str(period_name)
        .replace("Performance", "")
        .replace("(%)", "")
        .strip()
        .replace(" ", "")
    )


def get_theme_strength_settings():
    config = dict(THEME_STRENGTH_CONFIG)

    benchmark_ticker = str(config.get("BENCHMARK_TICKER", "")).strip().upper()
    period_weights = dict(config.get("PERIOD_WEIGHTS", {}))
    aggregation_mode = str(config.get("AGGREGATION_MODE", "")).strip().lower()
    enable_normalization = bool(config.get("ENABLE_NORMALIZATION", True))
    debug_theme_strength = bool(config.get("DEBUG_THEME_STRENGTH", False))

    if not benchmark_ticker:
        raise ValueError("THEME_STRENGTH_CONFIG.BENCHMARK_TICKER must be set.")

    if not period_weights:
        raise ValueError("THEME_STRENGTH_CONFIG.PERIOD_WEIGHTS must be set.")

    if aggregation_mode not in {"aum_weighted", "equal_weight"}:
        raise ValueError(
            "THEME_STRENGTH_CONFIG.AGGREGATION_MODE must be 'aum_weighted' or 'equal_weight'."
        )

    period_labels = {
        period: _period_label(period)
        for period in period_weights
    }

    return {
        "benchmark_ticker": benchmark_ticker,
        "period_weights": period_weights,
        "period_labels": period_labels,
        "aggregation_mode": aggregation_mode,
        "enable_normalization": enable_normalization,
        "debug_theme_strength": debug_theme_strength,
    }


def print_theme_strength_diagnostics(theme_strength):
    # Temporary diagnostics block for Theme Strength transparency.
    diagnostics_columns = [
        "Theme",
        "Rel_1D",
        "Rel_1W",
        "Rel_1M",
        "Rel_3M",
        "WgtContr_1D",
        "WgtContr_1W",
        "WgtContr_1M",
        "WgtContr_3M",
        "ContrPct_1D",
        "ContrPct_1W",
        "ContrPct_1M",
        "ContrPct_3M",
        "Dominant_Driver",
        "ETF_RS_Raw",
        "Theme_Strength_Normalized",
        "Theme_Rank",
    ]

    available_columns = [
        column for column in diagnostics_columns
        if column in theme_strength.columns
    ]

    if not available_columns:
        return

    diagnostics_df = theme_strength.sort_values("Theme_Rank").copy()

    contribution_periods = ["1D", "1W", "1M", "3M"]

    for period in contribution_periods:
        wgt_column = f"WgtContr_{period}"
        pct_column = f"ContrPct_{period}"

        if wgt_column in diagnostics_df.columns:
            diagnostics_df[pct_column] = diagnostics_df.apply(
                lambda row: (
                    (pd.to_numeric(row.get(wgt_column), errors="coerce")
                     / pd.to_numeric(row.get("ETF_RS_Raw"), errors="coerce")) * 100.0
                )
                if pd.notna(pd.to_numeric(row.get("ETF_RS_Raw"), errors="coerce"))
                and pd.to_numeric(row.get("ETF_RS_Raw"), errors="coerce") != 0
                and pd.notna(pd.to_numeric(row.get(wgt_column), errors="coerce"))
                else 0.0,
                axis=1,
            )

    def resolve_dominant_driver(row):
        period_contributions = {}
        for period in contribution_periods:
            wgt_value = pd.to_numeric(row.get(f"WgtContr_{period}"), errors="coerce")
            period_contributions[period] = 0.0 if pd.isna(wgt_value) else float(wgt_value)

        if not period_contributions:
            return "N/A"

        return max(period_contributions, key=lambda period: abs(period_contributions[period]))

    diagnostics_df["Dominant_Driver"] = diagnostics_df.apply(resolve_dominant_driver, axis=1)

    available_columns = [
        column for column in diagnostics_columns
        if column in diagnostics_df.columns
    ]
    diagnostics_df = diagnostics_df[available_columns]

    numeric_columns = [
        "Rel_1D",
        "Rel_1W",
        "Rel_1M",
        "Rel_3M",
        "WgtContr_1D",
        "WgtContr_1W",
        "WgtContr_1M",
        "WgtContr_3M",
        "ContrPct_1D",
        "ContrPct_1W",
        "ContrPct_1M",
        "ContrPct_3M",
        "ETF_RS_Raw",
        "Theme_Strength_Normalized",
    ]

    for column in numeric_columns:
        if column in diagnostics_df.columns:
            diagnostics_df[column] = pd.to_numeric(
                diagnostics_df[column], errors="coerce"
            ).round(4)

    print("\n")
  #  print("THEME STRENGTH DIAGNOSTICS (TEMP - ALL THEMES)")
  #  print("----------------------------------------")
  #  print(diagnostics_df.to_string(index=False))


def build_theme_classification(theme_strength):
    total_themes = len(theme_strength)
    theme_class_map = {}
    theme_score_map = {}
    theme_rank_map = {}
    theme_raw_score_map = {}
    leading_count = 1 if total_themes > 0 else 0

    if total_themes > 1:
        leading_count = max(1, math.ceil(total_themes * 0.20))
    lagging_start = total_themes - leading_count + 1

    for i, row in theme_strength.iterrows():
        theme = row["Theme"]
        rank_position = i + 1
        theme_rank_map[theme] = rank_position
        theme_raw_score_map[theme] = round(row["ETF_RS_Raw"], 2)

        if total_themes == 1:
            theme_class = "Leading"
        elif rank_position <= leading_count:
            theme_class = "Leading"
        elif rank_position >= lagging_start:
            theme_class = "Lagging"
        else:
            theme_class = "Neutral"

        if total_themes == 1:
            theme_score = 100
        else:
            theme_score = round(
                20 + 80 * (total_themes - rank_position) / (total_themes - 1),
                2,
            )

        theme_class_map[theme] = theme_class
        theme_score_map[theme] = theme_score

    return theme_class_map, theme_score_map, theme_rank_map, theme_raw_score_map


def assign_stock_theme_classification(stocks, theme_class_map, theme_score_map, theme_raw_score_map):
    theme_classes = []
    theme_scores = []
    theme_states = []
    etf_raw_scores = []

    for _, row in stocks.iterrows():
        etf_theme = row["ETF_Theme"]
        mapped_theme = row["Mapped_Theme"]

        if mapped_theme in THEME_PARENT_MAP:
            etf_theme = THEME_PARENT_MAP[mapped_theme]

        if etf_theme in theme_class_map:
            theme_class = theme_class_map[etf_theme]
            theme_score = theme_score_map[etf_theme]
            theme_state = theme_class_map.get(etf_theme)
            etf_raw_score = theme_raw_score_map.get(etf_theme)
        else:
            if (
                row["RS_Rating"] >= 90
                and row["Sales_Score"] >= 80
                and row["Zacks_Score"] >= 85
            ):
                theme_class = "Unclassified Leader"
                theme_score = 80
                theme_state = None
                etf_raw_score = None
                print("UNCLASSIFIED LEADER:", row["Ticker"])
            else:
                theme_class = "Unknown"
                theme_score = 60
                theme_state = None
                etf_raw_score = None

        theme_classes.append(theme_class)
        theme_scores.append(theme_score)
        theme_states.append(theme_state)
        etf_raw_scores.append(etf_raw_score)

    stocks["Theme_Class"] = theme_classes
    stocks["Theme_Score"] = theme_scores
    stocks["Theme_State"] = theme_states
    stocks["ETF_Raw_Score"] = etf_raw_scores
    return stocks


def extract_benchmark_returns(raw_etf_df, theme_strength_settings):
    benchmark_ticker = theme_strength_settings["benchmark_ticker"]
    period_weights = theme_strength_settings["period_weights"]

    benchmark_rows = raw_etf_df[
        raw_etf_df["Ticker"].astype(str).str.upper() == benchmark_ticker
    ]

    if benchmark_rows.empty:
        raise ValueError(
            f"Benchmark ETF '{benchmark_ticker}' not found in ETF.csv."
        )

    benchmark_row = benchmark_rows.iloc[0]
    benchmark_returns = {}

    for period in period_weights:
        benchmark_returns[period] = pd.to_numeric(
            benchmark_row.get(period), errors="coerce"
        )

    return benchmark_returns


def load_inputs(theme_strength_settings):
    stocks = pd.read_csv(STOCK_FILE)
    stocks = stocks[
        stocks["Zacks Rank"].astype(str).str.startswith(("1", "2", "3", "4", "5"))
    ].copy()

    raw_etf_df = pd.read_csv(ETF_FILE)
    benchmark_returns = extract_benchmark_returns(raw_etf_df, theme_strength_settings)

    etf_df = raw_etf_df.copy()
    etf_df = filter_valid_etfs(etf_df)
    etf_df = filter_institutional_etfs(etf_df)
    total_etfs = len(etf_df)
    etf_df, excluded_insufficient_history = filter_etfs_with_sufficient_history(etf_df)

    print(
        f"ETF Eligibility: Total ETFs={total_etfs}, "
        f"Eligible ETFs={len(etf_df)}, "
        f"Excluded ETFs (Insufficient History)={excluded_insufficient_history}"
    )

    etf_df[["Sector", "Theme", "Subtheme"]] = etf_df["Investment Strategy"].apply(
    lambda x: pd.Series(parse_theme(x))
)

# ETF Theme normalization (mandatory)

    etf_df["Theme"] = etf_df["Theme"].replace({

        "natural gas": "Natural Gas",
        "Natural Gas": "Natural Gas",

        "broad": "Broad",
        "Broad": "Broad",

        "mlp": "MLP",
        "MLP": "MLP",

        "reits": "REITs",
        "REITs": "REITs"

    })

    return stocks, etf_df, benchmark_returns


def build_theme_strength(etf_master, benchmark_returns, theme_strength_settings):
    benchmark_ticker = theme_strength_settings["benchmark_ticker"]
    period_weights = theme_strength_settings["period_weights"]
    period_alias_map = theme_strength_settings["period_labels"]
    aggregation_mode = theme_strength_settings["aggregation_mode"]
    enable_normalization = theme_strength_settings["enable_normalization"]

    etf_master = etf_master.copy()

    # Prevent benchmark ETF membership from biasing any theme score.
    etf_master = etf_master[
        etf_master["Ticker"].astype(str).str.upper() != benchmark_ticker
    ].copy()

    def compute_relative_components(row):
        weighted_sum = 0.0
        total_weight = 0.0
        result = {}

        for period, weight in period_weights.items():
            etf_return = pd.to_numeric(row.get(period), errors="coerce")
            benchmark_return = benchmark_returns.get(period)
            period_alias = period_alias_map.get(period, period)

            if pd.isna(etf_return) or pd.isna(benchmark_return):
                result[f"Rel_{period_alias}"] = None
                result[f"WgtContr_{period_alias}"] = 0.0
                continue

            relative_return = etf_return - benchmark_return
            result[f"Rel_{period_alias}"] = relative_return
            weighted_sum += relative_return * weight
            total_weight += weight

        if total_weight == 0:
            for period in period_weights:
                period_alias = period_alias_map.get(period, period)
                result[f"WgtContr_{period_alias}"] = 0.0
            result["Relative_ETF_Score"] = 0.0
            return pd.Series(result)

        for period, weight in period_weights.items():
            period_alias = period_alias_map.get(period, period)
            relative_value = result.get(f"Rel_{period_alias}")
            if relative_value is None or pd.isna(relative_value):
                result[f"WgtContr_{period_alias}"] = 0.0
            else:
                result[f"WgtContr_{period_alias}"] = relative_value * (weight / total_weight)

        result["Relative_ETF_Score"] = weighted_sum / total_weight
        return pd.Series(result)

    relative_components = etf_master.apply(compute_relative_components, axis=1)
    etf_master = pd.concat([etf_master, relative_components], axis=1)

    diagnostics_columns = [
        "Relative_ETF_Score",
        "Rel_1D",
        "Rel_1W",
        "Rel_1M",
        "Rel_3M",
        "WgtContr_1D",
        "WgtContr_1W",
        "WgtContr_1M",
        "WgtContr_3M",
    ]

    def aggregate_theme_relative_score(group):
        aum = pd.to_numeric(group["Market Value (mil)"], errors="coerce")
        diagnostics_df = group[diagnostics_columns].apply(pd.to_numeric, errors="coerce").fillna(0)

        if aggregation_mode == "equal_weight":
            aggregate_values = diagnostics_df.mean()
        elif aggregation_mode == "aum_weighted":
            valid_aum = aum.where(aum > 0)
            total_aum = valid_aum.fillna(0).sum()

            if total_aum > 0:
                weights = valid_aum.fillna(0) / total_aum
                aggregate_values = diagnostics_df.mul(weights, axis=0).sum()
            else:
                aggregate_values = diagnostics_df.mean()
        else:
            raise ValueError(
                f"Unsupported THEME_STRENGTH_CONFIG aggregation mode: '{aggregation_mode}'."
            )

        return pd.Series({
            "Theme_Relative_Score": aggregate_values.get("Relative_ETF_Score", 0.0),
            "Rel_1D": aggregate_values.get("Rel_1D", 0.0),
            "Rel_1W": aggregate_values.get("Rel_1W", 0.0),
            "Rel_1M": aggregate_values.get("Rel_1M", 0.0),
            "Rel_3M": aggregate_values.get("Rel_3M", 0.0),
            "WgtContr_1D": aggregate_values.get("WgtContr_1D", 0.0),
            "WgtContr_1W": aggregate_values.get("WgtContr_1W", 0.0),
            "WgtContr_1M": aggregate_values.get("WgtContr_1M", 0.0),
            "WgtContr_3M": aggregate_values.get("WgtContr_3M", 0.0),
        })

    theme_strength = (
        etf_master.groupby("Theme").apply(aggregate_theme_relative_score).reset_index()
    )
    theme_strength = theme_strength[theme_strength["Theme"] != "Filtered"].copy()

    min_score = theme_strength["Theme_Relative_Score"].min()
    max_score = theme_strength["Theme_Relative_Score"].max()

    theme_strength["ETF_RS_Raw"] = theme_strength["Theme_Relative_Score"].round(4)

    if not enable_normalization:
        theme_strength["Theme_Strength_Normalized"] = pd.NA
    elif pd.isna(min_score) or pd.isna(max_score):
        theme_strength["Theme_Strength_Normalized"] = 0.0
    elif max_score == min_score:
        theme_strength["Theme_Strength_Normalized"] = 100.0
    else:
        theme_strength["Theme_Strength_Normalized"] = (
            (theme_strength["Theme_Relative_Score"] - min_score)
            / (max_score - min_score)
            * 100.0
        )

    theme_strength["Theme_Strength_Normalized"] = theme_strength[
        "Theme_Strength_Normalized"
    ].round(2)

    theme_strength = theme_strength[[
        "Theme",
        "ETF_RS_Raw",
        "Theme_Strength_Normalized",
        "Rel_1D",
        "Rel_1W",
        "Rel_1M",
        "Rel_3M",
        "WgtContr_1D",
        "WgtContr_1W",
        "WgtContr_1M",
        "WgtContr_3M",
    ]]
    theme_strength = theme_strength.sort_values("ETF_RS_Raw", ascending=False).reset_index(drop=True)
    theme_strength["Theme_Rank"] = range(1, len(theme_strength) + 1)
    return theme_strength


def map_stock_themes(stocks):
    mapped_themes = []
    etf_themes = []

    for _, row in stocks.iterrows():
        ticker = row["Ticker"]
        industry_key = str(row["Industry"]).strip().lower()

        if ticker in COMPANY_THEME:
            stock_theme = COMPANY_THEME[ticker]
        elif industry_key in INDUSTRY_THEME:
            stock_theme = INDUSTRY_THEME[industry_key]
        else:
            stock_theme = map_stock_theme(row["Industry"], row["Sector"])

        if stock_theme in THEME_TRANSLATION:
            etf_theme = THEME_TRANSLATION[stock_theme]
        else:
            etf_theme = stock_theme

        mapped_themes.append(stock_theme)
        etf_themes.append(etf_theme)

    stocks["Mapped_Theme"] = mapped_themes
    stocks["ETF_Theme"] = etf_themes
    stocks["ETF_Theme"] = stocks["ETF_Theme"].apply(normalize_theme)
    return stocks


def score_stocks(stocks):
    stocks = calculate_rs_raw(stocks)
    stocks = calculate_rs_rating(stocks)
    stocks = calculate_sales_score(stocks)
    stocks = calculate_zacks_score(stocks)
    stocks = calculate_margin_score(stocks)
    stocks = calculate_composite_score(stocks)
    stocks = calculate_long_score(stocks)
    stocks = calculate_short_score(stocks)
    return stocks


def build_candidates(stocks):
    long_watchlist = build_long_watchlist(stocks)
    distribution_watchlist = build_short_watchlist(stocks)
    theme_breadth = build_theme_breadth(stocks)
    institutional_leaders = build_institutional_leaders(stocks)

    long_watchlist = long_watchlist.sort_values("Long_Score", ascending=False)

    long_tickers = set(long_watchlist["Ticker"])
    long_candidates = pd.concat([long_watchlist, institutional_leaders])
    long_candidates = long_candidates.drop_duplicates(subset="Ticker")
    long_candidates["Ticker"] = long_candidates.apply(
        lambda row: row["Ticker"] if row["Ticker"] in long_tickers else row["Ticker"] + "*",
        axis=1,
    )
    long_candidates = long_candidates.sort_values("Long_Score", ascending=False)

    distribution_watchlist = distribution_watchlist[
        ~distribution_watchlist["Ticker"].isin(long_tickers)
    ]

    stocks["Long_Rank"] = None
    stocks["Short_Rank"] = None
    stocks["Is_Long_Candidate"] = False
    stocks["Is_Short_Candidate"] = False

    for rank, ticker in enumerate(long_candidates["Ticker"], start=1):
        clean_ticker = ticker.replace("*", "")
        stocks.loc[stocks["Ticker"] == clean_ticker, "Long_Rank"] = rank
        stocks.loc[stocks["Ticker"] == clean_ticker, "Is_Long_Candidate"] = True

    for rank, ticker in enumerate(distribution_watchlist["Ticker"], start=1):
        stocks.loc[stocks["Ticker"] == ticker, "Short_Rank"] = rank
        stocks.loc[stocks["Ticker"] == ticker, "Is_Short_Candidate"] = True

    return stocks, long_candidates, distribution_watchlist, theme_breadth


def save_history(stocks):
    try:
        save_stock_history(stocks)
    except Exception as e:
        print()
        print("STOCK HISTORY ERROR:", e)


def print_report(
    today,
    theme_strength,
    theme_class_map,
    long_candidates,
    distribution_watchlist,
    theme_breadth,
    theme_strength_settings,
):
    leading_themes = theme_strength[
        theme_strength["Theme"].isin([k for k, v in theme_class_map.items() if v == "Leading"])
    ][["Theme", "Theme_Rank", "ETF_RS_Raw"]].to_dict("records")

    neutral_themes = theme_strength[
        theme_strength["Theme"].isin([k for k, v in theme_class_map.items() if v == "Neutral"])
    ][["Theme", "Theme_Rank", "ETF_RS_Raw"]].to_dict("records")

    lagging_themes = theme_strength[
        theme_strength["Theme"].isin([k for k, v in theme_class_map.items() if v == "Lagging"])
    ][["Theme", "Theme_Rank", "ETF_RS_Raw"]].to_dict("records")

    print("\n")
    print("==============================================")
    print("TABELA DAILY MARKET SCAN")
    print("DATE:", today)
    print("==============================================")
    print("\n")

    print("\n==============================================")
    print("MARKET ROTATION SUMMARY")
    print("==============================================")

    print_theme_group("LEADING THEMES", leading_themes)
    print_theme_group("NEUTRAL THEMES", neutral_themes)
    print_theme_group("LAGGING THEMES", lagging_themes)
    if theme_strength_settings["debug_theme_strength"]:
        print_theme_strength_diagnostics(theme_strength)

    print("\n\n")
    print("THEME BREADTH ANALYSIS")
    print("----------------------------")
    print(
        theme_breadth[[
            "Mapped_Theme",
            "Total_Stocks",
            "Strong_Stocks",
            "Breadth_Percent",
            "Weighted_Breadth_Score",
        ]].head(20).to_string(index=False)
    )

    print("\n\n")
    print("LONG CANDIDATE UNIVERSE")
    print("----------------------------")
    
    display_df = long_candidates[
        [
            "Ticker",
            "Mapped_Theme",
            "Theme_Class",
            "RS_Rating",
            "Long_Score",
            "Zacks Rank",
        ]
    ].copy()

    display_df["Zacks Rank"] = (
        display_df["Zacks Rank"]
        .fillna(0)
        .astype(int)
        .astype(str)
    )

    display_df.loc[
        display_df["Zacks Rank"].isin(["4", "5"]),
        "Zacks Rank"
    ] += "*"

    print(display_df.to_string(index=False))

    print("\n\n")
    print("========================================")
    print("DISTRIBUTION WATCHLIST")
    print("========================================")

    if distribution_watchlist.empty:
        print("No qualified distribution candidates today.")
    else:
        display_df = distribution_watchlist[
            [
                "Ticker",
                "Mapped_Theme",
                "Theme_Class",
                "RS_Rating",
                "Composite_Score",
                "Distribution_Reasons",
            ]
        ].copy()

        display_df = display_df.rename(
            columns={
                "Mapped_Theme": "Theme",
                "Theme_Class": "Theme Class",
                "RS_Rating": "RS Rating",
                "Composite_Score": "Composite Score",
                "Distribution_Reasons": "Reasons",
            }
        )

        print(display_df.to_string(index=False))

    print("\n")
    print("----------------------------")
    print("TRADINGVIEW WATCHLIST EXPORT")
    print("----------------------------")
    long_list = ",".join(long_candidates["Ticker"].head(50).astype(str).tolist())
    short_list = ",".join(distribution_watchlist["Ticker"].head(50).astype(str).tolist())
    print("###LONG," + long_list + ",")
    print("###SHORT," + short_list)

    compare_watchlists(
        long_candidates["Ticker"].head(50).tolist(),
        distribution_watchlist["Ticker"].head(50).tolist(),
    )


def save_intelligence_outputs(leading_themes, neutral_themes, lagging_themes, stocks, theme_breadth):
    total_stock_count = len(stocks)
    classified_stock_count = len(stocks[stocks["Theme_Class"] != "Unknown"])
    unclassified_stock_count = len(stocks[stocks["Theme_Class"] == "Unknown"])

    try:
        save_daily_snapshot(
            leading_themes,
            neutral_themes,
            lagging_themes,
            total_stock_count,
            classified_stock_count,
            unclassified_stock_count,
            theme_breadth,
        )

        rotation_data = calculate_rotation_delta()
        save_rotation_delta(rotation_data)
        print_rotation_report(rotation_data)

        try:
            build_historical_intelligence_report(min_days=3, max_days=21)
        except Exception as e:
            print()
            print("HISTORICAL INTELLIGENCE ERROR:", e)
    except Exception as e:
        print()
        print("INTELLIGENCE LAYER ERROR:", e)

    try:
        save_unknown_classification(stocks)
    except Exception as e:
        print()
        print("UNKNOWN CLASSIFICATION ERROR:", e)


def run_tabela_pipeline():
    print("\n")

    theme_strength_settings = get_theme_strength_settings()

    stocks, etf_df, benchmark_returns = load_inputs(theme_strength_settings)
    etf_df = calculate_etf_rs(etf_df)
    etf_df = assign_theme_score(etf_df)
    etf_master = etf_df.copy()

    theme_strength = build_theme_strength(
        etf_master,
        benchmark_returns,
        theme_strength_settings,
    )
    theme_class_map, theme_score_map, theme_rank_map, theme_raw_score_map = build_theme_classification(theme_strength)

    stocks = map_stock_themes(stocks)
    stocks["Theme_Rank"] = stocks["ETF_Theme"].map(theme_rank_map)

    stocks = calculate_rs_raw(stocks)
    stocks = calculate_rs_rating(stocks)
    stocks = calculate_sales_score(stocks)
    stocks = calculate_zacks_score(stocks)
    stocks = assign_stock_theme_classification(
        stocks,
        theme_class_map,
        theme_score_map,
        theme_raw_score_map,
    )

    stocks = score_stocks(stocks)
    stocks, long_candidates, distribution_watchlist, theme_breadth = build_candidates(stocks)

    today = datetime.date.today()
    save_history(stocks)

    print_report(
        today,
        theme_strength,
        theme_class_map,
        long_candidates,
        distribution_watchlist,
        theme_breadth,
        theme_strength_settings,
    )

    leading_themes = theme_strength[
        theme_strength["Theme"].isin([k for k, v in theme_class_map.items() if v == "Leading"])
    ][["Theme", "Theme_Rank", "ETF_RS_Raw"]].to_dict("records")

    neutral_themes = theme_strength[
        theme_strength["Theme"].isin([k for k, v in theme_class_map.items() if v == "Neutral"])
    ][["Theme", "Theme_Rank", "ETF_RS_Raw"]].to_dict("records")

    lagging_themes = theme_strength[
        theme_strength["Theme"].isin([k for k, v in theme_class_map.items() if v == "Lagging"])
    ][["Theme", "Theme_Rank", "ETF_RS_Raw"]].to_dict("records")

    save_intelligence_outputs(
        leading_themes,
        neutral_themes,
        lagging_themes,
        stocks,
        theme_breadth,
    )

    print("\n")
    print("==============================================")
    print("END OF TABELA SCAN")
    print("==============================================")


if __name__ == "__main__":
    run_tabela_pipeline()

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
from engines.watchlist_delta_engine import (
    compare_watchlists,
    load_previous_long_watchlist,
)

from engines.historical_intelligence_engine import build_theme_performance_table
from engines.institutional_leaders_engine import build_institutional_leaders
from engines.long_scoring_engine import calculate_long_score
from engines.presentation_engine import (
    print_daily_scan,
    print_etf_eligibility,
    print_intelligence_layer_error,
    print_market_context_summary,
    print_scan_epilogue,
    print_scan_preamble,
    print_stock_history_error,
    print_unknown_classification_error,
)

from engines.stock_transition_engine import apply_tracking_state
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
from engines.distribution_engine import build_distribution_watchlist

from engines.snapshot_engine import save_daily_snapshot
from engines.stock_history_engine import save_stock_history
from engines.unknown_classification_persistence import save_unknown_classification
from engines.watchlist_engine import build_long_watchlist
from core.runtime_context import context
from engines.stock_transition_engine import (
    apply_tracking_state,
    get_distribution_watchlist,
    get_distribution_candidates,
    load_registry,
    post_distribution_update,
    pre_distribution_update,
)

DATA_DIR = "market_data"
ETF_FILE = context.etf_file
STOCK_FILE = context.stocks_file


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
    is_unclassified_leaders = []
    theme_scores = []
    theme_states = []
    etf_raw_scores = []

    for _, row in stocks.iterrows():
        etf_theme = row["ETF_Theme"]
        mapped_theme = row["Mapped_Theme"]

        #
        # Preserve explicit company mappings.
        # Only promote child themes when the ETF theme still matches
        # the mapped theme.
        #
        if (
            mapped_theme in THEME_PARENT_MAP
            and etf_theme == mapped_theme
        ):
            etf_theme = THEME_PARENT_MAP[mapped_theme]

    

        if etf_theme in theme_class_map:
            theme_class = theme_class_map[etf_theme]
            theme_score = theme_score_map[etf_theme]
            theme_state = theme_class_map.get(etf_theme)
            etf_raw_score = theme_raw_score_map.get(etf_theme)
            is_unclassified = False
        else:
            if (
                row["RS_Rating"] >= 90
                and row["Sales_Score"] >= 80
                and row["Zacks_Score"] >= 85
            ):
                theme_class = "Unclassified Leader"
                theme_score = 80
                is_unclassified = True
                theme_state = None
                etf_raw_score = None
                
            else:
                theme_class = "Unknown"
                theme_score = 60
                theme_state = None
                etf_raw_score = None
                is_unclassified = False

        theme_classes.append(theme_class)
        theme_scores.append(theme_score)
        theme_states.append(theme_state)
        etf_raw_scores.append(etf_raw_score)
        is_unclassified_leaders.append(is_unclassified)


    stocks["Theme_Class"] = theme_classes
    stocks["Theme_Score"] = theme_scores
    stocks["Theme_State"] = theme_states
    stocks["ETF_Raw_Score"] = etf_raw_scores
    stocks["Is_Unclassified_Leader"] = is_unclassified_leaders
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

        ticker = str(row["Ticker"]).strip().upper()
        
        industry_key = str(row["Industry"]).strip().lower()

        #
        # Priority
        # 1. Explicit stock mapping
        # 2. Industry mapping
        # 3. Automatic mapper
        #
        if ticker in COMPANY_THEME:
            stock_theme = COMPANY_THEME[ticker]

        elif industry_key in INDUSTRY_THEME:
            stock_theme = INDUSTRY_THEME[industry_key]

        else:
            stock_theme = map_stock_theme(
                row["Industry"],
                row["Sector"],
            )

        etf_theme = THEME_TRANSLATION.get(
            stock_theme,
            stock_theme,
        )

        mapped_themes.append(stock_theme)
        etf_themes.append(normalize_theme(etf_theme))

    stocks = stocks.copy()
    stocks["Mapped_Theme"] = mapped_themes
    stocks["ETF_Theme"] = etf_themes

    return stocks

def score_stocks(stocks):
    stocks = calculate_rs_raw(stocks)
    stocks = calculate_rs_rating(stocks)
    stocks = calculate_sales_score(stocks)
    stocks = calculate_zacks_score(stocks)
    stocks = calculate_margin_score(stocks)
    stocks = calculate_composite_score(stocks)
    stocks = calculate_long_score(stocks)
    return stocks



def build_candidates(stocks):

    registry = load_registry()

    long_watchlist = build_long_watchlist(stocks)
    institutional_leaders = build_institutional_leaders(stocks)

    long_watchlist = long_watchlist.sort_values(
        "Long_Score",
        ascending=False,
    )

    long_tickers = set(long_watchlist["Ticker"])

    long_candidates = (
        pd.concat([long_watchlist, institutional_leaders])
        .drop_duplicates(subset="Ticker")
        .sort_values("Long_Score", ascending=False)
        .reset_index(drop=True)
    )

    long_candidates["Ticker"] = long_candidates.apply(
        lambda row: (
            row["Ticker"]
            if row["Ticker"] in long_tickers
            else row["Ticker"] + "*"
        ),
        axis=1,
    )

    registry, recovered = pre_distribution_update(
        registry=registry,
        current_long_candidates=long_candidates,
        stocks=stocks,
    )

    grace_tickers = [t for t, s in registry.items() if s["tracking_state"] == "LONG"]
    if grace_tickers:
        grace_df = stocks[
            stocks["Ticker"].astype(str).str.upper().isin(grace_tickers)
        ].copy()
        if not grace_df.empty:
            temp = pd.concat([long_candidates, grace_df])
            temp["_clean_ticker"] = temp["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper()
            long_candidates = temp.drop_duplicates(subset=["_clean_ticker"]).drop(columns=["_clean_ticker"])
            long_candidates = long_candidates.sort_values("Long_Score", ascending=False).reset_index(drop=True)

    distribution_candidates = get_distribution_candidates(
        registry=registry,
        stocks=stocks,
    )

    qualified_distribution = build_distribution_watchlist(
        distribution_candidates
    )

    registry = post_distribution_update(
        registry=registry,
        qualified_distribution=qualified_distribution,
    )

    distribution_watchlist = get_distribution_watchlist(
        registry=registry,
        stocks=stocks,
    )

    current_long_tickers = {
        ticker.replace("*", "")
        for ticker in long_candidates["Ticker"]
    }

    distribution_watchlist = distribution_watchlist[
        ~distribution_watchlist["Ticker"].isin(current_long_tickers)
    ].copy()

    stocks["Long_Rank"] = None
    stocks["Short_Rank"] = None
    stocks["Is_Long_Candidate"] = False
    stocks["Is_Short_Candidate"] = False
    stocks["Is_Pre_Observation_Candidate"] = False

    def is_pre_obs(row):
        t_class = row.get("Theme_Class", "")
        rs = row.get("RS_Rating", 0)
        ls = row.get("Long_Score", 0)
        cs = row.get("Composite_Score", 0)
        
        if t_class in ["Leading", "Unclassified Leader"] and rs >= 90 and ls >= 85:
            return False
        if t_class == "Leading" and (cs >= 90 or rs >= 95):
            return False
        return True

    for rank, (idx, candidate_row) in enumerate(long_candidates.iterrows(), start=1):
        clean_ticker = candidate_row["Ticker"].replace("*", "")

        stocks.loc[stocks["Ticker"] == clean_ticker, "Long_Rank"] = rank
        stocks.loc[stocks["Ticker"] == clean_ticker, "Is_Long_Candidate"] = True
        stocks.loc[stocks["Ticker"] == clean_ticker, "Is_Pre_Observation_Candidate"] = is_pre_obs(candidate_row)

    for rank, ticker in enumerate(
        distribution_watchlist["Ticker"],
        start=1,
    ):

        stocks.loc[
            stocks["Ticker"] == ticker,
            "Short_Rank",
        ] = rank

        stocks.loc[
            stocks["Ticker"] == ticker,
            "Is_Short_Candidate",
        ] = True


    theme_breadth = build_theme_breadth(stocks, long_candidates)

    stocks = apply_tracking_state(
        registry=registry,
        stocks=stocks,
    )

    # ==========================
    # VALIDATE CROSS-SECTION INVARIANTS
    # ==========================
    long_table_tickers = set(long_candidates["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper())
    
    breadth_leaders = set()
    for leaders_str in theme_breadth["Leaders"]:
        if pd.notna(leaders_str) and leaders_str != "":
            for t in leaders_str.split(","):
                breadth_leaders.add(t.strip().upper())
                
    if not breadth_leaders.issubset(long_table_tickers):
        diff = breadth_leaders - long_table_tickers
        raise ValueError(f"Build validation failed: Tickers {diff} found in THEME BREADTH leaders but missing from LONG CANDIDATE UNIVERSE shared state.")

    return (
        stocks,
        long_candidates,
        distribution_watchlist,
        theme_breadth,
        recovered,
    )

def save_history(stocks):
    try:
        save_stock_history(stocks)
    except Exception as e:
        print_stock_history_error(e)


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
        

        # Historical intelligence is now consumed by
        # Theme Performance. No standalone report.
        pass


    except Exception as e:
        print_intelligence_layer_error(e)

    try:
        save_unknown_classification(stocks)
    except Exception as e:
        print_unknown_classification_error(e)


def run_tabela_pipeline():
    from engines.market_context_engine import run_market_context_engine

    market_context = run_market_context_engine(
        context.market_date
    )
    print_scan_preamble()
    if market_context:
        print_market_context_summary(market_context)


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

    stocks, long_candidates, distribution_watchlist, theme_breadth, recovered = build_candidates(stocks)

    today = context.market_date
    save_history(stocks)

    theme_performance = build_theme_performance_table(
        theme_strength
    )

    print_daily_scan(
        today,
        theme_strength,
        theme_class_map,
        long_candidates,
        distribution_watchlist,
        theme_breadth,
        theme_strength_settings,
        stocks,
        theme_performance,
        recovered,
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

    print_scan_epilogue()


if __name__ == "__main__":
    run_tabela_pipeline()

import pandas as pd
import sys
import io
import re
import engines.rotation_engine
from engines.stock_transition_engine import (
    load_registry,
    get_transition_summary,
    OBSERVATION_MIN_RUNS,
)
import textwrap

engines.rotation_engine.print_rotation_report = lambda *args, **kwargs: None

from engines.watchlist_delta_engine import compare_watchlists


class OutputCapturer:
    def __init__(self):
        self.original_stdout = sys.stdout
        self.buffer = io.StringIO()

    def write(self, data):
        self.buffer.write(data)

    def flush(self):
        pass

_capturer = None


def print_scan_preamble():
    global _capturer
    _capturer = OutputCapturer()
    sys.stdout = _capturer
    print("\n")


def find_section_start(text, title_pos):
    lines = text[:title_pos].splitlines(keepends=True)
    if not lines:
        return 0
    start_line_idx = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        line_strip = lines[i].strip()
        if all(c in "=- " for c in line_strip):
            start_line_idx = i
        else:
            break
    return sum(len(line) for line in lines[:start_line_idx])


def clean_saved_messages(text):
    lines = text.splitlines(keepends=True)
    cleaned_lines = []
    for line in lines:
        clean = line.strip()
        if any(msg in clean for msg in (
            "STOCK HISTORY SAVED",
            "MARKET SNAPSHOT SAVED",
            "ROTATION DELTA SAVED",
            "UNKNOWN CLASSIFICATION SAVED"
        )):
            continue
        cleaned_lines.append(line)
    return "".join(cleaned_lines)


def collapse_newlines(text):
    return re.sub(r'\n{3,}', '\n\n', text)


def print_scan_epilogue():
    global _capturer
    if _capturer is not None:
        sys.stdout = _capturer.original_stdout
        captured_text = _capturer.buffer.getvalue()
        _capturer = None
    else:
        captured_text = ""

    titles = [
        ("MARKET_CONTEXT", "MARKET CONTEXT"),
        ("HEADER", "TABELA DAILY MARKET SCAN"),
        ("THEME_PERFORMANCE", "THEME PERFORMANCE"),
        ("THEME_BREADTH", "THEME BREADTH ANALYSIS"),
        ("LONG_UNIVERSE", "LONG CANDIDATE UNIVERSE"),
        ("UNCLASSIFIED_LEADERS", "UNCLASSIFIED LEADERS"),
        ("DISTRIBUTION_WATCHLIST", "DISTRIBUTION WATCHLIST"),
        ("TRADINGVIEW_EXPORT", "TRADINGVIEW WATCHLIST EXPORT"),
        ("WATCHLIST_DELTA", "WATCHLIST DELTA REPORT"),
        ("END_BANNER", "END OF TABELA SCAN")
    ]
    
    sections_found = []
    for key, title in titles:
        pos = captured_text.find(title)
        if pos != -1:
            start_idx = find_section_start(captured_text, pos)
            sections_found.append((key, start_idx))
            
    sections_found.sort(key=lambda x: x[1])
    
    section_texts = {}
    for i in range(len(sections_found)):
        key, start = sections_found[i]
        if i + 1 < len(sections_found):
            end = sections_found[i+1][1]
        else:
            end = len(captured_text)
        section_texts[key] = captured_text[start:end]
        
    pre_header = ""
    if sections_found:
        first_start = sections_found[0][1]
        pre_header = captured_text[:first_start]

    pre_header = clean_saved_messages(pre_header)
    for key in list(section_texts.keys()):
        section_texts[key] = clean_saved_messages(section_texts[key])

    order = [
        "THEME_PERFORMANCE",
        "THEME_BREADTH",
        "LONG_UNIVERSE",
        "UNCLASSIFIED_LEADERS",
        "DISTRIBUTION_WATCHLIST",
        "TRADINGVIEW_EXPORT",
        "WATCHLIST_DELTA"
    ]

    final_output = []

    if "MARKET_CONTEXT" in section_texts:
        final_output.append(section_texts["MARKET_CONTEXT"])

    if pre_header.strip():
        final_output.append(pre_header)

    if "HEADER" in section_texts:
        final_output.append(section_texts["HEADER"])

    for key in order:
        if key in section_texts:
            final_output.append(section_texts[key])

    files_generated = (
        "\n"
        "FILES GENERATED\n"
        "---------------\n"
        "✓ Market Context\n"
        "✓ Stock History\n"
        "✓ Market Snapshot\n"
        "✓ Rotation Delta\n"
        "✓ Unknown Classification\n"
        "✓ Stock Transition Registry\n"
        "\n"
    )
    final_output.append(files_generated)

    if "END_BANNER" in section_texts:
        final_output.append(section_texts["END_BANNER"])
    else:
        final_output.append(
            "\n"
            "==============================================\n"
            "END OF TABELA SCAN\n"
            "==============================================\n"
        )

    print_string = "".join(final_output)
    print_string = collapse_newlines(print_string)
    
    sys.stdout.write(print_string)
    sys.stdout.flush()


def print_etf_eligibility(total_etfs, eligible_etfs, excluded_insufficient_history):
    print(
        f"ETF Eligibility: Total ETFs={total_etfs}, "
        f"Eligible ETFs={eligible_etfs}, "
        f"Excluded ETFs (Insufficient History)={excluded_insufficient_history}"
    )


def print_stock_history_error(error):
    print()
    print("STOCK HISTORY ERROR:", error)


def print_intelligence_layer_error(error):
    print()
    print("INTELLIGENCE LAYER ERROR:", error)


def print_historical_intelligence_error(error):
    print()
    print("HISTORICAL INTELLIGENCE ERROR:", error)


def print_unknown_classification_error(error):
    print()
    print("UNKNOWN CLASSIFICATION ERROR:", error)


def print_theme_performance(theme_performance):
    print()
    print("==============================================")
    print("THEME PERFORMANCE")
    print("Legend: [] = Top 3   () = Bottom 3")
    print("==============================================")
    print()

    df = theme_performance.copy()

    expected_columns = [
        "Rank",
        "Theme",
        "Strength",
        "D",
        "W",
        "M",
        "Q",
        "Rank Δ",
        "Score Δ",
        "Transition",
    ]

    for col in expected_columns:
        if col not in df.columns:
            df[col] = None

    def fmt_delta(value, top3=False, bottom3=False):
        if pd.isna(value):
            return "—"

        text = f"{value:.2f}"

        if top3:
            return f"[{text}]"

        if bottom3:
            return f"({text})"

        return text

    def fmt_text(value, signed=True):
        if pd.isna(value) or value == "":
            return "—"

        if isinstance(value, (int, float)):

            if float(value).is_integer():

                if int(value) == 0:
                    return "0"

                return f"{int(value):+d}" if signed else f"{int(value)}"

            return f"{value:+.2f}" if signed else f"{value:.2f}"

        return str(value)

    print(
        f"{'Rank':>4}  "
        f"{'Theme':<35}"
        f"{'Strength':>9}"
        f"{'D':>9}"
        f"{'W':>9}"
        f"{'M':>9}"
        f"{'Q':>9}"
        f"{'Rank Δ':>9}"
        f"{'Score Δ':>10}"
        f"  Transition"
    )

    print("-" * 120)

    top3_strength = set(df.nlargest(3, "Strength")["Theme"])
    bottom3_strength = set(df.nsmallest(3, "Strength")["Theme"])

    top3_d = set(df.nlargest(3, "D")["Theme"])
    bottom3_d = set(df.nsmallest(3, "D")["Theme"])

    top3_w = set(df.nlargest(3, "W")["Theme"])
    bottom3_w = set(df.nsmallest(3, "W")["Theme"])

    for _, row in df.sort_values("Rank").iterrows():

        print(
            f"{int(row['Rank']):>4}  "
            f"{row['Theme']:<35}"
            f"{fmt_delta(row['Strength'], row['Theme'] in top3_strength, row['Theme'] in bottom3_strength):>9}"
            f"{fmt_delta(row['D'], row['Theme'] in top3_d, row['Theme'] in bottom3_d):>9}"
            f"{fmt_delta(row['W'], row['Theme'] in top3_w, row['Theme'] in bottom3_w):>9}"
            f"{fmt_delta(row['M']):>9}"
            f"{fmt_delta(row['Q']):>9}"
            f"{fmt_text(row['Rank Δ']):>9}"
            f"{fmt_text(row['Score Δ'], signed=False):>10}"
            f"  {fmt_text(row['Transition'])}"
        )

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

def print_market_context_summary(market_context):
    """
    Display Market Context summary.
    """

    TYPE_SYMBOL = {
        "Accumulation": "↑",
        "Distribution": "↓",
        "Consolidation": "◼",
        "Neutral": "-",
    }

    def fmt(value):
        if value is None:
            return "-"
        return f"{value:+.2f}"

    def fmt_rv(value):
        if value is None:
            return "-"
        return f"{value:.2f}"

    print()
    print("==============================================")
    print("MARKET CONTEXT")
    print("==============================================")
    print()

    analytics = market_context["market_analytics"]

    relative_volume = analytics["relative_volume"]
    lookback_performance = analytics["lookback_performance"]
    relative_performance = analytics["relative_performance"]
    market_structure = analytics["market_structure"]
    institutional_activity = analytics["institutional_activity"]

    print("MARKET STATISTICS")

    header = (
        f"{'ETF':<4}"
        f"{'Type':>4}"
        f"{'5D%':>8}"
        f"{'20D%':>8}"
        f"{'50D%':>8}"
        f"{'200D%':>8}"
        f"{'RV.20':>8}"
        f"{'RV.50':>8}"
        f"{'20Dist':>10}"
        f"{'50Dist':>10}"
        f"{'200Dist':>10}"
    )

    print("-" * len(header))
    print(header)
    print("-" * len(header))

    for etf in market_context["market"].keys():

        rv20 = relative_volume["20d"].get(etf)
        rv50 = relative_volume["50d"].get(etf)

        perf5 = lookback_performance["5d"].get(etf)
        perf20 = lookback_performance["20d"].get(etf)
        perf50 = lookback_performance["50d"].get(etf)
        perf200 = lookback_performance["200d"].get(etf)

        structure = market_structure.get(etf, {})

        dist20 = structure.get("distance_to_20sma_pct")
        dist50 = structure.get("distance_to_50sma_pct")
        dist200 = structure.get("distance_to_200sma_pct")

        day_type = institutional_activity.get(etf, {}).get(
            "day_type",
            "Neutral",
        )

        symbol = TYPE_SYMBOL.get(day_type, "-")

        print(
            f"{etf:<4}"
            f"{symbol:>4}"
            f"{fmt(perf5):>8}"
            f"{fmt(perf20):>8}"
            f"{fmt(perf50):>8}"
            f"{fmt(perf200):>8}"
            f"{fmt_rv(rv20):>8}"
            f"{fmt_rv(rv50):>8}"
            f"{fmt(dist20):>10}"
            f"{fmt(dist50):>10}"
            f"{fmt(dist200):>10}"
        )

    print()

    print("RELATIVE PERFORMANCE")
    print("-" * 90)

    first_period = next(iter(relative_performance))
    pairs = list(relative_performance[first_period].keys())

    headers = ["Pair"] + [
        period.upper()
        for period in relative_performance.keys()
    ]

    header_line = (
        f"{headers[0]:<16}"
        + "".join(f"{h:>9}" for h in headers[1:])
    )

    print(header_line)
    print("-" * len(header_line))

    for pair in pairs:

        display_pair = pair.replace("_vs_", " vs ")

        line = f"{display_pair:<16}"

        for period in relative_performance.keys():

            value = relative_performance[period].get(pair)

            if value is None:
                line += f"{'-':>9}"
            else:
                line += f"{value:>9.2f}"

        print(line)

    print()

def print_daily_scan(
    today,
    theme_strength,
    theme_class_map,
    long_candidates,
    distribution_watchlist,
    theme_breadth,
    theme_strength_settings,
    stocks,
    theme_performance,
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
    print("MARKET DATE:", today)
    print("==============================================")
    print("\n")

    print_theme_performance(theme_performance)

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
        ]].rename(
            columns={
                "Mapped_Theme": "Theme",
                "Total_Stocks": "Total",
                "Strong_Stocks": "Qualified Stocks",
                "Breadth_Percent": "Breadth %",
                "Weighted_Breadth_Score": "Breadth Score",
            }
        ).head(20).to_string(index=False)
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

    display_df = display_df.rename(
        columns={
            "Theme_Class": "Theme Classification",
        }
    )

    print(display_df.to_string(index=False))

    unclassified = long_candidates[
        long_candidates["Theme_Class"] == "Unclassified Leader"
    ].copy()

    if not unclassified.empty:
        print("\n")
        print("UNCLASSIFIED LEADERS")
        print("----------------------------")
        unclassified["Ticker_Display"] = unclassified.apply(
            lambda row: f"★★★★★ {row['Ticker']}" if row.get("Long_Score", 0) >= 90 else row["Ticker"],
            axis=1
        )
        col_width = max(unclassified["Ticker_Display"].astype(str).map(len).max(), len("Ticker")) + 3
        print(f"{'Ticker':<{col_width}}{'Industry'}")
        for _, row in unclassified.iterrows():
            ticker_disp = row["Ticker_Display"]
            industry = row["Industry"]
            print(f"{ticker_disp:<{col_width}}{industry}")


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
                "RS_Delta_Val",
                "RS_Trend_Val",
                "Leadership_Loss_Val",
                "History_Val",
                "Composite_Delta_Val",
                "Composite_Trend_Val",
            ]
        ].copy()

        display_df = display_df.rename(
            columns={
                "Mapped_Theme": "Theme",
                "Theme_Class": "Theme Class",
                "RS_Delta_Val": "RS \u0394",
                "RS_Trend_Val": "RS Trend",
                "Leadership_Loss_Val": "Leadership",
                "History_Val": "History",
                "Composite_Delta_Val": "Composite \u0394",
                "Composite_Trend_Val": "Composite Trend",
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
        stocks,
    )
    registry = load_registry()
    transition = get_transition_summary(registry)

    print()
    print("========================================")
    print("STOCK TRANSITIONS")
    print("========================================")

    #
    # OBSERVATION
    #
    print()
    print("OBSERVATION")
    print("----------------------------")
    print(f"Total : {len(transition['observation'])}")

    if transition["observation"]:

        observation_groups = {}

        for item in transition["observation"]:
            observation_groups.setdefault(item["runs"], []).append(
                item["ticker"]
            )

        print()

        for runs in sorted(observation_groups.keys()):

            tickers = sorted(observation_groups[runs])

            print(
                f"Progress {runs} / {OBSERVATION_MIN_RUNS} "
                f"({len(tickers)})"
            )

            print("-" * 30)

            wrapped = textwrap.fill(
                ", ".join(tickers),
                width=90,
                break_long_words=False,
                break_on_hyphens=False,
            )

            print(wrapped)
            print()

    #
    # DISTRIBUTION
    #
    print("DISTRIBUTION")
    print("----------------------------")
    print(f"Total : {len(transition['distribution'])}")

    if transition["distribution"]:

        distribution_groups = {}

        for item in transition["distribution"]:
            distribution_groups.setdefault(item["runs"], []).append(
                item["ticker"]
            )

        print()

        max_runs = max(
            item["runs"]
            for item in transition["distribution"]
        )

        for runs in sorted(distribution_groups.keys()):

            tickers = sorted(distribution_groups[runs])

            print(
            f"Progress {runs} / {max_runs} "
            f"({len(tickers)})"
        )

        print("-" * 30)

        wrapped = textwrap.fill(
            ", ".join(tickers),
            width=90,
            break_long_words=False,
            break_on_hyphens=False,
        )

        print(wrapped)
        print()
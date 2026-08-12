import pandas as pd
import sys
import io
import re
import engines.rotation_engine
from engines.stock_transition_engine import (
    get_transition_summary,
    OBSERVATION_MIN_RUNS,
)
import textwrap

engines.rotation_engine.print_rotation_report = lambda *args, **kwargs: None

from engines.watchlist_delta_engine import compare_watchlists
from core.theme_translation_engine import THEME_TRANSLATION


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
        ("MARKET_CONTEXT", "MARKET STATISTICS"),
        ("HEADER", "TABELA DAILY MARKET SCAN"),
        ("THEME_PERFORMANCE", "THEME PERFORMANCE"),
        ("THEME_BREADTH", "THEME BREADTH ANALYSIS"),
        ("LONG_UNIVERSE", "LONG CANDIDATE UNIVERSE"),
        ("OBSERVATION_WATCHLIST", "OBSERVATION WATCHLIST"),
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
        "HEADER",
        "MARKET_CONTEXT",
        "THEME_PERFORMANCE",
        "THEME_BREADTH",
        "LONG_UNIVERSE",
        "OBSERVATION_WATCHLIST",
        "DISTRIBUTION_WATCHLIST",
        "TRADINGVIEW_EXPORT",
        "WATCHLIST_DELTA"
    ]

    final_output = []

    if pre_header.strip():
        final_output.append(pre_header)

    if "HEADER" in section_texts:
        final_output.append(section_texts["HEADER"])

    for key in order:
        if key == "HEADER":
            continue

        if key in section_texts:
            final_output.append(section_texts[key])


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
            
    for col in ["Rank", "Strength", "D", "W", "M", "Q"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

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

    top3_rank = set(df.nsmallest(3, "Rank")["Theme"])
    bottom3_rank = set(df.nlargest(3, "Rank")["Theme"])

    for _, row in df.sort_values("Rank").iterrows():
        is_transition = pd.notna(row['Transition']) and str(row['Transition']).strip() != "" and str(row['Transition']).strip() != "—"
        if row['Theme'] not in top3_rank and row['Theme'] not in bottom3_rank and not is_transition:
            continue

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
        "Accumulation": "Accumulation",
        "Distribution": "Distribution",
        "Consolidation": "Consolidation",
        "Neutral": "N/A",
        None: "N/A",
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

    snapshot = market_context["latest_market_snapshot"]
    stats = snapshot["market_statistics"]
    relative_performance = snapshot["relative_performance"]

    has_valid_etfs = False
    for etf in ["SPY", "QQQ", "IWM", "DIA"]:
        data = stats[etf]
        day_type = data.get('day_type')
        if day_type in ["Accumulation", "Distribution", "Consolidation"]:
            has_valid_etfs = True
            break
            
    if has_valid_etfs:
        print("MARKET STATISTICS")
    
        header = (
            f"{'ETF':<6}"
            f"{'State':>14}"
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
    
        for etf in ["SPY", "QQQ", "IWM", "DIA"]:
    
            data = stats[etf]
            day_type = data.get('day_type')
            
            if day_type not in ["Accumulation", "Distribution", "Consolidation"]:
                continue
    
            returns = data["returns"]
            rv = data["relative_volume"]
            ma = data["moving_average_extension"]
    
            print(
                f"{etf:<6}"
                f"{TYPE_SYMBOL.get(data.get('day_type'),'N/A'):>14}"
                f"{fmt(returns.get('1w')):>8}"
                f"{fmt(returns.get('4w')):>8}"
                f"{fmt(returns.get('10w')):>8}"
                f"{fmt(returns.get('40w')):>8}"
                f"{fmt_rv(rv.get('20d')):>8}"
                f"{fmt_rv(rv.get('50d')):>8}"
                f"{fmt(ma.get('20dma')):>10}"
                f"{fmt(ma.get('50dma')):>10}"
                f"{fmt(ma.get('200dma')):>10}"
            )
    
        print()


def load_todays_registry():
    import os
    import json
    from core.runtime_context import context
    from core.config import STOCK_TRANSITION_CONFIG
    REGISTRY_DIR = STOCK_TRANSITION_CONFIG["REGISTRY_DIR"]
    today = str(context.market_date)
    path = os.path.join(REGISTRY_DIR, f"{today}_registry.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

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
    recovered,
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

    # print_theme_performance(theme_performance)

    if theme_strength_settings["debug_theme_strength"]:
        print_theme_strength_diagnostics(theme_strength)

    print()
    print("========================================")
    print("THEME BREADTH ANALYSIS")
    print("Legend: # = Distribution Watchlist Candidate")
    print("========================================")
    
    display_df = (
        theme_breadth[
            [
                "Mapped_Theme",
                "Total_Stocks",
                "Strong_Stocks",
                "Breadth_Percent",
                "Weighted_Breadth_Score",
                "Leaders",
            ]
        ]
    )

    def has_valid_leaders(leaders_val):
        return pd.notna(leaders_val) and str(leaders_val).strip() != "" and str(leaders_val).strip() != "None"
        
    display_df = display_df[display_df["Leaders"].apply(has_valid_leaders)]

    print(f"{'Theme':<42}  {'Total':>5}  {'Qual':>4}  {'Score':>8}  {'Macro State':>17}")
    print("-" * 83)
    
    for _, row in display_df.iterrows():
        mapped_theme = str(row['Mapped_Theme'])
        parent_theme = THEME_TRANSLATION.get(mapped_theme, mapped_theme)
        
        if parent_theme != mapped_theme:
            theme_display = f"{mapped_theme} ({parent_theme})"
        else:
            theme_display = mapped_theme
            
        theme_display = theme_display[:42]
        
        total = int(row['Total_Stocks']) if pd.notna(row['Total_Stocks']) else 0
        qual = int(row['Strong_Stocks']) if pd.notna(row['Strong_Stocks']) else 0
        score = float(row['Weighted_Breadth_Score']) if pd.notna(row['Weighted_Breadth_Score']) else 0.0
        
        macro_state = theme_class_map.get(parent_theme, "Unknown")
        macro_rank = "?"
        if not theme_strength[theme_strength["Theme"] == parent_theme].empty:
            macro_rank = theme_strength[theme_strength["Theme"] == parent_theme].iloc[0]["Theme_Rank"]
            
        macro_str = f"{macro_state} (#{macro_rank})"
        
        print(f"{theme_display:<42}  {total:>5}  {qual:>4}  {score:>8.2f}  {macro_str:>17}")
        
        leaders_str = str(row['Leaders']).strip()
        wrapped = textwrap.fill(
            leaders_str,
            width=95,
            initial_indent="    ↳ Stocks: ",
            subsequent_indent="              ",
            break_long_words=False,
            break_on_hyphens=False
        )
        print(wrapped)
        print()

    print("\n\n")
    print("========================================")
    print("LONG CANDIDATE UNIVERSE")
    print("Legend: * = Zacks Rank 4 or 5")
    print("========================================")

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

    if "Long_Score" in display_df.columns:
        display_df["Long_Score"] = display_df["Long_Score"].map("{:.2f}".format)

    def is_grace(row):
        clean = str(row["Ticker"]).replace("*", "").strip().upper()
        match = stocks[stocks["Ticker"].astype(str).str.upper() == clean]
        if not match.empty:
            return match.iloc[0].get("Is_Pre_Observation_Candidate", False)
        return False

    display_df["is_pre_obs"] = display_df.apply(is_grace, axis=1)

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

    true_longs = display_df[~display_df["is_pre_obs"]].drop(columns=["is_pre_obs"])
    grace_longs = display_df[display_df["is_pre_obs"]].drop(columns=["is_pre_obs"])

    if true_longs.empty:
        print("No active candidates in Long Candidate Universe.")
    else:
        print(true_longs.to_string(index=False))

    print("\n\n")
    print("========================================")
    print("PRE-OBSERVATION WATCHLIST")
    print("Legend: * = Zacks Rank 4 or 5")
    print("========================================")
    
    if grace_longs.empty:
        print("No candidates in Pre-Observation today.")
    else:
        print(grace_longs.to_string(index=False))

    deltas = compare_watchlists(
        current_long=long_candidates["Ticker"].tolist(),
        current_observation=stocks.loc[
            stocks["Tracking_State"] == "OBSERVATION",
            "Ticker",
        ].tolist(),
        current_distribution=distribution_watchlist["Ticker"].tolist(),
        recovered=recovered,
        stocks=stocks,
    )

    new_longs = deltas.get("new_longs", [])
    rec_obs = deltas.get("recovering_observation", [])
    rec_dist = deltas.get("recovering_distribution", [])
    all_rec = sorted(list(set(rec_obs + rec_dist)))
    all_rec_set = set(all_rec)
    formatted_new_longs = [
        f"{ticker}+" if ticker in all_rec_set else ticker
        for ticker in new_longs
    ]

    print("\n--- NEW LONG PIPELINE ENTRIES ---")
    print("Legend: + = Recovered from Observation/Distribution")
    
    prefix1 = "New Longs       : "
    if formatted_new_longs:
        print(textwrap.fill(", ".join(formatted_new_longs), width=95, initial_indent=prefix1, subsequent_indent=" " * len(prefix1)))
    else:
        print(f"{prefix1}None")


    print("\n\n")
    print("========================================")
    print("OBSERVATION WATCHLIST")
    print("Legend: * = Zacks Rank 4 or 5")
    print("========================================")

    obs_stocks = stocks[stocks["Tracking_State"] == "OBSERVATION"].copy()
    if obs_stocks.empty:
        print("No observation candidates today.")
    else:
        registry = load_todays_registry()
        
        days_col = []
        for ticker in obs_stocks["Ticker"]:
            t = str(ticker).replace("*", "").strip().upper()
            days = registry.get(t, {}).get("state_days", 1) if registry.get(t, {}).get("tracking_state") == "OBSERVATION" else 1
            days_col.append(days)
            
        obs_stocks["Days"] = days_col
        obs_stocks = obs_stocks.sort_values("Days", ascending=True)

        display_obs = obs_stocks[
            [
                "Days",
                "Ticker",
                "Mapped_Theme",
                "Theme_Class",
                "RS_Rating",
                "Long_Score",
                "Zacks Rank"
            ]
        ].copy()

        if "Long_Score" in display_obs.columns:
            display_obs["Long_Score"] = display_obs["Long_Score"].map("{:.2f}".format)

        if "Zacks Rank" in display_obs.columns:
            display_obs["Zacks Rank"] = (
                display_obs["Zacks Rank"]
                .fillna(0)
                .astype(int)
                .astype(str)
            )
            display_obs.loc[
                display_obs["Zacks Rank"].isin(["4", "5"]),
                "Zacks Rank"
            ] += "*"

        display_obs = display_obs.rename(
            columns={
                "Theme_Class": "Theme Classification",
            }
        )

        print(display_obs.to_string(index=False))


    print("\n\n")
    print("========================================")
    print("DISTRIBUTION WATCHLIST")
    print("========================================")

    if distribution_watchlist.empty:
        print("No qualified distribution candidates today.")
    else:
        registry = load_todays_registry()
        
        # Add Days column from registry
        days_col = []
        for ticker in distribution_watchlist["Ticker"]:
            t = ticker.replace("*", "").strip().upper()
            days = registry.get(t, {}).get("state_days", 1) if registry.get(t, {}).get("tracking_state") == "DISTRIBUTION" else 1
            days_col.append(days)
            
        distribution_watchlist["Days"] = days_col
        distribution_watchlist = distribution_watchlist.sort_values("Days", ascending=True)

        display_df = distribution_watchlist[
            [
                "Days",
                "Ticker",
                "Mapped_Theme",
                "Theme_Class",
                "RS_Rating",
                "Long_Score",
                "Zacks Rank"
            ]
        ].copy()

        if "Long_Score" in display_df.columns:
            display_df["Long_Score"] = display_df["Long_Score"].map("{:.2f}".format)

        # Format Zacks Rank identical to Long Candidates
        if "Zacks Rank" in display_df.columns:
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

    print()
    print("TRADINGVIEW WATCHLIST EXPORT")

    long_list_true = ",".join(
        [t for t in true_longs["Ticker"].astype(str).str.replace("*", "", regex=False).tolist()]
    )
    
    pre_obs_list = ",".join(
        [t for t in grace_longs["Ticker"].astype(str).str.replace("*", "", regex=False).tolist()]
    )

    observation_list = ",".join(
        stocks.loc[
            stocks["Tracking_State"] == "OBSERVATION",
            "Ticker",
        ]
        .astype(str)
        .tolist()
    )

    distribution_list = ",".join(
        distribution_watchlist["Ticker"]
        .astype(str)
        .tolist()
    )

    print("###LONG," + long_list_true + ",")
    print("###PRE_OBSERVATION," + pre_obs_list + ",")
    print("###OBSERVATION," + observation_list + ",")
    print("###DISTRIBUTION," + distribution_list + ",")

    print()
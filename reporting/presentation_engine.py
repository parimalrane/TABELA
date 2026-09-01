import pandas as pd
import sys
import io
import re
import scoring.rotation_engine
from lifecycle.stock_transition_engine import get_transition_summary
import textwrap

scoring.rotation_engine.print_rotation_report = lambda *args, **kwargs: None

from reporting.watchlist_delta_engine import compare_watchlists
from themes.theme_translation_engine import THEME_TRANSLATION


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

    has_valid_etfs = True
    print("MARKET STATISTICS")
    header = (
        f"{'ETF':<6}"
        f"{'State':>14}"
        f"{'1D%':>8}"
        f"{'5D%':>8}"
        f"{'20D%':>8}"
        f"{'50D%':>8}"
        f"{'200D%':>8}"
        f"{'Vol(M)':>8}"
        f"{'AvgV(M)':>8}"
        f"{'20Dist':>10}"
        f"{'50Dist':>10}"
        f"{'200Dist':>10}"
    )

    print("-" * len(header))
    print(header)
    print("-" * len(header))

    for etf in ["SPY", "QQQ", "IWM", "DIA"]:

        data = stats[etf]

        returns = data["returns"]
        vols = data.get("volume_data", {})
        ma = data["moving_average_extension"]

        # Format volumes in millions
        vol_m = f"{vols.get('volume', 0) / 1000000:.1f}"
        avg_m = f"{vols.get('avg_20d_vol', 0) / 1000000:.1f}"

        print(
            f"{etf:<6}"
            f"{TYPE_SYMBOL.get(data.get('day_type'),'N/A'):>14}"
            f"{fmt(returns.get('1d')):>8}"
            f"{fmt(returns.get('1w')):>8}"
            f"{fmt(returns.get('4w')):>8}"
            f"{fmt(returns.get('10w')):>8}"
            f"{fmt(returns.get('40w')):>8}"
            f"{vol_m:>8}"
            f"{avg_m:>8}"
            f"{fmt(ma.get('20dma')):>10}"
            f"{fmt(ma.get('50dma')):>10}"
            f"{fmt(ma.get('200dma')):>10}"
        )

    print()


def load_todays_registry():
    import os
    import json
    from config.runtime_context import context, get_monthly_path
    from config.config import STOCK_TRANSITION_CONFIG
    REGISTRY_DIR = STOCK_TRANSITION_CONFIG["REGISTRY_DIR"]
    today = str(context.market_date)
    
    target_dir = get_monthly_path(REGISTRY_DIR, today)
    path = os.path.join(target_dir, f"{today}_registry.json")
    
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
    import os
    ignore_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ignore_stocks.csv")
    ignore_tickers = set()
    if os.path.exists(ignore_file):
        try:
            with open(ignore_file, "r") as f:
                for line in f:
                    ticker = line.strip().upper()
                    if ticker and not ticker.startswith(","):
                        # Handling possible csv format
                        ticker = ticker.split(",")[0].strip()
                        ignore_tickers.add(ticker)
        except:
            pass

    if ignore_tickers:
        if not long_candidates.empty:
            long_candidates = long_candidates[~long_candidates["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper().isin(ignore_tickers)].copy()
        if not distribution_watchlist.empty:
            distribution_watchlist = distribution_watchlist[~distribution_watchlist["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper().isin(ignore_tickers)].copy()
        if not stocks.empty:
            stocks = stocks[~stocks["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper().isin(ignore_tickers)].copy()
            
        # Scrub Breadth Leaders safely
        theme_breadth = theme_breadth.copy()
        def scrub_leaders(leaders_str):
            if pd.isna(leaders_str) or not str(leaders_str).strip():
                return leaders_str
            tokens = []
            for t in str(leaders_str).split(","):
                clean = t.strip()
                bare_ticker = clean.replace("^", "").replace("-", "").replace("#", "").replace("~", "").upper()
                if bare_ticker not in ignore_tickers:
                    tokens.append(clean)
            return ", ".join(tokens)
            
        theme_breadth["Leaders"] = theme_breadth["Leaders"].apply(scrub_leaders)

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



    print()
    print("========================================")
    print("THEME BREADTH ANALYSIS")
    print("Legend: [No Prefix] = Long Candidate / # = Distribution")
    print("        + - = 1D Rank Delta")
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

    true_long_tickers = []
    for clean_ticker in long_candidates["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper():
        match = stocks[stocks["Ticker"].astype(str).str.upper() == clean_ticker]
        if not match.empty and not match.iloc[0].get("Is_Pre_Observation_Candidate", False):
            if clean_ticker not in true_long_tickers:
                true_long_tickers.append(clean_ticker)

    def should_display(row):
        leaders_val = row.get("Leaders")
        if pd.isna(leaders_val) or str(leaders_val).strip() == "" or str(leaders_val).strip() == "None":
            return False
            
        mapped_theme = str(row['Mapped_Theme'])
        parent_theme = THEME_TRANSLATION.get(mapped_theme, mapped_theme)
        macro_state = theme_class_map.get(parent_theme, "Unknown")
        
        if macro_state == "Neutral":
            has_valid_swing_signal = False
            for item in str(leaders_val).split(","):
                item_clean = item.strip()
                if item_clean.startswith("#"):
                    # Distribution candidate - critical for short setups and risk management
                    has_valid_swing_signal = True
                    break
                elif item_clean.upper() in true_long_tickers:
                    # True Long institutional leader
                    has_valid_swing_signal = True
                    break
                    
            if not has_valid_swing_signal:
                return False
            
        return True
        
    display_df = display_df[display_df.apply(should_display, axis=1)]

    print(f"{'Micro Theme'.ljust(30)} {'Macro Theme'.ljust(18)} {'Tot'.rjust(3)} {'Qual'.rjust(4)} {'Score'.rjust(7)}   {'Macro State & Movement'.ljust(29)}   {'Stocks'}")
    print("-" * 125)
    
    for _, row in display_df.iterrows():
        mapped_theme = str(row['Mapped_Theme'])
        parent_theme = THEME_TRANSLATION.get(mapped_theme, mapped_theme)
        
        # Format columns
        micro = (mapped_theme[:28] + "..") if len(mapped_theme) > 30 else mapped_theme.ljust(30)
        macro = (parent_theme[:16] + "..") if len(parent_theme) > 18 else parent_theme.ljust(18)
        
        total = int(row['Total_Stocks']) if pd.notna(row['Total_Stocks']) else 0
        qual = int(row['Strong_Stocks']) if pd.notna(row['Strong_Stocks']) else 0
        score = float(row['Weighted_Breadth_Score']) if pd.notna(row['Weighted_Breadth_Score']) else 0.0
        
        tot_str = str(total).rjust(3)
        q_str = str(qual).rjust(4)
        s_str = f"{score:>.2f}".rjust(7)
        
        macro_state = theme_class_map.get(parent_theme, "Unknown")
        if not theme_strength[theme_strength["Theme"] == parent_theme].empty:
            macro_rank = theme_strength[theme_strength["Theme"] == parent_theme].iloc[0]["Theme_Rank"]
            
            movement_str = ""
            if theme_performance is not None and not theme_performance.empty:
                perf_row = theme_performance[theme_performance["Theme"] == parent_theme]
                if not perf_row.empty:
                    rank_delta = perf_row.iloc[0].get("Rank Δ")
                    if pd.notna(rank_delta):
                        r_d = int(rank_delta)
                        if r_d > 0:
                            movement_str = f" -> +{r_d}"
                        elif r_d < 0:
                            movement_str = f" -> -{abs(r_d)}"
                            
            mac_state_str = f"{macro_state} ({macro_rank}{movement_str})".ljust(29)
        else:
            mac_state_str = macro_state.ljust(29)
        
        prefix = f"{micro} {macro} {tot_str} {q_str} {s_str}   {mac_state_str}   "
        prefix_len = len(prefix)
        
        leaders_str = str(row['Leaders']).strip()
        
        if not leaders_str:
            print(prefix)
            continue
            
        wrapped = textwrap.wrap(
            leaders_str, 
            width=(125 - prefix_len),
            break_long_words=False,
            break_on_hyphens=False
        )
        
        for i, line in enumerate(wrapped):
            if i == 0:
                print(f"{prefix}{line}")
            else:
                print(" " * prefix_len + line)
                
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
            "RS_Rating",
            "Long_Score",
            "Zacks Rank"
        ]
    ].copy()
    display_df["Ticker"] = display_df["Ticker"].astype(str).str.replace("*", "", regex=False)

    if "Long_Score" in display_df.columns:
        display_df["Long_Score"] = display_df["Long_Score"].map("{:.2f}".format)

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

    true_longs = display_df
    true_long_tickers = true_longs["Ticker"].tolist()

    deltas = compare_watchlists(
        current_true_long=true_long_tickers,
        current_pre_obs=[],
        current_observation=[],
        current_distribution=distribution_watchlist["Ticker"].tolist(),
        recovered=recovered,
        stocks=stocks,
    )

    movements = deltas.get("movements", {})
    days = deltas.get("days_on_list", {})
    if not true_longs.empty:
        true_longs["Movement"] = true_longs["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper().map(movements).fillna("NA")
        true_longs["Days"] = true_longs["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper().map(days).fillna(1).astype(int)

    if true_longs.empty:
        print("No active candidates in Long Candidate Universe.")
    else:
        print(true_longs.to_string(index=False))

    # Deltas already calculated above




    print("\n")
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
                "Long_Score",
                "Zacks Rank"
            ]
        ].copy()
        display_df["Ticker"] = display_df["Ticker"].astype(str).str.replace("*", "", regex=False)

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

        display_df["Movement"] = display_df["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper().map(movements).fillna("NA")
        display_df["Days"] = display_df["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper().map(days).fillna(1).astype(int)
        print(display_df.to_string(index=False))

    # Delta lists are handled natively via 'Days = 1' and the detailed Dropped Tables

    def print_dropped_table(title, tickers, stocks):
        if not tickers:
            return
        
        print("\n" + "-" * 40)
        print(f"{title} DETAILS")
        print("-" * 40)
        
        dropped_df = stocks[stocks["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper().isin(tickers)].copy()
        if dropped_df.empty:
            return
            
        display_cols = ["Ticker", "Mapped_Theme", "Theme_Class", "RS_Rating", "Long_Score", "Zacks_Score"]
        available_cols = [c for c in display_cols if c in dropped_df.columns]
        
        display_dropped = dropped_df[available_cols].rename(columns={"Theme_Class": "Theme Classification"})
        
        def get_exit_reason(row, is_long):
            from config.config import LONG_ENTRY, DIST_ENTRY
            
            rs = float(row.get("RS_Rating", 0))
            score = float(row.get("Long_Score", 0))
            theme = str(row.get("Theme Classification", ""))
            
            if is_long:
                themes_allowed = LONG_ENTRY.get("THEMES", ["Leading", "Unclassified Leader", "Unknown"])
                if theme not in themes_allowed: return "Theme Downgrade"
                if rs < LONG_ENTRY.get("MIN_RS", 90.0): return f"RS < {LONG_ENTRY.get('MIN_RS', 90)}"
                if score < LONG_ENTRY.get("MIN_LONG_SCORE", 90.0): return f"Score < {LONG_ENTRY.get('MIN_LONG_SCORE', 90)}"
                return "Not Top 3 (Crowded Out)"
            else:
                themes_allowed = DIST_ENTRY.get("THEMES", ["Lagging"])
                if theme not in themes_allowed: return "Theme Upgrade"
                if rs > DIST_ENTRY.get("MAX_RS", 50.0): return f"RS > {DIST_ENTRY.get('MAX_RS', 50)}"
                if score > DIST_ENTRY.get("MAX_LONG_SCORE", 50.0): return f"Score > {DIST_ENTRY.get('MAX_LONG_SCORE', 50)}"
                return "Not Bottom 3 (Crowded Out)"
                
        display_dropped["Exit_Reason"] = display_dropped.apply(lambda r: get_exit_reason(r, title == "DROPPED LONGS"), axis=1)

        if "Long_Score" in display_dropped.columns:
            display_dropped["Long_Score"] = display_dropped["Long_Score"].map("{:.2f}".format)
            
        display_dropped["Ticker"] = display_dropped["Ticker"].astype(str).str.replace("*", "", regex=False)
        print(display_dropped.to_string(
            index=False,
            justify="right",
            col_space={
                "Ticker": 6,
                "Mapped_Theme": 25,
                "Theme Classification": 20,
                "RS_Rating": 9,
                "Long_Score": 10,
                "Zacks_Score": 11,
                "Exit_Reason": 25
            }
        ))

    print_dropped_table("DROPPED LONGS", deltas.get('dropped_longs', []), stocks)
    print_dropped_table("DROPPED DISTRIBUTIONS", deltas.get('left_distribution', []), stocks)

    print()
    print("TRADINGVIEW WATCHLIST EXPORT")

    long_list_true = ",".join(
        [t for t in true_longs["Ticker"].astype(str).str.replace("*", "", regex=False).tolist()]
    )



    distribution_list = ",".join(
        distribution_watchlist["Ticker"]
        .astype(str)
        .tolist()
    )

    print("###LONG," + long_list_true + ",")
    print("###DISTRIBUTION," + distribution_list + ",")

    print()
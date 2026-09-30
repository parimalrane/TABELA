import pandas as pd
import sys
import io
import re
import scoring.rotation_engine

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
        from config.runtime_context import context
        market_date_str = str(context.market_date) if context.market_date else ""
        final_output.append(
            "\n"
            "==============================================\n"
            f"END OF TABELA SCAN - {market_date_str}\n"
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
    pass



def load_todays_registry():
    import os
    import json
    from config.runtime_context import context, get_monthly_path
    REGISTRY_DIR = "market_data/stock_transition"
    today = str(context.market_date)
    
    target_dir = get_monthly_path(REGISTRY_DIR, today)
    path = os.path.join(target_dir, f"{today}_registry.json")
    
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def print_macro_weather(stocks, theme_strength_settings):
    from config.runtime_context import context
    try:
        try:
            etf_df = pd.read_csv(context.etf_file, encoding='utf-16')
        except UnicodeError:
            etf_df = pd.read_csv(context.etf_file, encoding='utf-8')
    except Exception as e:
        return {}

    period_weights = theme_strength_settings.get("period_weights", {})
    if not period_weights:
        return {}

    etf_df["Raw_Mom"] = 0.0
    total_w = 0.0
    for p, w in period_weights.items():
        if p in etf_df.columns:
            etf_df["Raw_Mom"] += pd.to_numeric(etf_df[p], errors='coerce').fillna(0) * w
            total_w += w

    if total_w == 0:
        return {}
    
    spdr_map = {
        'XLK': 'Technology', 'XLY': 'Discretionary', 'XLC': 'Communications',
        'XLF': 'Financials', 'XLP': 'Staples', 'XLU': 'Utilities',
        'XLV': 'Health Care', 'XLE': 'Energy', 'XLB': 'Materials',
        'XLI': 'Industrials', 'XLRE': 'Real Estate'
    }
    
    idx_map = {'QQQ': 'Nasdaq', 'SPY': 'S&P 500', 'DIA': 'Dow Jones', 'IWM': 'Russell 2k'}
    focus = etf_df[etf_df['Ticker'].isin(list(spdr_map.keys()) + list(idx_map.keys()))].copy()
    
    sector_rs_map = {}
    green_count = 0
    top_spdrs = []
    bottom_spdrs = []
    
    import math
    spdrs_only = focus[focus['Ticker'].isin(spdr_map.keys())].copy()
    
    # Calculate Log-AUM Conviction Multiplier
    spdrs_only["AUM"] = pd.to_numeric(spdrs_only["Market Value (mil)"], errors='coerce').fillna(0)
    spdrs_only["Log_AUM"] = spdrs_only["AUM"].apply(lambda x: math.log10(x) if x > 10 else 1)
    
    # Institutional Impact Score (Momentum * Gravity)
    spdrs_only["Impact_Mom"] = spdrs_only["Raw_Mom"] * spdrs_only["Log_AUM"]
    
    # Rank 1 to 11 exactly (1 = Highest Institutional Impact)
    spdrs_only["Sector_Rank"] = spdrs_only["Impact_Mom"].rank(ascending=False, method='min')
    spdrs_only = spdrs_only.sort_values("Impact_Mom", ascending=False)
    
    w_pos = 0; w_neg = 0
    m_pos = 0; m_neg = 0
    q_pos = 0; q_neg = 0
    
    sector_matrix_strs = []
    for _, row in spdrs_only.iterrows():
        t = row["Ticker"]
        rank_val = int(row["Sector_Rank"])
        sector_rs_map[t] = rank_val
        
        perf_1w = pd.to_numeric(row.get("Performance 1W (%)", 0), errors='coerce')
        perf_1m = pd.to_numeric(row.get("Performance 1M (%)", 0), errors='coerce')
        perf_3m = pd.to_numeric(row.get("Performance 3M (%)", 0), errors='coerce')
        perf_ytd = pd.to_numeric(row.get("Performance YTD (%)", row.get("Performance 1Y (%)", 0)), errors='coerce')
        
        perf_1w = perf_1w if pd.notna(perf_1w) else 0.0
        perf_1m = perf_1m if pd.notna(perf_1m) else 0.0
        perf_3m = perf_3m if pd.notna(perf_3m) else 0.0
        perf_ytd = perf_ytd if pd.notna(perf_ytd) else 0.0
        
        if perf_1w >= 0: w_pos += 1
        else: w_neg += 1
            
        if perf_1m >= 0: m_pos += 1
        else: m_neg += 1
            
        if perf_3m >= 0: q_pos += 1
        else: q_neg += 1
            
        aum_val = row.get("AUM", 0)
        impact = row.get("Impact_Mom", 0)
        aum_b = (aum_val / 1000.0) if aum_val > 0 else 0.0
        

        name = spdr_map[t]
        sector_matrix_strs.append(
            f"    {rank_val:<4} {name:<15} ({t})  {perf_1w:>+8.2f}% {perf_1m:>+9.2f}% {perf_3m:>+10.2f}% {perf_ytd:>+9.2f}%   ${aum_b:>6.1f}B   {impact:>7.1f}"
        )
            
    idx_strs = []
    idx_only = focus[focus['Ticker'].isin(idx_map.keys())].copy()
    
    # Pre-sort to maintain QQQ, SPY, IWM, DIA order
    for t in ['QQQ', 'SPY', 'IWM', 'DIA']:
        row_eval = idx_only[idx_only["Ticker"] == t]
        if not row_eval.empty:
            r = row_eval.iloc[0]
            p1w = pd.to_numeric(r.get("Performance 1W (%)", 0), errors='coerce')
            p1m = pd.to_numeric(r.get("Performance 1M (%)", 0), errors='coerce')
            p3m = pd.to_numeric(r.get("Performance 3M (%)", 0), errors='coerce')
            pytd = pd.to_numeric(r.get("Performance YTD (%)", r.get("Performance 1Y (%)", 0)), errors='coerce')
            
            p1w = p1w if pd.notna(p1w) else 0.0
            p1m = p1m if pd.notna(p1m) else 0.0
            p3m = p3m if pd.notna(p3m) else 0.0
            pytd = pytd if pd.notna(pytd) else 0.0
            
            name = f"{idx_map[t]} ({t})"
            idx_strs.append(f"    {name:<17} {p1w:>+8.2f}% {p1m:>+9.2f}% {p3m:>+10.2f}% {pytd:>+13.2f}%")
        
    nh = nl = net = 0
    if "Price as a % of 52 Wk H-L Range" in stocks.columns:
        valid_range = pd.to_numeric(stocks["Price as a % of 52 Wk H-L Range"], errors='coerce').dropna()
        nh = len(valid_range[valid_range >= 98])
        nl = len(valid_range[valid_range <= 2])
        net = nh - nl

    print("\n========================================================================")
    print("              MACRO WEATHER REPORT & BREADTH X-RAY")
    print("========================================================================")
    print("[1] MARKET INDEXES (Multi-Timeframe Performance)")
    print(f"    {'Index':<17} {'1-Week':>9} {'1-Month':>10} {'1-Quarter':>11} {'Year-To-Date':>14}")
    print("    " + "-"*56)
    for line in idx_strs:
        print(line)
    print("")
    print("[2] MACRO SECTOR RANKINGS (Gravity-Weighted Capital Flows)")
    print(f"    > Sector Breadth  : W (+{w_pos}/-{w_neg}) ; M (+{m_pos}/-{m_neg}) ; Q (+{q_pos}/-{q_neg})\n")
    print(f"    {'Rank':<4} {'Sector':<15} {'SPDR'}  {'1-Week':>9} {'1-Month':>10} {'1-Quarter':>11} {'YTD':>10}   {'AUM ($B)':>9}   {'Impact':>7}")
    print("    " + "-"*92)
    for line in sector_matrix_strs:
        print(line)
    print("")
    print("[3] STRUCTURAL BREADTH (3,000+ Equities)")
    print(f"    > Price Extremes  : {nh} New Highs | {nl} New Lows  [ Net: {net:+} ]")
    print("========================================================================\n")

    return sector_rs_map


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
    # The pipeline prints MARKET STATISTICS externally somewhere, we slip this in 
    # to render right before Theme Breadth.
    
    sector_rs_map = print_macro_weather(stocks, theme_strength_settings)

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
        macro_for_lookup = THEME_TRANSLATION.get(mapped_theme, mapped_theme)
            
        macro_state = theme_class_map.get(macro_for_lookup, "Unknown")
        
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
            ts_row = theme_strength[theme_strength["Theme"] == parent_theme].iloc[0]
            macro_rank = ts_row["Theme_Rank"]
            
            movement_str = ""
            if theme_performance is not None and not theme_performance.empty:
                perf_row = theme_performance[theme_performance["Theme"] == parent_theme]
                if not perf_row.empty:
                    rank_delta = perf_row.iloc[0].get("Rank Δ")
                    if pd.notna(rank_delta):
                        r_d = int(rank_delta)
                        if r_d > 0:
                            movement_str = f" -> -{r_d}"
                        elif r_d < 0:
                            movement_str = f" -> +{abs(r_d)}"
                            
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

    ZACKS_TO_SPDR = {
        "Computer and Technology": "XLK", "Business Services": "XLK",
        "Finance": "XLF", "Medical": "XLV", "Oils-Energy": "XLE",
        "Consumer Discretionary": "XLY", "Retail-Wholesale": "XLY", "Auto-Tires-Trucks": "XLY",
        "Consumer Staples": "XLP", "Utilities": "XLU", "Basic Materials": "XLB",
        "Construction": "XLI", "Industrial Products": "XLI", "Aerospace": "XLI",
        "Transportation": "XLI", "Conglomerates": "XLI", "Multi-Sector Conglomerates": "XLI"
    }

    if long_candidates is not None:
        if "Sector" in long_candidates.columns:
            long_candidates["Sector (SPDR)"] = long_candidates["Sector"].map(ZACKS_TO_SPDR).fillna("N/A")
            long_candidates["Sector Rank"] = long_candidates["Sector (SPDR)"].map(sector_rs_map).fillna(0).astype(int)

    if distribution_watchlist is not None:
        if "Sector" in distribution_watchlist.columns:
            distribution_watchlist["Sector (SPDR)"] = distribution_watchlist["Sector"].map(ZACKS_TO_SPDR).fillna("N/A")
            distribution_watchlist["Sector Rank"] = distribution_watchlist["Sector (SPDR)"].map(sector_rs_map).fillna(0).astype(int)

    print("========================================")
    print("LONG CANDIDATE UNIVERSE")
    print("Legend: ^ = Micro Leader | ~ = Unknown/Unclassified")
    print("========================================")

    display_df = long_candidates[
        [
            "Ticker",
            "Mapped_Theme",
            "Theme_Class",
            "Long_Score",
            "RS_Rating",
            "Sector (SPDR)",
            "Sector Rank"
        ]
    ].copy()
    display_df["Ticker"] = display_df["Ticker"].astype(str).str.replace("*", "", regex=False)
    
    # Prepend tag directly to the Ticker string for clean left-side reading
    display_df.loc[display_df["Theme_Class"] == "Micro Leader", "Ticker"] = "^" + display_df["Ticker"]
    display_df.loc[display_df["Theme_Class"].isin(["Unknown", "Unclassified Leader"]), "Ticker"] = "~" + display_df["Ticker"]
    
    # Drop the Theme_Class column
    display_df = display_df.drop(columns=["Theme_Class"])

    if "Long_Score" in display_df.columns:
        display_df["Long_Score"] = display_df["Long_Score"].map("{:.2f}".format)

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
        
        # Merge columns to save horizontal space
        true_longs["Sector (Rk)"] = true_longs["Sector (SPDR)"].astype(str) + " (" + true_longs["Sector Rank"].astype(str) + ")"
        
        # Keep Movement but format it cleaner if needed. Wait, we want to restore Movement.
        true_longs["Ticker"] = true_longs["Ticker"].apply(lambda t: f" {str(t).strip()}")
        
        # Drop the un-merged columns
        true_longs = true_longs.drop(columns=["Sector (SPDR)", "Sector Rank"])
        
    if true_longs.empty:
        print("No active candidates in Long Candidate Universe.")
    else:
        print(true_longs.to_string(index=False))

    # Deltas already calculated above




    print("\n")
    print("========================================")
    print("DISTRIBUTION WATCHLIST")
    print("Legend: ^ = Micro Laggard")
    print("========================================")

    if distribution_watchlist.empty:
        print("No qualified distribution candidates today.")
    else:
        display_df = distribution_watchlist[
            [
                "Ticker",
                "Mapped_Theme",
                "Theme_Class",
                "Long_Score",
                "RS_Rating",
                "Sector (SPDR)",
                "Sector Rank"
            ]
        ].copy()
        display_df["Ticker"] = display_df["Ticker"].astype(str).str.replace("*", "", regex=False)

        # Prepend tag directly to the Ticker string
        display_df.loc[display_df["Theme_Class"] == "Micro Laggard", "Ticker"] = "^" + display_df["Ticker"]

        # Drop the Theme_Class column
        display_df = display_df.drop(columns=["Theme_Class"])

        if "Long_Score" in display_df.columns:
            display_df["Long_Score"] = display_df["Long_Score"].map("{:.2f}".format)

        display_df["Movement"] = display_df["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper().map(movements).fillna("NA")
        display_df["Days"] = display_df["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper().map(days).fillna(1).astype(int)
        
        display_df["Sector (Rk)"] = display_df["Sector (SPDR)"].astype(str) + " (" + display_df["Sector Rank"].astype(str) + ")"
        
        display_df["Ticker"] = display_df["Ticker"].apply(lambda t: f" {str(t).strip()}")
        display_df = display_df.drop(columns=["Sector (SPDR)", "Sector Rank"])
        
        print(display_df.to_string(index=False))

    # Delta lists are handled natively via 'Days = 1' and the detailed Dropped Tables

    # ========================================
    # TradingView Watchlist Export
    # ========================================
    def clean_all_tickers(df):
        """Extract all tickers from a DataFrame, cleaned of prefix markers."""
        if df.empty:
            return ""
        return ",".join(
            df["Ticker"].astype(str)
            .str.replace("*", "", regex=False)
            .str.replace("+", "", regex=False)
            .str.replace("^", "", regex=False)
            .str.replace("~", "", regex=False)
            .str.strip().tolist()
        )

    full_long_list = clean_all_tickers(true_longs)
    full_short_list = clean_all_tickers(display_df)

    # --- Accumulated Dropped History (21-Day Expiry + Auto-Purge) ---
    import json as _json
    from datetime import datetime, timedelta
    from config.runtime_context import context

    dropped_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "market_data", "dropped_accumulator.json"
    )

    # Dictionary format: {"TICKER": "YYYY-MM-DD"}
    accumulated = {"long_dropped": {}, "short_dropped": {}}
    if os.path.exists(dropped_file):
        try:
            with open(dropped_file, "r", encoding="utf-8") as _f:
                loaded = _json.load(_f)
                
                # Check if legacy format (lists) and wipe if true
                if isinstance(loaded.get("long_dropped", []), list):
                    pass # Schema change requires fresh start
                else:
                    accumulated = loaded
        except Exception:
            pass

    current_date_str = str(context.market_date) if hasattr(context, "market_date") else datetime.today().strftime("%Y-%m-%d")
    current_date = datetime.strptime(current_date_str, "%Y-%m-%d")

    # Add today's drops
    for t in deltas.get("dropped_longs", []):
        clean = str(t).replace("*", "").replace("^", "").replace("~", "").strip().upper()
        if clean:
            accumulated["long_dropped"][clean] = current_date_str

    for t in deltas.get("left_distribution", []):
        clean = str(t).replace("*", "").replace("^", "").replace("~", "").strip().upper()
        if clean:
            accumulated["short_dropped"][clean] = current_date_str

    # Process Auto-Purge and Expiry
    from config.config import LONG_ENTRY, DIST_ENTRY
    min_dropped_long = LONG_ENTRY.get("MIN_DROPPED_WATCH_SCORE", 70.0)
    max_dropped_dist = DIST_ENTRY.get("MAX_DROPPED_WATCH_SCORE", 30.0)

    def clean_accumulator(dropped_dict, active_list_str, is_long=True):
        active_set = set(t.strip().upper() for t in active_list_str.split(",") if t.strip())
        cleaned = {}
        for ticker, date_str in dropped_dict.items():
            # Opt 4: Auto-Purge if re-entered active list
            if ticker in active_set:
                continue
                
            # Technical Floor & Macro Theme Eviction
            match = stocks[stocks["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper() == ticker]
            if not match.empty:
                row = match.iloc[0]
                current_rs = pd.to_numeric(row.get("RS_Rating"), errors='coerce')
                current_score = pd.to_numeric(row.get("Long_Score"), errors='coerce')
                current_theme = str(row.get("Theme_Class", ""))
                
                zacks_raw = row.get("Zacks Rank", 0)
                try:
                    current_zacks = int(float(zacks_raw)) if pd.notna(zacks_raw) else 0
                except (ValueError, TypeError):
                    current_zacks = 0
                
                if pd.notna(current_rs) and pd.notna(current_score):
                    if is_long:
                        if current_rs < min_dropped_long or current_score < min_dropped_long:
                            continue  # Purge, either price or total composite is broken
                        if current_theme in DIST_ENTRY.get("THEMES", []):
                            continue  # Purge, macro theme has died (Lagging)
                        if current_zacks in LONG_ENTRY.get("BLOCKED_ZACKS", []):
                            continue  # Purge, fundamentally broken (Zacks 4/5)
                    if not is_long:
                        if current_rs > max_dropped_dist or current_score > max_dropped_dist:
                            continue  # Purge, shorts are squeezing upward
                        if current_theme in LONG_ENTRY.get("THEMES", []):
                            continue  # Purge, macro theme has rallied (Leading)
                        if current_zacks in DIST_ENTRY.get("BLOCKED_ZACKS", []):
                            continue  # Purge, fundamentals too strong to short (Zacks 1/2)

            # 21-Day Time Expiry
            try:
                date_val = datetime.strptime(date_str, "%Y-%m-%d")
                days_old = (current_date - date_val).days
                if days_old <= 21:
                    cleaned[ticker] = date_str
            except Exception:
                pass
        return cleaned

    accumulated["long_dropped"] = clean_accumulator(accumulated["long_dropped"], full_long_list, is_long=True)
    accumulated["short_dropped"] = clean_accumulator(accumulated["short_dropped"], full_short_list, is_long=False)

    # Save updated accumulator
    try:
        os.makedirs(os.path.dirname(dropped_file), exist_ok=True)
        with open(dropped_file, "w", encoding="utf-8") as _f:
            _json.dump(accumulated, _f, indent=4)
    except Exception:
        pass

    long_dropped_str = ",".join(sorted(accumulated["long_dropped"].keys()))
    short_dropped_str = ",".join(sorted(accumulated["short_dropped"].keys()))

    def print_dropped_table(dropped_dict, title):
        if not dropped_dict: return
        rows = []
        for ticker, date_str in dropped_dict.items():
            try:
                days_on_drop = (current_date - datetime.strptime(date_str, "%Y-%m-%d")).days
            except:
                days_on_drop = 0
                
            match = stocks[stocks["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper() == ticker]
            if not match.empty:
                r = match.iloc[0]
                theme_class = str(r.get("Theme_Class", "Unknown"))
                spdr = ZACKS_TO_SPDR.get(str(r.get("Sector", "")), "N/A")
                s_rank = sector_rs_map.get(spdr, 0)
                
                display_ticker = ticker
                if theme_class == "Micro Leader": display_ticker = "^" + ticker
                elif theme_class in ["Unknown", "Unclassified Leader"]: display_ticker = "~" + ticker
                
                rs_val = pd.to_numeric(r.get("RS_Rating", 0), errors='coerce')
                score_val = pd.to_numeric(r.get("Long_Score", 0), errors='coerce')
                
                rows.append({
                    "Ticker": display_ticker,
                    "Mapped_Theme": str(r.get("Mapped_Theme", "Unknown")),
                    "Long_Score": round(score_val, 2),
                    "RS_Rating": int(rs_val),
                    "Days Out": days_on_drop,
                    "Sector (Rk)": f"{spdr} ({int(s_rank)})"
                })
        if rows:
            df = pd.DataFrame(rows).sort_values(["Days Out", "Long_Score", "RS_Rating"], ascending=[True, False, False])
            print("=" * 40)
            print(title)
            print("=" * 40)
            print(df.to_string(index=False))
            print()

    print()
    print_dropped_table(accumulated["long_dropped"], "RECENTLY DROPPED LONGS (Watch For Breakdown)")
    print_dropped_table(accumulated["short_dropped"], "RECENTLY DROPPED SHORTS (Watch For Squeeze)")

    print("TRADINGVIEW WATCHLIST EXPORT")
    if full_long_list:
        print("###LONG," + full_long_list + ",")
    if full_short_list:
        print("###SHORT," + full_short_list + ",")
    if long_dropped_str:
        print("###LONG_Dropped," + long_dropped_str + ",")
    if short_dropped_str:
        print("###SHORT_Dropped," + short_dropped_str + ",")

    print()
import os
import json
from pathlib import Path
from datetime import datetime, date
import pandas as pd
import sys
import io
import re
import scoring.rotation_engine

import textwrap

scoring.rotation_engine.print_rotation_report = lambda *args, **kwargs: None

from reporting.watchlist_delta_engine import compare_watchlists
from themes.theme_translation_engine import THEME_TRANSLATION, THEME_ETF_MAPPING
from config.runtime_context import context



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
        ("STRONG_BULLISH", "1. STRONG BULLISH UNIVERSE"),
        ("MILD_BULLISH", "2. MILD BULLISH UNIVERSE"),
        ("STRONG_BEARISH", "3. STRONG BEARISH UNIVERSE"),
        ("MILD_BEARISH", "4. MILD BEARISH UNIVERSE"),
        ("TRADINGVIEW_EXPORT", "TRADINGVIEW WATCHLIST EXPORT"),
        ("DROPPED_EXPORT", "DROPPED WATCHLIST EXPORT"),
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
        "STRONG_BULLISH",
        "MILD_BULLISH",
        "STRONG_BEARISH",
        "MILD_BEARISH",
        "TRADINGVIEW_EXPORT",
        "DROPPED_EXPORT",
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


def _load_historical_breadth_nets(limit=10):
    from pathlib import Path
    from config.runtime_context import context
    data_dir = Path("market_data") / "input_files"
    cur_date = str(context.market_date).replace("-", "")
    by_date = {}
    for p in data_dir.rglob("*_stocks.csv"):
        d_str = p.stem.replace("_stocks", "").replace("-", "")
        if d_str < cur_date:
            by_date[d_str] = p
    stock_files = [by_date[d] for d in sorted(by_date.keys())[-limit:]]
    nets = []
    for f in stock_files:
        try:
            try:
                df = pd.read_csv(f)
            except UnicodeError:
                df = pd.read_csv(f, encoding="utf-16")
            if "Price as a % of 52 Wk H-L Range" in df.columns:
                valid_range = pd.to_numeric(
                    df["Price as a % of 52 Wk H-L Range"],
                    errors='coerce'
                ).dropna()
                nh = len(valid_range[valid_range >= 98])
                nl = len(valid_range[valid_range <= 2])
                nets.append(nh - nl)
        except Exception:
            continue
    return nets


def _load_historical_advance_decline(limit=10):
    from pathlib import Path
    from config.runtime_context import context
    data_dir = Path("market_data") / "input_files"
    cur_date = str(context.market_date).replace("-", "")
    by_date = {}
    for p in data_dir.rglob("*_stocks.csv"):
        d_str = p.stem.replace("_stocks", "").replace("-", "")
        if d_str <= cur_date:
            by_date[d_str] = p

    # Need limit + 1 files to calculate limit transitions
    stock_files = [by_date[d] for d in sorted(by_date.keys())[-(limit + 1):]]
    if len(stock_files) < 2:
        return 0, 0, 0.0, []

    series_list = []
    for f in stock_files:
        try:
            try:
                df = pd.read_csv(f, usecols=["Ticker", "Last Close"])
            except UnicodeError:
                df = pd.read_csv(f, usecols=["Ticker", "Last Close"], encoding="utf-16")
            px = pd.to_numeric(df["Last Close"].astype(str).str.replace(r'[%$,]', '', regex=True), errors='coerce')
            s = pd.Series(px.values, index=df["Ticker"].astype(str).str.upper()).dropna()
            s = s.groupby(level=0).first()
            series_list.append(s)
        except Exception:
            continue

    if len(series_list) < 2:
        return 0, 0, 0.0, []

    ad_nets = []
    today_adv = today_dec = 0
    for i in range(1, len(series_list)):
        s_prev = series_list[i - 1]
        s_curr = series_list[i]
        common = s_curr.index.intersection(s_prev.index)
        diff = s_curr.loc[common] - s_prev.loc[common]
        adv = int((diff > 0).sum())
        dec = int((diff < 0).sum())
        net = adv - dec
        ad_nets.append(net)
        if i == len(series_list) - 1:
            today_adv = adv
            today_dec = dec

    ratio = round(today_adv / today_dec, 2) if today_dec > 0 else 0.0
    return today_adv, today_dec, ratio, ad_nets


def _range_data_quality_warning(stocks, blank_jump_pct=5.0, min_lost_near_lows=200):
    """
    Data-QA guard for the 52-week-range column that feeds New Highs / New Lows.
    Blank values are counted as neither a high nor a low, so a sudden jump in
    blanks (especially among names that were near lows the prior day) silently
    understates New Lows. Returns a warning string, or "" when data looks sane.
    """
    col = "Price as a % of 52 Wk H-L Range"
    try:
        from config.runtime_context import context
        if stocks is None or stocks.empty or col not in stocks.columns:
            return ""
        cur_date = str(context.market_date)
        prev_files = sorted(
            [p for p in (Path("market_data") / "input_files").rglob("*_stocks.csv")
             if p.stem.replace("_stocks", "") < cur_date.replace("-", "")],
            key=lambda p: p.stem,
        )
        if not prev_files:
            return ""
        prev = pd.read_csv(prev_files[-1])
        if col not in prev.columns:
            return ""

        cur_vals = pd.to_numeric(stocks[col], errors="coerce")
        prev_vals = pd.to_numeric(prev[col], errors="coerce")
        cur_blank_pct = cur_vals.isna().mean() * 100
        prev_blank_pct = prev_vals.isna().mean() * 100

        def _clean(df):
            t = df["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper()
            return t

        cur_s = pd.Series(cur_vals.values, index=_clean(stocks)).groupby(level=0).first()
        prev_s = pd.Series(prev_vals.values, index=_clean(prev)).groupby(level=0).first()
        common = cur_s.index.intersection(prev_s.index)
        lost = prev_s.loc[common].notna() & cur_s.loc[common].isna()
        lost_near_lows = int((lost & (prev_s.loc[common] <= 10)).sum())

        jump = cur_blank_pct - prev_blank_pct
        if jump >= blank_jump_pct or lost_near_lows >= min_lost_near_lows:
            return (
                f"    ! DATA WARNING: 52-wk range blank {cur_blank_pct:.1f}% "
                f"(prior file {prev_blank_pct:.1f}%, {jump:+.1f} pts); "
                f"{lost_near_lows} names that were <=10 on prior file are now blank. "
                f"New Lows are likely UNDERSTATED - verify the source export."
            )
    except Exception:
        pass
    return ""


def _compute_breadth_streaks(nets):
    if len(nets) < 2:
        return []
    trends = []
    for i in range(1, len(nets)):
        prev_net = nets[i - 1]
        curr_net = nets[i]
        if curr_net > prev_net:
            trends.append("\u2191")
        elif curr_net < prev_net:
            trends.append("\u2193")
        else:
            trends.append("\u2192")
    streaks = []
    curr_trend = trends[0]
    count = 1
    for t in trends[1:]:
        if t == curr_trend:
            count += 1
        else:
            streaks.append((curr_trend, count))
            curr_trend = t
            count = 1
    streaks.append((curr_trend, count))
    return streaks


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
    legacy_data_list = []
    for _, row in spdrs_only.iterrows():
        t = row["Ticker"]
        rank_val = int(row["Sector_Rank"])
        sector_rs_map[t] = rank_val
        legacy_data_list.append({"Ticker": t, "Impact_Mom": row.get("Impact_Mom", 0)})
        
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
            p1d = pd.to_numeric(r.get("Performance 1D (%)", 0), errors='coerce')
            p1w = pd.to_numeric(r.get("Performance 1W (%)", 0), errors='coerce')
            p1m = pd.to_numeric(r.get("Performance 1M (%)", 0), errors='coerce')
            p3m = pd.to_numeric(r.get("Performance 3M (%)", 0), errors='coerce')
            pytd = pd.to_numeric(r.get("Performance YTD (%)", r.get("Performance 1Y (%)", 0)), errors='coerce')
            
            p1d = p1d if pd.notna(p1d) else 0.0
            p1w = p1w if pd.notna(p1w) else 0.0
            p1m = p1m if pd.notna(p1m) else 0.0
            p3m = p3m if pd.notna(p3m) else 0.0
            pytd = pytd if pd.notna(pytd) else 0.0
            
            name = f"{idx_map[t]} ({t})"
            idx_strs.append(f"    {name:<17} {p1d:>+7.2f}% {p1w:>+8.2f}% {p1m:>+9.2f}% {p3m:>+10.2f}% {pytd:>+13.2f}%")
        
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
    print(f"    {'Index':<17} {'1-Day':>8} {'1-Week':>9} {'1-Month':>10} {'1-Quarter':>11} {'Year-To-Date':>14}")
    print("    " + "-"*65)
    for line in idx_strs:
        print(line)
    print("")
    
    stock_count_str = f"{len(stocks):,} Equities" if stocks is not None and not stocks.empty else "3,000+ Equities"
    print(f"[2] STRUCTURAL BREADTH ({stock_count_str})")

    # --- Breadth & Sentiment Calculations ---
    adv_today, dec_today, ad_ratio, ad_nets = _load_historical_advance_decline(limit=10)
    historical_nets = _load_historical_breadth_nets(limit=10)

    b_5d = None
    b_20d = None
    pulse_lbl = "BALANCED"
    trend_lbl = "HEALTHY"
    if stocks is not None and not stocks.empty:
        px = pd.to_numeric(stocks["Last Close"].astype(str).str.replace(r'[%$,]', '', regex=True), errors='coerce')
        vol = pd.to_numeric(stocks["Avg Volume"].astype(str).str.replace(r'[%$,]', '', regex=True), errors='coerce')
        liquid = (px >= 10) & (vol >= 500_000)
        eval_stocks = stocks[liquid] if liquid.sum() >= 100 else stocks

        if "% Price Change (1 Week)" in eval_stocks.columns:
            p1w = pd.to_numeric(eval_stocks["% Price Change (1 Week)"].astype(str).str.replace(r'[%$,]', '', regex=True), errors='coerce').dropna()
            if not p1w.empty:
                b_5d = int(round((p1w > 0).mean() * 100))

        if "% Price Change (4 Weeks)" in eval_stocks.columns:
            p4w = pd.to_numeric(eval_stocks["% Price Change (4 Weeks)"].astype(str).str.replace(r'[%$,]', '', regex=True), errors='coerce').dropna()
            if not p4w.empty:
                b_20d = int(round((p4w > 0).mean() * 100))

    # --- Structural Breadth Output Rows ---
    if ad_nets:
        ad_streak_str = " , ".join([f"{n:+d}" for n in reversed(ad_nets)])
        print(f"    Advance / Decline : Ratio {ad_ratio:.2f}  ({adv_today:,} Adv / {dec_today:,} Dec)  | 10D Net (Today -> Past): {ad_streak_str}")

    if historical_nets:
        ext_all = [f"{net:+d}"] + [f"{n:+d}" for n in reversed(historical_nets[-9:])]
        ext_streak_str = " , ".join(ext_all)
    else:
        ext_streak_str = f"{net:+d}"
    print(f"    Price Extremes    : Net {net:+d}  ({nh} Highs / {nl} Lows)     | 10D Net (Today -> Past): {ext_streak_str}")

    if b_5d is not None and b_20d is not None:
        print(f"    Market Sentiment  : 5-Day: {b_5d}% Positive                  | 20-Day: {b_20d}% Positive")
    _qa_warn = _range_data_quality_warning(stocks)
    if _qa_warn:
        print(_qa_warn)
    print("========================================================================\n")

    return sector_rs_map, legacy_data_list, {"w": (w_pos, w_neg), "m": (m_pos, m_neg), "q": (q_pos, q_neg)}


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
    sector_rs_map = {}
    legacy_data_list = []
    breadth = {"w": (0,0), "m": (0,0), "q": (0,0)}
    
    try:
        macro_results = print_macro_weather(stocks, theme_strength_settings)
        if isinstance(macro_results, tuple) and len(macro_results) == 3:
            sector_rs_map, legacy_data_list, breadth = macro_results
        elif isinstance(macro_results, dict):
            sector_rs_map = macro_results
    except Exception:
        # Log the exception if necessary, but proceed with empty data
        pass

    # --- Inject Sector Intelligence Output ---
    try:
        from scoring.sector_intelligence import SectorIntelligence, get_historical_etf_path
        from config.runtime_context import context
        curr_etf = str(context.etf_file)
        hist_etf = get_historical_etf_path(curr_etf, days_back=7)
        si = SectorIntelligence(curr_etf, hist_etf)
        report_data = si.generate_intelligence_report()
        report_str = si.format_terminal_output(report_data, legacy_data_list, breadth)
        if False and report_str:
            print(report_str)
        if report_data and "sectors" in report_data:
            for s_rec in report_data["sectors"]:
                sector_rs_map[s_rec["Ticker"]] = int(s_rec["Rank"])
            print(report_str)
    except Exception:
        pass
    # ---------------------------------------
    import math
    theme_breadth["Strong_Stocks"] = pd.to_numeric(theme_breadth["Strong_Stocks"], errors="coerce").fillna(0).astype(int)
    theme_breadth["Avg_Strong_RS"] = pd.to_numeric(theme_breadth["Avg_Strong_RS"], errors="coerce").fillna(0.0)
    theme_breadth["Breadth_Percent"] = round((theme_breadth["Strong_Stocks"] / theme_breadth["Total_Stocks"]) * 100, 2)
    theme_breadth["Weighted_Breadth_Score"] = round(
        theme_breadth["Breadth_Percent"] * (theme_breadth["Avg_Strong_RS"] / 100) * theme_breadth["Total_Stocks"].apply(lambda x: math.log(x + 1)), 2
    )
    theme_breadth = theme_breadth.sort_values("Weighted_Breadth_Score", ascending=False)

    print("========================================")
    print("THEME BREADTH ANALYSIS")
    print("Legend: [No Prefix]=Long / #=Short")
    print("        + - = 1D Rank Delta")
    print("========================================")

    # --- INJECT RE-ENTRY STOCKS INTO BREADTH (replacing legacy Mild) ---
    import os
    import json as _json
    tracker_file_breadth = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "market_data", "reentry_tracker.json"
    )
    reentry_breadth = {"long_reentered": {}, "short_reentered": {}}
    if os.path.exists(tracker_file_breadth):
        try:
            with open(tracker_file_breadth, "r", encoding="utf-8") as _f:
                loaded_tr = _json.load(_f)
                if isinstance(loaded_tr, dict):
                    reentry_breadth = loaded_tr
        except Exception:
            pass

    for ticker in reentry_breadth.get("long_reentered", {}).keys():
        match = stocks[stocks["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper() == ticker]
        if not match.empty:
            theme = match.iloc[0].get("Mapped_Theme")
            if theme in theme_breadth["Mapped_Theme"].values:
                curr = theme_breadth.loc[theme_breadth["Mapped_Theme"] == theme, "Leaders"].iloc[0]
                existing = [t.strip().lstrip("#") for t in str(curr).split(",") if t.strip()]
                if ticker not in existing:
                    new_val = f"{ticker}" if pd.isna(curr) or str(curr).strip() in ("", "None", "nan") else f"{curr}, {ticker}"
                    c_strong = theme_breadth.loc[theme_breadth["Mapped_Theme"] == theme, "Strong_Stocks"].iloc[0]
                    c_rs = theme_breadth.loc[theme_breadth["Mapped_Theme"] == theme, "Avg_Strong_RS"].iloc[0]
                    st_rs = float(pd.to_numeric(match.iloc[0].get("RS_Rating", 70), errors="coerce") or 70)
                    theme_breadth.loc[theme_breadth["Mapped_Theme"] == theme, "Strong_Stocks"] = c_strong + 1
                    theme_breadth.loc[theme_breadth["Mapped_Theme"] == theme, "Avg_Strong_RS"] = (c_rs * c_strong + st_rs) / (c_strong + 1)
                    theme_breadth.loc[theme_breadth["Mapped_Theme"] == theme, "Leaders"] = new_val

    for ticker in reentry_breadth.get("short_reentered", {}).keys():
        match = stocks[stocks["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper() == ticker]
        if not match.empty:
            theme = match.iloc[0].get("Mapped_Theme")
            if theme in theme_breadth["Mapped_Theme"].values:
                curr = theme_breadth.loc[theme_breadth["Mapped_Theme"] == theme, "Leaders"].iloc[0]
                existing = [t.strip().lstrip("#") for t in str(curr).split(",") if t.strip()]
                if ticker not in existing:
                    new_val = f"#{ticker}" if pd.isna(curr) or str(curr).strip() in ("", "None", "nan") else f"{curr}, #{ticker}"
                    c_strong = theme_breadth.loc[theme_breadth["Mapped_Theme"] == theme, "Strong_Stocks"].iloc[0]
                    c_rs = theme_breadth.loc[theme_breadth["Mapped_Theme"] == theme, "Avg_Strong_RS"].iloc[0]
                    st_short_rs = float(pd.to_numeric(match.iloc[0].get("Short_RS_Rating", 50), errors="coerce") or 50)
                    st_rs = max(1.0, 100.0 - st_short_rs)
                    theme_breadth.loc[theme_breadth["Mapped_Theme"] == theme, "Strong_Stocks"] = c_strong + 1
                    theme_breadth.loc[theme_breadth["Mapped_Theme"] == theme, "Avg_Strong_RS"] = (c_rs * c_strong + st_rs) / (c_strong + 1)
                    theme_breadth.loc[theme_breadth["Mapped_Theme"] == theme, "Leaders"] = new_val

    # --- INJECT SHORT CANDIDATES INTO BREADTH LEADERS ---
    import math
    theme_breadth["Strong_Stocks"] = pd.to_numeric(theme_breadth["Strong_Stocks"], errors="coerce").fillna(0).astype(int)
    theme_breadth["Avg_Strong_RS"] = pd.to_numeric(theme_breadth["Avg_Strong_RS"], errors="coerce").fillna(0.0)
    theme_breadth["Breadth_Percent"] = round((theme_breadth["Strong_Stocks"] / theme_breadth["Total_Stocks"]) * 100, 2)
    theme_breadth["Weighted_Breadth_Score"] = round(
        theme_breadth["Breadth_Percent"] * (theme_breadth["Avg_Strong_RS"] / 100) * theme_breadth["Total_Stocks"].apply(lambda x: math.log(x + 1)), 2
    )
    theme_breadth = theme_breadth.sort_values("Weighted_Breadth_Score", ascending=False)
    
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

    # Micro Leader / Micro Lagging lookup: {micro_theme: (tier, etf, etf_rs)}
    micro_tier_by_theme = {}
    try:
        if stocks is not None and "Micro_Tier" in stocks.columns:
            _mt = stocks[stocks["Micro_Tier"].astype(str) != ""]
            for _th, _g in _mt.groupby("Mapped_Theme"):
                _rs_vals = pd.to_numeric(_g["Micro_ETF_RS"], errors="coerce").dropna()
                micro_tier_by_theme[str(_th)] = (
                    str(_g["Micro_Tier"].iloc[0]),
                    str(_g["Micro_ETF"].iloc[0]),
                    float(_rs_vals.iloc[0]) if not _rs_vals.empty else None,
                )
    except Exception:
        micro_tier_by_theme = {}

    def should_display(row):
        # Require at least one active stock candidate to display
        leaders_val = row.get("Leaders")
        if pd.isna(leaders_val) or str(leaders_val).strip() in ("", "None", "nan"):
            return False
            
        return True
        
    display_df = display_df[display_df.apply(should_display, axis=1)].copy()

    # Sort from Most Bullish at the top to Most Bearish at the bottom:
    # 1. Macro Rank ascending (Rank 1 Most Bullish -> Rank 42 Most Bearish)
    # 2. For same macro rank:
    #    - Leading: highest Weighted_Breadth_Score first
    #    - Lagging: highest Weighted_Breadth_Score (most active breakdown) at bottom
    def _get_theme_macro_rank(mapped_theme):
        # Micro Leader / Micro Lagging themes sit right at the boundary of the
        # Leading / Lagging blocks so they are visible without distorting macro order.
        if mapped_theme in micro_tier_by_theme:
            tier = micro_tier_by_theme[mapped_theme][0]
            if not theme_strength.empty and "Theme" in theme_strength.columns:
                lead_ranks = [float(r) for t, r in zip(theme_strength["Theme"], theme_strength["Theme_Rank"]) if theme_class_map.get(t) == "Leading"]
                lag_ranks = [float(r) for t, r in zip(theme_strength["Theme"], theme_strength["Theme_Rank"]) if theme_class_map.get(t) == "Lagging"]
                if tier == "Micro Leader":
                    return (max(lead_ranks) + 0.5) if lead_ranks else 1.0
                return (min(lag_ranks) - 0.5) if lag_ranks else 40.0
        p_theme = THEME_TRANSLATION.get(str(mapped_theme), str(mapped_theme))
        if not theme_strength.empty and "Theme" in theme_strength.columns:
            m_row = theme_strength[theme_strength["Theme"] == p_theme]
            if not m_row.empty:
                return float(m_row.iloc[0].get("Theme_Rank", 25.0))
        # Fallback for Unknown / unclassified: place right after Leading (rank 13.5)
        cls = theme_class_map.get(p_theme, "Unknown")
        if cls == "Leading": return 1.0
        if cls == "Lagging": return 40.0
        return 20.0

    display_df["_macro_rank"] = display_df["Mapped_Theme"].apply(_get_theme_macro_rank)
    display_df["_score_num"] = pd.to_numeric(display_df["Weighted_Breadth_Score"], errors="coerce").fillna(0.0)
    display_df["_tot_stocks"] = pd.to_numeric(display_df["Total_Stocks"], errors="coerce").fillna(0)
    
    # Sort: Macro Rank ascending (1 -> 42), then Weighted Breadth Score descending
    display_df = display_df.sort_values(
        ["_macro_rank", "_score_num", "_tot_stocks"],
        ascending=[True, False, False]
    ).drop(columns=["_macro_rank", "_score_num", "_tot_stocks"])

    print(f"{'Macro Theme'.ljust(18)} {'Micro Theme'.ljust(26)} {'Tot'.rjust(3)} {'Qual'.rjust(4)} {'W_Brdth'.rjust(7)} {'ETF_RS'.rjust(6)}   {'Macro State & Movement'.ljust(25)}   {'ETFs'.ljust(20)}   {'Stocks'}")
    print("-" * 145)
    
    for _, row in display_df.iterrows():
        mapped_theme = str(row['Mapped_Theme'])
        parent_theme = THEME_TRANSLATION.get(mapped_theme, mapped_theme)
        
        # Format columns
        macro = (parent_theme[:16] + "..") if len(parent_theme) > 18 else parent_theme.ljust(18)
        micro = (mapped_theme[:24] + "..") if len(mapped_theme) > 26 else mapped_theme.ljust(26)
        
        total = int(row['Total_Stocks']) if pd.notna(row['Total_Stocks']) else 0
        qual = int(row['Strong_Stocks']) if pd.notna(row['Strong_Stocks']) else 0
        score = float(row['Weighted_Breadth_Score']) if pd.notna(row['Weighted_Breadth_Score']) else 0.0
        
        tot_str = str(total).rjust(3)
        macro_state = theme_class_map.get(parent_theme, "Unknown")
        micro_info = micro_tier_by_theme.get(mapped_theme)
        masked = (macro_state == "Neutral") and not micro_info
        q_str = "-".rjust(4) if masked else str(qual).rjust(4)
        s_str = "-".rjust(7) if masked else f"{score:>.2f}".rjust(7)
        
        macro_state = theme_class_map.get(parent_theme, "Unknown")
        
        etf_rs_val = 0.0
        if not theme_strength[theme_strength["Theme"] == parent_theme].empty:
            ts_row = theme_strength[theme_strength["Theme"] == parent_theme].iloc[0]
            macro_rank = ts_row["Theme_Rank"]
            etf_rs_val = float(ts_row.get("ETF_RS_Raw", 0.0))
            
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
                            
            mac_state_str = f"{macro_state} ({macro_rank}{movement_str})".ljust(25)
        else:
            mac_state_str = macro_state.ljust(25)
            
        if micro_info:
            _tier, _metf, _mrs = micro_info
            mac_state_str = (f"{_tier} ({_metf})" if _metf else f"{_tier} (breadth)").ljust(25)
            if _mrs is not None:
                etf_rs_val = _mrs

        r_str = f"{etf_rs_val:>.2f}".rjust(6)

        etfs_val = THEME_ETF_MAPPING.get(mapped_theme) or THEME_ETF_MAPPING.get(parent_theme, "")
        etfs_col = (etfs_val[:18] + "..") if len(etfs_val) > 20 else etfs_val.ljust(20)

        prefix = f"{macro} {micro} {tot_str} {q_str} {s_str} {r_str}   {mac_state_str}   {etfs_col}   "

        prefix_len = len(prefix)
        
        leaders_str = str(row['Leaders']).strip()
        
        if not leaders_str:
            print(prefix)
            continue
            
        wrapped = textwrap.wrap(
            leaders_str, 
            width=max(35, 145 - prefix_len),
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

    strong_bullish_out = "========================================\nSTRONG BULLISH (Trend Continuation)\nLegend: ~ = Unknown/Unclassified\n========================================\n"

    long_candidates_df = long_candidates.copy()
    if '52 Week High' in long_candidates_df.columns and 'Last Close' in long_candidates_df.columns:
        clean_close_l = pd.to_numeric(long_candidates_df['Last Close'].astype(str).str.replace(r'[%$,]', '', regex=True), errors='coerce')
        clean_hi_l = pd.to_numeric(long_candidates_df['52 Week High'].astype(str).str.replace(r'[%$,]', '', regex=True), errors='coerce')
        long_candidates_df['% off Hi'] = ((clean_close_l - clean_hi_l) / clean_hi_l * 100).apply(
            lambda v: "0.0%" if pd.notna(v) and abs(round(v, 1)) == 0 else (f"{v:.1f}%" if pd.notna(v) else "NA")
        )
    else:
        long_candidates_df['% off Hi'] = "NA"
    long_candidates_df['Zacks'] = pd.to_numeric(long_candidates_df['Zacks Rank'], errors='coerce').fillna(0).astype(int).astype(str)

    display_df = long_candidates_df[
        [
            "Ticker",
            "Mapped_Theme",
            "Theme_Class",
            "Zacks",
            "RS_Rating",
            "% off Hi",
            "Sector (SPDR)",
            "Sector Rank"
        ]
    ].copy()
    display_df["Ticker"] = display_df["Ticker"].astype(str).str.replace("*", "", regex=False)
    
    # Prepend tag directly to the Ticker string for clean left-side reading
    display_df.loc[display_df["Theme_Class"].isin(["Unknown", "Unclassified Leader"]), "Ticker"] = "~" + display_df["Ticker"]
    if "Is_Elite_Exception" in long_candidates_df.columns:
        is_elite = long_candidates_df["Is_Elite_Exception"].reindex(display_df.index).fillna(False)
        display_df.loc[is_elite, "Ticker"] = "^" + display_df.loc[is_elite, "Ticker"]

    if "Is_Theme_Exempt" in long_candidates_df.columns:
        is_exempt = long_candidates_df["Is_Theme_Exempt"].reindex(display_df.index).fillna(False)
        display_df.loc[is_exempt, "Ticker"] = "*" + display_df.loc[is_exempt, "Ticker"]

    if "Micro_Tier" in long_candidates_df.columns:
        display_df["Micro_Tier"] = long_candidates_df["Micro_Tier"].reindex(display_df.index).fillna("")
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
        true_longs["Sector (Rk)"] = true_longs["Sector (SPDR)"].astype(str) + " (" + true_longs["Sector Rank"].astype(str) + ")"
        true_longs["Ticker"] = true_longs["Ticker"].apply(lambda t: f" {str(t).strip()}")
        true_longs = true_longs.drop(columns=["Sector (SPDR)", "Sector Rank"])

    if not distribution_watchlist.empty:
        dist_df = distribution_watchlist.copy()
        if '52 Week Low' in dist_df.columns and 'Last Close' in dist_df.columns:
            clean_close_s = pd.to_numeric(dist_df['Last Close'].astype(str).str.replace(r'[%$,]', '', regex=True), errors='coerce')
            clean_lo_s = pd.to_numeric(dist_df['52 Week Low'].astype(str).str.replace(r'[%$,]', '', regex=True), errors='coerce')
            dist_df['% off Lo'] = ((clean_close_s - clean_lo_s) / clean_lo_s * 100).apply(
                lambda v: "0.0%" if pd.notna(v) and abs(round(v, 1)) == 0 else (f"+{v:.1f}%" if pd.notna(v) and v > 0 else (f"{v:.1f}%" if pd.notna(v) else "NA"))
            )
        else:
            dist_df['% off Lo'] = "NA"
        dist_df['Zacks'] = pd.to_numeric(dist_df['Zacks Rank'], errors='coerce').fillna(0).astype(int).astype(str)

        display_df = dist_df[
            [
                "Ticker",
                "Mapped_Theme",
                "Theme_Class",
                "Zacks",
                "Short_RS_Rating",
                "% off Lo",
                "Sector (SPDR)",
                "Sector Rank"
            ]
        ].copy()
        display_df["Ticker"] = display_df["Ticker"].astype(str).str.replace("*", "", regex=False)

        display_df["Movement"] = display_df["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper().map(movements).fillna("NA")
        display_df["Days"] = display_df["Ticker"].astype(str).str.replace("*", "", regex=False).str.upper().map(days).fillna(1).astype(int)
        display_df["Sector (Rk)"] = display_df["Sector (SPDR)"].astype(str) + " (" + display_df["Sector Rank"].astype(str) + ")"
        display_df["Ticker"] = display_df["Ticker"].apply(lambda t: f" {str(t).strip()}")
        display_df = display_df.drop(columns=["Sector (SPDR)", "Sector Rank"])
        if "Micro_Tier" in dist_df.columns:
            display_df["Micro_Tier"] = dist_df["Micro_Tier"].reindex(display_df.index).fillna("")

    def clean_all_tickers(df):
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
    full_short_list = clean_all_tickers(distribution_watchlist)

    # --- COMBINED BULLISH & BEARISH UNIVERSE (INLINE COLUMN ALIGNMENT) ---
    bullish_list = []
    if not true_longs.empty:
        bullish_df = true_longs.copy()
        cols = ['Ticker', 'Mapped_Theme', 'Zacks', 'RS_Rating', '% off Hi', 'Movement', 'Days', 'Sector (Rk)', 'Micro_Tier']
        cols = [c for c in cols if c in bullish_df.columns]
        bullish_df = bullish_df[cols]
        bullish_df['_score_num'] = pd.to_numeric(bullish_df['RS_Rating'], errors='coerce').fillna(0)
        bullish_df = bullish_df.sort_values(['_score_num'], ascending=[False]).drop(columns=['_score_num'])
        bullish_list = bullish_df.to_dict('records')

    bearish_list = []
    if not distribution_watchlist.empty and not display_df.empty:
        bearish_df = display_df.copy()
        cols = ['Ticker', 'Mapped_Theme', 'Zacks', 'Short_RS_Rating', '% off Lo', 'Movement', 'Days', 'Sector (Rk)', 'Micro_Tier']
        cols = [c for c in cols if c in bearish_df.columns]
        bearish_df = bearish_df[cols]
        bullish_short_rs = 'Short_RS_Rating' if 'Short_RS_Rating' in bearish_df.columns else 'RS_Rating'
        bearish_df['_score_num'] = pd.to_numeric(bearish_df[bullish_short_rs], errors='coerce').fillna(999)
        bearish_df = bearish_df.sort_values(['_score_num'], ascending=[True]).drop(columns=['_score_num'])
        bearish_list = bearish_df.to_dict('records')

    def _micro_tag(theme_name, tier):
        tier = str(tier or "")
        if tier == "Micro Leader":
            return str(theme_name)[:21] + " [ML]"
        if tier == "Micro Lagging":
            return str(theme_name)[:20] + " [MLg]"
        return str(theme_name)[:26]

    def format_bullish_row(r):
        t = str(r.get("Ticker", "")).strip()[:6]
        theme = _micro_tag(r.get("Mapped_Theme", ""), r.get("Micro_Tier"))
        zk = str(r.get("Zacks", ""))[:2]
        rs = str(r.get("RS_Rating", ""))[:4]
        hi = str(r.get("% off Hi", ""))[:8]
        mov = str(r.get("Movement", ""))[:4]
        dys = str(r.get("Days", ""))[:4]
        sec = str(r.get("Sector (Rk)", ""))[:11]
        return f"{t:<7} {theme:<26} {zk:>5} {rs:>10} {hi:>9} {mov:>9} {dys:>5}  {sec:<11}"

    def format_bearish_row(r):
        t = str(r.get("Ticker", "")).strip()[:6]
        theme = _micro_tag(r.get("Mapped_Theme", ""), r.get("Micro_Tier"))
        zk = str(r.get("Zacks", ""))[:2]
        shrs = str(r.get("Short_RS_Rating", r.get("RS_Rating", "")))[:4]
        lo = str(r.get("% off Lo", ""))[:8]
        mov = str(r.get("Movement", ""))[:4]
        dys = str(r.get("Days", ""))[:4]
        sec = str(r.get("Sector (Rk)", ""))[:11]
        return f"{t:<7} {theme:<26} {zk:>5} {shrs:>10} {lo:>9} {mov:>9} {dys:>5}  {sec:<11}"

    b_hdr = f"{'Ticker':<7} {'Mapped_Theme':<26} {'Zacks':>5} {'RS_Rating':>10} {'% off Hi':>9} {'Movement':>9} {'Days':>5}  {'Sector (Rk)':<11}"
    s_hdr = f"{'Ticker':<7} {'Mapped_Theme':<26} {'Zacks':>5} {'Short_RS':>10} {'% off Lo':>9} {'Movement':>9} {'Days':>5}  {'Sector (Rk)':<11}"

    # Extract all active strong bullish & bearish tickers
    all_bullish_tickers = []
    for t in true_long_tickers:
        clean = str(t).replace('*', '').replace('~', '').replace('^', '').strip().upper()
        if clean and clean not in all_bullish_tickers:
            all_bullish_tickers.append(clean)

    all_bearish_tickers = []
    if not distribution_watchlist.empty:
        for t in distribution_watchlist['Ticker'].tolist():
            clean = str(t).replace('*', '').replace('~', '').replace('^', '').strip().upper()
            if clean and clean not in all_bearish_tickers:
                all_bearish_tickers.append(clean)

    # Fetch Mild Bullish (Reversal Longs) & Mild Bearish (Reversal Shorts)
    active_bullish_set = set(all_bullish_tickers)
    active_bearish_set = set(all_bearish_tickers)

    df_reversal_long = pd.DataFrame()
    try:
        from runners.run_reversal_scan import get_reversal_long_candidates
        df_reversal_long = get_reversal_long_candidates(
            context.market_date, stocks, active_bullish_set
        )
    except Exception:
        pass

    # 1. STRONG BULLISH UNIVERSE
    strong_bullish_out = '=============================================================================================\n'
    strong_bullish_out += '1. STRONG BULLISH UNIVERSE (Active Momentum Breakouts & Leaders)\n'
    strong_bullish_out += 'Criteria: RS >= 90 | 52W Range >= 85% | Zacks 1-2 | Leading Themes Only\n'
    strong_bullish_out += 'Legend: ~ = Unknown/Unclassified | [ML] = Micro Leader | ^ = Elite Momentum Carve-Out (RS >= 95, Zacks 3 with Growth A/B) | * = Independent Leader (RS >= 95 Theme Exemption)\n'
    strong_bullish_out += '=============================================================================================\n'

    if bullish_list:
        b_lines = [b_hdr]
        for r in bullish_list:
            b_lines.append(format_bullish_row(r))
        strong_bullish_out += '\n'.join(b_lines) + '\n'
    else:
        strong_bullish_out += 'No active strong bullish candidates today.\n'

    # 2. MILD BULLISH UNIVERSE
    mild_bullish_out = '=============================================================================================\n'
    mild_bullish_out += '2. MILD BULLISH UNIVERSE (Institutional Pullbacks & Reversals)\n'
    mild_bullish_out += 'Criteria: Leading or [ML] | Zacks 1-2 (Z3 if RS >= 95 & Growth A/B/C) | Range >= 40% | RS >= 50\n'
    mild_bullish_out += '=============================================================================================\n'

    reversal_longs = []
    if not df_reversal_long.empty:
        hdr_rev_l = f"{'Ticker':<7} {'Theme / Sector':<26} {'Zacks':>5} {'RS':>10} {'% off Hi':>9} {'YTD':>9}  {'52W Range':<11}"
        m_lines = [hdr_rev_l]
        for _, r in df_reversal_long.iterrows():
            t = str(r["Ticker"]).strip()
            reversal_longs.append(t)
            th = str(r["Theme"])[:26]
            zk = str(r["Zacks"])
            rs_s = str(r["RS"])
            hi_s = "0.0%" if pd.notna(r["pct_off_hi"]) and abs(round(r["pct_off_hi"], 1)) == 0 else (f"{r['pct_off_hi']:.1f}%" if pd.notna(r["pct_off_hi"]) else "NA")
            ytd_s = f"+{r['YTD']:.1f}%" if pd.notna(r["YTD"]) and r["YTD"] > 0 else (f"{r['YTD']:.1f}%" if pd.notna(r["YTD"]) else "NA")
            rg_s = f"{r['Range']:.1f}%" if pd.notna(r["Range"]) else "NA"
            m_lines.append(f"{t:<7} {th:<26} {zk:>5} {rs_s:>10} {hi_s:>9} {ytd_s:>9}  {rg_s:<11}")
        mild_bullish_out += '\n'.join(m_lines) + '\n'
    else:
        mild_bullish_out += 'No active mild bullish candidates today.\n'

    # 3. SHORT UNIVERSE (Stage 4 Candidates)
    short_out = '=============================================================================================\n'
    short_out += '3. SHORT UNIVERSE (Stage 4 Breakdown & Short Candidates)\n'
    short_out += 'Criteria: Short_RS 8-60 | 52W Range <= 30% | Zacks 3-5 | Non-Leading Themes (Blocks Leading)\n'
    short_out += 'Legend: [MLg] = Micro Lagging\n'
    short_out += '=============================================================================================\n'

    if bearish_list:
        s_lines = [s_hdr]
        for r in bearish_list:
            s_lines.append(format_bearish_row(r))
        short_out += '\n'.join(s_lines) + '\n'
    else:
        short_out += 'No active short candidates today.\n'

    print('\n' + strong_bullish_out)
    print('\n' + mild_bullish_out)
    print('\n' + short_out)

    print('TRADINGVIEW WATCHLIST EXPORT')
    strong_bullish_str = ','.join(all_bullish_tickers)
    mild_bullish_str = ','.join(reversal_longs)
    short_str = ','.join(all_bearish_tickers)

    print('###Strong_Bullish,' + strong_bullish_str + ',') if strong_bullish_str else print('###Strong_Bullish,')
    print('###Mild_Bullish,' + mild_bullish_str + ',') if mild_bullish_str else print('###Mild_Bullish,')
    print('###Short,' + short_str + ',') if short_str else print('###Short,')

    # Thematic & Sector ETF Watchlists (Primary Pure-Play per theme)
    def extract_primary_etf(etf_raw):
        if not etf_raw or pd.isna(etf_raw):
            return None
        cleaned = re.sub(r'\[.*?\]', '', str(etf_raw)).strip()
        if not cleaned:
            return None
        tokens = [t.strip() for t in cleaned.split(',') if t.strip()]
        if tokens:
            ticker = tokens[0].split()[0].replace('/', '').strip().upper()
            if ticker and ticker.isalpha():
                return ticker
        return None

    leading_etfs = []
    for _, row in display_df.iterrows():
        micro_theme = str(row['Mapped_Theme'])
        macro_theme = THEME_TRANSLATION.get(micro_theme, micro_theme)
        if theme_class_map.get(macro_theme) == "Leading":
            etf_raw = THEME_ETF_MAPPING.get(micro_theme) or THEME_ETF_MAPPING.get(macro_theme)
            etf = extract_primary_etf(etf_raw)
            if etf and etf not in leading_etfs:
                leading_etfs.append(etf)
    for row in leading_themes:
        theme = row.get("Theme")
        if theme:
            etf_raw = THEME_ETF_MAPPING.get(theme)
            etf = extract_primary_etf(etf_raw)
            if etf and etf not in leading_etfs:
                leading_etfs.append(etf)

    lagging_etfs = []
    for _, row in display_df.iterrows():
        micro_theme = str(row['Mapped_Theme'])
        macro_theme = THEME_TRANSLATION.get(micro_theme, micro_theme)
        if theme_class_map.get(macro_theme) == "Lagging":
            etf_raw = THEME_ETF_MAPPING.get(micro_theme) or THEME_ETF_MAPPING.get(macro_theme)
            etf = extract_primary_etf(etf_raw)
            if etf and etf not in lagging_etfs:
                lagging_etfs.append(etf)
    for row in lagging_themes:
        theme = row.get("Theme")
        if theme:
            etf_raw = THEME_ETF_MAPPING.get(theme)
            etf = extract_primary_etf(etf_raw)
            if etf and etf not in lagging_etfs:
                lagging_etfs.append(etf)

    # Micro Leader / Micro Lagging sub-ETFs (e.g. CIBR) join the ETF export lists
    for _th, (_tier, _metf, _mrs) in micro_tier_by_theme.items():
        if _metf:
            if _tier == "Micro Leader" and _metf not in leading_etfs:
                leading_etfs.append(_metf)
            elif _tier == "Micro Lagging" and _metf not in lagging_etfs:
                lagging_etfs.append(_metf)

    leading_etf_str = ",".join(leading_etfs)
    lagging_etf_str = ",".join(lagging_etfs)

    print("###Leading_ETF," + leading_etf_str + ",") if leading_etf_str else print("###Leading_ETF,")
    print("###Lagging_ETF," + lagging_etf_str + ",") if lagging_etf_str else print("###Lagging_ETF,")

    # =========================================================================
    # DROPPED WATCHLIST EXPORT (Today's Exits)
    # =========================================================================

    dropped_bullish = sorted([t for t in deltas.get("dropped_longs", []) if t not in active_bullish_set])
    dropped_bearish = sorted([t for t in deltas.get("left_distribution", []) if t not in active_bearish_set])

    prev_leading_etfs = []
    prev_lagging_etfs = []
    try:
        report_dir = Path("market_data") / "daily_reports"
        current_date_str = str(context.market_date)
        reports = sorted([f for f in report_dir.rglob("*.txt") if f.stem < current_date_str])
        if reports:
            for line in reports[-1].read_text(encoding="utf-8").splitlines():
                if line.startswith("###Leading_ETF,"):
                    prev_leading_etfs = [x.strip() for x in line.replace("###Leading_ETF,", "").split(",") if x.strip()]
                elif line.startswith("###Lagging_ETF,"):
                    prev_lagging_etfs = [x.strip() for x in line.replace("###Lagging_ETF,", "").split(",") if x.strip()]
    except Exception:
        pass

    dropped_leading_etfs = [e for e in prev_leading_etfs if e not in leading_etfs]
    dropped_lagging_etfs = [e for e in prev_lagging_etfs if e not in lagging_etfs]

    d_bull_str = ",".join(dropped_bullish)
    d_bear_str = ",".join(dropped_bearish)
    d_lead_etf_str = ",".join(dropped_leading_etfs)
    d_lag_etf_str = ",".join(dropped_lagging_etfs)

    print("==============================================")
    print("DROPPED WATCHLIST EXPORT")
    print("==============================================")
    print("###Dropped_Bullish_Stocks," + d_bull_str + ",") if d_bull_str else print("###Dropped_Bullish_Stocks,")
    print("###Dropped_Bearish_Stocks," + d_bear_str + ",") if d_bear_str else print("###Dropped_Bearish_Stocks,")
    print("###Dropped_Leading_ETF," + d_lead_etf_str + ",") if d_lead_etf_str else print("###Dropped_Leading_ETF,")
    print("###Dropped_Lagging_ETF," + d_lag_etf_str + ",") if d_lag_etf_str else print("###Dropped_Lagging_ETF,")
    print()

    # --- SAVE OUTPUT FILE TO market_data/dropped_list/ ---
    try:
        dropped_dir = Path("market_data") / "dropped_list"
        dropped_dir.mkdir(parents=True, exist_ok=True)

        # Clean up legacy txt and json files
        for old_f in ["dropped_list.json", "dropped_list.txt", "dropped list.txt"]:
            old_p = dropped_dir / old_f
            if old_p.exists():
                try: old_p.unlink()
                except Exception: pass

        csv_path = dropped_dir / "dropped_history.csv"
        market_date_val = str(context.market_date)

        etf_theme_map = {}
        for m_theme, e_str in THEME_ETF_MAPPING.items():
            if pd.notna(e_str):
                for tok in str(e_str).split(","):
                    c_tok = tok.strip().upper()
                    if c_tok and c_tok not in etf_theme_map:
                        etf_theme_map[c_tok] = m_theme

        stock_lookup = {}
        if stocks is not None and not stocks.empty:
            for _, s_row in stocks.iterrows():
                tkr = str(s_row.get("Ticker", "")).replace("*", "").replace("~", "").strip().upper()
                if tkr: stock_lookup[tkr] = s_row

        new_records = []
        # Only true drops from Strong Long are recorded as "Dropped Long" in the historical ledger
        # to ensure the re-entry qualification window only measures genuine pedigree breakdown drops.
        true_strong_drops_long = sorted([t for t in deltas.get("dropped_longs", []) if t not in active_bullish_set])
        for tkr in true_strong_drops_long:
            s_data = stock_lookup.get(tkr)
            if s_data is not None:
                z_val = pd.to_numeric(s_data.get("Zacks Rank"), errors="coerce")
                z_str = str(int(z_val)) if pd.notna(z_val) else "-"
                rs_val = pd.to_numeric(s_data.get("RS_Rating"), errors="coerce")
                rs_str = str(int(rs_val)) if pd.notna(rs_val) else "-"
                s_rs = pd.to_numeric(s_data.get("Short_RS_Rating"), errors="coerce")
                s_rs_str = str(int(s_rs)) if pd.notna(s_rs) else "-"
                close_v = pd.to_numeric(s_data.get("Last Close"), errors="coerce")
                close_str = f"{float(close_v):.2f}" if pd.notna(close_v) else "-"
                vol_v = pd.to_numeric(s_data.get("Avg Volume"), errors="coerce")
                vol_str = str(int(vol_v)) if pd.notna(vol_v) else "-"
                theme_val = str(s_data.get("Mapped_Theme", "-"))
            else:
                z_str = rs_str = s_rs_str = close_str = vol_str = theme_val = "-"
            new_records.append({
                "Date": market_date_val, "Type": "Dropped Long", "Ticker": tkr, "Theme": theme_val,
                "Zacks_Rank": z_str, "RS_Rating": rs_str,
                "Short_RS_Rating": s_rs_str, "Last_Close": close_str, "Volume": vol_str
            })

        # Only true drops from Strong Short are recorded as "Dropped Short" in the historical ledger
        true_strong_drops_short = sorted([t for t in deltas.get("left_distribution", []) if t not in active_bearish_set])
        for tkr in true_strong_drops_short:
            s_data = stock_lookup.get(tkr)
            if s_data is not None:
                z_val = pd.to_numeric(s_data.get("Zacks Rank"), errors="coerce")
                z_str = str(int(z_val)) if pd.notna(z_val) else "-"
                rs_val = pd.to_numeric(s_data.get("RS_Rating"), errors="coerce")
                rs_str = str(int(rs_val)) if pd.notna(rs_val) else "-"
                s_rs = pd.to_numeric(s_data.get("Short_RS_Rating"), errors="coerce")
                s_rs_str = str(int(s_rs)) if pd.notna(s_rs) else "-"
                close_v = pd.to_numeric(s_data.get("Last Close"), errors="coerce")
                close_str = f"{float(close_v):.2f}" if pd.notna(close_v) else "-"
                vol_v = pd.to_numeric(s_data.get("Avg Volume"), errors="coerce")
                vol_str = str(int(vol_v)) if pd.notna(vol_v) else "-"
                theme_val = str(s_data.get("Mapped_Theme", "-"))
            else:
                z_str = rs_str = s_rs_str = close_str = vol_str = theme_val = "-"
            new_records.append({
                "Date": market_date_val, "Type": "Dropped Short", "Ticker": tkr, "Theme": theme_val,
                "Zacks_Rank": z_str, "RS_Rating": rs_str,
                "Short_RS_Rating": s_rs_str, "Last_Close": close_str, "Volume": vol_str
            })

        for etf_tkr in dropped_leading_etfs:
            new_records.append({
                "Date": market_date_val, "Type": "Dropped Leading ETF", "Ticker": etf_tkr,
                "Theme": etf_theme_map.get(etf_tkr, "-"), "Zacks_Rank": "-", "RS_Rating": "-",
                "Short_RS_Rating": "-", "Last_Close": "-", "Volume": "-"
            })

        for etf_tkr in dropped_lagging_etfs:
            new_records.append({
                "Date": market_date_val, "Type": "Dropped Lagging ETF", "Ticker": etf_tkr,
                "Theme": etf_theme_map.get(etf_tkr, "-"), "Zacks_Rank": "-", "RS_Rating": "-",
                "Short_RS_Rating": "-", "Last_Close": "-", "Volume": "-"
            })

        cols = ["Date", "Type", "Ticker", "Theme", "Zacks_Rank", "RS_Rating", "Short_RS_Rating", "Last_Close", "Volume"]
        new_df = pd.DataFrame(new_records, columns=cols)

        if csv_path.exists():
            try:
                existing_df = pd.read_csv(csv_path, dtype=str)
                existing_df = existing_df[existing_df["Date"] != market_date_val]
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            except Exception:
                combined_df = new_df
        else:
            combined_df = new_df

        combined_df.to_csv(csv_path, index=False, encoding="utf-8")
        # Legacy file exports removed
        if False:
            pass
            json_data = {
            "date": str(context.market_date),
            "dropped_bullish_stocks": dropped_bullish,
            "dropped_bearish_stocks": dropped_bearish,
            "dropped_leading_etfs": dropped_leading_etfs,
            "dropped_lagging_etfs": dropped_lagging_etfs
        }
        if False: # with open json
            json.dump(json_data, f, indent=4)

        txt_lines = [
            f"###Dropped_Bullish_Stocks,{d_bull_str}," if d_bull_str else "###Dropped_Bullish_Stocks,",
            f"###Dropped_Bearish_Stocks,{d_bear_str}," if d_bear_str else "###Dropped_Bearish_Stocks,",
            f"###Dropped_Leading_ETF,{d_lead_etf_str}," if d_lead_etf_str else "###Dropped_Leading_ETF,",
            f"###Dropped_Lagging_ETF,{d_lag_etf_str}," if d_lag_etf_str else "###Dropped_Lagging_ETF,",
        ]
        txt_content = "\n".join(txt_lines) + "\n"
        if False: pass # write dropped_list.txt
        if False: pass # write dropped list.txt
    except Exception as e:
        print(f"Error saving dropped list: {e}")
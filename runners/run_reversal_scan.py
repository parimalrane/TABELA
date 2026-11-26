import sys
from pathlib import Path
import argparse
from datetime import datetime
import json
import pandas as pd
import re

# Ensure root directory is on PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.runtime_context import context, get_monthly_path
from config.config import MILD_CONFIG


def parse_args():
    parser = argparse.ArgumentParser(description="TABELA Market Reversal & Pullback Scanner")
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Maximum days since dropped to scan (default: 90). Set 0 for all-time history."
    )
    return parser.parse_args()


def load_all_dropped_bullish(market_date: datetime.date, extra_drops: dict = None):
    """
    Extracts all dropped bullish stocks up to market_date from:
    1. market_data/dropped_list/dropped_history.csv
    2. market_data/daily_reports/*.txt
    3. extra_drops (today's freshly dropped delta)

    Anchors each stock to its EARLIEST drop date so the 90-day window
    allows temporary drops/downgrades to resurface cleanly.
    """
    drops = {}

    csv_path = Path("market_data") / "dropped_list" / "dropped_history.csv"
    if csv_path.exists():
        try:
            df = pd.read_csv(csv_path)
            if "Type" in df.columns and "Ticker" in df.columns and "Date" in df.columns:
                long_df = df[df["Type"] == "Dropped Long"].copy()
                for _, row in long_df.iterrows():
                    tkr = str(row["Ticker"]).strip().upper()
                    try:
                        d_val = pd.to_datetime(row["Date"]).date()
                    except Exception:
                        continue
                    if d_val <= market_date:
                        theme = str(row.get("Theme", "-"))
                        if tkr not in drops or d_val < drops[tkr]["date"]:
                            drops[tkr] = {"date": d_val, "theme": theme}
        except Exception:
            pass

    report_files = sorted(list(Path("market_data").glob("daily_reports/**/*.txt")))
    for r in report_files:
        try:
            r_date = pd.to_datetime(r.stem).date()
        except Exception:
            continue
        if r_date > market_date:
            continue
        try:
            content = r.read_text(encoding="utf-8")
        except Exception:
            continue
        for line in content.splitlines():
            if line.startswith("###Dropped_Bullish_Stocks,"):
                tickers = [t.strip().upper() for t in line.split(",")[1:] if t.strip()]
                for tkr in tickers:
                    if tkr not in drops or r_date < drops[tkr]["date"]:
                        drops[tkr] = {"date": r_date, "theme": "-"}

    if extra_drops:
        for tkr, info in extra_drops.items():
            tkr_clean = str(tkr).strip().upper()
            d_val = info.get("date", market_date)
            theme_val = info.get("theme", "-")
            if tkr_clean not in drops:
                drops[tkr_clean] = {"date": d_val, "theme": theme_val}

    return drops


def load_all_dropped_bearish(market_date: datetime.date, extra_drops: dict = None):
    """
    Extracts all dropped bearish stocks up to market_date from:
    1. market_data/dropped_list/dropped_history.csv
    2. market_data/daily_reports/*.txt
    3. extra_drops (today's freshly dropped delta)

    Anchors each stock to its EARLIEST drop date so the 90-day window
    allows temporary drops/relief bounces to resurface cleanly.
    """
    drops = {}

    csv_path = Path("market_data") / "dropped_list" / "dropped_history.csv"
    if csv_path.exists():
        try:
            df = pd.read_csv(csv_path)
            if "Type" in df.columns and "Ticker" in df.columns and "Date" in df.columns:
                short_df = df[df["Type"] == "Dropped Short"].copy()
                for _, row in short_df.iterrows():
                    tkr = str(row["Ticker"]).strip().upper()
                    try:
                        d_val = pd.to_datetime(row["Date"]).date()
                    except Exception:
                        continue
                    if d_val <= market_date:
                        theme = str(row.get("Theme", "-"))
                        if tkr not in drops or d_val < drops[tkr]["date"]:
                            drops[tkr] = {"date": d_val, "theme": theme}
        except Exception:
            pass

    report_files = sorted(list(Path("market_data").glob("daily_reports/**/*.txt")))
    for r in report_files:
        try:
            r_date = pd.to_datetime(r.stem).date()
        except Exception:
            continue
        if r_date > market_date:
            continue
        try:
            content = r.read_text(encoding="utf-8")
        except Exception:
            continue
        for line in content.splitlines():
            if line.startswith("###Dropped_Bearish_Stocks,"):
                tickers = [t.strip().upper() for t in line.split(",")[1:] if t.strip()]
                for tkr in tickers:
                    if tkr not in drops or r_date < drops[tkr]["date"]:
                        drops[tkr] = {"date": r_date, "theme": "-"}

    if extra_drops:
        for tkr, info in extra_drops.items():
            tkr_clean = str(tkr).strip().upper()
            d_val = info.get("date", market_date)
            theme_val = info.get("theme", "-")
            if tkr_clean not in drops:
                drops[tkr_clean] = {"date": d_val, "theme": theme_val}

    return drops


def get_active_bullish_tickers(market_date: datetime.date):
    active_bulls = set()
    report_dir = get_monthly_path(Path("market_data") / "daily_reports", market_date)
    report_file = report_dir / f"{market_date}.txt"
    if report_file.exists():
        try:
            content = report_file.read_text(encoding="utf-8")
            for line in content.splitlines():
                if line.startswith("###Bullish_Stocks,"):
                    active_bulls = set(t.strip().upper() for t in line.split(",")[1:] if t.strip())
                    break
        except Exception:
            pass
    return active_bulls


def get_active_bearish_tickers(market_date: datetime.date):
    active_bears = set()
    report_dir = get_monthly_path(Path("market_data") / "daily_reports", market_date)
    report_file = report_dir / f"{market_date}.txt"
    if report_file.exists():
        try:
            content = report_file.read_text(encoding="utf-8")
            for line in content.splitlines():
                if line.startswith("###Bearish_Stocks,"):
                    active_bears = set(t.strip().upper() for t in line.split(",")[1:] if t.strip())
                    break
        except Exception:
            pass
    return active_bears


def _load_snapshot_themes(market_date: datetime.date):
    """
    Fallback loader for leading/neutral/lagging themes when running standalone.
    """
    leading = set()
    neutral = set()
    lagging = set()

    snap_path = get_monthly_path(Path("market_data") / "snapshots", market_date) / f"{market_date}_market_snapshot.json"
    if snap_path.exists():
        try:
            data = json.loads(snap_path.read_text(encoding="utf-8"))
            for item in data.get("leading_themes", []):
                th = item.get("theme") or item.get("Theme")
                if th: leading.add(str(th).strip())
            for item in data.get("neutral_themes", []):
                th = item.get("theme") or item.get("Theme")
                if th: neutral.add(str(th).strip())
            for item in data.get("lagging_themes", []):
                th = item.get("theme") or item.get("Theme")
                if th: lagging.add(str(th).strip())
        except Exception:
            pass

    return leading, neutral, lagging


def prepare_stocks_df(stocks, market_date):
    s_copy = stocks.copy()
    s_copy["Ticker_Clean"] = s_copy["Ticker"].astype(str).str.replace("*", "", regex=False).str.replace("~", "", regex=False).str.strip().str.upper()
    s_copy["Zacks_Num"] = pd.to_numeric(s_copy["Zacks Rank"], errors="coerce")
    s_copy["YTD_Num"] = pd.to_numeric(s_copy["Relative Price Change (YTD)"].astype(str).str.replace(r"[%$,]", "", regex=True), errors="coerce")
    s_copy["Close_Num"] = pd.to_numeric(s_copy["Last Close"].astype(str).str.replace(r"[%$,]", "", regex=True), errors="coerce")
    if "Avg Volume" in s_copy.columns:
        s_copy["Vol_Num"] = pd.to_numeric(s_copy["Avg Volume"].astype(str).str.replace(r"[%$,]", "", regex=True), errors="coerce").fillna(0.0)
    else:
        s_copy["Vol_Num"] = 0.0

    if "Growth Score" in s_copy.columns:
        s_copy["Growth_Score"] = s_copy["Growth Score"].astype(str).str.strip().str.upper()
    else:
        s_copy["Growth_Score"] = ""

    # Ensure RS Rating
    if "RS_Rating" not in s_copy.columns:
        from scoring.scoring_engine import calculate_rs_raw, calculate_rs_rating
        s_copy = calculate_rs_raw(s_copy)
        s_copy = calculate_rs_rating(s_copy)
    s_copy["RS_Num"] = pd.to_numeric(s_copy["RS_Rating"], errors="coerce")

    # Ensure Short RS Rating
    if "Short_RS_Rating" not in s_copy.columns:
        from scoring.scoring_engine import calculate_short_rs_raw, calculate_short_rs_rating
        s_copy = calculate_short_rs_raw(s_copy)
        s_copy = calculate_short_rs_rating(s_copy)
    s_copy["Short_RS_Num"] = pd.to_numeric(s_copy["Short_RS_Rating"], errors="coerce")

    # Ensure Theme mapping and Theme_Class if missing
    if "Theme_Class" not in s_copy.columns:
        from themes.theme_translation_engine import THEME_TRANSLATION
        leading, neutral, lagging = _load_snapshot_themes(market_date)
        theme_classes = []
        for _, r in s_copy.iterrows():
            m_th = str(r.get("Mapped_Theme", ""))
            p_th = THEME_TRANSLATION.get(m_th, m_th)
            if p_th in leading:
                theme_classes.append("Leading")
            elif p_th in lagging:
                theme_classes.append("Lagging")
            else:
                theme_classes.append("Neutral")
        s_copy["Theme_Class"] = theme_classes

    if "Micro_Tier" not in s_copy.columns:
        s_copy["Micro_Tier"] = ""

    # High / Low percentages
    if "52 Week High" in s_copy.columns and "52 Week Low" in s_copy.columns:
        s_copy["Hi_Num"] = pd.to_numeric(s_copy["52 Week High"].astype(str).str.replace(r"[%$,]", "", regex=True), errors="coerce")
        s_copy["Lo_Num"] = pd.to_numeric(s_copy["52 Week Low"].astype(str).str.replace(r"[%$,]", "", regex=True), errors="coerce")
        s_copy["pct_off_hi"] = ((s_copy["Close_Num"] - s_copy["Hi_Num"]) / s_copy["Hi_Num"] * 100)
        s_copy["pct_off_lo"] = ((s_copy["Close_Num"] - s_copy["Lo_Num"]) / s_copy["Lo_Num"] * 100)
    else:
        s_copy["pct_off_hi"] = pd.NA
        s_copy["pct_off_lo"] = pd.NA

    range_col = "Price as a % of 52 Wk H-L Range"
    if range_col in s_copy.columns:
        s_copy["Range_Num"] = pd.to_numeric(s_copy[range_col].astype(str).str.replace(r"[%$,]", "", regex=True), errors="coerce")
    else:
        s_copy["Range_Num"] = pd.NA

    return s_copy


def get_reversal_long_candidates(market_date, stocks, active_bullish_set, max_days=90, extra_drops: dict = None):
    """
    Qualifies Long Reversals (Mild Bullish) strictly from MILD_CONFIG:
    1. Dropped Long within max_days (not in active_bulls)
    2. Theme in LONG_ALLOWED_THEMES (or Micro Leader if LONG_ALLOW_MICRO_LEADER is True)
    3. Zacks in LONG_ALLOWED_ZACKS (or Zacks 3 if RS >= LONG_ZACKS_3_MIN_RS and Growth in LONG_ZACKS_3_ALLOWED_GROWTH)
    4. Price >= LONG_MIN_PRICE and Volume >= LONG_MIN_VOLUME
    5. 52W Range >= LONG_MIN_52W_RANGE and RS >= LONG_MIN_RS
    """
    if stocks is None or stocks.empty:
        return pd.DataFrame()

    dropped_dict = load_all_dropped_bullish(market_date, extra_drops=extra_drops)
    if not dropped_dict:
        return pd.DataFrame()

    s_copy = prepare_stocks_df(stocks, market_date)
    candidates = []

    # Configurable parameters
    allowed_themes = MILD_CONFIG.get("LONG_ALLOWED_THEMES", ["Leading"])
    allow_micro = MILD_CONFIG.get("LONG_ALLOW_MICRO_LEADER", True)
    min_rs = MILD_CONFIG.get("LONG_MIN_RS", 55.0)
    min_range = MILD_CONFIG.get("LONG_MIN_52W_RANGE", 50.0)
    allowed_zacks = MILD_CONFIG.get("LONG_ALLOWED_ZACKS", [1, 2])
    z3_min_rs = MILD_CONFIG.get("LONG_ZACKS_3_MIN_RS", 95.0)
    z3_growth = MILD_CONFIG.get("LONG_ZACKS_3_ALLOWED_GROWTH", ["A", "B", "C"])
    min_price = MILD_CONFIG.get("LONG_MIN_PRICE", 10.0)
    min_vol = MILD_CONFIG.get("LONG_MIN_VOLUME", 1_000_000)

    effective_max_days = max_days if max_days > 0 else MILD_CONFIG.get("LONG_MAX_DAYS_DROPPED", 90)

    for _, row in s_copy.iterrows():
        tkr = row["Ticker_Clean"]
        if tkr in dropped_dict and tkr not in active_bullish_set:
            drop_info = dropped_dict[tkr]
            days_since = (market_date - drop_info["date"]).days
            if effective_max_days > 0 and days_since > effective_max_days:
                continue

            z_val = row["Zacks_Num"]
            rs_val = row["RS_Num"]
            range_val = row["Range_Num"]
            t_cls = row["Theme_Class"]
            m_tier = row["Micro_Tier"]
            close_val = row.get("Close_Num")
            vol_val = row.get("Vol_Num")
            growth_val = row.get("Growth_Score", "")

            # 1. Strict Theme Gate: Leading or Micro Leader only
            is_valid_theme = (t_cls in allowed_themes) or (allow_micro and m_tier == "Micro Leader")
            if not is_valid_theme:
                continue

            # 2. Zacks Rank Gate: Zacks 1-2 standard, Zacks 3 if RS >= 95 and Growth in A/B/C
            if pd.isna(z_val):
                continue
            z_int = int(z_val)
            is_std_zacks = z_int in allowed_zacks
            is_elite_z3 = (z_int == 3) and pd.notna(rs_val) and (rs_val >= z3_min_rs) and (growth_val in z3_growth)
            if not (is_std_zacks or is_elite_z3):
                continue

            # 3. Liquidity Gate
            if pd.isna(close_val) or close_val < min_price:
                continue
            if pd.isna(vol_val) or vol_val < min_vol:
                continue

            # 4. Pullback Envelope & RS Gate
            if pd.isna(range_val) or range_val < min_range:
                continue
            if pd.isna(rs_val) or rs_val < min_rs:
                continue

            theme_val = drop_info["theme"]
            if theme_val == "-" and "Mapped_Theme" in row and pd.notna(row["Mapped_Theme"]):
                theme_val = str(row["Mapped_Theme"])
            elif theme_val == "-" and "Industry" in row and pd.notna(row["Industry"]):
                theme_val = str(row["Industry"])[:24]

            candidates.append({
                "Ticker": tkr,
                "Theme": theme_val if theme_val and theme_val != "-" else str(row.get("Sector", "-")),
                "Zacks": int(z_val),
                "RS": int(round(rs_val)),
                "YTD": row["YTD_Num"],
                "pct_off_hi": row["pct_off_hi"],
                "pct_off_lo": row["pct_off_lo"],
                "Range": range_val,
                "Days_Dropped": days_since,
                "Drop_Date": str(drop_info["date"]),
            })

    if not candidates:
        return pd.DataFrame()

    df_res = pd.DataFrame(candidates)
    df_res = df_res.sort_values(by=["Days_Dropped", "RS"], ascending=[True, False])
    return df_res


def get_reversal_short_candidates(market_date, stocks, active_bearish_set, max_days=90, extra_drops: dict = None):
    """
    Qualifies Short Reversals (Mild Bearish / Sell the Bounce) strictly from MILD_CONFIG:
    1. Dropped Short within max_days (not in active_bears)
    2. Theme in SHORT_ALLOWED_THEMES (or Micro Lagging if SHORT_ALLOW_MICRO_LAGGING is True)
    3. Zacks in SHORT_ALLOWED_ZACKS (3, 4, 5)
    4. Price >= SHORT_MIN_PRICE and Volume >= SHORT_MIN_VOLUME
    5. 52W Range <= SHORT_MAX_52W_RANGE (under overhead resistance)
    6. pct_off_lo >= SHORT_MIN_PCT_OFF_LO (bounced >= 10% off low)
    7. Short_RS <= SHORT_MAX_SHORT_RS (weakness percentile <= 60%)
    """
    if stocks is None or stocks.empty:
        return pd.DataFrame()

    dropped_dict = load_all_dropped_bearish(market_date, extra_drops=extra_drops)
    if not dropped_dict:
        return pd.DataFrame()

    s_copy = prepare_stocks_df(stocks, market_date)
    candidates = []

    # Configurable parameters
    allowed_themes = MILD_CONFIG.get("SHORT_ALLOWED_THEMES", ["Lagging"])
    allow_micro = MILD_CONFIG.get("SHORT_ALLOW_MICRO_LAGGING", True)
    max_short_rs = MILD_CONFIG.get("SHORT_MAX_SHORT_RS", 60.0)
    max_range = MILD_CONFIG.get("SHORT_MAX_52W_RANGE", 50.0)
    min_bounce = MILD_CONFIG.get("SHORT_MIN_PCT_OFF_LO", 10.0)
    allowed_zacks = MILD_CONFIG.get("SHORT_ALLOWED_ZACKS", [3, 4, 5])
    min_price = MILD_CONFIG.get("SHORT_MIN_PRICE", 10.0)
    min_vol = MILD_CONFIG.get("SHORT_MIN_VOLUME", 2_000_000)

    effective_max_days = max_days if max_days > 0 else MILD_CONFIG.get("SHORT_MAX_DAYS_DROPPED", 90)

    for _, row in s_copy.iterrows():
        tkr = row["Ticker_Clean"]
        if tkr in dropped_dict and tkr not in active_bearish_set:
            drop_info = dropped_dict[tkr]
            days_since = (market_date - drop_info["date"]).days
            if effective_max_days > 0 and days_since > effective_max_days:
                continue

            z_val = row["Zacks_Num"]
            srs_val = row["Short_RS_Num"]
            range_val = row["Range_Num"]
            t_cls = row["Theme_Class"]
            m_tier = row["Micro_Tier"]
            close_val = row.get("Close_Num")
            vol_val = row.get("Vol_Num")

            # 1. Strict Theme Gate: Lagging or Micro Lagging only
            is_valid_theme = (t_cls in allowed_themes) or (allow_micro and m_tier == "Micro Lagging")
            if not is_valid_theme:
                continue

            # 2. Zacks Rank Gate
            if pd.isna(z_val) or int(z_val) not in allowed_zacks:
                continue

            # 3. Liquidity Gate
            if pd.isna(close_val) or close_val < min_price:
                continue
            if pd.isna(vol_val) or vol_val < min_vol:
                continue

            # 4. Overhead Resistance Envelope (52W Range <= max_range)
            if pd.isna(range_val) or range_val > max_range:
                continue

            # 5. Relief Bounce Floor (pct_off_lo >= min_bounce)
            lo_val = row.get("pct_off_lo")
            if pd.isna(lo_val) or lo_val < min_bounce:
                continue

            # 6. Relative Weakness Filter (Short_RS <= max_short_rs)
            if pd.isna(srs_val) or srs_val > max_short_rs:
                continue

            theme_val = drop_info["theme"]
            if theme_val == "-" and "Mapped_Theme" in row and pd.notna(row["Mapped_Theme"]):
                theme_val = str(row["Mapped_Theme"])
            elif theme_val == "-" and "Industry" in row and pd.notna(row["Industry"]):
                theme_val = str(row["Industry"])[:24]

            candidates.append({
                "Ticker": tkr,
                "Theme": theme_val if theme_val and theme_val != "-" else str(row.get("Sector", "-")),
                "Zacks": int(z_val),
                "Short_RS": int(round(srs_val)),
                "YTD": row["YTD_Num"],
                "pct_off_hi": row["pct_off_hi"],
                "pct_off_lo": row["pct_off_lo"],
                "Range": range_val,
                "Days_Dropped": days_since,
                "Drop_Date": str(drop_info["date"]),
            })

    if not candidates:
        return pd.DataFrame()

    df_res = pd.DataFrame(candidates)
    df_res = df_res.sort_values(by=["Days_Dropped", "Short_RS"], ascending=[True, False])
    return df_res


def get_reversal_long_tickers(market_date, stocks, active_bullish_set, max_days=90):
    df = get_reversal_long_candidates(market_date, stocks, active_bullish_set, max_days=max_days)
    if df.empty:
        return []
    return df["Ticker"].tolist()


def get_reversal_short_tickers(market_date, stocks, active_bearish_set, max_days=90):
    df = get_reversal_short_candidates(market_date, stocks, active_bearish_set, max_days=max_days)
    if df.empty:
        return []
    return df["Ticker"].tolist()


def run_reversal_scan():
    args = parse_args()
    market_date = context.market_date
    stocks_file = context.stocks_file

    if not stocks_file.exists():
        print(f"ERROR: Stocks file not found at {stocks_file}")
        return

    active_bulls = get_active_bullish_tickers(market_date)
    active_bears = get_active_bearish_tickers(market_date)
    stocks = pd.read_csv(stocks_file)

    df_long = get_reversal_long_candidates(market_date, stocks, active_bulls, max_days=args.days)
    df_short = get_reversal_short_candidates(market_date, stocks, active_bears, max_days=args.days)

    days_label = f"<= {args.days} Days" if args.days > 0 else "All-Time"

    output_lines = []
    output_lines.append("=============================================================================================")
    output_lines.append("                          TABELA MARKET REVERSAL SCANNER")
    output_lines.append(f"                          MARKET DATE: {market_date}")
    output_lines.append("=============================================================================================")
    output_lines.append(f"Lookback Window: {days_label} | Strict Guardrails Active (Zero Basement Noise)")
    output_lines.append("")

    # --- SECTION 1: BULLISH REVERSALS ---
    output_lines.append("=============================================================================================")
    output_lines.append("1. BULLISH REVERSALS (Institutional Pullbacks & Bottom Turns)")
    output_lines.append("   Criteria: Dropped Long | Zacks: 1, 2 | RS >= 55 | 52W Range >= 50% | Excludes Lagging Themes")
    output_lines.append(f"   Qualified Candidates: {len(df_long)}")
    output_lines.append("---------------------------------------------------------------------------------------------")

    long_tickers = []
    if df_long.empty:
        output_lines.append("No qualifying bullish reversal candidates today.")
    else:
        hdr_long = f"{'Ticker':<7}{'Theme / Sector':<24}{'Zacks':<7}{'RS':>5}{'YTD':>8}  {'% off Hi':>9}  {'% off Lo':>9}  {'52W Range':>10}  {'Days Dropped':>12}"
        output_lines.append(hdr_long)
        output_lines.append("-" * len(hdr_long))

        for _, r in df_long.iterrows():
            t = r["Ticker"]
            long_tickers.append(t)
            th = str(r["Theme"])[:22]
            zk = str(r["Zacks"])
            rs_s = str(r["RS"])
            ytd_s = f"+{r['YTD']:.1f}%" if pd.notna(r["YTD"]) and r["YTD"] > 0 else (f"{r['YTD']:.1f}%" if pd.notna(r["YTD"]) else "NA")
            hi_s = f"{r['pct_off_hi']:.1f}%" if pd.notna(r["pct_off_hi"]) else "NA"
            lo_s = f"+{r['pct_off_lo']:.1f}%" if pd.notna(r["pct_off_lo"]) else "NA"
            rg_s = f"{r['Range']:.1f}%" if pd.notna(r["Range"]) else "NA"
            dd_s = str(r["Days_Dropped"])

            output_lines.append(
                f"{t:<7}{th:<24}{zk:<7}{rs_s:>5}{ytd_s:>8}  {hi_s:>9}  {lo_s:>9}  {rg_s:>10}  {dd_s:>12}"
            )

    output_lines.append("")

    # --- SECTION 2: BEARISH REVERSALS ---
    output_lines.append("=============================================================================================")
    output_lines.append("2. BEARISH REVERSALS (Relief Bounce Exhaustions & Breakdown Resumptions)")
    output_lines.append("   Criteria: Dropped Short | Zacks: 3, 4, 5 | Short_RS >= 55 | 52W Range <= 50% | Excludes Leading Themes")
    output_lines.append(f"   Qualified Candidates: {len(df_short)}")
    output_lines.append("---------------------------------------------------------------------------------------------")

    short_tickers = []
    if df_short.empty:
        output_lines.append("No qualifying bearish reversal candidates today.")
    else:
        hdr_short = f"{'Ticker':<7}{'Theme / Sector':<24}{'Zacks':<7}{'Short_RS':>9}{'YTD':>8}  {'% off Hi':>9}  {'% off Lo':>9}  {'52W Range':>10}  {'Days Dropped':>12}"
        output_lines.append(hdr_short)
        output_lines.append("-" * len(hdr_short))

        for _, r in df_short.iterrows():
            t = r["Ticker"]
            short_tickers.append(t)
            th = str(r["Theme"])[:22]
            zk = str(r["Zacks"])
            srs_s = str(r["Short_RS"])
            ytd_s = f"+{r['YTD']:.1f}%" if pd.notna(r["YTD"]) and r["YTD"] > 0 else (f"{r['YTD']:.1f}%" if pd.notna(r["YTD"]) else "NA")
            hi_s = f"{r['pct_off_hi']:.1f}%" if pd.notna(r["pct_off_hi"]) else "NA"
            lo_s = f"+{r['pct_off_lo']:.1f}%" if pd.notna(r["pct_off_lo"]) else "NA"
            rg_s = f"{r['Range']:.1f}%" if pd.notna(r["Range"]) else "NA"
            dd_s = str(r["Days_Dropped"])

            output_lines.append(
                f"{t:<7}{th:<24}{zk:<7}{srs_s:>9}{ytd_s:>8}  {hi_s:>9}  {lo_s:>9}  {rg_s:>10}  {dd_s:>12}"
            )

    output_lines.append("")
    output_lines.append("=============================================================================================")
    output_lines.append("TRADINGVIEW WATCHLIST EXPORTS")
    output_lines.append("###Reversal_Longs," + ",".join(long_tickers) + ("," if long_tickers else ""))
    output_lines.append("###Reversal_Shorts," + ",".join(short_tickers) + ("," if short_tickers else ""))
    output_lines.append("=============================================================================================")

    full_output = "\n".join(output_lines)
    print(full_output)

    try:
        rev_dir = get_monthly_path(Path("market_data") / "reversal_reports", market_date)
        rev_file = rev_dir / f"{market_date}_reversals.txt"
        rev_file.write_text(full_output, encoding="utf-8")
    except Exception:
        pass


if __name__ == "__main__":
    run_reversal_scan()

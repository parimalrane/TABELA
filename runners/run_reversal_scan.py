import sys
from pathlib import Path
import argparse
from datetime import datetime
import pandas as pd
import re

# Ensure root directory is on PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.runtime_context import context, get_monthly_path


def parse_args():
    parser = argparse.ArgumentParser(description="TABELA Bullish Reversal & Bottom Fishing Scanner")
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Maximum days since dropped to scan (default: 90). Set 0 for all-time history."
    )
    return parser.parse_args()


def load_all_dropped_bullish(market_date: datetime.date):
    """
    Extracts all dropped bullish stocks up to market_date from:
    1. market_data/dropped_list/dropped_history.csv
    2. market_data/daily_reports/*.txt
    """
    drops = {}

    # 1. Check dropped_history.csv
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
                        if tkr not in drops or d_val > drops[tkr]["date"]:
                            drops[tkr] = {"date": d_val, "theme": theme}
        except Exception:
            pass

    # 2. Supplement from daily reports
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
                    if tkr not in drops or r_date > drops[tkr]["date"]:
                        drops[tkr] = {"date": r_date, "theme": "-"}

    return drops


def get_active_bullish_tickers(market_date: datetime.date):
    """
    Retrieves currently active Strong Bullish tickers on market_date to exclude them.
    """
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


def get_reversal_long_candidates(market_date, stocks, active_bullish_set, max_days=90):
    """
    Core calculation function shared between run_reversal_scan.py and presentation_engine.py.
    Returns DataFrame of qualifying reversal long candidates.
    """
    if stocks is None or stocks.empty:
        return pd.DataFrame()

    dropped_dict = load_all_dropped_bullish(market_date)
    if not dropped_dict:
        return pd.DataFrame()

    s_copy = stocks.copy()
    s_copy["Ticker_Clean"] = s_copy["Ticker"].astype(str).str.replace("*", "", regex=False).str.replace("~", "", regex=False).str.strip().str.upper()
    s_copy["Zacks_Num"] = pd.to_numeric(s_copy["Zacks Rank"], errors="coerce")
    s_copy["YTD_Num"] = pd.to_numeric(s_copy["Relative Price Change (YTD)"].astype(str).str.replace(r"[%$,]", "", regex=True), errors="coerce")
    s_copy["Close_Num"] = pd.to_numeric(s_copy["Last Close"].astype(str).str.replace(r"[%$,]", "", regex=True), errors="coerce")

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

    candidates = []
    for _, row in s_copy.iterrows():
        tkr = row["Ticker_Clean"]
        if tkr in dropped_dict and tkr not in active_bullish_set:
            drop_info = dropped_dict[tkr]
            days_since = (market_date - drop_info["date"]).days

            if max_days > 0 and days_since > max_days:
                continue

            z_val = row["Zacks_Num"]
            ytd_val = row["YTD_Num"]

            if pd.notna(z_val) and int(z_val) in [1, 2]:
                theme_val = drop_info["theme"]
                if theme_val == "-" and "Mapped_Theme" in row and pd.notna(row["Mapped_Theme"]):
                    theme_val = str(row["Mapped_Theme"])
                elif theme_val == "-" and "Industry" in row and pd.notna(row["Industry"]):
                    theme_val = str(row["Industry"])[:24]

                candidates.append({
                    "Ticker": tkr,
                    "Theme": theme_val if theme_val and theme_val != "-" else str(row.get("Sector", "-")),
                    "Zacks": int(z_val),
                    "YTD": ytd_val,
                    "pct_off_hi": row["pct_off_hi"],
                    "pct_off_lo": row["pct_off_lo"],
                    "Range": row["Range_Num"],
                    "Days_Dropped": days_since,
                    "Drop_Date": str(drop_info["date"]),
                })

    if not candidates:
        return pd.DataFrame()

    df_res = pd.DataFrame(candidates)
    df_res = df_res.sort_values(by=["Days_Dropped", "YTD"], ascending=[True, False])
    return df_res


def get_reversal_long_tickers(market_date, stocks, active_bullish_set, max_days=90):
    """
    Returns simple list of reversal long ticker symbols for TradingView export.
    """
    df = get_reversal_long_candidates(market_date, stocks, active_bullish_set, max_days=max_days)
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
    stocks = pd.read_csv(stocks_file)

    df_res = get_reversal_long_candidates(market_date, stocks, active_bulls, max_days=args.days)

    output_lines = []
    output_lines.append("=============================================================================================")
    output_lines.append("                          TABELA BULLISH REVERSAL SCANNER")
    output_lines.append(f"                          MARKET DATE: {market_date}")
    output_lines.append("=============================================================================================")
    days_label = f"<= {args.days} Days" if args.days > 0 else "All-Time"
    output_lines.append(f"Criteria: Dropped Bullish ({days_label}) | Zacks: 1 or 2 | Non-Active Bulls")
    output_lines.append(f"Qualified Candidates: {len(df_res)}")
    output_lines.append("---------------------------------------------------------------------------------------------")

    if df_res.empty:
        output_lines.append("No qualifying candidates found for this scan criteria.")
    else:
        header = f"{'Ticker':<7}{'Theme / Sector':<26}{'Zacks':<7}{'YTD':>8}  {'% off Hi':>10}  {'% off Lo':>10}  {'52W Range':>10}  {'Days Dropped':>12}"
        output_lines.append(header)
        output_lines.append("-" * len(header))

        tickers_for_export = []
        for _, r in df_res.iterrows():
            t = r["Ticker"]
            tickers_for_export.append(t)
            th = str(r["Theme"])[:24]
            zk = str(r["Zacks"])
            if pd.notna(r["YTD"]):
                ytd_s = f"+{r['YTD']:.1f}%" if r["YTD"] > 0 else f"{r['YTD']:.1f}%"
            else:
                ytd_s = "NA"

            hi_s = f"{r['pct_off_hi']:.1f}%" if pd.notna(r["pct_off_hi"]) else "NA"
            lo_s = f"+{r['pct_off_lo']:.1f}%" if pd.notna(r["pct_off_lo"]) else "NA"
            rg_s = f"{r['Range']:.1f}%" if pd.notna(r["Range"]) else "NA"
            dd_s = str(r["Days_Dropped"])

            output_lines.append(
                f"{t:<7}{th:<26}{zk:<7}{ytd_s:>8}  {hi_s:>10}  {lo_s:>10}  {rg_s:>10}  {dd_s:>12}"
            )

        output_lines.append("")
        output_lines.append("TRADINGVIEW WATCHLIST EXPORT")
        output_lines.append("###Reversal_Longs," + ",".join(tickers_for_export) + ",")

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

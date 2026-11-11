import os
import math
import time
import sys
from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path("c:/TABELA")
sys.path.append(str(BASE_DIR))

from themes.company_theme_engine import COMPANY_THEME
from themes.industry_theme_engine import INDUSTRY_THEME
from themes.stock_mapper import map_stock_theme
from themes.theme_parser import parse_theme
from themes.theme_translation_engine import THEME_TRANSLATION
from scoring.etf_filter import (
    filter_valid_etfs,
    filter_institutional_etfs,
    filter_etfs_with_sufficient_history,
)
from pipeline.pipeline import normalize_theme, resolve_unclassified_leaders
from config.config import (
    RS_RAW_WEIGHTS,
    LONG_WEIGHTS,
    ZACKS_SCORE_MAP,
    GROWTH_SCORE_MAP,
    SHORT_RS_RAW_WEIGHTS,
    SHORT_ZACKS_SCORE_MAP,
    SHORT_GROWTH_SCORE_MAP,
)

CSV_DIR = BASE_DIR / "market_data" / "input_files"
FWD_SWING_DAYS = 10


def load_raw_csv_data():
    stock_data = {}
    etf_data = {}
    for root, _, files in os.walk(CSV_DIR):
        for file in files:
            filepath = os.path.join(root, file)
            if file.endswith("_stocks.csv"):
                date_str = file[:8]
                date_fmt = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                df = pd.read_csv(filepath)
                df["Ticker"] = df["Ticker"].astype(str).str.strip()
                stock_data[date_fmt] = df
            elif file.endswith("_ETF.csv"):
                date_str = file[:8]
                date_fmt = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                try:
                    df = pd.read_csv(filepath, encoding="utf-16")
                    if len(df.columns) < 2:
                        df = pd.read_csv(filepath, sep="\t", encoding="utf-16")
                except Exception:
                    df = pd.read_csv(filepath, encoding="utf-8")
                    if len(df.columns) < 2:
                        df = pd.read_csv(filepath, sep="\t", encoding="utf-8")
                df["Ticker"] = df["Ticker"].astype(str).str.strip()
                etf_data[date_fmt] = df

    all_dates = sorted(stock_data.keys())
    print(f"[1/4] Loaded {len(all_dates)} trading days ({all_dates[0]} to {all_dates[-1]})", flush=True)
    return stock_data, etf_data, all_dates


def precalculate_pipeline_data(stock_data, etf_data, all_dates):
    print("[2/4] Precalculating exact pipeline ETF themes & stock base scores...", flush=True)
    etf_cols = [
        "Performance 1D (%)",
        "Performance 1W (%)",
        "Performance 1M (%)",
        "Performance 3M (%)",
        "Performance 6M (%)",
        "Performance 1Y (%)",
    ]

    # Map stock Ticker -> ETF_Theme using exact pipeline.py logic
    stock_to_etf_theme = {}
    for _, df in stock_data.items():
        for t, ind, sec in zip(
            df["Ticker"].astype(str).str.strip().str.upper(),
            df.get("Industry", pd.Series("", index=df.index)).astype(str),
            df.get("Sector", pd.Series("", index=df.index)).astype(str),
        ):
            if t not in stock_to_etf_theme:
                ind_key = ind.strip().lower()
                if t in COMPANY_THEME:
                    st_theme = COMPANY_THEME[t]
                elif ind_key in INDUSTRY_THEME:
                    st_theme = INDUSTRY_THEME[ind_key]
                else:
                    st_theme = map_stock_theme(ind, sec)
                etf_th = THEME_TRANSLATION.get(st_theme, st_theme)
                stock_to_etf_theme[t] = normalize_theme(etf_th)

    # Load unclassified overrides just like resolve_unclassified_leaders()
    override_file = BASE_DIR / "data" / "unclassified_overrides.csv"
    overrides = {}
    if override_file.exists():
        df_ov = pd.read_csv(override_file)
        for _, row in df_ov.iterrows():
            overrides[str(row["Ticker"]).strip().upper()] = str(row["Theme"]).strip()

    cleaned_etfs = {}
    spy_benchmarks = {}
    for date in all_dates:
        raw_etf = etf_data.get(date)
        if raw_etf is None or raw_etf.empty:
            continue
        df = raw_etf.copy()

        for col in etf_cols + ["Market Value (mil)"]:
            if col in df.columns:
                s = df[col].astype(str).str.replace(r"[%$,]", "", regex=True).str.strip()
                s = s.replace(r"^\((.*)\)$", r"-\1", regex=True)
                df[col] = pd.to_numeric(s, errors="coerce")
            else:
                df[col] = 0.0

        # Extract SPY benchmark returns
        spy_rows = df[df["Ticker"].str.upper() == "SPY"]
        spy_ret = {}
        for col in etf_cols:
            if not spy_rows.empty and pd.notna(spy_rows.iloc[0][col]):
                spy_ret[col] = float(spy_rows.iloc[0][col])
            else:
                spy_ret[col] = 0.0
        spy_benchmarks[date] = spy_ret

        # Exact pipeline ETF filters & theme parsing
        df = filter_valid_etfs(df)
        df = filter_institutional_etfs(df)
        df, _ = filter_etfs_with_sufficient_history(df)
        df = df[df["Ticker"].str.upper() != "SPY"].copy()

        df[["Sector", "Theme", "Subtheme"]] = df["Investment Strategy"].apply(lambda x: pd.Series(parse_theme(x)))
        df["Theme"] = df["Theme"].apply(normalize_theme)
        df = df[df["Theme"] != "Filtered"].copy()

        # Store relative returns vs SPY
        for col in etf_cols:
            df[f"Rel_{col}"] = df[col].fillna(0.0) - spy_ret[col]
        df["AUM"] = df["Market Value (mil)"].fillna(0.0).clip(lower=0.0)

        cleaned_etfs[date] = df[["Ticker", "Theme", "AUM"] + [f"Rel_{col}" for col in etf_cols]]

    prices = {}
    base_stocks = {}
    for date in all_dates:
        df = stock_data[date].copy()
        df["Ticker"] = df["Ticker"].astype(str).str.strip().str.upper()
        df = df[df["Zacks Rank"].astype(str).str.startswith(("1", "2", "3", "4", "5"))].copy()

        df["Last_Close_Num"] = pd.to_numeric(df.get("Last Close", 0.0), errors="coerce").fillna(0.0)
        prices[date] = dict(zip(df["Ticker"], df["Last_Close_Num"]))

        for col in [
            "% Price Change (1 Week)",
            "% Price Change (4 Weeks)",
            "% Price Change (12 Weeks)",
            "Relative Price Change (YTD)",
            "Price as a % of 52 Wk H-L Range",
        ]:
            if col in df.columns:
                s = df[col].astype(str).str.replace(r"[%$,]", "", regex=True).str.strip()
                s = s.replace(r"^\((.*)\)$", r"-\1", regex=True)
                df[col] = pd.to_numeric(s, errors="coerce").fillna(0.0)
            else:
                df[col] = 0.0

        # Long RS_Rating
        df["raw_rs"] = (
            df["% Price Change (4 Weeks)"] * RS_RAW_WEIGHTS["% Price Change (4 Weeks)"]
            + df["% Price Change (12 Weeks)"] * RS_RAW_WEIGHTS["% Price Change (12 Weeks)"]
            + df["% Price Change (1 Week)"] * RS_RAW_WEIGHTS["% Price Change (1 Week)"]
            + df["Relative Price Change (YTD)"] * RS_RAW_WEIGHTS["Relative Price Change (YTD)"]
            + df["Price as a % of 52 Wk H-L Range"] * RS_RAW_WEIGHTS["Price as a % of 52 Wk H-L Range"]
        )
        df = df.sort_values("raw_rs", ascending=False).reset_index(drop=True)
        pct_long = (1.0 - (df.index.to_numpy() / len(df))) * 100.0
        df["RS_Rating"] = np.clip(pct_long, 1.0, 99.0).round().astype(int)

        # Short_RS_Rating
        df["short_raw_rs"] = (
            df["% Price Change (4 Weeks)"] * SHORT_RS_RAW_WEIGHTS["% Price Change (4 Weeks)"]
            + df["% Price Change (12 Weeks)"] * SHORT_RS_RAW_WEIGHTS["% Price Change (12 Weeks)"]
            + df["% Price Change (1 Week)"] * SHORT_RS_RAW_WEIGHTS["% Price Change (1 Week)"]
            + df["Relative Price Change (YTD)"] * SHORT_RS_RAW_WEIGHTS["Relative Price Change (YTD)"]
        )
        df = df.sort_values("short_raw_rs", ascending=True).reset_index(drop=True)
        pct_short = (df.index.to_numpy() / len(df)) * 100.0
        df["Short_RS_Rating"] = np.clip(pct_short, 1.0, 99.0).round().astype(int)

        df["Zacks Rank"] = pd.to_numeric(df.get("Zacks Rank", np.nan), errors="coerce")
        df["Long_Zacks"] = df["Zacks Rank"].map(ZACKS_SCORE_MAP).fillna(50.0)
        df["Short_Zacks"] = df["Zacks Rank"].map(SHORT_ZACKS_SCORE_MAP).fillna(20.0)

        g_col = df["Growth Score"].fillna("C").astype(str).str.strip().str.upper() if "Growth Score" in df.columns else pd.Series("C", index=df.index)
        df["Long_Growth"] = g_col.map(GROWTH_SCORE_MAP).fillna(20.0)
        df["Short_Growth"] = g_col.map(SHORT_GROWTH_SCORE_MAP).fillna(50.0)

        df["Avg Volume"] = pd.to_numeric(df.get("Avg Volume", 0), errors="coerce").fillna(0.0)
        df["ETF_Theme"] = df["Ticker"].map(lambda t: stock_to_etf_theme.get(t, "Unknown"))
        df["Is_Override"] = df["Ticker"].isin(overrides)

        df["Long_Base"] = (
            df["RS_Rating"] * LONG_WEIGHTS["RS_WEIGHT"]
            + df["Long_Zacks"] * LONG_WEIGHTS["ZACKS_WEIGHT"]
            + df["Long_Growth"] * LONG_WEIGHTS["GROWTH_WEIGHT"]
        )
        df["Short_Base_50_35"] = (
            df["Short_RS_Rating"] * 0.50
            + df["Short_Zacks"] * 0.10
            + df["Short_Growth"] * 0.05
        )
        df["Short_Base_65_20"] = (
            df["Short_RS_Rating"] * 0.65
            + df["Short_Zacks"] * 0.10
            + df["Short_Growth"] * 0.05
        )

        base_stocks[date] = df[
            [
                "Ticker",
                "ETF_Theme",
                "Is_Override",
                "RS_Rating",
                "Short_RS_Rating",
                "Zacks Rank",
                "Avg Volume",
                "Last_Close_Num",
                "Long_Base",
                "Short_Base_50_35",
                "Short_Base_65_20",
            ]
        ]

    return cleaned_etfs, base_stocks, prices


def compute_metrics(rets):
    if not rets:
        return {"wr": 0.0, "avg": 0.0, "pf": 0.0, "n": 0}
    gains = [r for r in rets if r > 0]
    losses = [abs(r) for r in rets if r < 0]
    sum_g = sum(gains)
    sum_l = sum(losses)
    pf = round(sum_g / sum_l, 2) if sum_l > 0 else (99.0 if sum_g > 0 else 1.0)
    wr = round((len(gains) / len(rets)) * 100.0, 2)
    avg_ret = round(sum(rets) / len(rets), 2)
    return {"wr": wr, "avg": avg_ret, "pf": pf, "n": len(rets)}


def evaluate_exact_theme_config(cleaned_etfs, base_stocks, prices, all_dates, p_weights, agg_mode, lead_lag_pct=0.30):
    w_map = {
        "Rel_Performance 1D (%)": p_weights.get("1D", 0.0),
        "Rel_Performance 1W (%)": p_weights.get("1W", 0.0),
        "Rel_Performance 1M (%)": p_weights.get("1M", 0.0),
        "Rel_Performance 3M (%)": p_weights.get("3M", 0.0),
        "Rel_Performance 6M (%)": p_weights.get("6M", 0.0),
        "Rel_Performance 1Y (%)": p_weights.get("1Y", 0.0),
    }
    tot_w = sum(w_map.values())

    long_entries = {}
    short_50_entries = {}
    short_65_entries = {}

    total_dates = len(all_dates)

    for d_idx, date in enumerate(all_dates):
        etf_df = cleaned_etfs.get(date)
        sdf = base_stocks.get(date)
        if etf_df is None or sdf is None or etf_df.empty or sdf.empty:
            continue

        rel_score = sum(etf_df[col] * w for col, w in w_map.items()) / tot_w
        temp = pd.DataFrame({"Theme": etf_df["Theme"], "Rel_Score": rel_score, "AUM": etf_df["AUM"]})

        if agg_mode == "equal_weight":
            theme_raw = temp.groupby("Theme")["Rel_Score"].mean()
        else:  # aum_weighted
            temp["W_Score"] = temp["Rel_Score"] * temp["AUM"]
            grp = temp.groupby("Theme")[["W_Score", "AUM"]].sum()
            mean_fallback = temp.groupby("Theme")["Rel_Score"].mean()
            theme_raw = np.where(grp["AUM"] > 0, grp["W_Score"] / grp["AUM"], mean_fallback)
            theme_raw = pd.Series(theme_raw, index=grp.index)

        theme_raw = theme_raw.sort_values(ascending=False)
        mn, mx = theme_raw.min(), theme_raw.max()
        if mx > mn:
            theme_norm = ((theme_raw - mn) / (mx - mn) * 100.0).round(2)
        else:
            theme_norm = pd.Series(100.0, index=theme_raw.index)

        total_themes = len(theme_raw)
        lead_cnt = max(1, math.ceil(total_themes * lead_lag_pct))
        lag_cnt = max(1, math.ceil(total_themes * lead_lag_pct))
        lag_start = total_themes - lag_cnt + 1

        theme_class_map = {}
        theme_score_map = {}
        for idx, (th, raw_val) in enumerate(theme_raw.items(), start=1):
            if idx <= lead_cnt and raw_val > 0:
                t_cls = "Leading"
            elif idx >= lag_start:
                t_cls = "Lagging"
            else:
                t_cls = "Neutral"
            theme_class_map[th] = t_cls
            theme_score_map[th] = float(theme_norm[th])

        themes = sdf["ETF_Theme"].to_numpy()
        is_ov = sdf["Is_Override"].to_numpy()
        t_scores = np.array([80.0 if ov else theme_score_map.get(th, 0.0) for th, ov in zip(themes, is_ov)])
        t_classes = [
            "Leading" if ov else theme_class_map.get(th, "Unknown")
            for th, ov in zip(themes, is_ov)
        ]

        long_scores = sdf["Long_Base"].to_numpy() + t_scores * LONG_WEIGHTS["THEME_WEIGHT"]
        short_scores_50 = sdf["Short_Base_50_35"].to_numpy() + t_scores * 0.35
        short_scores_65 = sdf["Short_Base_65_20"].to_numpy() + t_scores * 0.20

        tickers = sdf["Ticker"].to_numpy()
        rs_long = sdf["RS_Rating"].to_numpy()
        rs_short = sdf["Short_RS_Rating"].to_numpy()
        zacks = sdf["Zacks Rank"].to_numpy()
        vols = sdf["Avg Volume"].to_numpy()
        closes = sdf["Last_Close_Num"].to_numpy()

        for t, l_sc, s50_sc, s65_sc, t_cls, t_sc, r_l, r_s, z, v, c in zip(
            tickers, long_scores, short_scores_50, short_scores_65, t_classes, t_scores, rs_long, rs_short, zacks, vols, closes
        ):
            if c < 10.0 or v < 1_000_000:
                continue

            # Production Long Gate: MIN_RS=90, MIN_LONG_SCORE=80, Leading Theme (Score >= 60), Zacks 1/2
            if r_l >= 90 and l_sc >= 80.0 and t_cls == "Leading" and t_sc >= 60.0 and z in (1, 2):
                if t not in long_entries:
                    long_entries[t] = (d_idx, c)

            # Short Gate (Approved 50/35 weights, Score <= 25, RS 8..60, Lagging Theme <= 30, Zacks not 1/2, Vol >= 5M)
            if v >= 5_000_000 and 8 <= r_s <= 60 and s50_sc <= 25.0 and t_cls == "Lagging" and t_sc <= 30.0 and z not in (1, 2):
                if t not in short_50_entries:
                    short_50_entries[t] = (d_idx, c)

            # Short Gate (Prod 65/20 weights, Score <= 30, RS 8..60, Lagging Theme <= 30, Zacks not 1/2, Vol >= 5M)
            if v >= 5_000_000 and 8 <= r_s <= 60 and s65_sc <= 30.0 and t_cls == "Lagging" and t_sc <= 30.0 and z not in (1, 2):
                if t not in short_65_entries:
                    short_65_entries[t] = (d_idx, c)

    def eval_entries(ent_dict, is_short=False):
        fwd10 = []
        for t, (idx, p0) in ent_dict.items():
            if idx + FWD_SWING_DAYS < total_dates:
                p10 = prices.get(all_dates[idx + FWD_SWING_DAYS], {}).get(t, 0.0)
                if p10 > 0:
                    ret = ((p0 - p10) / p0) * 100.0 if is_short else ((p10 - p0) / p0) * 100.0
                    fwd10.append(ret)
        m = compute_metrics(fwd10)
        m["trades"] = len(ent_dict)
        return m

    return eval_entries(long_entries, False), eval_entries(short_50_entries, True), eval_entries(short_65_entries, True)


def main():
    t0 = time.time()
    stock_data, etf_data, all_dates = load_raw_csv_data()
    cleaned_etfs, base_stocks, prices = precalculate_pipeline_data(stock_data, etf_data, all_dates)

    period_candidates = [
        {"Name": "1. Current Prod (35% 1W / 40% 1M / 25% 3M)",          "1D": 0.00, "1W": 0.35, "1M": 0.40, "3M": 0.25, "6M": 0.00, "1Y": 0.00},
        {"Name": "2. Ultra-Fast Flow (50% 1W / 35% 1M / 15% 3M)",       "1D": 0.00, "1W": 0.50, "1M": 0.35, "3M": 0.15, "6M": 0.00, "1Y": 0.00},
        {"Name": "3. Immediate Tactical (10% 1D / 40% 1W / 35% 1M / 15% 3M)", "1D": 0.10, "1W": 0.40, "1M": 0.35, "3M": 0.15, "6M": 0.00, "1Y": 0.00},
        {"Name": "4. 1M Dominant (20% 1W / 55% 1M / 25% 3M)",           "1D": 0.00, "1W": 0.20, "1M": 0.55, "3M": 0.25, "6M": 0.00, "1Y": 0.00},
        {"Name": "5. Sector Match (20% 1W / 40% 1M / 30% 3M / 10% 1Y)", "1D": 0.00, "1W": 0.20, "1M": 0.40, "3M": 0.30, "6M": 0.00, "1Y": 0.10},
        {"Name": "6. Balanced 1M/3M (20% 1W / 40% 1M / 40% 3M)",        "1D": 0.00, "1W": 0.20, "1M": 0.40, "3M": 0.40, "6M": 0.00, "1Y": 0.00},
        {"Name": "7. 3M Trend Heavy (15% 1W / 30% 1M / 55% 3M)",        "1D": 0.00, "1W": 0.15, "1M": 0.30, "3M": 0.55, "6M": 0.00, "1Y": 0.00},
        {"Name": "8. Equal 4-Period (25% 1W / 25% 1M / 25% 3M / 25% 6M)","1D": 0.00, "1W": 0.25, "1M": 0.25, "3M": 0.25, "6M": 0.25, "1Y": 0.00},
        {"Name": "9. 6M/1Y Structural (15/25/25/20/15)",                "1D": 0.00, "1W": 0.15, "1M": 0.25, "3M": 0.25, "6M": 0.20, "1Y": 0.15},
    ]

    print("\n[3/4] Evaluating THEME_STRENGTH_CONFIG['PERIOD_WEIGHTS'] & AGGREGATION_MODE across Long & Short...", flush=True)
    rows = []
    for agg_mode in ["aum_weighted", "equal_weight"]:
        for cand in period_candidates:
            l_m, s50_m, s65_m = evaluate_exact_theme_config(cleaned_etfs, base_stocks, prices, all_dates, cand, agg_mode, 0.30)
            rows.append({
                "Period_Model": cand["Name"],
                "Agg_Mode": agg_mode,
                "1D": cand["1D"], "1W": cand["1W"], "1M": cand["1M"], "3M": cand["3M"], "6M": cand["6M"], "1Y": cand["1Y"],
                "Long_WR%": l_m["wr"],
                "Long_PF": l_m["pf"],
                "Long_Avg%": l_m["avg"],
                "Long_Trd": l_m["trades"],
                "Short50_WR%": s50_m["wr"],
                "Short50_PF": s50_m["pf"],
                "Short50_Avg%": s50_m["avg"],
                "Short50_Trd": s50_m["trades"],
                "Short65_WR%": s65_m["wr"],
                "Short65_PF": s65_m["pf"],
            })

    df_out = pd.DataFrame(rows).sort_values(by=["Long_PF", "Long_WR%", "Short50_WR%"], ascending=False)
    out_csv = BASE_DIR / "backtesting" / "results" / "theme_period_weights_optimization.csv"
    df_out.to_csv(out_csv, index=False)

    print("\n=========================================================================================================")
    print("EXACT PIPELINE THEME_STRENGTH_CONFIG['PERIOD_WEIGHTS'] OPTIMIZATION RESULTS")
    print("=========================================================================================================")
    print(df_out.to_string(index=False), flush=True)
    print(f"\nSaved to: {out_csv} (Elapsed: {time.time() - t0:.2f}s)")


if __name__ == "__main__":
    main()

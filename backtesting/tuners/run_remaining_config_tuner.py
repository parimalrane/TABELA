import os
import json
import math
import time
import sys
from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path("c:/TABELA")
sys.path.append(str(BASE_DIR))

from backtesting.tuners.run_theme_period_tuner import (
    load_raw_csv_data,
    precalculate_pipeline_data,
    compute_metrics,
)
from config.config import (
    THEME_STRENGTH_CONFIG,
    LONG_WEIGHTS,
    SHORT_COMPOSITE_WEIGHTS,
    ZACKS_SCORE_MAP,
    GROWTH_SCORE_MAP,
    SHORT_ZACKS_SCORE_MAP,
    SHORT_GROWTH_SCORE_MAP,
)

FWD_SWING_DAYS = 10


def precompute_daily_themes(cleaned_etfs, all_dates, lead_pct, lag_pct):
    p_w = THEME_STRENGTH_CONFIG["PERIOD_WEIGHTS"]
    w_map = {
        "Rel_Performance 1D (%)": p_w.get("Performance 1D (%)", 0.0),
        "Rel_Performance 1W (%)": p_w.get("Performance 1W (%)", 0.0),
        "Rel_Performance 1M (%)": p_w.get("Performance 1M (%)", 0.0),
        "Rel_Performance 3M (%)": p_w.get("Performance 3M (%)", 0.0),
        "Rel_Performance 6M (%)": p_w.get("Performance 6M (%)", 0.0),
        "Rel_Performance 1Y (%)": p_w.get("Performance 1Y (%)", 0.0),
    }
    tot_w = sum(w_map.values())
    daily_theme_maps = {}

    for date in all_dates:
        etf_df = cleaned_etfs.get(date)
        if etf_df is None or etf_df.empty:
            continue
        rel_score = sum(etf_df[col] * w for col, w in w_map.items()) / tot_w
        temp = pd.DataFrame({"Theme": etf_df["Theme"], "Rel_Score": rel_score, "AUM": etf_df["AUM"]})
        temp["W_Score"] = temp["Rel_Score"] * temp["AUM"]
        grp = temp.groupby("Theme")[["W_Score", "AUM"]].sum()
        mean_fallback = temp.groupby("Theme")["Rel_Score"].mean()
        theme_raw = pd.Series(
            np.where(grp["AUM"] > 0, grp["W_Score"] / grp["AUM"], mean_fallback),
            index=grp.index,
        ).sort_values(ascending=False)

        mn, mx = theme_raw.min(), theme_raw.max()
        theme_norm = ((theme_raw - mn) / (mx - mn) * 100.0).round(2) if mx > mn else pd.Series(100.0, index=theme_raw.index)

        total_themes = len(theme_raw)
        lead_cnt = max(1, math.ceil(total_themes * lead_pct))
        lag_cnt = max(1, math.ceil(total_themes * lag_pct))
        lag_start = total_themes - lag_cnt + 1

        t_cls_map = {}
        t_sc_map = {}
        for idx, (th, raw_val) in enumerate(theme_raw.items(), start=1):
            if idx <= lead_cnt and raw_val > 0:
                t_cls_map[th] = "Leading"
            elif idx >= lag_start:
                t_cls_map[th] = "Lagging"
            else:
                t_cls_map[th] = "Neutral"
            t_sc_map[th] = float(theme_norm[th])

        daily_theme_maps[date] = (t_cls_map, t_sc_map)
    return daily_theme_maps


def eval_entries(ent_dict, all_dates, prices, is_short=False):
    total_dates = len(all_dates)
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


def run_exp1_theme_buckets(cleaned_etfs, base_stocks, prices, all_dates):
    print("\n=======================================================================================")
    print("[EXP 1/4] THEME CLASSIFICATION_PERCENTAGE_LEADING / LAGGING SWEEP")
    print("=======================================================================================")
    bucket_grid = [
        (0.15, 0.15),
        (0.20, 0.20),
        (0.25, 0.25),
        (0.30, 0.30),  # Current Prod
        (0.35, 0.35),
        (0.20, 0.30),
        (0.25, 0.30),
        (0.30, 0.20),
        (0.30, 0.25),
    ]
    rows = []
    for lead_p, lag_p in bucket_grid:
        d_themes = precompute_daily_themes(cleaned_etfs, all_dates, lead_p, lag_p)
        l_ent = {}
        s_ent = {}
        for d_idx, date in enumerate(all_dates):
            if date not in d_themes or date not in base_stocks:
                continue
            t_cls_map, t_sc_map = d_themes[date]
            sdf = base_stocks[date]
            themes = sdf["ETF_Theme"].to_numpy()
            is_ov = sdf["Is_Override"].to_numpy()
            t_scores = np.array([80.0 if ov else t_sc_map.get(th, 0.0) for th, ov in zip(themes, is_ov)])
            t_classes = ["Leading" if ov else t_cls_map.get(th, "Unknown") for th, ov in zip(themes, is_ov)]

            l_scores = sdf["Long_Base"].to_numpy() + t_scores * LONG_WEIGHTS["THEME_WEIGHT"]
            s_scores = sdf["Short_Base_50_35"].to_numpy() + t_scores * SHORT_COMPOSITE_WEIGHTS["THEME_WEIGHT"]

            for t, l_sc, s_sc, t_cls, r_l, r_s, z, v, c in zip(
                sdf["Ticker"].to_numpy(),
                l_scores,
                s_scores,
                t_classes,
                sdf["RS_Rating"].to_numpy(),
                sdf["Short_RS_Rating"].to_numpy(),
                sdf["Zacks Rank"].to_numpy(),
                sdf["Avg Volume"].to_numpy(),
                sdf["Last_Close_Num"].to_numpy(),
            ):
                if c < 10.0 or v < 1_000_000:
                    continue
                if r_l >= 90 and l_sc >= 80.0 and t_cls == "Leading" and z in (1, 2):
                    if t not in l_ent:
                        l_ent[t] = (d_idx, c)
                if v >= 5_000_000 and 8 <= r_s <= 60 and s_sc <= 25.0 and t_cls == "Lagging" and z not in (1, 2):
                    if t not in s_ent:
                        s_ent[t] = (d_idx, c)

        lm = eval_entries(l_ent, all_dates, prices, False)
        sm = eval_entries(s_ent, all_dates, prices, True)
        rows.append({
            "Lead_Pct": lead_p,
            "Lag_Pct": lag_p,
            "Long_10D_WR%": lm["wr"],
            "Long_10D_PF": lm["pf"],
            "Long_10D_Avg%": lm["avg"],
            "Long_Trades": lm["trades"],
            "Short_10D_WR%": sm["wr"],
            "Short_10D_PF": sm["pf"],
            "Short_10D_Avg%": sm["avg"],
            "Short_Trades": sm["trades"],
        })
    df_b = pd.DataFrame(rows)
    df_b.to_csv(BASE_DIR / "backtesting" / "results" / "exp1_theme_buckets.csv", index=False)
    print(df_b.to_string(index=False), flush=True)


def run_exp2_fundamental_curves(stock_data, cleaned_etfs, base_stocks, prices, all_dates):
    print("\n=======================================================================================")
    print("[EXP 2/4] LONG & SHORT FUNDAMENTAL CURVES (ZACKS_SCORE_MAP & GROWTH_SCORE_MAP)")
    print("=======================================================================================")
    d_themes = precompute_daily_themes(cleaned_etfs, all_dates, 0.30, 0.30)

    # Pre-attach Growth Grade and Theme_Score to base_stocks
    enriched = {}
    for date in all_dates:
        if date not in d_themes or date not in base_stocks:
            continue
        t_cls_map, t_sc_map = d_themes[date]
        sdf = base_stocks[date].copy()
        raw_df = stock_data[date]
        g_map_day = dict(
            zip(
                raw_df["Ticker"].astype(str).str.strip().str.upper(),
                raw_df.get("Growth Score", pd.Series("C", index=raw_df.index)).fillna("C").astype(str).str.strip().str.upper(),
            )
        )
        sdf["Growth_Grade"] = sdf["Ticker"].map(lambda t: g_map_day.get(t, "C"))
        themes = sdf["ETF_Theme"].to_numpy()
        is_ov = sdf["Is_Override"].to_numpy()
        sdf["T_Score"] = [80.0 if ov else t_sc_map.get(th, 0.0) for th, ov in zip(themes, is_ov)]
        sdf["T_Class"] = ["Leading" if ov else t_cls_map.get(th, "Unknown") for th, ov in zip(themes, is_ov)]
        enriched[date] = sdf

    long_curves = [
        ("1. Current Prod (Z1=100,Z2=100 | A=100,B=95,C=90)", {1: 100.0, 2: 100.0, 3: 0.0, 4: -50.0, 5: -100.0}, {"A": 100.0, "B": 95.0, "C": 90.0, "D": 20.0, "F": -50.0}),
        ("2. Zacks 1 Premium (Z1=100,Z2=80 | A=100,B=95,C=90)", {1: 100.0, 2: 80.0, 3: 0.0, 4: -50.0, 5: -100.0}, {"A": 100.0, "B": 95.0, "C": 90.0, "D": 20.0, "F": -50.0}),
        ("3. Tiered Growth A/B (Z1=100,Z2=100 | A=100,B=85,C=50)", {1: 100.0, 2: 100.0, 3: 0.0, 4: -50.0, 5: -100.0}, {"A": 100.0, "B": 85.0, "C": 50.0, "D": 0.0, "F": -50.0}),
        ("4. Strict Growth A/B (Z1=100,Z2=100 | A=100,B=80,C=20)", {1: 100.0, 2: 100.0, 3: 0.0, 4: -50.0, 5: -100.0}, {"A": 100.0, "B": 80.0, "C": 20.0, "D": -20.0, "F": -100.0}),
        ("5. Combined Z1 + Growth A/B (Z1=100,Z2=85 | A=100,B=85,C=50)", {1: 100.0, 2: 85.0, 3: 0.0, 4: -50.0, 5: -100.0}, {"A": 100.0, "B": 85.0, "C": 50.0, "D": 0.0, "F": -50.0}),
    ]

    l_rows = []
    for name, z_map, g_map in long_curves:
        l_ent = {}
        for d_idx, date in enumerate(all_dates):
            sdf = enriched.get(date)
            if sdf is None:
                continue
            z_pts = sdf["Zacks Rank"].map(z_map).fillna(50.0).to_numpy()
            g_pts = sdf["Growth_Grade"].map(g_map).fillna(20.0).to_numpy()
            l_sc = sdf["RS_Rating"].to_numpy() * 0.60 + sdf["T_Score"].to_numpy() * 0.20 + z_pts * 0.10 + g_pts * 0.10
            for t, sc, t_cls, t_sc, r_l, z, v, c in zip(
                sdf["Ticker"].to_numpy(), l_sc, sdf["T_Class"].to_numpy(), sdf["T_Score"].to_numpy(),
                sdf["RS_Rating"].to_numpy(), sdf["Zacks Rank"].to_numpy(), sdf["Avg Volume"].to_numpy(), sdf["Last_Close_Num"].to_numpy()
            ):
                if c >= 10.0 and v >= 1_000_000 and r_l >= 90 and sc >= 80.0 and t_cls == "Leading" and t_sc >= 60.0 and z in (1, 2):
                    if t not in l_ent:
                        l_ent[t] = (d_idx, c)
        lm = eval_entries(l_ent, all_dates, prices, False)
        l_rows.append({"Long_Curve": name, "10D_WR%": lm["wr"], "10D_PF": lm["pf"], "10D_Avg%": lm["avg"], "Trades": lm["trades"]})

    print("--- LONG FUNDAMENTAL CURVES ---")
    print(pd.DataFrame(l_rows).to_string(index=False), flush=True)

    short_curves = [
        ("1. Current Prod (Z3=20,Z4=80,Z5=100 | A=-50..F=100)", {1: -100.0, 2: -50.0, 3: 20.0, 4: 80.0, 5: 100.0}, {"A": -50.0, "B": 0.0, "C": 50.0, "D": 80.0, "F": 100.0}),
        ("2. Direction-Aligned Mild (Z3=40,Z4=10,Z5=-20 | A=80,C=30,F=-20)", {1: 100.0, 2: 80.0, 3: 40.0, 4: 10.0, 5: -20.0}, {"A": 80.0, "B": 50.0, "C": 30.0, "D": 0.0, "F": -20.0}),
        ("3. Direction-Aligned Strict (Z3=50,Z4=0,Z5=-50 | A=100,C=40,F=-50)", {1: 100.0, 2: 100.0, 3: 50.0, 4: 0.0, 5: -50.0}, {"A": 100.0, "B": 70.0, "C": 40.0, "D": 0.0, "F": -50.0}),
        ("4. Neutralized Zacks 3-5 (Z3=20,Z4=20,Z5=20 | A=50,C=20,F=0)", {1: 100.0, 2: 80.0, 3: 20.0, 4: 20.0, 5: 20.0}, {"A": 50.0, "B": 35.0, "C": 20.0, "D": 10.0, "F": 0.0}),
    ]

    s_rows = []
    for name, sz_map, sg_map in short_curves:
        for max_sc, min_vol in [(30.0, 1_000_000), (25.0, 2_000_000), (25.0, 5_000_000)]:
            s_ent = {}
            for d_idx, date in enumerate(all_dates):
                sdf = enriched.get(date)
                if sdf is None:
                    continue
                z_pts = sdf["Zacks Rank"].map(sz_map).fillna(20.0).to_numpy()
                g_pts = sdf["Growth_Grade"].map(sg_map).fillna(50.0).to_numpy()
                s_sc = sdf["Short_RS_Rating"].to_numpy() * 0.50 + sdf["T_Score"].to_numpy() * 0.35 + z_pts * 0.10 + g_pts * 0.05
                for t, sc, t_cls, t_sc, r_s, z, v, c in zip(
                    sdf["Ticker"].to_numpy(), s_sc, sdf["T_Class"].to_numpy(), sdf["T_Score"].to_numpy(),
                    sdf["Short_RS_Rating"].to_numpy(), sdf["Zacks Rank"].to_numpy(), sdf["Avg Volume"].to_numpy(), sdf["Last_Close_Num"].to_numpy()
                ):
                    if c >= 10.0 and v >= min_vol and 8 <= r_s <= 60 and sc <= max_sc and t_cls == "Lagging" and z not in (1, 2):
                        if t not in s_ent:
                            s_ent[t] = (d_idx, c)
            sm = eval_entries(s_ent, all_dates, prices, True)
            s_rows.append({
                "Short_Curve": name,
                "Max_Score": max_sc,
                "Min_Vol": min_vol,
                "10D_WR%": sm["wr"],
                "10D_PF": sm["pf"],
                "10D_Avg%": sm["avg"],
                "Trades": sm["trades"],
            })

    print("\n--- SHORT FUNDAMENTAL CURVES & SHORT_ENTRY GATES ---")
    df_s = pd.DataFrame(s_rows)
    df_s.to_csv(BASE_DIR / "backtesting" / "results" / "exp2_3_short_curves_and_gates.csv", index=False)
    print(df_s.to_string(index=False), flush=True)


def run_exp4_reentry_lookback():
    print("\n=======================================================================================")
    print("[EXP 4/4] REENTERED_LONG & REENTERED_SHORT LOOKBACK_DAYS SWEEP (14, 21, 30, 40, 50)")
    print("=======================================================================================")
    stock_universe_dir = BASE_DIR / "market_data" / "stock_universe"
    snapshot_files = sorted(list(stock_universe_dir.rglob("*_stock_history.json")))
    daily_stocks = {}
    daily_prices = {}
    for f in snapshot_files:
        date_str = f.stem[:10]
        try:
            with open(f, "r", encoding="utf-8") as _f:
                records = json.load(_f)
            s_map = {}
            p_map = {}
            for r in records:
                t = str(r.get("ticker", "")).strip().upper()
                if t:
                    s_map[t] = r
                    c = r.get("last_close")
                    if c is not None and not pd.isna(c) and float(c) > 0:
                        p_map[t] = float(c)
            daily_stocks[date_str] = s_map
            daily_prices[date_str] = p_map
        except Exception:
            pass

    dates = sorted(daily_stocks.keys())
    date_to_idx = {d: i for i, d in enumerate(dates)}

    drops_df = pd.read_csv(BASE_DIR / "market_data" / "dropped_list" / "dropped_history.csv", dtype=str)
    drops_df["_dt"] = pd.to_datetime(drops_df["Date"], errors="coerce")
    drops_df["Ticker"] = drops_df["Ticker"].astype(str).str.replace("*", "").str.replace("~", "").str.strip().str.upper()

    long_drops = {r["Ticker"]: r["Date"] for _, r in drops_df[drops_df["Type"] == "Dropped Long"].sort_values("_dt").drop_duplicates("Ticker", keep="first").iterrows()}
    short_drops = {r["Ticker"]: r["Date"] for _, r in drops_df[drops_df["Type"] == "Dropped Short"].sort_values("_dt").drop_duplicates("Ticker", keep="first").iterrows()}

    re_rows = []
    for lb_days in [14, 21, 30, 40, 50]:
        # Long Re-entry
        l_entered = set()
        l_rets_10 = []
        for cur_date in dates:
            c_idx = date_to_idx[cur_date]
            cur_s = daily_stocks[cur_date]
            for tkr, d_date in long_drops.items():
                if tkr in l_entered or d_date not in date_to_idx:
                    continue
                diff = c_idx - date_to_idx[d_date]
                if not (1 <= diff <= lb_days):
                    continue
                st = cur_s.get(tkr)
                if not st or st.get("tracking_state") == "LONG":
                    continue
                price = float(st.get("last_close") or 0)
                vol = float(st.get("avg_volume") or 0)
                rs = float(st.get("rs_rating") or 0)
                sc = float(st.get("long_score") or 0)
                th = str(st.get("theme_class") or "")
                try:
                    z = int(float(st.get("zacks_rank") or 0))
                except Exception:
                    z = 0
                if price >= 10.0 and vol >= 1_000_000 and rs >= 60.0 and sc >= 60.0 and th in ("Leading", "Neutral", "Unclassified Leader"):
                    if z in (1, 2) or (z == 3 and sc >= 70.0):
                        l_entered.add(tkr)
                        if c_idx + 10 < len(dates):
                            p10 = daily_prices[dates[c_idx + 10]].get(tkr, 0)
                            if p10 > 0:
                                l_rets_10.append((p10 - price) / price * 100.0)

        # Short Re-entry
        s_entered = set()
        s_rets_10 = []
        for cur_date in dates:
            c_idx = date_to_idx[cur_date]
            cur_s = daily_stocks[cur_date]
            for tkr, d_date in short_drops.items():
                if tkr in s_entered or d_date not in date_to_idx:
                    continue
                diff = c_idx - date_to_idx[d_date]
                if not (1 <= diff <= lb_days):
                    continue
                st = cur_s.get(tkr)
                if not st or st.get("tracking_state") == "DISTRIBUTION":
                    continue
                price = float(st.get("last_close") or 0)
                vol = float(st.get("avg_volume") or 0)
                srs = float(st.get("short_rs_rating") or 99)
                th = str(st.get("theme_class") or "")
                try:
                    z = int(float(st.get("zacks_rank") or 0))
                except Exception:
                    z = 0
                if price >= 10.0 and vol >= 1_000_000 and srs <= 50.0 and th in ("Lagging", "Neutral") and z in (3, 4, 5):
                    s_entered.add(tkr)
                    if c_idx + 10 < len(dates):
                        p10 = daily_prices[dates[c_idx + 10]].get(tkr, 0)
                        if p10 > 0:
                            s_rets_10.append((price - p10) / price * 100.0)

        lm = compute_metrics(l_rets_10)
        sm = compute_metrics(s_rets_10)
        re_rows.append({
            "LOOKBACK_DAYS": lb_days,
            "ReLong_10D_WR%": lm["wr"],
            "ReLong_10D_PF": lm["pf"],
            "ReLong_10D_Avg%": lm["avg"],
            "ReLong_Trades": len(l_entered),
            "ReShort_10D_WR%": sm["wr"],
            "ReShort_10D_PF": sm["pf"],
            "ReShort_10D_Avg%": sm["avg"],
            "ReShort_Trades": len(s_entered),
        })

    df_re = pd.DataFrame(re_rows)
    df_re.to_csv(BASE_DIR / "backtesting" / "results" / "exp4_reentry_lookback.csv", index=False)
    print(df_re.to_string(index=False), flush=True)


def main():
    t0 = time.time()
    stock_data, etf_data, all_dates = load_raw_csv_data()
    cleaned_etfs, base_stocks, prices = precalculate_pipeline_data(stock_data, etf_data, all_dates)

    run_exp1_theme_buckets(cleaned_etfs, base_stocks, prices, all_dates)
    run_exp2_fundamental_curves(stock_data, cleaned_etfs, base_stocks, prices, all_dates)
    run_exp4_reentry_lookback()
    print(f"\nAll 4 remaining parameter experiments completed in {time.time() - t0:.2f}s", flush=True)


if __name__ == "__main__":
    main()


"""
Theme Tier Optimization Tuner (In-Memory Fast Sweep)
Compares theme tier cutoff percentages: 15%, 20%, 25%, 30%
Measures Win Rate, Profit Factor, Total Trades, and Daily Watchlist Size
across 96 historical daily snapshots (July - Nov 2026).
"""

import json
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path("c:/TABELA")
sys.path.insert(0, str(BASE_DIR))

SNAPSHOT_DIR = BASE_DIR / "market_data" / "stock_universe"
RESULTS_DIR = BASE_DIR / "backtesting" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_all_snapshots():
    snapshot_files = sorted(list(SNAPSHOT_DIR.rglob("*_stock_history.json")))
    print(f"Loading {len(snapshot_files)} historical snapshots into memory...", flush=True)

    daily_stocks = {}
    daily_prices = {}

    for f in snapshot_files:
        date_str = f.stem[:10]
        try:
            with open(f, "r", encoding="utf-8") as _f:
                records = json.load(_f)
            stock_map = {}
            price_map = {}
            max_rank = 0
            for r in records:
                t = str(r.get("ticker", "")).replace("*", "").strip().upper()
                if not t:
                    continue
                stock_map[t] = r
                c = r.get("last_close")
                if c is not None and not pd.isna(c) and float(c) > 0:
                    price_map[t] = float(c)
                tr = r.get("theme_rank")
                if tr is not None and not pd.isna(tr):
                    try:
                        tr_val = float(tr)
                        if tr_val > max_rank:
                            max_rank = tr_val
                    except:
                        pass
                        
            daily_stocks[date_str] = {
                "stocks": stock_map,
                "max_rank": max_rank if max_rank > 0 else 118.0
            }
            daily_prices[date_str] = price_map
        except Exception as e:
            print(f"Error loading {f}: {e}")

    dates = sorted(daily_stocks.keys())
    print(f"Loaded {len(dates)} dates: {dates[0]} to {dates[-1]}")
    return dates, daily_stocks, daily_prices


def simulate_trade(ticker, pick_date_idx, dates, daily_prices, is_long=True,
                    pullback_pct=0.05, wait_days=21, stop_pct=0.07, target_pct=0.21, max_hold_days=50):
    pick_date = dates[pick_date_idx]
    pick_price = daily_prices[pick_date].get(ticker)
    if not pick_price or pick_price <= 0:
        return None

    entry_idx = None
    entry_price = None

    # Step 1: Wait for entry pullback / bounce
    for i in range(1, wait_days + 1):
        curr_idx = pick_date_idx + i
        if curr_idx >= len(dates):
            break
        d = dates[curr_idx]
        p = daily_prices[d].get(ticker)
        if not p or p <= 0:
            continue

        if is_long:
            if p <= pick_price * (1.0 - pullback_pct):
                entry_idx = curr_idx
                entry_price = p
                break
        else:
            if p >= pick_price * (1.0 + pullback_pct):
                entry_idx = curr_idx
                entry_price = p
                break

    if entry_idx is None:
        return None

    # Step 2: Simulate execution
    stop_price = entry_price * (1.0 - stop_pct) if is_long else entry_price * (1.0 + stop_pct)
    target_price = entry_price * (1.0 + target_pct) if is_long else entry_price * (1.0 - target_pct)

    for h in range(1, max_hold_days + 1):
        curr_idx = entry_idx + h
        if curr_idx >= len(dates):
            last_p = daily_prices[dates[-1]].get(ticker, entry_price)
            ret = (last_p / entry_price - 1.0) if is_long else (1.0 - last_p / entry_price)
            return {"win": ret > 0, "return": ret, "status": "OPEN"}

        d = dates[curr_idx]
        p = daily_prices[d].get(ticker)
        if not p or p <= 0:
            continue

        if is_long:
            if p <= stop_price:
                ret = (p / entry_price) - 1.0
                return {"win": False, "return": ret, "status": "STOP"}
            if p >= target_price:
                ret = (p / entry_price) - 1.0
                return {"win": True, "return": ret, "status": "TARGET"}
        else:
            if p >= stop_price:
                ret = 1.0 - (p / entry_price)
                return {"win": False, "return": ret, "status": "STOP"}
            if p <= target_price:
                ret = 1.0 - (p / entry_price)
                return {"win": True, "return": ret, "status": "TARGET"}

    exit_p = daily_prices[dates[entry_idx + max_hold_days]].get(ticker, entry_price)
    ret = (exit_p / entry_price - 1.0) if is_long else (1.0 - exit_p / entry_price)
    return {"win": ret > 0, "return": ret, "status": "EXPIRED"}


def run_tier_experiment(dates, daily_stocks, daily_prices, tier_pct, short_lagging_only=True):
    """
    Evaluates:
    1. Strong Bullish (Rank <= tier_pct * max_rank, RS >= 90, Range >= 85, Zacks 1-2)
    2. Mild Bullish (Rank <= tier_pct * max_rank, RS >= 70, Range >= 60, Zacks 1-2)
    3. Short (Rank >= (1-tier_pct) * max_rank if short_lagging_only else Rank > tier_pct * max_rank, Short_RS <= 60, Range <= 30, Zacks 3-5)
    """
    strong_trades = []
    mild_trades = []
    short_trades = []

    daily_strong_counts = []
    daily_mild_counts = []
    daily_short_counts = []

    last_strong_pick = {}
    last_mild_pick = {}
    last_short_pick = {}

    wait_days = 21

    for idx, d in enumerate(dates):
        data = daily_stocks[d]
        stocks = data["stocks"]
        max_rank = data["max_rank"]

        leading_cutoff = max_rank * tier_pct
        lagging_cutoff = max_rank * (1.0 - tier_pct)

        strong_today = 0
        mild_today = 0
        short_today = 0

        for ticker, row in stocks.items():
            price = float(row.get("last_close") or 0.0)
            vol = float(row.get("avg_volume") or 0.0)
            rs = float(row.get("rs_rating") or 0.0)
            short_rs = float(row.get("short_rs_rating") or 999.0)
            trank = float(row.get("theme_rank") or 999.0)
            
            try:
                zacks = int(float(row.get("zacks_rank") or 0))
            except:
                zacks = 0
                
            try:
                range_val = float(row.get("price_position_52w") or 50.0)
            except:
                range_val = 50.0

            # Independent Leader exemption
            is_independent = (rs >= 95.0) and (range_val >= 85.0) and (zacks in [1, 2])
            is_leading = (trank <= leading_cutoff) or is_independent

            # 1. STRONG BULLISH
            if price >= 10.0 and vol >= 1_000_000 and is_leading and (zacks in [1, 2]) and (rs >= 90.0) and (range_val >= 85.0):
                strong_today += 1
                if (idx - last_strong_pick.get(ticker, -999)) > wait_days:
                    last_strong_pick[ticker] = idx
                    res = simulate_trade(ticker, idx, dates, daily_prices, is_long=True, pullback_pct=0.05, wait_days=wait_days)
                    if res:
                        strong_trades.append(res)
            
            # 2. MILD BULLISH (Strict Quality: RS >= 70, Range >= 60)
            elif price >= 10.0 and vol >= 1_000_000 and is_leading and (zacks in [1, 2] or (zacks == 3 and rs >= 95.0)) and (rs >= 70.0) and (range_val >= 60.0):
                mild_today += 1
                if (idx - last_mild_pick.get(ticker, -999)) > wait_days:
                    last_mild_pick[ticker] = idx
                    res = simulate_trade(ticker, idx, dates, daily_prices, is_long=True, pullback_pct=0.08, wait_days=wait_days)
                    if res:
                        mild_trades.append(res)

            # 3. SHORT UNIVERSE
            is_short_theme = (trank >= lagging_cutoff) if short_lagging_only else (trank > leading_cutoff)
            if price >= 10.0 and vol >= 1_000_000 and is_short_theme and (zacks in [3, 4, 5]) and (short_rs <= 60.0) and (range_val <= 30.0):
                short_today += 1
                if (idx - last_short_pick.get(ticker, -999)) > wait_days:
                    last_short_pick[ticker] = idx
                    res = simulate_trade(ticker, idx, dates, daily_prices, is_long=False, pullback_pct=0.05, wait_days=wait_days)
                    if res:
                        short_trades.append(res)

        daily_strong_counts.append(strong_today)
        daily_mild_counts.append(mild_today)
        daily_short_counts.append(short_today)

    def calc_stats(trades_list):
        if not trades_list:
            return {"trades": 0, "win_rate": 0.0, "avg_return": 0.0, "profit_factor": 0.0}
        wins = [t for t in trades_list if t["win"]]
        wr = len(wins) / len(trades_list) * 100.0
        avg_ret = np.mean([t["return"] for t in trades_list]) * 100.0
        gross_gains = sum([t["return"] for t in trades_list if t["return"] > 0])
        gross_losses = abs(sum([t["return"] for t in trades_list if t["return"] < 0]))
        pf = (gross_gains / gross_losses) if gross_losses > 0 else 99.9
        return {
            "trades": len(trades_list),
            "win_rate": round(wr, 1),
            "avg_return": round(avg_ret, 2),
            "profit_factor": round(pf, 2)
        }

    return {
        "tier_pct": int(tier_pct * 100),
        "short_mode": "Lagging Only" if short_lagging_only else "All Non-Leading",
        "avg_strong_wl": round(np.mean(daily_strong_counts), 1),
        "avg_mild_wl": round(np.mean(daily_mild_counts), 1),
        "avg_short_wl": round(np.mean(daily_short_counts), 1),
        "avg_total_wl": round(np.mean(daily_strong_counts) + np.mean(daily_mild_counts) + np.mean(daily_short_counts), 1),
        "strong": calc_stats(strong_trades),
        "mild": calc_stats(mild_trades),
        "short": calc_stats(short_trades),
    }


def main():
    dates, daily_stocks, daily_prices = load_all_snapshots()
    
    tier_options = [0.15, 0.20, 0.25, 0.30]
    results = []

    print("\nRunning in-memory Cartesian sweep across theme tiers...", flush=True)

    for tier in tier_options:
        # Lagging-only shorts
        res_lag = run_tier_experiment(dates, daily_stocks, daily_prices, tier_pct=tier, short_lagging_only=True)
        results.append(res_lag)
        print(f"Completed Tier {int(tier*100)}% (Lagging Shorts): Total Daily WL = {res_lag['avg_total_wl']} charts | Strong WR = {res_lag['strong']['win_rate']}% | Short WR = {res_lag['short']['win_rate']}%")

    # Also test baseline 30% with old Non-Leading shorts
    res_base = run_tier_experiment(dates, daily_stocks, daily_prices, tier_pct=0.30, short_lagging_only=False)
    res_base["short_mode"] = "Baseline (All Non-Leading)"
    results.append(res_base)

    # Flatten for CSV export
    flat_rows = []
    for r in results:
        flat_rows.append({
            "Tier_Pct": f"{r['tier_pct']}%",
            "Short_Mode": r["short_mode"],
            "Avg_Strong_WL": r["avg_strong_wl"],
            "Avg_Mild_WL": r["avg_mild_wl"],
            "Avg_Short_WL": r["avg_short_wl"],
            "Avg_Total_WL": r["avg_total_wl"],
            "Strong_Trades": r["strong"]["trades"],
            "Strong_WR%": r["strong"]["win_rate"],
            "Strong_AvgRet%": r["strong"]["avg_return"],
            "Strong_PF": r["strong"]["profit_factor"],
            "Mild_Trades": r["mild"]["trades"],
            "Mild_WR%": r["mild"]["win_rate"],
            "Mild_AvgRet%": r["mild"]["avg_return"],
            "Mild_PF": r["mild"]["profit_factor"],
            "Short_Trades": r["short"]["trades"],
            "Short_WR%": r["short"]["win_rate"],
            "Short_AvgRet%": r["short"]["avg_return"],
            "Short_PF": r["short"]["profit_factor"],
        })

    df_res = pd.DataFrame(flat_rows)
    out_csv = RESULTS_DIR / "theme_tier_optimization_results.csv"
    df_res.to_csv(out_csv, index=False)
    print(f"\nSaved detailed results to {out_csv}")


if __name__ == "__main__":
    main()

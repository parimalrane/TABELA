import json
import os
from pathlib import Path
import pandas as pd
import numpy as np

def run_advanced_reentry_backtest():
    print("==========================================================")
    print("TABELA ADVANCED RE-ENTRY BACKTEST (ZACKS 3 & SCORE GATING)")
    print("==========================================================")
    
    # 1. Load all stock universe history
    stock_universe_dir = Path("market_data/stock_universe")
    snapshot_files = sorted(list(stock_universe_dir.rglob("*_stock_history.json")))
    print(f"Loading {len(snapshot_files)} daily snapshots into memory...")
    
    daily_stocks = {}
    daily_prices = {}
    
    for f in snapshot_files:
        date_str = f.stem[:10]
        try:
            with open(f, "r", encoding="utf-8") as _f:
                records = json.load(_f)
            stock_map = {}
            price_map = {}
            for r in records:
                t = str(r.get("ticker", "")).strip().upper()
                if t:
                    stock_map[t] = r
                    c = r.get("last_close")
                    if c is not None and not pd.isna(c) and float(c) > 0:
                        price_map[t] = float(c)
            daily_stocks[date_str] = stock_map
            daily_prices[date_str] = price_map
        except Exception as e:
            print(f"Error loading {f}: {e}")
            
    dates = sorted(daily_stocks.keys())
    date_to_idx = {d: i for i, d in enumerate(dates)}
    print(f"Dates loaded: {len(dates)} (from {dates[0]} to {dates[-1]})")
    
    # 2. Load dropped history
    dropped_csv = Path("market_data/dropped_list/dropped_history.csv")
    drops_df = pd.read_csv(dropped_csv, dtype=str)
    drops_df["_dt"] = pd.to_datetime(drops_df["Date"], errors="coerce")
    drops_df["Ticker"] = drops_df["Ticker"].astype(str).str.replace("*", "").str.replace("~", "").str.strip().str.upper()
    
    long_drops_df = drops_df[drops_df["Type"] == "Dropped Long"].sort_values("_dt").drop_duplicates(subset=["Ticker"], keep="first")
    short_drops_df = drops_df[drops_df["Type"] == "Dropped Short"].sort_values("_dt").drop_duplicates(subset=["Ticker"], keep="first")
    
    long_first_drops = {r["Ticker"]: r["Date"] for _, r in long_drops_df.iterrows()}
    short_first_drops = {r["Ticker"]: r["Date"] for _, r in short_drops_df.iterrows()}
    
    def trading_days_between(d1, d2):
        if d1 not in date_to_idx or d2 not in date_to_idx:
            return 999
        return date_to_idx[d2] - date_to_idx[d1]

    def get_forward_returns(ticker, entry_date, side="long"):
        idx = date_to_idx.get(entry_date)
        if idx is None:
            return {}
        p_entry = daily_prices[entry_date].get(ticker)
        if not p_entry or p_entry <= 0:
            return {}
            
        res = {}
        for horizon in [5, 10, 20]:
            f_idx = idx + horizon
            if f_idx < len(dates):
                f_date = dates[f_idx]
                p_future = daily_prices[f_date].get(ticker)
                if p_future and p_future > 0:
                    if side == "long":
                        ret = (p_future - p_entry) / p_entry * 100.0
                    else:
                        ret = (p_entry - p_future) / p_entry * 100.0
                    res[f"ret_{horizon}d"] = ret
        return res

    # ==============================================================
    # EXPERIMENT 1: BULLISH RE-ENTRY
    # Test combinations of:
    # Zacks Mode:
    #   - "Zacks_1_2_Only"
    #   - "Allow_Zacks_3_if_Score>=70"
    #   - "Allow_Zacks_3_if_Score>=75"
    #   - "Allow_Zacks_3_if_RS>=75"
    # Min RS: [50, 60, 65, 70]
    # Min Long Score: [0, 60, 65, 70]
    # ==============================================================
    print("\n--------------------------------------------------")
    print("RUNNING ADVANCED BULLISH GRID SEARCH...")
    print("--------------------------------------------------")
    
    zacks_configs = [
        ("Zacks 1-2 Only", lambda z, s, rs: z in [1, 2]),
        ("Zacks 1-2 OR (Z3 & Score>=70)", lambda z, s, rs: (z in [1, 2]) or (z == 3 and s >= 70)),
        ("Zacks 1-2 OR (Z3 & Score>=75)", lambda z, s, rs: (z in [1, 2]) or (z == 3 and s >= 75)),
        ("Zacks 1-2 OR (Z3 & RS>=75)", lambda z, s, rs: (z in [1, 2]) or (z == 3 and rs >= 75)),
        ("Zacks 1-3 Unrestricted", lambda z, s, rs: z in [1, 2, 3]),
    ]
    
    min_rs_list = [50, 60, 65, 70]
    min_score_list = [0, 60, 65, 70]
    allowed_themes_l = ["Leading", "Neutral", "Unclassified Leader"]
    
    bullish_results = []
    
    for z_label, z_fn in zacks_configs:
        for min_rs in min_rs_list:
            for min_score in min_score_list:
                active_entered = set()
                trades = []
                
                for cur_date in dates:
                    cur_stocks = daily_stocks[cur_date]
                    for tkr, drop_date in long_first_drops.items():
                        if tkr in active_entered:
                            continue
                        days_since_drop = trading_days_between(drop_date, cur_date)
                        if not (0 < days_since_drop <= 50):
                            continue
                            
                        s_data = cur_stocks.get(tkr)
                        if not s_data:
                            continue
                            
                        z = s_data.get("zacks_rank")
                        if z is None:
                            continue
                        z = int(z)
                        
                        th_class = s_data.get("theme_class", "Unknown")
                        if th_class not in allowed_themes_l:
                            continue
                            
                        close = s_data.get("last_close")
                        if not close or close < 10.0:
                            continue
                            
                        vol = s_data.get("avg_volume")
                        if not vol or vol < 1_000_000:
                            continue
                            
                        rs = s_data.get("rs_rating") or 0
                        score = s_data.get("long_score") or 0.0
                        
                        # Apply Zacks rule
                        if not z_fn(z, score, rs):
                            continue
                            
                        # Apply RS and Score threshold
                        if rs < min_rs or score < min_score:
                            continue
                            
                        active_entered.add(tkr)
                        f_rets = get_forward_returns(tkr, cur_date, side="long")
                        trades.append(f_rets)
                        
                n_trades = len(trades)
                if n_trades == 0:
                    continue
                r5 = [t["ret_5d"] for t in trades if "ret_5d" in t]
                r10 = [t["ret_10d"] for t in trades if "ret_10d" in t]
                r20 = [t["ret_20d"] for t in trades if "ret_20d" in t]
                
                w5 = (sum(1 for r in r5 if r > 0) / len(r5) * 100.0) if r5 else 0.0
                avg5 = np.mean(r5) if r5 else 0.0
                
                w10 = (sum(1 for r in r10 if r > 0) / len(r10) * 100.0) if r10 else 0.0
                avg10 = np.mean(r10) if r10 else 0.0
                
                w20 = (sum(1 for r in r20 if r > 0) / len(r20) * 100.0) if r20 else 0.0
                avg20 = np.mean(r20) if r20 else 0.0
                
                bullish_results.append({
                    "Zacks Mode": z_label,
                    "Min RS": min_rs,
                    "Min Score": min_score,
                    "Trades": n_trades,
                    "WinRate 5d": round(w5, 1),
                    "AvgRet 5d": round(avg5, 2),
                    "WinRate 10d": round(w10, 1),
                    "AvgRet 10d": round(avg10, 2),
                    "WinRate 20d": round(w20, 1),
                    "AvgRet 20d": round(avg20, 2),
                })
                
    b_df = pd.DataFrame(bullish_results)
    
    # Sort by best combined 5d and 10d performance
    b_df["Score_Metric"] = b_df["WinRate 5d"] * 0.4 + b_df["AvgRet 5d"] * 10 + b_df["WinRate 10d"] * 0.4 + b_df["AvgRet 10d"] * 10
    b_df = b_df.sort_values("Score_Metric", ascending=False).drop(columns=["Score_Metric"])
    
    print("\n--- TOP 15 BULLISH RE-ENTRY CONFIGURATIONS ---")
    print(b_df.head(15).to_string(index=False))
    
    print("\n--- COMPARISON OF ZACKS MODES AT Min RS 60, Min Score 60 ---")
    sub_df = b_df[(b_df["Min RS"] == 60) & (b_df["Min Score"] == 60)]
    print(sub_df.to_string(index=False))

    # ==============================================================
    # EXPERIMENT 2: BEARISH RE-ENTRY
    # Test combinations of:
    # Zacks Mode:
    #   - "Zacks 3-5 (Standard)"
    #   - "Zacks 4-5 Only"
    # Max Short RS: [40, 50, 60]
    # Max Short Score: [50, 60, 70, 999]
    # ==============================================================
    print("\n--------------------------------------------------")
    print("RUNNING ADVANCED BEARISH GRID SEARCH...")
    print("--------------------------------------------------")
    
    zacks_configs_s = [
        ("Zacks 3,4,5", [3, 4, 5]),
        ("Zacks 4,5 Only", [4, 5]),
    ]
    max_s_rs_list = [40, 50, 60]
    max_s_score_list = [50, 60, 70, 999]
    allowed_themes_s = ["Lagging"]
    
    bearish_results = []
    
    for z_label, allowed_zacks_s in zacks_configs_s:
        for max_s_rs in max_s_rs_list:
            for max_score in max_s_score_list:
                active_entered = set()
                trades = []
                
                for cur_date in dates:
                    cur_stocks = daily_stocks[cur_date]
                    for tkr, drop_date in short_first_drops.items():
                        if tkr in active_entered:
                            continue
                        days_since_drop = trading_days_between(drop_date, cur_date)
                        if not (0 < days_since_drop <= 50):
                            continue
                            
                        s_data = cur_stocks.get(tkr)
                        if not s_data:
                            continue
                            
                        z = s_data.get("zacks_rank")
                        if z is None or int(z) not in allowed_zacks_s:
                            continue
                            
                        th_class = s_data.get("theme_class", "Unknown")
                        if th_class not in allowed_themes_s:
                            continue
                            
                        close = s_data.get("last_close")
                        if not close or close < 10.0:
                            continue
                            
                        vol = s_data.get("avg_volume")
                        if not vol or vol < 1_000_000:
                            continue
                            
                        s_rs = s_data.get("short_rs_rating") or 999
                        s_score = s_data.get("short_score") or 999.0
                        
                        if s_rs > max_s_rs or s_score > max_score:
                            continue
                            
                        active_entered.add(tkr)
                        f_rets = get_forward_returns(tkr, cur_date, side="short")
                        trades.append(f_rets)
                        
                n_trades = len(trades)
                if n_trades == 0:
                    continue
                r5 = [t["ret_5d"] for t in trades if "ret_5d" in t]
                r10 = [t["ret_10d"] for t in trades if "ret_10d" in t]
                r20 = [t["ret_20d"] for t in trades if "ret_20d" in t]
                
                w5 = (sum(1 for r in r5 if r > 0) / len(r5) * 100.0) if r5 else 0.0
                avg5 = np.mean(r5) if r5 else 0.0
                
                w10 = (sum(1 for r in r10 if r > 0) / len(r10) * 100.0) if r10 else 0.0
                avg10 = np.mean(r10) if r10 else 0.0
                
                w20 = (sum(1 for r in r20 if r > 0) / len(r20) * 100.0) if r20 else 0.0
                avg20 = np.mean(r20) if r20 else 0.0
                
                bearish_results.append({
                    "Zacks Mode": z_label,
                    "Max Short RS": max_s_rs,
                    "Max Score": max_score if max_score < 999 else "None",
                    "Trades": n_trades,
                    "WinRate 5d": round(w5, 1),
                    "AvgRet 5d": round(avg5, 2),
                    "WinRate 10d": round(w10, 1),
                    "AvgRet 10d": round(avg10, 2),
                    "WinRate 20d": round(w20, 1),
                    "AvgRet 20d": round(avg20, 2),
                })
                
    s_df = pd.DataFrame(bearish_results)
    s_df["Score_Metric"] = s_df["WinRate 5d"] * 0.4 + s_df["AvgRet 5d"] * 10 + s_df["WinRate 10d"] * 0.4 + s_df["AvgRet 10d"] * 10
    s_df = s_df.sort_values("Score_Metric", ascending=False).drop(columns=["Score_Metric"])
    
    print("\n--- TOP 10 BEARISH RE-ENTRY CONFIGURATIONS ---")
    print(s_df.head(10).to_string(index=False))
    
    out_dir = Path("backtesting/results")
    out_dir.mkdir(parents=True, exist_ok=True)
    b_df.to_csv(out_dir / "advanced_reentry_bullish_grid.csv", index=False)
    s_df.to_csv(out_dir / "advanced_reentry_bearish_grid.csv", index=False)
    print("\nResults saved to backtesting/results/advanced_reentry_bullish_grid.csv and advanced_reentry_bearish_grid.csv")

if __name__ == "__main__":
    run_advanced_reentry_backtest()


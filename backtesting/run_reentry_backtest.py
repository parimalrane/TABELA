import json
import os
from pathlib import Path
import pandas as pd
import numpy as np

def run_reentry_backtest():
    print("==================================================")
    print("TABELA RE-ENTRY BACKTEST (BULLISH & BEARISH)")
    print("==================================================")
    
    # 1. Load all stock universe history into memory
    stock_universe_dir = Path("market_data/stock_universe")
    snapshot_files = sorted(list(stock_universe_dir.rglob("*_stock_history.json")))
    print(f"Loading {len(snapshot_files)} daily snapshots into memory...")
    
    daily_stocks = {} # date_str -> {ticker: dict}
    daily_prices = {} # date_str -> {ticker: last_close}
    
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
    if not dropped_csv.exists():
        print("dropped_history.csv not found!")
        return
        
    drops_df = pd.read_csv(dropped_csv, dtype=str)
    drops_df["_dt"] = pd.to_datetime(drops_df["Date"], errors="coerce")
    
    # Clean tickers
    drops_df["Ticker"] = drops_df["Ticker"].astype(str).str.replace("*", "").str.replace("~", "").str.strip().str.upper()
    
    # Separate Long and Short drops, sort ascending by date, keep first drop for each ticker
    long_drops_df = drops_df[drops_df["Type"] == "Dropped Long"].sort_values("_dt").drop_duplicates(subset=["Ticker"], keep="first")
    short_drops_df = drops_df[drops_df["Type"] == "Dropped Short"].sort_values("_dt").drop_duplicates(subset=["Ticker"], keep="first")
    
    long_first_drops = {r["Ticker"]: r["Date"] for _, r in long_drops_df.iterrows()}
    short_first_drops = {r["Ticker"]: r["Date"] for _, r in short_drops_df.iterrows()}
    
    print(f"Total Unique Dropped Long Tickers: {len(long_first_drops)}")
    print(f"Total Unique Dropped Short Tickers: {len(short_first_drops)}")
    
    # Helper to calculate trading days between two dates
    def trading_days_between(d1, d2):
        if d1 not in date_to_idx or d2 not in date_to_idx:
            return 999
        return date_to_idx[d2] - date_to_idx[d1]

    # Forward return calculator: 5d, 10d, 20d forward returns
    # For long: (P_future - P_entry) / P_entry
    # For short: (P_entry - P_future) / P_entry
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
    # 3. BACKTEST BULLISH RE-ENTRY GRID
    # Parameters to test: MIN_RS in [0, 40, 50, 60, 65, 70, 75, 80]
    # Theme: ['Leading', 'Unclassified Leader'] vs + ['Neutral']
    # ==============================================================
    print("\n--------------------------------------------------")
    print("RUNNING BULLISH RE-ENTRY GRID SEARCH...")
    print("--------------------------------------------------")
    
    rs_thresholds_long = [0, 40, 50, 60, 65, 70, 75, 80]
    theme_modes = [
        ("Leading_Only", ["Leading", "Unclassified Leader"]),
        ("Leading+Neutral", ["Leading", "Neutral", "Unclassified Leader"])
    ]
    
    bullish_results = []
    
    for theme_label, allowed_themes in theme_modes:
        for min_rs in rs_thresholds_long:
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
                    if z is None or z not in [1, 2]:
                        continue
                        
                    th_class = s_data.get("theme_class", "Unknown")
                    if th_class not in allowed_themes:
                        continue
                        
                    close = s_data.get("last_close")
                    if not close or close < 10.0:
                        continue
                        
                    vol = s_data.get("avg_volume")
                    if not vol or vol < 1_000_000:
                        continue
                        
                    rs = s_data.get("rs_rating")
                    if rs is None or rs < min_rs:
                        continue
                        
                    active_entered.add(tkr)
                    f_rets = get_forward_returns(tkr, cur_date, side="long")
                    trades.append(f_rets)
                    
            n_trades = len(trades)
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
                "Theme Mode": theme_label,
                "Min RS": min_rs,
                "Trades": n_trades,
                "WinRate 5d": round(w5, 1),
                "AvgRet 5d": round(avg5, 2),
                "WinRate 10d": round(w10, 1),
                "AvgRet 10d": round(avg10, 2),
                "WinRate 20d": round(w20, 1),
                "AvgRet 20d": round(avg20, 2),
            })
            
    b_df = pd.DataFrame(bullish_results)
    print("\n--- BULLISH RE-ENTRY RESULTS ---")
    print(b_df.to_string(index=False))
    
    # ==============================================================
    # 4. BACKTEST BEARISH RE-ENTRY GRID
    # Parameters to test: MAX_SHORT_RS in [100, 70, 60, 50, 40, 30]
    # Theme: ['Lagging'] vs + ['Neutral']
    # ==============================================================
    print("\n--------------------------------------------------")
    print("RUNNING BEARISH RE-ENTRY GRID SEARCH...")
    print("--------------------------------------------------")
    
    rs_thresholds_short = [100, 70, 60, 50, 40, 30]
    theme_modes_short = [
        ("Lagging_Only", ["Lagging"]),
        ("Lagging+Neutral", ["Lagging", "Neutral"])
    ]
    
    bearish_results = []
    
    for theme_label, allowed_themes in theme_modes_short:
        for max_short_rs in rs_thresholds_short:
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
                    if z is None or z not in [3, 4, 5]:
                        continue
                        
                    th_class = s_data.get("theme_class", "Unknown")
                    if th_class not in allowed_themes:
                        continue
                        
                    close = s_data.get("last_close")
                    if not close or close < 10.0:
                        continue
                        
                    vol = s_data.get("avg_volume")
                    if not vol or vol < 1_000_000:
                        continue
                        
                    s_rs = s_data.get("short_rs_rating")
                    if s_rs is None or s_rs > max_short_rs:
                        continue
                        
                    active_entered.add(tkr)
                    f_rets = get_forward_returns(tkr, cur_date, side="short")
                    trades.append(f_rets)
                    
            n_trades = len(trades)
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
                "Theme Mode": theme_label,
                "Max Short RS": max_short_rs,
                "Trades": n_trades,
                "WinRate 5d": round(w5, 1),
                "AvgRet 5d": round(avg5, 2),
                "WinRate 10d": round(w10, 1),
                "AvgRet 10d": round(avg10, 2),
                "WinRate 20d": round(w20, 1),
                "AvgRet 20d": round(avg20, 2),
            })
            
    s_df = pd.DataFrame(bearish_results)
    print("\n--- BEARISH RE-ENTRY RESULTS ---")
    print(s_df.to_string(index=False))
    
    # Save results to backtesting/results/
    out_dir = Path("backtesting/results")
    out_dir.mkdir(parents=True, exist_ok=True)
    b_df.to_csv(out_dir / "reentry_bullish_grid.csv", index=False)
    s_df.to_csv(out_dir / "reentry_bearish_grid.csv", index=False)
    print("\nSaved grid results to backtesting/results/reentry_bullish_grid.csv and reentry_bearish_grid.csv")

if __name__ == "__main__":
    run_reentry_backtest()


import json
import os
from pathlib import Path
import pandas as pd
import numpy as np

def load_data():
    stock_universe_dir = Path("market_data/stock_universe")
    snapshot_files = sorted(list(stock_universe_dir.rglob("*_stock_history.json")))
    print(f"Loading {len(snapshot_files)} daily snapshots into memory...", flush=True)
    
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
    print(f"Loaded {len(dates)} dates: {dates[0]} to {dates[-1]}")
    return dates, daily_stocks, daily_prices

def evaluate_trade(ticker, pick_date_idx, dates, daily_prices, is_long=True,
                   pullback_pct=0.05, wait_days=21, stop_pct=0.07, target_pct=0.21, max_hold_days=50):
    """
    Simulates:
    1. Wait up to wait_days for close pullback of pullback_pct
    2. If entered, hold up to max_hold_days with stop_pct and target_pct (1:3 R:R)
    """
    pick_date = dates[pick_date_idx]
    pick_price = daily_prices[pick_date].get(ticker)
    if not pick_price or pick_price <= 0:
        return {"status": "NO_PRICE"}
    
    entry_idx = None
    entry_price = None
    
    # Step 1: Wait for pullback
    for i in range(1, wait_days + 1):
        curr_idx = pick_date_idx + i
        if curr_idx >= len(dates):
            break
        d = dates[curr_idx]
        p = daily_prices[d].get(ticker)
        if not p or p <= 0:
            continue
        
        if is_long:
            # Long pullback: price drops by pullback_pct
            if p <= pick_price * (1.0 - pullback_pct):
                entry_idx = curr_idx
                entry_price = p
                break
        else:
            # Short bounce: price rises by pullback_pct
            if p >= pick_price * (1.0 + pullback_pct):
                entry_idx = curr_idx
                entry_price = p
                break
                
    if entry_idx is None:
        return {"status": "NO_PULLBACK"}
    
    # Step 2: Simulate trade execution
    stop_price = entry_price * (1.0 - stop_pct) if is_long else entry_price * (1.0 + stop_pct)
    target_price = entry_price * (1.0 + target_pct) if is_long else entry_price * (1.0 - target_pct)
    
    for h in range(1, max_hold_days + 1):
        curr_idx = entry_idx + h
        if curr_idx >= len(dates):
            # Data ended, trade is still OPEN
            last_p = daily_prices[dates[-1]].get(ticker, entry_price)
            ret = (last_p / entry_price - 1.0) if is_long else (1.0 - last_p / entry_price)
            return {"status": "OPEN", "return": ret, "days_held": h}
            
        d = dates[curr_idx]
        p = daily_prices[d].get(ticker)
        if not p or p <= 0:
            continue
            
        if is_long:
            if p <= stop_price:
                ret = (p / entry_price) - 1.0
                return {"status": "STOP", "return": ret, "days_held": h}
            if p >= target_price:
                ret = (p / entry_price) - 1.0
                return {"status": "TARGET", "return": ret, "days_held": h}
        else:
            if p >= stop_price:
                ret = 1.0 - (p / entry_price)
                return {"status": "STOP", "return": ret, "days_held": h}
            if p <= target_price:
                ret = 1.0 - (p / entry_price)
                return {"status": "TARGET", "return": ret, "days_held": h}
                
    # Max hold expired
    exit_p = daily_prices[dates[entry_idx + max_hold_days]].get(ticker, entry_price)
    ret = (exit_p / entry_price - 1.0) if is_long else (1.0 - exit_p / entry_price)
    return {"status": "EXPIRED", "return": ret, "days_held": max_hold_days}

def run_simulation(dates, daily_stocks, daily_prices, 
                   is_long=True,
                   min_range=85.0, max_range=30.0,
                   use_52w_gate=True,
                   use_tabela_retention=True,
                   pullback_pct=0.05,
                   wait_days=21,
                   stop_pct=0.07,
                   target_pct=0.21,
                   max_hold_days=50):
    """
    Simulates day-by-day watchlist generation and pullback execution.
    """
    active_watchlist = set() # tickers currently in watchlist
    trades = []
    daily_wl_sizes = []
    
    # Track ticker pick cooldown to prevent duplicate entries on consecutive days
    last_picked_idx = {}
    
    for idx, d in enumerate(dates):
        stocks_today = daily_stocks[d]
        next_watchlist = set()
        
        # 1. Evaluate candidate universe
        for ticker, row in stocks_today.items():
            price = row.get("last_close") or 0.0
            vol = row.get("avg_volume") or 0.0
            rs = row.get("rs_rating") or 0.0
            short_rs = row.get("short_rs_rating") or 0.0
            theme_class = row.get("theme_class") or "Unknown"
            zacks = row.get("zacks_rank")
            pos_52w = row.get("price_position_52w")
            
            try:
                zacks = int(float(zacks)) if zacks is not None and not pd.isna(zacks) else 0
            except:
                zacks = 0
            try:
                pos_52w = float(pos_52w) if pos_52w is not None and not pd.isna(pos_52w) else 50.0
            except:
                pos_52w = 50.0
                
            in_previous_wl = ticker in active_watchlist
            
            if is_long:
                min_vol = 1_000_000
                min_price = 10.0
                if price < min_price or vol < min_vol:
                    continue
                
                if not in_previous_wl:
                    # GET-IN CRITERIA
                    if rs < 90.0:
                        continue
                    if theme_class not in ["Leading", "Unclassified Leader"]:
                        continue
                    if zacks not in [1, 2]:
                        continue
                    if use_52w_gate and pos_52w < min_range:
                        continue
                    
                    next_watchlist.add(ticker)
                    
                    # Trigger trade evaluation if not recently triggered
                    prev_idx = last_picked_idx.get(ticker, -999)
                    if (idx - prev_idx) > wait_days:
                        last_picked_idx[ticker] = idx
                        res = evaluate_trade(ticker, idx, dates, daily_prices, is_long=True,
                                             pullback_pct=pullback_pct, wait_days=wait_days,
                                             stop_pct=stop_pct, target_pct=target_pct, max_hold_days=max_hold_days)
                        if res["status"] in ["STOP", "TARGET", "EXPIRED", "OPEN"]:
                            trades.append(res)
                else:
                    # STAY-IN CRITERIA (TABELA Retention)
                    if use_tabela_retention:
                        if rs >= 75.0 and theme_class in ["Leading", "Neutral", "Unclassified Leader"] and zacks in [1, 2, 3]:
                            next_watchlist.add(ticker)
                    else:
                        # Original stateless logic: must meet 90/90 daily
                        if rs >= 90.0 and theme_class in ["Leading", "Unclassified Leader"] and zacks in [1, 2]:
                            next_watchlist.add(ticker)
            else:
                # SHORT
                min_vol = 2_000_000
                min_price = 10.0
                if price < min_price or vol < min_vol:
                    continue
                    
                if not in_previous_wl:
                    # GET-IN CRITERIA
                    if rs < 8.0 or rs > 60.0:
                        continue
                    if theme_class not in ["Lagging"]:
                        continue
                    if zacks not in [3, 4, 5]:
                        continue
                    if use_52w_gate and pos_52w > max_range:
                        continue
                        
                    next_watchlist.add(ticker)
                    
                    prev_idx = last_picked_idx.get(ticker, -999)
                    if (idx - prev_idx) > wait_days:
                        last_picked_idx[ticker] = idx
                        res = evaluate_trade(ticker, idx, dates, daily_prices, is_long=False,
                                             pullback_pct=pullback_pct, wait_days=wait_days,
                                             stop_pct=stop_pct, target_pct=target_pct, max_hold_days=max_hold_days)
                        if res["status"] in ["STOP", "TARGET", "EXPIRED", "OPEN"]:
                            trades.append(res)
                else:
                    # STAY-IN CRITERIA (TABELA Retention)
                    if use_tabela_retention:
                        if rs <= 75.0 and theme_class in ["Lagging", "Neutral"] and zacks in [2, 3, 4, 5]:
                            next_watchlist.add(ticker)
                    else:
                        if rs <= 60.0 and theme_class in ["Lagging"] and zacks in [3, 4, 5]:
                            next_watchlist.add(ticker)
                            
        active_watchlist = next_watchlist
        daily_wl_sizes.append(len(active_watchlist))
        
    avg_wl_size = np.mean(daily_wl_sizes) if daily_wl_sizes else 0.0
    
    # Calculate performance metrics
    closed_trades = [t for t in trades if t["status"] in ["STOP", "TARGET", "EXPIRED"]]
    open_trades = [t for t in trades if t["status"] == "OPEN"]
    
    if not closed_trades:
        return {
            "total_trades": len(trades),
            "closed": 0,
            "open": len(open_trades),
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "avg_return": 0.0,
            "avg_wl_size": round(avg_wl_size, 1)
        }
        
    wins = [t["return"] for t in closed_trades if t["return"] > 0]
    losses = [abs(t["return"]) for t in closed_trades if t["return"] <= 0]
    
    win_rate = (len(wins) / len(closed_trades)) * 100.0
    tot_win = sum(wins)
    tot_loss = sum(losses)
    profit_factor = (tot_win / tot_loss) if tot_loss > 0 else 99.9
    avg_return = np.mean([t["return"] for t in closed_trades]) * 100.0
    
    return {
        "total_trades": len(trades),
        "closed": len(closed_trades),
        "open": len(open_trades),
        "win_rate": round(win_rate, 1),
        "profit_factor": round(profit_factor, 2),
        "avg_return": round(avg_return, 2),
        "avg_wl_size": round(avg_wl_size, 1)
    }

def main():
    dates, daily_stocks, daily_prices = load_data()
    
    print("\n" + "="*80)
    print("STAGE 0: BASELINE COMPARISON (NO 52W GATE vs 52W GATE)")
    print("="*80)
    
    print("\n--- LONG SIDE: 52W RANGE GATE SWEEP ---")
    headers = f"{'Config':<35} | {'Trades':<8} | {'Closed':<7} | {'Win%':<7} | {'Avg%':<7} | {'PF':<6} | {'Avg WL':<7}"
    print(headers)
    print("-" * len(headers))
    
    # Baseline Long (No 52W gate, No TABELA Retention)
    res_base = run_simulation(dates, daily_stocks, daily_prices, is_long=True, use_52w_gate=False, use_tabela_retention=False)
    print(f"{'Baseline (No 52W Gate, Daily Reset)':<35} | {res_base['total_trades']:<8} | {res_base['closed']:<7} | {res_base['win_rate']:<6}% | {res_base['avg_return']:<6}% | {res_base['profit_factor']:<6} | {res_base['avg_wl_size']:<7}")
    
    # Long 52W Gate variations (with TABELA Retention)
    for r in [70.0, 75.0, 80.0, 85.0, 90.0, 95.0]:
        res = run_simulation(dates, daily_stocks, daily_prices, is_long=True, min_range=r, use_52w_gate=True, use_tabela_retention=True)
        lbl = f"52W Range >= {r:.0f}% + TABELA Retention"
        print(f"{lbl:<35} | {res['total_trades']:<8} | {res['closed']:<7} | {res['win_rate']:<6}% | {res['avg_return']:<6}% | {res['profit_factor']:<6} | {res['avg_wl_size']:<7}")
        
    print("\n--- SHORT SIDE: 52W RANGE GATE SWEEP ---")
    print(headers)
    print("-" * len(headers))
    
    res_short_base = run_simulation(dates, daily_stocks, daily_prices, is_long=False, use_52w_gate=False, use_tabela_retention=False)
    print(f"{'Baseline (No 52W Gate, Daily Reset)':<35} | {res_short_base['total_trades']:<8} | {res_short_base['closed']:<7} | {res_short_base['win_rate']:<6}% | {res_short_base['avg_return']:<6}% | {res_short_base['profit_factor']:<6} | {res_short_base['avg_wl_size']:<7}")
    
    for r in [40.0, 30.0, 20.0, 15.0, 10.0]:
        res = run_simulation(dates, daily_stocks, daily_prices, is_long=False, max_range=r, use_52w_gate=True, use_tabela_retention=True)
        lbl = f"52W Range <= {r:.0f}% + TABELA Retention"
        print(f"{lbl:<35} | {res['total_trades']:<8} | {res['closed']:<7} | {res['win_rate']:<6}% | {res['avg_return']:<6}% | {res['profit_factor']:<6} | {res['avg_wl_size']:<7}")
        
    print("\n" + "="*80)
    print("STAGE 1: PULLBACK DEPTH SWEEP (5% to 20% on Best Long/Short Gates)")
    print("="*80)
    print(f"{'Pullback Depth':<35} | {'Trades':<8} | {'Closed':<7} | {'Win%':<7} | {'Avg%':<7} | {'PF':<6} | {'Side':<7}")
    print("-" * 80)
    
    for pb in [0.03, 0.05, 0.08, 0.10, 0.15, 0.20]:
        res_l = run_simulation(dates, daily_stocks, daily_prices, is_long=True, min_range=85.0, use_52w_gate=True, use_tabela_retention=True, pullback_pct=pb)
        print(f"Long Pullback {pb*100:4.1f}% | Range>=85%    | {res_l['total_trades']:<8} | {res_l['closed']:<7} | {res_l['win_rate']:<6}% | {res_l['avg_return']:<6}% | {res_l['profit_factor']:<6} | Long")
        
    print("-" * 80)
    for pb in [0.03, 0.05, 0.08, 0.10, 0.15, 0.20]:
        res_s = run_simulation(dates, daily_stocks, daily_prices, is_long=False, max_range=30.0, use_52w_gate=True, use_tabela_retention=True, pullback_pct=pb)
        print(f"Short Bounce  {pb*100:4.1f}% | Range<=30%    | {res_s['total_trades']:<8} | {res_s['closed']:<7} | {res_s['win_rate']:<6}% | {res_s['avg_return']:<6}% | {res_s['profit_factor']:<6} | Short")

if __name__ == "__main__":
    main()


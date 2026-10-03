import sys
import os
import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

# Add root directory to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import config.config as cfg

def run_pullback_tuner():
    prices = {}
    input_dir = Path("c:/TABELA/market_data/input_files")
    
    # Load daily closing prices
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith("stocks.csv"):
                date_str = file[:8]
                date_fmt = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                try:
                    df = pd.read_csv(os.path.join(root, file))
                    df["Ticker"] = df["Ticker"].str.strip()
                    price_dict = dict(zip(df["Ticker"], df["Last Close"]))
                    prices[date_fmt] = price_dict
                except Exception:
                    continue

    json_dir = Path("c:/TABELA/market_data/stock_universe")
    json_files = sorted([os.path.join(r, f) for r, d, files in os.walk(json_dir) for f in files if f.endswith("_stock_history.json")])

    all_dates = sorted(prices.keys())
    if not all_dates:
        print("No price data found.")
        return

    # Track historical state transitions
    previous_state = {}  # ticker: 'STRONG_LONG', 'MILD_LONG', 'STRONG_SHORT', 'MILD_SHORT', 'NONE'
    
    # Track triggered setups
    # {ticker: {"entry_date": date, "entry_price": px, "type": "LONG_PULLBACK"}}
    active_pullbacks = []
    
    long_themes = cfg.LONG_ENTRY.get("THEMES", [])
    dist_themes = cfg.DIST_ENTRY.get("THEMES", [])
    long_rs_gate = cfg.LONG_ENTRY.get("MIN_RS", 90.0)
    long_score_gate = cfg.LONG_ENTRY.get("MIN_LONG_SCORE", 90.0)
    mild_long_gate = cfg.LONG_ENTRY.get("MIN_DROPPED_WATCH_SCORE", 70.0)
    
    short_rs_max = cfg.SHORT_ENTRY.get("MAX_SHORT_RS", 35.0)
    short_score_max = cfg.SHORT_ENTRY.get("MAX_SHORT_SCORE", 40.0)
    mild_short_gate = cfg.DIST_ENTRY.get("MAX_DROPPED_WATCH_SCORE", 30.0)
    short_themes = cfg.SHORT_ENTRY.get("THEMES", [])

    for file in json_files:
        date_str = os.path.basename(file)[:10]
        
        with open(file, "r") as f:
            try:
                data = json.load(f)
            except Exception:
                continue
        
        current_state = {}
        
        for row in data:
            ticker = row["ticker"]
            long_score = row.get("long_score", 0.0)
            rs_rating = row.get("rs_rating", 0.0)
            short_score = row.get("short_score", long_score)
            short_rs_rating = row.get("short_rs_rating", rs_rating)
            theme_class = row.get("theme_class", "Unknown")
            last_close = row.get("last_close", prices.get(date_str, {}).get(ticker, 0))
            
            state = "NONE"
            
            # Check LONG thresholds
            is_strong_long = (long_score >= long_score_gate and rs_rating >= long_rs_gate and theme_class in long_themes)
            is_mild_long = (long_score >= mild_long_gate and rs_rating >= mild_long_gate and theme_class not in dist_themes)
            
            # Check SHORT thresholds
            is_strong_short = (short_score <= short_score_max and short_rs_rating <= short_rs_max and theme_class in short_themes)
            is_mild_short = (short_score <= mild_short_gate and short_rs_rating <= mild_short_gate and theme_class not in long_themes)
            
            if is_strong_long: state = "STRONG_LONG"
            elif is_mild_long: state = "MILD_LONG"
            elif is_strong_short: state = "STRONG_SHORT"
            elif is_mild_short: state = "MILD_SHORT"
            
            current_state[ticker] = state
            
            prev = previous_state.get(ticker, "NONE")
            
            if prev == "STRONG_LONG" and state == "MILD_LONG":
                active_pullbacks.append({
                    "ticker": ticker,
                    "entry_date": date_str,
                    "entry_price": last_close,
                    "type": "LONG_PULLBACK"
                })
            elif prev == "STRONG_SHORT" and state == "MILD_SHORT":
                active_pullbacks.append({
                    "ticker": ticker,
                    "entry_date": date_str,
                    "entry_price": last_close,
                    "type": "SHORT_RALLY"
                })
                
        previous_state = current_state

    print(f"Discovered {len([x for x in active_pullbacks if x['type'] == 'LONG_PULLBACK'])} Long Pullbacks")
    print(f"Discovered {len([x for x in active_pullbacks if x['type'] == 'SHORT_RALLY'])} Short Relief Rallies")
    
    # Calculate MFE (Maximum Favorable Excursion)
    time_windows = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
    
    long_results = {w: [] for w in time_windows}
    short_results = {w: [] for w in time_windows}
    
    for trade in active_pullbacks:
        ticker = trade["ticker"]
        entry_date = trade["entry_date"]
        entry_px = trade["entry_price"]
        
        if entry_px <= 0: continue
        
        # Find index of entry date
        try:
            start_idx = all_dates.index(entry_date)
        except ValueError:
            continue
            
        for w in time_windows:
            end_idx = min(start_idx + w, len(all_dates) - 1)
            future_dates = all_dates[start_idx+1 : end_idx+1]
            
            if not future_dates: continue
            
            px_path = [prices.get(d, {}).get(ticker, 0) for d in future_dates]
            px_path = [p for p in px_path if p > 0]
            
            if not px_path: continue
            
            if trade["type"] == "LONG_PULLBACK":
                max_px = max(px_path)
                mfe_pct = ((max_px - entry_px) / entry_px) * 100
                long_results[w].append(mfe_pct)
            else:
                min_px = min(px_path)
                mfe_pct = ((entry_px - min_px) / entry_px) * 100 # Gain as a short
                short_results[w].append(mfe_pct)

    print("\n========================================")
    print("MILD BULLISH (LONG PULLBACK) MFE TUNING")
    print("========================================")
    print(f"{'Wait Days':<12} | {'Avg Max Return (%)':<20} | {'Sample Size'}")
    print("-" * 50)
    for w in time_windows:
        arr = long_results[w]
        avg_mfe = sum(arr) / len(arr) if arr else 0
        print(f"{w:<12} | {avg_mfe:<20.2f} | {len(arr)}")

    print("\n========================================")
    print("MILD BEARISH (SHORT RALLY FADE) MFE TUNING")
    print("========================================")
    print(f"{'Wait Days':<12} | {'Avg Max Gain (%)':<20} | {'Sample Size'}")
    print("-" * 50)
    for w in time_windows:
        arr = short_results[w]
        avg_mfe = sum(arr) / len(arr) if arr else 0
        print(f"{w:<12} | {avg_mfe:<20.2f} | {len(arr)}")

if __name__ == "__main__":
    run_pullback_tuner()

import os
import json
import pandas as pd
from pathlib import Path
from config.config import LONG_ENTRY, DIST_ENTRY

def run_backtest(mode="long", silent=False):
    prices = {}
    input_dir = Path("c:/TABELA/market_data/input_files")
    
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
        if not silent: print("No price data found.")
        return None
    current_date = all_dates[-1]

    entries = {}

    for file in json_files:
        date_str = os.path.basename(file)[:10]
        if date_str == current_date:
            break
            
        with open(file, "r") as f:
            try:
                data = json.load(f)
            except Exception:
                continue
        
        for row in data:
            if mode == "long":
                long_score = row.get("long_score", 0.0)
                rs_rating = row.get("rs_rating", 0)
            else:
                long_score = row.get("long_score", 100.0)
                rs_rating = row.get("rs_rating", 100)
                
            ticker = row["ticker"]
            theme_class = row.get("theme_class", "Unknown")
            
            if mode == "long":
                allowed_themes = LONG_ENTRY.get("THEMES", [])
                min_rs = LONG_ENTRY.get("MIN_RS", 0.0)
                min_score = LONG_ENTRY.get("MIN_LONG_SCORE", 0.0)
                min_price = LONG_ENTRY.get("MIN_PRICE", 10.0)
                
                if long_score >= min_score and rs_rating >= min_rs and theme_class in allowed_themes:
                    if ticker not in entries:
                        entry_price = prices.get(date_str, {}).get(ticker, 0)
                        if entry_price >= min_price:  
                            entries[ticker] = {
                                "entry_date": date_str,
                                "entry_price": entry_price,
                                "theme_class": theme_class,
                                "best_score": long_score
                            }
                    else:
                        if long_score > entries[ticker]["best_score"]:
                            entries[ticker]["best_score"] = long_score

            elif mode == "short":
                allowed_themes = DIST_ENTRY.get("THEMES", [])
                max_rs = DIST_ENTRY.get("MAX_RS", 10.0)
                min_rs_short = DIST_ENTRY.get("MIN_RS", 0.0)
                max_score = DIST_ENTRY.get("MAX_LONG_SCORE", 20.0)
                min_price = LONG_ENTRY.get("MIN_PRICE", 10.0)
                
                if long_score <= max_score and rs_rating <= max_rs and rs_rating > min_rs_short and theme_class in allowed_themes:
                    if ticker not in entries:
                        entry_price = prices.get(date_str, {}).get(ticker, 0)
                        if entry_price >= min_price:  
                            entries[ticker] = {
                                "entry_date": date_str,
                                "entry_price": entry_price,
                                "theme_class": theme_class,
                                "best_score": long_score
                            }
                    else:
                        if long_score < entries[ticker]["best_score"]:
                            entries[ticker]["best_score"] = long_score

    today_prices = prices.get(current_date, {})
    results = []

    for ticker, data in entries.items():
        current_price = today_prices.get(ticker, 0)
        if current_price > 0:
            if mode == "long":
                ret = ((current_price - data["entry_price"]) / data["entry_price"]) * 100.0
            else:
                ret = ((data["entry_price"] - current_price) / data["entry_price"]) * 100.0
                
            results.append({
                "Ticker": ticker,
                "Entry Px": data["entry_price"],
                "Current Px": current_price,
                "Return %": round(ret, 2),
                "Class": data["theme_class"]
            })

    res_df = pd.DataFrame(results)
    
    if res_df.empty:
        if not silent: print("No trades triggered.")
        return {
            "total_trades": 0, "win_rate": 0.0, "avg_return": 0.0,
            "leading_trades": 0, "leading_win_rate": 0.0, "leading_avg_return": 0.0,
            "neutral_trades": 0, "neutral_win_rate": 0.0, "neutral_avg_return": 0.0,
            "lagging_trades": 0, "lagging_win_rate": 0.0, "lagging_avg_return": 0.0
        }
    
    win_rate = (len(res_df[res_df['Return %'] > 0]) / len(res_df)) * 100
    avg_return = res_df['Return %'].mean()
    
    leading = res_df[res_df['Class'] == 'Leading']
    neutral = res_df[res_df['Class'] == 'Neutral']
    lagging = res_df[res_df['Class'] == 'Lagging']
    
    ld_t = len(leading)
    nt_t = len(neutral)
    lg_t = len(lagging)
    
    result_dict = {
        "total_trades": len(res_df),
        "win_rate": round(win_rate, 2),
        "avg_return": round(avg_return, 2),
        "leading_trades": ld_t,
        "leading_win_rate": round((len(leading[leading['Return %'] > 0]) / ld_t * 100), 2) if ld_t else 0.0,
        "leading_avg_return": round(leading['Return %'].mean(), 2) if ld_t else 0.0,
        "neutral_trades": nt_t,
        "neutral_win_rate": round((len(neutral[neutral['Return %'] > 0]) / nt_t * 100), 2) if nt_t else 0.0,
        "neutral_avg_return": round(neutral['Return %'].mean(), 2) if nt_t else 0.0,
        "lagging_trades": lg_t,
        "lagging_win_rate": round((len(lagging[lagging['Return %'] > 0]) / lg_t * 100), 2) if lg_t else 0.0,
        "lagging_avg_return": round(lagging['Return %'].mean(), 2) if lg_t else 0.0,
    }
    
    if not silent:
        print("\n" + "="*80)
        print(f"          TABELA 3-MONTH {mode.upper()} BACKTEST")
        print("="*80)
        print(f"Total Trades: {len(res_df)}")
        print(f"Win Rate: {win_rate:.1f}%")
        print(f"Average Return: {avg_return:.2f}%\n")
        
    return result_dict

if __name__ == "__main__":
    import sys
    run_mode = "long"
    if len(sys.argv) > 1 and sys.argv[1] == "short":
        run_mode = "short"
    run_backtest(mode=run_mode)

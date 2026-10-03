import os
import json
import pandas as pd
from pathlib import Path
import config.config as cfg

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

    # Global tracking of all actual trades triggered: entries = {ticker: {bucket_type: {data}}}
    entries = {}
    # Stateful memory mapping for drops: drop_tracker = {ticker: {"drop_date": date, "days_dropped": 0}}
    drop_tracker = {}

    for file in json_files:
        date_str = os.path.basename(file)[:10]
        if date_str == current_date:
            break
            
        with open(file, "r") as f:
            try:
                data = json.load(f)
            except Exception:
                continue
        
        # Increment all dropped clocks today
        for t in list(drop_tracker.keys()):
            drop_tracker[t]["days_dropped"] += 1

        for row in data:
            if mode == "long":
                score = row.get("long_score", 0.0)
                rs_rating = row.get("rs_rating", 0)
            else:
                score = row.get("short_score", row.get("long_score", 100.0))
                rs_rating = row.get("short_rs_rating", row.get("rs_rating", 100))
                
            ticker = row["ticker"]
            theme_class = row.get("theme_class", "Unknown")
            zacks_rank = row.get("zacks_rank", 3)
            
            # Fetch daily price to ensure liquidity/entry logic
            entry_price = prices.get(date_str, {}).get(ticker, 0)
            
            if mode == "long":
                allowed_themes = cfg.LONG_ENTRY.get("THEMES", [])
                min_rs = cfg.LONG_ENTRY.get("MIN_RS", 0.0)
                min_score = cfg.LONG_ENTRY.get("MIN_LONG_SCORE", 0.0)
                min_price = cfg.LONG_ENTRY.get("MIN_PRICE", 10.0)
                mild_floor = cfg.LONG_ENTRY.get("MIN_DROPPED_WATCH_SCORE", 70.0)
                basing_zacks = cfg.LONG_ENTRY.get("BASING_ZACKS", [1, 2])
                basing_themes = cfg.LONG_ENTRY.get("BASING_THEMES", ["Leading", "Neutral"])
                
                if entry_price < min_price:
                    continue

                # Is it Strong?
                is_strong = (score >= min_score and rs_rating >= min_rs and theme_class in allowed_themes)
                
                if ticker not in entries:
                    entries[ticker] = {}

                # 1. STRONG BLOCK
                if is_strong:
                    # Clear from drops if it recovered
                    if ticker in drop_tracker:
                        del drop_tracker[ticker]
                        
                    if "Strong" not in entries[ticker]:
                        entries[ticker]["Strong"] = {
                            "entry_date": date_str, "entry_price": entry_price, "theme_class": theme_class
                        }
                else:
                    # It is NOT Strong. 
                    # If it previously entered Strong, it is now "Dropped". Start the clock if not started.
                    if "Strong" in entries[ticker] and ticker not in drop_tracker:
                        drop_tracker[ticker] = {"days_dropped": 1}
                    
                    if ticker in drop_tracker:
                        days = drop_tracker[ticker]["days_dropped"]
                        
                        # 2. MILD BLOCK (Days 1 - 21)
                        if days <= 21:
                            if score >= mild_floor and rs_rating >= mild_floor:
                                if "Mild" not in entries[ticker]:
                                    entries[ticker]["Mild"] = {
                                        "entry_date": date_str, "entry_price": entry_price, "theme_class": theme_class
                                    }
                            else:
                                # It failed the floor! It is permanently killed from tracking.
                                del drop_tracker[ticker]
                        
                        # 3. BASING BLOCK (Days 22 - 50)
                        elif 22 <= days <= 50:
                            if zacks_rank in basing_zacks and theme_class in basing_themes:
                                if "Basing" not in entries[ticker]:
                                    entries[ticker]["Basing"] = {
                                        "entry_date": date_str, "entry_price": entry_price, "theme_class": theme_class
                                    }
                            else:
                                # Failed fundamental forgiveness. Kill it.
                                del drop_tracker[ticker]
                        
                        elif days > 50:
                            # Tracking expires natively
                            del drop_tracker[ticker]

            elif mode == "short":
                # SHORT ENGINE BLOCK
                allowed_themes = cfg.SHORT_ENTRY.get("THEMES", [])
                max_rs = cfg.SHORT_ENTRY.get("MAX_SHORT_RS", 15.0)
                min_rs_short = cfg.SHORT_ENTRY.get("MIN_SHORT_RS", 8.0)
                max_score = cfg.SHORT_ENTRY.get("MAX_SHORT_SCORE", 25.0)
                min_price = cfg.SHORT_ENTRY.get("MIN_PRICE", 10.0)
                mild_floor = cfg.SHORT_ENTRY.get("MAX_DROPPED_WATCH_SCORE", 30.0)
                decay_zacks = cfg.SHORT_ENTRY.get("DECAY_ZACKS", [4, 5])
                decay_themes = cfg.SHORT_ENTRY.get("DECAY_THEMES", ["Lagging"])
                avg_vol = row.get("avg_volume", 0) or 0
                
                passes_liquidity = (entry_price >= min_price) and (avg_vol >= cfg.SHORT_ENTRY.get("MIN_VOLUME", 1000000))
                if not passes_liquidity:
                    continue

                # Is it Strong Breakdown?
                is_strong = (score <= max_score and min_rs_short <= rs_rating <= max_rs and theme_class in allowed_themes)

                if ticker not in entries:
                    entries[ticker] = {}

                if is_strong:
                    if ticker in drop_tracker:
                        del drop_tracker[ticker]
                    if "Strong" not in entries[ticker]:
                        entries[ticker]["Strong"] = {
                            "entry_date": date_str, "entry_price": entry_price, "theme_class": theme_class
                        }
                else:
                    if "Strong" in entries[ticker] and ticker not in drop_tracker:
                        drop_tracker[ticker] = {"days_dropped": 1}
                    
                    if ticker in drop_tracker:
                        days = drop_tracker[ticker]["days_dropped"]
                        if days <= 21:
                            if score <= mild_floor and rs_rating <= mild_floor:
                                if "Mild" not in entries[ticker]:
                                    entries[ticker]["Mild"] = {
                                        "entry_date": date_str, "entry_price": entry_price, "theme_class": theme_class
                                    }
                            else:
                                del drop_tracker[ticker]
                        elif 22 <= days <= 50:
                            if zacks_rank in decay_zacks and theme_class in decay_themes:
                                if "Basing" not in entries[ticker]: # using Basing literal as bucket tag universally
                                    entries[ticker]["Basing"] = {
                                        "entry_date": date_str, "entry_price": entry_price, "theme_class": theme_class
                                    }
                            else:
                                del drop_tracker[ticker]
                        elif days > 50:
                            del drop_tracker[ticker]

    # Evaluate Returns Natively For All Buckets
    today_prices = prices.get(current_date, {})
    results = []

    for ticker, buckets in entries.items():
        current_price = today_prices.get(ticker, 0)
        if current_price > 0:
            for bucket_type, data in buckets.items():
                if mode == "long":
                    ret = ((current_price - data["entry_price"]) / data["entry_price"]) * 100.0
                else:
                    ret = ((data["entry_price"] - current_price) / data["entry_price"]) * 100.0
                    
                results.append({
                    "Ticker": ticker,
                    "Bucket": bucket_type,
                    "Entry Date": data["entry_date"],
                    "Entry Px": data["entry_price"],
                    "Current Px": current_price,
                    "Return %": round(ret, 2),
                    "Win": "YES" if ret > 0 else "NO",
                    "Class": data["theme_class"],
                })

    res_df = pd.DataFrame(results)
    
    if res_df.empty:
        if not silent: print("No trades triggered.")
        return {
            "total_trades": 0, "win_rate": 0.0, "avg_return": 0.0,
            "strong_trades": 0, "strong_win_rate": 0.0, "strong_avg_return": 0.0,
            "mild_trades": 0, "mild_win_rate": 0.0, "mild_avg_return": 0.0,
            "basing_trades": 0, "basing_win_rate": 0.0, "basing_avg_return": 0.0,
            "leading_trades": 0, "leading_win_rate": 0.0, "leading_avg_return": 0.0,
            "neutral_trades": 0, "neutral_win_rate": 0.0, "neutral_avg_return": 0.0,
        }
    
    def calc_bucket(df_sub):
        t = len(df_sub)
        wr = (len(df_sub[df_sub['Return %'] > 0]) / t * 100) if t else 0.0
        ar = df_sub['Return %'].mean() if t else 0.0
        return t, round(wr, 2), round(ar, 2)
        
    t_all, wr_all, ar_all = calc_bucket(res_df)
    t_str, wr_str, ar_str = calc_bucket(res_df[res_df["Bucket"] == "Strong"])
    t_mil, wr_mil, ar_mil = calc_bucket(res_df[res_df["Bucket"] == "Mild"])
    t_bas, wr_bas, ar_bas = calc_bucket(res_df[res_df["Bucket"] == "Basing"])
    
    lead_df = res_df[res_df['Class'] == 'Leading']
    neut_df = res_df[res_df['Class'] == 'Neutral']
    t_ld, wr_ld, ar_ld = calc_bucket(lead_df)
    t_nt, wr_nt, ar_nt = calc_bucket(neut_df)
    
    result_dict = {
        "total_trades": t_all, "win_rate": wr_all, "avg_return": ar_all,
        "strong_trades": t_str, "strong_win_rate": wr_str, "strong_avg_return": ar_str,
        "mild_trades": t_mil, "mild_win_rate": wr_mil, "mild_avg_return": ar_mil,
        "basing_trades": t_bas, "basing_win_rate": wr_bas, "basing_avg_return": ar_bas,
        "leading_trades": t_ld, "leading_win_rate": wr_ld, "leading_avg_return": ar_ld,
        "neutral_trades": t_nt, "neutral_win_rate": wr_nt, "neutral_avg_return": ar_nt,
        "_detail_df": res_df,
    }
    
    if not silent:
        print("\n" + "="*80)
        print(f"          TABELA 3-MONTH {mode.upper()} BACKTEST (TIERED MODEL)")
        print("="*80)
        print(f"Total Combined Trades: {t_all} | WR: {wr_all:.1f}% | Avg: {ar_all:.2f}%")
        print(f"  [Strong Tier]  Trades: {t_str} | WR: {wr_str:.1f}% | Avg: {ar_str:.2f}%")
        print(f"  [Mild Tier]    Trades: {t_mil} | WR: {wr_mil:.1f}% | Avg: {ar_mil:.2f}%")
        print(f"  [Basing Tier]  Trades: {t_bas} | WR: {wr_bas:.1f}% | Avg: {ar_bas:.2f}%\n")
        
    return result_dict

if __name__ == "__main__":
    import sys
    run_mode = "long"
    if len(sys.argv) > 1 and sys.argv[1] == "short":
        run_mode = "short"
    run_backtest(mode=run_mode)


import os
import json
import pandas as pd
import itertools
from pathlib import Path
from datetime import datetime
import time

def load_data_once():
    print("[1/4] Loading Historical Price Data into RAM...")
    prices = {}
    input_dir = Path("c:/TABELA/market_data/input_files")
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith("stocks.csv"):
                date_str = file[:8]
                date_fmt = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                try:
                    df = pd.read_csv(os.path.join(root, file), usecols=["Ticker", "Last Close", "Average Volume"])
                    df["Ticker"] = df["Ticker"].str.strip()
                    # Store price and avg volume
                    price_dict = df.set_index("Ticker").to_dict('index')
                    prices[date_fmt] = price_dict
                except Exception:
                    continue

    print("[2/4] Loading Processed JSON History into RAM...")
    json_dir = Path("c:/TABELA/market_data/stock_universe")
    json_files = sorted([os.path.join(r, f) for r, d, files in os.walk(json_dir) for f in files if f.endswith("_stock_history.json")])
    
    all_dates = sorted(prices.keys())
    if not all_dates:
        return {}, [], None

    current_date = all_dates[-1]
    daily_data = []

    for file in json_files:
        date_str = os.path.basename(file)[:10]
        if date_str == current_date:
            break
        try:
            with open(file, "r") as f:
                data = json.load(f)
                daily_data.append((date_str, data))
        except Exception:
            continue
            
    print("[3/4] Data Load Complete. Generating Grid...")
    return prices, daily_data, current_date


def run_scenario_in_ram(scenario, prices, daily_data, current_date):
    entries = {}
    drop_tracker = {}

    allowed_themes = scenario["THEMES"]
    max_rs = scenario["MAX_RS"]
    min_rs_short = scenario["MIN_RS"]
    max_score = scenario["MAX_SCORE"]
    mild_floor = scenario["MILD_FLOOR"]
    blocked_zacks = scenario["BLOCKED_ZACKS"]
    min_volume = scenario["MIN_VOLUME"]
    min_price = 10.0

    for date_str, data in daily_data:
        # Increment all dropped clocks today
        for t in list(drop_tracker.keys()):
            drop_tracker[t]["days_dropped"] += 1

        day_prices = prices.get(date_str, {})

        for row in data:
            score = row.get("short_score", row.get("long_score", 100.0))
            rs_rating = row.get("short_rs_rating", row.get("rs_rating", 100))
            ticker = row.get("ticker", "").strip()
            theme_class = row.get("theme_class", "Unknown")
            zacks_raw = row.get("zacks_rank", 3)
            try:
                zacks_rank = int(float(zacks_raw))
            except:
                zacks_rank = 3
                
            entry_data = day_prices.get(ticker, {})
            entry_price = entry_data.get("Last Close", 0)
            avg_vol = entry_data.get("Average Volume", 0)

            passes_liquidity = (entry_price >= min_price) and (avg_vol >= min_volume) and (zacks_rank not in blocked_zacks)
            if not passes_liquidity:
                continue

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
                    if days <= 50:
                        if score <= mild_floor:
                            if "Mild" not in entries[ticker]:
                                entries[ticker]["Mild"] = {
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
        current_price = today_prices.get(ticker, {}).get("Last Close", 0)
        if current_price > 0:
            for bucket_type, data in buckets.items():
                ret = ((data["entry_price"] - current_price) / data["entry_price"]) * 100.0
                results.append({"Bucket": bucket_type, "Return %": ret})

    res_df = pd.DataFrame(results)
    
    def calc_bucket(df_sub):
        t = len(df_sub)
        wr = (len(df_sub[df_sub['Return %'] > 0]) / t * 100) if t else 0.0
        ar = df_sub['Return %'].mean() if t else 0.0
        return t, round(wr, 2), round(ar, 2)
        
    t_all, wr_all, ar_all = calc_bucket(res_df)
    t_str, wr_str, ar_str = calc_bucket(res_df[res_df["Bucket"] == "Strong"])
    t_mil, wr_mil, ar_mil = calc_bucket(res_df[res_df["Bucket"] == "Mild"])

    return {
        "Trades": t_all, "WR%": wr_all, "Avg%": ar_all,
        "Str.Trd": t_str, "Str.WR%": wr_str, "Mil.Trd": t_mil, "Mil.WR%": wr_mil
    }

def main():
    prices, daily_data, current_date = load_data_once()
    if not prices:
        print("Failed to load data.")
        return

    # Cartesian Axes (Our Judgment)
    grid_scores = [45.0, 50.0]
    grid_max_rs = [75.0]
    grid_zacks = [[1, 2]]
    grid_vols = [1_000_000, 2_500_000]
    grid_mild_floor = [65.0, 75.0, 85.0]
    grid_themes = [
        ["Lagging", "Micro Laggard", "Neutral", "Unknown"]
    ]

    scenarios = []
    for sc, mrs, zk, v, mf, th in itertools.product(grid_scores, grid_max_rs, grid_zacks, grid_vols, grid_mild_floor, grid_themes):
        # Logical constraint: Mild floor must be >= Max Score
        if mf >= sc:
            scenarios.append({
                "MIN_RS": 40.0, "MAX_RS": mrs, "MAX_SCORE": sc,
                "BLOCKED_ZACKS": zk, "MIN_VOLUME": v, 
                "MILD_FLOOR": mf, "THEMES": th
            })

    print(f"[4/4] Bypassing sub-processes. Running {len(scenarios)} Cartesian Grid Combinations fully in-memory...")
    
    start_time = time.time()
    results = []

    for i, scen in enumerate(scenarios):
        if i % 20 == 0 and i > 0:
            print(f"  Processed {i}/{len(scenarios)}...")
        
        stat = run_scenario_in_ram(scen, prices, daily_data, current_date)
        if stat["Trades"] > 0:
            row = scen.copy()
            row.update(stat)
            results.append(row)

    elapsed = time.time() - start_time
    print(f"\\nGrid execution complete in {elapsed:.2f} seconds!")

    df = pd.DataFrame(results)
    
    # Sort for overall "Low Volume / High Probability" 
    # Formula: Filter for Mild Trades > 10, sort by Mild WR% Descending, then Total WR%
    qualified = df[df["Mil.Trd"] >= 5]
    if qualified.empty:
        qualified = df
    top_performers = qualified.sort_values(by=["Mil.WR%", "Str.WR%"], ascending=[False, False]).head(10)

    out_file = Path("c:/TABELA/backtesting/results/cartesian_mild_short.csv")
    top_performers.to_csv(out_file, index=False)
    print(f"Saved Top 10 Permutations to {out_file}\\n")
    print("TOP 3 ULTRA-PREMIUM RESULTS FOR MILD BOUNCE CATCHING:")
    
    for _, row in top_performers.head(3).iterrows():
        print(f"[-] Max Score: {row['MAX_SCORE']}, Max RS: {row['MAX_RS']}, "
              f"Mild Floor: {row['MILD_FLOOR']}, Min Vol: {row['MIN_VOLUME']/1000000}m, "
              f"Blocked Zacks: {row['BLOCKED_ZACKS']}")
        print(f"    ↳ Mild WR: {row['Mil.WR%']}% ({row['Mil.Trd']} trades) | Strong WR: {row['Str.WR%']}% ({row['Str.Trd']} trades)")

if __name__ == "__main__":
    main()

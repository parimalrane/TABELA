import os
import json
import pandas as pd
import itertools
import time
from pathlib import Path

def load_data_once():
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
                    prices[date_fmt] = df.set_index("Ticker").to_dict('index')
                except Exception:
                    continue

    json_dir = Path("c:/TABELA/market_data/stock_universe")
    json_files = sorted([os.path.join(r, f) for r, d, files in os.walk(json_dir) for f in files if f.endswith("_stock_history.json")])
    
    all_dates = sorted(prices.keys())
    if not all_dates: return {}, [], None

    current_date = all_dates[-1]
    daily_data = []

    for file in json_files:
        date_str = os.path.basename(file)[:10]
        if date_str == current_date: break
        try:
            with open(file, "r") as f:
                daily_data.append((date_str, json.load(f)))
        except:
            continue
    return prices, daily_data, current_date

def run_scenario(scenario, prices, daily_data, current_date):
    entries = {}
    drop_tracker = {}

    min_rs = scenario["MIN_RS"]
    min_score = scenario["MIN_SCORE"]
    blocked_zacks = scenario["BLOCKED_ZACKS"]
    min_vol = scenario["MIN_VOL"]
    mild_floor = scenario["MILD_FLOOR"]
    mild_days = scenario["MILD_DAYS"]
    allowed_themes = ["Leading", "Neutral", "Unclassified Leader", "Unknown"]

    for date_str, data in daily_data:
        day_prices = prices.get(date_str, {})
        
        for t in list(drop_tracker.keys()):
            drop_tracker[t]["days"] += 1

        for row in data:
            ticker = row.get("ticker", "").strip()
            score = row.get("long_score", 0.0)
            rs_rating = row.get("rs_rating", 0)
            theme = row.get("theme_class", "Unknown")
            zacks_raw = row.get("zacks_rank", 3)
            try: zacks_rank = int(float(zacks_raw))
            except: zacks_rank = 3
            
            entry_data = day_prices.get(ticker, {})
            entry_px = entry_data.get("Last Close", 0)
            avg_vol = entry_data.get("Average Volume", 0)

            passes_liq = (entry_px >= 10.0 and avg_vol >= min_vol and zacks_rank not in blocked_zacks)
            if not passes_liq: continue

            is_strong = (rs_rating >= min_rs and score >= min_score and theme in allowed_themes)
            
            if ticker not in entries: entries[ticker] = {}

            if is_strong:
                if ticker in drop_tracker: del drop_tracker[ticker]
                if "Strong" not in entries[ticker]:
                    entries[ticker]["Strong"] = {"px": entry_px}
            else:
                if "Strong" in entries[ticker] and ticker not in drop_tracker:
                    drop_tracker[ticker] = {"days": 1}
                if ticker in drop_tracker:
                    days = drop_tracker[ticker]["days"]
                    if days <= mild_days:
                        if score >= mild_floor:
                            if "Mild" not in entries[ticker]:
                                entries[ticker]["Mild"] = {"px": entry_px}
                        else:
                            del drop_tracker[ticker]
                    else:
                        del drop_tracker[ticker]

    today_prices = prices.get(current_date, {})
    results = []
    for ticker, buckets in entries.items():
        current_price = today_prices.get(ticker, {}).get("Last Close", 0)
        if current_price > 0:
            for b_type, b_data in buckets.items():
                ret = ((current_price - b_data["px"]) / b_data["px"]) * 100.0
                results.append({"Bucket": b_type, "Ret": ret})

    df = pd.DataFrame(results)
    def calc_b(df_s):
        t = len(df_s)
        wr = (len(df_s[df_s['Ret'] > 0]) / t * 100) if t else 0.0
        ar = df_s['Ret'].mean() if t else 0.0
        return t, round(wr, 2), round(ar, 2)

    t_all, wr_all, ar_all = calc_b(df)
    t_str, wr_str, ar_str = calc_b(df[df["Bucket"] == "Strong"])
    t_mil, wr_mil, ar_mil = calc_b(df[df["Bucket"] == "Mild"])

    return {
        "Trades": t_all, "WR%": wr_all, "Avg%": ar_all,
        "Str.Trd": t_str, "Str.WR%": wr_str, "Str.Avg": ar_str,
        "Mil.Trd": t_mil, "Mil.WR%": wr_mil, "Mil.Avg": ar_mil
    }

def main():
    prices, daily_data, current_date = load_data_once()
    grid_gates = [(90.0, 90.0), (90.0, 85.0)]
    grid_vols = [300000, 1500000]
    grid_zacks = [[4, 5]]
    grid_floors = [70.0, 80.0]
    grid_days = [21]
    
    scenarios = []
    for g, v, z, f, d in itertools.product(grid_gates, grid_vols, grid_zacks, grid_floors, grid_days):
        scenarios.append({
            "MIN_RS": g[0], "MIN_SCORE": g[1], "MIN_VOL": v,
            "BLOCKED_ZACKS": z, "MILD_FLOOR": f, "MILD_DAYS": d
        })
        
    print(f"Running {len(scenarios)} Cartesian Long permutations...")
    res = []
    for i, sc in enumerate(scenarios):
        s = run_scenario(sc, prices, daily_data, current_date)
        if s["Trades"] > 0:
            row = sc.copy()
            row.update(s)
            res.append(row)

    df = pd.DataFrame(res)
    out = Path("c:/TABELA/backtesting/results/cartesian_mild_long.csv")
    df.to_csv(out, index=False)
    print(f"\\nSaved to {out}")

    qualified = df[df["Str.Trd"] >= 5]
    if qualified.empty: qualified = df
    top = qualified.sort_values(by=["Str.WR%", "Mil.WR%"], ascending=[False, False]).head(5)
    for _, r in top.iterrows():
        print(f"Gate: {r['MIN_RS']}/{r['MIN_SCORE']} | Vol: {r['MIN_VOL']} | Zacks: {r['BLOCKED_ZACKS']} | Floor: {r['MILD_FLOOR']} | Days: {r['MILD_DAYS']}")
        print(f"  ↳ Strong WR: {r['Str.WR%']}% (Avg {r['Str.Avg']}%) | Mild WR: {r['Mil.WR%']}% (Avg {r['Mil.Avg']}%) | Total: {r['Trades']} Trades")

if __name__ == "__main__":
    main()

import os
import json
import pandas as pd
from pathlib import Path

def run_backtest():
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
    json_files = []
    for root, dirs, files in os.walk(json_dir):
        for file in files:
            if file.endswith("_stock_history.json"):
                json_files.append(os.path.join(root, file))

    json_files = sorted(json_files)

    entries = {} 
    current_date = "2026-09-25"

    from config.config import LONG_ENTRY
    allowed_themes = LONG_ENTRY.get("THEMES", [])
    min_rs = LONG_ENTRY.get("MIN_RS", 90.0)
    min_score = LONG_ENTRY.get("MIN_LONG_SCORE", 85.0)
    min_price = LONG_ENTRY.get("MIN_PRICE", 10.0)

    for file in json_files:
        date_str = os.path.basename(file)[:10]
        if date_str == current_date:
            break
            
        with open(file, "r") as f:
            data = json.load(f)
        
        for row in data:
            long_score = row.get("long_score")
            rs_rating = row.get("rs_rating", 0)
            if long_score is None:
                long_score = 0.0
                
            ticker = row["ticker"]
            theme_class = row.get("theme_class", "Unknown")
            
            # STRICT CONFIG.PY PARITY
            if long_score >= min_score and rs_rating >= min_rs and theme_class in allowed_themes:
                if ticker not in entries:
                    entry_price = prices.get(date_str, {}).get(ticker, 0)
                    if entry_price >= min_price:  
                        entries[ticker] = {
                            "entry_date": date_str,
                            "entry_price": entry_price,
                            "theme_class": theme_class,
                            "highest_score": long_score
                        }
                else:
                    if long_score > entries[ticker]["highest_score"]:
                        entries[ticker]["highest_score"] = long_score

    today_prices = prices.get(current_date, {})

    results = []
    for ticker, data in entries.items():
        current_price = today_prices.get(ticker, 0)
        if current_price > 0:
            ret = ((current_price - data["entry_price"]) / data["entry_price"]) * 100.0
            results.append({
                "Ticker": ticker,
                "Entry Date": data["entry_date"],
                "Entry Px": data["entry_price"],
                "Current Px": current_price,
                "Return %": round(ret, 2),
                "Class": data["theme_class"]
            })

    res_df = pd.DataFrame(results)
    if not res_df.empty:
        res_df = res_df.sort_values("Return %", ascending=False)
        
        print("\n" + "="*80)
        print("          TABELA 3-MONTH BRUTAL MACRO BACKTEST (July 10 -> Sept 25)")
        print("="*80)
        
        win_rate = (len(res_df[res_df['Return %'] > 0]) / len(res_df)) * 100
        print(f"\nTotal Confirmed Breakouts (Score >= {min_score}): {len(res_df)}")
        print(f"Total Win Rate: {win_rate:.1f}%")
        print(f"Average Trade Return: {res_df['Return %'].mean():.2f}%\n")
        
        print(">>> EDGE VALIDATION: RETURNS BY THEME CLASS <<<")
        print("This mathematically proves your CANSLIM group strength philosophy.\n")
        
        res_df['Win'] = (res_df['Return %'] > 0).astype(int)
        
        def win_rate_calc(x):
            return f"{(x.sum() / len(x) * 100):.1f}%"
            
        summary = res_df.groupby("Class").agg(
            Avg_Return=("Return %", "mean"),
            Win_Rate=("Win", win_rate_calc),
            Total_Trades=("Ticker", "count")
        )
        summary = summary.sort_values("Avg_Return", ascending=False).round(2)
        print(summary.to_string())
        
        print("\n>>> TOP 5 MONSTER BREAKOUTS <<<")
        print(res_df.head(5)[['Ticker', 'Entry Date', 'Class', 'Return %']].to_string(index=False))
        
        print("\n" + "="*80)
    else:
        print("No trades triggered in the backtest.")

if __name__ == "__main__":
    run_backtest()

import os
import json
import pandas as pd
from pathlib import Path
import time

def build_matrix():
    t0 = time.time()
    
    json_dir = Path("c:/TABELA/market_data/stock_universe")
    csv_dir = Path("c:/TABELA/market_data/input_files")
    
    json_files = sorted([f for f in json_dir.rglob("*_stock_history.json")])
    
    # 1. Load JSONs to get theme info
    json_data = []
    for f in json_files:
        date_str = f.name[:10]
        with open(f, "r") as json_f:
            try:
                data = json.load(json_f)
                for row in data:
                    json_data.append({
                        "date": date_str,
                        "Ticker": row.get("ticker", "").strip(),
                        "theme_class": row.get("theme_class", "Unknown"),
                        "theme_strength_score": row.get("theme_strength_score", 0.0),
                        "zacks_rank": row.get("zacks_rank", 3)
                    })
            except: pass
            
    df_json = pd.DataFrame(json_data)
    print(f"JSON loaded in {time.time()-t0:.2f}s. Rows: {len(df_json)}")
    
    # 2. Load CSVs to get raw scoring fields
    t1 = time.time()
    csv_data = []
    csv_files = sorted([f for f in csv_dir.rglob("*stocks.csv")])
    for f in csv_files:
        date_str = f.name[:8]
        date_fmt = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        try:
            df = pd.read_csv(f)
            df["Ticker"] = df["Ticker"].str.strip()
            df["date"] = date_fmt
            csv_data.append(df)
        except: pass
        
    df_csv = pd.concat(csv_data, ignore_index=True)
    print(f"CSV loaded in {time.time()-t1:.2f}s. Rows: {len(df_csv)}")
    
    # 3. Merge
    t2 = time.time()
    master = pd.merge(df_csv, df_json, on=["date", "Ticker"], how="left")
    print(f"Merged in {time.time()-t2:.2f}s. Master shape: {master.shape}")
    
    # Print sample cols
    print("\nSample Master Cols:")
    cols = ["date", "Ticker", "Last Close", "% Price Change (4 Weeks)", "Relative Price Change (YTD)", "theme_class"]
    available = [c for c in cols if c in master.columns]
    print(master[available].head(3))
    
if __name__ == "__main__":
    build_matrix()

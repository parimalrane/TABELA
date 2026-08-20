import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yfinance as yf
import pandas as pd
from datetime import datetime
import os

ETFS = ["DIA", "IWM", "QQQ", "SPY"]

def get_perf(close_series, window):
    if len(close_series) > window:
        return ((close_series.iloc[-1] - close_series.iloc[-(window+1)]) / close_series.iloc[-(window+1)]) * 100
    return 0.0

def generate_market_csv():
    output_dir = "market_data/input_files"
    os.makedirs(output_dir, exist_ok=True)
        
    print("Downloading market data from Yahoo Finance...")
    
    rows = []
    
    for etf in ETFS:
        print(f"Fetching {etf}...")
        df = yf.download(etf, period="1y", progress=False)
        if df.empty:
            print(f"Warning: No data for {etf}")
            continue
            
        close_raw = df["Close"].squeeze()
        vol_raw = df["Volume"].squeeze()

        # Drop NaN values (like current incomplete day on weekends)
        close = close_raw.dropna()
        if close.empty:
            continue
            
        vol = vol_raw.loc[close.index]
        
        last_px = close.iloc[-1]
        last_vol = vol.iloc[-1]
        
        sma_5 = close.rolling(5).mean().iloc[-1]
        sma_20 = close.rolling(20).mean().iloc[-1]
        sma_50 = close.rolling(50).mean().iloc[-1]
        sma_200 = close.rolling(200).mean().iloc[-1]
        
        v_sma_20 = vol.rolling(20).mean().iloc[-1]
        v_sma_50 = vol.rolling(50).mean().iloc[-1]
        
        # Calculate trailing performance (close to close)
        perf_1d = get_perf(close, 1)
        perf_5d = get_perf(close, 5)
        perf_20d = get_perf(close, 20)
        perf_50d = get_perf(close, 50)
        perf_200d = get_perf(close, 200)
        
        # Calculate moving average distance %
        dist_5d = ((last_px - sma_5) / sma_5) * 100
        dist_20d = ((last_px - sma_20) / sma_20) * 100
        dist_50d = ((last_px - sma_50) / sma_50) * 100
        dist_200d = ((last_px - sma_200) / sma_200) * 100
        
        # Use the actual last trading date from Yahoo Finance for stamping
        market_date_obj = close.index[-1]
        
        rows.append({
            "Market Date": market_date_obj.strftime("%Y-%m-%d"),
            "ETF": etf,
            "Derived Price": round(last_px, 2),
            "Volume": int(last_vol),
            "20D Avg Vol": int(v_sma_20),
            "1D Perf %": round(perf_1d, 2),
            "5D Perf %": round(perf_5d, 2),
            "20D Perf %": round(perf_20d, 2),
            "50D Perf %": round(perf_50d, 2),
            "200D Perf %": round(perf_200d, 2),
            "5D Dist %": round(dist_5d, 2),
            "20D Dist %": round(dist_20d, 2),
            "50D Dist %": round(dist_50d, 2),
            "200D Dist %": round(dist_200d, 2),
        })
        
    if not rows:
        print("No data fetched. Exiting.")
        return

    # Use the date from the last processed ETF to name the file
    final_market_date_obj = market_date_obj 
    file_date_str = final_market_date_obj.strftime("%Y%m%d")
    csv_file = os.path.join(output_dir, f"{file_date_str}_Market.csv")

    out_df = pd.DataFrame(rows)
    out_df.to_csv(csv_file, index=False)
    print(f"\nSuccessfully created true market file: {csv_file} with {len(rows)} ETFs!")

if __name__ == "__main__":
    generate_market_csv()

import sys
import pandas as pd
from pathlib import Path

BASE_DIR = Path("c:/TABELA")
sys.path.insert(0, str(BASE_DIR))

from backtesting.vectorized_backtest import VectorizedBacktestEngine
import config.config as cfg
import scoring.scoring_engine as scoring

engine = VectorizedBacktestEngine()
engine.load_data()

# Process first 5 dates
sample_dates = engine.all_dates[-5:]
print(f"Checking Garage RS for {sample_dates}...")

max_garage_rs = 0
basing_candidates = 0

for d in sample_dates:
    df_d = engine.master_matrix[engine.master_matrix["date"] == d].copy()
    cols_to_clean = list(cfg.RS_RAW_WEIGHTS.keys()) + ["Last Close", "avg_volume"]
    for c in cols_to_clean:
        if c in df_d.columns:
            df_d[c] = pd.to_numeric(
                df_d[c].astype(str).str.replace(r'[%$,]', '', regex=True).str.replace(r'^\((.*)\)$', r'-\1', regex=True),
                errors='coerce'
            ).fillna(0.0)

    # Need Zacks and Themes to check Basing candidates
    df_d = scoring.calculate_zacks_score(df_d)
    
    # Calculate Garage RS
    df_d = scoring.calculate_long_garage_rs_raw(df_d)
    df_d = scoring.calculate_long_garage_rs_rating(df_d)
    
    if "Long_Garage_RS_Rating" in df_d.columns:
        m = df_d["Long_Garage_RS_Rating"].max()
        max_garage_rs = max(max_garage_rs, m)
        print(f"[{d}] Max Garage_RS_Rating: {m}")
        
        # Check how many are Zacks 1/2
        z12 = df_d[df_d["Zacks Rank"].isin([1, 2])]
        print(f"[{d}] Total Zacks 1/2 Stocks: {len(z12)}")
        
        # Of Zacks 1/2, how many have Garage_RS >= 80?
        waking = z12[z12["Long_Garage_RS_Rating"] >= 80.0]
        print(f"[{d}] Zacks 1/2 with Garage RS >= 80: {len(waking)}")
        basing_candidates += len(waking)

print(f"\nTotal Wake Up Candidates in sample: {basing_candidates}")

import pandas as pd
df = pd.read_csv("C:/TABELA/market_data/input_files/2026-10/20261007_stocks.csv")
import os
import sys

pypl = df[df['Ticker'].str.contains('PYPL', case=False, na=False)]
print("Raw PYPL entry in CSV:")
print(pypl.T.to_string())

import sys
sys.path.append("C:/TABELA")
from pipeline.pipeline import build_stock_master

try:
    master = build_stock_master(df, "20261007")
    p_master = master[master['Ticker'].str.contains('PYPL', case=False, na=False)]
    print("\nProcessed PYPL output from pipeline:")
    if not p_master.empty:
        for col in ["Ticker", "RS_Raw", "RS_Rating", "Long_Score", "Zacks Rank", "Growth_Score", "Theme_Class"]:
            if col in p_master.columns:
                print(f"{col}: {p_master[col].values[0]}")
except Exception as e:
    print("Pipeline failed:", str(e))

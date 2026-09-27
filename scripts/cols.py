import pandas as pd
df = pd.read_csv(r"c:\TABELA\market_data\input_files\2026-09\20260925_ETF.csv", encoding="utf-16", nrows=0)
cols = [c for c in df.columns if "Perf" in c or "YTD" in c or "Year" in c]
with open(r"c:\TABELA\cols.txt", "w") as f:
    f.write(str(cols))

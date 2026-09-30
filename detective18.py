import pandas as pd
df = pd.read_csv('c:/TABELA/market_data/input_files/2026-09/20260928_etf.csv')
target = [x for x in df["Ticker"].values if "XLU" in str(x)]
print(target)

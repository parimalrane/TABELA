import pandas as pd
df = pd.read_csv('c:/TABELA/market_data/input_files/2026-09/20260928_stocks.csv', encoding='utf-8', on_bad_lines='skip')
print("XLU present?", "XLU" in df["Ticker"].values)

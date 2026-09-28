import pandas as pd
df = pd.read_csv('c:/TABELA/market_data/input_files/2026-09/20260925_ETF.csv')
print(df['Investment Strategy'].unique()[:20])

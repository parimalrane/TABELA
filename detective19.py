import pandas as pd
df25 = pd.read_csv('c:/TABELA/market_data/input_files/2026-09/20260925_stocks.csv')
df28 = pd.read_csv('c:/TABELA/market_data/input_files/2026-09/20260928_stocks.csv')

def get_stats(df, ticker):
    row = df[df['Ticker'] == ticker].iloc[0]
    return row[['Ticker', 'RS Rating', 'Zacks Rank', 'Growth Score', 'Last Close']]

print("PLTR 25:", get_stats(df25, "PLTR").to_dict())
print("PLTR 28:", get_stats(df28, "PLTR").to_dict())

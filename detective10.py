import pandas as pd
df = pd.read_csv('c:/TABELA/market_data/input_files/2026-09/20260925_stocks.csv')
be = df[df['Ticker'] == 'BE'].iloc[0]
print(f"BE:")
print(f"Zacks Rank: {be.get('Zacks Rank')}")
print(f"Growth Score: {be.get('Growth Score')}")
print(f"RS (12W): {be.get('% Price Change (12 Weeks)')}")
print(f"RS (4W): {be.get('% Price Change (4 Weeks)')}")

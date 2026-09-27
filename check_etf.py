import pandas as pd

df = pd.read_csv(r'c:\TABELA\market_data\input_files\2026-09\20260925_ETF.csv')
tickers = ['XLB', 'XLC', 'XLE', 'XLF', 'XLU', 'XLI', 'XLK', 'XLP', 'XLRE', 'XLV', 'XLY']
subset = df[df['Ticker'].isin(tickers)][['Ticker', 'Performance 1M (%)', 'Performance 1W (%)']]
print(f"Found {len(subset)} / 11 ETFs")
print(subset)

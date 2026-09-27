import pandas as pd
try:
    df = pd.read_csv(r'c:\TABELA\market_data\input_files\2026-09\20260925_ETF.csv')
    tickers = ['XLB', 'XLC', 'XLE', 'XLF', 'XLU', 'XLI', 'XLK', 'XLP', 'XLRE', 'XLV', 'XLY']
    subset = df[df['Ticker'].isin(tickers)][['Ticker', 'Performance 1M (%)', 'Performance 1W (%)']]
    with open(r'c:\TABELA\output.txt', 'w') as f:
        f.write(f"Found {len(subset)} / 11 ETFs\n")
        f.write(subset.to_string())
except Exception as e:
    with open(r'c:\TABELA\output.txt', 'w') as f:
        f.write(str(e))

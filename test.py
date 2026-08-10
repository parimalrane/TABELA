import pandas as pd
df = pd.read_csv('market_data/input_files/20260710_stocks.csv')
print(df[df['Ticker'].isin(['URGN', 'KNSA', 'PACS', 'VIK', 'MPC', 'DDOG', 'GKOS', 'CBZ'])][['Ticker', 'Industry']])

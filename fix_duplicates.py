import pandas as pd
df = pd.read_csv('c:/TABELA/data/stock_theme_mapping.csv')
df = df.drop_duplicates(subset=['Ticker'], keep='last')
df.to_csv('c:/TABELA/data/stock_theme_mapping.csv', index=False)

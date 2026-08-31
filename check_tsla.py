import json
import pandas as pd
with open('market_data/stock_universe/2026-08/2026-08-28_stock_history.json') as f:
    data = json.load(f)
df = pd.DataFrame(data)
tsla = df[df['Ticker'].str.contains('TSLA', na=False)]
print(tsla[['Ticker', 'RS_Rating', 'Industry']])

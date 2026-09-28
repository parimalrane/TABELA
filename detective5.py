import json
with open("c:/TABELA/market_data/stock_universe/2026-09/2026-09-25_stock_history.json") as f:
    data = json.load(f)

for row in data:
    if row['ticker'] in ['AOUT', 'CNK', 'IMAX', 'NSIT']:
        print(row['ticker'], "-> Theme:", row['theme'], "Theme_Class:", row['theme_class'], "Long Score:", row['long_score'])

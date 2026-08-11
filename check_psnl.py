import json
with open('market_data/stock_universe/2026-08-10_stock_history.json') as f:
    data = json.load(f)
for x in data:
    if x['ticker'] == 'PSNL':
        print(json.dumps(x, indent=2))

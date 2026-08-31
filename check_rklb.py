import json
with open('market_data/stock_universe/2026-08/2026-08-28_stock_history.json') as f:
    data = json.load(f)

for row in data:
    for k, v in row.items():
        if isinstance(v, str) and 'RKLB' in v:
            print("FOUND RKLB:", row)

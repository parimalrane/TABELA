import json
with open('c:/TABELA/market_data/stock_universe/2026-09/2026-09-25_stock_history.json') as f:
    d = json.load(f)
print("Longs 25:", len([x for x in d if x.get('is_long_candidate')]))

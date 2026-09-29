import json
with open('c:/TABELA/market_data/stock_universe/2026-07/2026-07-10_stock_history.json') as f:
    d = json.load(f)
    print(d[0])

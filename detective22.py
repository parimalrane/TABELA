import json
import pandas as pd
with open('c:/TABELA/market_data/stock_universe/2026-09/2026-09-28_stock_history.json') as f:
    d = json.load(f)
okta = [x for x in d if x['ticker'] == 'OKTA'][0]
print(json.dumps(okta, indent=2))

import json
r = json.load(open('market_data/stock_transition/2026-08-18_registry.json'))
print('WDC in registry:', 'WDC' in r)
if 'WDC' in r:
    print(r['WDC'])

import pandas as pd
import json

with open('market_data/stock_transition/registry/2026-08/2026-08-28_registry.json', 'r') as f:
    reg = json.load(f)

d = [k for k,v in reg.items() if v['tracking_state'] == 'DISTRIBUTION']
print("DIST IN REGISTRY:", len(d))

from pipeline.pipeline import get_distribution_candidates
stocks = pd.read_csv("market_data/stock_universe/2026-08/2026-08-28.csv")
print("Total raw stocks:", len(stocks))
print("DAL in raw:", stocks[stocks['Ticker']=='DAL'].to_dict('records'))

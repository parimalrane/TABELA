import json
f = 'market_data/snapshots/2026-08-18_market_snapshot.json'
with open(f, 'r') as file:
    data = json.load(file)
    print(data.keys())

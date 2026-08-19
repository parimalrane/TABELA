import pandas as pd
import json

f = 'market_data/snapshots/2026-08-18_market_snapshot.json'
with open(f, 'r') as file:
    data = json.load(file)
    if 'theme_strength' in data:
        df = pd.DataFrame(data['theme_strength'])
        print(df['Theme'].head(10).tolist())

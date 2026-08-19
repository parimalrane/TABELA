import pandas as pd
import json
import glob

files = sorted(glob.glob('market_data/snapshots/*_market_snapshot.json'))
print("Semiconductors Historical Ranks:")
for f in files[-10:]:
    with open(f, 'r') as file:
        data = json.load(file)
        if 'theme_strength' in data:
            df = pd.DataFrame(data['theme_strength'])
            r = df[df['Theme'] == 'Semiconductors']
            if not r.empty:
                print(f"{f[-31:-21]} Rank: {r.iloc[0]['Theme_Rank']}")

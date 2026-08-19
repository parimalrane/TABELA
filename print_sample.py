import json

for d in ['2026-08-17', '2026-08-18']:
    f = f'market_data/snapshots/{d}_market_snapshot.json'
    with open(f, 'r') as file:
        data = json.load(file)
        
        for k in ['leading_themes', 'neutral_themes', 'lagging_themes']:
            for t in data.get(k, []):
                if t['theme'] == 'Semiconductors':
                    print(f"\n[{d}] -> {k}")
                    print(json.dumps(t, indent=4))

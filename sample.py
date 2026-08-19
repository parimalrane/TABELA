import json  
for d in ['2026-08-17', '2026-08-18']:  
    data = json.load(open(f'market_data/snapshots/{d}_market_snapshot.json'))  
    for k in ['leading_themes', 'neutral_themes', 'lagging_themes']:  
        for t in data.get(k, []):  
            if t['theme'] == 'Semiconductors': print(f\"{d} ({k}):\", json.dumps(t))  

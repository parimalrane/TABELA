import pandas as pd  
import json  
import glob  
sn = sorted(glob.glob('market_data/snapshots/*_market_snapshot.json'))[-5:]  
for f in sn:  
    data = json.load(open(f))  
    df = pd.DataFrame(data['theme_strength'])  
    r = df[df['Theme']=='Semiconductors']  
    if not r.empty: print(f[-31:-21], \"Rank:\", r.iloc[0]['Theme_Rank'])  

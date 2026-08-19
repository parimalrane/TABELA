from engines.historical_query_engine import load_history  
history = load_history()  
snapshots = [r.get('snapshot').data for r in history.runs[-16:] if r.get('snapshot') and r.get('snapshot').exists]  
for s in snapshots:  
    for k in ['leading_themes', 'neutral_themes', 'lagging_themes']:  
        for t in s.get(k, []):  
            if t.get('theme') == 'Semiconductors': print(s['date'], k, t['rank'])  

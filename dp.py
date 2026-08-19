from engines.historical_query_engine import load_history  
from engines.historical_intelligence_engine import build_theme_daily_series  
h = load_history()  
s = build_theme_daily_series([r.get('snapshot').data for r in h.runs if r.get('snapshot') and r.get('snapshot').exists and r.date.isoformat() <= '2026-08-14'])  
pts = sorted(s.get('Semiconductors', []), key=lambda x: x['date'])[-10:]  
for p in pts: print(p['date'], p['rank'])  

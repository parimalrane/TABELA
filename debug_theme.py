import pandas as pd
from core.pipeline import run_tabela_pipeline

stocks, long_candidates, distribution_watchlist, theme_breadth, recovered = run_tabela_pipeline()

from engines.historical_intelligence_engine import run_historical_intelligence_engine

import json
sn = json.load(open('market_data/snapshots/2026-08-18_market_snapshot.json'))
df = pd.DataFrame(sn['theme_strength'])
movement, p = run_historical_intelligence_engine(df)

row = p[p['Theme'] == 'Semiconductors']
print("\n--- THEME PERFORMANCE TABLE ROW ---")
print(row.to_string())

# let's write out the window logic quickly to print the points
from engines.historical_query_engine import load_history
from engines.historical_intelligence_engine import build_theme_daily_series
h = load_history()
s = build_theme_daily_series([r.get('snapshot').data for r in h.runs if r.get('snapshot') and r.get('snapshot').exists])
pts = s.get('Semiconductors', [])
pts = sorted(pts, key=lambda x: x['date'])[-10:]
print("\n--- 10-DAY ROLLING WINDOW POINTS ---")
for p in pts:
    print(f"Date: {p['date']} | Rank: {p['rank']}")

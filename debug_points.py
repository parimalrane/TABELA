from engines.historical_query_engine import load_history
from engines.historical_intelligence_engine import build_theme_daily_series
h = load_history()
s = build_theme_daily_series([r.get('snapshot').data for r in h.runs if r.get('snapshot') and r.get('snapshot').exists])
pts = s.get('Semiconductors', [])
pts = sorted(pts, key=lambda x: x['date'])[-10:]
print("\n--- 10-DAY ROLLING WINDOW POINTS ---")
for p in pts:
    print(f"Date: {p['date']} | Rank: {p['rank']}")

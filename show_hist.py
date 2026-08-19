from engines.historical_query_engine import load_history
from engines.historical_intelligence_engine import build_theme_daily_series

sn = load_history()
data = build_theme_daily_series(sn)

print("Semiconductors historical points:")
for p in data.get('Semiconductors', [])[-5:]:
    print(p)

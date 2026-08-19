from engines.historical_query_engine import load_history

history = load_history()
snapshots = []
for run in history.runs:
    s = run.get("snapshot")
    if s and s.exists:
        snapshots.append(s.data)

print("Semiconductors Historical Ranks:")
for snapshot in snapshots[-5:]:
    date = snapshot.get("date")
    # rank is in theme_strength list maybe? No, build_theme_daily_series extracts it.
    for k in ["leading_themes", "neutral_themes", "lagging_themes"]:
        for t in snapshot.get(k, []):
            if t.get("theme") == "Semiconductors":
                print(f"{date} - {k} - Rank {t.get('rank')} - Score {t.get('score')}")

lines = open("engines/distribution_engine.py", "r", encoding="utf-8").read().splitlines()
for i, l in enumerate(lines):
    if "build_distribution_watchlist" in l:
        print(i, l)

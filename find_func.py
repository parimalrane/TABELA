import glob
for f in glob.glob("engines/*.py"):
    lines = open(f, encoding="utf-8").read().splitlines()
    for l in lines:
        if "def get_distribution_watchlist" in l:
            print(f, l)

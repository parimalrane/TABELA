import glob
import os

files = glob.glob("market_data/daily_reports/*.txt")
if not files: exit()
latest_file = max(files, key=os.path.getctime)

with open(latest_file, "r", encoding="utf-8") as f:
    out = open("found.txt", "w", encoding="utf-8")
    for line in f.read().splitlines():
        if "CDNA" in line or "BLFS" in line or "NEO" in line or "LQDA" in line:
            out.write(line + "\n")
    out.close()

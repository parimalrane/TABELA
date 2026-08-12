import glob
import os

files = glob.glob("market_data/daily_reports/*.txt")
if not files:
    print("No daily reports found.")
    exit(0)
    
latest_file = max(files, key=os.path.getctime)

with open(latest_file, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

with open("out.txt", "w", encoding="utf-8") as f:
    for l in lines:
        if "Macro State" in l or "Cybersecurity" in l or "Biotech" in l or "Score" in l:
            f.write(l + "\n")

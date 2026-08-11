import os
for root, _, files in os.walk("."):
    if "venv" in root: continue
    for f in files:
        if f.endswith(".py"):
            text = open(os.path.join(root, f), encoding='utf-8').read()
            if "calculate_short_score" in text and f != "short_scoring_engine.py":
                print("FOUND in", os.path.join(root, f))

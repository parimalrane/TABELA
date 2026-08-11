import os

targets = ["short_score", "is_short_candidate", "short_rank", "short_weakness", "short_scoring"]

for root, _, files in os.walk("."):
    if "venv" in root: continue
    for f in files:
        if f.endswith(".py"):
            text = open(os.path.join(root, f), encoding='utf-8').read().lower()
            for t in targets:
                if t in text and f not in ["short_scoring_engine.py", "find_s.py", "config.py", "find_short.py", "find_unused4.py"]:
                    print(f"Used {t} in {f}")

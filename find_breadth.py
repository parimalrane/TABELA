import os
for root, _, files in os.walk("."):
    for f in files:
        if f.endswith(".py"):
            text = open(os.path.join(root, f), encoding="utf-8").read()
            if "breadth_engine" in text:
                print(os.path.join(root, f))

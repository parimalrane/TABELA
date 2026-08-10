with open("run_metrics.txt", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

for line in lines[-1000:]:
    if "Unclassified Leader" in line:
        print(line.strip())

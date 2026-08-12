with open("market_data/input_files/20260811_ETF.csv", "r", encoding="utf-8") as f:
    lines = f.readlines()

count = 0
for l in lines:
    if "Consumer Staples" in l or "Energy" in l or "Gold" in l:
        print(l.strip())
        count += 1
        if count > 10: break

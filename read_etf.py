with open("market_data/input_files/20260811_ETF.csv", "r", encoding="utf-8") as f:
    for i in range(5):
        print(f.readline().strip())

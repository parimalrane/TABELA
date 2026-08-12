import pandas as pd
df = pd.read_csv("market_data/input_files/20260811_Market.csv")
print(df[["ETF", "Volume", "RV 20D %", "RV 50D %"]])

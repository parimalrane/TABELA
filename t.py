import pandas as pd  
df = pd.read_csv('market_data/input_files/20260818_Market.csv')  
r = df.iloc[2]  
print(\"returns_1d\", round(float(r.get(\"1D Perf %\", 0.0)), 2))  
print(\"vol\", int(r[\"Volume\"]))  
print(\"avg_vol\", int(r.get(\"20D Avg Vol\", -1)))  

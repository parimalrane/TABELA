import pandas as pd  
df = pd.read_csv('market_data/input_files/20260814_Market.csv')  
print(df[['ETF', 'Volume', '20D Avg Vol']].to_string(index=False))  

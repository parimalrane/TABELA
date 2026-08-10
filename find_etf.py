import glob
import pandas as pd
df = pd.read_csv(glob.glob('market_data/input_files/*ETF.csv')[-1])
print("Strategies:")
print(sorted(df['Investment Strategy'].dropna().unique().tolist()))

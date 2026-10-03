import pandas as pd
df = pd.read_csv('market_data/input_files/2026-10/20261002_ETF.csv')
for period in ["Performance 1M (%)", "Performance 1W (%)", "Performance 3M (%)"]:
    val = df[period].astype(str).str.replace(r'[%$]', '', regex=True).str.replace(',', '')
    num = pd.to_numeric(val, errors='coerce')
    print(period, num.isna().sum())

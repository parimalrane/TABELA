import pandas as pd
df = pd.read_csv('C:/TABELA/backtesting/tuners/quarterly_master_results.csv')
print("\n--- TOP LONG CONFIGURATIONS ---")
print(df[['WinRate_Final', 'AvgReturn_Final', 'Trades_Final', 'MIN_LONG_SCORE', 'MIN_RS', 'MIN_VOLUME']].sort_values(['WinRate_Final', 'AvgReturn_Final'], ascending=False).head(5).to_string())

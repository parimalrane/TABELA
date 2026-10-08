import pandas as pd
df = pd.read_csv('C:/TABELA/backtesting/tuners/quarterly_short_master_results.csv')
print("\n--- LOWEST TRADES CONFIGURATIONS ---")
print(df[['WinRate_Final', 'AvgReturn_Final', 'Trades_Final', 'MAX_SHORT_SCORE', 'MAX_SHORT_RS', 'MIN_SHORT_RS', 'MIN_VOLUME']].sort_values('Trades_Final').head(15).to_string())
